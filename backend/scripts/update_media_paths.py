#!/usr/bin/env python3
"""Update database entries with actual file paths for downloaded media"""
import asyncpg
import asyncio
import os
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")
DATA_DIR = Path(__file__).parent.parent.parent / "data"

async def update_media_paths():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Update videos
    video_files = {
        "MCC Cell Block Surveillance - Raw Footage": "videos/video1.mp4",
        "MCC Surveillance - Enhanced Version": "videos/video2.mp4",
    }
    
    for title, file_path in video_files.items():
        full_path = DATA_DIR / file_path
        if full_path.exists():
            await conn.execute("""
                UPDATE documents 
                SET file_path = $1 
                WHERE title = $2 AND type = 'video'
            """, file_path, title)
            print(f"✓ Updated {title}")
    
    # Update audio files - check what's actually downloaded
    audio_dir = DATA_DIR / "audio"
    if audio_dir.exists():
        audio_files = list(audio_dir.glob("*.wav"))
        print(f"\nFound {len(audio_files)} audio files")
        
        # Try to match audio files to database entries
        for audio_file in audio_files:
            filename = audio_file.name
            # Try to match by filename pattern
            if "Day_1" in filename or "Day1" in filename or "Part_1" in filename:
                if "Part_1" in filename or filename.startswith("Day"):
                    await conn.execute("""
                        UPDATE documents 
                        SET file_path = $1 
                        WHERE title LIKE '%Day 1, Part 1%' AND type = 'audio' AND file_path IS NULL
                        LIMIT 1
                    """, f"audio/{filename}")
                    print(f"  Matched {filename} to Day 1 Part 1")
    
    # Count what we have
    video_count = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE type = 'video' AND file_path IS NOT NULL")
    audio_count = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE type = 'audio' AND file_path IS NOT NULL")
    
    await conn.close()
    
    print(f"\n✓ Videos with files: {video_count}/2")
    print(f"✓ Audio with files: {audio_count}/11")

if __name__ == "__main__":
    asyncio.run(update_media_paths())


