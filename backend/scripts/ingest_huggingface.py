#!/usr/bin/env python3
"""Ingest pre-OCR'd data from HuggingFace"""
from datasets import load_dataset
import asyncpg
import asyncio
import os
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/epsteinbase")

async def ingest_huggingface():
    print("Loading HuggingFace dataset...")
    try:
        ds = load_dataset("tensonaut/EPSTEIN_FILES_20K", split="train")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Make sure you have 'datasets' library installed: pip install datasets")
        return
    
    print(f"Loaded {len(ds)} documents")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print(f"Make sure PostgreSQL is running and DATABASE_URL is correct")
        return
    
    # Batch insert
    batch_size = 500
    inserted = 0
    
    for i in range(0, len(ds), batch_size):
        batch = ds[i:i+batch_size]
        
        values = []
        for item in batch:
            # Limit text size for database
            text = item.get('text', '')
            if text and len(text) > 50000:
                text = text[:50000]
            
            filename = item.get('filename', '')
            title = filename if filename else f"Document {i + len(values)}"
            
            metadata = {k: v for k, v in item.items() if k != 'text'}
            
            values.append((
                title,
                'HuggingFace_EPSTEIN_FILES_20K',
                'document',
                text,
                filename,
                json.dumps(metadata) if metadata else '{}'
            ))
        
        try:
            await conn.executemany("""
                INSERT INTO documents (title, source, type, ocr_text, original_filename, metadata)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT DO NOTHING
            """, values)
            inserted += len(values)
            print(f"Inserted {inserted}/{len(ds)} documents...")
        except Exception as e:
            print(f"Error inserting batch {i}-{i+batch_size}: {e}")
            continue
    
    await conn.close()
    print(f"\n✓ HuggingFace ingestion complete! Inserted {inserted} documents")

if __name__ == "__main__":
    asyncio.run(ingest_huggingface())


