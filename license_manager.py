import os
import json
import requests
from pathlib import Path

APP_NAME = "Inspecto"
LICENSE_FILE = os.path.join(os.getenv("APPDATA"), APP_NAME, "license.json")
GUMROAD_API = "https://api.gumroad.com/v2/licenses/verify"
PRODUCT_PERMALINK = "inspecto-pro"  # ← replace with your Gumroad product permalink


def ensure_license_folder():
    folder = os.path.dirname(LICENSE_FILE)
    os.makedirs(folder, exist_ok=True)


def save_license_locally(license_key, purchase_info):
    ensure_license_folder()
    data = {"license_key": license_key, "purchase_info": purchase_info}
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)


def load_license():
    if not os.path.exists(LICENSE_FILE):
        return None
    try:
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def verify_license_online(license_key):
    """Verify license using Gumroad API"""
    data = {"product_permalink": PRODUCT_PERMALINK, "license_key": license_key}
    try:
        r = requests.post(GUMROAD_API, data=data, timeout=8)
        r.raise_for_status()
        response = r.json()

        if response.get("success"):
            save_license_locally(license_key, response["purchase"])
            email = response["purchase"].get("email", "unknown user")
            return True, f"✅ License activated for {email}"
        else:
            return False, f"❌ {response.get('message', 'Invalid license key')}"
    except Exception as e:
        return False, f"⚠️ Network or server error: {e}"


def is_pro():
    """Check if local license exists and seems valid"""
    lic = load_license()
    return lic is not None and "license_key" in lic


def get_registered_email():
    lic = load_license()
    if lic and "purchase_info" in lic:
        return lic["purchase_info"].get("email")
    return None
