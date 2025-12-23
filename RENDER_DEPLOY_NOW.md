# Render Deployment - Quick Guide

## ✅ Code is Ready!

Your backend code has been updated with:
- ✅ B2 integration for serving images from Backblaze
- ✅ CORS updated to include epsteinbase.xyz
- ✅ boto3 added to requirements.txt

## Deploy to Render Now

### Step 1: Create Web Service

1. Go to: https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repo: `white-roz3/epsteinbase`
4. Configure:

**Basic Settings:**
- Name: `epsteinbase-api`
- Region: `Oregon (US West)` or closest to you
- Branch: `main`
- Root Directory: (leave blank)
- Runtime: `Python 3`
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Plan:** Free (or Starter $7/month for always-on)

### Step 2: Add Environment Variables

In the "Environment" tab, add:

```
B2_APPLICATION_KEY_ID=0055fbac3b92ba80000000001
B2_APPLICATION_KEY=K005ezwA+wavo4CXgTmFzqKVrpcvDgc
B2_BUCKET_NAME=Epsteinbase
B2_ENDPOINT_URL=https://f005.backblazeb2.com/file/Epsteinbase/
B2_S3_ENDPOINT=https://s3.us-east-005.backblazeb2.com
```

**DATABASE_URL** will be auto-set when you link the database.

### Step 3: Add PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: `epsteinbase-db`
3. Database: `epsteinbase`
4. Plan: Free (90 days free)
5. Create Database
6. Go back to web service → "Environment" → "Link Database" → Select `epsteinbase-db`

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your API URL: `https://epsteinbase-api.onrender.com`

### Step 5: Initialize Database

After first successful deployment:

1. Go to web service → "Shell" tab
2. Run:
```bash
cd backend
psql $DATABASE_URL -f init.sql
```

### Step 6: Update Frontend API URL

In Vercel dashboard:
1. Go to your project → Settings → Environment Variables
2. Add/Update:
   - `VITE_API_URL` = `https://epsteinbase-api.onrender.com`
3. Redeploy frontend

## Testing

After deployment, test:
- `https://epsteinbase-api.onrender.com/api/stats`
- `https://epsteinbase-api.onrender.com/api/files/images`
- `https://epsteinbase-api.onrender.com/health`

## Content Serving

- ✅ Images: Served from B2 (uploading now)
- ✅ Audio: Will serve from B2 or DOJ URLs
- ✅ Videos: Already using DOJ URLs in frontend
- ✅ Emails: From database

All content will be accessible once backend is deployed and database is initialized!


