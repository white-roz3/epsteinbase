#!/usr/bin/env python3
"""Ingest sample data directly into database - quick way to populate with known files"""
import asyncpg
import asyncio
import os
import json
from datetime import date

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")

SAMPLE_VIDEOS = [
    {
        "title": "MCC Cell Block Surveillance - Raw Footage",
        "source": "DOJ",
        "type": "video",
        "date": "2019-08-09",
        "duration": "12+ hours",
        "url": "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video1.mp4",
        "location": "Metropolitan Correctional Center, New York",
        "description": "Unedited surveillance footage from the Special Housing Unit (SHU) tier where Jeffrey Epstein was held.",
        "context": "July 2025 FBI memo concluded no one entered Epstein's cell. Guards later charged with falsifying records.",
        "file_path": "videos/video1.mp4",
        "date_released": "2025-12-19"
    },
    {
        "title": "MCC Surveillance - Enhanced Version",
        "source": "DOJ",
        "type": "video",
        "date": "2019-08-09",
        "duration": "12+ hours",
        "url": "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video2.mp4",
        "location": "Metropolitan Correctional Center, New York",
        "description": "Digitally enhanced version with improved visibility for the low-light corridor footage.",
        "context": "DOJ released both raw and enhanced versions to address claims the original was too dark.",
        "file_path": "videos/video2.mp4",
        "date_released": "2025-12-19"
    },
]

