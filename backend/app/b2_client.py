"""
Cloud storage client (supports Backblaze B2 and Cloudflare R2)
"""
import os
import boto3
from botocore.config import Config
from typing import Optional

# Storage provider type (b2 or r2)
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "b2").lower()

# Backblaze B2 Configuration
B2_APPLICATION_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME", "Epsteinbase")
B2_ENDPOINT_URL = os.getenv("B2_ENDPOINT_URL", "https://f005.backblazeb2.com/file/Epsteinbase/")
B2_S3_ENDPOINT = os.getenv("B2_S3_ENDPOINT", "https://s3.us-east-005.backblazeb2.com")

# Cloudflare R2 Configuration
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "epsteinbase")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")  # Your R2 custom domain or public URL

# Use R2 if configured, otherwise fall back to B2
if STORAGE_TYPE == "r2" and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY:
    # R2 Configuration
    ACCESS_KEY_ID = R2_ACCESS_KEY_ID
    SECRET_ACCESS_KEY = R2_SECRET_ACCESS_KEY
    BUCKET_NAME = R2_BUCKET_NAME
    S3_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    # R2 public URL format: https://pub-{ACCOUNT_ID}.r2.dev (bucket name not in path)
    PUBLIC_URL = R2_PUBLIC_URL or f"https://pub-{R2_ACCOUNT_ID}.r2.dev"
elif B2_APPLICATION_KEY_ID and B2_APPLICATION_KEY:
    # B2 Configuration
    ACCESS_KEY_ID = B2_APPLICATION_KEY_ID
    SECRET_ACCESS_KEY = B2_APPLICATION_KEY
    BUCKET_NAME = B2_BUCKET_NAME
    S3_ENDPOINT = B2_S3_ENDPOINT
    PUBLIC_URL = B2_ENDPOINT_URL
else:
    # No storage configured
    ACCESS_KEY_ID = None
    SECRET_ACCESS_KEY = None
    BUCKET_NAME = None
    S3_ENDPOINT = None
    PUBLIC_URL = None

# Initialize S3-compatible client
_storage_client = None

def get_storage_client():
    """Get or create S3-compatible storage client (B2 or R2)"""
    global _storage_client
    if _storage_client is None and ACCESS_KEY_ID and SECRET_ACCESS_KEY and S3_ENDPOINT:
        _storage_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
    return _storage_client

def get_file_url(file_path: str) -> str:
    """
    Generate public URL for a file path
    file_path should be relative (e.g., "extracted/folder/image.png")
    Works with both B2 and R2
    """
    if not file_path or not PUBLIC_URL:
        return None
    
    # Remove leading slash if present
    file_path = file_path.lstrip('/')
    
    # Construct public URL
    return f"{PUBLIC_URL.rstrip('/')}/{file_path}"

def list_files(prefix: str = "", max_keys: int = 1000) -> list:
    """
    List files from storage bucket with given prefix
    Returns list of file paths (relative to bucket root)
    Works with both B2 and R2
    """
    client = get_storage_client()
    if not client or not BUCKET_NAME:
        return []
    
    try:
        response = client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        files = []
        for obj in response.get('Contents', []):
            files.append(obj['Key'])
        
        return files
    except Exception as e:
        print(f"Error listing storage files: {e}")
        return []

# Backward compatibility aliases
get_b2_client = get_storage_client
get_b2_url = get_file_url
list_b2_files = list_files


