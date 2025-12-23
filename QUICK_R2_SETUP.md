# Quick R2 API Token Setup

## Steps in Cloudflare Dashboard:

1. **Go to**: https://dash.cloudflare.com
2. **Click**: **R2** in left sidebar
3. **Look for**: **"Manage R2 API Tokens"** button (usually top right)
4. **Click**: **"Create API Token"**
5. **Fill out**:
   - **Name**: `epsteinbase-api`
   - **Permissions**: **Admin Read & Write** ⭐ (this is the key one!)
   - **Bucket**: Select `epsteinbase`
6. **Click**: **Create API Token**
7. **Copy these** (shown only once!):
   - Access Key ID
   - Secret Access Key

## Then Provide Me With:

Once you have the tokens, I'll need:
- Access Key ID
- Secret Access Key

Then I'll help you:
- ✅ Set environment variables
- ✅ Upload files to R2
- ✅ Configure backend to use R2

