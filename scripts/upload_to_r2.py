#!/usr/bin/env python3
"""
Upload files to Cloudflare R2 using Wrangler CLI
"""
import subprocess
import os
import sys
from pathlib import Path

BUCKET_NAME = "epsteinbase"
UPLOAD_DIR = Path(__file__).parent.parent / "public" / "curated"

def upload_file(local_path: Path, r2_path: str):
    """Upload a single file to R2 using wrangler"""
    try:
        # Determine content type based on extension
        ext = local_path.suffix.lower()
        content_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
        }
        content_type = content_types.get(ext, 'application/octet-stream')
        
        cmd = [
            'npx', 'wrangler', 'r2', 'object', 'put',
            f'{BUCKET_NAME}/{r2_path}',
            '--file', str(local_path),
            '--content-type', content_type,
            '--remote'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Uploaded: {local_path.name} → {r2_path}", flush=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upload {local_path.name}: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error uploading {local_path.name}: {e}")
        return False

def upload_directory(source_dir: Path, r2_prefix: str = ""):
    """Upload all files from a directory to R2"""
    if not source_dir.exists():
        print(f"❌ Directory not found: {source_dir}")
        return
    
    files = list(source_dir.rglob('*'))
    files = [f for f in files if f.is_file()]
    
    print(f"📤 Uploading {len(files)} files to R2 bucket '{BUCKET_NAME}'...", flush=True)
    print(f"   Source: {source_dir}", flush=True)
    print(f"   R2 prefix: {r2_prefix or '(root)'}", flush=True)
    print(flush=True)
    
    success = 0
    failed = 0
    
    for file_path in files:
        # Get relative path from source directory
        rel_path = file_path.relative_to(source_dir)
        r2_path = f"{r2_prefix}/{rel_path}".lstrip('/') if r2_prefix else str(rel_path)
        
        # Convert Windows-style paths to forward slashes
        r2_path = r2_path.replace('\\', '/')
        
        if upload_file(file_path, r2_path):
            success += 1
        else:
            failed += 1
    
    print(flush=True)
    print(f"📊 Upload complete!", flush=True)
    print(f"   ✅ Success: {success}", flush=True)
    print(f"   ❌ Failed: {failed}", flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        upload_dir = Path(sys.argv[1])
        prefix = sys.argv[2] if len(sys.argv) > 2 else ""
    else:
        upload_dir = UPLOAD_DIR
        prefix = ""
    
    upload_directory(upload_dir, prefix)

