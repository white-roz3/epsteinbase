# Render Docker Build Issue

## Problem
Render is NOT using the Dockerfile - it's using Python 3.13.4 buildpack instead of Docker with Python 3.11.

## Evidence
Logs show: `/opt/render/project/python/Python-3.13.4/include/python3.13/`
This is Render's Python buildpack, not Docker.

## Current render.yaml
```yaml
services:
  - type: web
    name: epsteinbase-api
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
```

## Possible Solutions

1. **Remove dockerfilePath and use Docker service type:**
   ```yaml
   services:
     - type: web
       name: epsteinbase-api
       dockerfilePath: ./backend/Dockerfile
   ```

2. **Or configure in Render Dashboard:**
   - Go to service settings
   - Change "Environment" from "Python" to "Docker"
   - Set Dockerfile Path to `backend/Dockerfile`
   - Set Docker Context to `backend`

3. **Or use buildCommand with explicit Docker build:**
   Might not be possible with Blueprint.

## Recommendation
Configure Docker manually in Render Dashboard instead of using Blueprint, as Blueprint might not support Docker properly.

