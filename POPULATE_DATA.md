# How to Populate Data on Render

## Current Situation
- ✅ Backend deployed on Render
- ✅ Database created and initialized (schema exists)
- ❌ Database is empty (no documents)
- ❌ R2 credentials not configured on Render

## Two Options:

### Option 1: Quick Test with Sample Data (Easiest)
Add some sample data directly via SQL or a script to test the frontend.

### Option 2: Full Setup with R2 (Production)
1. Configure R2 credentials on Render
2. Upload files to R2 (if not already done)
3. Ingest data from R2 into database

## Step 1: Configure R2 on Render

Go to Render Dashboard → `epsteinbase-api` service → Environment → Add:

```
STORAGE_TYPE=r2
R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=epsteinbase
R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase
```

Then restart the service.

## Step 2: Ingest Data

You have two options:

### A) Use Sample Data Script
If you have `backend/scripts/ingest_sample_data.py`, you can run it locally and it will insert sample records.

### B) Ingest from R2
Once R2 is configured, the backend can list files from R2 and you can create records for them.

Let me know which approach you want, or if you have R2 credentials ready!

