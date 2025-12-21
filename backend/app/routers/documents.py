from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.database import get_pool
import asyncpg

router = APIRouter()

async def get_db_pool():
    return await get_pool()

@router.get("/documents")
async def get_documents(
    type: Optional[str] = None,
    source: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Get documents with optional filtering"""
    async with pool.acquire() as conn:
        where_clauses = []
        params = []
        param_idx = 1
        
        if type and type != 'all':
            where_clauses.append(f"type = ${param_idx}")
            params.append(type)
            param_idx += 1
            
        if source:
            where_clauses.append(f"source ILIKE ${param_idx}")
            params.append(f"%{source}%")
            param_idx += 1
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        total_query = f"SELECT COUNT(*) FROM documents WHERE {where_sql}"
        total = await conn.fetchval(total_query, *params)
        
        # Get paginated results
        params.extend([per_page, (page - 1) * per_page])
        results_query = f"""
            SELECT id, efta_id, title, source, type, subtype, description, context,
                   file_path, thumbnail_path, ocr_text, metadata, date_released
            FROM documents 
            WHERE {where_sql}
            ORDER BY id DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        
        rows = await conn.fetch(results_query, *params)
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "efta_id": row["efta_id"],
                "title": row["title"],
                "source": row["source"],
                "type": row["type"],
                "subtype": row["subtype"],
                "description": row["description"],
                "context": row["context"],
                "file_path": row["file_path"],
                "thumbnail_path": row["thumbnail_path"],
                "ocr_text": row["ocr_text"],
                "metadata": row["metadata"] or {},
                "date_released": row["date_released"].isoformat() if row["date_released"] else None,
            })
        
        return {
            "results": results,
            "total": total,
            "page": page,
            "per_page": per_page
        }

@router.get("/documents/{doc_id}")
async def get_document(
    doc_id: int,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Get a single document by ID"""
    async with pool.acquire() as conn:
        # Get document with related people
        row = await conn.fetchrow("""
            SELECT d.*, 
                   COALESCE(
                       array_agg(p.name) FILTER (WHERE p.name IS NOT NULL),
                       ARRAY[]::text[]
                   ) as people
            FROM documents d
            LEFT JOIN document_people dp ON d.id = dp.document_id
            LEFT JOIN people p ON dp.person_id = p.id
            WHERE d.id = $1
            GROUP BY d.id
        """, doc_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": row["id"],
            "efta_id": row["efta_id"],
            "title": row["title"],
            "source": row["source"],
            "type": row["type"],
            "subtype": row["subtype"],
            "description": row["description"],
            "context": row["context"],
            "ocr_text": row["ocr_text"],
            "original_filename": row["original_filename"],
            "file_path": row["file_path"],
            "thumbnail_path": row["thumbnail_path"],
            "file_size_bytes": row["file_size_bytes"],
            "mime_type": row["mime_type"],
            "page_number": row["page_number"],
            "source_pdf": row["source_pdf"],
            "metadata": row["metadata"] or {},
            "date_original": row["date_original"].isoformat() if row["date_original"] else None,
            "date_released": row["date_released"].isoformat() if row["date_released"] else None,
            "people": row["people"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }


