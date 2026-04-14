import os
import shutil

print("=" * 55)
print("REORGANIZING DATASET FOR MULTI-CLASS TRAINING")
print("=" * 55)

# Map insect names to their search terms used during download
insect_map = {
    "Harmful": {
        "Aphid"      : ["Aphid_insect", "Aphid_bug_on_leaf"],
        "Whitefly"   : ["Whitefly_insect", "Whitefly_pest_crop"],
        "Caterpillar": ["Caterpillar_insect", "Caterpillar_eating_plant"],
        "Mealybug"   : ["Mealybug_insect", "Mealybug_on_plant_stem"],
        "Thrips"     : ["Thrips_insect", "Thrips_damage_on_leaves"]
    },
    "Beneficial": {
        "Ladybug"      : ["Ladybug_insect", "Ladybug_on_flower"],
        "Honeybee"     : ["Honeybee_insect", "Honeybee_collecting_pollen"],
        "Dragonfly"    : ["Dragonfly_insect", "Dragonfly_resting"],
        "Lacewing"     : ["Lacewing_insect", "Lacewing_on_leaf"],
        "Ground_Beetle": ["Ground_Beetle_insect", "Ground_Beetle_on_soil"]
    }
}

source_base = "dataset"
dest_base   = "dataset_multiclass"
os.makedirs(dest_base, exist_ok=True)

moved = 0
skipped = 0

for category, insects in insect_map.items():
    category_path = os.path.join(source_base, category)

    for insect_name, search_terms in insects.items():
        dest_folder = os.path.join(dest_base, insect_name)
        os.makedirs(dest_folder, exist_ok=True)

        # Find images matching this insect's search terms
        for fname in os.listdir(category_path):
            if not fname.lower().endswith(('.jpg','.jpeg','.png','.webp')):
                continue

            # Check if filename contains any of the search terms
            fname_lower = fname.lower()
            matched = any(
                term.lower().replace("_", "").replace(" ", "")
                in fname_lower.replace("_", "").replace(" ", "")
                for term in search_terms
            )

            if matched:
                src  = os.path.join(category_path, fname)
                dest = os.path.join(dest_folder, fname)
                if not os.path.exists(dest):
                    shutil.copy2(src, dest)
                    moved += 1

        count = len(os.listdir(dest_folder))
        print(f"  {insect_name:15} → {count} images")

print(f"\n✅ Done! Moved {moved} images")
print("\nChecking counts:")
for folder in sorted(os.listdir(dest_base)):
    path  = os.path.join(dest_base, folder)
    count = len([f for f in os.listdir(path)
                 if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))])
    status = "✅" if count >= 30 else "⚠️  Need more images"
    print(f"  {status}  {folder}: {count} images")