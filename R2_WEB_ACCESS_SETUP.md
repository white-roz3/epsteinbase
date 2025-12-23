# Make R2 Files Accessible on the Web

## ✅ What's Done:
- ✅ Files uploaded to R2 bucket `epsteinbase`
- ✅ Backend code updated to use R2 URLs
- ⏳ Need to enable Public Development URL

## 🔧 Final Step: Enable Public Access

**In Cloudflare Dashboard:**
1. Go to: https://dash.cloudflare.com
2. Navigate to **R2** → **epsteinbase** bucket
3. Click **Settings** tab
4. Find **"Public Development URL"** section
5. Click **"Enable"** button

## 📍 Your Files Will Be Accessible At:

Once Public Development URL is enabled:

**Images:**
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/images/{filename}.png
```

**Audio:**
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/audio/{filename}.wav
```

## 🔧 Backend Configuration:

Set these environment variables in Render/Vercel:

```bash
STORAGE_TYPE=r2
R2_ACCOUNT_ID=ad3c74e324b945bcde28453399bdecbb
R2_BUCKET_NAME=epsteinbase
R2_PUBLIC_URL=https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase
```

## ✅ Code Updates Made:

1. ✅ Updated `backend/app/b2_client.py` to support R2
2. ✅ Updated `backend/app/main.py` to use `get_file_url()` for R2/B2 compatibility
3. ✅ Files are uploaded to R2

## 🧪 Test After Enabling:

Try accessing a file directly:
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/images/page_00001.png
```

If you get a 403 error, Public Development URL is not enabled yet.

