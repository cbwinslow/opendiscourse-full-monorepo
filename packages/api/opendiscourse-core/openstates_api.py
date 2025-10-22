"""
OpenStates API Helper Functions

This module provides helper functions, data models, and utilities for interacting
with the OpenStates API v3 to access state legislative information.
"""

import requests
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# API Configuration
OPENSTATES_API_BASE = "https://v3.openstates.org"
OPENSTATES_API_KEY = os.getenv("OPENSTATES_API_KEY", "")

# Data Models
@dataclass
class Jurisdiction:
    id: str
    name: str
    classification: str
    url: str
    division: Dict[str, Any]
    legislative_sessions: List[Dict[str, Any]]

@dataclass
class Person:
    id: str
    name: str
    given_name: str
    family_name: str
    email: Optional[str]
    gender: Optional[str]
    biography: Optional[str]
    birth_date: Optional[str]
    death_date: Optional[str]
    image: Optional[str]
    links: List[Dict[str, str]]
    sources: List[Dict[str, str]]
    extras: Dict[str, Any]
    offices: List[Dict[str, Any]]
    party: List[Dict[str, str]]
    roles: List[Dict[str, Any]]

@dataclass
class Bill:
    id: str
    session: str
    jurisdiction: Dict[str, Any]
    identifier: str
    title: str
    classification: List[str]
    subject: List[str]
    extras: Dict[str, Any]
    created_at: str
    updated_at: str
    openstates_url: str
    sponsorships: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    votes: List[Dict[str, Any]]
    versions: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    sources: List[Dict[str, str]]

@dataclass
class Committee:
    id: str
    name: str
    chamber: str
    jurisdiction: Dict[str, Any]
    members: List[Dict[str, Any]]
    sources: List[Dict[str, str]]
    links: List[Dict[str, str]]
    extras: Dict[str, Any]
    created_at: str
    updated_at: str

@dataclass
class Event:
    id: str
    name: str
    jurisdiction: Dict[str, Any]
    description: str
    classification: str
    start_date: str
    end_date: str
    all_day: bool
    status: str
    location: Dict[str, Any]
    media: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    links: List[Dict[str, str]]
    sources: List[Dict[str, str]]
    participants: List[Dict[str, Any]]
    agenda: List[Dict[str, Any]]
    extras: Dict[str, Any]
    created_at: str
    updated_at: str

