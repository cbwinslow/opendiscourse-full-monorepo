"""
Congress.gov API Helper Functions

This module provides helper functions, data models, and utilities for interacting
with the Congress.gov API to access federal legislative information.
"""

import requests
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# API Configuration
CONGRESS_GOV_API_BASE = "https://api.data.gov/congress/v3"
CONGRESS_GOV_API_KEY = os.getenv("CONGRESS_GOV_API_KEY", "")

# Data Models (Based on ProPublica Congress API documentation as official docs are limited)
@dataclass
class Member:
    id: str
    title: str
    short_title: str
    api_uri: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix: Optional[str]
    date_of_birth: str
    gender: str
    party: str
    leadership_role: Optional[str]
    twitter_account: Optional[str]
    facebook_account: Optional[str]
    youtube_account: Optional[str]
    govtrack_id: Optional[str]
    cspan_id: Optional[str]
    votesmart_id: Optional[str]
    icpsr_id: Optional[str]
    crp_id: Optional[str]
    google_entity_id: Optional[str]
    fec_candidate_id: Optional[str]
    url: str
    rss_url: Optional[str]
    contact_form: Optional[str]
    in_office: bool
    cook_pvi: Optional[str]
    dw_nominate: Optional[str]
    ideal_point: Optional[str]
    seniority: str
    next_election: str
    total_votes: int
    missed_votes: int
    total_present: int
    last_updated: str
    ocd_id: str
    office: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    state: str
    senate_class: Optional[str]
    state_rank: Optional[str]
    district: Optional[str]
    at_large: Optional[bool]
    geoid: Optional[str]
    missed_votes_pct: float
    votes_with_party_pct: float
    votes_against_party_pct: float

@dataclass
class Bill:
    bill_id: str
    bill_type: str
    number: str
    bill_uri: str
    title: str
    short_title: Optional[str]
    sponsor_id: str
    congressdotgov_url: str
    govtrack_url: Optional[str]
    introduced_date: str
    active: bool
    last_vote: Optional[str]
    house_passage: Optional[str]
    senate_passage: Optional[str]
    enacted: Optional[str]
    vetoed: Optional[str]
    cosponsors: int
    cosponsors_by_party: Dict[str, int]
    committees: str
    primary_subject: str
    summary: str
    summary_short: str
    latest_major_action_date: str
    latest_major_action: str

@dataclass
class Vote:
    member_id: str
    chamber: str
    congress: str
    session: str
    roll_call: str
    vote_uri: str
    bill: Dict[str, Any]
    amendment: Dict[str, Any]
    description: str
    question: str
    result: str
    date: str
    time: str
    position: str

