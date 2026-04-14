import os
import shutil

source_base = "dataset_extra"
dest_base   = "dataset"

print("=" * 55)
print("MERGING EXTRA IMAGES INTO MAIN DATASET...")
print("=" * 55)

moved = 0

for category in ["Harmful", "Beneficial"]:
    source_cat = os.path.join(source_base, category)
    dest_cat   = os.path.join(dest_base,   category)

    if not os.path.exists(source_cat):
        print(f"⚠️  Skipping {category} — extra folder not found")
        continue

    print(f"\n📁 Merging: {category}/")

    for item in os.listdir(source_cat):
        item_path = os.path.join(source_cat, item)

        # If it is a subfolder (insect name folder), go inside it
        if os.path.isdir(item_path):
            for img_file in os.listdir(item_path):
                if not img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    continue
                src  = os.path.join(item_path, img_file)
                new_name = item.replace(" ", "_") + "_extra_" + img_file
                dest = os.path.join(dest_cat, new_name)

                counter = 1
                while os.path.exists(dest):
                    name_part, ext = os.path.splitext(new_name)
                    dest = os.path.join(dest_cat, f"{name_part}_{counter}{ext}")
                    counter += 1

                shutil.copy2(src, dest)
                moved += 1

        # If it is directly an image file
        elif item.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            src  = os.path.join(source_cat, item)
            dest = os.path.join(dest_cat, "extra_" + item)

            counter = 1
            while os.path.exists(dest):
                name_part, ext = os.path.splitext(item)
                dest = os.path.join(dest_cat, f"extra_{name_part}_{counter}{ext}")
                counter += 1

            shutil.copy2(src, dest)
            moved += 1

print("\n" + "=" * 55)
print(f"✅ Total images merged: {moved}")
print("=" * 55)

# Show final count
print("\nFinal dataset count:")
for category in ["Harmful", "Beneficial"]:
    cat_path = os.path.join(dest_base, category)
    if os.path.exists(cat_path):
        count = len([
            f for f in os.listdir(cat_path)
            if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))
        ])
        print(f"  📁 {category}/ → {count} images")

print("\n✅ Now run: python clean_images.py")