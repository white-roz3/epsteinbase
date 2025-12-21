#!/usr/bin/env python3
"""Extract individual emails from PDFs and create email documents"""
import fitz  # PyMuPDF
from pathlib import Path
import re
import json
import asyncpg
import asyncio
import os
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")

def extract_email_content(text: str) -> dict:
    """Extract email metadata and content from text"""
    email_data = {
        'subject': None,
        'from': None,
        'to': None,
        'cc': None,
        'date': None,
        'body': text,
        'is_email': False
    }
    
    # Check if this looks like an email
    text_lower = text.lower()
    has_email_patterns = any([
        'from:' in text_lower,
        'to:' in text_lower,
        'subject:' in text_lower,
        'date:' in text_lower,
        '@' in text and ('mail' in text_lower or 'email' in text_lower)
    ])
    
    if not has_email_patterns:
        return email_data
    
    email_data['is_email'] = True
    
    # Extract subject
    subject_match = re.search(r'(?i)subject[:\s]+(.+?)(?:\n|$)', text)
    if subject_match:
        email_data['subject'] = subject_match.group(1).strip()
    
    # Extract from
    from_match = re.search(r'(?i)from[:\s]+(.+?)(?:\n|$)', text)
    if from_match:
        email_data['from'] = from_match.group(1).strip()
    
    # Extract to
    to_match = re.search(r'(?i)to[:\s]+(.+?)(?:\n|$)', text)
    if to_match:
        email_data['to'] = to_match.group(1).strip()
    
    # Extract cc
    cc_match = re.search(r'(?i)cc[:\s]+(.+?)(?:\n|$)', text)
    if cc_match:
        email_data['cc'] = cc_match.group(1).strip()
    
    # Extract date
    date_match = re.search(r'(?i)(?:date|sent)[:\s]+(.+?)(?:\n|$)', text)
    if date_match:
        email_data['date'] = date_match.group(1).strip()
    
    # Extract body (everything after headers)
    body_start = max(
        text.lower().find('\n\n'),
        text.lower().find('subject:'),
        text.lower().find('from:'),
        0
    )
    if body_start > 0:
        # Find where body actually starts (after all headers)
        lines = text[body_start:].split('\n')
        body_lines = []
        in_body = False
        for line in lines:
            if in_body or not any([line.strip().startswith(prefix) for prefix in ['From:', 'To:', 'Subject:', 'Date:', 'CC:', 'Cc:']]):
                if line.strip() or in_body:
                    in_body = True
                    body_lines.append(line)
        email_data['body'] = '\n'.join(body_lines).strip()
    
    return email_data

def generate_email_title(email_data: dict) -> str:
    """Generate a contextual title for the email"""
    subject = (email_data.get('subject') or '').strip() if email_data.get('subject') else ''
    from_addr = (email_data.get('from') or '').strip() if email_data.get('from') else ''
    to_addr = (email_data.get('to') or '').strip() if email_data.get('to') else ''
    
    # Use subject if available
    if subject and len(subject) > 5 and len(subject) < 200:
        title = subject
    else:
        # Create title from from/to
        if from_addr and to_addr:
            # Extract name or email
            from_name = from_addr.split('<')[0].strip() if '<' in from_addr else from_addr
            to_name = to_addr.split('<')[0].strip() if '<' in to_addr else to_addr
            title = f"Email from {from_name} to {to_name}"
        elif from_addr:
            from_name = from_addr.split('<')[0].strip() if '<' in from_addr else from_addr
            title = f"Email from {from_name}"
        elif to_addr:
            to_name = to_addr.split('<')[0].strip() if '<' in to_addr else to_addr
            title = f"Email to {to_name}"
        else:
            # Fallback to first line of body
            body_preview = email_data.get('body', '')[:100].strip().split('\n')[0]
            title = f"Email: {body_preview}" if body_preview else "Untitled Email"
    
    # Clean up title
    title = re.sub(r'\s+', ' ', title)  # Multiple spaces to single
    title = title[:200]  # Limit length
    
    return title

