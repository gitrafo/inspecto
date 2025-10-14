import secrets
import hmac
import hashlib
import json

SECRET_KEY = b"YourVerySecretKeyHere12345"
NUM_KEYS = 1000

keys = {}
for _ in range(NUM_KEYS):
    key = ''.join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(16))
    # Optional: pre-sign keys with HMAC (empty machine_id for now)
    sig = hmac.new(SECRET_KEY, key.encode(), hashlib.sha256).hexdigest()
    keys[key] = sig

# Save to JSON
with open("valid_keys.json", "w") as f:
    json.dump(keys, f, indent=2)

print("Generated keys saved to valid_keys.json")
