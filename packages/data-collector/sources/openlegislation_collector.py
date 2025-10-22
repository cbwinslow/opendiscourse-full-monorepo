"""
OpenLegislation Data Collection Module

This module handles the collection of data from the OpenLegislation API and stores it in the database.
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

from opendiscourse.opendiscourse.openlegislation_api import create_openlegislation_client, OpenLegislationAPI
from opendiscourse.opendiscourse.unified_api import UnifiedAPISuite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenLegislationDataCollector:
    """Handles collection of data from the OpenLegislation API."""
    
    def __init__(self, api_key: str, db_connection_string: str):
        """
        Initialize the OpenLegislation data collector.
        
        Args:
            api_key: OpenLegislation API key
            db_connection_string: PostgreSQL connection string
        """
        self.client = create_openlegislation_client(api_key)
        self.db_conn = psycopg2.connect(db_connection_string)
        self.db_conn.autocommit = False
        
    def collect_bills(self, year: str, page_size: int = 20) -> None:
        """
        Collect bills from OpenLegislation by searching by year and store in database.
        
        Args:
            year: Year to search for bills
            page_size: Number of results per page
        """
        logger.info(f"Collecting bills for year {year} from OpenLegislation")
        
        try:
            # Search for bills by year
            bills = self._search_bills_by_year(year, page_size)
            
            cursor = self.db_conn.cursor()
            
            for bill_result in bills:
                bill_data = bill_result.get('data', {})
                if not bill_data:
                    continue
                    
                # Extract bill information
                senate_bill_no = bill_data.get('senateBillNo')
                if not senate_bill_no:
                    continue
                    
                # Create a unique bill ID
                bill_id = f"nys-{year}-{senate_bill_no}"
                
                # Create session ID for New York State
                session_id = f"nys-{year}"
                jurisdiction_id = "ocd-jurisdiction/country:us/state:ny/government"  # NY jurisdiction
                
                # Insert bill
                cursor.execute("""
                    INSERT INTO bills (id, session_id, jurisdiction_id, identifier, title, classification, subject, extras, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        identifier = EXCLUDED.identifier,
                        title = EXCLUDED.title,
                        classification = EXCLUDED.classification,
                        subject = EXCLUDED.subject,
                        extras = EXCLUDED.extras,
                        updated_at = EXCLUDED.updated_at
                """, (
                    bill_id,
                    session_id,
                    jurisdiction_id,
                    senate_bill_no,
                    bill_data.get('title'),
                    ['bill'],  # Classification
                    None,  # Subject
                    Json({
                        "lawSection": bill_data.get('lawSection'),
                        "sameAs": bill_data.get('sameAs'),
                        "previousVersions": bill_data.get('previousVersions'),
                        "summary": bill_data.get('summary'),
                        "currentCommittee": bill_data.get('currentCommittee'),
                        "fulltext": bill_data.get('fulltext'),
                        "memo": bill_data.get('memo'),
                        "law": bill_data.get('law')
                    }),
                    datetime.now(),
                    datetime.now()
                ))
                
                # Insert sponsor if available
                sponsor = bill_data.get('sponsor', {})
                sponsor_name = sponsor.get('fullname') if sponsor else None
                if sponsor_name:
                    cursor.execute("""
                        INSERT INTO bill_sponsors (bill_id, organization_name, entity_type, primary_sponsor, classification, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        bill_id,
                        sponsor_name,
                        "person",
                        True,
                        "primary",
                        datetime.now()
                    ))
                
                # Insert actions
                self._collect_bill_actions(cursor, bill_id, bill_data.get('actions', []))
                
                # Insert votes
                self._collect_votes(cursor, bill_id, bill_data.get('votes', []))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected bills for year {year} from OpenLegislation")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting bills: {e}")
            raise
    
    def _search_bills_by_year(self, year: str, page_size: int = 20) -> List[Dict]:
        """
        Search for bills by year.
        
        Args:
            year: Year to search for
            page_size: Number of results per page
            
        Returns:
            List of bills
        """
        term = f"year:{year}"
        response = self.client.search(term, page_size=page_size)
        return response.get("response", {}).get("results", [])
    
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
                INSERT INTO bill_actions (id, bill_id, description, date, order_num, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    description = EXCLUDED.description,
                    date = EXCLUDED.date,
                    order_num = EXCLUDED.order_num
            """, (
                action_id,
                bill_id,
                action.get('text'),
                action.get('date'),
                i,
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
            # Create a unique vote ID
            vote_id = f"{bill_id}-vote-{hash(str(vote))}"
            
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
                vote.get('description', ''),
                'pass' if vote.get('ayes') and len(vote.get('ayes', [])) > len(vote.get('nays', [])) else 'fail',
                vote.get('voteDate'),
                'New York State Senate',  # Organization name
                datetime.now(),
                datetime.now()
            ))
            
            # Insert vote details for ayes
            for aye in vote.get('ayes', []):
                self._insert_vote_detail(cursor, vote_id, aye, 'yes')
            
            # Insert vote details for nays
            for nay in vote.get('nays', []):
                self._insert_vote_detail(cursor, vote_id, nay, 'no')
            
            # Insert vote details for abstains
            for abstain in vote.get('abstains', []):
                self._insert_vote_detail(cursor, vote_id, abstain, 'abstain')
            
            # Insert vote details for excused
            for excused in vote.get('excused', []):
                self._insert_vote_detail(cursor, vote_id, excused, 'excused')
    
    def _insert_vote_detail(self, cursor, vote_id: str, person_name: str, option: str) -> None:
        """
        Insert a vote detail record.
        
        Args:
            cursor: Database cursor
            vote_id: Vote ID
            person_name: Person name
            option: Vote option (yes, no, abstain, excused)
        """
        cursor.execute("""
            INSERT INTO vote_details (vote_id, option, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            vote_id,
            option,
            datetime.now()
        ))
    
    def collect_meetings(self, committee: str, month: str, day: str, year: str) -> None:
        """
        Collect meeting information from OpenLegislation and store in database.
        
        Args:
            committee: Committee name
            month: Month (MM)
            day: Day (DD)
            year: Year (YYYY)
        """
        logger.info(f"Collecting meeting for {committee} on {year}-{month}-{day} from OpenLegislation")
        
        try:
            response = self.client.get_meeting(committee, month, day, year)
            meeting_result = response.get("response", {}).get("results", [{}])[0]
            meeting_data = meeting_result.get("data", {})
            
            if not meeting_data:
                logger.warning("No meeting data found")
                return
            
            # Create a unique event ID
            event_id = f"nys-meeting-{committee}-{year}-{month}-{day}"
            
            cursor = self.db_conn.cursor()
            
            # Insert event
            cursor.execute("""
                INSERT INTO events (id, name, jurisdiction_id, description, classification, start_date, location_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    classification = EXCLUDED.classification,
                    start_date = EXCLUDED.start_date,
                    location_name = EXCLUDED.location_name,
                    updated_at = EXCLUDED.updated_at
            """, (
                event_id,
                f"{committee} Meeting",
                "ocd-jurisdiction/country:us/state:ny/government",  # NY jurisdiction
                meeting_data.get('notes'),
                "committee-meeting",
                meeting_data.get('meetingDateTime'),
                meeting_data.get('location'),
                datetime.now(),
                datetime.now()
            ))
            
            # Insert agenda items (bills being discussed)
            bills = meeting_data.get('bills', [])
            for i, bill in enumerate(bills):
                cursor.execute("""
                    INSERT INTO event_agenda_items (event_id, description, order_num, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    event_id,
                    f"Bill {bill.get('senateBillNo', '')}: {bill.get('title', '')}",
                    i,
                    datetime.now()
                ))
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected meeting for {committee} on {year}-{month}-{day} from OpenLegislation")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting meeting: {e}")
            raise
    
    def collect_transcripts(self, session_type: str, month: str, day: str, year: str) -> None:
        """
        Collect transcript information from OpenLegislation and store in database.
        
        Args:
            session_type: Session type (regular or special)
            month: Month (MM)
            day: Day (DD)
            year: Year (YYYY)
        """
        logger.info(f"Collecting {session_type} session transcript on {year}-{month}-{day} from OpenLegislation")
        
        try:
            response = self.client.get_transcript(session_type, month, day, year)
            transcript_result = response.get("response", {}).get("results", [{}])[0]
            transcript_data = transcript_result.get("data", {})
            
            if not transcript_data:
                logger.warning("No transcript data found")
                return
            
            # For now, we'll just log that we have transcript data
            # In a real implementation, we might want to parse and store the transcript text
            logger.info(f"Transcript collected for {session_type} session on {year}-{month}-{day}")
            logger.debug(f"Transcript timestamp: {transcript_data.get('timeStamp')}")
            
        except Exception as e:
            logger.error(f"Error collecting transcript: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.db_conn:
            self.db_conn.close()

# Example usage
if __name__ == "__main__":
    # Example of how to use the OpenLegislation data collector
    # collector = OpenLegislationDataCollector(
    #     api_key="your-openlegislation-api-key",
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse"
    # )
    # 
    # # Collect bills for a specific year
    # collector.collect_bills("2021")
    # 
    # # Collect a specific meeting
    # collector.collect_meetings("Finance", "06", "24", "2021")
    # 
    # collector.close()
    pass