class OpenStatesAPI:
    """Helper class for interacting with the OpenStates API v3."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenStates API client.
        
        Args:
            api_key: API key for authentication. If not provided, will use 
                    OPENSTATES_API_KEY environment variable.
        """
        self.api_key = api_key or OPENSTATES_API_KEY
        if not self.api_key:
            raise ValueError("OpenStates API key is required. Set OPENSTATES_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the OpenStates API.
        
        Args:
            endpoint: API endpoint (e.g., "/jurisdictions")
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{OPENSTATES_API_BASE}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_jurisdictions(self, page: int = 1, per_page: int = 100) -> Dict:
        """
        Get list of available jurisdictions.
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dictionary with jurisdictions data
        """
        params = {
            "page": page,
            "per_page": per_page
        }
        return self._make_request("/jurisdictions", params)
    
    def get_jurisdiction(self, jurisdiction_id: str) -> Jurisdiction:
        """
        Get detailed metadata for a particular jurisdiction.
        
        Args:
            jurisdiction_id: OCD ID of the jurisdiction
            
        Returns:
            Jurisdiction object
        """
        data = self._make_request(f"/jurisdictions/{jurisdiction_id}")
        return Jurisdiction(**data)
    
    def get_people(self, name: Optional[str] = None, jurisdiction: Optional[str] = None,
                   district: Optional[str] = None, chamber: Optional[str] = None,
                   page: int = 1, per_page: int = 100) -> Dict:
        """
        List or search people (legislators, governors, etc.).
        
        Args:
            name: Filter by name
            jurisdiction: Filter by jurisdiction ID
            district: Filter by district
            chamber: Filter by chamber (upper/lower)
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dictionary with people data
        """
        params = {
            "page": page,
            "per_page": per_page
        }
        if name:
            params["name"] = name
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if district:
            params["district"] = district
        if chamber:
            params["chamber"] = chamber
            
        return self._make_request("/people", params)
    
    def get_person(self, person_id: str) -> Person:
        """
        Get detailed information about a specific person.
        
        Args:
            person_id: OCD ID of the person
            
        Returns:
            Person object
        """
        data = self._make_request(f"/people/{person_id}")
        return Person(**data)
    
    def get_people_geo(self, lat: float, lng: float) -> Dict:
        """
        Get legislators for a given location.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Dictionary with people data for the location
        """
        params = {
            "lat": lat,
            "lng": lng
        }
        return self._make_request("/people.geo", params)
    
    def get_bills(self, jurisdiction: Optional[str] = None, session: Optional[str] = None,
                  chamber: Optional[str] = None, sponsor: Optional[str] = None,
                  subject: Optional[str] = None, updated_since: Optional[str] = None,
                  created_since: Optional[str] = None, search: Optional[str] = None,
                  sort: Optional[str] = None, page: int = 1, per_page: int = 100) -> Dict:
        """
        Search bills by various criteria.
        
        Args:
            jurisdiction: Filter by jurisdiction ID
            session: Filter by session
            chamber: Filter by chamber
            sponsor: Filter by sponsor ID
            subject: Filter by subject
            updated_since: Filter by updated date (YYYY-MM-DD)
            created_since: Filter by created date (YYYY-MM-DD)
            search: Full text search
            sort: Sort field (created_at, updated_at)
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dictionary with bills data
        """
        params = {
            "page": page,
            "per_page": per_page
        }
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if session:
            params["session"] = session
        if chamber:
            params["chamber"] = chamber
        if sponsor:
            params["sponsor"] = sponsor
        if subject:
            params["subject"] = subject
        if updated_since:
            params["updated_since"] = updated_since
        if created_since:
            params["created_since"] = created_since
        if search:
            params["search"] = search
        if sort:
            params["sort"] = sort
            
        return self._make_request("/bills", params)
    
    def get_bill_by_id(self, bill_id: str) -> Bill:
        """
        Get bill by internal ID.
        
        Args:
            bill_id: OCD ID of the bill
            
        Returns:
            Bill object
        """
        data = self._make_request(f"/bills/ocd-bill/{bill_id}")
        return Bill(**data)
    
    def get_bill_by_jurisdiction(self, jurisdiction: str, session: str, bill_id: str) -> Bill:
        """
        Get bill by jurisdiction, session, and ID.
        
        Args:
            jurisdiction: Jurisdiction ID
            session: Session identifier
            bill_id: Bill identifier
            
        Returns:
            Bill object
        """
        data = self._make_request(f"/bills/{jurisdiction}/{session}/{bill_id}")
        return Bill(**data)
    
    def get_committees(self, jurisdiction: str, page: int = 1, per_page: int = 100) -> Dict:
        """
        Get list of committees by jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction ID
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dictionary with committees data
        """
        params = {
            "jurisdiction": jurisdiction,
            "page": page,
            "per_page": per_page
        }
        return self._make_request("/committees", params)
    
    def get_committee(self, committee_id: str) -> Committee:
        """
        Get details on committee by internal ID.
        
        Args:
            committee_id: OCD ID of the committee
            
        Returns:
            Committee object
        """
        data = self._make_request(f"/committees/{committee_id}")
        return Committee(**data)
    
    def get_events(self, jurisdiction: str, page: int = 1, per_page: int = 100) -> Dict:
        """
        Get list of events by jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction ID
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dictionary with events data
        """
        params = {
            "jurisdiction": jurisdiction,
            "page": page,
            "per_page": per_page
        }
        return self._make_request("/events", params)
    
    def get_event(self, event_id: str) -> Event:
        """
        Get details on event by internal ID.
        
        Args:
            event_id: OCD ID of the event
            
        Returns:
            Event object
        """
        data = self._make_request(f"/events/{event_id}")
        return Event(**data)
    
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

# Utility functions for common operations
def create_openstates_client(api_key: Optional[str] = None) -> OpenStatesAPI:
    """
    Create an OpenStates API client.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        OpenStatesAPI client instance
    """
    return OpenStatesAPI(api_key)

def get_all_jurisdictions(client: OpenStatesAPI) -> List[Jurisdiction]:
    """
    Get all jurisdictions from the OpenStates API.
    
    Args:
        client: OpenStatesAPI client instance
        
    Returns:
        List of all jurisdictions
    """
    all_jurisdictions = []
    page = 1
    
    while True:
        response = client.get_jurisdictions(page=page)
        jurisdictions = response.get('results', [])
        
        if not jurisdictions:
            break
            
        for jur in jurisdictions:
            all_jurisdictions.append(Jurisdiction(**jur))
            
        page += 1
        
        # Check if we've reached the end
        if len(jurisdictions) < 100:  # Assuming default per_page=100
            break
    
    return all_jurisdictions

def get_all_people_for_jurisdiction(client: OpenStatesAPI, jurisdiction_id: str) -> List[Person]:
    """
    Get all people for a specific jurisdiction.
    
    Args:
        client: OpenStatesAPI client instance
        jurisdiction_id: Jurisdiction ID
        
    Returns:
        List of all people in the jurisdiction
    """
    all_people = []
    page = 1
    
    while True:
        response = client.get_people(jurisdiction=jurisdiction_id, page=page)
        people = response.get('results', [])
        
        if not people:
            break
            
        for person in people:
            all_people.append(Person(**person))
            
        page += 1
        
        # Check if we've reached the end
        if len(people) < 100:  # Assuming default per_page=100
            break
    
    return all_people

def get_all_bills_for_jurisdiction(client: OpenStatesAPI, jurisdiction_id: str) -> List[Bill]:
    """
    Get all bills for a specific jurisdiction.
    
    Args:
        client: OpenStatesAPI client instance
        jurisdiction_id: Jurisdiction ID
        
    Returns:
        List of all bills in the jurisdiction
    """
    all_bills = []
    page = 1
    
    while True:
        response = client.get_bills(jurisdiction=jurisdiction_id, page=page)
        bills = response.get('results', [])
        
        if not bills:
            break
            
        for bill in bills:
            all_bills.append(Bill(**bill))
            
        page += 1
        
        # Check if we've reached the end
        if len(bills) < 100:  # Assuming default per_page=100
            break
    
    return all_bills

# Example usage
if __name__ == "__main__":
    # Example of how to use the OpenStates API helper functions
    # client = create_openstates_client("your-api-key-here")
    # 
    # # Get all jurisdictions
    # jurisdictions = get_all_jurisdictions(client)
    # print(f"Found {len(jurisdictions)} jurisdictions")
    # 
    # # Get people for a specific jurisdiction (e.g., California)
    # ca_people = get_all_people_for_jurisdiction(client, "ocd-jurisdiction/country:us/state:ca/government")
    # print(f"Found {len(ca_people)} people in California")
    pass