class CongressGovAPI:
    """Helper class for interacting with the Congress.gov API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Congress.gov API client.
        
        Args:
            api_key: API key for authentication. If not provided, will use 
                    CONGRESS_GOV_API_KEY environment variable.
        """
        self.api_key = api_key or CONGRESS_GOV_API_KEY
        if not self.api_key:
            raise ValueError("Congress.gov API key is required. Set CONGRESS_GOV_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Congress.gov API.
        
        Args:
            endpoint: API endpoint (e.g., "/member")
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        if params is None:
            params = {}
        
        # Add API key to parameters
        params["api_key"] = self.api_key
        
        url = f"{CONGRESS_GOV_API_BASE}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_members(self, congress: Optional[str] = None, chamber: Optional[str] = None) -> Dict:
        """
        Get list of members of Congress.
        
        Args:
            congress: Congress number (e.g., "117")
            chamber: Chamber ("house" or "senate")
            
        Returns:
            Dictionary with members data
        """
        endpoint = "/member"
        params = {}
        
        if congress:
            endpoint += f"/{congress}"
        if chamber:
            endpoint += f"/{chamber}"
            
        return self._make_request(endpoint, params)
    
    def get_member(self, member_id: str) -> Member:
        """
        Get detailed information about a specific member.
        
        Args:
            member_id: Member ID
            
        Returns:
            Member object
        """
        data = self._make_request(f"/member/{member_id}")
        # Note: This is based on ProPublica API structure, actual Congress.gov structure may differ
        return Member(**data.get("results", [{}])[0])
    
    def get_bills(self, bill_type: Optional[str] = None, congress: Optional[str] = None,
                  chamber: Optional[str] = None, page: int = 1) -> Dict:
        """
        Get list of bills.
        
        Args:
            bill_type: Type of bill ("introduced", "updated", "active", "passed", "enacted")
            congress: Congress number
            chamber: Chamber ("house" or "senate")
            page: Page number
            
        Returns:
            Dictionary with bills data
        """
        endpoint = "/bill"
        params = {"page": page}
        
        if bill_type:
            endpoint += f"/{bill_type}"
        if congress:
            endpoint += f"/{congress}"
        if chamber:
            endpoint += f"/{chamber}"
            
        return self._make_request(endpoint, params)
    
    def get_bill(self, bill_id: str) -> Bill:
        """
        Get detailed information about a specific bill.
        
        Args:
            bill_id: Bill ID
            
        Returns:
            Bill object
        """
        data = self._make_request(f"/bill/{bill_id}")
        # Note: This is based on ProPublica API structure, actual Congress.gov structure may differ
        return Bill(**data.get("results", [{}])[0])
    
    def get_votes(self, member_id: str, offset: int = 0) -> Dict:
        """
        Get voting history for a member.
        
        Args:
            member_id: Member ID
            offset: Offset for pagination
            
        Returns:
            Dictionary with votes data
        """
        params = {
            "offset": offset
        }
        return self._make_request(f"/member/{member_id}/votes", params)
    
    def get_committees(self, congress: Optional[str] = None, chamber: Optional[str] = None) -> Dict:
        """
        Get list of committees.
        
        Args:
            congress: Congress number
            chamber: Chamber ("house" or "senate")
            
        Returns:
            Dictionary with committees data
        """
        endpoint = "/committee"
        if congress:
            endpoint += f"/{congress}"
        if chamber:
            endpoint += f"/{chamber}"
            
        return self._make_request(endpoint)
    
    def get_nominations(self, congress: Optional[str] = None) -> Dict:
        """
        Get list of nominations.
        
        Args:
            congress: Congress number
            
        Returns:
            Dictionary with nominations data
        """
        endpoint = "/nomination"
        if congress:
            endpoint += f"/{congress}"
            
        return self._make_request(endpoint)
    
    def save_data_to_file(self, data: Dict, filename: str) -> None:
        """
        Save API response data to a JSON file.
        
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

# Alternative implementation using ProPublica Congress API
class ProPublicaCongressAPI:
    """Helper class for interacting with the ProPublica Congress API as an alternative."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ProPublica Congress API client.
        
        Args:
            api_key: API key for authentication. If not provided, will use 
                    PROPUBLICA_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("PROPUBLICA_API_KEY", "")
        if not self.api_key:
            raise ValueError("ProPublica API key is required. Set PROPUBLICA_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })
        
        self.base_url = "https://api.propublica.org/congress/v1"
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the ProPublica Congress API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_members(self, congress: str, chamber: str) -> Dict:
        """
        Get list of members of Congress.
        
        Args:
            congress: Congress number (e.g., "117")
            chamber: Chamber ("house" or "senate")
            
        Returns:
            Dictionary with members data
        """
        return self._make_request(f"/{congress}/{chamber}/members.json")
    
    def get_member(self, member_id: str) -> Dict:
        """
        Get detailed information about a specific member.
        
        Args:
            member_id: Member ID
            
        Returns:
            Dictionary with member data
        """
        return self._make_request(f"/members/{member_id}.json")
    
    def get_bills(self, congress: str, chamber: str, bill_type: str, page: int = 1) -> Dict:
        """
        Get list of bills.
        
        Args:
            congress: Congress number
            chamber: Chamber ("house" or "senate")
            bill_type: Type of bill ("introduced", "updated", "active", "passed", "enacted")
            page: Page number
            
        Returns:
            Dictionary with bills data
        """
        return self._make_request(f"/{congress}/{chamber}/bills/{bill_type}.json", {"page": page})
    
    def get_bill(self, congress: str, bill_id: str) -> Dict:
        """
        Get detailed information about a specific bill.
        
        Args:
            congress: Congress number
            bill_id: Bill ID
            
        Returns:
            Dictionary with bill data
        """
        return self._make_request(f"/{congress}/bills/{bill_id}.json")
    
    def get_votes(self, chamber: str, year: str, month: str) -> Dict:
        """
        Get votes for a specific month.
        
        Args:
            chamber: Chamber ("house" or "senate")
            year: Year (e.g., "2022")
            month: Month (e.g., "01")
            
        Returns:
            Dictionary with votes data
        """
        return self._make_request(f"/{chamber}/votes/{year}/{month}.json")

# Utility functions for common operations
def create_congress_gov_client(api_key: Optional[str] = None) -> CongressGovAPI:
    """
    Create a Congress.gov API client.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        CongressGovAPI client instance
    """
    return CongressGovAPI(api_key)

def create_propublica_client(api_key: Optional[str] = None) -> ProPublicaCongressAPI:
    """
    Create a ProPublica Congress API client.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        ProPublicaCongressAPI client instance
    """
    return ProPublicaCongressAPI(api_key)

# Example usage
if __name__ == "__main__":
    # Example of how to use the Congress.gov API helper functions
    # congress_client = create_congress_gov_client("your-api-key-here")
    # propublica_client = create_propublica_client("your-api-key-here")
    # 
    # # Get members of the House
    # members = congress_client.get_members(chamber="house")
    # print(f"Found {len(members.get('results', []))} House members")
    pass