#!/usr/bin/env python3
"""Initialize Render database schema using DATABASE_URL environment variable"""
import os
import asyncpg
import asyncio
from pathlib import Path

# Get DATABASE_URL from environment (should be set by Render)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    print("Render should set this automatically when database is linked")
    exit(1)

# Read schema file
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
SCHEMA_FILE = PROJECT_ROOT / "backend" / "init.sql"

if not SCHEMA_FILE.exists():
    print(f"Error: Schema file not found: {SCHEMA_FILE}")
    exit(1)

async def init_schema():
    """Initialize database schema"""
    print(f"Connecting to database...")
    print(f"DATABASE_URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'}")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected to database")
        
        # Read and execute schema
        print(f"Reading schema from: {SCHEMA_FILE}")
        schema_sql = SCHEMA_FILE.read_text()
        
        print("Executing schema...")
        await conn.execute(schema_sql)
        
        print("✓ Schema initialized successfully!")
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"\nCreated tables: {', '.join([t['table_name'] for t in tables])}")
        
        await conn.close()
        
    except asyncpg.exceptions.DuplicateTableError as e:
        print(f"⚠ Warning: Some tables already exist: {e}")
        print("Schema may have already been initialized")
    except Exception as e:
        print(f"✗ Error initializing schema: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_schema())

