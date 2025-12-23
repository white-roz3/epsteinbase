#!/usr/bin/env python3
"""Extract people from image metadata and populate people table"""
import asyncpg
import asyncio
import os
import json
from collections import defaultdict

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")

async def extract_and_populate_people():
    """Extract people from image metadata and create people entries"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    print("Extracting people from image metadata...")
    
    # Get all images with metadata
    rows = await conn.fetch("""
        SELECT id, metadata
        FROM documents 
        WHERE type = 'image' AND metadata IS NOT NULL
    """)
    
    # Collect people with document counts
    people_docs = defaultdict(set)
    
    for row in rows:
        metadata = row['metadata']
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                continue
        
        detected_people = metadata.get('detected_people', [])
        for person_name in detected_people:
            if person_name and isinstance(person_name, str):
                people_docs[person_name].add(row['id'])
    
    print(f"Found {len(people_docs)} unique people")
    
    # Insert/update people and document_people relationships
    inserted_people = 0
    inserted_relations = 0
    
    for person_name, doc_ids in people_docs.items():
        # Insert or get person
        person_id = await conn.fetchval("""
            INSERT INTO people (name, description)
            VALUES ($1, $2)
            ON CONFLICT (name) DO UPDATE SET name = people.name
            RETURNING id
        """, person_name, f"Person detected in {len(doc_ids)} images")
        
        if not person_id:
            person_id = await conn.fetchval("SELECT id FROM people WHERE name = $1", person_name)
        
        # Insert document_people relationships
        for doc_id in doc_ids:
            try:
                await conn.execute("""
                    INSERT INTO document_people (document_id, person_id)
                    VALUES ($1, $2)
                    ON CONFLICT DO NOTHING
                """, doc_id, person_id)
                inserted_relations += 1
            except:
                pass
        
        inserted_people += 1
        if inserted_people % 10 == 0:
            print(f"  Processed {inserted_people} people...")
    
    await conn.close()
    print(f"\n✓ Inserted/updated {inserted_people} people")
    print(f"✓ Created {inserted_relations} document-person relationships")

if __name__ == "__main__":
    asyncio.run(extract_and_populate_people())



