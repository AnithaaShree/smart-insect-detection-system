import os

print("=" * 55)
print("  PROJECT SETUP CHECKER")
print("=" * 55)

required_files = {
    "server.py"        : "Flask server",
    "keras_model.h5"   : "Trained CNN model",
    "firebase_key.json": "Firebase credentials",
    "pesticide.json"   : "Pesticide suggestions"
}

all_good = True

for filename, description in required_files.items():
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌ MISSING"
    size   = ""

    if exists:
        size_bytes = os.path.getsize(filename)
        if size_bytes < 100:
            status = "⚠️  File exists but very small — may be empty!"
            all_good = False
        else:
            size = f"({round(size_bytes / 1024 / 1024, 2)} MB)"
    else:
        all_good = False

    print(f"  {status}  {filename} {size}")
    print(f"           → {description}")
    print()

print("=" * 55)
if all_good:
    print("  ✅ ALL FILES READY — You can start the server!")
else:
    print("  ❌ Fix missing files before starting server.")
print("=" * 55)