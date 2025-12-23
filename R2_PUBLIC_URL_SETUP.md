# Making R2 Files Publicly Accessible

## Current Status

Files uploaded to R2 are accessible via Public Development URL (if enabled).

## To Enable Public Access:

1. **Go to Cloudflare Dashboard**:
   - https://dash.cloudflare.com
   - Navigate to **R2** → **epsteinbase** bucket
   - Click **Settings** tab

2. **Enable Public Development URL**:
   - Find **"Public Development URL"** section
   - Click **"Enable"** button
   - This gives you a public URL like: `https://pub-{account_id}.r2.dev/epsteinbase/`

## Your Public URLs:

Once enabled, files will be accessible at:

**Images:**
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/images/{filename}.png
```

**Audio:**
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/audio/{filename}.wav
```

## Example URLs:

If you uploaded `page_00001.png`:
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/images/page_00001.png
```

If you uploaded `Day_1_-_Part_1_-_7_24_25_Tallahassee.003.wav`:
```
https://pub-ad3c74e324b945bcde28453399bdecbb.r2.dev/epsteinbase/audio/Day_1_-_Part_1_-_7_24_25_Tallahassee.003.wav
```

## Test if Files are Accessible:

Try opening these URLs in your browser after enabling Public Development URL. If you see a 403 error, you need to enable public access in Settings.

