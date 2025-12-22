#!/usr/bin/env python3
"""
Simple media server to serve files from local data directory via Cloudflare Tunnel
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import os
from typing import Optional

app = FastAPI(title="EpsteinBase Media Server")

# CORS - allow all origins since this will be accessed via Cloudflare Tunnel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Media directory - point to your data folder
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", Path(__file__).parent.parent / "data"))

@app.get("/health")
async def health():
    return {"status": "healthy", "media_dir": str(MEDIA_DIR)}

@app.get("/media/{filepath:path}")
async def serve_media(filepath: str):
    """
    Serve media files from the data directory
    Supports nested paths like: /media/extracted/folder/image.png
    """
    # Security: prevent path traversal
    safe_path = Path(filepath)
    if ".." in filepath or safe_path.is_absolute():
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    file_path = MEDIA_DIR / safe_path
    
    # Check if file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if it's actually a file (not directory)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Path is not a file")
    
    # Check if file is within media directory (additional security)
    try:
        file_path.resolve().relative_to(MEDIA_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=str(file_path),
        media_type=None,  # Let browser detect content type
        filename=file_path.name
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)

