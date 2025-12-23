"""Ingest emails from PDFs into database"""
import asyncio
import asyncpg
import os
from pathlib import Path
import sys
import json
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")
DATA_DIR = Path(__file__).parent.parent.parent / "data"

async def ingest_emails_async(conn: asyncpg.Connection):
    """Ingest emails from PDFs into database"""
    try:
        from extract_emails import extract_emails_from_pdf
    except ImportError:
        return {"error": "Email extraction module not available. PyMuPDF may not be installed."}
    
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
    
    # Ingest emails directly
    batch_size = 100
    inserted = 0
    
    for i in range(0, len(all_emails), batch_size):
        batch = all_emails[i:i+batch_size]
        values = []
        
        for email in batch:
            dataset_name = email['source_pdf'].replace('.pdf', '').replace('_COMPLETE', '')
            
            # Build description from email metadata
            desc_parts = []
            if email.get('from'):
                desc_parts.append(f"From: {email['from']}")
            if email.get('to'):
                desc_parts.append(f"To: {email['to']}")
            if email.get('date'):
                desc_parts.append(f"Date: {email['date']}")
            
            description = ' | '.join(desc_parts) if desc_parts else None
            
            # Build context from subject and first part of body
            context_parts = []
            if email.get('subject'):
                context_parts.append(f"Subject: {email['subject']}")
            body_preview = email.get('body', '')[:200]
            if body_preview:
                context_parts.append(body_preview)
            context = ' | '.join(context_parts) if context_parts else None
            
            # Store email metadata in metadata JSON
            metadata = {
                'from': email.get('from'),
                'to': email.get('to'),
                'cc': email.get('cc'),
                'subject': email.get('subject'),
                'date': email.get('date'),
                'source_pdf': email['source_pdf'],
                'page_number': email['page_number']
            }
            
            # Truncate fields
            title = email['title'][:500] if len(email['title']) > 500 else email['title']
            description = (description[:500] if description and len(description) > 500 else description) if description else None
            context = (context[:1000] if context and len(context) > 1000 else context) if context else None
            
            values.append((
                email.get('efta_id'),
                title,
                f"DOJ_{dataset_name}"[:50],
                'email',
                description,
                context,
                (email.get('ocr_text', '')[:50000] if email.get('ocr_text') else None),
                email['page_number'],
                email['source_pdf'][:500] if len(email['source_pdf']) > 500 else email['source_pdf'],
                json.dumps(metadata),
                datetime(2025, 12, 19).date()
            ))
        
        await conn.executemany("""
            INSERT INTO documents (
                efta_id, title, source, type, description, context, ocr_text,
                page_number, source_pdf, metadata, date_released
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT DO NOTHING
        """, values)
        
        inserted += len(batch)
        print(f"  Inserted {inserted}/{len(all_emails)} emails...")
    
    return {"success": True, "emails_found": len(all_emails), "emails_inserted": inserted, "files_processed": len(pdf_files)}

