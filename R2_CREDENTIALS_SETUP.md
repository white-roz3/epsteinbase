# R2 Credentials Setup

## ✅ What's Done:
- ✅ Logged into Cloudflare CLI
- ✅ Created R2 bucket: `epsteinbase`
- ✅ Account ID: `ad3c74e324b945bcde28453399bdecbb`

## 📝 Next Steps - Get API Tokens:

1. **Go to Cloudflare Dashboard**:
   - Visit: https://dash.cloudflare.com
   - Navigate to **R2** in the sidebar

2. **Create API Token**:
   - Click **Manage R2 API Tokens** (usually at the top right or in settings)
   - Click **Create API Token**
   - Name it: `epsteinbase-api`
   - **Permissions**: Select **Object Read & Write**
   - **Bucket access**: Select `epsteinbase` bucket
   - Click **Create API Token**

3. **Save Your Credentials** (shown only once!):
   - **Access Key ID**: Copy this
   - **Secret Access Key**: Copy this

## 🔧 Environment Variables for Render/Vercel:

Once you have the tokens, set these environment variables:

```bash
STORAGE_TYPE=r2
R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
R2_ACCESS_KEY_ID=your_access_key_id_here
R2_SECRET_ACCESS_KEY=your_secret_access_key_here
R2_BUCKET_NAME=epsteinbase
R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase
```

## 📤 Upload Files to R2:

### Option 1: Using Wrangler CLI

```bash
# Upload a single file
npx wrangler r2 object put epsteinbase/extracted/test.png --file=./data/extracted/test.png

# Upload a directory (recursive)
# Note: Wrangler doesn't have recursive upload built-in, so we'll need a script
```

### Option 2: Using AWS CLI (S3-compatible)

```bash
# Configure AWS CLI for R2
export AWS_ENDPOINT_URL_R2=https://ad3c74e324b945bcde28453399bdecbb.r2.cloudflarestorage.com
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key

# Upload files
aws s3 cp data/extracted/ s3://epsteinbase/extracted/ \
  --recursive \
  --endpoint-url $AWS_ENDPOINT_URL_R2
```

### Option 3: Python Script (I can create this for you)

Let me know once you have the API tokens and I can create an upload script!

## 🔗 Public Access URL:

Your files will be accessible at:
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/{file_path}
```

Example:
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/extracted/page_00001.png
```

## 🎯 Current Status:

- ✅ Bucket created: `epsteinbase`
- ✅ Account ID: `ad3c74e324b945bcde28453399bdecbb`
- ⏳ Waiting for API tokens from dashboard
- ⏳ Then we'll configure environment variables
- ⏳ Then upload files

