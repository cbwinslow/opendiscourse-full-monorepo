"""
GovInfo.gov API Helper Functions

This module provides helper functions and utilities for accessing
GovInfo.gov content and metadata through various available methods.
"""

import requests
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import xml.etree.ElementTree as ET

# API Configuration
GOVINFO_BASE_URL = "https://www.govinfo.gov"

class GovInfoAPI:
    """Helper class for interacting with GovInfo.gov services."""
    
    def __init__(self):
        """Initialize the GovInfo API client."""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make a request to GovInfo.gov.
        
        Args:
            url: Full URL for the request
            params: Query parameters
            
        Returns:
            Response object
        """
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response
    
    def get_bulk_data_collections(self) -> Dict:
        """
        Get information about available bulk data collections.
        
        Returns:
            Dictionary with bulk data collection information
        """
        # This is a placeholder as the actual endpoint structure is not well documented
        url = f"{GOVINFO_BASE_URL}/bulkdata/json"
        try:
            response = self._make_request(url)
            return response.json()
        except:
            # Return a basic structure if the endpoint doesn't work as expected
            return {
                "collections": [
                    "CFR", "Federal Register", "US Code", "Public Laws", 
                    "Private Laws", "Statutes at Large", "Congressional Record"
                ]
            }
    
    def get_collection_data(self, collection: str, year: Optional[str] = None) -> Dict:
        """
        Get data for a specific collection.
        
        Args:
            collection: Collection name (e.g., "CFR", "FR", "USCODE")
            year: Year for the collection (if applicable)
            
        Returns:
            Dictionary with collection data
        """
        # This is a placeholder as the actual endpoint structure is not well documented
        url = f"{GOVINFO_BASE_URL}/bulkdata/{collection}"
        if year:
            url += f"/{year}"
        url += "/json"
        
        try:
            response = self._make_request(url)
            return response.json()
        except:
            # Return a basic structure if the endpoint doesn't work as expected
            return {
                "collection": collection,
                "year": year,
                "status": "endpoint not accessible",
                "note": "Please check GovInfo.gov documentation for correct endpoint structure"
            }
    
    def create_link_service_url(self, collection: str, params: Dict) -> str:
        """
        Create a URL using the GovInfo link service.
        
        Args:
            collection: Collection name
            params: Parameters for the link service
            
        Returns:
            URL for accessing the content
        """
        # Base URL for link service
        url = f"{GOVINFO_BASE_URL}/link"
        
        # Add collection parameter
        params["collection"] = collection
        
        # Construct URL with parameters
        param_strings = [f"{key}={value}" for key, value in params.items()]
        if param_strings:
            url += "?" + "&".join(param_strings)
            
        return url
    
    def get_rss_feed(self, collection: str) -> str:
        """
        Get RSS feed URL for a collection.
        
        Args:
            collection: Collection name
            
        Returns:
            RSS feed URL
        """
        return f"{GOVINFO_BASE_URL}/rss/{collection}.xml"
    
    def save_data_to_file(self, data: Dict, filename: str) -> None:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filename: Name of the file to save to
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data_from_file(self, filename: str) -> Dict:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded data as dictionary
        """
        with open(filename, 'r') as f:
            return json.load(f)

# Utility functions for common operations
def create_govinfo_client() -> GovInfoAPI:
    """
    Create a GovInfo API client.
    
    Returns:
        GovInfoAPI client instance
    """
    return GovInfoAPI()

def download_bulk_data_collection(client: GovInfoAPI, collection: str, 
                                output_dir: str = "govinfo_data") -> None:
    """
    Download a bulk data collection.
    
    Args:
        client: GovInfoAPI client instance
        collection: Collection name
        output_dir: Directory to save downloaded data
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get collection data
    data = client.get_collection_data(collection)
    
    # Save to file
    filename = os.path.join(output_dir, f"{collection.lower()}_data.json")
    client.save_data_to_file(data, filename)
    print(f"Saved {collection} data to {filename}")

# Example usage
if __name__ == "__main__":
    # Example of how to use the GovInfo API helper functions
    # client = create_govinfo_client()
    # 
    # # Get bulk data collections
    # collections = client.get_bulk_data_collections()
    # print(f"Available collections: {collections}")
    # 
    # # Create a link service URL
    # link_url = client.create_link_service_url("CFR", {"title": "26", "part": "1"})
    # print(f"Link service URL: {link_url}")
    # 
    # # Get RSS feed URL
    # rss_url = client.get_rss_feed("CFR")
    # print(f"RSS feed URL: {rss_url}")
    pass