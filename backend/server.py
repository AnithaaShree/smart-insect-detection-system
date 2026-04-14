from flask import Flask, request, jsonify
import numpy as np
import cv2
import tensorflow as tf
import firebase_admin
from firebase_admin import credentials, db
import json
from datetime import datetime

# ── Firebase ──────────────────────────────────────────
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smartinsect-b6e1f-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# ── Load model ────────────────────────────────────────
print("Loading AI model...")
model = tf.keras.models.load_model("keras_model.h5")
print(f"Model output shape: {model.output_shape}")
print("Model loaded!")

# ── Class labels — must match your training folders ───
CLASS_LABELS = {
    0: "Aphid",
    1: "Caterpillar",
    2: "Dragonfly",
    3: "Ground_Beetle",
    4: "Honeybee",
    5: "Lacewing",
    6: "Ladybug",
    7: "Mealybug",
    8: "Thrips",
    9: "Whitefly"
}

# ── Load pesticide data ───────────────────────────────
with open("pesticide.json", encoding="utf-8") as f:
    pesticide_data = json.load(f)

app = Flask(__name__)

def safe(val):
    if val is None:
        return ""
    return str(val)

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    img  = cv2.imdecode(
        np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR
    )
    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    # Preprocess
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.reshape(img, (1, 224, 224, 3))

    # Predict — 10 class output
    predictions   = model.predict(img, verbose=0)[0]
    class_index   = int(np.argmax(predictions))
    confidence    = float(predictions[class_index])
    insect_name   = CLASS_LABELS.get(class_index, "Unknown")

    # Get insect data from pesticide.json
    insect_data   = pesticide_data.get(insect_name, {})
    insect_type   = insect_data.get("type", "Unknown")
    is_harmful    = insect_type == "Harmful"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build all predictions list for debugging
    all_preds = {
        CLASS_LABELS[i]: round(float(predictions[i]) * 100, 2)
        for i in range(len(predictions))
    }

    if is_harmful:
        response_data = {
            "insect_type"    : "Harmful",
            "insect_name"    : insect_name,
            "tamil_name"     : safe(insect_data.get("tamil_name")),
            "confidence"     : str(round(confidence * 100, 2)) + "%",
            "alert"          : True,
            "action_message" : safe(insect_data.get("action_message")),
            "crops_affected" : safe(insect_data.get("crops_affected")),
            "damage"         : safe(insect_data.get("damage")),
            "pesticide"      : safe(insect_data.get("pesticide")),
            "organic"        : safe(insect_data.get("organic")),
            "best_time"      : safe(insect_data.get("best_time")),
            "warning"        : safe(insect_data.get("warning")),
            "benefit"        : "",
            "crops_helped"   : "",
            "advice"         : "",
            "fun_fact"       : "",
            "timestamp"      : timestamp
        }
    else:
        response_data = {
            "insect_type"    : "Beneficial",
            "insect_name"    : insect_name,
            "tamil_name"     : safe(insect_data.get("tamil_name")),
            "confidence"     : str(round(confidence * 100, 2)) + "%",
            "alert"          : False,
            "action_message" : safe(insect_data.get("action_message")),
            "crops_affected" : "",
            "damage"         : "",
            "pesticide"      : "",
            "organic"        : "",
            "best_time"      : "",
            "warning"        : "",
            "benefit"        : safe(insect_data.get("benefit")),
            "crops_helped"   : safe(insect_data.get("crops_helped")),
            "advice"         : safe(insect_data.get("advice")),
            "fun_fact"       : safe(insect_data.get("fun_fact")),
            "timestamp"      : timestamp
        }

    # Store in Firebase
    db.reference('detections').push({
        "insect_type" : insect_type,
        "insect_name" : insect_name,
        "confidence"  : str(round(confidence * 100, 2)) + "%",
        "alert"       : is_harmful,
        "action"      : safe(insect_data.get("action_message")),
        "timestamp"   : timestamp
    })

    print(f"\n[{timestamp}] {insect_name} ({insect_type}) | {round(confidence*100,2)}%")
    print(f"All predictions: {all_preds}")

    return jsonify(response_data)

@app.route('/history', methods=['GET'])
def history():
    data = db.reference('detections').get()
    if data:
        items = list(data.values())
        items.reverse()
        return jsonify(items[:50])
    return jsonify([])

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status"  : "running",
        "version" : "7.0",
        "classes" : CLASS_LABELS
    })

if __name__ == '__main__':
    print("=" * 50)
    print("  Smart Insect Server v7.0")
    print("  10-Class Detection Model")
    print("  http://0.0.0.0:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)