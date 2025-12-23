# Railway Storage Options & Limits

## Your Current Usage
- **Images/Data**: ~36GB (actual size)

## Railway Storage Options

### Option 1: Persistent Volumes (For Direct File Access)

Best for: Serving files directly from the filesystem (your current setup)

| Plan | Storage per Volume | Cost |
|------|-------------------|------|
| **Free/Trial** | 0.5 GB | Free (limited trial) |
| **Hobby** | 5 GB | $5/month |
| **Pro** | 50 GB (expandable to 250 GB) | $20/month |
| **Enterprise** | Custom (contact Railway) | Custom pricing |

**Your 36GB fits in:**
- ❌ **Hobby Plan** ($5/month) - Only 5 GB (too small)
- ⚠️ **Pro Plan** ($20/month) - 50 GB base, needs expansion to 250 GB (contact Railway)
- ✅ **Pro Plan + Buckets** ($20/month + storage fees) - Unlimited storage

**Note**: Pro users can self-serve expand volumes up to 250 GB. Beyond that, contact Railway support.

### Option 2: Object Storage (Buckets) - S3-Compatible

Best for: Storing large files, backups, or when you need more storage

| Plan | Storage Limit | Cost |
|------|--------------|------|
| **Free** | 10 GB-month | Free |
| **Trial** | 50 GB-month (during trial) | Free |
| **Hobby** | Up to 1 TB | $5/month + $0.015/GB-month |
| **Pro** | **Unlimited** | $20/month + $0.015/GB-month |

**Buckets Pricing:**
- Storage: $0.015 per GB-month
- API operations: Unlimited & free
- Egress/bandwidth: Unlimited & free

**For 36GB with Buckets:**
- Hobby: $5/month + ($0.015 × 36) = **~$5.54/month** (but Hobby has 1TB limit on buckets, so you're good)
- Pro: $20/month + ($0.015 × 36) = **~$20.54/month** (unlimited buckets)

## Recommendation for Your Use Case

### Current Setup (36GB images):

**❌ Hobby Plan won't work** - Only 5GB available, you have 36GB

### ✅ Best Option: Pro Plan (Recommended)

**Option 1: Pro Plan with Base Volume**
- **50 GB base volume** (included with Pro plan)
- **Cost**: $20/month
- Works with your current code (no changes needed)
- Direct filesystem access via persistent volumes
- **Your 36GB fits perfectly!** ✅ (~14GB headroom)

**If you exceed 50GB later:**
- Contact Railway support to expand volume to 250GB (no extra cost)

**Option 2: Pro Plan + Buckets (Alternative)**
- **Unlimited storage**
- **Cost**: $20/month + ($0.015 × 36GB) = **~$20.54/month**
- Requires code changes to use S3 API
- Better long-term scalability
- More setup work

### If You Need More Storage Later:

**Option A: Upgrade to Pro Plan**
- Get 50 GB per volume (expandable to 250 GB)
- Cost: $20/month
- Still uses persistent volumes (no code changes needed)

**Option B: Use Buckets (Object Storage)**
- Hobby: 1 TB limit ($5/month + $0.015/GB)
- Pro: Unlimited ($20/month + $0.015/GB)
- Requires code changes to use S3 API
- Better for very large files or future scaling

## Current Storage Architecture

Your backend serves files from:
```
backend/app/main.py:
  DATA_DIR = Path(__file__).parent.parent.parent / "data"
  app.mount("/files", StaticFiles(directory=str(DATA_DIR)))
```

This works perfectly with **Railway Persistent Volumes** - just mount the volume to your service and point to the mounted path.

## Comparison: Volume vs Bucket

| Feature | Volume (Current) | Buckets |
|---------|-----------------|---------|
| **Setup** | Mount to service | Use S3 API |
| **Code Changes** | None needed | Need to refactor |
| **Access** | Direct filesystem | API calls |
| **Cost** | Included in plan | $0.015/GB-month extra |
| **Limit (Hobby)** | 5 GB | 1 TB |
| **Limit (Pro)** | 50-250 GB | Unlimited |

## Bottom Line

**For 36GB: Railway Pro Plan ($20/month) required**

**Best Option: Pro Plan ($20/month)**
- Base 50GB volume included (your 36GB fits perfectly!)
- Works with your current code (no changes needed)
- Direct filesystem access via persistent volumes
- Can expand to 250GB later if needed (contact Railway)

**Alternative: Pro Plan + Buckets**
- Unlimited storage
- Cost: ~$20.54/month
- Requires code refactoring to use S3 API
- Better for future scaling beyond 250GB

**Considerations:**
- 36GB is substantial - you may want to consider:
  - Cleaning up/compressing old images
  - Moving to external CDN (Cloudflare R2, AWS S3) for better cost/efficiency
  - Using Railway Buckets for better scalability

