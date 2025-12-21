from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.database import get_pool
import asyncpg

router = APIRouter()

async def get_db_pool():
    return await get_pool()

@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Full-text search across documents"""
    if not q or len(q.strip()) == 0:
        return {
            "results": [],
            "total": 0,
            "page": page,
            "per_page": per_page
        }
    
    async with pool.acquire() as conn:
        type_filter = f"AND type = '{type.replace(\"'\", \"''\")}'" if type and type != 'all' else ""
        
        # Search query using PostgreSQL full-text search
        search_query = f"""
            SELECT id, efta_id, title, source, type, description, file_path, thumbnail_path,
                   ts_rank(
                       to_tsvector('english', COALESCE(ocr_text, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(title, '')),
                       plainto_tsquery('english', $1)
                   ) as rank,
                   ts_headline('english', COALESCE(ocr_text, ''), plainto_tsquery('english', $1), 'MaxWords=30, MinWords=10') as snippet
            FROM documents
            WHERE to_tsvector('english', COALESCE(ocr_text, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(title, ''))
                  @@ plainto_tsquery('english', $1)
            {type_filter}
            ORDER BY rank DESC, id DESC
            LIMIT $2 OFFSET $3
        """
        
        rows = await conn.fetch(search_query, q, per_page, (page - 1) * per_page)
        
        count_query = f"""
            SELECT COUNT(*) 
            FROM documents
            WHERE to_tsvector('english', COALESCE(ocr_text, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(title, ''))
                  @@ plainto_tsquery('english', $1)
            {type_filter}
        """
        
        total = await conn.fetchval(count_query, q)
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "efta_id": row["efta_id"],
                "title": row["title"],
                "source": row["source"],
                "type": row["type"],
                "description": row["description"],
                "file_path": row["file_path"],
                "thumbnail_path": row["thumbnail_path"],
                "snippet": row["snippet"],
                "rank": float(row["rank"]) if row["rank"] else 0.0,
            })
        
        return {
            "results": results,
            "total": total,
            "page": page,
            "per_page": per_page
        }


