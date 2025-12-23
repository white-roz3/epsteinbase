# Render Quick Start Guide

## Fast Setup (5 minutes)

### Step 1: Sign Up
1. Go to: https://render.com
2. Click "Get Started for Free"
3. Sign in with GitHub (recommended)

### Step 2: Create Web Service

1. Click "New +" → "Web Service"
2. Connect GitHub repo: `white-roz3/epsteinbase`
3. Fill in:

```
Name: epsteinbase-api
Environment: Python 3
Region: US East (or closest to you)
Branch: main
Root Directory: (leave blank)
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type: Free (or Starter $7/month for always-on)
```

4. Click "Advanced" → Add Environment Variables:

```
B2_APPLICATION_KEY_ID = 0055fbac3b92ba80000000001
B2_APPLICATION_KEY = K005ezwA+wavo4CXgTmFzqKVrpcvDgc
B2_BUCKET_NAME = Epsteinbase
B2_ENDPOINT_URL = https://f005.backblazeb2.com/file/Epsteinbase/
B2_S3_ENDPOINT = https://s3.us-east-005.backblazeb2.com
```

5. Click "Create Web Service"

### Step 3: Add PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Fill in:

```
Name: epsteinbase-db
Database: epsteinbase
Region: Same as web service
Plan: Free (90 days free)
```

3. Click "Create Database"
4. Go back to your web service → "Environment" tab
5. Under "Link Database", select `epsteinbase-db`
6. This auto-sets `DATABASE_URL`

### Step 4: Initialize Database

After first deployment:

1. Go to web service → "Shell" tab
2. Run:
```bash
cd backend
psql $DATABASE_URL -f init.sql
```

### Step 5: Deploy

1. Render auto-deploys on git push
2. Or click "Manual Deploy" → "Deploy latest commit"
3. Wait for build to complete
4. Your API URL: `https://epsteinbase-api.onrender.com`

---

## Important Notes

⚠️ **Free Tier**: Service spins down after 15min inactivity (first request takes ~30s)

⚠️ **Storage**: Render doesn't have persistent file storage. Backend needs B2 integration (I'll help update the code)

⚠️ **System Dependencies**: Some Python packages (PyMuPDF, Tesseract) might need buildpacks - we may need to adjust

---

## Next Steps

After deployment works, we need to:
1. Update backend to serve images from B2 (not filesystem)
2. Update CORS to include your Vercel domain
3. Update frontend API URL to point to Render

Let me know when you've created the service and I'll help with the code updates!


