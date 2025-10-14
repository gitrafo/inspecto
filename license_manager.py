import os
import json
import hashlib
import hmac
import uuid
from pathlib import Path

# Secret key for HMAC – keep this secret and offline
SECRET_KEY = b"YourVerySecretKeyHere12345"

# Pre-generated valid keys (replace with your actual 1000 keys)
VALID_KEYS = {
    "ABCD1234EFGH5678": "SIGNATURE1",
    "IJKL9012MNOP3456": "SIGNATURE2",
    # ...
}

LICENSE_FILE = Path.home() / ".inspecto_license.json"

def generate_hmac(key: str, machine_id: str) -> str:
    """Create a signature for a key + machine ID."""
    data = f"{key}:{machine_id}".encode("utf-8")
    return hmac.new(SECRET_KEY, data, hashlib.sha256).hexdigest()

def get_machine_id() -> str:
    """Generate a unique machine ID for binding."""
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode()).hexdigest()

def is_pro() -> bool:
    """Check if current machine has a valid Pro license."""
    if not LICENSE_FILE.exists():
        return False
    try:
        data = json.loads(LICENSE_FILE.read_text())
        key = data.get("key")
        machine_id = data.get("machine_id")
        signature = data.get("signature")
        if not key or not machine_id or not signature:
            return False
        expected_sig = generate_hmac(key, machine_id)
        return signature == expected_sig
    except Exception:
        return False

def validate_key_format(key: str) -> bool:
    """Optional: check key pattern (16 alphanumeric chars)."""
    return len(key) == 16 and key.isalnum()

def save_license(key: str):
    """Bind the key to this machine and save locally."""
    machine_id = get_machine_id()
    signature = generate_hmac(key, machine_id)
    data = {
        "key": key,
        "machine_id": machine_id,
        "signature": signature
    }
    LICENSE_FILE.write_text(json.dumps(data))

def verify_key_offline(key: str) -> bool:
    """Check if a key exists in your pre-generated list."""
    return key in VALID_KEYS
