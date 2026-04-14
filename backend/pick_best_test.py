import os
import shutil
import cv2
import numpy as np
import tensorflow as tf

print("=" * 55)
print("  FINDING BEST TEST IMAGES FROM DATASET")
print("=" * 55)

# Load model
model = tf.keras.models.load_model("keras_model.h5")

def get_confidence(img_path, expected_class):
    img = cv2.imread(img_path)
    if img is None:
        return 0
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.reshape(img, (1, 224, 224, 3))
    pred = float(model.predict(img, verbose=0)[0][0])

    # Beneficial = pred < 0.5, Harmful = pred > 0.5
    if expected_class == "Harmful":
        return pred          # Higher = more confident it is Harmful
    else:
        return 1 - pred      # Higher = more confident it is Beneficial

best_harmful    = {"path": None, "score": 0}
best_beneficial = {"path": None, "score": 0}

# Search Harmful folder
harmful_path = os.path.join("dataset", "Harmful")
print("\n🔍 Scanning Harmful images...")
files = [f for f in os.listdir(harmful_path)
         if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))][:50]

for i, f in enumerate(files):
    full_path = os.path.join(harmful_path, f)
    score = get_confidence(full_path, "Harmful")
    if score > best_harmful["score"]:
        best_harmful = {"path": full_path, "score": score}
    if i % 10 == 0:
        print(f"  Checked {i+1}/{len(files)} images...")

# Search Beneficial folder
beneficial_path = os.path.join("dataset", "Beneficial")
print("\n🔍 Scanning Beneficial images...")
files = [f for f in os.listdir(beneficial_path)
         if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))][:50]

for i, f in enumerate(files):
    full_path = os.path.join(beneficial_path, f)
    score = get_confidence(full_path, "Beneficial")
    if score > best_beneficial["score"]:
        best_beneficial = {"path": full_path, "score": score}
    if i % 10 == 0:
        print(f"  Checked {i+1}/{len(files)} images...")

# Copy best images as test images
if best_harmful["path"]:
    shutil.copy2(best_harmful["path"], "test_harmful.jpg")
    print(f"\n✅ Best Harmful image    : {best_harmful['path']}")
    print(f"   Confidence Score     : {round(best_harmful['score'] * 100, 2)}%")

if best_beneficial["path"]:
    shutil.copy2(best_beneficial["path"], "test_beneficial.jpg")
    print(f"\n✅ Best Beneficial image : {best_beneficial['path']}")
    print(f"   Confidence Score     : {round(best_beneficial['score'] * 100, 2)}%")

print("\n✅ Best test images saved!")
print("Now run: python test_server.py")