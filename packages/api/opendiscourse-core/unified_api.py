"""
Unified API Suite for Government Legislative Data

This module provides a unified interface for accessing legislative data from
multiple government sources including OpenStates, Congress.gov, GovInfo.gov,
and OpenLegislation.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# Import existing API clients
from .openstates_api import (
    OpenStatesAPI, Jurisdiction as OpenStatesJurisdiction, 
    Person as OpenStatesPerson, Bill as OpenStatesBill,
    Committee as OpenStatesCommittee, Event as OpenEventsEvent,
    create_openstates_client, get_all_jurisdictions, 
    get_all_people_for_jurisdiction, get_all_bills_for_jurisdiction
)
from .congress_gov_api import (
    CongressGovAPI, ProPublicaCongressAPI, Member as CongressMember,
    Bill as CongressBill, Vote as CongressVote,
    create_congress_gov_client, create_propublica_client
)
from .openlegislation_api import (
    OpenLegislationAPI, Bill as OpenLegislationBill,
    Meeting as OpenLegislationMeeting, Calendar as OpenLegislationCalendar,
    Transcript as OpenLegislationTranscript,
    create_openlegislation_client
)
from .govinfo_api import (
    GovInfoAPI, create_govinfo_client
)

# Unified data models
@dataclass
class UnifiedJurisdiction:
    """Unified model for legislative jurisdictions"""
    id: str
    name: str
    classification: str
    url: Optional[str]
    source: str  # 'openstates', 'congressgov', etc.
    data: Dict[str, Any]  # Original data from source

@dataclass
class UnifiedPerson:
    """Unified model for legislative people"""
    id: str
    name: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    party: Optional[str]
    state: Optional[str]
    chamber: Optional[str]
    source: str  # 'openstates', 'congressgov', etc.
    data: Dict[str, Any]  # Original data from source

@dataclass
class UnifiedBill:
    """Unified model for legislative bills"""
    id: str
    bill_number: str
    title: str
    description: Optional[str]
    jurisdiction: Optional[str]
    session: Optional[str]
    introduced_date: Optional[str]
    sponsor: Optional[str]
    status: Optional[str]
    source: str  # 'openstates', 'congressgov', 'openlegislation', etc.
    data: Dict[str, Any]  # Original data from source

@dataclass
class UnifiedCommittee:
    """Unified model for legislative committees"""
    id: str
    name: str
    chamber: Optional[str]
    jurisdiction: Optional[str]
    source: str  # 'openstates', 'congressgov', etc.
    data: Dict[str, Any]  # Original data from source

@dataclass
class UnifiedVote:
    """Unified model for legislative votes"""
    id: str
    bill_id: Optional[str]
    person_id: Optional[str]
    vote_type: Optional[str]
    vote_date: Optional[str]
    position: Optional[str]
    source: str  # 'openstates', 'congressgov', 'openlegislation', etc.
    data: Dict[str, Any]  # Original data from source

@dataclass
class UnifiedMeeting:
    """Unified model for legislative meetings"""
    id: str
    committee_name: str
    meeting_date: Optional[str]
    location: Optional[str]
    source: str  # 'openlegislation', etc.
    data: Dict[str, Any]  # Original data from source

@dataclass
class UnifiedCalendar:
    """Unified model for legislative calendars"""
    id: str
    calendar_type: str
    date: Optional[str]
    source: str  # 'openlegislation', etc.
    data: Dict[str, Any]  # Original data from source

@dataclass
class UnifiedTranscript:
    """Unified model for legislative transcripts"""
    id: str
    session_type: str
    date: Optional[str]
    location: Optional[str]
    source: str  # 'openlegislation', etc.
    data: Dict[str, Any]  # Original data from source

class UnifiedAPISuite:
    """Unified API suite for accessing government legislative data from multiple sources."""
    
    def __init__(self, 
                 openstates_api_key: Optional[str] = None,
                 congressgov_api_key: Optional[str] = None,
                 propublica_api_key: Optional[str] = None,
                 openlegislation_api_key: Optional[str] = None):
        """
        Initialize the unified API suite.
        
        Args:
            openstates_api_key: API key for OpenStates
            congressgov_api_key: API key for Congress.gov
            propublica_api_key: API key for ProPublica Congress API
            openlegislation_api_key: API key for OpenLegislation
        """
        # Initialize API clients
        self.openstates_client = None
        self.congressgov_client = None
        self.propublica_client = None
        self.openlegislation_client = None
        self.govinfo_client = None
        
        # Initialize clients if API keys are provided
        if openstates_api_key or os.getenv("OPENSTATES_API_KEY"):
            self.openstates_client = create_openstates_client(openstates_api_key)
            
        if congressgov_api_key or os.getenv("CONGRESS_GOV_API_KEY"):
            self.congressgov_client = create_congress_gov_client(congressgov_api_key)
            
        if propublica_api_key or os.getenv("PROPUBLICA_API_KEY"):
            self.propublica_client = create_propublica_client(propublica_api_key)
            
        if openlegislation_api_key or os.getenv("OPENLEGISLATION_API_KEY"):
            self.openlegislation_client = create_openlegislation_client(openlegislation_api_key)
            
        # GovInfo doesn't require API keys
        self.govinfo_client = create_govinfo_client()
    
    # Jurisdiction methods
    def get_all_jurisdictions(self) -> List[UnifiedJurisdiction]:
        """
        Get all jurisdictions from all available sources.
        
        Returns:
            List of unified jurisdiction objects
        """
        jurisdictions = []
        
        # Get from OpenStates if available
        if self.openstates_client:
            try:
                openstates_jurisdictions = get_all_jurisdictions(self.openstates_client)
                for jur in openstates_jurisdictions:
                    jurisdictions.append(UnifiedJurisdiction(
                        id=jur.id,
                        name=jur.name,
                        classification=jur.classification,
                        url=jur.url,
                        source='openstates',
                        data=asdict(jur)
                    ))
            except Exception as e:
                print(f"Error fetching OpenStates jurisdictions: {e}")
        
        # Get from Congress.gov if available
        if self.congressgov_client:
            try:
                # Congress.gov doesn't have jurisdictions in the same sense,
                # but we can create a federal jurisdiction
                jurisdictions.append(UnifiedJurisdiction(
                    id='us',
                    name='United States',
                    classification='country',
                    url='https://congress.gov',
                    source='congressgov',
                    data={'congresses': []}  # Would need to fetch congress data
                ))
            except Exception as e:
                print(f"Error creating federal jurisdiction: {e}")
        
        return jurisdictions
    
    # Person methods
    def get_all_people(self, jurisdiction_id: Optional[str] = None) -> List[UnifiedPerson]:
        """
        Get all people from all available sources.
        
        Args:
            jurisdiction_id: Optional jurisdiction ID to filter by
            
        Returns:
            List of unified person objects
        """
        people = []
        
        # Get from OpenStates if available
        if self.openstates_client and jurisdiction_id:
            try:
                openstates_people = get_all_people_for_jurisdiction(
                    self.openstates_client, jurisdiction_id)
                for person in openstates_people:
                    people.append(UnifiedPerson(
                        id=person.id,
                        name=person.name,
                        first_name=person.given_name,
                        last_name=person.family_name,
                        email=person.email,
                        party=person.party[0]['name'] if person.party else None,
                        state=None,  # Would need to extract from jurisdiction
                        chamber=None,  # Would need to extract from roles
                        source='openstates',
                        data=asdict(person)
                    ))
            except Exception as e:
                print(f"Error fetching OpenStates people: {e}")
        
        # Get from Congress.gov if available
        if self.congressgov_client or self.propublica_client:
            try:
                # This would require knowing which congress and chamber
                # For now, we'll skip this as it requires specific parameters
                pass
            except Exception as e:
                print(f"Error fetching Congress.gov people: {e}")
        
        return people
    
    # Bill methods
    def get_all_bills(self, jurisdiction_id: Optional[str] = None) -> List[UnifiedBill]:
        """
        Get all bills from all available sources.
        
        Args:
            jurisdiction_id: Optional jurisdiction ID to filter by
            
        Returns:
            List of unified bill objects
        """
        bills = []
        
        # Get from OpenStates if available
        if self.openstates_client and jurisdiction_id:
            try:
                openstates_bills = get_all_bills_for_jurisdiction(
                    self.openstates_client, jurisdiction_id)
                for bill in openstates_bills:
                    bills.append(UnifiedBill(
                        id=bill.id,
                        bill_number=bill.identifier,
                        title=bill.title,
                        description=None,  # No summary field in OpenStates Bill
                        jurisdiction=bill.jurisdiction.get('name') if bill.jurisdiction else None,
                        session=bill.session,
                        introduced_date=None,  # Not directly available in OpenStates Bill
                        sponsor=bill.sponsorships[0]['name'] if bill.sponsorships else None,
                        status=None,  # Would need to determine from actions
                        source='openstates',
                        data=asdict(bill)
                    ))
            except Exception as e:
                print(f"Error fetching OpenStates bills: {e}")
        
        # Get from Congress.gov if available
        if self.congressgov_client:
            try:
                # This would require specific congress/chamber parameters
                # For now, we'll skip this
                pass
            except Exception as e:
                print(f"Error fetching Congress.gov bills: {e}")
        
        # Get from OpenLegislation if available
        if self.openlegislation_client:
            try:
                # OpenLegislation requires specific bill ID and year
                # For now, we'll skip this
                pass
            except Exception as e:
                print(f"Error fetching OpenLegislation bills: {e}")
        
        return bills
    
    # Search methods
    def search_bills(self, query: str, jurisdiction: Optional[str] = None) -> List[UnifiedBill]:
        """
        Search for bills across all available sources.
        
        Args:
            query: Search query
            jurisdiction: Optional jurisdiction to limit search
            
        Returns:
            List of unified bill objects matching the query
        """
        bills = []
        
        # Search in OpenStates if available
        if self.openstates_client:
            try:
                response = self.openstates_client.get_bills(search=query, jurisdiction=jurisdiction)
                results = response.get('results', [])
                for bill_data in results:
                    bill = OpenStatesBill(**bill_data)
                    bills.append(UnifiedBill(
                        id=bill.id,
                        bill_number=bill.identifier,
                        title=bill.title,
                        description=None,
                        jurisdiction=bill.jurisdiction.get('name') if bill.jurisdiction else None,
                        session=bill.session,
                        introduced_date=None,
                        sponsor=bill.sponsorships[0]['name'] if bill.sponsorships else None,
                        status=None,
                        source='openstates',
                        data=bill_data
                    ))
            except Exception as e:
                print(f"Error searching OpenStates bills: {e}")
        
        # Search in Congress.gov if available
        if self.congressgov_client:
            try:
                # This would require implementing search functionality
                # For now, we'll skip this
                pass
            except Exception as e:
                print(f"Error searching Congress.gov bills: {e}")
        
        # Search in OpenLegislation if available
        if self.openlegislation_client:
            try:
                response = self.openlegislation_client.search(query)
                results = response.get('response', {}).get('results', [])
                for result in results:
                    bill_data = result.get('data', {})
                    # Note: This is a simplified representation
                    bills.append(UnifiedBill(
                        id=result.get('oid', ''),
                        bill_number=bill_data.get('senateBillNo', ''),
                        title=bill_data.get('title', ''),
                        description=bill_data.get('summary', ''),
                        jurisdiction='New York State',  # OpenLegislation is NY-specific
                        session=bill_data.get('year', ''),
                        introduced_date=None,
                        sponsor=bill_data.get('sponsor', {}).get('fullname', '') if bill_data.get('sponsor') else None,
                        status=None,
                        source='openlegislation',
                        data=bill_data
                    ))
            except Exception as e:
                print(f"Error searching OpenLegislation bills: {e}")
        
        return bills
    
    # Utility methods
    def get_data_source_info(self) -> Dict[str, bool]:
        """
        Get information about which data sources are configured.
        
        Returns:
            Dictionary indicating which sources are available
        """
        return {
            'openstates': self.openstates_client is not None,
            'congressgov': self.congressgov_client is not None,
            'propublica': self.propublica_client is not None,
            'openlegislation': self.openlegislation_client is not None,
            'govinfo': self.govinfo_client is not None
        }
    
    def save_results_to_file(self, data: List[Any], filename: str) -> None:
        """
        Save API results to a JSON file.
        
        Args:
            data: Data to save (list of unified objects)
            filename: Name of the file to save to
        """
        # Convert dataclass objects to dictionaries
        data_dicts = []
        for item in data:
            if hasattr(item, '__dataclass_fields__'):
                data_dicts.append(asdict(item))
            else:
                data_dicts.append(item)
        
        with open(filename, 'w') as f:
            json.dump(data_dicts, f, indent=2)

# Factory functions for creating the unified API suite
def create_unified_api_suite(
    openstates_api_key: Optional[str] = None,
    congressgov_api_key: Optional[str] = None,
    propublica_api_key: Optional[str] = None,
    openlegislation_api_key: Optional[str] = None
) -> UnifiedAPISuite:
    """
    Create a unified API suite instance.
    
    Args:
        openstates_api_key: API key for OpenStates
        congressgov_api_key: API key for Congress.gov
        propublica_api_key: API key for ProPublica Congress API
        openlegislation_api_key: API key for OpenLegislation
        
    Returns:
        UnifiedAPISuite instance
    """
    return UnifiedAPISuite(
        openstates_api_key=openstates_api_key,
        congressgov_api_key=congressgov_api_key,
        propublica_api_key=propublica_api_key,
        openlegislation_api_key=openlegislation_api_key
    )

# Example usage
if __name__ == "__main__":
    # Example of how to use the unified API suite
    # suite = create_unified_api_suite(
    #     openstates_api_key="your-openstates-key",
    #     congressgov_api_key="your-congressgov-key",
    #     openlegislation_api_key="your-openlegislation-key"
    # )
    # 
    # # Get all jurisdictions
    # jurisdictions = suite.get_all_jurisdictions()
    # print(f"Found {len(jurisdictions)} jurisdictions")
    # 
    # # Search for bills
    # bills = suite.search_bills("renewable energy")
    # print(f"Found {len(bills)} bills matching query")
    # 
    # # Check which sources are configured
    # sources = suite.get_data_source_info()
    # print(f"Configured sources: {sources}")
    pass