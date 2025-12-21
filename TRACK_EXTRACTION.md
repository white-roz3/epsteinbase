# How to Track PDF Extraction Progress

## Quick Commands

### 1. Check if extraction is still running
```bash
ps aux | grep extract_images | grep -v grep
```

If you see a line with `extract_images.py`, the process is running.

### 2. Count extracted pages
```bash
# Count extracted full-size images
ls -1 data/extracted/COMBINED_ALL_EPSTEIN_FILES/page_*.png 2>/dev/null | wc -l

# Count thumbnails
ls -1 data/thumbnails/COMBINED_ALL_EPSTEIN_FILES/page_*.png 2>/dev/null | wc -l
```

### 3. Check disk usage
```bash
# Size of extracted images
du -sh data/extracted/COMBINED_ALL_EPSTEIN_FILES/

# Size of thumbnails
du -sh data/thumbnails/COMBINED_ALL_EPSTEIN_FILES/

# Total size
du -sh data/extracted/ data/thumbnails/
```

### 4. Check for completion (manifest file)
```bash
# If this file exists, extraction is complete
ls -lh data/extraction_manifest.json
```

## Automated Progress Checker

Use the progress checker script:

```bash
cd backend/scripts
python3 check_extraction_progress.py
```

This will show:
- ✓ Process status (running/stopped)
- 📄 Total pages in PDF
- 📊 Current progress (X / Y pages, percentage)
- ⏱️ Estimated time remaining
- 💾 Disk usage
- ✓ Completion status

## Watch Progress in Real-Time

### Watch extracted page count:
```bash
watch -n 30 'ls -1 data/extracted/COMBINED_ALL_EPSTEIN_FILES/page_*.png 2>/dev/null | wc -l'
```

This updates every 30 seconds showing the current count.

### Watch with details:
```bash
watch -n 60 'cd backend/scripts && python3 check_extraction_progress.py'
```

This runs the full progress check every minute.

## Manual Calculation

The PDF has approximately **4,055+ pages** (based on DOJ stats).

To see current progress:
```bash
EXTRACTED=$(ls -1 data/extracted/COMBINED_ALL_EPSTEIN_FILES/page_*.png 2>/dev/null | wc -l | tr -d ' ')
TOTAL=4055
PERCENT=$(echo "scale=1; $EXTRACTED * 100 / $TOTAL" | bc)
echo "Progress: $EXTRACTED / $TOTAL pages ($PERCENT%)"
```

## Expected Timeline

- **Total pages**: ~4,055
- **Extraction speed**: ~1-2 pages/second (varies by page complexity)
- **Estimated time**: 1-3 hours total
- **Disk space**: ~5-10GB for extracted images + thumbnails

## When Extraction Completes

You'll know it's done when:
1. ✅ `data/extraction_manifest.json` file exists
2. ✅ Process no longer appears in `ps aux | grep extract_images`
3. ✅ Page count matches total (~4,055)

Then run:
```bash
cd backend/scripts
export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/epsteinbase"
python3 ingest_extracted.py
```

This will add all extracted pages to the database.


