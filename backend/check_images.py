import os

dataset_path = "dataset"

print("=" * 50)
print("IMAGE COUNT REPORT")
print("=" * 50)

total = 0

for category in ["Harmful", "Beneficial"]:
    category_path = os.path.join(dataset_path, category)
    print(f"\n📁 {category}/")

    if not os.path.exists(category_path):
        print("   ❌ Folder does not exist yet!")
        continue

    for insect_folder in sorted(os.listdir(category_path)):
        insect_path = os.path.join(category_path, insect_folder)
        if os.path.isdir(insect_path):
            count = len([
                f for f in os.listdir(insect_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            ])
            status = "✅" if count >= 50 else "⚠️ Need more"
            print(f"   {status}  {insect_folder}: {count} images")
            total += count

print("\n" + "=" * 50)
print(f"TOTAL IMAGES: {total}")
print("=" * 50)