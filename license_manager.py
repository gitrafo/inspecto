# license_manager.py
import os
import json
import hashlib
import platform
from pathlib import Path
from valid_key_hashes import VALID_KEY_HASHES

APP_NAME = "Inspecto"
LICENSE_FILE = os.path.join(os.getenv("APPDATA") or str(Path.home()), APP_NAME, "license.json")


def ensure_license_folder():
    folder = os.path.dirname(LICENSE_FILE)
    os.makedirs(folder, exist_ok=True)


def save_license(key: str):
    """Save license key and current machine HWID."""
    ensure_license_folder()
    data = {"key": key, "hwid": machine_fingerprint()}
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_license():
    """Return (key, hwid) tuple, or (None, None) if missing."""
    if not os.path.exists(LICENSE_FILE):
        return None, None
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("key"), data.get("hwid")
    except Exception:
        return None, None


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def machine_fingerprint() -> str:
    """
    Returns a simple fingerprint of the machine.
    You can extend this to include CPU/BIOS/other identifiers.
    """
    info = platform.node() + platform.system() + platform.machine()
    return sha256_hex(info)
    #return "fake"


def verify_key_offline(key: str) -> bool:
    """Check if key hash exists in the valid keys list (offline)."""
    return sha256_hex(key.strip()) in VALID_KEY_HASHES


def validate_key_format(key: str) -> bool:
    """Check basic format: INSPECTO-PRO-XXXX-XXXX"""
    if not isinstance(key, str):
        return False
    parts = key.split("-")
    return len(parts) >= 4 and parts[0] == "INSPECTO" and parts[1] == "PRO"


def is_pro() -> bool:
    """Return True if the license is valid and matches this machine."""
    key, hwid = load_license()
    if not key or not hwid:
        return False
    return verify_key_offline(key) and hwid == machine_fingerprint()


def verify_hwid_match(key: str) -> bool:
    """
    Return True if:
      - no license yet (first activation)
      - or key already activated on this machine
    Return False if key is already used on another machine.
    """
    saved_key, saved_hwid = load_license()
    if saved_key is None:
        return True  # first activation
    if saved_key == key and saved_hwid == machine_fingerprint():
        return True  # already
