# Fix Render Build Error

## Problem
Render build is failing with: `metadata-generation-failed`

**Cause**: PyMuPDF and pytesseract require system dependencies that Render can't install easily.

## Solution: Use Minimal Requirements

The **API server doesn't actually need** PyMuPDF/pytesseract - those are only used in extraction scripts!

### Steps to Fix Render:

1. **In Render Dashboard**, go to your web service
2. **Edit the Build Command** to use minimal requirements:
   ```
   cd backend && pip install -r requirements-api.txt
   ```
3. **Save and redeploy**

### What's Removed:
- ❌ PyMuPDF (needs libmupdf system library)
- ❌ pytesseract (needs tesseract-ocr system library)  
- ❌ Pillow (only needed for image processing scripts)
- ❌ datasets (only needed for HuggingFace ingestion scripts)

### What's Kept:
- ✅ FastAPI (API framework)
- ✅ uvicorn (ASGI server)
- ✅ asyncpg (PostgreSQL driver)
- ✅ boto3 (B2 S3 API)
- ✅ Everything needed for the API!

## Why This Works

Your API only needs to:
- Serve files from B2 (boto3)
- Query database (asyncpg)
- Handle HTTP requests (FastAPI/uvicorn)

It doesn't need to:
- Extract images from PDFs (already done)
- Process images (already done)
- Run OCR (already done)

All the heavy processing was done locally. The API just serves the results!

## Alternative: Fix Render Build with System Dependencies

If you want to keep full requirements, you'd need to:
1. Use Dockerfile deployment instead of buildpack
2. Install system dependencies in Dockerfile

But for API serving, minimal requirements is the better approach!


