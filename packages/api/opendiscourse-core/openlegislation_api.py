"""
OpenLegislation API Helper Functions

This module provides helper functions, data models, and utilities for interacting
with the OpenLegislation API to access legislative information.
"""

import requests
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# API Configuration
OPENLEGISLATION_API_BASE = "https://legislation.nysenate.gov/api/3"
OPENLEGISLATION_API_KEY = os.getenv("OPENLEGISLATION_API_KEY", "")

# Data Models
@dataclass
class Sponsor:
    fullname: str

@dataclass
class BillAction:
    date: str
    text: str

@dataclass
class BillVote:
    voteType: str
    voteDate: str
    ayes: List[str]
    nays: List[str]
    abstains: List[str]
    excused: List[str]
    ayeswr: Optional[List[str]]
    description: Optional[str]

@dataclass
class Bill:
    year: str
    senateBillNo: str
    title: str
    lawSection: str
    sameAs: Optional[str]
    previousVersions: Optional[List[str]]
    sponsor: Sponsor
    coSponsors: Optional[List[str]]
    multiSponsors: Optional[List[str]]
    summary: str
    currentCommittee: Optional[str]
    actions: List[BillAction]
    fulltext: str
    memo: str
    law: str
    votes: List[BillVote]

@dataclass
class MeetingBill:
    year: str
    senateBillNo: str
    title: str
    sameAs: Optional[str]
    sponsor: Sponsor
    summary: str

@dataclass
class Meeting:
    meetingDateTime: str
    meetday: str
    location: Optional[str]
    committeeName: str
    committeeChair: str
    bills: List[MeetingBill]
    notes: str

@dataclass
class CalendarEntry:
    no: str
    bill: Dict[str, Any]  # Using Dict for flexibility
    billHigh: Optional[bool]
    subBill: Optional[str]
    motionDate: Optional[str]

@dataclass
class CalendarSection:
    name: str
    type: str
    cd: str
    calendarEntries: List[CalendarEntry]

@dataclass
class CalendarSupplemental:
    calendarDate: Optional[str]
    releaseDateTime: Optional[str]
    sections: Optional[List[CalendarSection]]
    sequence: Optional[Dict[str, Any]]  # Using Dict for flexibility

@dataclass
class Calendar:
    year: str
    type: str
    sessionYear: str
    no: str
    supplementals: List[CalendarSupplemental]
    id: str

@dataclass
class Transcript:
    timeStamp: str
    location: str
    type: str
    transcriptText: str

