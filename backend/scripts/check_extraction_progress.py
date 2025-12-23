#!/usr/bin/env python3
"""Check progress of PDF extraction"""
import subprocess
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent.parent / "data"
EXTRACTED_DIR = DATA_DIR / "extracted" / "COMBINED_ALL_EPSTEIN_FILES"
THUMB_DIR = DATA_DIR / "thumbnails" / "COMBINED_ALL_EPSTEIN_FILES"
PDF_PATH = DATA_DIR / "pdfs" / "COMBINED_ALL_EPSTEIN_FILES.pdf"

def get_pdf_page_count():
    """Get total page count from PDF"""
    try:
        import fitz
        doc = fitz.open(str(PDF_PATH))
        count = len(doc)
        doc.close()
        return count
    except:
        return None

def get_extracted_count():
    """Count extracted pages"""
    if not EXTRACTED_DIR.exists():
        return 0
    return len(list(EXTRACTED_DIR.glob("page_*.png")))

def get_thumb_count():
    """Count thumbnails"""
    if not THUMB_DIR.exists():
        return 0
    return len(list(THUMB_DIR.glob("page_*.png")))

def get_process_status():
    """Check if extraction process is running"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.split('\n')
        for line in lines:
            if 'extract_images.py' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) >= 11:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    return {
                        "running": True,
                        "pid": pid,
                        "cpu": cpu,
                        "memory": mem
                    }
        return {"running": False}
    except:
        return {"running": False}

def get_dir_size(path):
    """Get directory size in GB"""
    if not path.exists():
        return 0.0
    total = 0
    for file in path.rglob("*"):
        if file.is_file():
            total += file.stat().st_size
    return total / (1024 ** 3)

def main():
    print("=" * 60)
    print("PDF EXTRACTION PROGRESS")
    print("=" * 60)
    print(f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check process
    proc = get_process_status()
    if proc["running"]:
        print(f"✓ Extraction process is RUNNING")
        print(f"  PID: {proc['pid']}")
        print(f"  CPU: {proc['cpu']}%")
        print(f"  Memory: {proc['memory']}%")
    else:
        print("✗ Extraction process NOT running")
        print("  (May have completed or crashed)")
    
    # Check PDF info
    total_pages = get_pdf_page_count()
    if total_pages:
        print(f"\n📄 PDF: COMBINED_ALL_EPSTEIN_FILES.pdf")
        print(f"   Total pages: {total_pages:,}")
    else:
        print(f"\n⚠️  Could not read PDF page count")
    
    # Check extracted pages
    extracted = get_extracted_count()
    thumbs = get_thumb_count()
    
    print(f"\n📊 Progress:")
    if total_pages:
        percent = (extracted / total_pages * 100) if total_pages > 0 else 0
        print(f"   Pages extracted: {extracted:,} / {total_pages:,} ({percent:.1f}%)")
        
        # Estimate remaining time (rough)
        if proc["running"] and extracted > 100:
            # Rough estimate: assume ~1-2 pages per second average
            remaining = total_pages - extracted
            est_seconds = remaining * 0.5  # conservative estimate
            est_minutes = est_seconds / 60
            est_hours = est_minutes / 60
            if est_hours >= 1:
                print(f"   Estimated time remaining: ~{est_hours:.1f} hours")
            else:
                print(f"   Estimated time remaining: ~{est_minutes:.0f} minutes")
    else:
        print(f"   Pages extracted: {extracted:,}")
    
    print(f"   Thumbnails created: {thumbs:,}")
    
    # Check file sizes
    extracted_size = get_dir_size(EXTRACTED_DIR)
    thumb_size = get_dir_size(THUMB_DIR)
    
    print(f"\n💾 Disk Usage:")
    print(f"   Extracted images: {extracted_size:.2f} GB")
    print(f"   Thumbnails: {thumb_size:.2f} GB")
    print(f"   Total: {extracted_size + thumb_size:.2f} GB")
    
    # Check for manifest
    manifest_path = DATA_DIR / "extraction_manifest.json"
    if manifest_path.exists():
        import json
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"\n✓ Extraction COMPLETE!")
        print(f"   Manifest created with {len(manifest)} entries")
        print(f"\n   Next step: Run 'python3 ingest_extracted.py'")
    else:
        print(f"\n⏳ Extraction in progress...")
        print(f"   Manifest not yet created")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()



