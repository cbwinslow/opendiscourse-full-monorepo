"""
Data Transformation Pipeline Module

This module provides functions for transforming and unifying data from different
government data sources into a common format.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add the project root to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.data_processing.data_validator import DataValidator, DataCleaner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    """Transforms data from different sources into a unified format."""
    
    def __init__(self):
        """Initialize the data transformer."""
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
    
    def transform_openstates_person(self, openstates_person: Dict) -> Dict:
        """
        Transform OpenStates person data to unified format.
        
        Args:
            openstates_person: OpenStates person data
            
        Returns:
            Unified person data
        """
        transformed = {}
        
        # Basic person information
        transformed['id'] = f"openstates-{openstates_person.get('id', '')}"
        transformed['name'] = openstates_person.get('name', '')
        transformed['given_name'] = openstates_person.get('given_name', '')
        transformed['family_name'] = openstates_person.get('family_name', '')
        transformed['email'] = openstates_person.get('email', '')
        transformed['gender'] = openstates_person.get('gender', '')
        transformed['birth_date'] = openstates_person.get('birth_date', '')
        transformed['biography'] = openstates_person.get('biography', '')
        transformed['image_url'] = openstates_person.get('image', '')
        
        # Source information
        sources = openstates_person.get('sources', [])
        if sources:
            transformed['source_url'] = sources[0].get('url', '')
            transformed['source_note'] = sources[0].get('note', '')
        
        # Party affiliation
        parties = openstates_person.get('party', [])
        if parties:
            transformed['party'] = parties[0].get('name', '')
        
        # Roles
        transformed['roles'] = []
        for role in openstates_person.get('roles', []):
            transformed_role = {
                'type': role.get('type', ''),
                'district': role.get('district', ''),
                'jurisdiction_id': f"openstates-{role.get('jurisdiction', '')}",
                'start_date': role.get('start_date', ''),
                'end_date': role.get('end_date', '')
            }
            transformed['roles'].append(transformed_role)
        
        # Social media links
        links = openstates_person.get('links', [])
        transformed['social_media'] = {}
        for link in links:
            url = link.get('url', '')
            if 'twitter.com' in url:
                transformed['social_media']['twitter'] = url
            elif 'facebook.com' in url:
                transformed['social_media']['facebook'] = url
            elif 'youtube.com' in url:
                transformed['social_media']['youtube'] = url
        
        return self.validator.validate_person(transformed)
    
    def transform_congress_gov_person(self, congress_person: Dict) -> Dict:
        """
        Transform Congress.gov person data to unified format.
        
        Args:
            congress_person: Congress.gov person data
            
        Returns:
            Unified person data
        """
        transformed = {}
        
        # Basic person information
        transformed['id'] = f"congressgov-{congress_person.get('id', '')}"
        transformed['name'] = f"{congress_person.get('first_name', '')} {congress_person.get('last_name', '')}".strip()
        transformed['given_name'] = congress_person.get('first_name', '')
        transformed['family_name'] = congress_person.get('last_name', '')
        transformed['email'] = congress_person.get('email', '')
        transformed['gender'] = congress_person.get('gender', '')
        transformed['birth_date'] = congress_person.get('date_of_birth', '')
        transformed['biography'] = ''  # Not directly available
        
        # Contact information
        transformed['office'] = congress_person.get('office', '')
        transformed['phone'] = congress_person.get('phone', '')
        transformed['fax'] = congress_person.get('fax', '')
        
        # Party affiliation
        transformed['party'] = congress_person.get('party', '')
        
        # Term information
        transformed['roles'] = [{
            'type': congress_person.get('title', '').lower().replace(' ', '-'),
            'district': congress_person.get('district', ''),
            'jurisdiction_id': 'ocd-jurisdiction/country:us/government',  # Federal
            'start_date': '',  # Not directly available
            'end_date': '',    # Not directly available
            'state': congress_person.get('state', ''),
            'senate_class': congress_person.get('senate_class', ''),
            'state_rank': congress_person.get('state_rank', '')
        }]
        
        # Social media links
        transformed['social_media'] = {
            'twitter': congress_person.get('twitter_account', ''),
            'facebook': congress_person.get('facebook_account', ''),
            'youtube': congress_person.get('youtube_account', '')
        }
        
        # Website and contact
        transformed['website'] = congress_person.get('url', '')
        transformed['contact_form'] = congress_person.get('contact_form', '')
        
        return self.validator.validate_person(transformed)
    
    def transform_openlegislation_person(self, openlegislation_person: Dict) -> Dict:
        """
        Transform OpenLegislation person data to unified format.
        
        Args:
            openlegislation_person: OpenLegislation person data
            
        Returns:
            Unified person data
        """
        transformed = {}
        
        # For OpenLegislation, person data is often embedded in other records
        # This is a simplified transformation
        sponsor = openlegislation_person.get('sponsor', {})
        if sponsor:
            transformed['id'] = f"openlegislation-sponsor-{sponsor.get('fullname', '').replace(' ', '-')}"
            transformed['name'] = sponsor.get('fullname', '')
            transformed['party'] = ''  # Not directly available
            transformed['roles'] = []  # Not directly available
        
        return transformed
    
    def transform_openstates_bill(self, openstates_bill: Dict) -> Dict:
        """
        Transform OpenStates bill data to unified format.
        
        Args:
            openstates_bill: OpenStates bill data
            
        Returns:
            Unified bill data
        """
        transformed = {}
        
        # Basic bill information
        transformed['id'] = f"openstates-{openstates_bill.get('id', '')}"
        transformed['session_id'] = openstates_bill.get('session', '')
        transformed['jurisdiction_id'] = f"openstates-{openstates_bill.get('jurisdiction', {}).get('id', '')}" if openstates_bill.get('jurisdiction') else ''
        transformed['identifier'] = openstates_bill.get('identifier', '')
        transformed['title'] = openstates_bill.get('title', '')
        transformed['classification'] = openstates_bill.get('classification', [])
        transformed['subject'] = openstates_bill.get('subject', [])
        
        # Extras
        transformed['extras'] = {
            'openstates_url': openstates_bill.get('openstates_url', ''),
            'created_at': openstates_bill.get('created_at', ''),
            'updated_at': openstates_bill.get('updated_at', '')
        }
        
        # Sponsors
        transformed['sponsors'] = []
        for sponsorship in openstates_bill.get('sponsorships', []):
            sponsor = {
                'name': sponsorship.get('name', ''),
                'entity_type': sponsorship.get('entity_type', ''),
                'primary': sponsorship.get('primary', False),
                'classification': sponsorship.get('classification', '')
            }
            transformed['sponsors'].append(sponsor)
        
        # Actions
        transformed['actions'] = []
        for action in openstates_bill.get('actions', []):
            transformed_action = {
                'organization': action.get('organization', {}).get('name', '') if action.get('organization') else '',
                'description': action.get('description', ''),
                'date': action.get('date', ''),
                'classification': action.get('classification', [])
            }
            transformed['actions'].append(transformed_action)
        
        # Versions
        transformed['versions'] = []
        for version in openstates_bill.get('versions', []):
            for link in version.get('links', []):
                transformed_version = {
                    'note': version.get('note', ''),
                    'date': version.get('date', ''),
                    'url': link.get('url', ''),
                    'media_type': link.get('media_type', '')
                }
                transformed['versions'].append(transformed_version)
        
        # Documents
        transformed['documents'] = []
        for document in openstates_bill.get('documents', []):
            for link in document.get('links', []):
                transformed_document = {
                    'note': document.get('note', ''),
                    'date': document.get('date', ''),
                    'url': link.get('url', ''),
                    'media_type': link.get('media_type', '')
                }
                transformed['documents'].append(transformed_document)
        
        return self.validator.validate_bill(transformed)
    
    def transform_congress_gov_bill(self, congress_bill: Dict) -> Dict:
        """
        Transform Congress.gov bill data to unified format.
        
        Args:
            congress_bill: Congress.gov bill data
            
        Returns:
            Unified bill data
        """
        transformed = {}
        
        # Basic bill information
        transformed['id'] = f"congressgov-{congress_bill.get('bill_id', '')}"
        transformed['jurisdiction_id'] = 'ocd-jurisdiction/country:us/government'  # Federal
        transformed['identifier'] = congress_bill.get('number', '')
        transformed['title'] = congress_bill.get('title', '')
        transformed['classification'] = [congress_bill.get('bill_type', '')] if congress_bill.get('bill_type') else []
        transformed['subject'] = [congress_bill.get('primary_subject', '')] if congress_bill.get('primary_subject') else []
        
        # Extras
        transformed['extras'] = {
            'sponsor_id': congress_bill.get('sponsor_id', ''),
            'cosponsors': congress_bill.get('cosponsors', 0),
            'committees': congress_bill.get('committees', ''),
            'summary': congress_bill.get('summary', ''),
            'summary_short': congress_bill.get('summary_short', ''),
            'congressdotgov_url': congress_bill.get('congressdotgov_url', ''),
            'govtrack_url': congress_bill.get('govtrack_url', ''),
            'introduced_date': congress_bill.get('introduced_date', ''),
            'latest_major_action_date': congress_bill.get('latest_major_action_date', ''),
            'latest_major_action': congress_bill.get('latest_major_action', '')
        }
        
        # Sponsors
        transformed['sponsors'] = []
        sponsor_id = congress_bill.get('sponsor_id')
        if sponsor_id:
            sponsor = {
                'person_id': f"congressgov-{sponsor_id}",
                'entity_type': 'person',
                'primary': True,
                'classification': 'primary'
            }
            transformed['sponsors'].append(sponsor)
        
        return self.validator.validate_bill(transformed)
    
    def transform_openlegislation_bill(self, openlegislation_bill: Dict) -> Dict:
        """
        Transform OpenLegislation bill data to unified format.
        
        Args:
            openlegislation_bill: OpenLegislation bill data
            
        Returns:
            Unified bill data
        """
        bill_data = openlegislation_bill.get('data', {})
        if not bill_data:
            return {}
        
        transformed = {}
        
        # Basic bill information
        senate_bill_no = bill_data.get('senateBillNo', '')
        year = bill_data.get('year', '')
        transformed['id'] = f"openlegislation-{year}-{senate_bill_no}"
        transformed['session_id'] = f"nys-{year}"
        transformed['jurisdiction_id'] = 'ocd-jurisdiction/country:us/state:ny/government'  # NY State
        transformed['identifier'] = senate_bill_no
        transformed['title'] = bill_data.get('title', '')
        transformed['classification'] = ['bill']
        
        # Extras
        transformed['extras'] = {
            'lawSection': bill_data.get('lawSection', ''),
            'sameAs': bill_data.get('sameAs', ''),
            'summary': bill_data.get('summary', ''),
            'currentCommittee': bill_data.get('currentCommittee', ''),
            'fulltext': bill_data.get('fulltext', ''),
            'memo': bill_data.get('memo', ''),
            'law': bill_data.get('law', '')
        }
        
        # Sponsor
        sponsor = bill_data.get('sponsor', {})
        if sponsor:
            transformed['sponsors'] = [{
                'name': sponsor.get('fullname', ''),
                'entity_type': 'person',
                'primary': True,
                'classification': 'primary'
            }]
        
        # Actions
        transformed['actions'] = []
        for action in bill_data.get('actions', []):
            transformed_action = {
                'description': action.get('text', ''),
                'date': action.get('date', ''),
                'classification': []
            }
            transformed['actions'].append(transformed_action)
        
        # Votes
        transformed['votes'] = []
        for vote in bill_data.get('votes', []):
            transformed_vote = {
                'motion_text': vote.get('description', ''),
                'result': 'pass' if vote.get('ayes') and len(vote.get('ayes', [])) > len(vote.get('nays', [])) else 'fail',
                'date': vote.get('voteDate', ''),
                'organization_name': 'New York State Senate'
            }
            transformed['votes'].append(transformed_vote)
        
        return self.validator.validate_bill(transformed)
    
    def unify_people_data(self, people_data: List[Dict], source: str) -> List[Dict]:
        """
        Unify people data from a specific source.
        
        Args:
            people_data: List of people data from a source
            source: Source identifier ('openstates', 'congressgov', 'openlegislation')
            
        Returns:
            List of unified people data
        """
        unified_people = []
        
        for person in people_data:
            try:
                if source == 'openstates':
                    unified_person = self.transform_openstates_person(person)
                elif source == 'congressgov':
                    unified_person = self.transform_congress_gov_person(person)
                elif source == 'openlegislation':
                    unified_person = self.transform_openlegislation_person(person)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue
                
                if unified_person:
                    unified_people.append(unified_person)
                    
            except Exception as e:
                logger.error(f"Error transforming person data from {source}: {e}")
                continue
        
        # Clean and deduplicate
        cleaned_people = self.cleaner.clean_person_data(unified_people)
        unique_people = self.cleaner.deduplicate_people(cleaned_people)
        
        return unique_people
    
    def unify_bills_data(self, bills_data: List[Dict], source: str) -> List[Dict]:
        """
        Unify bills data from a specific source.
        
        Args:
            bills_data: List of bills data from a source
            source: Source identifier ('openstates', 'congressgov', 'openlegislation')
            
        Returns:
            List of unified bills data
        """
        unified_bills = []
        
        for bill in bills_data:
            try:
                if source == 'openstates':
                    unified_bill = self.transform_openstates_bill(bill)
                elif source == 'congressgov':
                    unified_bill = self.transform_congress_gov_bill(bill)
                elif source == 'openlegislation':
                    unified_bill = self.transform_openlegislation_bill(bill)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue
                
                if unified_bill:
                    unified_bills.append(unified_bill)
                    
            except Exception as e:
                logger.error(f"Error transforming bill data from {source}: {e}")
                continue
        
        # Clean data
        cleaned_bills = self.cleaner.clean_bill_data(unified_bills)
        
        return cleaned_bills
    
    def standardize_jurisdiction(self, jurisdiction_data: Dict, source: str) -> Dict:
        """
        Standardize jurisdiction data from a specific source.
        
        Args:
            jurisdiction_data: Jurisdiction data
            source: Source identifier
            
        Returns:
            Standardized jurisdiction data
        """
        standardized = jurisdiction_data.copy()
        
        # Add source prefix to ID
        if 'id' in standardized:
            standardized['id'] = f"{source}-{standardized['id']}"
        
        # Standardize classification
        if 'classification' in standardized:
            classification = standardized['classification']
            if classification == 'state':
                standardized['classification'] = 'state'
            elif classification == 'country':
                standardized['classification'] = 'federal'
        
        return self.validator.validate_jurisdiction(standardized)

# Example usage
if __name__ == "__main__":
    # Example of how to use the data transformer
    # transformer = DataTransformer()
    # 
    # # Transform sample OpenStates person data
    # openstates_person = {
    #     'id': 'ocd-person/123',
    #     'name': 'John Doe',
    #     'given_name': 'John',
    #     'family_name': 'Doe',
    #     'email': 'john.doe@example.com',
    #     'party': [{'name': 'Democratic'}],
    #     'roles': [{
    #         'type': 'lower',
    #         'district': '10',
    #         'jurisdiction': 'ocd-jurisdiction/country:us/state:ca/government'
    #     }]
    # }
    # 
    # unified_person = transformer.transform_openstates_person(openstates_person)
    # print(f"Unified person: {unified_person}")
    pass