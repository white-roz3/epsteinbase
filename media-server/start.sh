#!/bin/bash
# Start script for media server
cd "$(dirname "$0")"

# Set default port if not provided
export PORT=${PORT:-8001}
export MEDIA_DIR=${MEDIA_DIR:-$(pwd)/../data}

echo "Starting media server..."
echo "Port: $PORT"
echo "Media Directory: $MEDIA_DIR"

# Check if media directory exists
if [ ! -d "$MEDIA_DIR" ]; then
    echo "Warning: Media directory not found: $MEDIA_DIR"
    echo "Please set MEDIA_DIR environment variable or ensure ../data exists"
fi

# Run the server
python3 server.py

