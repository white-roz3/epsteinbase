# Media Server

Simple FastAPI server to serve media files from your local `data/` directory via Cloudflare Tunnel.

## Setup

1. Install dependencies:
```bash
cd media-server
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export MEDIA_DIR=/path/to/your/data/directory  # Default: ../data
export PORT=8001  # Default: 8001
```

3. Run the server:
```bash
python server.py
```

Or with uvicorn:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```

## Cloudflare Tunnel Setup

1. Install Cloudflare Tunnel:
```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Or download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

2. Authenticate:
```bash
cloudflared tunnel login
```

3. Create a tunnel:
```bash
cloudflared tunnel create epsteinbase-media
```

4. Configure the tunnel (edit `~/.cloudflared/config.yml`):
```yaml
tunnel: <tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: media.epsteinbase.xyz
    service: http://localhost:8001
  - service: http_status:404
```

5. Run the tunnel:
```bash
cloudflared tunnel run epsteinbase-media
```

Or run as a service:
```bash
cloudflared service install
cloudflared service start
```

## Usage

The server exposes files at `/media/{filepath}` where `filepath` is relative to your `data/` directory.

Examples:
- `GET /media/extracted/folder/image.png` → serves `data/extracted/folder/image.png`
- `GET /media/audio/file.wav` → serves `data/audio/file.wav`
- `GET /media/thumbnails/folder/thumb.png` → serves `data/thumbnails/folder/thumb.png`

## Security

- Path traversal (`..`) is blocked
- Only files within `MEDIA_DIR` can be accessed
- CORS is enabled for all origins (adjust in production if needed)

