"""API configuration settings for all services"""

import os

# GovInfo API Configuration
GOVINFO_API_KEY = os.getenv("GOVINFO_API_KEY", "YOUR_API_KEY_HERE")
GOVINFO_BASE_URL = "https://api.govinfo.gov"
GOVINFO_HEADERS = {"X-Api-Key": GOVINFO_API_KEY, "Accept": "application/json"}

# Ollama Configuration
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "default_model": "llama2",
    "timeout": 300,
    "max_retries": 3
}

# MCP Server Configuration
MCP_SERVER = "http://localhost:8080"
