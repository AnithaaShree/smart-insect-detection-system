import urllib.request
import os

test_images = {
    "test_harmful.jpg"   : "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Aphis_fabae.jpg/320px-Aphis_fabae.jpg",
    "test_beneficial.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/24701-nature-natural-beauty.jpg/320px-24701-nature-natural-beauty.jpg"
}

print("Downloading test images...")

for filename, url in test_images.items():
    try:
        urllib.request.urlretrieve(url, filename)
        size = os.path.getsize(filename)
        print(f"✅ Downloaded: {filename} ({size} bytes)")
    except Exception as e:
        print(f"❌ Failed: {filename} — {e}")

print("\nTest images ready!")
print("Now run: python test_server.py")