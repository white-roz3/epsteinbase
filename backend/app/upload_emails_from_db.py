"""Upload emails from offline database to Render database"""
import asyncio
import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime
import asyncpg

async def upload_emails_from_db_async(conn: asyncpg.Connection, db_path: str = None):
    """Read emails from SQLite database and upload to PostgreSQL"""
    
    # Default database path
    if not db_path:
        db_path = os.getenv("OFFLINE_DB_PATH", "emails.db")
    
    db_file = Path(db_path)
    if not db_file.exists():
        # Try in data directory
        db_file = Path(__file__).parent.parent.parent / "data" / db_path
        if not db_file.exists():
            return {"error": f"Database file not found: {db_path}. Please provide the path to your email database file."}
    
    print(f"Connecting to offline database: {db_file}")
    
    try:
        offline_db = sqlite3.connect(str(db_file))
        offline_db.row_factory = sqlite3.Row
    except Exception as e:
        return {"error": f"Failed to connect to database: {e}"}
    
    try:
        # Try different table names
        table_names = ['emails', 'email', 'documents', 'messages', 'email_data']
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
            return {"error": f"Email table not found. Available tables: {tables}. Please specify the correct table name."}
        
        # Fetch emails
        print(f"Fetching emails from {emails_table}...")
        cursor = offline_db.execute(f"SELECT * FROM {emails_table}")
        rows = cursor.fetchall()
        
        if not rows:
            return {"error": "No emails found in database"}
        
        print(f"Found {len(rows)} emails to upload")
        
        batch_size = 100
        inserted = 0
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            values = []
            
            for row in batch:
                email_data = dict(row)
                
                # Map common field names (case-insensitive)
                subject = next((email_data.get(k) for k in ['subject', 'Subject', 'title', 'Title'] if k in email_data), None)
                from_addr = next((email_data.get(k) for k in ['from', 'From', 'sender', 'Sender', 'from_address'] if k in email_data), None)
                to_addr = next((email_data.get(k) for k in ['to', 'To', 'recipient', 'Recipient', 'to_address'] if k in email_data), None)
                cc_addr = next((email_data.get(k) for k in ['cc', 'CC', 'Cc'] if k in email_data), None)
                body = next((email_data.get(k) for k in ['body', 'Body', 'content', 'Content', 'text', 'Text', 'message'] if k in email_data), None)
                date_str = next((email_data.get(k) for k in ['date', 'Date', 'sent_date', 'created_at', 'timestamp'] if k in email_data), None)
                efta_id = email_data.get('efta_id') or email_data.get('EFTA_ID')
                source = email_data.get('source') or 'DOJ'
                
                # Generate title
                title = subject[:500] if subject else (f"Email from {from_addr}" if from_addr else "Untitled Email")
                
                # Build description
                desc_parts = []
                if from_addr:
                    desc_parts.append(f"From: {from_addr}")
                if to_addr:
                    desc_parts.append(f"To: {to_addr}")
                if date_str:
                    desc_parts.append(f"Date: {date_str}")
                description = ' | '.join(desc_parts) if desc_parts else None
                
                # Build context
                context_parts = []
                if subject:
                    context_parts.append(f"Subject: {subject}")
                if body:
                    body_preview = str(body)[:200]
                    context_parts.append(body_preview)
                context = ' | '.join(context_parts) if context_parts else None
                
                # Metadata
                metadata = {
                    'from': from_addr,
                    'to': to_addr,
                    'cc': cc_addr,
                    'subject': subject,
                    'date': str(date_str) if date_str else None,
                }
                
                # Parse date
                date_released = datetime(2025, 12, 19).date()
                if date_str:
                    try:
                        date_str_clean = str(date_str)[:10]
                        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']:
                            try:
                                date_released = datetime.strptime(date_str_clean, fmt).date()
                                break
                            except:
                                continue
                    except:
                        pass
                
                # Limit sizes
                ocr_text = (str(body)[:50000] if body else None)
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
                print(f"  Error inserting batch: {e}")
                continue
        
        return {
            "success": True,
            "emails_found": len(rows),
            "emails_inserted": inserted
        }
        
    finally:
        offline_db.close()

