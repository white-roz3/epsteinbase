#!/usr/bin/env python3
"""Incrementally ingest extracted images into database as they're extracted"""
import asyncpg
import asyncio
import os
import json
from pathlib import Path
from datetime import date
import re
from time import sleep

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")

# Data directory
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
EXTRACTED_DIR = DATA_DIR / "extracted" / "COMBINED_ALL_EPSTEIN_FILES"
THUMB_DIR = DATA_DIR / "thumbnails" / "COMBINED_ALL_EPSTEIN_FILES"
PDF_NAME = "COMBINED_ALL_EPSTEIN_FILES.pdf"

def extract_efta_id(text: str) -> str:
    """Extract EFTA ID from text"""
    if not text:
        return None
    match = re.search(r'EFTA\d{8}', text)
    return match.group(0) if match else None

def classify_page_type(ocr_text: str) -> dict:
    """Classify page and extract context based on OCR text"""
    if not ocr_text:
        return {"type": "unknown", "context": None, "description": None}
    
    text_lower = ocr_text.lower()
    context = None
    description = None
    page_type = "document"
    
    # Check for photographs/photos
    if any(term in text_lower for term in ['photograph', 'photo', 'image', 'picture']):
        page_type = "photo"
        if 'clinton' in text_lower:
            context = "Contains images potentially related to Bill Clinton"
        elif 'epstein' in text_lower:
            context = "Contains images related to Jeffrey Epstein"
        elif 'flight' in text_lower or 'airplane' in text_lower:
            context = "Contains flight-related photographs"
        description = "Photograph page from Epstein files"
    
    # Check for flight logs
    elif any(term in text_lower for term in ['flight log', 'aircraft', 'passenger manifest', 'lolita express']):
        page_type = "flight_log"
        context = "Flight log or passenger manifest from Epstein's aircraft"
        description = "Flight log document"
    
    # Check for contact information
    elif any(term in text_lower for term in ['contact', 'address book', 'phone', 'email address']):
        page_type = "contact"
        context = "Contact information or address book entry"
        description = "Contact information page"
    
    # Check for financial documents
    elif any(term in text_lower for term in ['bank', 'transaction', 'wire transfer', 'payment', 'check']):
        page_type = "financial"
        context = "Financial transaction or banking document"
        description = "Financial document"
    
    # Check for emails/correspondence
    elif any(term in text_lower for term in ['from:', 'to:', 'subject:', 'sent:', 'email']):
        page_type = "email"
        context = "Email correspondence"
        description = "Email document"
    
    # Check for legal documents
    elif any(term in text_lower for term in ['court', 'judge', 'plaintiff', 'defendant', 'deposition', 'affidavit']):
        page_type = "legal"
        context = "Legal document or court filing"
        description = "Legal document"
    
    # Check for calendar/scheduling
    elif any(term in text_lower for term in ['appointment', 'schedule', 'calendar', 'meeting']):
        page_type = "calendar"
        context = "Calendar or scheduling information"
        description = "Calendar/schedule page"
    
    # Check for medical records
    elif any(term in text_lower for term in ['medical', 'prescription', 'doctor', 'hospital', 'diagnosis']):
        page_type = "medical"
        context = "Medical record or health information"
        description = "Medical document"
    
    # Check for redaction notices
    elif any(term in text_lower for term in ['redacted', 'withheld', 'privileged', 'confidential']):
        context = "Page contains redacted information"
        description = "Redacted document page"
    
    return {
        "type": page_type,
        "context": context,
        "description": description
    }

