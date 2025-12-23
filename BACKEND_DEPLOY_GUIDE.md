# Backend Deployment Guide

## 🎯 Recommended: Render (Easiest)

### Why Render?
- ✅ Already configured (`render.yaml` exists)
- ✅ Free tier for 90 days, then $7/month
- ✅ PostgreSQL included
- ✅ Simple deployment via GitHub
- ✅ Minimal dependencies (using `requirements-api.txt`)

### Steps:

1. **Push to GitHub** (if not already):
   ```bash
   git add render.yaml
   git commit -m "Fix Render deployment to use minimal requirements"
   git push origin main
   ```

2. **Go to Render Dashboard**:
   - Visit: https://dashboard.render.com
   - Sign up/login with GitHub

3. **Deploy from GitHub**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo (`white-roz3/epsteinbase`)
   - Render will automatically detect `render.yaml` and configure everything

4. **Set Environment Variables** (in Render dashboard):
   - `B2_APPLICATION_KEY_ID` (if using Backblaze for media)
   - `B2_APPLICATION_KEY` (if using Backblaze for media)
   - `B2_BUCKET_NAME` = `Epsteinbase` (if using Backblaze)
   - `B2_ENDPOINT_URL` (if using Backblaze)

5. **Get your API URL**:
   - Render will give you: `https://epsteinbase-api.onrender.com`
   - Update your frontend `.env`: `VITE_API_URL=https://epsteinbase-api.onrender.com`

---

## 🐳 Alternative: Fly.io (Docker-based)

### Why Fly.io?
- ✅ Great for Docker deployments
- ✅ Free tier available
- ✅ Simple CLI-based deployment
- ✅ Easy PostgreSQL addon

### Steps:

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Create app**:
   ```bash
   cd backend
   fly launch --name epsteinbase-api
   ```

4. **Add PostgreSQL**:
   ```bash
   fly postgres create --name epsteinbase-db
   fly postgres attach epsteinbase-db
   ```

5. **Set environment variables**:
   ```bash
   fly secrets set B2_APPLICATION_KEY_ID=your_key
   fly secrets set B2_APPLICATION_KEY=your_secret
   fly secrets set B2_BUCKET_NAME=Epsteinbase
   ```

6. **Deploy**:
   ```bash
   fly deploy
   ```

---

## 📊 Comparison

| Platform | Cost | Setup | Pros | Cons |
|----------|------|-------|------|------|
| **Render** | Free (90 days), then $7/mo | ⭐⭐⭐⭐⭐ Easiest | Auto-config, PostgreSQL included, GitHub integration | Sleeps after 15min inactivity (free tier) |
| **Fly.io** | Free tier available | ⭐⭐⭐⭐ Easy | Docker-native, fast cold starts, global regions | Need to create config files |
| Railway | $5-20/mo | ⭐⭐⭐ Medium | Good DX, persistent volumes | Paid only, payment issues you experienced |
| Vercel | Free/Pro | ⭐⭐ Harder | You already use it for frontend | Python serverless limitations |

---

## 🚀 Quick Start (Render - Recommended)

**Just do this:**

1. Push `render.yaml` to GitHub
2. Go to https://dashboard.render.com
3. Click "New +" → "Blueprint"
4. Connect repo → Deploy
5. Done! 🎉

Your API will be live at: `https://epsteinbase-api.onrender.com`

**Note:** On free tier, first request after 15min of inactivity will take ~30 seconds (cold start). This is fine for most use cases.

---

## 🔧 If you need to update the deployment:

The `render.yaml` uses minimal dependencies (`requirements-api.txt`) which includes only:
- FastAPI
- Uvicorn
- PostgreSQL driver (asyncpg)
- B2 client (boto3)

This avoids the heavy dependencies (PyMuPDF, Tesseract) that caused build issues before.

