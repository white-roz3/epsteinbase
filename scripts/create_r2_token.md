# Create R2 API Token via CLI

Unfortunately, Wrangler CLI doesn't support creating R2 API tokens directly. You need to create them via the Cloudflare dashboard.

## Quick Steps:

1. Go to: https://dash.cloudflare.com
2. Click "R2" in left sidebar
3. Click "Manage R2 API Tokens" (top right)
4. Click "Create API Token"
5. Name: "Render Backend Access"
6. Permissions: "Admin Read & Write" (or "Object Read & Write")
7. Buckets: "epsteinbase" (or "All buckets")
8. Click "Create API Token"
9. **Copy both Access Key ID and Secret Access Key immediately** (secret is only shown once!)

Once you have the keys, you can add them to Render or I can help you add them via environment variables if you share them.

