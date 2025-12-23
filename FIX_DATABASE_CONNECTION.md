# Fix Database Connection Issue

The error `'NoneType' object has no attribute 'acquire'` means `DATABASE_URL` is not set or the database isn't linked.

## Check These:

1. **In Render Dashboard → `epsteinbase-api` → Environment:**
   - Look for `DATABASE_URL` variable
   - If it's NOT there, the database isn't linked!

2. **If DATABASE_URL is missing:**
   - Go to `epsteinbase-db` (PostgreSQL service)
   - Click "Connections" tab
   - Look for "Internal Database URL" or "Connection String"
   - Copy it
   - Go back to `epsteinbase-api` → Environment
   - Add: `DATABASE_URL` = (paste the connection string)
   - Save and redeploy

3. **Verify database exists:**
   - Check if `epsteinbase-db` shows as "Available" or "Running"
   - If not, the Blueprint might not have created it properly

## Quick Fix:

If DATABASE_URL is missing, add it manually to the API service environment variables!

