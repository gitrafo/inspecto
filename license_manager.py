import os
import json

APP_NAME = "Inspecto"
LICENSE_FILE = os.path.join(os.getenv("APPDATA"), APP_NAME, "license.json")

# List of valid Pro keys
VALID_KEYS = [
    "INSPECTO-PRO-2025-0001",
    "INSPECTO-PRO-2025-0002",
    "INSPECTO-PRO-2025-0003",
]

def ensure_license_folder():
    folder = os.path.dirname(LICENSE_FILE)
    os.makedirs(folder, exist_ok=True)

def save_license(key):
    ensure_license_folder()
    data = {"key": key}
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

def load_license():
    if not os.path.exists(LICENSE_FILE):
        return None
    try:
        with open(LICENSE_FILE, "r") as f:
            data = json.load(f)
        return data.get("key")
    except:
        return None

# <<< This is the function you must have >>>
def is_pro():
    key = load_license()
    return key in VALID_KEYS

def validate_key_format(key):
    """
    Basic format check: INSPECTO-PRO-YYYY-XXXX
    """
    if not isinstance(key, str):
        return False
    parts = key.split("-")
    if len(parts) != 4:
        return False
    prefix, pro, year, serial = parts
    return prefix == "INSPECTO" and pro == "PRO" and year.isdigit() and serial.isdigit()