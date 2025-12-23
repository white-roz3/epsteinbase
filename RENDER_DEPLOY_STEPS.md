# Deploy to Render - Simple Steps

## ✅ Code is Ready
- ✅ Code pushed to GitHub
- ✅ `render.yaml` configured
- ✅ `requirements-api.txt` ready
- ✅ Media files excluded (using R2)

## 🚀 Deploy Steps:

### 1. Go to Render Dashboard
Visit: https://dashboard.render.com
- Sign up/login with GitHub (if not already)

### 2. Create New Blueprint
1. Click **"New +"** button (top right)
2. Select **"Blueprint"**
3. Connect your GitHub account (if not connected)
4. Select repository: **`white-roz3/epsteinbase`**
5. Render will automatically detect `render.yaml`
6. Click **"Apply"**

### 3. Render Will Create:
- ✅ Web Service: `epsteinbase-api` (your FastAPI backend)
- ✅ PostgreSQL Database: `epsteinbase-db`

### 4. After Deployment Starts:

**Add Environment Variables** (go to your service → Environment):

```
STORAGE_TYPE=r2
R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
R2_BUCKET_NAME=epsteinbase
R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase
```

**Note:** Database URL (`DATABASE_URL`) is automatically set by Render - no need to add it manually.

### 5. Initialize Database
After the database is created:
1. Go to your PostgreSQL service in Render
2. Click **"Connect"** or use **"Shell"**
3. Run the schema:
   ```bash
   psql $DATABASE_URL -f backend/init.sql
   ```
   Or copy/paste the contents of `backend/init.sql` into the SQL editor

### 6. Your API Will Be Live At:
```
https://epsteinbase-api.onrender.com
```

### 7. Update Frontend (Vercel)
In Vercel dashboard, add environment variable:
```
VITE_API_URL=https://epsteinbase-api.onrender.com
```

## ✅ That's It!

Your backend will:
- Serve API endpoints
- Connect to PostgreSQL database  
- Serve files from Cloudflare R2 (when `STORAGE_TYPE=r2` is set)
- No media files needed (served from R2)

## 🔍 Monitor Deployment
Watch the build logs in Render dashboard to see:
- Dependencies installing
- Application starting
- Any errors (should be none!)

## ⚠️ First Request Warning
On free tier, first request after 15min inactivity takes ~30 seconds (cold start). This is normal!

