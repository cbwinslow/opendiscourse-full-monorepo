# GovInfo API Configuration
import os

# Sign up for API key at https://api.data.gov/signup
API_KEY = os.getenv('GOVINFO_API_KEY', 'YOUR_API_KEY_HERE')

# API Base URL
BASE_URL = "https://api.govinfo.gov"

# Headers for API requests
HEADERS = {
    "X-Api-Key": API_KEY,
    "Accept": "application/json"
}

# Collections endpoint
COLLECTIONS_URL = f"{BASE_URL}/collections"

# Package endpoint
PACKAGE_URL = f"{BASE_URL}/packages"