import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    GlobalAveragePooling2D, Dense, Dropout, BatchNormalization
)
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
)
import json
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
DATASET_PATH = "dataset_multiclass"
IMG_SIZE     = 224
BATCH_SIZE   = 16
EPOCHS       = 40
MODEL_OUTPUT = "keras_model.h5"
LABELS_FILE  = "class_labels.json"
# ─────────────────────────────────────────

print("=" * 55)
print("  MULTI-CLASS INSECT TRAINING (10 classes)")
print("=" * 55)

# Check dataset
print("\n📂 Dataset check:")
classes = sorted(os.listdir(DATASET_PATH))
for c in classes:
    path  = os.path.join(DATASET_PATH, c)
    count = len([f for f in os.listdir(path)
                 if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))])
    print(f"   {c}: {count} images")

# ─────────────────────────────────────────
# STEP 1: Load images
# ─────────────────────────────────────────
print("\n📂 Loading images...")

train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=40,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.35,
    horizontal_flip=True,
    vertical_flip=True,
    brightness_range=[0.6, 1.4],
    channel_shift_range=30.0,
    fill_mode='nearest',
    validation_split=0.2
)

val_datagen = ImageDataGenerator(
    rescale=1.0/255,
    validation_split=0.2
)

train_gen = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_gen = val_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

num_classes = len(train_gen.class_indices)
print(f"\n✅ Classes found  : {train_gen.class_indices}")
print(f"✅ Training images : {train_gen.samples}")
print(f"✅ Val images      : {val_gen.samples}")
print(f"✅ Num classes     : {num_classes}")

# Save class labels
labels_map = {v: k for k, v in train_gen.class_indices.items()}
with open(LABELS_FILE, 'w') as f:
    json.dump(labels_map, f, indent=2)
print(f"✅ Labels saved to : {LABELS_FILE}")

# ─────────────────────────────────────────
# STEP 2: Build model
# ─────────────────────────────────────────
print("\n🧠 Building multi-class model...")

base = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base.trainable = False

x      = base.output
x      = GlobalAveragePooling2D()(x)
x      = BatchNormalization()(x)
x      = Dense(512, activation='relu')(x)
x      = Dropout(0.5)(x)
x      = Dense(256, activation='relu')(x)
x      = Dropout(0.3)(x)
output = Dense(num_classes, activation='softmax')(x)  # softmax for multi-class

model = Model(inputs=base.input, outputs=output)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"✅ Model ready — {num_classes} output classes")

# ─────────────────────────────────────────
# STEP 3: Callbacks
# ─────────────────────────────────────────
checkpoint = ModelCheckpoint(
    MODEL_OUTPUT,
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

early_stop = EarlyStopping(
    monitor='val_accuracy',
    patience=8,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=4,
    min_lr=1e-8,
    verbose=1
)

# ─────────────────────────────────────────
# STEP 4: Phase 1 — Train top layers only
# ─────────────────────────────────────────
print("\n🚀 Phase 1: Training top layers (8 epochs)...")

history1 = model.fit(
    train_gen,
    epochs=8,
    validation_data=val_gen,
    callbacks=[checkpoint, reduce_lr],
    verbose=1
)

# ─────────────────────────────────────────
# STEP 5: Phase 2 — Fine tune
# ─────────────────────────────────────────
print("\n🔓 Phase 2: Fine-tuning last 80 layers...")

base.trainable = True
for layer in base.layers[:-80]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.00005),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    train_gen,
    epochs=EPOCHS,
    validation_data=val_gen,
    callbacks=[checkpoint, early_stop, reduce_lr],
    verbose=1
)

# ─────────────────────────────────────────
# STEP 6: Results
# ─────────────────────────────────────────
all_acc     = history1.history['accuracy']     + history2.history['accuracy']
all_val_acc = history1.history['val_accuracy'] + history2.history['val_accuracy']
all_loss    = history1.history['loss']         + history2.history['loss']
all_val_loss= history1.history['val_loss']     + history2.history['val_loss']

best_val   = max(all_val_acc)
best_train = max(all_acc)

print("\n" + "=" * 55)
print("  TRAINING COMPLETE!")
print("=" * 55)
print(f"  Classes          : {num_classes}")
print(f"  Best Train Acc   : {round(best_train*100,2)}%")
print(f"  Best Val Acc     : {round(best_val*100,2)}%")
print(f"  Model saved      : {MODEL_OUTPUT}")
print(f"  Labels saved     : {LABELS_FILE}")

if best_val >= 0.80:
    print("\n  🎉 EXCELLENT! Ready for deployment.")
elif best_val >= 0.70:
    print("\n  ✅ GOOD! Acceptable accuracy.")
else:
    print("\n  ⚠️  Low accuracy. Share results for help.")
print("=" * 55)

# ─────────────────────────────────────────
# STEP 7: Save graph
# ─────────────────────────────────────────
plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(all_acc,     label='Train')
plt.plot(all_val_acc, label='Val')
plt.axvline(x=7, color='gray', linestyle='--', label='Fine-tune')
plt.title('Accuracy')
plt.xlabel('Epoch')
plt.legend()

plt.subplot(1,2,2)
plt.plot(all_loss,     label='Train')
plt.plot(all_val_loss, label='Val')
plt.axvline(x=7, color='gray', linestyle='--', label='Fine-tune')
plt.title('Loss')
plt.xlabel('Epoch')
plt.legend()

plt.tight_layout()
plt.savefig("training_result_multiclass.png")
print("\n📊 Graph saved: training_result_multiclass.png")
print("✅ All done!")