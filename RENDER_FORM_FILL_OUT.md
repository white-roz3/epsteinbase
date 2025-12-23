# Render Form - Exact Values to Enter

## Current Form Fields

### 1. Name
- **Value**: `epsteinbase-api` (or `epsteinbase` is fine)

### 2. Language ⚠️ CHANGE THIS
- **Current**: "Node" ❌
- **Change to**: "Python 3" ✅

### 3. Branch
- **Value**: `main` ✅ (already correct)

### 4. Region
- **Value**: "Oregon (US West)" ✅ (or any region is fine)

### 5. Root Directory (Optional)
- **Value**: Leave **BLANK** or use `backend`

### 6. Build Command ⚠️ CHANGE THIS
- **Current**: `$ npm install; npm run build` ❌
- **Change to**: 
  ```
  cd backend && pip install -r requirements.txt
  ```

### 7. Start Command ⚠️ CHANGE THIS
- **Current**: `$ yarn start` ❌ (or empty with red underline)
- **Change to**:
  ```
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### 8. Instance Type
- **Select**: **Free** ($0/month) for testing
- Or **Starter** ($7/month) if you want always-on (no spin-down)

### 9. Environment Variables
Click "+ Add Environment Variable" and add these 5:

1. **Name**: `B2_APPLICATION_KEY_ID`
   **Value**: `0055fbac3b92ba80000000001`

2. **Name**: `B2_APPLICATION_KEY`
   **Value**: `K005ezwA+wavo4CXgTmFzqKVrpcvDgc`

3. **Name**: `B2_BUCKET_NAME`
   **Value**: `Epsteinbase`

4. **Name**: `B2_ENDPOINT_URL`
   **Value**: `https://f005.backblazeb2.com/file/Epsteinbase/`

5. **Name**: `B2_S3_ENDPOINT`
   **Value**: `https://s3.us-east-005.backblazeb2.com`

### 10. Deploy
Click **"Deploy Web Service"** button at bottom

---

## Quick Copy-Paste

**Build Command:**
```
cd backend && pip install -r requirements.txt
```

**Start Command:**
```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## After Deployment

1. Wait for build to complete (5-10 minutes)
2. Create PostgreSQL database (we'll do this next)
3. Initialize database schema


