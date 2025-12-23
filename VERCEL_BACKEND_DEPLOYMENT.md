# Deploying Backend to Vercel Pro - Considerations

## TL;DR: Possible but Requires Changes

Yes, you **can** deploy your FastAPI backend to Vercel Pro, but it requires significant modifications because:

1. **File System Limitations**: The `data/` directory (~2.3GB) can't be deployed with serverless functions
2. **Static File Serving**: Need external storage (S3, Cloudflare R2, etc.)
3. **Database Connection Pooling**: Serverless functions need different connection handling

## Current Architecture Challenges

### 1. Static Files (Biggest Issue)
Your backend currently serves files from:
```python
DATA_DIR = Path(__file__).parent.parent.parent / "data"
app.mount("/files", StaticFiles(directory=str(DATA_DIR)), name="files")
```

**Problem**: Vercel serverless functions have read-only filesystem (except `/tmp`). You can't bundle 2.3GB of images.

**Solution**: 
- Upload images to Cloudflare R2, AWS S3, or Backblaze B2
- Update file paths in database to use external URLs
- Serve files from CDN/storage service

### 2. Database Connection Pooling
```python
app.state.pool = await asyncpg.create_pool(DATABASE_URL)
```

**Problem**: Serverless functions are stateless and may reuse connections, but connection pooling behaves differently.

**Solution**: 
- Use per-request connections, OR
- Use a connection pooler like PgBouncer
- Vercel Pro has longer execution times, so pooling can work with proper setup

### 3. File System Operations
Your code uses:
```python
EXTRACTED_DIR.glob("**/*.png")  # File system scans
```

**Problem**: Can't scan filesystem in serverless environment.

**Solution**: Store file metadata in database instead of scanning filesystem.

## Recommended Approach

### Option A: Keep Railway (Recommended)
Railway is better suited for this use case:
- ✅ Persistent file storage
- ✅ Better for long-running processes
- ✅ Easier static file serving
- ✅ Native PostgreSQL support
- ✅ More predictable pricing for your use case

### Option B: Hybrid Approach
- **Frontend**: Vercel (already deployed)
- **Backend API**: Railway (FastAPI)
- **Static Files**: Cloudflare R2 or AWS S3
- **Database**: Railway PostgreSQL or Supabase

This gives you the best of both worlds.

### Option C: Full Vercel Pro Deployment (More Work)

If you want everything on Vercel Pro, you'd need to:

1. **Move Images to External Storage**
   ```bash
   # Upload to Cloudflare R2 or S3
   # Update file_path in database to use CDN URLs
   ```

2. **Create Vercel Serverless Function**
   Create `api/index.py`:
   ```python
   from mangum import Mangum
   from backend.app.main import app
   
   handler = Mangum(app)
   ```

3. **Update File Serving**
   ```python
   # Instead of StaticFiles, redirect to CDN
   @app.get("/files/{file_path:path}")
   async def serve_file(file_path: str):
       # Look up CDN URL from database
       cdn_url = get_cdn_url(file_path)
       return RedirectResponse(cdn_url)
   ```

4. **Fix Database Connections**
   ```python
   # Use per-request connections or connection pooler
   async def get_db():
       return await asyncpg.connect(DATABASE_URL)
   ```

5. **Update Environment Variables**
   - `DATABASE_URL`: External PostgreSQL (Railway, Supabase, Neon, etc.)
   - `CDN_BASE_URL`: Your Cloudflare R2 or S3 URL

6. **Create `vercel.json` for Backend**
   ```json
   {
     "functions": {
       "api/**/*.py": {
         "runtime": "python3.11"
       }
     },
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "/api/:path*"
       }
     ]
   }
   ```

7. **Create `requirements.txt` in root**
   Include all backend dependencies + `mangum` (ASGI adapter)

## Comparison: Railway vs Vercel Pro

| Feature | Railway | Vercel Pro |
|---------|---------|------------|
| File Storage | ✅ Persistent volumes | ❌ Need external storage |
| Database | ✅ Included PostgreSQL | ❌ Need external DB |
| Static Files | ✅ Direct serving | ❌ Need CDN/storage |
| Cost | ~$5/month | ~$20/month + storage |
| Setup Complexity | Simple | Complex (need storage migration) |
| Best For | Full-stack with files | API-only or static sites |

## My Recommendation

**Stick with Railway for the backend** because:
1. Your use case needs file storage (2.3GB of images)
2. Railway handles this natively
3. Simpler architecture
4. Lower cost
5. Already configured

**Use Vercel for frontend** (already done):
- Perfect for React/Vite
- Great CDN
- Excellent performance

This hybrid approach is the industry standard and gives you the best performance and cost.

## If You Still Want Vercel Pro

I can help you:
1. Set up Cloudflare R2 for image storage
2. Create migration script to move images
3. Update backend code for serverless
4. Configure Vercel serverless functions

But it's significantly more work and ongoing cost (storage + bandwidth).


