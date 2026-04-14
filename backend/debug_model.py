import tensorflow as tf
import numpy as np
import json
import cv2
import os

print("Loading model...")
model = tf.keras.models.load_model("keras_model.h5")
print(f"Model output shape: {model.output_shape}")
print(f"Number of output classes: {model.output_shape[-1]}")

with open("class_labels.json") as f:
    labels = json.load(f)
print(f"\nClass labels: {labels}")
print(f"Number of labels: {len(labels)}")

# Test with a real image
test_images = [
    "test_harmful.jpg",
    "test_beneficial.jpg"
]

for img_path in test_images:
    if not os.path.exists(img_path):
        continue
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224, 224)) / 255.0
    img = np.reshape(img, (1, 224, 224, 3))

    pred     = model.predict(img, verbose=0)[0]
    top_idx  = int(np.argmax(pred))
    top_conf = float(pred[top_idx])
    top_name = labels.get(str(top_idx), "Unknown")

    print(f"\nImage: {img_path}")
    print(f"  Predicted class : {top_name}")
    print(f"  Confidence      : {round(top_conf*100,2)}%")
    print(f"  All predictions :")
    for i, p in enumerate(pred):
        name = labels.get(str(i), f"class_{i}")
        print(f"    {i}: {name:20} {round(p*100,2)}%")

print("\nDone!")