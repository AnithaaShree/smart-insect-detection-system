from bing_image_downloader import downloader
import os
import time

def download_insect(name, category, limit=100):
    folder_path = os.path.join("dataset", category, name)

    # Count existing images
    if os.path.exists(folder_path):
        existing = len([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ])
        if existing >= 50:
            print(f"✅ Skipping '{name}' — already has {existing} images")
            return
        else:
            print(f"⚠️  '{name}' only has {existing} images — downloading more...")
    else:
        print(f"📥 Starting download for '{name}'...")

    # Try downloading with retry
    for attempt in range(1, 4):
        try:
            downloader.download(
                name,
                limit=limit,
                output_dir=f'dataset/{category}',
                adult_filter_off=True,
                force_replace=False,
                timeout=10
            )
            print(f"✅ Done: '{name}'")
            time.sleep(3)  # Small pause between downloads
            break
        except Exception as e:
            print(f"❌ Attempt {attempt} failed for '{name}': {e}")
            print(f"   Waiting 10 seconds before retry...")
            time.sleep(10)

# ──────────────────────────────────────
# HARMFUL INSECTS
# ──────────────────────────────────────
print("\n🔴 Downloading HARMFUL insects...\n")
download_insect("Aphid insect",        "Harmful")
download_insect("Whitefly insect",     "Harmful")
download_insect("Caterpillar insect",  "Harmful")
download_insect("Mealybug insect",     "Harmful")
download_insect("Thrips insect",       "Harmful")

# ──────────────────────────────────────
# BENEFICIAL INSECTS
# ──────────────────────────────────────
print("\n🟢 Downloading BENEFICIAL insects...\n")
download_insect("Ladybug insect",       "Beneficial")
download_insect("Honeybee insect",      "Beneficial")
download_insect("Dragonfly insect",     "Beneficial")
download_insect("Lacewing insect",      "Beneficial")
download_insect("Ground Beetle insect", "Beneficial")

print("\n✅ ALL DOWNLOADS COMPLETE!")
print("Now run: python check_images.py")