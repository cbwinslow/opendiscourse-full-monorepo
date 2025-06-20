"""Configuration for the GovInfo API."""
import os

API_KEY = os.getenv("GOVINFO_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.govinfo.gov"
HEADERS = {"X-Api-Key": API_KEY, "Accept": "application/json"}
COLLECTIONS_URL = f"{BASE_URL}/collections"
PACKAGE_URL = f"{BASE_URL}/packages"