async def ingest_page(page_num: int, conn: asyncpg.Connection, source_pdf: str):
    """Ingest a single extracted page"""
    page_filename = f"page_{page_num:05d}.png"
    page_path = EXTRACTED_DIR / page_filename
    thumb_path = THUMB_DIR / page_filename
    
    if not page_path.exists():
        return False
    
    # Check if already ingested
    existing = await conn.fetchval("""
        SELECT COUNT(*) FROM documents 
        WHERE source_pdf = $1 AND page_number = $2
    """, source_pdf, page_num)
    
    if existing > 0:
        return False  # Already ingested
    
    # Try to read OCR text from saved text file
    ocr_text = None
    efta_id = None
    
    text_path = EXTRACTED_DIR / f"page_{page_num:05d}.txt"
    if text_path.exists():
        try:
            ocr_text = text_path.read_text(encoding='utf-8')[:50000]  # Limit to 50KB
            efta_id = extract_efta_id(ocr_text)
        except Exception as e:
            print(f"    Warning: Could not read text file for page {page_num}: {e}")
    else:
        # If text file doesn't exist yet, try to extract from PDF directly
        # (This is slower but works for pages extracted before text saving was added)
        try:
            import fitz
            pdf_path = DATA_DIR / "pdfs" / PDF_NAME
            if pdf_path.exists():
                doc = fitz.open(str(pdf_path))
                if page_num < len(doc):
                    page = doc[page_num]
                    text = page.get_text()
                    ocr_text = text[:50000] if text else None
                    efta_id = extract_efta_id(text) if text else None
                doc.close()
        except Exception as e:
            pass  # OCR extraction failed, continue without it
    
    # Classify page
    classification = classify_page_type(ocr_text or "")
    
    # Determine document type
    doc_type = "image"
    if classification["type"] in ["flight_log", "contact", "financial", "email", "legal", "calendar", "medical"]:
        doc_type = classification["type"]
    elif classification["type"] == "photo":
        doc_type = "image"
    
    # Build title
    title_parts = [f"Page {page_num}"]
    if efta_id:
        title_parts.insert(0, efta_id)
    if classification["description"]:
        title = f"{classification['description']} - {title_parts[0]}"
    else:
        title = f"Document {title_parts[0]}"
    
    title = f"{title} - {source_pdf}"
    
    # Build metadata
    metadata = {
        "source_pdf": source_pdf,
        "page_number": page_num,
        "classification": classification["type"],
        "has_thumbnail": thumb_path.exists()
    }
    if efta_id:
        metadata["efta_id"] = efta_id
    
    # Insert into database
    try:
        await conn.execute("""
            INSERT INTO documents 
            (efta_id, title, source, type, subtype, description, context, ocr_text, 
             file_path, thumbnail_path, page_number, source_pdf, date_released, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14::jsonb)
        """,
            efta_id,
            title,
            "DOJ",
            doc_type,
            classification["type"] if classification["type"] != "unknown" else None,
            classification["description"],
            classification["context"],
            ocr_text,
            f"extracted/COMBINED_ALL_EPSTEIN_FILES/{page_filename}",
            f"thumbnails/COMBINED_ALL_EPSTEIN_FILES/{page_filename}" if thumb_path.exists() else None,
            page_num,
            source_pdf,
            date(2025, 12, 19),
            json.dumps(metadata)
        )
        return True
    except Exception as e:
        print(f"  Error ingesting page {page_num}: {e}")
        return False

async def process_existing_images(conn: asyncpg.Connection):
    """Process all already-extracted images"""
    if not EXTRACTED_DIR.exists():
        return 0
    
    pages = sorted(EXTRACTED_DIR.glob("page_*.png"))
    print(f"\nProcessing {len(pages)} already-extracted pages...")
    
    ingested = 0
    for page_path in pages:
        # Extract page number from filename
        match = re.search(r'page_(\d+)\.png', page_path.name)
        if match:
            page_num = int(match.group(1))
            if await ingest_page(page_num, conn, PDF_NAME):
                ingested += 1
                if ingested % 100 == 0:
                    print(f"  Ingested {ingested} pages...")
    
    return ingested

async def watch_and_ingest(conn: asyncpg.Connection, watch_interval: int = 10):
    """Watch for new extracted pages and ingest them"""
    print(f"\nWatching for new pages (checking every {watch_interval} seconds)...")
    print("Press Ctrl+C to stop\n")
    
    last_count = 0
    
    try:
        while True:
            # Count current extracted pages
            if EXTRACTED_DIR.exists():
                current_pages = sorted(EXTRACTED_DIR.glob("page_*.png"))
                current_count = len(current_pages)
                
                if current_count > last_count:
                    new_pages = current_count - last_count
                    print(f"  Found {new_pages} new page(s) ({current_count} total)")
                    
                    # Process new pages
                    for page_path in current_pages[last_count:]:
                        match = re.search(r'page_(\d+)\.png', page_path.name)
                        if match:
                            page_num = int(match.group(1))
                            if await ingest_page(page_num, conn, PDF_NAME):
                                print(f"  ✓ Ingested page {page_num}")
                    
                    last_count = current_count
                elif current_count == last_count:
                    # Check if extraction is complete
                    if not any(proc for proc in os.popen("ps aux").readlines() if "extract_images.py" in proc and "grep" not in proc):
                        print("\n✓ Extraction process completed. Waiting for final pages...")
                        await asyncio.sleep(30)  # Wait a bit more
                        break
            
            await asyncio.sleep(watch_interval)
            
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")

async def main():
    print("=" * 60)
    print("INCREMENTAL IMAGE INGESTION")
    print("=" * 60)
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    try:
        # Process existing images first
        existing_count = await process_existing_images(conn)
        print(f"\n✓ Processed {existing_count} existing pages")
        
        # Then watch for new ones
        await watch_and_ingest(conn, watch_interval=5)
        
        # Final count
        total = await conn.fetchval("""
            SELECT COUNT(*) FROM documents 
            WHERE source_pdf = $1
        """, PDF_NAME)
        
        print(f"\n✓ Total pages ingested: {total}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())