def extract_emails_from_pdf(pdf_path: Path) -> list:
    """Extract individual emails from a PDF"""
    doc = fitz.open(pdf_path)
    pdf_name = pdf_path.stem
    emails = []
    
    print(f"Processing {pdf_path.name} ({len(doc)} pages)...")
    
    current_email = None
    
    for page_num in range(len(doc)):
        try:
            page = doc[page_num]
            text = page.get_text()
            
            if not text or len(text.strip()) < 50:
                continue
            
            # Check if this page contains an email
            email_data = extract_email_content(text)
            
            if email_data and email_data.get('is_email'):
                # This looks like an email - extract it
                title = generate_email_title(email_data)
                
                email_record = {
                    'source_pdf': pdf_path.name,
                    'page_number': page_num,
                    'title': title,
                    'subject': email_data.get('subject'),
                    'from': email_data.get('from'),
                    'to': email_data.get('to'),
                    'cc': email_data.get('cc'),
                    'date': email_data.get('date'),
                    'body': email_data.get('body', ''),
                    'ocr_text': text,  # Full text for search
                    'efta_id': extract_efta_id(text)
                }
                
                emails.append(email_record)
        except Exception as e:
            print(f"  Error processing page {page_num}: {e}")
            continue
        
        if (page_num + 1) % 100 == 0:
            print(f"  Processed {page_num + 1}/{len(doc)} pages, found {len(emails)} emails...")
    
    doc.close()
    return emails

def extract_efta_id(text: str) -> str | None:
    """Extract EFTA ID from text if present"""
    match = re.search(r'EFTA\d{8}', text)
    return match.group(0) if match else None

async def ingest_emails(emails: list):
    """Ingest extracted emails into database"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    print(f"\nIngesting {len(emails)} emails into database...")
    
    batch_size = 100
    inserted = 0
    
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i+batch_size]
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
            
            # Truncate title if too long (database limit is TEXT but be reasonable)
            title = email['title'][:500] if len(email['title']) > 500 else email['title']
            description = (description[:500] if description and len(description) > 500 else description) if description else None
            context = (context[:1000] if context and len(context) > 1000 else context) if context else None
            
            values.append((
                email.get('efta_id'),
                title,
                f"DOJ_{dataset_name}"[:50],  # Ensure source fits VARCHAR(50)
                'email',
                description,
                context,
                (email.get('ocr_text', '')[:50000] if email.get('ocr_text') else None),  # Limit OCR text
                email['page_number'],
                email['source_pdf'][:500] if len(email['source_pdf']) > 500 else email['source_pdf'],
                json.dumps(metadata),
                datetime(2025, 12, 19).date()  # Release date
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
        print(f"  Inserted {inserted}/{len(emails)} emails...")
    
    await conn.close()
    print(f"✓ Ingested {inserted} emails")

async def main():
    pdf_dir = DATA_DIR / "pdfs"
    # Try both naming patterns
    pdf_files = sorted(list(pdf_dir.glob("DataSet_*.pdf")) + list(pdf_dir.glob("*.pdf")))
    
    if not pdf_files:
        print("No PDF files found. Run download_data.py first.")
        return
    
    all_emails = []
    
    for pdf_file in pdf_files:
        if pdf_file.name.startswith('.') or 'COMBINED_ALL' in pdf_file.name:
            print(f"⚠ Skipping {pdf_file.name} (too large or problematic)")
            continue
        try:
            emails = extract_emails_from_pdf(pdf_file)
            all_emails.extend(emails)
            print(f"✓ {pdf_file.name}: Found {len(emails)} emails")
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
            continue
    
    print(f"\nTotal emails found: {len(all_emails)}")
    
    if all_emails:
        await ingest_emails(all_emails)
    else:
        print("No emails found in PDFs.")

if __name__ == "__main__":
    asyncio.run(main())
