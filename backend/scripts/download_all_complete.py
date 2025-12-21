#!/usr/bin/env python3
"""Download ALL Epstein files including December 2025 release"""
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"

# All video URLs from DOJ
ALL_VIDEOS = [
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video1.mp4",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video2.mp4",
]

# All audio URLs - Maxwell Proffer sessions (December 2025 release)
ALL_AUDIO = [
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%201%20-%207_24_25_Tallahassee.003.wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%202%20-%207_24_25_Tallahassee.004.wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%203%20-%207_24_25_Tallahassee.005%20(R).wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%204%20-%207_24_25_Tallahassee.007.wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%205%20-%207_24_25_Tallahassee.008%20(R).wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%206%20-%207_24_25_Tallahassee.009%20(R).wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%207%20-%207_24_25_Tallahassee.010.wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%201%20-%202025.07.25%20-%20xxx7_25.003%20(R).wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%202%20-%202025.07.25%20-%20xxx7_25.004%20(R).wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%203%20-%202025.07.25%20-%20xxx7_25.005.wav",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%202%20-%20Part%204%20-%202025.07.25%20-%20xxx7_25.006%20(R).wav",
]

# Additional PDFs from December 2025 release
ADDITIONAL_PDFS = [
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/First%20Phase%20of%20Declassified%20Epstein%20Files/B.%20Flight%20Log%20Released%20in%20US%20v.%20Maxwell,%201.20-cr-00330%20(SDNY%202020).pdf",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/First%20Phase%20of%20Declassified%20Epstein%20Files/C.%20Contact%20Book%20(Redacted).pdf",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/First%20Phase%20of%20Declassified%20Epstein%20Files/D.%20Masseuse%20List%20(Redacted).pdf",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Interview%20Transcript%20-%20Maxwell%202025.07.24%20(Redacted).pdf",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Interview%20Transcript%20-%20Maxwell%202025.07.25%20(Redacted).pdf",
    "https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/2025.07%20DOJ%20FBI%20Memorandum.pdf",
]

# Main combined PDF from Internet Archive
MAIN_PDF = "https://archive.org/download/combined-all-epstein-files/COMBINED_ALL_EPSTEIN_FILES.pdf"

def download_file(url: str, dest: Path, label: str = ""):
    """Download file with progress"""
    if dest.exists():
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"  ✓ {dest.name} ({size_mb:.1f}MB) - already exists")
        return True
    
    print(f"  ↓ Downloading {dest.name} {label}...")
    try:
        # Use curl with progress bar
        result = subprocess.run(
            ["curl", "-L", "-o", str(dest), "--progress-bar", url],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and dest.exists():
            size_mb = dest.stat().st_size / (1024 * 1024)
            print(f"  ✓ Downloaded {dest.name} ({size_mb:.1f}MB)")
            return True
        else:
            print(f"  ✗ Failed to download {dest.name}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    # Create directories
    (DATA_DIR / "pdfs").mkdir(exist_ok=True, parents=True)
    (DATA_DIR / "videos").mkdir(exist_ok=True, parents=True)
    (DATA_DIR / "audio").mkdir(exist_ok=True, parents=True)
    
    print("=" * 60)
    print("EPSTEIN FILES COMPLETE DOWNLOAD")
    print("December 2025 DOJ Release")
    print("=" * 60)
    
    # Download videos
    print("\n[1/3] DOWNLOADING VIDEOS...")
    video_dir = DATA_DIR / "videos"
    for i, url in enumerate(ALL_VIDEOS, 1):
        filename = url.split("/")[-1].replace("%20", "_")
        dest = video_dir / filename
        download_file(url, dest, f"({i}/{len(ALL_VIDEOS)})")
    
    # Download audio
    print(f"\n[2/3] DOWNLOADING AUDIO FILES ({len(ALL_AUDIO)} files)...")
    audio_dir = DATA_DIR / "audio"
    for i, url in enumerate(ALL_AUDIO, 1):
        filename = url.split("/")[-1].replace("%20", "_")
        dest = audio_dir / filename
        download_file(url, dest, f"({i}/{len(ALL_AUDIO)})")
    
    # Download additional PDFs
    print(f"\n[3/3] DOWNLOADING ADDITIONAL PDFs ({len(ADDITIONAL_PDFS)} files)...")
    pdf_dir = DATA_DIR / "pdfs"
    for i, url in enumerate(ADDITIONAL_PDFS, 1):
        filename = url.split("/")[-1].replace("%20", "_").replace("%2C", ",")
        dest = pdf_dir / filename
        download_file(url, dest, f"({i}/{len(ADDITIONAL_PDFS)})")
    
    # Main combined PDF (if not exists)
    print(f"\nChecking main combined PDF...")
    main_pdf_path = pdf_dir / "COMBINED_ALL_EPSTEIN_FILES.pdf"
    if not main_pdf_path.exists():
        download_file(MAIN_PDF, main_pdf_path, "(Main Archive)")
    else:
        size_gb = main_pdf_path.stat().st_size / (1024 * 1024 * 1024)
        print(f"  ✓ Already exists ({size_gb:.1f}GB)")
    
    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    
    video_count = len(list((DATA_DIR / "videos").glob("*.mp4")))
    audio_count = len(list((DATA_DIR / "audio").glob("*.wav")))
    pdf_count = len(list((DATA_DIR / "pdfs").glob("*.pdf")))
    
    total_video_size = sum(f.stat().st_size for f in (DATA_DIR / "videos").glob("*.mp4")) / (1024**3)
    total_audio_size = sum(f.stat().st_size for f in (DATA_DIR / "audio").glob("*.wav")) / (1024**3)
    total_pdf_size = sum(f.stat().st_size for f in (DATA_DIR / "pdfs").glob("*.pdf")) / (1024**3)
    
    print(f"\nVideos: {video_count} files ({total_video_size:.1f}GB)")
    print(f"Audio: {audio_count} files ({total_audio_size:.1f}GB)")
    print(f"PDFs: {pdf_count} files ({total_pdf_size:.1f}GB)")
    print(f"\nTotal: {total_video_size + total_audio_size + total_pdf_size:.1f}GB")
    print(f"\nData directory: {DATA_DIR}")

if __name__ == "__main__":
    main()


