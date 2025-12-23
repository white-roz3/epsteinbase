from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
import asyncpg
import os
import json
from pathlib import Path
from glob import glob
from .b2_client import get_file_url, list_files, get_b2_url, list_b2_files  # Backward compat

app = FastAPI(title="EpsteinBase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://localhost:5175",
        "https://epsteinbase.xyz",
        "https://www.epsteinbase.xyz",
        "https://epsteinbase-*.vercel.app",  # Vercel preview deployments
        "*"  # Allow all for now, can restrict later
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve extracted images/files statically (only if not using B2)
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
EXTRACTED_DIR = DATA_DIR / "extracted"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"

# Only mount filesystem static files if not using B2 or R2 (for local dev)
if not os.getenv("B2_APPLICATION_KEY_ID") and not os.getenv("R2_ACCESS_KEY_ID"):
    app.mount("/files", StaticFiles(directory=str(DATA_DIR)), name="files")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/epsteinbase")

@app.on_event("startup")
async def startup():
    try:
        app.state.pool = await asyncpg.create_pool(DATABASE_URL)
        app.state.db_connected = True
        
        # Auto-initialize schema if tables don't exist
        async with app.state.pool.acquire() as conn:
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'documents'
            """)
            
            if not tables:
                print("Database schema not found. Initializing...")
                init_sql_path = Path(__file__).parent.parent / "init.sql"
                if init_sql_path.exists():
                    init_sql = init_sql_path.read_text()
                    await conn.execute(init_sql)
                    print("✓ Database schema initialized successfully")
                else:
                    print(f"Warning: init.sql not found at {init_sql_path}")
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        app.state.pool = None
        app.state.db_connected = False

@app.on_event("shutdown")
async def shutdown():
    if app.state.pool:
        await app.state.pool.close()


@app.get("/api/stats")
async def get_stats():
    """Get counts for tabs and overview"""
    if not app.state.pool:
        # Return filesystem-based stats if no database
        image_count = len(list(EXTRACTED_DIR.glob("**/*.png"))) if EXTRACTED_DIR.exists() else 0
        # Flight logs count includes both flight and contact book images
        flightlog_count = len([f for f in EXTRACTED_DIR.glob("**/*.png") if ("flight" in f.parent.name.lower() or "contact" in f.parent.name.lower())]) if EXTRACTED_DIR.exists() else 0
        # Regular images count excludes flight and contact book images
        regular_image_count = len([f for f in EXTRACTED_DIR.glob("**/*.png") if ("flight" not in f.parent.name.lower() and "contact" not in f.parent.name.lower())]) if EXTRACTED_DIR.exists() else 0
        return {
            "total_documents": image_count,
            "by_type": {"image": regular_image_count},
            "by_source": {"filesystem": image_count},
            "flightlogs": flightlog_count
        }
    async with app.state.pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM documents")
        
        # Get counts by type, excluding flight logs from image count
        by_type = await conn.fetch("""
            SELECT 
                type,
                COUNT(*) as count
            FROM documents 
            WHERE type IS NOT NULL
            AND NOT (
                type = 'image' 
                AND (LOWER(file_path) LIKE '%flight%' OR LOWER(file_path) LIKE '%contact%')
            )
            GROUP BY type
        """)
        
        by_source = await conn.fetch("""
            SELECT source, COUNT(*) as count 
            FROM documents 
            GROUP BY source
        """)
        
        # Calculate flight logs count from database (images with "flight" or "contact" in file_path)
        flightlog_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE type = 'image' 
            AND (LOWER(file_path) LIKE '%flight%' OR LOWER(file_path) LIKE '%contact%')
        """) or 0
        
        return {
            "total_documents": total,
            "by_type": {r['type']: r['count'] for r in by_type},
            "by_source": {r['source']: r['count'] for r in by_source},
            "flightlogs": flightlog_count
        }


