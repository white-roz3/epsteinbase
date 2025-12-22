# Split Architecture Setup Guide

This guide explains how to set up the split architecture with frontend on Vercel, media files and database served from your local machine via Cloudflare Tunnel.

## Architecture Overview

- **Frontend**: React/Vite app on Vercel (epsteinbase.xyz)
- **Backend API**: FastAPI on Vercel/Render/etc (connects to database via Cloudflare Tunnel)
- **Media Server**: Local FastAPI server (serves files from `data/` directory via Cloudflare Tunnel)
- **Database**: Local PostgreSQL (accessed via Cloudflare Tunnel)

## Quick Start

### 1. Local Development Setup

All services run on localhost:

```bash
# Terminal 1: Media Server
cd media-server
pip install -r requirements.txt
python server.py
# Server runs on http://localhost:8001

# Terminal 2: Backend API (if needed locally)
cd backend
uvicorn app.main:app --reload
# API runs on http://localhost:8000

# Terminal 3: Frontend
npm run dev
# Frontend runs on http://localhost:5173
```

The frontend automatically uses:
- `VITE_API_URL=http://localhost:8000` (default)
- `VITE_MEDIA_URL=http://localhost:8001` (default)

### 2. Media Server Setup

The media server serves files from your `data/` directory at `/media/{filepath}`.

**Example URLs:**
- `http://localhost:8001/media/extracted/folder/image.png`
- `http://localhost:8001/media/audio/file.wav`
- `http://localhost:8001/media/thumbnails/folder/thumb.png`

**Environment Variables:**
```bash
export MEDIA_DIR=./data  # Path to your data directory
export PORT=8001         # Server port
```

### 3. Cloudflare Tunnel Setup for Media Server

1. **Install Cloudflare Tunnel:**
```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Or download from:
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

2. **Authenticate:**
```bash
cloudflared tunnel login
```

3. **Create a tunnel:**
```bash
cloudflared tunnel create epsteinbase-media
```

4. **Configure the tunnel** (edit `~/.cloudflared/config.yml`):
```yaml
tunnel: <tunnel-id-from-create-command>
credentials-file: /Users/yourusername/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: media.epsteinbase.xyz  # Your subdomain
    service: http://localhost:8001
  - service: http_status:404
```

5. **Create DNS record:**
```bash
cloudflared tunnel route dns epsteinbase-media media.epsteinbase.xyz
```

6. **Run the tunnel:**
```bash
cloudflared tunnel run epsteinbase-media
```

Or run as a service:
```bash
sudo cloudflared service install
sudo cloudflared service start
```

### 4. Cloudflare Tunnel Setup for Database

1. **Create a tunnel for database:**
```bash
cloudflared tunnel create epsteinbase-db
```

2. **Configure the tunnel** (add to `~/.cloudflared/config.yml`):
```yaml
tunnel: <db-tunnel-id>
credentials-file: /Users/yourusername/.cloudflared/<db-tunnel-id>.json

ingress:
  - hostname: db.epsteinbase.xyz  # Your subdomain
    service: postgresql://localhost:5433
  - service: http_status:404
```

3. **Create DNS record:**
```bash
cloudflared tunnel route dns epsteinbase-db db.epsteinbase.xyz
```

4. **Update DATABASE_URL:**
   - Format: `postgresql://user:password@db.epsteinbase.xyz:5432/epsteinbase`
   - Note: Cloudflare Tunnel will proxy the PostgreSQL connection

### 5. Vercel Environment Variables

Set these in your Vercel project settings:

**Frontend Environment Variables:**
- `VITE_API_URL`: Your backend API URL (e.g., `https://api.epsteinbase.xyz`)
- `VITE_MEDIA_URL`: Your media server URL via Cloudflare Tunnel (e.g., `https://media.epsteinbase.xyz`)

**Backend Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string via Cloudflare Tunnel (e.g., `postgresql://user:pass@db.epsteinbase.xyz:5432/epsteinbase`)

### 6. Testing

1. **Test media server locally:**
```bash
curl http://localhost:8001/media/extracted/some-folder/image.png
```

2. **Test media server via tunnel:**
```bash
curl https://media.epsteinbase.xyz/media/extracted/some-folder/image.png
```

3. **Test database connection:**
```bash
# From your backend server
psql $DATABASE_URL -c "SELECT 1;"
```

## File Structure

```
epsteinbase/
├── media-server/          # Media server (FastAPI)
│   ├── server.py
│   ├── requirements.txt
│   └── start.sh
├── backend/               # Backend API (FastAPI)
│   └── app/
├── src/                   # Frontend (React/Vite)
│   └── App.jsx
└── data/                  # Media files directory
    ├── extracted/
    ├── thumbnails/
    ├── audio/
    └── videos/
```

## How It Works

1. **Frontend** loads and requests data from **Backend API**
2. Backend API queries **Database** (via Cloudflare Tunnel)
3. Frontend constructs media URLs using `VITE_MEDIA_URL`
4. Frontend requests media files from **Media Server** (via Cloudflare Tunnel)
5. Media Server serves files from local `data/` directory

## Troubleshooting

**Media files not loading:**
- Check media server is running: `curl http://localhost:8001/health`
- Check Cloudflare Tunnel is running: `cloudflared tunnel list`
- Verify `VITE_MEDIA_URL` is set correctly in Vercel
- Check browser console for CORS errors

**Database connection failing:**
- Verify PostgreSQL is running locally
- Check Cloudflare Tunnel for database is running
- Test connection: `psql $DATABASE_URL -c "SELECT 1;"`
- Verify `DATABASE_URL` format is correct

**CORS errors:**
- Media server has CORS enabled for all origins
- If issues persist, update CORS settings in `media-server/server.py`

## Production Considerations

- **Media Server**: Consider running as a systemd service (Linux) or launchd (macOS)
- **Database**: Ensure PostgreSQL is properly secured and backed up
- **Cloudflare Tunnel**: Set up monitoring and alerts for tunnel uptime
- **Backup**: Regularly backup your `data/` directory and database

