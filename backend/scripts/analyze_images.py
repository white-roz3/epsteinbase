#!/usr/bin/env python3
"""Analyze images to detect people, objects, and generate captions"""
import asyncpg
import asyncio
import os
import json
from pathlib import Path
from typing import List, Dict

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")
DATA_DIR = Path(__file__).parent.parent.parent / "data"

def analyze_image_content(image_path: Path, ocr_text: str = None) -> Dict:
    """
    Analyze image to detect content.
    For now, uses OCR text and heuristics. Can be extended with actual vision models.
    """
    analysis = {
        "has_people": False,
        "people_count": 0,
        "detected_people": [],
        "objects": [],
        "scene_type": "unknown",
        "caption": None,
        "tags": []
    }
    
    # Analyze OCR text if available
    if ocr_text:
        text_lower = ocr_text.lower()
        
        # Look for people-related terms
        people_keywords = [
            'person', 'people', 'man', 'woman', 'men', 'women', 'boy', 'girl',
            'child', 'children', 'face', 'faces', 'portrait', 'group', 'crowd',
            'clinton', 'epstein', 'trump', 'gates', 'maxwell', 'andrew',
            'prince', 'president', 'celebrit', 'actor', 'actress', 'model'
        ]
        
        # Check for people
        people_matches = [kw for kw in people_keywords if kw in text_lower]
        if people_matches:
            analysis["has_people"] = True
            analysis["people_count"] = min(len(people_matches), 10)  # Estimate
        
        # Extract specific people names from common patterns
        name_patterns = [
            r'bill\s+clinton',
            r'jeffrey\s+epstein',
            r'donald\s+trump',
            r'ghislaine\s+maxwell',
            r'prince\s+andrew',
            r'bill\s+gates',
            r'michael\s+jackson',
            r'kevin\s+spacey',
            r'walter\s+cronkite'
        ]
        
        detected_names = []
        import re
        for pattern in name_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                detected_names.extend([m.title() for m in matches])
        
        analysis["detected_people"] = list(set(detected_names))
        
        # Detect scene types
        if any(term in text_lower for term in ['airplane', 'plane', 'aircraft', 'jet', 'flight']):
            analysis["scene_type"] = "aircraft"
            analysis["objects"].append("airplane")
        elif any(term in text_lower for term in ['building', 'office', 'house', 'mansion', 'residence']):
            analysis["scene_type"] = "building"
            analysis["objects"].append("building")
        elif any(term in text_lower for term in ['beach', 'ocean', 'water', 'island']):
            analysis["scene_type"] = "outdoor"
            analysis["objects"].extend(["beach", "water"])
        elif any(term in text_lower for term in ['room', 'interior', 'inside']):
            analysis["scene_type"] = "interior"
            analysis["objects"].append("room")
        elif any(term in text_lower for term in ['hot tub', 'pool', 'swimming']):
            analysis["scene_type"] = "recreation"
            analysis["objects"].append("hot tub" if "hot tub" in text_lower else "pool")
        elif any(term in text_lower for term in ['check', 'money', 'payment', 'transaction']):
            analysis["scene_type"] = "document"
            analysis["objects"].append("check" if "check" in text_lower else "document")
        elif analysis["has_people"]:
            analysis["scene_type"] = "portrait" if analysis["people_count"] <= 3 else "group"
        
        # Generate caption
        caption_parts = []
        
        if analysis["detected_people"]:
            people_str = ", ".join(analysis["detected_people"][:3])
            if len(analysis["detected_people"]) > 3:
                people_str += f" and {len(analysis['detected_people']) - 3} others"
            caption_parts.append(people_str)
        
        if analysis["scene_type"] != "unknown":
            scene_desc = {
                "aircraft": "on an aircraft",
                "building": "at a building",
                "outdoor": "outdoors",
                "interior": "indoors",
                "recreation": "at a recreational facility",
                "portrait": "portrait photo",
                "group": "group photo",
                "document": "document image"
            }
            if analysis["scene_type"] in scene_desc:
                caption_parts.append(scene_desc[analysis["scene_type"]])
        
        if caption_parts:
            analysis["caption"] = " - ".join(caption_parts)
        
        # Add tags
        if analysis["has_people"]:
            analysis["tags"].append("people")
        if analysis["scene_type"] != "unknown":
            analysis["tags"].append(analysis["scene_type"])
        analysis["tags"].extend(analysis["objects"][:3])
    
    return analysis

async def analyze_and_update_images():
    """Analyze all images and update their descriptions"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    print("Analyzing images for content detection...")
    
    # Get all image documents
    rows = await conn.fetch("""
        SELECT id, title, ocr_text, description, metadata
        FROM documents 
        WHERE type = 'image'
        ORDER BY id
    """)
    
    print(f"Analyzing {len(rows)} images...")
    
    updated = 0
    for row in rows:
        ocr_text = row['ocr_text'] or ''
        current_metadata = row['metadata'] or {}
        
        if isinstance(current_metadata, str):
            try:
                current_metadata = json.loads(current_metadata)
            except:
                current_metadata = {}
        
        # Analyze image
        analysis = analyze_image_content(Path(""), ocr_text)
        
        # Merge with existing metadata
        updated_metadata = {**current_metadata, **analysis}
        
        # Update description if we generated a caption and don't have one
        new_description = row['description']
        if not new_description and analysis.get('caption'):
            new_description = analysis['caption']
        
        # Build enhanced description
        if analysis.get('detected_people'):
            people_list = ", ".join(analysis['detected_people'])
            if not new_description:
                new_description = f"Photo featuring {people_list}"
            elif people_list not in new_description:
                new_description = f"{people_list} - {new_description}"
        
        # Update database
        await conn.execute("""
            UPDATE documents 
            SET description = COALESCE(NULLIF($1, ''), description),
                metadata = $2::jsonb
            WHERE id = $3
        """,
            new_description,
            json.dumps(updated_metadata),
            row['id']
        )
        
        updated += 1
        if updated % 100 == 0:
            print(f"  Updated {updated}/{len(rows)} images...")
    
    await conn.close()
    print(f"\n✓ Analyzed and updated {updated} images")

async def main():
    print("=" * 60)
    print("IMAGE CONTENT ANALYSIS")
    print("=" * 60)
    
    await analyze_and_update_images()
    
    # Show stats
    conn = await asyncpg.connect(DATABASE_URL)
    with_people = await conn.fetchval("""
        SELECT COUNT(*) FROM documents 
        WHERE type = 'image' 
        AND metadata::text LIKE '%"has_people": true%'
    """)
    total_images = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE type = 'image'")
    await conn.close()
    
    print(f"\nImages with detected people: {with_people}/{total_images}")

if __name__ == "__main__":
    asyncio.run(main())



