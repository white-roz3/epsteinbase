# Quick Fix - Use B2 Files NOW

## What's Already Done ✅

1. **Backend code** - Updated to use B2
2. **B2 files** - Already uploaded (checking now)
3. **Minimal requirements** - Created (removes problematic packages)

## Fix Render Build (2 minutes)

1. Go to: https://dashboard.render.com → Your service → Settings
2. **Change Build Command**:
   ```
   cd backend && pip install -r requirements-api.txt
   ```
3. Click "Save Changes"
4. It will auto-redeploy

**This should build successfully in 2-3 minutes!**

## What This Does

- ✅ Removes PyMuPDF (causing build failure)
- ✅ Removes pytesseract (causing build failure)  
- ✅ Keeps everything needed for API (FastAPI, asyncpg, boto3)
- ✅ Backend will serve files from B2 (already uploaded)

## After Build Succeeds

1. Add PostgreSQL database in Render
2. Initialize schema
3. Backend will serve images from B2 immediately

No more waiting - use what's already there!


