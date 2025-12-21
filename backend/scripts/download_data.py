#!/usr/bin/env python3
"""Download Epstein files from Internet Archive and DOJ"""
import os
import subprocess
from pathlib import Path

# Data directory (relative to scripts/)
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Internet Archive - Complete DOJ Release (best source)
ARCHIVE_FILES = [
    "https://archive.org/download/combined-all-epstein-files/COMBINED_ALL_EPSTEIN_FILES.pdf",
    # Alternative: Individual datasets if combined doesn't work
    # "https://archive.org/download/combined-all-epstein-files/DataSet_1_COMPLETE.pdf",
    # "https://archive.org/download/combined-all-epstein-files/DataSet_2_COMPLETE.pdf",
]

# DOJ Direct files (videos, audio)
DOJ_VIDEOS = [
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video1.mp4",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video2.mp4",
]

DOJ_AUDIO = [
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%201%20-%207_24_25_Tallahassee.003.wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%202%20-%207_24_25_Tallahassee.004.wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%203%20-%207_24_25_Tallahassee.005%20(R).wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%204%20-%207_24_25_Tallahassee.007.wav",
]

def download_file(url: str, dest_dir: Path):
    """Download a file using wget or curl"""
    filename = url.split("/")[-1].replace("%20", "_")
    dest = dest_dir / filename
    
    if dest.exists():
        print(f"✓ Skipping {filename} (already exists)")
        return dest
    
    print(f"Downloading {filename}...")
    
    # Try wget first, then curl
    try:
        subprocess.run(
            ["wget", "-q", "--show-progress", "-O", str(dest), url],
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run(
                ["curl", "-L", "-o", str(dest), url],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to download {filename}: {e}")
            return None
    
    print(f"✓ Downloaded {filename}")
    return dest

def main():
    # Create subdirectories
    (DATA_DIR / "pdfs").mkdir(exist_ok=True, parents=True)
    (DATA_DIR / "images").mkdir(exist_ok=True, parents=True)
    (DATA_DIR / "videos").mkdir(exist_ok=True, parents=True)
    (DATA_DIR / "audio").mkdir(exist_ok=True, parents=True)
    
    print("=== Downloading Internet Archive PDFs ===\n")
    for url in ARCHIVE_FILES:
        if url.endswith('.pdf'):
            download_file(url, DATA_DIR / "pdfs")
        elif url.endswith('.zip'):
            download_file(url, DATA_DIR / "images")
    
    print("\n=== Downloading DOJ Videos ===\n")
    for url in DOJ_VIDEOS:
        download_file(url, DATA_DIR / "videos")
    
    print("\n=== Downloading DOJ Audio ===\n")
    for url in DOJ_AUDIO:
        download_file(url, DATA_DIR / "audio")
    
    print("\n✓ Download complete!")
    print(f"\nData directory: {DATA_DIR}")

if __name__ == "__main__":
    main()


