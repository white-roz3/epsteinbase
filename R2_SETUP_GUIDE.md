# Cloudflare R2 Setup Guide

## Why R2?

**Cloudflare R2** is perfect for your use case:

✅ **10GB free storage** (more than enough for curated images)  
✅ **1M free Class A operations/month** (uploads/listings)  
✅ **10M free Class B operations/month** (downloads/reads)  
✅ **Zero egress fees** - No charges for bandwidth/downloads (unlike S3)  
✅ **S3-compatible API** - Works with existing boto3 code  
✅ **Fast global CDN** - Files served from Cloudflare's edge network  
✅ **Simple setup** - Just need API tokens

## Setup Steps

### 1. Create R2 Bucket

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **R2** in the sidebar
3. Click **Create bucket**
4. Name it: `epsteinbase`
5. Click **Create bucket**

### 2. Get API Tokens

1. In R2, click **Manage R2 API Tokens**
2. Click **Create API Token**
3. Set permissions:
   - **Permissions**: Object Read & Write
   - **TTL**: Leave empty (no expiration) or set to a future date
4. Click **Create API Token**
5. **Copy these values** (shown only once!):
   - **Account ID** (you'll see this at the top of R2 page)
   - **Access Key ID**
   - **Secret Access Key**

### 3. Configure Public Access (Optional but Recommended)

To serve files directly from R2:

1. Go to your bucket settings
2. Enable **Public Access**
3. Set a **Custom Domain** (optional, e.g., `media.epsteinbase.xyz`) OR use the default R2 public URL

### 4. Set Environment Variables

Add these to your Render/Railway/Vercel environment variables:

```bash
STORAGE_TYPE=r2
R2_ACCOUNT_ID=your_account_id_here
R2_ACCESS_KEY_ID=your_access_key_id_here
R2_SECRET_ACCESS_KEY=your_secret_access_key_here
R2_BUCKET_NAME=epsteinbase
R2_PUBLIC_URL=https://pub-{account_id}.r2.dev/epsteinbase
# OR if using custom domain:
# R2_PUBLIC_URL=https://media.epsteinbase.xyz
```

**For Render:**
- Go to your service → Environment → Add environment variable
- Add each variable above

## Upload Files to R2

### Option 1: Using AWS CLI (Easiest)

```bash
# Install AWS CLI
brew install awscli  # macOS
# or: pip install awscli

# Configure AWS CLI for R2
aws configure --profile r2
# Access Key ID: [your R2_ACCESS_KEY_ID]
# Secret Access Key: [your R2_SECRET_ACCESS_KEY]
# Default region: auto
# Default output: json

# Set R2 endpoint
export AWS_ENDPOINT_URL_R2=https://your-account-id.r2.cloudflarestorage.com

# Upload files
aws s3 cp data/extracted/ s3://epsteinbase/extracted/ \
  --recursive \
  --endpoint-url $AWS_ENDPOINT_URL_R2 \
  --profile r2
```

### Option 2: Using Python Script

I can create an upload script similar to your B2 upload script. Let me know if you want this!

### Option 3: Using Cloudflare Dashboard

1. Go to your R2 bucket in Cloudflare dashboard
2. Click **Upload** button
3. Drag and drop files/folders

## Migration from B2 to R2

If you want to switch from B2 to R2:

1. Upload your files to R2 (see above)
2. Set the environment variables (see step 4)
3. Update `STORAGE_TYPE=r2` in your environment
4. Restart your backend service
5. Your API will now serve files from R2 instead of B2

## Cost Comparison

### R2 (Free Tier)
- 10GB storage: **FREE**
- 1M operations/month: **FREE**
- 10M reads/month: **FREE**
- Egress/bandwidth: **FREE** ⭐
- **Total: $0/month** for most use cases

### B2 (Current)
- 10GB storage: **$0.005/GB/month = $0.05/month**
- Operations: **FREE**
- Downloads: **$0.01/GB** ⚠️
- **Total: ~$0.05/month + download costs**

**Winner: R2** - Zero egress fees means unlimited downloads for free!

## Testing R2

Once configured, test with:

```bash
# Check if files are accessible
curl https://pub-{account_id}.r2.dev/epsteinbase/extracted/test.png

# Or using your API
curl https://your-api-url.com/api/files/images
```

## Troubleshooting

**Issue: "Access Denied"**
- Check that your API token has "Object Read & Write" permissions
- Verify `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY` are correct

**Issue: "Bucket not found"**
- Verify `R2_BUCKET_NAME` matches your bucket name exactly
- Check that `R2_ACCOUNT_ID` is correct

**Issue: Files not publicly accessible**
- Make sure Public Access is enabled in bucket settings
- Verify `R2_PUBLIC_URL` is set correctly

## Current Code Support

The updated `backend/app/b2_client.py` now supports both B2 and R2:

- If `STORAGE_TYPE=r2` and R2 credentials are set → Uses R2
- Otherwise, falls back to B2 (if B2 credentials exist)
- Backward compatible with existing B2 code

No code changes needed in `main.py` - it will automatically use R2 when configured!

