"""
Backblaze B2 client for serving files
"""
import os
import boto3
from botocore.config import Config
from typing import Optional

# B2 Configuration
B2_APPLICATION_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME", "Epsteinbase")
B2_ENDPOINT_URL = os.getenv("B2_ENDPOINT_URL", "https://f005.backblazeb2.com/file/Epsteinbase/")
B2_S3_ENDPOINT = os.getenv("B2_S3_ENDPOINT", "https://s3.us-east-005.backblazeb2.com")

# Initialize B2 S3 client
_b2_client = None

def get_b2_client():
    """Get or create B2 S3 client"""
    global _b2_client
    if _b2_client is None and B2_APPLICATION_KEY_ID and B2_APPLICATION_KEY:
        _b2_client = boto3.client(
            's3',
            endpoint_url=B2_S3_ENDPOINT,
            aws_access_key_id=B2_APPLICATION_KEY_ID,
            aws_secret_access_key=B2_APPLICATION_KEY,
            config=Config(signature_version='s3v4')
        )
    return _b2_client

def get_b2_url(file_path: str) -> str:
    """
    Generate B2 URL for a file path
    file_path should be relative (e.g., "extracted/folder/image.png")
    """
    if not file_path:
        return None
    
    # Remove leading slash if present
    file_path = file_path.lstrip('/')
    
    # Construct B2 download URL
    # Format: https://f005.backblazeb2.com/file/bucket-name/path
    return f"{B2_ENDPOINT_URL.rstrip('/')}/{file_path}"

def list_b2_files(prefix: str = "", max_keys: int = 1000) -> list:
    """
    List files from B2 bucket with given prefix
    Returns list of file paths (relative to bucket root)
    """
    client = get_b2_client()
    if not client:
        return []
    
    try:
        response = client.list_objects_v2(
            Bucket=B2_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        files = []
        for obj in response.get('Contents', []):
            files.append(obj['Key'])
        
        return files
    except Exception as e:
        print(f"Error listing B2 files: {e}")
        return []

