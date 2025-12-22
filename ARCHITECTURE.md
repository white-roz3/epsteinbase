# Architecture: Split Frontend/Media/Database

This project uses a split architecture:

## Components

1. **Frontend (Vercel)**
   - React/Vite app
   - Served at `epsteinbase.xyz`
   - Fetches API data from backend
   - Loads media from media server via `VITE_MEDIA_URL`

2. **Backend API (Vercel/Render/etc)**
   - FastAPI application
   - Connects to PostgreSQL via `DATABASE_URL`
   - Provides API endpoints for documents, search, stats

3. **Media Server (Local + Cloudflare Tunnel)**
   - Simple FastAPI server serving files from `data/` directory
   - Accessible via Cloudflare Tunnel at `media.epsteinbase.xyz` (or your domain)
   - Serves images, videos, audio files

4. **Database (Local + Cloudflare Tunnel)**
   - PostgreSQL database
   - Accessible via Cloudflare Tunnel
   - Connected by backend via `DATABASE_URL`

## Environment Variables

### Frontend (Vercel)
- `VITE_API_URL`: Backend API URL (e.g., `https://api.epsteinbase.xyz`)
- `VITE_MEDIA_URL`: Media server URL (e.g., `https://media.epsteinbase.xyz`)

### Backend
- `DATABASE_URL`: PostgreSQL connection string (via Cloudflare Tunnel)

### Media Server
- `MEDIA_DIR`: Path to data directory (default: `./data`)
- `PORT`: Server port (default: `8001`)

## Local Development

All services run on localhost:

```bash
# Terminal 1: Media Server
cd media-server
python server.py

# Terminal 2: Backend API
cd backend
uvicorn app.main:app --reload

# Terminal 3: Frontend
npm run dev

# Terminal 4: Database (if using Docker)
docker-compose up postgres
```

Frontend will use:
- `VITE_API_URL=http://localhost:8000`
- `VITE_MEDIA_URL=http://localhost:8001`

## Production Deployment

### Frontend (Vercel)
1. Set environment variables in Vercel dashboard
2. Deploy from GitHub

### Media Server (Local + Cloudflare Tunnel)
1. Run media server locally
2. Set up Cloudflare Tunnel to expose it
3. Update `VITE_MEDIA_URL` in Vercel to point to tunnel URL

### Database (Local + Cloudflare Tunnel)
1. Run PostgreSQL locally or on server
2. Set up Cloudflare Tunnel to expose it
3. Update `DATABASE_URL` in backend to use tunnel URL

## Cloudflare Tunnel Setup

See `media-server/README.md` for detailed Cloudflare Tunnel setup instructions.

