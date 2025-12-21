#!/usr/bin/env python3
"""Extract images from PDFs and create thumbnails"""
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import json
import re

# Data directory (relative to scripts/)
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "extracted"
THUMB_DIR = DATA_DIR / "thumbnails"

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
THUMB_DIR.mkdir(exist_ok=True, parents=True)

def extract_efta_id(text: str) -> str:
    """Extract EFTA ID from page text if present"""
    if not text:
        return None
    match = re.search(r'EFTA\d{8}', text)
    return match.group(0) if match else None

def extract_from_pdf(pdf_path: Path):
    """Extract embedded images and render pages"""
    print(f"\nProcessing {pdf_path.name}...")
    doc = fitz.open(str(pdf_path))
    pdf_name = pdf_path.stem
    results = []
    
    output_subdir = OUTPUT_DIR / pdf_name
    thumb_subdir = THUMB_DIR / pdf_name
    output_subdir.mkdir(exist_ok=True, parents=True)
    thumb_subdir.mkdir(exist_ok=True, parents=True)
    
    total_pages = len(doc)
    print(f"  Total pages: {total_pages}")
    
    for page_num in range(total_pages):
        try:
            page = doc[page_num]
            
            # Render page as image (for scanned docs)
            mat = fitz.Matrix(1.5, 1.5)  # 1.5x zoom = ~108 DPI
            pix = page.get_pixmap(matrix=mat)
            
            page_filename = f"page_{page_num:05d}.png"
            page_path = output_subdir / page_filename
            pix.save(str(page_path))
            
            # Create thumbnail
            thumb_path = thumb_subdir / page_filename
            try:
                img = Image.open(page_path)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumb_path, quality=85, optimize=True)
            except Exception as e:
                print(f"    Warning: Could not create thumbnail for page {page_num}: {e}")
            
            # Extract text
            text = page.get_text()
            efta_id = extract_efta_id(text) if text else None
            
            # Save OCR text to file for incremental ingestion
            if text:
                text_filename = f"page_{page_num:05d}.txt"
                text_path = output_subdir / text_filename
                try:
                    text_path.write_text(text[:50000], encoding='utf-8')
                except Exception as e:
                    print(f"    Warning: Could not save text for page {page_num}: {e}")
            
            # Limit text size for storage
            ocr_text = text[:50000] if text else None
            
            results.append({
                "source_pdf": pdf_path.name,
                "page_number": page_num,
                "file_path": f"extracted/{pdf_name}/{page_filename}",
                "thumbnail_path": f"thumbnails/{pdf_name}/{page_filename}",
                "ocr_text": ocr_text,
                "efta_id": efta_id
            })
            
            if (page_num + 1) % 100 == 0:
                print(f"  Processed {page_num + 1}/{total_pages} pages...")
        except Exception as e:
            print(f"  Error processing page {page_num}: {e}")
            continue
    
    doc.close()
    return results

def main():
    pdf_files = list((DATA_DIR / "pdfs").glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {DATA_DIR / 'pdfs'}")
        print("Run download_data.py first to download PDFs")
        return
    
    all_results = []
    
    for pdf_file in sorted(pdf_files):
        results = extract_from_pdf(pdf_file)
        all_results.extend(results)
        print(f"  Extracted {len(results)} pages from {pdf_file.name}")
    
    # Save manifest
    manifest_path = DATA_DIR / "extraction_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✓ Total: {len(all_results)} pages extracted")
    print(f"✓ Manifest saved to {manifest_path}")

if __name__ == "__main__":
    main()

