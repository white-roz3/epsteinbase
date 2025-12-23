#!/usr/bin/env python3
"""Download and ingest all Epstein files"""
import subprocess
import asyncpg
import asyncio
import os
import json
from pathlib import Path
from datetime import date

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# All audio URLs
ALL_AUDIO_URLS = [
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%201%20-%207_24_25_Tallahassee.003.wav", "Day 1, Part 1", False),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%202%20-%207_24_25_Tallahassee.004.wav", "Day 1, Part 2", False),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%203%20-%207_24_25_Tallahassee.005%20(R).wav", "Day 1, Part 3", True),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%204%20-%207_24_25_Tallahassee.007.wav", "Day 1, Part 4", False),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%205%20-%207_24_25_Tallahassee.008%20(R).wav", "Day 1, Part 5", True),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%206%20-%207_24_25_Tallahassee.009%20(R).wav", "Day 1, Part 6", True),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%207%20-%207_24_25_Tallahassee.010.wav", "Day 1, Part 7", False),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%201%20-%202025.07.25%20-%20xxx7_25.003%20(R).wav", "Day 2, Part 1", True),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%202%20-%202025.07.25%20-%20xxx7_25.004%20(R).wav", "Day 2, Part 2", True),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%203%20-%202025.07.25%20-%20xxx7_25.005.wav", "Day 2, Part 3", False),
    ("https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%204%20-%202025.07.25%20-%20xxx7_25.006%20(R).wav", "Day 2, Part 4", True),
]

def download_file(url, dest):
    """Download with progress"""
    if dest.exists():
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"  ✓ {dest.name} ({size_mb:.1f}MB) - already exists")
        return True
    
    print(f"  ↓ Downloading {dest.name}...")
    try:
        subprocess.run(["curl", "-L", "-o", str(dest), url], check=True)
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"  ✓ Downloaded {dest.name} ({size_mb:.1f}MB)")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

async def download_and_ingest_audio():
    """Download all audio files and ingest"""
    audio_dir = DATA_DIR / "audio"
    audio_dir.mkdir(exist_ok=True, parents=True)
    
    print("\n=== DOWNLOADING AUDIO FILES ===\n")
    downloaded = []
    
    for url, title_key, redacted in ALL_AUDIO_URLS:
        filename = url.split("/")[-1].replace("%20", "_")
        dest = audio_dir / filename
        
        if download_file(url, dest):
            downloaded.append((dest, title_key, redacted))
    
    print(f"\n✓ Downloaded {len(downloaded)}/{len(ALL_AUDIO_URLS)} audio files\n")
    
    # Ingest into database
    print("=== INGESTING AUDIO FILES ===\n")
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Clean up old entries
    await conn.execute("DELETE FROM documents WHERE type = 'audio'")
    
    for audio_file, title_key, redacted in downloaded:
        # Extract day and part from title_key
        day = "Day 1" if "Day 1" in title_key else "Day 2"
        part_num = title_key.split("Part ")[-1] if "Part" in title_key else "1"
        title = f"Maxwell Proffer - {day}, Part {part_num}"
        
        session_date = "2025-07-24" if "Day 1" in day else "2025-07-25"
        metadata = json.dumps({"session_date": session_date, "redacted": redacted})
        
        await conn.execute("""
            INSERT INTO documents 
            (title, source, type, file_path, description, location, redacted, date_released, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
        """,
            title, 'DOJ', 'audio', f"audio/{audio_file.name}",
            "Maxwell proffer session recording with DOJ prosecutors",
            "FCI Tallahassee",
            redacted,
            date.fromisoformat(session_date),
            metadata
        )
        print(f"  ✓ {title}")
    
    count = await conn.fetchval("SELECT COUNT(*) FROM documents WHERE type = 'audio'")
    await conn.close()
    print(f"\n✓ Ingested {count} audio files")

async def main():
    print("=== EPSTEIN FILES DOWNLOAD & INGEST ===\n")
    await download_and_ingest_audio()
    
    print("\n=== STATUS ===")
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
    
    print(f"\nTotal documents: {total}")
    for row in by_type:
        print(f"  {row['type']}: {row['count']} total, {row['with_files']} with files")

if __name__ == "__main__":
    asyncio.run(main())



