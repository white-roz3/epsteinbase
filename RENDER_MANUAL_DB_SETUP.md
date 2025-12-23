# Render Database Manual Setup

Since Blueprint doesn't exist, let's create the database manually:

## Step 1: Create PostgreSQL Database

1. Go to: https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"PostgreSQL"**
4. Configure:
   - **Name**: `epsteinbase-db`
   - **Database**: `epsteinbase`
   - **User**: `epsteinbase`
   - **Region**: Choose closest to you
   - **Plan**: Free (90 days) or Starter ($7/month)
5. Click **"Create Database"**

## Step 2: Link Database to API Service

1. Go to your **`epsteinbase-api`** service
2. Click **"Environment"** tab
3. Check if `DATABASE_URL` already exists (Render might auto-add it)
4. If not, click **"Add Environment Variable"**:
   - **Key**: `DATABASE_URL`
   - **Value**: Copy the "Internal Database URL" from your PostgreSQL service
   - Should look like: `postgresql://epsteinbase:password@dpg-xxxxx-a/epsteinbase`

## Step 3: Restart API Service

1. Go to `epsteinbase-api` service
2. Click **"Manual Deploy"** → **"Deploy latest commit"** (or just restart)
3. The app will now:
   - Connect to database ✅
   - Auto-initialize schema ✅
   - Start working ✅

## Alternative: Check Existing Services

If you want to see what services already exist:
- Go to: https://dashboard.render.com
- Look in the main dashboard for services
- Check if `epsteinbase-api` exists
- Check if any PostgreSQL databases exist

The database connection error will disappear once the database is created and linked!

