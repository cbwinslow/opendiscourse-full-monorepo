# Congress.gov Member API Configuration
import os

# Sign up for API key at https://api.data.gov/signup
API_KEY = os.getenv('CONGRESS_API_KEY', 'YOUR_API_KEY_HERE')

# API Base URL
BASE_URL = "https://api.congress.gov/v3"

# Headers for API requests
HEADERS = {
    "X-Api-Key": API_KEY,
    "Accept": "application/json"
}

# Member endpoints
MEMBER_LIST_URL = f"{BASE_URL}/member"
MEMBER_DETAILS_URL = f"{BASE_URL}/member/{{member_id}}"
MEMBER_VOTES_URL = f"{BASE_URL}/member/{{member_id}}/votes"

# Data directories
MEMBER_DATA_DIR = "member_data"
os.makedirs(MEMBER_DATA_DIR, exist_ok=True)