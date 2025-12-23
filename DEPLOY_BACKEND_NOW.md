# Deploy Backend to Render - Quick Steps

## ✅ What's Ready:
- ✅ `render.yaml` configured
- ✅ `requirements-api.txt` (minimal dependencies)
- ✅ Backend code ready

## 🚀 Deploy Steps:

### 1. Push Code to GitHub
```bash
git add render.yaml backend/app/b2_client.py scripts/upload_to_r2.py
git commit -m "Add R2 support and fix Render config"
git push origin main
```

### 2. Deploy on Render

**Option A: Using Blueprint (Easiest)**
1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect GitHub repo: `white-roz3/epsteinbase`
4. Render will auto-detect `render.yaml` and configure everything
5. Click **"Apply"**

**Option B: Manual Setup**
1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo
4. Set:
   - **Name**: `epsteinbase-api`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements-api.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

### 3. Add Environment Variables in Render

After deployment, go to your service → **Environment** and add:

```
# R2 Configuration (if using R2)
STORAGE_TYPE=r2
R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase
R2_BUCKET_NAME=epsteinbase

# Database (auto-set by Render, but verify)
DATABASE_URL=postgresql://... (Render sets this automatically)
```

### 4. Add PostgreSQL Database

In Render dashboard:
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `epsteinbase-db`
3. Plan: Free (or Starter)
4. Copy the connection string to `DATABASE_URL`

Or use the database from `render.yaml` (if using Blueprint, it creates it automatically).

### 5. Initialize Database

After deployment, run the init script:
```bash
# Via Render Shell or SSH
psql $DATABASE_URL -f backend/init.sql
```

Or use Render's database connection and run:
```sql
-- Paste contents of backend/init.sql
```

## ✅ After Deployment:

Your backend will be at:
```
https://epsteinbase-api.onrender.com
```

Update your frontend `.env`:
```
VITE_API_URL=https://epsteinbase-api.onrender.com
```

## 🔄 What About Wrangler?

**Wrangler is only for:**
- ✅ Uploading files to R2 (we already did this)
- ❌ NOT for deploying FastAPI backends

**Backend deployment uses:**
- ✅ Render (recommended - already configured)
- ✅ Or Fly.io, Railway, etc.

Want me to push the code to GitHub now so you can deploy to Render?

