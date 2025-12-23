#!/bin/bash

# Backblaze B2 Upload Script for EpsteinBase
# This script helps authenticate and upload images to B2

set -e

echo "🚀 Backblaze B2 Upload Script"
echo ""

# Check if authenticated
if ! b2 bucket list &>/dev/null; then
    echo "⚠️  Not authenticated with B2"
    echo ""
    echo "To authenticate, you need:"
    echo "1. Application Key ID (from Backblaze dashboard)"
    echo "2. Application Key (from Backblaze dashboard)"
    echo ""
    echo "Option 1: Authenticate now (you'll be prompted for credentials)"
    read -p "Do you want to authenticate now? (y/n): " auth_choice
    
    if [ "$auth_choice" = "y" ] || [ "$auth_choice" = "Y" ]; then
        read -p "Enter Application Key ID: " key_id
        read -sp "Enter Application Key: " key_secret
        echo ""
        b2 authorize-account "$key_id" "$key_secret"
        echo "✅ Authenticated!"
    else
        echo ""
        echo "To authenticate manually, run:"
        echo "  b2 authorize-account <keyID> <applicationKey>"
        echo ""
        echo "Or set environment variables:"
        echo "  export B2_APPLICATION_KEY_ID=your_key_id"
        echo "  export B2_APPLICATION_KEY=your_key_secret"
        echo "  b2 authorize-account"
        exit 1
    fi
fi

# Verify authentication
echo ""
echo "✅ Authentication verified!"
echo ""

# List buckets
echo "Available buckets:"
b2 bucket list
echo ""

# Get bucket name
read -p "Enter bucket name (or create new): " bucket_name

# Check if bucket exists, if not create it
if ! b2 bucket list | grep -q "$bucket_name"; then
    echo "Bucket '$bucket_name' not found. Creating new bucket..."
    read -p "Bucket type (allPublic/allPrivate) [allPrivate]: " bucket_type
    bucket_type=${bucket_type:-allPrivate}
    b2 create-bucket "$bucket_name" "$bucket_type"
    echo "✅ Bucket '$bucket_name' created!"
fi

echo ""
echo "📦 Uploading files to B2..."
echo ""
echo "This will upload:"
echo "  - data/extracted/ → b2://$bucket_name/extracted/"
echo "  - data/thumbnails/ → b2://$bucket_name/thumbnails/"
echo ""
echo "⚠️  This may take a while (8GB+ of data)..."
echo ""

read -p "Continue with upload? (y/n): " upload_choice
if [ "$upload_choice" != "y" ] && [ "$upload_choice" != "Y" ]; then
    echo "Upload cancelled."
    exit 0
fi

# Upload extracted images
echo ""
echo "📤 Uploading extracted images..."
b2 sync --threads 4 data/extracted/ "b2://$bucket_name/extracted/"

# Upload thumbnails
echo ""
echo "📤 Uploading thumbnails..."
b2 sync --threads 4 data/thumbnails/ "b2://$bucket_name/thumbnails/"

echo ""
echo "✅ Upload complete!"
echo ""
echo "Next steps:"
echo "1. Get your B2 endpoint URL from bucket settings"
echo "2. Update backend code to use B2 URLs"
echo "3. Update database file paths"


