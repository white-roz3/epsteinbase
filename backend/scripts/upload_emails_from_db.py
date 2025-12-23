#!/usr/bin/env python3
"""Upload emails from offline database (SQLite) to Render PostgreSQL database"""
import asyncio
import asyncpg
import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime

# Database paths
OFFLINE_DB_PATH = os.getenv("OFFLINE_DB_PATH", "emails.db")  # Path to your offline SQLite database
RENDER_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")

async def upload_emails_from_sqlite():
    """Read emails from SQLite and upload to PostgreSQL"""
    
    # Check if offline DB exists
    if not Path(OFFLINE_DB_PATH).exists():
        print(f"Error: Database file not found: {OFFLINE_DB_PATH}")
        print(f"Please set OFFLINE_DB_PATH environment variable to your database file path")
        return
    
    print(f"Connecting to offline database: {OFFLINE_DB_PATH}")
    offline_db = sqlite3.connect(OFFLINE_DB_PATH)
    offline_db.row_factory = sqlite3.Row  # Enable column access by name
    
    # Try different table names
    table_names = ['emails', 'email', 'documents', 'messages']
    emails_table = None
    
    for table in table_names:
        try:
            cursor = offline_db.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                emails_table = table
                print(f"Found emails table: {table}")
                break
        except:
            continue
    
    if not emails_table:
        # List all tables
        cursor = offline_db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Available tables: {tables}")
        print("Please specify the table name containing emails")
        return
    
    # Fetch emails from offline database
    print(f"Fetching emails from {emails_table}...")
    cursor = offline_db.execute(f"SELECT * FROM {emails_table}")
    rows = cursor.fetchall()
    
    if not rows:
        print("No emails found in offline database")
        return
    
    print(f"Found {len(rows)} emails to upload")
    
    # Connect to Render PostgreSQL
    print(f"Connecting to Render database...")
    conn = await asyncpg.connect(RENDER_DATABASE_URL)
    
    try:
        batch_size = 100
        inserted = 0
        skipped = 0
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            values = []
            
            for row in batch:
                # Extract email data - try common column names
                email_data = dict(row)
                
                # Map common field names
                subject = email_data.get('subject') or email_data.get('Subject') or email_data.get('title') or email_data.get('Title')
                from_addr = email_data.get('from') or email_data.get('From') or email_data.get('sender') or email_data.get('Sender')
                to_addr = email_data.get('to') or email_data.get('To') or email_data.get('recipient') or email_data.get('Recipient')
                cc_addr = email_data.get('cc') or email_data.get('CC') or email_data.get('Cc')
                body = email_data.get('body') or email_data.get('Body') or email_data.get('content') or email_data.get('Content') or email_data.get('text') or email_data.get('Text')
                date_str = email_data.get('date') or email_data.get('Date') or email_data.get('sent_date') or email_data.get('created_at')
                efta_id = email_data.get('efta_id') or email_data.get('EFTA_ID')
                source = email_data.get('source') or 'DOJ'
                
                # Generate title from subject
                title = subject[:500] if subject else f"Email from {from_addr}" if from_addr else "Untitled Email"
                
                # Build description
                desc_parts = []
                if from_addr:
                    desc_parts.append(f"From: {from_addr}")
                if to_addr:
                    desc_parts.append(f"To: {to_addr}")
                if date_str:
                    desc_parts.append(f"Date: {date_str}")
                description = ' | '.join(desc_parts) if desc_parts else None
                
                # Build context (subject + body preview)
                context_parts = []
                if subject:
                    context_parts.append(f"Subject: {subject}")
                if body:
                    body_preview = body[:200] if isinstance(body, str) else str(body)[:200]
                    context_parts.append(body_preview)
                context = ' | '.join(context_parts) if context_parts else None
                
                # Store full email metadata
                metadata = {
                    'from': from_addr,
                    'to': to_addr,
                    'cc': cc_addr,
                    'subject': subject,
                    'date': date_str,
                }
                
                # Parse date if string
                date_released = datetime(2025, 12, 19).date()  # Default
                if date_str:
                    try:
                        # Try parsing common date formats
                        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']:
                            try:
                                date_released = datetime.strptime(str(date_str)[:10], fmt).date()
                                break
                            except:
                                continue
                    except:
                        pass
                
                # Limit text sizes
                ocr_text = (body[:50000] if body and isinstance(body, str) else str(body)[:50000] if body else None)
                title = title[:500] if len(title) > 500 else title
                description = (description[:500] if description and len(description) > 500 else description) if description else None
                context = (context[:1000] if context and len(context) > 1000 else context) if context else None
                
                values.append((
                    efta_id,
                    title,
                    source[:50],
                    'email',
                    description,
                    context,
                    ocr_text,
                    None,  # page_number
                    None,  # source_pdf
                    json.dumps(metadata),
                    date_released
                ))
            
            # Insert batch
            try:
                await conn.executemany("""
                    INSERT INTO documents (
                        efta_id, title, source, type, description, context, ocr_text,
                        page_number, source_pdf, metadata, date_released
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT DO NOTHING
                """, values)
                inserted += len(values)
                print(f"  Inserted {inserted}/{len(rows)} emails...")
            except Exception as e:
                print(f"  Error inserting batch {i}-{i+batch_size}: {e}")
                skipped += len(values)
                continue
        
        print(f"\n✓ Upload complete!")
        print(f"  Inserted: {inserted}")
        print(f"  Skipped: {skipped}")
        
    finally:
        await conn.close()
        offline_db.close()

if __name__ == "__main__":
    asyncio.run(upload_emails_from_sqlite())

