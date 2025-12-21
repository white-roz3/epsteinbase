#!/usr/bin/env python3
"""Ingest extracted images into database"""
import json
import asyncpg
import asyncio
import os
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/epsteinbase")

# Data directory (relative to scripts/)
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"

async def ingest_manifest():
    """Ingest extracted PDF pages from manifest"""
    manifest_path = DATA_DIR / "extraction_manifest.json"
    
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        print("Run extract_images.py first to extract pages from PDFs")
        return
    
    with open(manifest_path) as f:
        items = json.load(f)
    
    print(f"Ingesting {len(items)} extracted pages...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    batch_size = 500
    inserted = 0
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        
        values = []
        for item in batch:
            # Determine type based on content
            doc_type = 'document'  # Default
            ocr_text = item.get('ocr_text', '')
            if ocr_text:
                text_lower = ocr_text.lower()
                if 'photograph' in text_lower or 'photo' in text_lower:
                    doc_type = 'photo'
            
            source_pdf = item.get('source_pdf', '')
            source = f"DOJ_{source_pdf.replace('.pdf', '')}" if source_pdf else "DOJ"
            
            title = f"Page {item['page_number']}"
            if item.get('efta_id'):
                title = f"{item['efta_id']} - {title}"
            title = f"{title} - {source_pdf}"
            
            # Limit text size
            text = ocr_text[:50000] if ocr_text else None
            
            values.append((
                item.get('efta_id'),
                title,
                source,
                doc_type,
                text,
                item.get('file_path'),
                item.get('thumbnail_path'),
                item['page_number'],
                source_pdf
            ))
        
        try:
            await conn.executemany("""
                INSERT INTO documents 
                (efta_id, title, source, type, ocr_text, file_path, thumbnail_path, page_number, source_pdf)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, values)
            inserted += len(values)
            print(f"Inserted {inserted}/{len(items)} pages...")
        except Exception as e:
            print(f"Error inserting batch {i}-{i+batch_size}: {e}")
            continue
    
    await conn.close()
    print(f"\n✓ Extracted pages ingestion complete! Inserted {inserted} documents")

async def ingest_media():
    """Ingest videos and audio files"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    inserted = 0
    
    # Videos
    video_files = list((DATA_DIR / "videos").glob("*.mp4"))
    for video_file in video_files:
        title = video_file.stem.replace("_", " ").replace("%20", " ")
        
        # Determine description based on filename
        if "video1" in video_file.name.lower():
            description = "Complete raw surveillance footage from MCC cell block, August 9-10, 2019"
        elif "video2" in video_file.name.lower():
            description = "Digitally enhanced version of MCC surveillance footage"
        else:
            description = "DOJ surveillance footage"
        
        try:
            await conn.execute("""
                INSERT INTO documents (title, source, type, file_path, description)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """, title, "DOJ", "video", f"videos/{video_file.name}", description)
            inserted += 1
        except Exception as e:
            print(f"Error inserting video {video_file.name}: {e}")
    
    # Audio
    audio_files = list((DATA_DIR / "audio").glob("*.wav"))
    for audio_file in audio_files:
        title = audio_file.stem.replace("_", " ").replace("%20", " ")
        redacted = "(R)" in title or "(Redacted)" in title
        
        metadata = json.dumps({"redacted": redacted}) if redacted else None
        
        try:
            await conn.execute("""
                INSERT INTO documents (title, source, type, file_path, description, metadata)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT DO NOTHING
            """, title, "DOJ", "audio", f"audio/{audio_file.name}",
                "Maxwell proffer session recording",
                metadata)
            inserted += 1
        except Exception as e:
            print(f"Error inserting audio {audio_file.name}: {e}")
    
    await conn.close()
    print(f"\n✓ Media files ingested! Inserted {inserted} files")

if __name__ == "__main__":
    print("=== Ingesting Extracted Pages ===\n")
    asyncio.run(ingest_manifest())
    
    print("\n=== Ingesting Media Files ===\n")
    asyncio.run(ingest_media())


