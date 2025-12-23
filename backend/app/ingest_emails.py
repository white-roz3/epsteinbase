"""Ingest emails from PDFs into database"""
import asyncio
import asyncpg
import os
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from extract_emails import extract_emails_from_pdf, ingest_emails

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")
DATA_DIR = Path(__file__).parent.parent.parent / "data"

async def ingest_emails_async(conn: asyncpg.Connection):
    """Ingest emails from PDFs into database"""
    pdf_dir = DATA_DIR / "pdfs"
    
    if not pdf_dir.exists():
        return {"error": "PDF directory not found. Make sure PDFs are downloaded first."}
    
    # Try both naming patterns
    pdf_files = sorted(list(pdf_dir.glob("DataSet_*.pdf")) + list(pdf_dir.glob("*.pdf")))
    
    # Filter out problematic files
    pdf_files = [f for f in pdf_files if not (f.name.startswith('.') or 'COMBINED_ALL' in f.name)]
    
    if not pdf_files:
        return {"error": "No PDF files found. Run download_data.py first."}
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    all_emails = []
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing {pdf_file.name}...")
            emails = extract_emails_from_pdf(pdf_file)
            all_emails.extend(emails)
            print(f"✓ {pdf_file.name}: Found {len(emails)} emails")
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
            continue
    
    print(f"\nTotal emails found: {len(all_emails)}")
    
    if not all_emails:
        return {"error": "No emails found in PDFs."}
    
    # Ingest emails using the existing function
    await ingest_emails(all_emails)
    
    return {"success": True, "emails_found": len(all_emails), "files_processed": len(pdf_files)}

