#!/usr/bin/env python3
"""Ingest files from R2 into database"""
import asyncpg
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.b2_client import list_files, get_file_url

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/epsteinbase")

async def ingest_from_r2():
    """Ingest files from R2 storage into database"""
    print("Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print(f"DATABASE_URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'}")
        return
    
    print("✓ Connected to database")
    
    # List files from R2
    print("\nListing files from R2...")
    all_files = list_files()  # Get all files
    
    if not all_files:
        print("⚠ No files found in R2. Make sure R2 credentials are configured.")
        await conn.close()
        return
    
    print(f"Found {len(all_files)} files in R2")
    
    # Group files by type
    images = [f for f in all_files if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    videos = [f for f in all_files if f.endswith(('.mp4', '.mov', '.avi'))]
    audio = [f for f in all_files if f.endswith(('.wav', '.mp3', '.m4a'))]
    
    print(f"  - Images: {len(images)}")
    print(f"  - Videos: {len(videos)}")
    print(f"  - Audio: {len(audio)}")
    
    inserted = 0
    
    # Ingest images
    for file_path in images[:1000]:  # Limit to 1000 for now
        try:
            title = Path(file_path).stem.replace("_", " ").replace("-", " ")
            source = "R2"
            
            # Determine if it's a flight log or regular image
            doc_type = "image"
            if "flight" in file_path.lower() or "contact" in file_path.lower():
                source = "DOJ"
            
            await conn.execute("""
                INSERT INTO documents (title, source, type, file_path, description)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """, title, source, doc_type, file_path, f"Image from {source}")
            inserted += 1
            
            if inserted % 100 == 0:
                print(f"  Inserted {inserted} documents...")
        except Exception as e:
            print(f"  Error inserting {file_path}: {e}")
    
    # Ingest videos
    for file_path in videos:
        try:
            title = Path(file_path).stem.replace("_", " ").replace("-", " ")
            await conn.execute("""
                INSERT INTO documents (title, source, type, file_path, description)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """, title, "DOJ", "video", file_path, "Video file from R2")
            inserted += 1
        except Exception as e:
            print(f"  Error inserting {file_path}: {e}")
    
    # Ingest audio
    for file_path in audio:
        try:
            title = Path(file_path).stem.replace("_", " ").replace("-", " ")
            redacted = "(R)" in title or "(Redacted)" in title
            metadata = '{"redacted": true}' if redacted else None
            
            await conn.execute("""
                INSERT INTO documents (title, source, type, file_path, description, metadata)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT DO NOTHING
            """, title, "DOJ", "audio", file_path, "Audio file from R2", metadata)
            inserted += 1
        except Exception as e:
            print(f"  Error inserting {file_path}: {e}")
    
    await conn.close()
    print(f"\n✓ Ingested {inserted} documents from R2 into database")

if __name__ == "__main__":
    asyncio.run(ingest_from_r2())