@app.get("/api/documents")
async def get_documents(
    type: Optional[str] = None,
    source: Optional[str] = None,
    year: Optional[int] = None,
    flightlogs: Optional[bool] = Query(None, description="Filter for flight logs (images with 'flight' or 'contact' in file_path)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=1000)
):
    """Get documents with filtering - matches your existing tab structure"""
    if not app.state.pool:
        # If no database, return filesystem images for image type
        if type == 'image' or type is None:
            filter_param = "flightlogs" if flightlogs else None
            return await list_local_images(page=page, per_page=per_page, filter=filter_param)
        return {"results": [], "total": 0, "page": page, "per_page": per_page}
    async with app.state.pool.acquire() as conn:
        where_clauses = []
        params = []
        idx = 1
        
        # Map frontend tab IDs to database types
        type_map = {
            'videos': 'video',
            'audio': 'audio',
            'images': 'image',
            'emails': 'email',
            'documents': 'document',
            'photo': 'image'  # Also support 'photo' for images
        }
        
        if type and type != 'all':
            db_type = type_map.get(type, type)
            where_clauses.append(f"type = ${idx}")
            params.append(db_type)
            idx += 1
        
        if source:
            where_clauses.append(f"source ILIKE ${idx}")
            params.append(f"%{source}%")
            idx += 1
        
        if year:
            where_clauses.append(f"EXTRACT(YEAR FROM date_released) = ${idx}")
            params.append(year)
            idx += 1
        
        # Filter for flight logs: images with "flight" or "contact" in file_path
        if flightlogs:
            where_clauses.append(f"(LOWER(file_path) LIKE ${idx} OR LOWER(file_path) LIKE ${idx + 1})")
            params.append("%flight%")
            params.append("%contact%")
            idx += 2
        elif flightlogs is False:
            # Exclude flight logs (for regular images tab)
            where_clauses.append(f"(LOWER(file_path) NOT LIKE ${idx} AND LOWER(file_path) NOT LIKE ${idx + 1})")
            params.append("%flight%")
            params.append("%contact%")
            idx += 2
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        total = await conn.fetchval(f"SELECT COUNT(*) FROM documents WHERE {where_sql}", *params)
        
        # Get paginated results
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        
        rows = await conn.fetch(f"""
            SELECT 
                id, efta_id, title, source, type, subtype,
                description, context, ocr_text,
                file_path, thumbnail_path, url,
                duration, location, date_released,
                downloadable, redacted, metadata
            FROM documents 
            WHERE {where_sql}
            ORDER BY id DESC
            LIMIT ${idx} OFFSET ${idx + 1}
        """, *params)
        
        # Format results to match your existing SAMPLE_DATA structure
        results = []
        for row in rows:
            # Construct URL from R2 if url is NULL but file_path exists
            file_url = row['url']
            if not file_url and row['file_path']:
                try:
                    file_url = get_file_url(row['file_path']) or get_b2_url(row['file_path'])
                except:
                    pass
            
            # Construct thumbnail URL from R2 if thumbnail_path exists
            # If no thumbnail_path, use the main image URL as thumbnail
            thumbnail_url = row['thumbnail_path']
            if thumbnail_url:
                try:
                    thumbnail_url = get_file_url(thumbnail_url) or get_b2_url(thumbnail_url)
                except:
                    pass
            elif file_url and row['type'] == 'image':
                # Use main image as thumbnail if no thumbnail available
                thumbnail_url = file_url
            
            item = {
                "id": row['id'],
                "efta_id": row['efta_id'],
                "title": row['title'] or f"Document {row['id']}",
                "source": row['source'],
                "type": row['type'],
                "subtype": row['subtype'],
                "description": row['description'],
                "context": row['context'],
                "date": row['date_released'].isoformat() if row['date_released'] else None,
                "date_released": row['date_released'].isoformat() if row['date_released'] else None,
                "url": file_url,
                "file_path": row['file_path'],
                "thumbnail_path": thumbnail_url or row['thumbnail_path'],
                "thumbnail_url": thumbnail_url,  # Add thumbnail_url for frontend convenience
                "duration": row['duration'],
                "location": row['location'],
                "downloadable": row['downloadable'],
                "redacted": row['redacted'],
                "ocr_text": row['ocr_text'][:1000] if row['ocr_text'] else None,
                "metadata": row['metadata'] or {}
            }
            results.append(item)
        
        return {
            "results": results,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: int):
    """Get single document with full details and people"""
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT d.*,
                   COALESCE(
                       (SELECT array_agg(p.name) 
                        FROM document_people dp 
                        JOIN people p ON dp.person_id = p.id 
                        WHERE dp.document_id = d.id),
                       ARRAY[]::text[]
                   ) as people
            FROM documents d
            WHERE d.id = $1
        """, doc_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Construct URL from R2 if url is NULL but file_path exists
        file_url = row['url']
        if not file_url and row['file_path']:
            try:
                file_url = get_file_url(row['file_path']) or get_b2_url(row['file_path'])
            except:
                pass
        
        # Construct thumbnail URL from R2 if thumbnail_path exists
        # If no thumbnail_path, use the main image URL as thumbnail
        thumbnail_url = row['thumbnail_path']
        if thumbnail_url and not (thumbnail_url.startswith('http') or thumbnail_url.startswith('/')):
            try:
                thumbnail_url = get_file_url(thumbnail_url) or get_b2_url(thumbnail_url)
            except:
                pass
        elif file_url and row['type'] == 'image':
            # Use main image as thumbnail if no thumbnail available
            thumbnail_url = file_url
        
        return {
            "id": row['id'],
            "efta_id": row['efta_id'],
            "title": row['title'],
            "source": row['source'],
            "type": row['type'],
            "subtype": row['subtype'],
            "description": row['description'],
            "context": row['context'],
            "ocr_text": row['ocr_text'],
            "date": row['date_released'].isoformat() if row['date_released'] else None,
            "url": file_url,
            "file_path": row['file_path'],
            "thumbnail_path": thumbnail_url or row['thumbnail_path'],
            "thumbnail_url": thumbnail_url,  # Add thumbnail_url for frontend convenience
            "duration": row['duration'],
            "location": row['location'],
            "downloadable": row['downloadable'],
            "redacted": row['redacted'],
            "people": row['people'] or [],
            "metadata": row['metadata'] or {}
        }


@app.get("/api/search")
async def search_documents(
    q: str = Query(..., min_length=1),
    type: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100)
):
    """Full-text search across all documents"""
    async with app.state.pool.acquire() as conn:
        type_map = {
            'videos': 'video',
            'audio': 'audio', 
            'images': 'image',
            'emails': 'email',
            'documents': 'document',
            'photo': 'image'
        }
        
        filters = []
        params = [q]
        idx = 2
        
        if type and type != 'all':
            db_type = type_map.get(type, type)
            filters.append(f"type = ${idx}")
            params.append(db_type)
            idx += 1
        
        if source:
            filters.append(f"source ILIKE ${idx}")
            params.append(f"%{source}%")
            idx += 1
        
        filter_sql = (" AND " + " AND ".join(filters)) if filters else ""
        
        # Search query
        params.extend([per_page, (page - 1) * per_page])
        
        rows = await conn.fetch(f"""
            SELECT 
                id, efta_id, title, source, type, description, context,
                file_path, thumbnail_path, url, duration, location,
                date_released, downloadable, redacted,
                ts_rank(
                    to_tsvector('english', COALESCE(ocr_text,'') || ' ' || COALESCE(description,'') || ' ' || COALESCE(title,'')),
                    plainto_tsquery('english', $1)
                ) as rank
            FROM documents
            WHERE to_tsvector('english', COALESCE(ocr_text,'') || ' ' || COALESCE(description,'') || ' ' || COALESCE(title,''))
                  @@ plainto_tsquery('english', $1)
            {filter_sql}
            ORDER BY rank DESC
            LIMIT ${idx} OFFSET ${idx + 1}
        """, *params)
        
        # Get total count
        count_params = [q]
        count_filters = []
        count_idx = 2
        if type and type != 'all':
            db_type = type_map.get(type, type)
            count_filters.append(f"type = ${count_idx}")
            count_params.append(db_type)
            count_idx += 1
        if source:
            count_filters.append(f"source ILIKE ${count_idx}")
            count_params.append(f"%{source}%")
            count_idx += 1
        count_filter_sql = (" AND " + " AND ".join(count_filters)) if count_filters else ""
        
        total = await conn.fetchval(f"""
            SELECT COUNT(*) FROM documents
            WHERE to_tsvector('english', COALESCE(ocr_text,'') || ' ' || COALESCE(description,'') || ' ' || COALESCE(title,''))
                  @@ plainto_tsquery('english', $1)
            {count_filter_sql}
        """, *count_params)
        
        results = [{
            "id": r['id'],
            "efta_id": r['efta_id'],
            "title": r['title'],
            "source": r['source'],
            "type": r['type'],
            "description": r['description'],
            "context": r['context'],
            "file_path": r['file_path'],
            "thumbnail_path": r['thumbnail_path'],
            "url": r['url'],
            "duration": r['duration'],
            "location": r['location'],
            "date": r['date_released'].isoformat() if r['date_released'] else None,
            "date_released": r['date_released'].isoformat() if r['date_released'] else None,
            "downloadable": r['downloadable'],
            "redacted": r['redacted'],
            "metadata": r.get('metadata', {}),
            "rank": float(r['rank']) if 'rank' in r else None
        } for r in rows]
        
        return {
            "results": results,
            "total": total,
            "page": page,
            "per_page": per_page,
            "query": q
        }


@app.get("/api/people")
async def get_people(limit: int = 100, type: Optional[str] = None):
    """Get people mentioned/pictured with document counts, optionally filtered by document type"""
    async with app.state.pool.acquire() as conn:
        # First try people table
        type_filter = "AND d.type = $2" if type else ""
        params = [limit]
        if type:
            params.insert(0, type)
        
        query = f"""
            SELECT p.id, p.name, p.description,
                   COUNT(dp.document_id) as doc_count
            FROM people p
            JOIN document_people dp ON p.id = dp.person_id
            JOIN documents d ON dp.document_id = d.id
            WHERE 1=1 {type_filter}
            GROUP BY p.id
            ORDER BY doc_count DESC
            LIMIT ${len(params)}
        """
        
        rows = await conn.fetch(query, *params)
        
        # If no results from people table, extract from metadata
        if not rows:
            type_condition = "AND type = $1" if type else ""
            params_meta = [type] if type else []
            
            meta_query = f"""
                SELECT metadata
                FROM documents
                WHERE type = COALESCE($1, type) AND metadata IS NOT NULL
            """
            
            all_rows = await conn.fetch(meta_query, *params_meta)
            
            # Count people from metadata
            people_counts = {}
            for row in all_rows:
                meta = row['metadata']
                if isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except:
                        continue
                
                detected_people = meta.get('detected_people', [])
                for person in detected_people:
                    if person and isinstance(person, str):
                        people_counts[person] = people_counts.get(person, 0) + 1
            
            # Convert to list format
            result = [
                {"id": i, "name": name, "description": None, "doc_count": count}
                for i, (name, count) in enumerate(sorted(people_counts.items(), key=lambda x: x[1], reverse=True)[:limit])
            ]
            return result
        
        return [{"id": r['id'], "name": r['name'], "description": r['description'], "doc_count": r['doc_count']} for r in rows]


@app.get("/")
async def root():
    return {"message": "EpsteinBase API", "version": "1.0.0", "docs": "/docs"}


@app.get("/api/files/images")
async def list_local_images(page: int = 1, per_page: int = 1000, filter: Optional[str] = None):
    """List images from B2 if configured, otherwise from filesystem"""
    # Check if B2 is configured
    use_b2 = os.getenv("B2_APPLICATION_KEY_ID") and os.getenv("B2_BUCKET_NAME")
    
    if use_b2:
        # Use B2 - list all files recursively
        try:
            all_b2_files = list_b2_files(prefix="extracted/", max_keys=50000)
            
            # Filter for image files only
            image_files = [f for f in all_b2_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            # Filter logic for flightlogs vs regular images
            if filter == "flightlogs":
                image_files = [f for f in image_files if any(x in f.lower() for x in ["flight", "contact"])]
            else:
                image_files = [f for f in image_files if not any(x in f.lower() for x in ["flight", "contact"])]
            
            # Sort for consistent pagination
            image_files = sorted(image_files)
            
            # Paginate
            total = len(image_files)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_files = image_files[start_idx:end_idx]
            
            # Build response
            images = []
            for file_path in paginated_files:
                try:
                    # Extract parent folder name for source
                    source = Path(file_path).parent.name
                    
                    # Construct thumbnail path (assumes same structure under thumbnails/)
                    thumb_path = file_path.replace("extracted/", "thumbnails/", 1)
                    
                    images.append({
                        "id": abs(hash(file_path)) % (10**9),
                        "title": Path(file_path).stem.replace("_", " ").replace("page", "Page").title(),
                        "type": "image",
                        "file_path": file_path,
                        "thumbnail_path": thumb_path,
                        "source": source,
                        "url": get_file_url(file_path) or get_b2_url(file_path),
                        "thumbnail_url": get_file_url(thumb_path) or get_b2_url(thumb_path)
                    })
                except Exception as e:
                    continue
            
            return {
                "results": images,
                "total": total,
                "page": page,
                "per_page": per_page
            }
        except Exception as e:
            print(f"Error listing B2 files: {e}")
            # Fallback to empty if B2 fails
            return {"results": [], "total": 0, "page": page, "per_page": per_page}
    
    # Fallback to filesystem (for local dev)
    if not EXTRACTED_DIR.exists():
        return {"results": [], "total": 0, "page": page, "per_page": per_page}
    
    images = []
    image_files = sorted(list(EXTRACTED_DIR.glob("**/*.png")) + list(EXTRACTED_DIR.glob("**/*.jpg")) + list(EXTRACTED_DIR.glob("**/*.jpeg")))
    
    # Filter logic
    if filter == "flightlogs":
        image_files = [f for f in image_files if "flight" in f.parent.name.lower() or "contact" in f.parent.name.lower()]
    else:
        image_files = [f for f in image_files if "flight" not in f.parent.name.lower() and "contact" not in f.parent.name.lower()]
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_files = image_files[start_idx:end_idx]
    
    for img_path in paginated_files:
        try:
            rel_path = img_path.relative_to(DATA_DIR)
            thumb_path = THUMBNAIL_DIR / rel_path
            images.append({
                "id": abs(hash(str(rel_path))) % (10**9),
                "title": img_path.stem.replace("_", " ").replace("page", "Page").title(),
                "type": "image",
                "file_path": str(rel_path).replace("\\", "/"),
                "thumbnail_path": str(thumb_path.relative_to(DATA_DIR)).replace("\\", "/") if thumb_path.exists() else None,
                "source": img_path.parent.name
            })
        except Exception as e:
            continue
    
    return {
        "results": images,
        "total": len(image_files),
        "page": page,
        "per_page": per_page
    }


@app.get("/health")
async def health():
    try:
        async with app.state.pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/api/admin/ingest-r2")
async def ingest_r2_endpoint():
    """Admin endpoint to ingest files from R2 into database"""
    if not app.state.pool:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        async with app.state.pool.acquire() as conn:
            # Import here to avoid circular dependency
            from .ingest_r2 import ingest_from_r2_async
            result = await ingest_from_r2_async(conn)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
