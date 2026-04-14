import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    GlobalAveragePooling2D, Dense, Dropout, BatchNormalization
)
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────
DATASET_PATH = "dataset"
IMG_SIZE     = 224
BATCH_SIZE   = 16        # Smaller batch = better generalization
EPOCHS       = 40
MODEL_OUTPUT = "keras_model.h5"

print("=" * 55)
print("  SMART INSECT — FINAL IMPROVED TRAINING")
print("=" * 55)

# ─────────────────────────────────────────
# STEP 1: Load Images
# ─────────────────────────────────────────
print("\n📂 Loading images...")

train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
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
    rescale=1.0 / 255,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='training',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='validation',
    shuffle=False
)

print(f"\n✅ Classes          : {train_generator.class_indices}")
print(f"✅ Training images   : {train_generator.samples}")
print(f"✅ Validation images : {val_generator.samples}")

# ─────────────────────────────────────────
# STEP 2: Build Model — MobileNetV2
# ─────────────────────────────────────────
print("\n🧠 Building model...")

base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

x      = base_model.output
x      = GlobalAveragePooling2D()(x)
x      = BatchNormalization()(x)
x      = Dense(256, activation='relu')(x)
x      = Dropout(0.6)(x)               # Higher dropout = less overfitting
x      = Dense(128, activation='relu')(x)
x      = Dropout(0.4)(x)
output = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

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
# STEP 4: Phase 1 — Train Top Layers Only
# ─────────────────────────────────────────
print("\n🚀 Phase 1: Training top layers (8 epochs)...")

history1 = model.fit(
    train_generator,
    epochs=8,
    validation_data=val_generator,
    callbacks=[checkpoint, reduce_lr],
    verbose=1
)

# ─────────────────────────────────────────
# STEP 5: Phase 2 — Fine Tune Deeper Layers
# ─────────────────────────────────────────
print("\n🔓 Phase 2: Fine-tuning last 80 layers...")

base_model.trainable = True
for layer in base_model.layers[:-80]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.00005),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=[checkpoint, early_stop, reduce_lr],
    verbose=1
)

# ─────────────────────────────────────────
# STEP 6: Results
# ─────────────────────────────────────────
all_train_acc = history1.history['accuracy'] + history2.history['accuracy']
all_val_acc   = history1.history['val_accuracy'] + history2.history['val_accuracy']
all_train_loss = history1.history['loss'] + history2.history['loss']
all_val_loss   = history1.history['val_loss'] + history2.history['val_loss']

best_val   = max(all_val_acc)
best_train = max(all_train_acc)

print("\n" + "=" * 55)
print("  TRAINING COMPLETE!")
print("=" * 55)
print(f"  Best Training Accuracy   : {round(best_train * 100, 2)}%")
print(f"  Best Validation Accuracy : {round(best_val * 100, 2)}%")
print(f"  Model saved to           : {MODEL_OUTPUT}")

if best_val >= 0.85:
    print("\n  🎉 EXCELLENT! Model is ready for deployment.")
elif best_val >= 0.78:
    print("\n  ✅ GOOD! Model is acceptable for deployment.")
else:
    print("\n  ⚠️  Accuracy still low. Share results for further help.")

print("=" * 55)

# ─────────────────────────────────────────
# STEP 7: Save Graph
# ─────────────────────────────────────────
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(all_train_acc, label='Train Accuracy')
plt.plot(all_val_acc,   label='Val Accuracy')
plt.axvline(x=7, color='gray', linestyle='--', label='Fine-tune start')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(all_train_loss, label='Train Loss')
plt.plot(all_val_loss,   label='Val Loss')
plt.axvline(x=7, color='gray', linestyle='--', label='Fine-tune start')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.savefig("training_result.png")
print("\n📊 Graph saved as: training_result.png")
print("✅ Done! keras_model.h5 is ready.")