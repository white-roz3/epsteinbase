# Render Deployment Guide

## Step-by-Step Setup

### Step 1: Sign Up for Render

1. Go to: https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended - easier integration)

### Step 2: Create Web Service

1. In Render dashboard, click "New +" → "Web Service"
2. Connect your GitHub account if not already connected
3. Select repository: `white-roz3/epsteinbase`
4. Configure the service:

**Settings:**
- **Name**: `epsteinbase-api`
- **Environment**: `Python 3`
- **Region**: Choose closest to you (US East/West, Europe, etc.)
- **Branch**: `main`
- **Root Directory**: Leave blank (or `backend` if needed)
- **Build Command**: 
  ```bash
  cd backend && pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- **Plan**: Free (or Starter $7/month for always-on)

### Step 3: Add PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `epsteinbase-db`
   - **Database**: `epsteinbase`
   - **User**: `epsteinbase` (or auto-generated)
   - **Region**: Same as web service
   - **Plan**: Free (90 days, then $7/month)

3. **Important**: After creating database, go to your web service → "Environment" → "Link Database"
   - This automatically sets `DATABASE_URL` environment variable

### Step 4: Set Environment Variables

Go to your web service → "Environment" tab, add:

1. **B2_APPLICATION_KEY_ID**: `0055fbac3b92ba80000000001`
2. **B2_APPLICATION_KEY**: `K005ezwA+wavo4CXgTmFzqKVrpcvDgc`
3. **B2_BUCKET_NAME**: `Epsteinbase`
4. **B2_ENDPOINT_URL**: `https://f005.backblazeb2.com/file/Epsteinbase/`
5. **B2_S3_ENDPOINT**: `https://s3.us-east-005.backblazeb2.com`

**DATABASE_URL** will be auto-set when you link the PostgreSQL database.

### Step 5: Initialize Database Schema

After deployment, you need to initialize the database:

**Option A: Using Render Shell**
1. Go to your web service
2. Click "Shell" tab
3. Run:
   ```bash
   cd backend
   psql $DATABASE_URL -f init.sql
   ```

**Option B: Using local psql**
1. Get database connection string from Render dashboard
2. Run locally:
   ```bash
   psql "postgresql://..." -f backend/init.sql
   ```

### Step 6: Deploy

1. Click "Save Changes"
2. Render will automatically:
   - Clone your repo
   - Install dependencies
   - Build and deploy
   - Start your service

3. Your API will be available at:
   - `https://epsteinbase-api.onrender.com` (or your custom domain)

---

## Important Notes

### Free Tier Limitations

- **Spins down after 15min inactivity**: First request takes ~30s to wake up
- **PostgreSQL**: Free for 90 days, then $7/month
- **Bandwidth**: Limited but generous for small apps

### Upgrade Options

- **Starter Plan ($7/month)**: Always-on, no spin-down
- **PostgreSQL ($7/month)**: After free 90 days

### B2 Integration

Your backend will serve images from Backblaze B2 instead of local filesystem:
- Images are already uploaded to B2
- Backend code needs to be updated to use B2 URLs
- This solves the storage limitation issue

---

## Next Steps After Deployment

1. ✅ Backend deployed on Render
2. ⏳ Update backend code to use B2 (I'll help with this)
3. ⏳ Update frontend API URL to point to Render
4. ⏳ Test everything works

---

## Troubleshooting

**Service won't start:**
- Check build logs for errors
- Verify requirements.txt has all dependencies
- Check start command is correct

**Database connection fails:**
- Make sure database is linked to web service
- Check DATABASE_URL is set correctly
- Verify database is running

**Images not loading:**
- Backend needs B2 integration code (we'll add this)
- Verify B2 environment variables are set

---

## Cost Summary

- **Render Web Service**: $0/month (free tier) or $7/month (always-on)
- **PostgreSQL**: $0/month (90 days) then $7/month
- **Backblaze B2 Storage**: $0.18/month
- **Total**: $0.18/month (free tier) or $14.18/month (always-on)