SAMPLE_AUDIO = [
    {"title": "Maxwell Proffer - Day 1, Part 1", "file": "Day_1_-_Part_1", "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 2", "file": "Day_1_-_Part_2", "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 3", "file": "Day_1_-_Part_3", "redacted": True, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 4", "file": "Day_1_-_Part_4", "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 5", "file": "Day_1_-_Part_5", "redacted": True, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 6", "file": "Day_1_-_Part_6", "redacted": True, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 1, Part 7", "file": "Day_1_-_Part_7", "redacted": False, "date": "2025-07-24"},
    {"title": "Maxwell Proffer - Day 2, Part 1", "file": "Day_2_-_Part_1", "redacted": True, "date": "2025-07-25"},
    {"title": "Maxwell Proffer - Day 2, Part 2", "file": "Day_2_-_Part_2", "redacted": True, "date": "2025-07-25"},
    {"title": "Maxwell Proffer - Day 2, Part 3", "file": "Day_2_-_Part_3", "redacted": False, "date": "2025-07-25"},
    {"title": "Maxwell Proffer - Day 2, Part 4", "file": "Day_2_-_Part_4", "redacted": True, "date": "2025-07-25"},
]

SAMPLE_IMAGES = [
    {
        "title": "Clinton in Hot Tub",
        "description": "Former President Bill Clinton in a hot tub. Another person present but face redacted by DOJ.",
        "context": "Clinton acknowledged flying on Epstein's plane but denied knowledge of criminal activity.",
        "people": ["Bill Clinton", "[Redacted]"]
    },
    {
        "title": "Clinton and Epstein Standing Together",
        "people": ["Bill Clinton", "Jeffrey Epstein"]
    },
    {
        "title": "Epstein with Michael Jackson",
        "description": "Epstein standing with Michael Jackson in front of artwork.",
        "people": ["Jeffrey Epstein", "Michael Jackson"]
    },
    {
        "title": "Clinton with Kevin Spacey - Churchill War Rooms",
        "description": "Clinton in London with Kevin Spacey inside the Cabinet Room of the Churchill War Rooms.",
        "people": ["Bill Clinton", "Kevin Spacey", "Doug Band"],
        "context": "From Clinton's 2002 Africa trip aboard Epstein's jet with Spacey and Chris Tucker."
    },
    {
        "title": "Epstein with Walter Cronkite",
        "people": ["Jeffrey Epstein", "Walter Cronkite"],
        "context": "Cronkite was 'the most trusted man in America.' Shows Epstein's media access."
    },
    {
        "title": "Framed Trump Check",
        "description": "Framed check from Trump to Epstein with caption 'once in a blue moon.'",
        "people": ["Donald Trump", "Jeffrey Epstein"],
        "context": "Found among estate photos. Trump has denied inappropriate relationship with Epstein."
    },
]

SAMPLE_DOCUMENTS = [
    {
        "title": "Flight Logs (Lolita Express)",
        "subtype": "Evidence",
        "format": "PDF",
        "url": "https://www.justice.gov/multimedia/DOJ%20Disclosures/First%20Phase%20of%20Declassified%20Epstein%20Files/B.%20Flight%20Log%20Released%20in%20US%20v.%20Maxwell,%201.20-cr-00330%20(SDNY%202020).pdf",
        "description": "Flight logs from Epstein's Boeing 727 showing passengers and destinations.",
    },
    {
        "title": "Contact Book (Black Book)",
        "subtype": "Evidence",
        "format": "PDF - Redacted",
        "url": "https://www.justice.gov/multimedia/DOJ%20Disclosures/First%20Phase%20of%20Declassified%20Epstein%20Files/C.%20Contact%20Book%20(Redacted).pdf",
        "description": "Personal contact book. Unredacted version reportedly has 1,500+ names.",
        "redacted": True
    },
    {
        "title": "DOJ/FBI Memo on BOP Footage",
        "subtype": "Memo",
        "format": "PDF",
        "url": "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/2025.07%20DOJ%20FBI%20Memorandum.pdf",
        "description": "Concludes no evidence Epstein was murdered or kept a 'client list.'",
    },
    {
        "title": "EPSTEIN_FILES_20K Dataset",
        "subtype": "Dataset",
        "format": "CSV (106MB)",
        "url": "https://huggingface.co/datasets/tensonaut/EPSTEIN_FILES_20K",
        "description": "25,000+ OCR'd documents in single CSV for analysis and search.",
        "source": "HuggingFace"
    },
    {
        "title": "Combined All Files (Searchable)",
        "subtype": "Archive",
        "format": "PDF (6GB)",
        "url": "https://archive.org/details/combined-all-epstein-files",
        "description": "All DOJ DataSets 1-7 combined into searchable PDFs by researchers.",
        "source": "Internet Archive"
    },
]

SAMPLE_EMAILS = [
    {
        "title": "Epstein Estate Email Archive",
        "source": "House Oversight",
        "description": "20,000+ pages of emails from estate.",
        "url": "https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/",
        "date_released": "2025-11-12"
    },
    {
        "title": "Structured Email Dataset",
        "source": "HuggingFace",
        "description": "Vision LLM-processed emails with SQLite database.",
        "url": "https://huggingface.co/datasets/to-be/epstein-emails",
    },
]

async def ingest_videos():
    conn = await asyncpg.connect(DATABASE_URL)
    inserted = 0
    
    for video in SAMPLE_VIDEOS:
        try:
            await conn.execute("""
                INSERT INTO documents 
                (title, source, type, file_path, url, description, context, location, duration, date_released, downloadable)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT DO NOTHING
            """, 
                video['title'], video['source'], video['type'], 
                video.get('file_path'), video['url'], video['description'], 
                video.get('context'), video['location'], video['duration'],
                date.fromisoformat(video['date_released']), True
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting {video['title']}: {e}")
    
    await conn.close()
    print(f"✓ Inserted {inserted} videos")

async def ingest_audio():
    conn = await asyncpg.connect(DATABASE_URL)
    inserted = 0
    
    for audio in SAMPLE_AUDIO:
        try:
            metadata = json.dumps({"session_date": audio['date'], "redacted": audio['redacted']})
            await conn.execute("""
                INSERT INTO documents 
                (title, source, type, description, location, redacted, date_released, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                ON CONFLICT DO NOTHING
            """,
                audio['title'], 'DOJ', 'audio',
                "Maxwell proffer session recording with DOJ prosecutors",
                "FCI Tallahassee",
                audio['redacted'],
                date.fromisoformat(audio['date']),
                metadata
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting {audio['title']}: {e}")
    
    await conn.close()
    print(f"✓ Inserted {inserted} audio files")

async def ingest_images():
    conn = await asyncpg.connect(DATABASE_URL)
    inserted = 0
    
    for image in SAMPLE_IMAGES:
        try:
            metadata = json.dumps({"people": image.get('people', [])})
            await conn.execute("""
                INSERT INTO documents 
                (title, source, type, description, context, date_released, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                ON CONFLICT DO NOTHING
            """,
                image['title'], 'DOJ', 'image',
                image.get('description'),
                image.get('context'),
                date(2025, 12, 19),
                metadata
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting {image['title']}: {e}")
    
    await conn.close()
    print(f"✓ Inserted {inserted} images")

async def ingest_documents():
    conn = await asyncpg.connect(DATABASE_URL)
    inserted = 0
    
    for doc in SAMPLE_DOCUMENTS:
        try:
            source = doc.get('source', 'DOJ')
            metadata = json.dumps({"format": doc.get('format')})
            await conn.execute("""
                INSERT INTO documents 
                (title, source, type, subtype, description, url, downloadable, redacted, date_released, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb)
                ON CONFLICT DO NOTHING
            """,
                doc['title'], source, 'document', doc.get('subtype'),
                doc.get('description'), doc.get('url'), True,
                doc.get('redacted', False), date(2025, 12, 19), metadata
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting {doc['title']}: {e}")
    
    await conn.close()
    print(f"✓ Inserted {inserted} documents")

async def ingest_emails():
    conn = await asyncpg.connect(DATABASE_URL)
    inserted = 0
    
    for email in SAMPLE_EMAILS:
        try:
            source = email.get('source', 'House Oversight')
            date_released = date.fromisoformat(email.get('date_released', '2025-11-12'))
            await conn.execute("""
                INSERT INTO documents 
                (title, source, type, description, url, downloadable, date_released)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT DO NOTHING
            """,
                email['title'], source, 'email',
                email.get('description'), email.get('url'), False, date_released
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting {email['title']}: {e}")
    
    await conn.close()
    print(f"✓ Inserted {inserted} emails")

async def main():
    print("=== Ingesting Sample Data ===\n")
    
    print("Videos:")
    await ingest_videos()
    
    print("\nAudio:")
    await ingest_audio()
    
    print("\nImages:")
    await ingest_images()
    
    print("\nDocuments:")
    await ingest_documents()
    
    print("\nEmails:")
    await ingest_emails()
    
    print("\n✓ Sample data ingestion complete!")
    
    # Show stats
    conn = await asyncpg.connect(DATABASE_URL)
    total = await conn.fetchval("SELECT COUNT(*) FROM documents")
    by_type = await conn.fetch("SELECT type, COUNT(*) as count FROM documents WHERE type IS NOT NULL GROUP BY type")
    await conn.close()
    
    print(f"\nTotal documents in database: {total}")
    print("By type:")
    for row in by_type:
        print(f"  {row['type']}: {row['count']}")

if __name__ == "__main__":
    asyncio.run(main())



