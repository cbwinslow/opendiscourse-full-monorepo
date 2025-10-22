"""
Congress.gov Data Collection Module

This module handles the collection of data from the Congress.gov API and stores it in the database.
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

from opendiscourse.opendiscourse.congress_gov_api import create_congress_gov_client, CongressGovAPI
from opendiscourse.opendiscourse.unified_api import UnifiedAPISuite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CongressGovDataCollector:
    """Handles collection of data from the Congress.gov API."""
    
    def __init__(self, api_key: str, db_connection_string: str):
        """
        Initialize the Congress.gov data collector.
        
        Args:
            api_key: Congress.gov API key
            db_connection_string: PostgreSQL connection string
        """
        self.client = create_congress_gov_client(api_key)
        self.db_conn = psycopg2.connect(db_connection_string)
        self.db_conn.autocommit = False
        
    def collect_bills(self, bill_type: str = "introduced", congress: Optional[str] = None, 
                     chamber: Optional[str] = None, page: int = 1) -> None:
        """
        Collect bills from Congress.gov and store in database.
        
        Args:
            bill_type: Type of bills to collect (introduced, updated, active, passed, enacted)
            congress: Congress number (e.g., "117")
            chamber: Chamber (house or senate)
            page: Page number for pagination
        """
        logger.info(f"Collecting {bill_type} bills from Congress.gov")
        
        try:
            response = self.client.get_bills(bill_type, congress, chamber, page)
            bills = response.get('results', [])
            
            cursor = self.db_conn.cursor()
            
            for bill_data in bills:
                # Extract bill information
                bill_id = bill_data.get('bill_id')
                if not bill_id:
                    continue
                    
                # Create session ID for federal bills
                session_id = f"congress-{congress}" if congress else None
                jurisdiction_id = "ocd-jurisdiction/country:us/government"  # Federal jurisdiction
                
                # Insert bill
                cursor.execute("""
                    INSERT INTO bills (id, session_id, jurisdiction_id, identifier, title, classification, subject, extras, created_at, updated_at, congress_gov_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        identifier = EXCLUDED.identifier,
                        title = EXCLUDED.title,
                        classification = EXCLUDED.classification,
                        subject = EXCLUDED.subject,
                        extras = EXCLUDED.extras,
                        updated_at = EXCLUDED.updated_at,
                        congress_gov_url = EXCLUDED.congress_gov_url
                """, (
                    bill_id,
                    session_id,
                    jurisdiction_id,
                    bill_data.get('number'),
                    bill_data.get('title'),
                    [bill_data.get('bill_type')] if bill_data.get('bill_type') else None,
                    [bill_data.get('primary_subject')] if bill_data.get('primary_subject') else None,
                    Json({
                        "sponsor_id": bill_data.get('sponsor_id'),
                        "cosponsors": bill_data.get('cosponsors'),
                        "cosponsors_by_party": bill_data.get('cosponsors_by_party'),
                        "committees": bill_data.get('committees'),
                        "summary": bill_data.get('summary'),
                        "summary_short": bill_data.get('summary_short'),
                        "latest_major_action_date": bill_data.get('latest_major_action_date'),
                        "latest_major_action": bill_data.get('latest_major_action')
                    }),
                    datetime.now(),
                    datetime.now(),
                    bill_data.get('congressdotgov_url')
                ))
                
                # Insert sponsor if available
                sponsor_id = bill_data.get('sponsor_id')
                if sponsor_id:
                    cursor.execute("""
                        INSERT INTO bill_sponsors (bill_id, person_id, entity_type, primary_sponsor, classification, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        bill_id,
                        sponsor_id,
                        "person",
                        True,
                        "primary",
                        datetime.now()
                    ))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected {len(bills)} {bill_type} bills from Congress.gov")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting bills: {e}")
            raise
    
    def collect_members(self, congress: str, chamber: str) -> None:
        """
        Collect members from Congress.gov and store in database.
        
        Args:
            congress: Congress number (e.g., "117")
            chamber: Chamber (house or senate)
        """
        logger.info(f"Collecting {chamber} members for Congress {congress} from Congress.gov")
        
        try:
            response = self.client.get_members(congress, chamber)
            members = response.get('results', [])
            
            cursor = self.db_conn.cursor()
            
            for member_data in members:
                # Insert member
                member_id = member_data.get('id')
                cursor.execute("""
                    INSERT INTO people (id, name, given_name, family_name, email, gender, birth_date, image_url, source_url, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        given_name = EXCLUDED.given_name,
                        family_name = EXCLUDED.family_name,
                        email = EXCLUDED.email,
                        gender = EXCLUDED.gender,
                        birth_date = EXCLUDED.birth_date,
                        image_url = EXCLUDED.image_url,
                        source_url = EXCLUDED.source_url,
                        updated_at = EXCLUDED.updated_at
                """, (
                    member_id,
                    f"{member_data.get('first_name', '')} {member_data.get('last_name', '')}".strip(),
                    member_data.get('first_name'),
                    member_data.get('last_name'),
                    member_data.get('email'),
                    member_data.get('gender'),
                    member_data.get('date_of_birth'),
                    None,  # Image URL not directly available
                    member_data.get('url'),
                    datetime.now(),
                    datetime.now()
                ))
                
                # Insert party affiliation
                party = member_data.get('party')
                if party:
                    # Get or create party
                    cursor.execute("""
                        INSERT INTO parties (name, created_at)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (party, datetime.now()))
                    
                    # Get party ID
                    cursor.execute("SELECT id FROM parties WHERE name = %s", (party,))
                    party_result = cursor.fetchone()
                    if party_result:
                        party_id = party_result[0]
                        
                        # Insert party affiliation
                        cursor.execute("""
                            INSERT INTO person_party_affiliations (person_id, party_id, created_at, updated_at)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            member_id,
                            party_id,
                            datetime.now(),
                            datetime.now()
                        ))
                
                # Insert role for current congress
                state = member_data.get('state')
                district = member_data.get('district')
                cursor.execute("""
                    INSERT INTO person_roles (person_id, type, district, jurisdiction_id, start_date, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    member_id,
                    chamber,
                    district,
                    "ocd-jurisdiction/country:us/government",  # Federal jurisdiction
                    f"{congress}-01-01",  # Approximate start date
                    datetime.now(),
                    datetime.now()
                ))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected {len(members)} {chamber} members for Congress {congress} from Congress.gov")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting members: {e}")
            raise
    
    def collect_votes(self, member_id: str, offset: int = 0) -> None:
        """
        Collect voting history for a member from Congress.gov and store in database.
        
        Args:
            member_id: Member ID
            offset: Offset for pagination
        """
        logger.info(f"Collecting voting history for member {member_id} from Congress.gov")
        
        try:
            response = self.client.get_votes(member_id, offset)
            votes = response.get('results', [])
            
            cursor = self.db_conn.cursor()
            
            for vote_data in votes:
                # Extract vote information
                vote_uri = vote_data.get('vote_uri')
                if not vote_uri:
                    continue
                    
                # Extract bill information from vote data
                bill_info = vote_data.get('bill', {})
                bill_id = bill_info.get('bill_id') if bill_info else None
                
                # Create a unique vote ID
                vote_id = f"congressgov-{hash(vote_uri)}"
                
                # Insert vote
                cursor.execute("""
                    INSERT INTO votes (id, bill_id, motion_text, result, date, organization_name, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        bill_id = EXCLUDED.bill_id,
                        motion_text = EXCLUDED.motion_text,
                        result = EXCLUDED.result,
                        date = EXCLUDED.date,
                        organization_name = EXCLUDED.organization_name,
                        updated_at = EXCLUDED.updated_at
                """, (
                    vote_id,
                    bill_id,
                    vote_data.get('description'),
                    vote_data.get('result'),
                    vote_data.get('date'),
                    "Congress",  # Organization name
                    datetime.now(),
                    datetime.now()
                ))
                
                # Insert vote detail for this member
                cursor.execute("""
                    INSERT INTO vote_details (vote_id, person_id, option, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    vote_id,
                    member_id,
                    vote_data.get('position'),
                    datetime.now()
                ))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected {len(votes)} votes for member {member_id} from Congress.gov")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting votes: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.db_conn:
            self.db_conn.close()

# Example usage
if __name__ == "__main__":
    # Example of how to use the Congress.gov data collector
    # collector = CongressGovDataCollector(
    #     api_key="your-congressgov-api-key",
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse"
    # )
    # 
    # # Collect introduced bills
    # collector.collect_bills("introduced", "117", "house")
    # 
    # # Collect members
    # collector.collect_members("117", "house")
    # 
    # collector.close()
    pass