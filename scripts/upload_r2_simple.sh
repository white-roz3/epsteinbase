#!/bin/bash
# Simple R2 upload with live output

BUCKET="epsteinbase"
SOURCE_DIR="public/curated/images"
R2_PREFIX="images"

echo "📤 Starting upload to R2..."
echo "Bucket: $BUCKET"
echo "Source: $SOURCE_DIR"
echo ""

COUNT=0
TOTAL=$(find "$SOURCE_DIR" -name "*.png" | wc -l | xargs)

echo "Found $TOTAL files to upload"
echo ""

for file in "$SOURCE_DIR"/*.png; do
    [ -f "$file" ] || continue
    
    FILENAME=$(basename "$file")
    R2_PATH="$R2_PREFIX/$FILENAME"
    COUNT=$((COUNT + 1))
    
    echo "[$COUNT/$TOTAL] Uploading $FILENAME..."
    
    npx wrangler r2 object put "$BUCKET/$R2_PATH" \
        --file="$file" \
        --content-type="image/png" \
        --remote 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Success: $FILENAME"
    else
        echo "❌ Failed: $FILENAME"
    fi
    echo ""
done

echo "📊 Upload complete! Uploaded $COUNT/$TOTAL files"

