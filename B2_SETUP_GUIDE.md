# Backblaze B2 Setup Guide for EpsteinBase

## Choose: **B2 Cloud Storage** (NOT Computer Backup)

You need: **B2 Cloud Storage** (Object Storage)
- ✅ Object storage for applications
- ✅ S3 compatible API
- ✅ Perfect for storing your 36GB of images
- ✅ $0.005/GB-month (cheapest option!)

You DON'T need: Computer Backup
- ❌ That's for backing up computers/endpoints
- ❌ Not suitable for web application storage

## Step-by-Step Setup

### Step 1: Sign Up for Backblaze B2

1. Go to: https://www.backblaze.com/b2/cloud-storage.html
2. Click "Try for Free" under **B2 Cloud Storage**
3. Create an account (if you don't have one)

### Step 2: Create a Bucket

1. Log into Backblaze B2 dashboard
2. Go to "Buckets" section
3. Click "Create a Bucket"
4. **Bucket Name**: `epsteinbase-images` (or your choice)
5. **Bucket Type**: **Private** (recommended for your use case)
6. **Default Encryption**: Enabled (recommended)
7. Click "Create a Bucket"

### Step 3: Create Application Key (API Credentials)

1. Go to "App Keys" section
2. Click "Add a New Application Key"
3. **Name**: `epsteinbase-api-key`
4. **Allow access to Bucket(s)**: Select your bucket
5. **Type of access**: 
   - **Read and Write** (for uploading/managing files)
   - OR **Read Only** (if you'll upload files via CLI separately)
6. Click "Create New Key"
7. **IMPORTANT**: Save these credentials immediately (you can't see the key again!):
   - `applicationKeyId`: (like `xxxxx`)
   - `applicationKey`: (like `yyyyy`)

### Step 4: Get Your B2 Credentials

You'll need:
- **Key ID**: From the application key you just created
- **Application Key**: From the application key you just created
- **Bucket Name**: The bucket name you created (e.g., `epsteinbase-images`)
- **Endpoint URL**: Available in bucket settings, or use:
  - For private buckets: `https://f002.backblazeb2.com/file/your-bucket-name/`
  - Or use B2's S3-compatible endpoint

### Step 5: Pricing Information

**Storage Cost**: $0.005 per GB-month
- For 36GB: $0.005 × 36 = **$0.18/month**

**Free Egress**: 
- First 1 GB per day is free
- After that: $0.01 per GB
- For most web apps, you'll stay within free tier

**Total Cost**: ~**$0.18/month** (very cheap!)

## Next Steps: Integration with Your Backend

Once you have B2 set up, I can help you:

1. **Upload your 36GB of images** to B2 bucket
2. **Update backend code** to use B2 instead of filesystem
3. **Update database** file paths to use B2 URLs
4. **Configure environment variables** for B2 credentials

## Required Environment Variables

You'll need to add these to your Railway backend:

```bash
B2_APPLICATION_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_application_key
B2_BUCKET_NAME=epsteinbase-images
B2_ENDPOINT_URL=https://f002.backblazeb2.com/file/your-bucket-name/
```

## Python Library for B2

You'll use `boto3` (AWS SDK) which works with B2's S3-compatible API:

```python
import boto3
from botocore.config import Config

# Configure B2 S3-compatible endpoint
s3_client = boto3.client(
    's3',
    endpoint_url='https://s3.us-west-000.backblazeb2.com',  # Your B2 endpoint
    aws_access_key_id=B2_APPLICATION_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY,
)
```

## Benefits of B2

✅ **Cheapest option**: $0.18/month for 36GB
✅ **S3 compatible**: Use standard AWS SDK
✅ **Free egress**: First 1GB/day free
✅ **Reliable**: Enterprise-grade infrastructure
✅ **Fast**: Good performance for serving images

## Cost Comparison

| Solution | Monthly Cost |
|----------|-------------|
| **Backblaze B2** | **$0.18** ⭐ Cheapest |
| Railway Buckets | $0.54 |
| Cloudflare R2 | $0.54 |
| Railway Pro Plan | $20.00 |

Backblaze B2 is the most cost-effective option!


