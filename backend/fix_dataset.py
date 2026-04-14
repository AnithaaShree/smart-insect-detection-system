import os
import shutil

dataset_path = "dataset"

print("=" * 55)
print("FIXING DATASET STRUCTURE...")
print("=" * 55)

moved = 0

for category in ["Harmful", "Beneficial"]:
    category_path = os.path.join(dataset_path, category)

    if not os.path.exists(category_path):
        print(f"❌ Folder not found: {category_path}")
        continue

    print(f"\n📁 Processing: {category}/")

    for insect_folder in os.listdir(category_path):
        insect_path = os.path.join(category_path, insect_folder)

        # Only process subfolders (insect name folders)
        if not os.path.isdir(insect_path):
            continue

        print(f"   Moving images from: {insect_folder}/")

        for img_file in os.listdir(insect_path):
            if not img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue

            src  = os.path.join(insect_path, img_file)

            # Rename to avoid conflicts between insect folders
            new_name = insect_folder.replace(" ", "_") + "_" + img_file
            dest = os.path.join(category_path, new_name)

            # If file with same name exists, add a number
            counter = 1
            while os.path.exists(dest):
                name_part, ext = os.path.splitext(new_name)
                dest = os.path.join(category_path, f"{name_part}_{counter}{ext}")
                counter += 1

            shutil.move(src, dest)
            moved += 1

        # Remove now-empty insect subfolder
        try:
            os.rmdir(insect_path)
            print(f"   ✅ Done — subfolder removed")
        except:
            print(f"   ⚠️  Could not remove folder (may not be empty)")

print("\n" + "=" * 55)
print(f"✅ Total images moved: {moved}")
print("=" * 55)
print("\nNew structure:")

for category in ["Harmful", "Beneficial"]:
    category_path = os.path.join(dataset_path, category)
    if os.path.exists(category_path):
        count = len([
            f for f in os.listdir(category_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ])
        print(f"  📁 {category}/  →  {count} images")

print("\n✅ Now run: python train_model.py")