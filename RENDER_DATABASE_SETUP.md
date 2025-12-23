# Render Database Setup

## Current Status
✅ Backend deployed and running at: https://epsteinbase.onrender.com
❌ Database connection failing: "Connection refused"

## What to Do Next

### 1. Check Database Service in Render Dashboard
- Go to https://dashboard.render.com
- Check if `epsteinbase-db` PostgreSQL service exists
- If not created by Blueprint, create it manually:
  - New + → PostgreSQL
  - Name: `epsteinbase-db`
  - Plan: Free (90 days) or Starter ($7/month)

### 2. Link Database to API Service
- Go to your `epsteinbase-api` service
- Environment tab → Add Environment Variable
- **Important:** Render should auto-create `DATABASE_URL`, but verify it exists
- It should look like: `postgresql://epsteinbase:password@dpg-xxxxx/epsteinbase`

### 3. Initialize Database Schema
After database is connected:

**Option A: Via Render Dashboard**
1. Go to PostgreSQL service → "Connect" or "Shell"
2. Connect via psql
3. Run the schema from `backend/init.sql`

**Option B: Via API Endpoint (if we add one)**
- Could create a `/init` endpoint, but not recommended for production

**Option C: Local connection**
```bash
psql $DATABASE_URL -f backend/init.sql
```

### 4. Restart API Service
- After setting DATABASE_URL, restart the `epsteinbase-api` service
- The connection error should disappear

## Current Error Explanation
"Connection refused" means:
- The database service doesn't exist, OR
- DATABASE_URL is not set, OR  
- Database service is not accessible from the API service

This is a configuration issue, not a code problem!

