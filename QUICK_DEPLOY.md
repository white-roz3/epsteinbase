# Quick Deployment Guide - Best Solution

## Current Status

✅ **Frontend**: Deployed to Vercel
- URL: https://epsteinbase-eod7y62wg-white-roz3s-projects.vercel.app
- Repository: https://github.com/white-roz3/epsteinbase

## Next Steps: Deploy Backend to Railway

### Option 1: Deploy via Railway Dashboard (Easiest)

1. **Go to Railway**: https://railway.app/new
2. **Select "Deploy from GitHub repo"**
3. **Connect GitHub** and select `white-roz3/epsteinbase`
4. **Railway will detect the Dockerfile** automatically
5. **Add PostgreSQL Database**:
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway auto-creates `DATABASE_URL` environment variable
6. **Initialize Database**:
   - Go to PostgreSQL service → "Connect" → "Query"
   - Copy contents of `backend/init.sql` and run it
7. **Get Backend URL**:
   - Railway will provide a URL like `https://epsteinbase-production.up.railway.app`
   - Copy this URL

### Option 2: Deploy via Railway CLI

```bash
# Login (opens browser)
railway login

# Initialize project
railway init

# Link to GitHub repo (or create new)
railway link

# Deploy
railway up

# Add PostgreSQL database
railway add postgresql

# Get the DATABASE_URL from Railway dashboard
# Initialize schema (run once)
railway run psql $DATABASE_URL -f backend/init.sql
```

## Configure Frontend to Use Backend

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Select your `epsteinbase` project**
3. **Go to Settings → Environment Variables**
4. **Add variable**:
   - Key: `VITE_API_URL`
   - Value: Your Railway backend URL (e.g., `https://epsteinbase-production.up.railway.app`)
   - Environment: Production (and Preview if you want)
5. **Redeploy**: Go to "Deployments" → Click "..." on latest → "Redeploy"

## Verify Everything Works

1. **Test Backend**: `https://your-railway-url.railway.app/api/stats`
2. **Test Frontend**: Your Vercel URL
3. **Check Search**: Should connect to backend API

## Important Notes

### Data Directory

The `data/` directory (~2.3GB) won't be deployed by default. Options:

**Option A: Railway Volumes** (for development/small scale)
- Add a volume in Railway
- Mount to `/app/data`
- Upload files manually

**Option B: External Storage** (recommended for production)
- Upload images to Cloudflare R2, AWS S3, or Backblaze B2
- Update backend code to serve from external URLs
- Much faster and cheaper at scale

**Option C: Keep Backend Local** (for now)
- Keep backend running locally for development
- Use ngrok to expose it: `ngrok http 8000`
- Set Vercel env var to ngrok URL

## Cost Estimate

- **Vercel**: Free (generous free tier)
- **Railway**: $5/month starter (or free trial credits)
- **Total**: ~$5/month for full deployment

## Need Help?

Check `DEPLOYMENT.md` for detailed troubleshooting and advanced configuration.


