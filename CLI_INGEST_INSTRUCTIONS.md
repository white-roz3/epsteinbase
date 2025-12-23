# CLI Instructions: Populate Database from R2

## Step 1: Add R2 Credentials to Render (One-time setup)

Unfortunately, Render CLI doesn't support setting environment variables. You need to do this once in the dashboard:

1. Go to: https://dashboard.render.com
2. Click `epsteinbase-api` service
3. Go to "Environment" tab
4. Add these variables:
   - `STORAGE_TYPE` = `r2`
   - `R2_ACCOUNT_ID` = `ad3c74e324b945bcde28453399bdecbb`
   - `R2_ACCESS_KEY_ID` = (your R2 access key)
   - `R2_SECRET_ACCESS_KEY` = (your R2 secret key)
   - `R2_BUCKET_NAME` = `epsteinbase`
   - `R2_PUBLIC_URL` = `https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase`
5. Click "Save Changes"
6. Service will auto-restart

## Step 2: Trigger Ingestion via CLI (After R2 is configured)

Once R2 credentials are added and service restarted, trigger ingestion:

```bash
curl -X POST https://epsteinbase-api.onrender.com/api/admin/ingest-r2
```

This will:
- Connect to R2
- List all files
- Insert them into database
- Return count of inserted documents

## Step 3: Verify

Check stats:
```bash
curl https://epsteinbase-api.onrender.com/api/stats
```

Should show counts > 0 if ingestion worked.

## Alternative: If you have DATABASE_URL locally

You can also run the script locally:

```bash
export DATABASE_URL="postgresql://epsteinbase:password@dpg-xxxxx-a/epsteinbase"
export STORAGE_TYPE=r2
export R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
export R2_ACCESS_KEY_ID=your_key
export R2_SECRET_ACCESS_KEY=your_secret
export R2_BUCKET_NAME=epsteinbase
export R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase

python backend/scripts/ingest_from_r2.py
```

