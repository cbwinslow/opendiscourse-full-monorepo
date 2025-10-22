"""
OpenStates Data Collection Module

This module handles the collection of data from the OpenStates API and stores it in the database.
"""

import os
import sys
import logging
from typing import Dict, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import Json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.opendiscourse.openstates_api import create_openstates_client, OpenStatesAPI
from opendiscourse.opendiscourse.unified_api import UnifiedAPISuite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenStatesDataCollector:
    """Handles collection of data from the OpenStates API."""
    
    def __init__(self, api_key: str, db_connection_string: str):
        """
        Initialize the OpenStates data collector.
        
        Args:
            api_key: OpenStates API key
            db_connection_string: PostgreSQL connection string
        """
        self.client = create_openstates_client(api_key)
        self.db_conn = psycopg2.connect(db_connection_string)
        self.db_conn.autocommit = False
        
    def collect_jurisdictions(self) -> None:
        """
        Collect all jurisdictions from OpenStates and store in database.
        """
        logger.info("Collecting jurisdictions from OpenStates")
        
        try:
            response = self.client.get_jurisdictions()
            jurisdictions = response.get('results', [])
            
            cursor = self.db_conn.cursor()
            
            for jurisdiction in jurisdictions:
                cursor.execute("""
                    INSERT INTO jurisdictions (id, name, classification, division_id, division_name, url, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        classification = EXCLUDED.classification,
                        division_id = EXCLUDED.division_id,
                        division_name = EXCLUDED.division_name,
                        url = EXCLUDED.url,
                        updated_at = EXCLUDED.updated_at
                """, (
                    jurisdiction.get('id'),
                    jurisdiction.get('name'),
                    jurisdiction.get('classification'),
                    jurisdiction.get('division', {}).get('id') if jurisdiction.get('division') else None,
                    jurisdiction.get('division', {}).get('name') if jurisdiction.get('division') else None,
                    jurisdiction.get('url'),
                    datetime.now(),
                    datetime.now()
                ))
                
                # Collect legislative sessions for this jurisdiction
                self._collect_legislative_sessions(cursor, jurisdiction.get('id'), jurisdiction.get('legislative_sessions', []))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected {len(jurisdictions)} jurisdictions from OpenStates")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting jurisdictions: {e}")
            raise
    
    def _collect_legislative_sessions(self, cursor, jurisdiction_id: str, sessions: List[Dict]) -> None:
        """
        Collect legislative sessions for a jurisdiction.
        
        Args:
            cursor: Database cursor
            jurisdiction_id: Jurisdiction ID
            sessions: List of session data
        """
        for session in sessions:
            cursor.execute("""
                INSERT INTO legislative_sessions (id, jurisdiction_id, identifier, name, classification, start_date, end_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    identifier = EXCLUDED.identifier,
                    name = EXCLUDED.name,
                    classification = EXCLUDED.classification,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    updated_at = EXCLUDED.updated_at
            """, (
                f"{jurisdiction_id}-{session.get('identifier')}",
                jurisdiction_id,
                session.get('identifier'),
                session.get('name'),
                session.get('classification'),
                session.get('start_date'),
                session.get('end_date'),
                datetime.now(),
                datetime.now()
            ))
    
    def collect_people(self, jurisdiction_id: Optional[str] = None) -> None:
        """
        Collect people (legislators) from OpenStates and store in database.
        
        Args:
            jurisdiction_id: Optional jurisdiction ID to filter by
        """
        logger.info("Collecting people from OpenStates")
        
        try:
            # Get all people or people from a specific jurisdiction
            if jurisdiction_id:
                response = self.client.get_people(jurisdiction=jurisdiction_id)
            else:
                response = self.client.get_people()
                
            people = response.get('results', [])
            
            cursor = self.db_conn.cursor()
            
            for person in people:
                # Insert person
                cursor.execute("""
                    INSERT INTO people (id, name, given_name, family_name, email, gender, biography, birth_date, image_url, source_url, source_note, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        given_name = EXCLUDED.given_name,
                        family_name = EXCLUDED.family_name,
                        email = EXCLUDED.email,
                        gender = EXCLUDED.gender,
                        biography = EXCLUDED.biography,
                        birth_date = EXCLUDED.birth_date,
                        image_url = EXCLUDED.image_url,
                        source_url = EXCLUDED.source_url,
                        source_note = EXCLUDED.source_note,
                        updated_at = EXCLUDED.updated_at
                """, (
                    person.get('id'),
                    person.get('name'),
                    person.get('given_name'),
                    person.get('family_name'),
                    person.get('email'),
                    person.get('gender'),
                    person.get('biography'),
                    person.get('birth_date'),
                    person.get('image'),
                    person.get('sources', [{}])[0].get('url') if person.get('sources') else None,
                    person.get('sources', [{}])[0].get('note') if person.get('sources') else None,
                    datetime.now(),
                    datetime.now()
                ))
                
                # Insert party affiliations
                self._collect_party_affiliations(cursor, person.get('id'), person.get('party', []))
                
                # Insert roles
                self._collect_person_roles(cursor, person.get('id'), person.get('roles', []))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected {len(people)} people from OpenStates")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting people: {e}")
            raise
    
    def _collect_party_affiliations(self, cursor, person_id: str, parties: List[Dict]) -> None:
        """
        Collect party affiliations for a person.
        
        Args:
            cursor: Database cursor
            person_id: Person ID
            parties: List of party data
        """
        for party in parties:
            party_name = party.get('name')
            if party_name:
                # Get or create party
                cursor.execute("""
                    INSERT INTO parties (name, created_at)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (party_name, datetime.now()))
                
                # Get party ID
                cursor.execute("SELECT id FROM parties WHERE name = %s", (party_name,))
                party_result = cursor.fetchone()
                if party_result:
                    party_id = party_result[0]
                    
                    # Insert party affiliation
                    cursor.execute("""
                        INSERT INTO person_party_affiliations (person_id, party_id, created_at, updated_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        person_id,
                        party_id,
                        datetime.now(),
                        datetime.now()
                    ))
    
    def _collect_person_roles(self, cursor, person_id: str, roles: List[Dict]) -> None:
        """
        Collect roles for a person.
        
        Args:
            cursor: Database cursor
            person_id: Person ID
            roles: List of role data
        """
        for role in roles:
            cursor.execute("""
                INSERT INTO person_roles (person_id, type, district, jurisdiction_id, start_date, end_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                person_id,
                role.get('type'),
                role.get('district'),
                role.get('jurisdiction'),
                role.get('start_date'),
                role.get('end_date'),
                datetime.now(),
                datetime.now()
            ))
    
    def collect_bills(self, jurisdiction_id: str, session: Optional[str] = None) -> None:
        """
        Collect bills from OpenStates and store in database.
        
        Args:
            jurisdiction_id: Jurisdiction ID
            session: Optional session identifier
        """
        logger.info(f"Collecting bills for jurisdiction {jurisdiction_id}")
        
        try:
            # Search for bills
            search_params = {"jurisdiction": jurisdiction_id}
            if session:
                search_params["session"] = session
                
            response = self.client.search_bills(**search_params)
            bills = response.get('results', [])
            
            cursor = self.db_conn.cursor()
            
            for bill in bills:
                # Insert bill
                cursor.execute("""
                    INSERT INTO bills (id, session_id, jurisdiction_id, identifier, title, classification, subject, extras, created_at, updated_at, openstates_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        identifier = EXCLUDED.identifier,
                        title = EXCLUDED.title,
                        classification = EXCLUDED.classification,
                        subject = EXCLUDED.subject,
                        extras = EXCLUDED.extras,
                        updated_at = EXCLUDED.updated_at,
                        openstates_url = EXCLUDED.openstates_url
                """, (
                    bill.get('id'),
                    bill.get('session'),
                    bill.get('jurisdiction', {}).get('id') if bill.get('jurisdiction') else None,
                    bill.get('identifier'),
                    bill.get('title'),
                    bill.get('classification'),
                    bill.get('subject'),
                    Json(bill.get('extras', {})),
                    datetime.now(),
                    datetime.now(),
                    bill.get('openstates_url')
                ))
                
                # Insert sponsors
                self._collect_bill_sponsors(cursor, bill.get('id'), bill.get('sponsorships', []))
                
                # Insert actions
                self._collect_bill_actions(cursor, bill.get('id'), bill.get('actions', []))
                
                # Insert versions
                self._collect_bill_versions(cursor, bill.get('id'), bill.get('versions', []))
                
                # Insert documents
                self._collect_bill_documents(cursor, bill.get('id'), bill.get('documents', []))
                
                # Insert votes
                self._collect_votes(cursor, bill.get('id'), bill.get('votes', []))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected {len(bills)} bills from OpenStates for jurisdiction {jurisdiction_id}")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting bills: {e}")
            raise
    
    def _collect_bill_sponsors(self, cursor, bill_id: str, sponsorships: List[Dict]) -> None:
        """
        Collect sponsors for a bill.
        
        Args:
            cursor: Database cursor
            bill_id: Bill ID
            sponsorships: List of sponsorship data
        """
        for sponsorship in sponsorships:
            cursor.execute("""
                INSERT INTO bill_sponsors (bill_id, person_id, organization_name, entity_type, primary_sponsor, classification, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                bill_id,
                None,  # Person ID would need to be looked up
                sponsorship.get('name'),
                sponsorship.get('entity_type'),
                sponsorship.get('primary'),
                sponsorship.get('classification'),
                datetime.now()
            ))
    
    def _collect_bill_actions(self, cursor, bill_id: str, actions: List[Dict]) -> None:
        """
        Collect actions for a bill.
        
        Args:
            cursor: Database cursor
            bill_id: Bill ID
            actions: List of action data
        """
        for i, action in enumerate(actions):
            action_id = f"{bill_id}-action-{i}"
            cursor.execute("""
                INSERT INTO bill_actions (id, bill_id, organization_name, description, date, classification, order_num, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    organization_name = EXCLUDED.organization_name,
                    description = EXCLUDED.description,
                    date = EXCLUDED.date,
                    classification = EXCLUDED.classification,
                    order_num = EXCLUDED.order_num
            """, (
                action_id,
                bill_id,
                action.get('organization', {}).get('name') if action.get('organization') else None,
                action.get('description'),
                action.get('date'),
                action.get('classification'),
                action.get('order', i),
                datetime.now()
            ))
    
    def _collect_bill_versions(self, cursor, bill_id: str, versions: List[Dict]) -> None:
        """
        Collect versions for a bill.
        
        Args:
            cursor: Database cursor
            bill_id: Bill ID
            versions: List of version data
        """
        for version in versions:
            for link in version.get('links', []):
                version_id = f"{bill_id}-version-{hash(link.get('url', ''))}"
                cursor.execute("""
                    INSERT INTO bill_versions (id, bill_id, note, date, url, media_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        note = EXCLUDED.note,
                        date = EXCLUDED.date,
                        url = EXCLUDED.url,
                        media_type = EXCLUDED.media_type
                """, (
                    version_id,
                    bill_id,
                    version.get('note'),
                    version.get('date'),
                    link.get('url'),
                    link.get('media_type'),
                    datetime.now()
                ))
    
    def _collect_bill_documents(self, cursor, bill_id: str, documents: List[Dict]) -> None:
        """
        Collect documents for a bill.
        
        Args:
            cursor: Database cursor
            bill_id: Bill ID
            documents: List of document data
        """
        for document in documents:
            for link in document.get('links', []):
                document_id = f"{bill_id}-document-{hash(link.get('url', ''))}"
                cursor.execute("""
                    INSERT INTO bill_documents (id, bill_id, note, date, url, media_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        note = EXCLUDED.note,
                        date = EXCLUDED.date,
                        url = EXCLUDED.url,
                        media_type = EXCLUDED.media_type
                """, (
                    document_id,
                    bill_id,
                    document.get('note'),
                    document.get('date'),
                    link.get('url'),
                    link.get('media_type'),
                    datetime.now()
                ))
    
    def _collect_votes(self, cursor, bill_id: str, votes: List[Dict]) -> None:
        """
        Collect votes for a bill.
        
        Args:
            cursor: Database cursor
            bill_id: Bill ID
            votes: List of vote data
        """
        for vote in votes:
            vote_id = vote.get('id', f"{bill_id}-vote-{hash(str(vote))}")
            cursor.execute("""
                INSERT INTO votes (id, bill_id, motion_text, result, date, organization_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    motion_text = EXCLUDED.motion_text,
                    result = EXCLUDED.result,
                    date = EXCLUDED.date,
                    organization_name = EXCLUDED.organization_name,
                    updated_at = EXCLUDED.updated_at
            """, (
                vote_id,
                bill_id,
                vote.get('motion_text'),
                vote.get('result'),
                vote.get('date'),
                vote.get('organization', {}).get('name') if vote.get('organization') else None,
                datetime.now(),
                datetime.now()
            ))
    
    def close(self) -> None:
        """Close the database connection."""
        if self.db_conn:
            self.db_conn.close()

# Example usage
if __name__ == "__main__":
    # Example of how to use the OpenStates data collector
    # collector = OpenStatesDataCollector(
    #     api_key="your-openstates-api-key",
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse"
    # )
    # 
    # # Collect jurisdictions
    # collector.collect_jurisdictions()
    # 
    # # Collect people
    # collector.collect_people()
    # 
    # # Collect bills for a specific jurisdiction
    # collector.collect_bills("ocd-jurisdiction/country:us/state:ca/government")
    # 
    # collector.close()
    pass