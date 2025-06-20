# Committee API Configuration
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

# Committee endpoints
COMMITTEE_BROWSE_URL = f"{BASE_URL}/browse/committee"
COMMITTEE_DETAILS_URL = f"{BASE_URL}/committees"  # Example endpoint
COMMITTEE_DOCUMENTS_URL = f"{BASE_URL}/committee/documents"  # Example endpoint

# Data directories
COMMITTEE_DATA_DIR = "committee_data"
os.makedirs(COMMITTEE_DATA_DIR, exist_ok=True)