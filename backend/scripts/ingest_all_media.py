#!/usr/bin/env python3
"""Ingest all downloaded media files into database"""
import asyncpg
import asyncio
import os
import json
from pathlib import Path
from datetime import date
import re

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")
DATA_DIR = Path(__file__).parent.parent.parent / "data"

async def ingest_all_audio():
    """Ingest all audio files"""
    conn = await asyncpg.connect(DATABASE_URL)
    audio_dir = DATA_DIR / "audio"
    
    # Delete old audio entries
    await conn.execute("DELETE FROM documents WHERE type = 'audio'")
    
    audio_files = sorted(audio_dir.glob("*.wav"))
    print(f"\nIngesting {len(audio_files)} audio files...")
    
    for audio_file in audio_files:
        filename = audio_file.name
        
        # Parse filename to extract metadata
        day = "Day 1" if "Day_1" in filename or "Day1" in filename else "Day 2"
        redacted = "(R)" in filename or "redacted" in filename.lower()
        
        # Extract part number
        part_match = re.search(r'Part[_\s](\d+)', filename, re.IGNORECASE)
        part_num = part_match.group(1) if part_match else "1"
        
        session_date = "2025-07-24" if "Day_1" in filename or "Day1" in filename else "2025-07-25"
        title = f"Maxwell Proffer - {day}, Part {part_num}"
        
        metadata = json.dumps({
            "session_date": session_date,
            "redacted": redacted,
            "filename": filename
        })
        
        await conn.execute("""
            INSERT INTO documents 
            (title, source, type, file_path, description, location, redacted, date_released, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
        """,
            title, 'DOJ', 'audio', f"audio/{filename}",
            "Maxwell proffer session recording with DOJ prosecutors",
            "FCI Tallahassee",
            redacted,
            date.fromisoformat(session_date),
            metadata
        )
    
    count = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE type = 'audio'")
    await conn.close()
    print(f"✓ Ingested {count} audio files")

async def ingest_all_videos():
    """Update video entries with file paths"""
    conn = await asyncpg.connect(DATABASE_URL)
    video_dir = DATA_DIR / "videos"
    
    video_files = {
        "video1.mp4": "MCC Cell Block Surveillance - Raw Footage",
        "video2.mp4": "MCC Surveillance - Enhanced Version",
    }
    
    for filename, title in video_files.items():
        file_path = video_dir / filename
        if file_path.exists():
            await conn.execute("""
                UPDATE documents 
                SET file_path = $1 
                WHERE title = $2 AND type = 'video'
            """, f"videos/{filename}", title)
    
    count = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE type = 'video' AND file_path IS NOT NULL")
    await conn.close()
    print(f"✓ Updated {count} videos with file paths")

async def ingest_additional_documents():
    """Ingest the additional PDF documents"""
    conn = await asyncpg.connect(DATABASE_URL)
    pdf_dir = DATA_DIR / "pdfs"
    
    pdf_metadata = {
        "B._Flight_Log_Released_in_US_v._Maxwell,_1.20-cr-00330_(SDNY_2020).pdf": {
            "title": "Flight Logs (Lolita Express)",
            "subtype": "Evidence",
            "description": "Flight logs from Epstein's Boeing 727 showing passengers and destinations.",
        },
        "C._Contact_Book_(Redacted).pdf": {
            "title": "Contact Book (Black Book)",
            "subtype": "Evidence",
            "description": "Personal contact book. Unredacted version reportedly has 1,500+ names.",
            "redacted": True,
        },
        "D._Masseuse_List_(Redacted).pdf": {
            "title": "Masseuse List (Redacted)",
            "subtype": "Evidence",
            "description": "List of masseuses from estate records.",
            "redacted": True,
        },
        "Interview_Transcript_-_Maxwell_2025.07.24_(Redacted).pdf": {
            "title": "Maxwell Proffer Transcript - Day 1",
            "subtype": "Transcript",
            "description": "Transcript of Maxwell's proffer session on July 24, 2025.",
            "redacted": True,
        },
        "Interview_Transcript_-_Maxwell_2025.07.25_(Redacted).pdf": {
            "title": "Maxwell Proffer Transcript - Day 2",
            "subtype": "Transcript",
            "description": "Transcript of Maxwell's proffer session on July 25, 2025.",
            "redacted": True,
        },
        "2025.07_DOJ_FBI_Memorandum.pdf": {
            "title": "DOJ/FBI Memo on BOP Footage",
            "subtype": "Memo",
            "description": "Concludes no evidence Epstein was murdered or kept a 'client list.'",
        },
    }
    
    inserted = 0
    for filename, meta in pdf_metadata.items():
        pdf_path = pdf_dir / filename
        if pdf_path.exists():
            # Check if already exists
            exists = await conn.fetchval("""
                SELECT COUNT(*) FROM documents 
                WHERE title = $1 AND type = 'document'
            """, meta['title'])
            
            if exists == 0:
                await conn.execute("""
                    INSERT INTO documents 
                    (title, source, type, subtype, description, file_path, url, downloadable, redacted, date_released)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                    meta['title'], 'DOJ', 'document', meta.get('subtype'),
                    meta.get('description'), f"pdfs/{filename}",
                    f"https://www.justice.gov/multimedia/DOJ%20Disclosures/.../{filename.replace('_', '%20')}",
                    True, meta.get('redacted', False), date(2025, 12, 19)
                )
                inserted += 1
    
    await conn.close()
    print(f"✓ Ingested {inserted} additional documents")

async def main():
    print("=" * 60)
    print("INGESTING ALL MEDIA FILES")
    print("=" * 60)
    
    await ingest_all_videos()
    await ingest_all_audio()
    await ingest_additional_documents()
    
    # Show final stats
    conn = await asyncpg.connect(DATABASE_URL)
    total = await conn.fetchval("SELECT COUNT(*) FROM documents")
    by_type = await conn.fetch("""
        SELECT type, COUNT(*) as count, COUNT(file_path) as with_files
        FROM documents 
        WHERE type IS NOT NULL 
        GROUP BY type
        ORDER BY type
    """)
    await conn.close()
    
    print("\n" + "=" * 60)
    print("FINAL DATABASE STATUS")
    print("=" * 60)
    print(f"\nTotal documents: {total}\n")
    for row in by_type:
        print(f"  {row['type']:12} {row['count']:4} total, {row['with_files']:4} with files")

if __name__ == "__main__":
    asyncio.run(main())



