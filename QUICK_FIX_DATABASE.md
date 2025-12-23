# Quick Fix: Create Database on Render

## The Problem
Your API is running but can't connect to database because it doesn't exist yet.

## Quick Solution (2 minutes)

### Option 1: Create Database Manually (Easiest)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"PostgreSQL"**
3. **Fill in**:
   - Name: `epsteinbase-db`
   - Database: `epsteinbase`  
   - User: `epsteinbase`
   - Plan: Free
4. **Click "Create Database"**
5. **Go to your `epsteinbase-api` service** → **Environment tab**
6. **Verify `DATABASE_URL` is auto-set** (Render should do this automatically)
7. **Restart the service** (Manual Deploy → Deploy latest commit)

That's it! The app will auto-initialize the schema on next startup.

### Option 2: Check What Exists First

1. Go to: https://dashboard.render.com
2. Look at your services list
3. See if `epsteinbase-api` exists
4. See if any PostgreSQL database exists
5. If database exists but not linked, add `DATABASE_URL` manually

The auto-initialization code is already deployed, so once the database is connected, everything will work automatically!

