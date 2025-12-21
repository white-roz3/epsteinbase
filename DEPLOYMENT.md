# Deployment Guide - Best Solution

This guide walks through deploying EpsteinBase using the recommended setup:
- **Frontend**: Vercel (already deployed)
- **Backend**: Railway (Python/FastAPI)
- **Database**: Railway PostgreSQL

## Prerequisites

1. Railway account: https://railway.app
2. Vercel account: https://vercel.com (already set up)

## Step 1: Deploy Backend to Railway

### Option A: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project (if not already linked)
railway init

# Deploy
railway up
```

### Option B: Using Railway Dashboard

1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select the `epsteinbase` repository
5. Railway will detect the Dockerfile and deploy

## Step 2: Add PostgreSQL Database

1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically create a `DATABASE_URL` environment variable
3. The backend will automatically use this URL

## Step 3: Initialize Database Schema

After deployment, run the database initialization:

```bash
# Get database connection string from Railway dashboard
# Then run:
psql $DATABASE_URL -f backend/init.sql
```

Or use Railway's database console:
1. Go to your PostgreSQL service in Railway
2. Click "Connect" → "Query"
3. Copy and paste the contents of `backend/init.sql`

## Step 4: Handle Data Directory (Images/Media)

The `data/` directory is too large (~2.3GB) for direct deployment. Options:

### Option A: Use Railway Volumes (Recommended)

1. In Railway, add a volume to your service
2. Mount it to `/app/data`
3. Upload your data files (this can take time)

### Option B: Use External Storage (Better for Production)

1. Upload images to Cloudflare R2, AWS S3, or similar
2. Update the backend to serve from external URLs
3. Update frontend to use CDN URLs

### Option C: Serve from External URLs (Current)

The frontend already uses DOJ URLs for videos/audio. For images, you may need to:
- Keep backend running locally with data directory
- Or deploy images to a CDN/storage service

## Step 5: Configure Environment Variables

### Backend (Railway):

- `DATABASE_URL`: Auto-set by Railway PostgreSQL service
- `PORT`: Auto-set by Railway
- `PYTHONUNBUFFERED`: Set to `1` (optional, for better logging)

### Frontend (Vercel):

1. Go to Vercel project settings
2. Add environment variable:
   - Name: `VITE_API_URL`
   - Value: Your Railway backend URL (e.g., `https://epsteinbase-production.up.railway.app`)

3. Redeploy frontend:
   ```bash
   vercel --prod
   ```

## Step 6: Verify Deployment

1. Check backend health: `https://your-railway-url.railway.app/api/stats`
2. Check frontend: Your Vercel URL
3. Test search functionality

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly in Railway
- Check database is running in Railway dashboard
- Verify schema is initialized

### CORS Issues

- Update `allow_origins` in `backend/app/main.py` to include your Vercel URL

### Images Not Loading

- Verify data directory is accessible or external URLs are configured
- Check `/files` endpoint is working: `https://your-backend/api/files/images/...`

## Cost Considerations

- **Vercel**: Free tier for frontend (generous limits)
- **Railway**: $5/month starter plan (or free trial credits)
- **Database**: Included with Railway plan
- **Storage**: Consider external storage for large files

## Recommended Production Setup

For production at scale:
1. Frontend: Vercel (CDN edge network)
2. Backend: Railway or Fly.io
3. Database: Railway PostgreSQL or Supabase
4. Images: Cloudflare R2 or AWS S3 with CDN
5. Monitoring: Railway logs + Vercel analytics

