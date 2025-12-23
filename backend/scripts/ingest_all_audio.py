#!/usr/bin/env python3
"""Ingest all downloaded audio files into database"""
import asyncpg
import asyncio
import os
import json
from pathlib import Path
from datetime import date

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")
DATA_DIR = Path(__file__).parent.parent.parent / "data"

AUDIO_METADATA = [
    {"title": "Maxwell Proffer - Day 1, Part 1", "pattern": "Day_1", "part": 1, "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 2", "pattern": "Day_1.*Part_2", "part": 2, "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 3", "pattern": "Day_1.*Part_3", "part": 3, "redacted": True, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 4", "pattern": "Day_1.*Part_4", "part": 4, "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 5", "pattern": "Day_1.*Part_5", "part": 5, "redacted": True, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 6", "pattern": "Day_1.*Part_6", "part": 6, "redacted": True, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 7", "pattern": "Day_1.*Part_7", "part": 7, "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 2, Part 1", "pattern": "Day_2.*Part_1", "part": 1, "redacted": True, "date": "2025-07-25"},
    {"title": "Maxwell Proffer - Day 2, Part 2", "pattern": "Day_2.*Part_2", "part": 2, "redacted": True, "date": "2025-07-25"},
    {"title": "Maxwell Proffer - Day 2, Part 3", "pattern": "Day_2.*Part_3", "part": 3, "redacted": False, "date": "2025-07-25"},
    {"title": "Maxwell Proffer - Day 2, Part 4", "pattern": "Day_2.*Part_4", "part": 4, "redacted": True, "date": "2025-07-25"},
]

async def ingest_audio_files():
    conn = await asyncpg.connect(DATABASE_URL)
    audio_dir = DATA_DIR / "audio"
    
    if not audio_dir.exists():
        print("Audio directory doesn't exist")
        await conn.close()
        return
    
    audio_files = list(audio_dir.glob("*.wav"))
    print(f"Found {len(audio_files)} audio files")
    
    # First, delete existing audio entries that don't have files
    await conn.execute("""
        DELETE FROM documents 
        WHERE type = 'audio' AND file_path IS NULL
    """)
    print("Cleaned up audio entries without files")
    
    imported = {}
    
    for audio_file in audio_files:
        filename = audio_file.name
        
        # Try to match to metadata
        matched = None
        for meta in AUDIO_METADATA:
            import re
            pattern = meta['pattern'].replace('_', '[_ ]').replace('.', r'\.')
            if re.search(pattern, filename, re.IGNORECASE):
                matched = meta
                break
        
        if matched:
            metadata = json.dumps({
                "session_date": matched['date'],
                "redacted": matched['redacted'],
                "part": matched['part']
            })
            
            await conn.execute("""
                INSERT INTO documents 
                (title, source, type, file_path, description, location, redacted, date_released, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
            """,
                matched['title'], 'DOJ', 'audio', f"audio/{filename}",
                "Maxwell proffer session recording with DOJ prosecutors",
                "FCI Tallahassee",
                matched['redacted'],
                date.fromisoformat(matched['date']),
                metadata
            )
            imported[matched['title']] = filename
            print(f"✓ Imported {matched['title']}")
        else:
            # Generic entry
            title = filename.replace('_', ' ').replace('.wav', '')
            await conn.execute("""
                INSERT INTO documents 
                (title, source, type, file_path, description, location, date_released)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                title, 'DOJ', 'audio', f"audio/{filename}",
                "Maxwell proffer session recording",
                "FCI Tallahassee",
                date(2025, 7, 24)
            )
            print(f"✓ Imported generic: {title}")
    
    count = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE type = 'audio' AND file_path IS NOT NULL")
    await conn.close()
    
    print(f"\n✓ Total audio files in database: {count}")

if __name__ == "__main__":
    asyncio.run(ingest_audio_files())



