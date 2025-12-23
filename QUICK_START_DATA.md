# Quick Start: Get Data Showing on Frontend

## Problem
Frontend is live but showing no data because:
1. Database is empty (no documents)
2. R2 credentials not configured on Render

## Solution Steps

### Step 1: Add R2 Credentials to Render (REQUIRED)

Go to: https://dashboard.render.com → `epsteinbase-api` → Environment → Add these variables:

```
STORAGE_TYPE=r2
R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
R2_ACCESS_KEY_ID=<your_access_key>
R2_SECRET_ACCESS_KEY=<your_secret_key>
R2_BUCKET_NAME=epsteinbase
R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase
```

**Get R2 credentials from**: Cloudflare Dashboard → R2 → Manage R2 API Tokens

Then **restart the service**.

### Step 2: Ingest Data from R2

Once R2 is configured, you can ingest files:

**Option A: Run locally (connects to Render DB)**
```bash
export DATABASE_URL="postgresql://epsteinbase:password@dpg-xxxxx-a/epsteinbase"
python backend/scripts/ingest_from_r2.py
```

**Option B: Create ingestion endpoint** (we can add this)

The script `backend/scripts/ingest_from_r2.py` will:
- Connect to R2 and list all files
- Insert records into database
- Link file paths to R2 URLs

### Step 3: Verify

After ingestion:
- Frontend should show documents
- Images/videos/audio should load from R2
- API `/api/stats` should show counts > 0

Let me know when R2 credentials are added and we can run the ingestion!

