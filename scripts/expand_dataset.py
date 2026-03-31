import os
import shutil
import hashlib
from PIL import Image

# Configuration
CANONICAL_DIR = "data/cattle"
STAGING_DIRS = ["data/staging", "data/staging2"]
# Weak classes we want to expand and their canonical names
WEAK_CLASSES = [
    "Krishna_Valley", "gangatari", "dagri", "Sahiwal",
    "Shweta Kapila", "Hariana", "Amritmahal", "Khillari", "Rathi"
]

# We will limit additions to hit around ~400 max, but Sahiwal is already at 421. 
# We'll set a soft cap at 450 to prevent it blowing up.
MAX_IMAGES_PER_CLASS = 450

# Map common variations to canonical name
NAME_MAPPINGS = {
    # Lowercase and stripped of spaces/underscores mapping
    "krishnavalley": "Krishna_Valley",
    "krishnvalley": "Krishna_Valley",
    "gangatari": "gangatari",
    "gangatiri": "gangatari",
    "dagri": "dagri",
    "sahiwal": "Sahiwal",
    "shwetakapila": "Shweta Kapila",
    "hariana": "Hariana",
    "haryana": "Hariana",
    "amritmahal": "Amritmahal",
    "amrutmahal": "Amritmahal",
    "khillari": "Khillari",
    "khilari": "Khillari",
    "rathi": "Rathi",
}

def normalize_name(name):
    # lower case, remove spaces, remove underscores
    return name.lower().replace(" ", "").replace("_", "")

def get_canonical_name(name):
    norm = normalize_name(name)
    if norm in NAME_MAPPINGS:
        return NAME_MAPPINGS[norm]
    # Check if a canonical name starts with norm and it's long enough
    for k, v in NAME_MAPPINGS.items():
        if norm == k:
            return v
    return None

def file_hash(filepath):
    # compute md5 hash
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        # read in chunks
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def is_valid_image(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()
        # Verify doesn't catch all broken images. Try loading the image.
        with Image.open(filepath) as img:
            img.load()
        return True
    except Exception:
        return False

print("Computing existing hashes...")
# 1. Pre-compute hashes of existing files in the canonical dirs for the weak classes
existing_hashes = set()
for wc in os.listdir(CANONICAL_DIR):
    # we can hash ALL classes to make sure we don't duplicate a Sahiwal image into Hariana, etc.
    wc_dir = os.path.join(CANONICAL_DIR, wc)
    if os.path.isdir(wc_dir):
        for f in os.listdir(wc_dir):
            fp = os.path.join(wc_dir, f)
            if os.path.isfile(fp):
                existing_hashes.add(file_hash(fp))

print(f"Computed {len(existing_hashes)} hashes for existing images.")

images_added = {wc: 0 for wc in WEAK_CLASSES}

# 2. Iterate through staging directories
print("Scanning staging datasets...")
for staging_dir in STAGING_DIRS:
    if not os.path.exists(staging_dir):
        print(f"Staging directory not found: {staging_dir}")
        continue
    for root, dirs, files in os.walk(staging_dir):
        folder_name = os.path.basename(root)
        cname = get_canonical_name(folder_name)
        if cname in WEAK_CLASSES:
            print(f"Found source class: '{folder_name}' matching canonical '{cname}' with {len(files)} files.")
            cname_dir = os.path.join(CANONICAL_DIR, cname)
            os.makedirs(cname_dir, exist_ok=True)
            current_count = len([f for f in os.listdir(cname_dir) if os.path.isfile(os.path.join(cname_dir, f))])
            
            for file in files:
                if current_count >= MAX_IMAGES_PER_CLASS:
                    break
                
                src_path = os.path.join(root, file)
                
                # Only process potential image extensions
                if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    # Might not have an extension or it's another file type
                    pass
                
                # Check validity
                if not is_valid_image(src_path):
                    continue
                
                # Check hash
                h = file_hash(src_path)
                if h in existing_hashes:
                    continue
                
                # Find a unique filename
                ext = os.path.splitext(file)[1].lower()
                if ext == "":
                    ext = ".jpg"
                new_filename = f"augmented_{h[:8]}{ext}"
                dst_path = os.path.join(cname_dir, new_filename)
                
                # Copy
                shutil.copy2(src_path, dst_path)
                existing_hashes.add(h)
                images_added[cname] += 1
                current_count += 1

print("\n--- Final Dataset Expansion Stats ---")
for wc in WEAK_CLASSES:
    cname_dir = os.path.join(CANONICAL_DIR, wc)
    if os.path.exists(cname_dir):
        final_count = len([f for f in os.listdir(cname_dir) if os.path.isfile(os.path.join(cname_dir, f))])
    else:
        final_count = 0
    added = images_added[wc]
    print(f"Class: {wc:<16} | Added: {added:<4} | Total Final Count: {final_count}")
