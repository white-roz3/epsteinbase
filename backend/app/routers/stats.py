from fastapi import APIRouter, Depends
from app.database import get_pool
import asyncpg

router = APIRouter()

async def get_db_pool():
    return await get_pool()

@router.get("/stats")
async def get_stats(pool: asyncpg.Pool = Depends(get_db_pool)):
    """Get database statistics"""
    async with pool.acquire() as conn:
        # Total documents
        total = await conn.fetchval("SELECT COUNT(*) FROM documents")
        
        # Count by type
        by_type_rows = await conn.fetch("""
            SELECT type, COUNT(*) as count 
            FROM documents 
            WHERE type IS NOT NULL 
            GROUP BY type
            ORDER BY count DESC
        """)
        by_type = {row["type"]: row["count"] for row in by_type_rows}
        
        # Count by source
        by_source_rows = await conn.fetch("""
            SELECT source, COUNT(*) as count 
            FROM documents 
            GROUP BY source
            ORDER BY count DESC
        """)
        by_source = {row["source"]: row["count"] for row in by_source_rows}
        
        return {
            "total_documents": total,
            "by_type": by_type,
            "by_source": by_source
        }

@router.get("/people")
async def get_people(pool: asyncpg.Pool = Depends(get_db_pool)):
    """Get people mentioned in documents"""
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT p.name, COUNT(dp.document_id) as doc_count
            FROM people p
            JOIN document_people dp ON p.id = dp.person_id
            GROUP BY p.id, p.name
            ORDER BY doc_count DESC 
            LIMIT 100
        """)
        
        return [{"name": row["name"], "doc_count": row["doc_count"]} for row in rows]



