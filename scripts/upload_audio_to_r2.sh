#!/bin/bash
# Upload all audio files to R2 with live progress

BUCKET="epsteinbase"
SOURCE_DIR="data/audio"
R2_PREFIX="audio"

echo "📤 Starting audio upload to R2..."
echo "Bucket: $BUCKET"
echo "Source: $SOURCE_DIR"
echo ""

# Count files
TOTAL=$(find "$SOURCE_DIR" -type f \( -name "*.wav" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.aac" \) | wc -l | xargs)
echo "Found $TOTAL audio files to upload"
echo ""

COUNT=0
# Find all audio files
files=$(find "$SOURCE_DIR" -type f \( -name "*.wav" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.aac" \) 2>/dev/null | sort)

for file in $files; do
    [ -f "$file" ] || continue
    
    FILENAME=$(basename "$file")
    R2_PATH="$R2_PREFIX/$FILENAME"
    COUNT=$((COUNT + 1))
    
    # Get file size for display
    SIZE=$(ls -lh "$file" | awk '{print $5}')
    
    echo "[$COUNT/$TOTAL] Uploading $FILENAME ($SIZE)..."
    
    # Determine content type
    if [[ "$file" == *.wav ]]; then
        CONTENT_TYPE="audio/wav"
    elif [[ "$file" == *.mp3 ]]; then
        CONTENT_TYPE="audio/mpeg"
    elif [[ "$file" == *.m4a ]]; then
        CONTENT_TYPE="audio/mp4"
    elif [[ "$file" == *.aac ]]; then
        CONTENT_TYPE="audio/aac"
    else
        CONTENT_TYPE="audio/wav"
    fi
    
    npx wrangler r2 object put "$BUCKET/$R2_PATH" \
        --file="$file" \
        --content-type="$CONTENT_TYPE" \
        --remote
    
    if [ $? -eq 0 ]; then
        echo "✅ Success: $FILENAME"
    else
        echo "❌ Failed: $FILENAME"
    fi
    echo ""
done

echo "📊 Audio upload complete! Uploaded $COUNT/$TOTAL files"

