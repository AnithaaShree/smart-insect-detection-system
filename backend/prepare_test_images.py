import os
import shutil

print("=" * 55)
print("  PREPARING TEST IMAGES FROM YOUR DATASET")
print("=" * 55)

def get_first_image(category):
    cat_path = os.path.join("dataset", category)
    if not os.path.exists(cat_path):
        print(f"❌ Folder not found: {cat_path}")
        return None
    for f in os.listdir(cat_path):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            return os.path.join(cat_path, f)
    return None

# Get one harmful image
harmful_src = get_first_image("Harmful")
if harmful_src:
    shutil.copy2(harmful_src, "test_harmful.jpg")
    print(f"✅ Copied Harmful test image  : {harmful_src}")
else:
    print("❌ No harmful image found!")

# Get one beneficial image
beneficial_src = get_first_image("Beneficial")
if beneficial_src:
    shutil.copy2(beneficial_src, "test_beneficial.jpg")
    print(f"✅ Copied Beneficial test image: {beneficial_src}")
else:
    print("❌ No beneficial image found!")

print("\n✅ Test images ready!")
print("Now run: python test_server.py")