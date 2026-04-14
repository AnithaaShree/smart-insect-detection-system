import os
import cv2

dataset_path = "dataset"
removed = 0
kept = 0

print("=" * 50)
print("CLEANING BROKEN IMAGES...")
print("=" * 50)

for category in os.listdir(dataset_path):
    category_path = os.path.join(dataset_path, category)
    if not os.path.isdir(category_path):
        continue

    for insect_folder in os.listdir(category_path):
        insect_path = os.path.join(category_path, insect_folder)
        if not os.path.isdir(insect_path):
            continue

        for img_file in os.listdir(insect_path):
            img_path = os.path.join(insect_path, img_file)
            try:
                img = cv2.imread(img_path)
                if img is None:
                    os.remove(img_path)
                    print(f"❌ Removed: {img_path}")
                    removed += 1
                else:
                    kept += 1
            except Exception as e:
                os.remove(img_path)
                print(f"❌ Removed (error): {img_path}")
                removed += 1

print("\n" + "=" * 50)
print(f"✅ Kept   : {kept} good images")
print(f"🗑️  Removed: {removed} broken images")
print("=" * 50)
print("\nNow run: python train_model.py")