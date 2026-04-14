import requests
import json
import os

SERVER_URL = "http://localhost:5000/predict"

print("=" * 55)
print("  TESTING FLASK SERVER")
print("=" * 55)

def test_image(image_path, expected_label=None):
    print(f"\n📸 Testing: {image_path}")

    if not os.path.exists(image_path):
        print(f"  ❌ Image not found: {image_path}")
        print(f"     Run prepare_test_images.py first!")
        return

    try:
        with open(image_path, 'rb') as f:
            files    = {'image': (image_path, f, 'image/jpeg')}
            response = requests.post(SERVER_URL, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Response received!")
            print(f"  🐛 Insect Type : {result['insect_type']}")
            print(f"  📊 Confidence  : {result['confidence']}")
            print(f"  💊 Suggestion  : {result['suggestion']}")

            if expected_label:
                if result['insect_type'] == expected_label:
                    print(f"  🎯 Result      : ✅ Correct prediction!")
                else:
                    print(f"  🎯 Result      : ⚠️  Got {result['insect_type']}, expected {expected_label}")
        else:
            print(f"  ❌ Server returned error: {response.status_code}")
            print(f"  Message: {response.text}")

    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to server!")
        print("  → Make sure server.py is running in Terminal 1")
        print("  → Run: python server.py")
    except requests.exceptions.Timeout:
        print("  ❌ Server took too long to respond.")
        print("  → This is normal on first request. Try again.")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")

# ─────────────────────────────────────────
# RUN ALL TESTS
# ─────────────────────────────────────────

print("\n🔴 Test 1 — Harmful Insect:")
test_image("test_harmful.jpg", expected_label="Harmful")

print("\n🟢 Test 2 — Beneficial Insect:")
test_image("test_beneficial.jpg", expected_label="Beneficial")

print("\n" + "=" * 55)
print("  ALL TESTS DONE!")
print("  ➡️  Now check Firebase console:")
print("  https://console.firebase.google.com")
print("  Look for 'detections' node in Realtime Database")
print("=" * 55)