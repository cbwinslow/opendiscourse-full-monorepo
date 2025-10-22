"""
Data Validation and Cleaning Module

This module provides functions for validating and cleaning government data
collected from various sources.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    """Validates and cleans government data."""
    
    def __init__(self):
        """Initialize the data validator."""
        pass
    
    def validate_jurisdiction(self, jurisdiction_data: Dict) -> Dict:
        """
        Validate jurisdiction data.
        
        Args:
            jurisdiction_data: Jurisdiction data dictionary
            
        Returns:
            Validated and cleaned jurisdiction data
        """
        validated = {}
        
        # Validate ID
        jurisdiction_id = jurisdiction_data.get('id')
        if not jurisdiction_id or not isinstance(jurisdiction_id, str):
            raise ValueError("Jurisdiction ID is required and must be a string")
        validated['id'] = jurisdiction_id.strip()
        
        # Validate name
        name = jurisdiction_data.get('name')
        if not name or not isinstance(name, str):
            raise ValueError("Jurisdiction name is required and must be a string")
        validated['name'] = name.strip()
        
        # Validate classification
        classification = jurisdiction_data.get('classification')
        if classification and isinstance(classification, str):
            validated['classification'] = classification.strip().lower()
        
        # Validate division information
        division_id = jurisdiction_data.get('division_id')
        if division_id and isinstance(division_id, str):
            validated['division_id'] = division_id.strip()
            
        division_name = jurisdiction_data.get('division_name')
        if division_name and isinstance(division_name, str):
            validated['division_name'] = division_name.strip()
        
        # Validate URL
        url = jurisdiction_data.get('url')
        if url and isinstance(url, str):
            validated['url'] = self._clean_url(url)
        
        return validated
    
    def validate_person(self, person_data: Dict) -> Dict:
        """
        Validate person data.
        
        Args:
            person_data: Person data dictionary
            
        Returns:
            Validated and cleaned person data
        """
        validated = {}
        
        # Validate ID
        person_id = person_data.get('id')
        if not person_id or not isinstance(person_id, str):
            raise ValueError("Person ID is required and must be a string")
        validated['id'] = person_id.strip()
        
        # Validate name
        name = person_data.get('name')
        if not name or not isinstance(name, str):
            raise ValueError("Person name is required and must be a string")
        validated['name'] = self._clean_name(name)
        
        # Validate given and family names
        given_name = person_data.get('given_name')
        if given_name and isinstance(given_name, str):
            validated['given_name'] = given_name.strip()
            
        family_name = person_data.get('family_name')
        if family_name and isinstance(family_name, str):
            validated['family_name'] = family_name.strip()
        
        # Validate email
        email = person_data.get('email')
        if email and isinstance(email, str):
            cleaned_email = email.strip().lower()
            if self._is_valid_email(cleaned_email):
                validated['email'] = cleaned_email
            else:
                logger.warning(f"Invalid email format for person {person_id}: {email}")
        
        # Validate gender
        gender = person_data.get('gender')
        if gender and isinstance(gender, str):
            validated['gender'] = gender.strip().capitalize()
        
        # Validate birth date
        birth_date = person_data.get('birth_date')
        if birth_date:
            validated['birth_date'] = self._parse_date(birth_date)
        
        # Validate image URL
        image_url = person_data.get('image_url')
        if image_url and isinstance(image_url, str):
            validated['image_url'] = self._clean_url(image_url)
        
        # Validate source URL
        source_url = person_data.get('source_url')
        if source_url and isinstance(source_url, str):
            validated['source_url'] = self._clean_url(source_url)
        
        return validated
    
    def validate_bill(self, bill_data: Dict) -> Dict:
        """
        Validate bill data.
        
        Args:
            bill_data: Bill data dictionary
            
        Returns:
            Validated and cleaned bill data
        """
        validated = {}
        
        # Validate ID
        bill_id = bill_data.get('id')
        if not bill_id or not isinstance(bill_id, str):
            raise ValueError("Bill ID is required and must be a string")
        validated['id'] = bill_id.strip()
        
        # Validate session ID
        session_id = bill_data.get('session_id')
        if session_id and isinstance(session_id, str):
            validated['session_id'] = session_id.strip()
        
        # Validate jurisdiction ID
        jurisdiction_id = bill_data.get('jurisdiction_id')
        if jurisdiction_id and isinstance(jurisdiction_id, str):
            validated['jurisdiction_id'] = jurisdiction_id.strip()
        
        # Validate identifier
        identifier = bill_data.get('identifier')
        if identifier and isinstance(identifier, str):
            validated['identifier'] = identifier.strip()
        
        # Validate title
        title = bill_data.get('title')
        if title and isinstance(title, str):
            validated['title'] = title.strip()
        
        # Validate classification
        classification = bill_data.get('classification')
        if classification:
            if isinstance(classification, list):
                validated['classification'] = [c.strip().lower() for c in classification if isinstance(c, str)]
            elif isinstance(classification, str):
                validated['classification'] = [classification.strip().lower()]
        
        # Validate subject
        subject = bill_data.get('subject')
        if subject:
            if isinstance(subject, list):
                validated['subject'] = [s.strip() for s in subject if isinstance(s, str)]
            elif isinstance(subject, str):
                validated['subject'] = [subject.strip()]
        
        # Validate extras (JSON data)
        extras = bill_data.get('extras')
        if extras:
            try:
                if isinstance(extras, str):
                    validated['extras'] = json.loads(extras)
                else:
                    validated['extras'] = extras
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in extras for bill {bill_id}")
                validated['extras'] = {}
        
        # Validate URLs
        openstates_url = bill_data.get('openstates_url')
        if openstates_url and isinstance(openstates_url, str):
            validated['openstates_url'] = self._clean_url(openstates_url)
            
        congress_gov_url = bill_data.get('congress_gov_url')
        if congress_gov_url and isinstance(congress_gov_url, str):
            validated['congress_gov_url'] = self._clean_url(congress_gov_url)
            
        govinfo_url = bill_data.get('govinfo_url')
        if govinfo_url and isinstance(govinfo_url, str):
            validated['govinfo_url'] = self._clean_url(govinfo_url)
        
        return validated
    
    def validate_vote(self, vote_data: Dict) -> Dict:
        """
        Validate vote data.
        
        Args:
            vote_data: Vote data dictionary
            
        Returns:
            Validated and cleaned vote data
        """
        validated = {}
        
        # Validate ID
        vote_id = vote_data.get('id')
        if not vote_id or not isinstance(vote_id, str):
            raise ValueError("Vote ID is required and must be a string")
        validated['id'] = vote_id.strip()
        
        # Validate bill ID
        bill_id = vote_data.get('bill_id')
        if bill_id and isinstance(bill_id, str):
            validated['bill_id'] = bill_id.strip()
        
        # Validate motion text
        motion_text = vote_data.get('motion_text')
        if motion_text and isinstance(motion_text, str):
            validated['motion_text'] = motion_text.strip()
        
        # Validate result
        result = vote_data.get('result')
        if result and isinstance(result, str):
            validated['result'] = result.strip().lower()
        
        # Validate date
        date = vote_data.get('date')
        if date:
            validated['date'] = self._parse_date(date)
        
        # Validate organization name
        organization_name = vote_data.get('organization_name')
        if organization_name and isinstance(organization_name, str):
            validated['organization_name'] = organization_name.strip()
        
        return validated
    
    def _clean_name(self, name: str) -> str:
        """
        Clean a person's name.
        
        Args:
            name: Name to clean
            
        Returns:
            Cleaned name
        """
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', name.strip())
        
        # Capitalize properly (simple approach)
        words = cleaned.split()
        capitalized_words = []
        for word in words:
            if word.lower() in ['ii', 'iii', 'iv', 'jr', 'sr']:
                capitalized_words.append(word.upper())
            else:
                capitalized_words.append(word.capitalize())
        
        return ' '.join(capitalized_words)
    
    def _clean_url(self, url: str) -> str:
        """
        Clean a URL.
        
        Args:
            url: URL to clean
            
        Returns:
            Cleaned URL
        """
        # Remove extra whitespace and normalize
        cleaned = url.strip()
        
        # Ensure it starts with http:// or https://
        if not cleaned.startswith(('http://', 'https://')):
            cleaned = 'https://' + cleaned
            
        return cleaned
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Check if an email is valid.
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _parse_date(self, date_input: Any) -> Optional[str]:
        """
        Parse a date from various formats.
        
        Args:
            date_input: Date input in various formats
            
        Returns:
            Date string in YYYY-MM-DD format or None if invalid
        """
        if not date_input:
            return None
            
        if isinstance(date_input, str):
            # Try common date formats
            formats = ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_input.strip(), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            # If we can't parse it, log a warning and return None
            logger.warning(f"Unable to parse date: {date_input}")
            return None
            
        elif isinstance(date_input, (datetime,)):
            return date_input.strftime('%Y-%m-%d')
            
        else:
            logger.warning(f"Invalid date type: {type(date_input)}")
            return None

class DataCleaner:
    """Cleans and standardizes government data."""
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.validator = DataValidator()
    
    def clean_jurisdiction_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Clean a list of jurisdiction data.
        
        Args:
            raw_data: List of raw jurisdiction data dictionaries
            
        Returns:
            List of cleaned jurisdiction data dictionaries
        """
        cleaned_data = []
        
        for jurisdiction in raw_data:
            try:
                validated = self.validator.validate_jurisdiction(jurisdiction)
                cleaned_data.append(validated)
            except ValueError as e:
                logger.warning(f"Skipping invalid jurisdiction data: {e}")
                continue
                
        return cleaned_data
    
    def clean_person_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Clean a list of person data.
        
        Args:
            raw_data: List of raw person data dictionaries
            
        Returns:
            List of cleaned person data dictionaries
        """
        cleaned_data = []
        
        for person in raw_data:
            try:
                validated = self.validator.validate_person(person)
                cleaned_data.append(validated)
            except ValueError as e:
                logger.warning(f"Skipping invalid person data: {e}")
                continue
                
        return cleaned_data
    
    def clean_bill_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Clean a list of bill data.
        
        Args:
            raw_data: List of raw bill data dictionaries
            
        Returns:
            List of cleaned bill data dictionaries
        """
        cleaned_data = []
        
        for bill in raw_data:
            try:
                validated = self.validator.validate_bill(bill)
                cleaned_data.append(validated)
            except ValueError as e:
                logger.warning(f"Skipping invalid bill data: {e}")
                continue
                
        return cleaned_data
    
    def clean_vote_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Clean a list of vote data.
        
        Args:
            raw_data: List of raw vote data dictionaries
            
        Returns:
            List of cleaned vote data dictionaries
        """
        cleaned_data = []
        
        for vote in raw_data:
            try:
                validated = self.validator.validate_vote(vote)
                cleaned_data.append(validated)
            except ValueError as e:
                logger.warning(f"Skipping invalid vote data: {e}")
                continue
                
        return cleaned_data
    
    def deduplicate_people(self, people_data: List[Dict]) -> List[Dict]:
        """
        Remove duplicate people based on ID.
        
        Args:
            people_data: List of person data dictionaries
            
        Returns:
            List of unique person data dictionaries
        """
        unique_people = {}
        
        for person in people_data:
            person_id = person.get('id')
            if person_id:
                # If we already have this person, keep the one with more complete data
                if person_id in unique_people:
                    existing = unique_people[person_id]
                    # Count non-null fields
                    existing_count = sum(1 for v in existing.values() if v is not None)
                    new_count = sum(1 for v in person.values() if v is not None)
                    
                    # Keep the record with more complete data
                    if new_count > existing_count:
                        unique_people[person_id] = person
                else:
                    unique_people[person_id] = person
        
        return list(unique_people.values())
    
    def standardize_party_names(self, party_name: str) -> str:
        """
        Standardize party names to consistent format.
        
        Args:
            party_name: Raw party name
            
        Returns:
            Standardized party name
        """
        if not party_name or not isinstance(party_name, str):
            return "Unknown"
            
        party_name = party_name.strip().lower()
        
        # Standardize common party names
        if party_name in ['democratic', 'democrat', 'd', 'dem']:
            return 'Democratic'
        elif party_name in ['republican', 'gop', 'r', 'rep']:
            return 'Republican'
        elif party_name in ['independent', 'ind', 'i']:
            return 'Independent'
        elif party_name in ['libertarian', 'lib']:
            return 'Libertarian'
        elif party_name in ['green', 'grn']:
            return 'Green'
        else:
            # Capitalize first letter of each word
            return ' '.join(word.capitalize() for word in party_name.split())

# Example usage
if __name__ == "__main__":
    # Example of how to use the data validation and cleaning modules
    # validator = DataValidator()
    # cleaner = DataCleaner()
    # 
    # # Validate some sample data
    # sample_person = {
    #     'id': 'person-123',
    #     'name': 'john doe',
    #     'email': 'JOHN.DOE@EXAMPLE.COM',
    #     'birth_date': '1980-01-15'
    # }
    # 
    # validated_person = validator.validate_person(sample_person)
    # print(f"Validated person: {validated_person}")
    # 
    # # Clean a list of people
    # raw_people = [
    #     {'id': 'person-1', 'name': 'john doe', 'email': 'john@example.com'},
    #     {'id': 'person-2', 'name': 'jane smith', 'email': 'invalid-email'},
    #     {'id': 'person-1', 'name': 'john doe jr', 'email': 'john.doe@example.com'}  # duplicate
    # ]
    # 
    # cleaned_people = cleaner.clean_person_data(raw_people)
    # unique_people = cleaner.deduplicate_people(cleaned_people)
    # print(f"Cleaned and deduplicated people: {unique_people}")
    pass