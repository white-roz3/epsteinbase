# Deploy to Render - Options

## Option 1: Deploy via CLI (Interactive Terminal Required)

**In your terminal, run:**

```bash
# 1. Login to Render
render login

# 2. List services (if already deployed)
render services

# 3. Deploy using Blueprint (from render.yaml)
render blueprints create --file render.yaml

# OR if service already exists, trigger new deployment:
render deploys create [SERVICE_ID]
```

## Option 2: Deploy via GitHub (Easiest - Recommended) ⭐

**Steps:**

1. **Push code to GitHub:**
   ```bash
   cd /Users/white_roze/epsteinbase
   git add .
   git commit -m "Add R2 support and backend updates"
   git push origin main
   ```

2. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com
   - Sign up/login with GitHub

3. **Deploy from Blueprint:**
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repo: `white-roz3/epsteinbase`
   - Render will auto-detect `render.yaml` and configure everything
   - Click **"Apply"**

4. **Set Environment Variables** (in Render dashboard after deployment):
   ```
   STORAGE_TYPE=r2
   R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
   R2_BUCKET_NAME=epsteinbase
   R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase
   ```

## Option 3: Deploy via Render Dashboard (Manual)

1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo: `white-roz3/epsteinbase`
4. Configure:
   - **Name**: `epsteinbase-api`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements-api.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add PostgreSQL database
6. Set environment variables (see above)

## Recommendation: Option 2 (GitHub Blueprint)

Easiest and most reliable - just push to GitHub and let Render's Blueprint handle the rest!

