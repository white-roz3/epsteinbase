#!/bin/bash
# Upload curated images to R2 using Wrangler

BUCKET="epsteinbase"
SOURCE_DIR="public/curated/images"

echo "📤 Uploading curated images to R2..."
echo "Bucket: $BUCKET"
echo "Source: $SOURCE_DIR"
echo ""

# Count files
TOTAL=$(find "$SOURCE_DIR" -type f -name "*.png" | wc -l | xargs)
echo "Found $TOTAL images to upload"
echo ""

COUNT=0
for file in "$SOURCE_DIR"/*.png; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        R2_PATH="images/$FILENAME"
        
        echo "[$((++COUNT))/$TOTAL] Uploading $FILENAME..."
        npx wrangler r2 object put "$BUCKET/$R2_PATH" \
            --file="$file" \
            --content-type="image/png" \
            --remote
        
        if [ $? -eq 0 ]; then
            echo "✅ Uploaded: $FILENAME"
        else
            echo "❌ Failed: $FILENAME"
        fi
        echo ""
    fi
done

echo "📊 Upload complete!"

