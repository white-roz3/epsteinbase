#!/bin/bash

# Check B2 upload status

echo "📊 Checking B2 bucket contents..."
echo ""

echo "Files in extracted/:"
b2 ls Epsteinbase extracted/ | head -20
echo ""
echo "(Showing first 20 files. Use 'b2 ls Epsteinbase extracted/' for full list)"
echo ""

echo "Files in thumbnails/:"
b2 ls Epsteinbase thumbnails/ | head -20
echo ""

echo "To check upload progress, you can compare:"
echo "  Local files: find data/extracted -type f | wc -l"
echo "  B2 files: b2 ls Epsteinbase extracted/ | wc -l"


