#!/usr/bin/env python3
"""
Curate 200 images with people for Vercel deployment
Prioritizes images that have detected people in metadata
"""
import json
import sqlite3
from pathlib import Path
import shutil
import random

DATA_DIR = Path("data")
EXTRACTED_DIR = DATA_DIR / "extracted"
PUBLIC_DIR = Path("public/curated/images")
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

# Try to find images with people from database
images_with_people = []
all_images = []

db_path = DATA_DIR / "epsteinbase.db"
if db_path.exists():
    print("📊 Checking database for images with people...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get images with detected_people in metadata
    cursor.execute("""
        SELECT file_path, metadata 
        FROM documents 
        WHERE type='image' 
        AND (metadata LIKE '%detected_people%' OR metadata LIKE '%people%')
        LIMIT 500
    """)
    
    for row in cursor.fetchall():
        file_path, metadata = row
        try:
            if isinstance(metadata, str):
                meta = json.loads(metadata)
            else:
                meta = metadata
            
            detected_people = meta.get('detected_people', [])
            if detected_people and len(detected_people) > 0:
                full_path = DATA_DIR / file_path
                if full_path.exists():
                    images_with_people.append(full_path)
        except:
            pass
    
    conn.close()
    print(f"✅ Found {len(images_with_people)} images with detected people in database")

# Also scan filesystem for images
print("🔍 Scanning filesystem for images...")
all_image_files = list(EXTRACTED_DIR.glob("**/*.png")) + \
                  list(EXTRACTED_DIR.glob("**/*.jpg")) + \
                  list(EXTRACTED_DIR.glob("**/*.jpeg"))

print(f"📸 Found {len(all_image_files)} total images")

# Prioritize images with people, fill rest with random
selected = set()

# Add images with people first (up to 200)
for img_path in images_with_people[:200]:
    if len(selected) >= 200:
        break
    selected.add(img_path)

# Fill remaining slots with random images (avoiding flight/contact folders)
remaining = 200 - len(selected)
random.shuffle(all_image_files)
for img_path in all_image_files:
    if len(selected) >= 200:
        break
    # Skip flight logs and contact books
    if "flight" in str(img_path).lower() or "contact" in str(img_path).lower():
        continue
    if img_path not in selected:
        selected.add(img_path)

print(f"🎯 Selected {len(selected)} images to copy")

# Copy images to public folder
copied = 0
for img_path in list(selected)[:200]:
    try:
        # Create a unique filename
        rel_path = img_path.relative_to(EXTRACTED_DIR)
        dest = PUBLIC_DIR / rel_path.name
        
        # If filename exists, add parent folder name
        if dest.exists():
            dest = PUBLIC_DIR / f"{rel_path.parent.name}_{rel_path.name}"
        
        shutil.copy2(img_path, dest)
        copied += 1
        if copied % 50 == 0:
            print(f"  Copied {copied}/200...")
    except Exception as e:
        print(f"  Error copying {img_path}: {e}")

print(f"✅ Copied {copied} images to public/curated/images/")