class OpenLegislationAPI:
    """Helper class for interacting with the OpenLegislation API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenLegislation API client.
        
        Args:
            api_key: API key for authentication. If not provided, will use 
                    OPENLEGISLATION_API_KEY environment variable.
        """
        self.api_key = api_key or OPENLEGISLATION_API_KEY
        # Note: API key may not be required for public access
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the OpenLegislation API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        if params is None:
            params = {}
        
        # Add API key if provided
        if self.api_key:
            params["key"] = self.api_key
            
        url = f"{OPENLEGISLATION_API_BASE}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_bill(self, bill_id: str, year: str, format: str = "json") -> Dict:
        """
        Get a specific bill by ID and year.
        
        Args:
            bill_id: Bill ID (e.g., "S1234")
            year: Year (e.g., "2011")
            format: Response format ("json", "xml", "jsonp")
            
        Returns:
            Dictionary with bill data
        """
        endpoint = f"/bills/{bill_id}-{year}.{format}"
        return self._make_request(endpoint)
    
    def get_meeting(self, committee: str, month: str, day: str, year: str, 
                   format: str = "json") -> Dict:
        """
        Get a specific meeting by committee and date.
        
        Args:
            committee: Committee name
            month: Month (MM)
            day: Day (DD)
            year: Year (YYYY)
            format: Response format ("json", "xml", "jsonp")
            
        Returns:
            Dictionary with meeting data
        """
        endpoint = f"/meetings/{committee}-{month}-{day}-{year}.{format}"
        return self._make_request(endpoint)
    
    def get_calendar(self, calendar_type: str, month: str, day: str, year: str,
                    format: str = "json") -> Dict:
        """
        Get a specific calendar by type and date.
        
        Args:
            calendar_type: Calendar type ("floor" or "active")
            month: Month (MM)
            day: Day (DD)
            year: Year (YYYY)
            format: Response format ("json", "xml", "jsonp")
            
        Returns:
            Dictionary with calendar data
        """
        endpoint = f"/calendars/{calendar_type}-{month}-{day}-{year}.{format}"
        return self._make_request(endpoint)
    
    def get_transcript(self, session_type: str, month: str, day: str, year: str,
                      format: str = "json") -> Dict:
        """
        Get a specific transcript by session type and date.
        
        Args:
            session_type: Session type ("regular" or "special")
            month: Month (MM)
            day: Day (DD)
            year: Year (YYYY)
            format: Response format ("json", "xml", "jsonp")
            
        Returns:
            Dictionary with transcript data
        """
        endpoint = f"/transcripts/{session_type}-session-{month}-{day}-{year}.{format}"
        return self._make_request(endpoint)
    
    def search(self, term: str, page_size: int = 20, page_idx: int = 1,
              sort_order: bool = True, sort: Optional[str] = None,
              format: str = "json") -> Dict:
        """
        Search for documents using Lucene query syntax.
        
        Args:
            term: Lucene search term
            page_size: Number of results per page (1-1000)
            page_idx: Page index (1+)
            sort_order: Sort order (True = descending, False = ascending)
            sort: Field to sort by
            format: Response format ("json", "xml", "rss", "atom", "jsonp")
            
        Returns:
            Dictionary with search results
        """
        endpoint = f"/search.{format}"
        params = {
            "term": term,
            "pageSize": page_size,
            "pageIdx": page_idx,
            "sortOrder": sort_order
        }
        
        if sort:
            params["sort"] = sort
            
        return self._make_request(endpoint, params)
    
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
def create_openlegislation_client(api_key: Optional[str] = None) -> OpenLegislationAPI:
    """
    Create an OpenLegislation API client.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        OpenLegislationAPI client instance
    """
    return OpenLegislationAPI(api_key)

def search_bills_by_sponsor(client: OpenLegislationAPI, sponsor_name: str,
                           page_size: int = 20) -> List[Dict]:
    """
    Search for bills by sponsor name.
    
    Args:
        client: OpenLegislationAPI client instance
        sponsor_name: Name of the sponsor
        page_size: Number of results per page
        
    Returns:
        List of bills
    """
    term = f"sponsor.fullname:{sponsor_name}"
    response = client.search(term, page_size=page_size)
    return response.get("response", {}).get("results", [])

def search_bills_by_year(client: OpenLegislationAPI, year: str,
                        page_size: int = 20) -> List[Dict]:
    """
    Search for bills by year.
    
    Args:
        client: OpenLegislationAPI client instance
        year: Year to search for
        page_size: Number of results per page
        
    Returns:
        List of bills
    """
    term = f"year:{year}"
    response = client.search(term, page_size=page_size)
    return response.get("response", {}).get("results", [])

def get_bill_actions(client: OpenLegislationAPI, bill_id: str, year: str) -> List[BillAction]:
    """
    Get actions for a specific bill.
    
    Args:
        client: OpenLegislationAPI client instance
        bill_id: Bill ID
        year: Year
        
    Returns:
        List of bill actions
    """
    response = client.get_bill(bill_id, year)
    bill_data = response.get("response", {}).get("results", [{}])[0].get("data", {})
    actions_data = bill_data.get("actions", [])
    
    actions = []
    for action_data in actions_data:
        actions.append(BillAction(
            date=action_data.get("date", ""),
            text=action_data.get("text", "")
        ))
    
    return actions

# Example usage
if __name__ == "__main__":
    # Example of how to use the OpenLegislation API helper functions
    # client = create_openlegislation_client()
    # 
    # # Search for bills by sponsor
    # bills = search_bills_by_sponsor(client, "MAZIARZ")
    # print(f"Found {len(bills)} bills sponsored by MAZIARZ")
    # 
    # # Search for bills by year
    # bills_2011 = search_bills_by_year(client, "2011")
    # print(f"Found {len(bills_2011)} bills from 2011")
    # 
    # # Get a specific bill
    # bill = client.get_bill("S607", "2011")
    # print(f"Retrieved bill: {bill.get('response', {}).get('results', [{}])[0].get('data', {}).get('title', '')}")
    pass