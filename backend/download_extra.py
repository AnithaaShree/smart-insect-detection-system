from bing_image_downloader import downloader
import os
import time

def download_extra(name, category, limit=60):
    folder_path = os.path.join("dataset", category)
    os.makedirs(folder_path, exist_ok=True)

    print(f"📥 Downloading extra: '{name}' → {category}/")
    for attempt in range(1, 4):
        try:
            downloader.download(
                name,
                limit=limit,
                output_dir=f'dataset_extra/{category}',
                adult_filter_off=True,
                force_replace=False,
                timeout=10
            )
            print(f"✅ Done: '{name}'")
            time.sleep(3)
            break
        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {e}")
            time.sleep(10)

# ── HARMFUL — different search terms for variety ──
print("\n🔴 Extra HARMFUL images...\n")
download_extra("Aphid bug on leaf",           "Harmful")
download_extra("Whitefly pest crop",          "Harmful")
download_extra("Caterpillar eating plant",    "Harmful")
download_extra("Mealybug on plant stem",      "Harmful")
download_extra("Thrips damage on leaves",     "Harmful")

# ── BENEFICIAL — different search terms for variety ──
print("\n🟢 Extra BENEFICIAL images...\n")
download_extra("Ladybug on flower",           "Beneficial")
download_extra("Honeybee collecting pollen",  "Beneficial")
download_extra("Dragonfly resting",           "Beneficial")
download_extra("Lacewing on leaf",            "Beneficial")
download_extra("Ground Beetle on soil",       "Beneficial")

print("\n✅ Extra downloads complete!")