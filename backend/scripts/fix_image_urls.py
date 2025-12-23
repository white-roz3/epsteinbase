"""Script to fix broken image URLs in the database by reconstructing them from file_path"""
import asyncio
import asyncpg
import os
from pathlib import Path

# Add parent directory to path to import app modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.b2_client import get_file_url

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")

async def fix_image_urls():
    """Update NULL or broken URLs for images using file_path"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Get all images with NULL URLs or URLs that don't start with http
        rows = await conn.fetch("""
            SELECT id, file_path, url, type
            FROM documents
            WHERE type = 'image'
            AND (url IS NULL OR url NOT LIKE 'http%')
            AND file_path IS NOT NULL
        """)
        
        print(f"Found {len(rows)} images with broken/missing URLs")
        
        updated = 0
        for row in rows:
            try:
                # Reconstruct URL from file_path
                new_url = get_file_url(row['file_path'])
                if new_url:
                    await conn.execute("""
                        UPDATE documents
                        SET url = $1
                        WHERE id = $2
                    """, new_url, row['id'])
                    updated += 1
                    if updated % 100 == 0:
                        print(f"Updated {updated} URLs...")
            except Exception as e:
                print(f"Error updating ID {row['id']}: {e}")
        
        print(f"\n✓ Fixed {updated} image URLs")
        
        # Also fix thumbnails
        thumb_rows = await conn.fetch("""
            SELECT id, thumbnail_path, thumbnail_url
            FROM documents
            WHERE type = 'image'
            AND thumbnail_path IS NOT NULL
            AND (thumbnail_url IS NULL OR thumbnail_url NOT LIKE 'http%')
        """)
        
        print(f"Found {len(thumb_rows)} images with broken/missing thumbnail URLs")
        
        thumb_updated = 0
        for row in thumb_rows:
            try:
                new_thumb_url = get_file_url(row['thumbnail_path'])
                if new_thumb_url:
                    await conn.execute("""
                        UPDATE documents
                        SET thumbnail_url = $1
                        WHERE id = $2
                    """, new_thumb_url, row['id'])
                    thumb_updated += 1
            except Exception as e:
                print(f"Error updating thumbnail for ID {row['id']}: {e}")
        
        print(f"✓ Fixed {thumb_updated} thumbnail URLs")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_image_urls())

