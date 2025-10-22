"""
Unified Data Processing Pipeline

This module coordinates the data validation, cleaning, and transformation processes
for government data from multiple sources.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import psycopg2
from psycopg2.extras import Json

# Add the project root to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.data_processing.data_validator import DataValidator, DataCleaner
from opendiscourse.data_processing.data_transformer import DataTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessingPipeline:
    """Coordinates the data processing pipeline for government data."""
    
    def __init__(self, db_connection_string: str):
        """
        Initialize the data processing pipeline.
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.db_connection_string = db_connection_string
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.transformer = DataTransformer()
        
        logger.info("Data processing pipeline initialized")
    
    def process_people_data(self, raw_people: List[Dict], source: str) -> int:
        """
        Process people data through the pipeline.
        
        Args:
            raw_people: List of raw people data
            source: Source identifier
            
        Returns:
            Number of people successfully processed
        """
        logger.info(f"Processing {len(raw_people)} people from {source}")
        
        try:
            # Transform to unified format
            unified_people = self.transformer.unify_people_data(raw_people, source)
            
            # Store in database
            processed_count = self._store_people_data(unified_people)
            
            logger.info(f"Successfully processed {processed_count} people from {source}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing people data from {source}: {e}")
            raise
    
    def process_bills_data(self, raw_bills: List[Dict], source: str) -> int:
        """
        Process bills data through the pipeline.
        
        Args:
            raw_bills: List of raw bills data
            source: Source identifier
            
        Returns:
            Number of bills successfully processed
        """
        logger.info(f"Processing {len(raw_bills)} bills from {source}")
        
        try:
            # Transform to unified format
            unified_bills = self.transformer.unify_bills_data(raw_bills, source)
            
            # Store in database
            processed_count = self._store_bills_data(unified_bills)
            
            logger.info(f"Successfully processed {processed_count} bills from {source}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing bills data from {source}: {e}")
            raise
    
    def process_jurisdictions_data(self, raw_jurisdictions: List[Dict], source: str) -> int:
        """
        Process jurisdictions data through the pipeline.
        
        Args:
            raw_jurisdictions: List of raw jurisdictions data
            source: Source identifier
            
        Returns:
            Number of jurisdictions successfully processed
        """
        logger.info(f"Processing {len(raw_jurisdictions)} jurisdictions from {source}")
        
        try:
            # Standardize jurisdictions
            standardized_jurisdictions = []
            for jurisdiction in raw_jurisdictions:
                standardized = self.transformer.standardize_jurisdiction(jurisdiction, source)
                standardized_jurisdictions.append(standardized)
            
            # Store in database
            processed_count = self._store_jurisdictions_data(standardized_jurisdictions)
            
            logger.info(f"Successfully processed {processed_count} jurisdictions from {source}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing jurisdictions data from {source}: {e}")
            raise
    
    def _store_people_data(self, people_data: List[Dict]) -> int:
        """
        Store processed people data in the database.
        
        Args:
            people_data: List of processed people data
            
        Returns:
            Number of people successfully stored
        """
        if not self.db_connection_string:
            logger.warning("No database connection string provided")
            return 0
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            stored_count = 0
            
            for person in people_data:
                try:
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
                        person.get('image_url'),
                        person.get('source_url'),
                        person.get('source_note'),
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    # Insert party affiliation if available
                    party = person.get('party')
                    if party:
                        # Standardize party name
                        standardized_party = self.cleaner.standardize_party_names(party)
                        
                        # Get or create party
                        cursor.execute("""
                            INSERT INTO parties (name, created_at)
                            VALUES (%s, %s)
                            ON CONFLICT (name) DO NOTHING
                        """, (standardized_party, datetime.now()))
                        
                        # Get party ID
                        cursor.execute("SELECT id FROM parties WHERE name = %s", (standardized_party,))
                        party_result = cursor.fetchone()
                        if party_result:
                            party_id = party_result[0]
                            
                            # Insert party affiliation
                            cursor.execute("""
                                INSERT INTO person_party_affiliations (person_id, party_id, created_at, updated_at)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                person.get('id'),
                                party_id,
                                datetime.now(),
                                datetime.now()
                            ))
                    
                    # Insert roles if available
                    roles = person.get('roles', [])
                    for role in roles:
                        cursor.execute("""
                            INSERT INTO person_roles (person_id, type, district, jurisdiction_id, start_date, end_date, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            person.get('id'),
                            role.get('type'),
                            role.get('district'),
                            role.get('jurisdiction_id'),
                            role.get('start_date'),
                            role.get('end_date'),
                            datetime.now(),
                            datetime.now()
                        ))
                    
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing person {person.get('id', 'unknown')}: {e}")
                    continue
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing people data: {e}")
            raise
    
    def _store_bills_data(self, bills_data: List[Dict]) -> int:
        """
        Store processed bills data in the database.
        
        Args:
            bills_data: List of processed bills data
            
        Returns:
            Number of bills successfully stored
        """
        if not self.db_connection_string:
            logger.warning("No database connection string provided")
            return 0
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            stored_count = 0
            
            for bill in bills_data:
                try:
                    # Insert bill
                    cursor.execute("""
                        INSERT INTO bills (id, session_id, jurisdiction_id, identifier, title, classification, subject, extras, created_at, updated_at, openstates_url, congress_gov_url, govinfo_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            session_id = EXCLUDED.session_id,
                            jurisdiction_id = EXCLUDED.jurisdiction_id,
                            identifier = EXCLUDED.identifier,
                            title = EXCLUDED.title,
                            classification = EXCLUDED.classification,
                            subject = EXCLUDED.subject,
                            extras = EXCLUDED.extras,
                            updated_at = EXCLUDED.updated_at,
                            openstates_url = EXCLUDED.openstates_url,
                            congress_gov_url = EXCLUDED.congress_gov_url,
                            govinfo_url = EXCLUDED.govinfo_url
                    """, (
                        bill.get('id'),
                        bill.get('session_id'),
                        bill.get('jurisdiction_id'),
                        bill.get('identifier'),
                        bill.get('title'),
                        bill.get('classification'),
                        bill.get('subject'),
                        Json(bill.get('extras', {})),
                        datetime.now(),
                        datetime.now(),
                        bill.get('extras', {}).get('openstates_url') if bill.get('extras') else None,
                        bill.get('extras', {}).get('congressdotgov_url') if bill.get('extras') else None,
                        bill.get('extras', {}).get('govinfo_url') if bill.get('extras') else None
                    ))
                    
                    # Insert sponsors if available
                    sponsors = bill.get('sponsors', [])
                    for sponsor in sponsors:
                        cursor.execute("""
                            INSERT INTO bill_sponsors (bill_id, person_id, organization_name, entity_type, primary_sponsor, classification, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            bill.get('id'),
                            sponsor.get('person_id'),
                            sponsor.get('name'),
                            sponsor.get('entity_type'),
                            sponsor.get('primary'),
                            sponsor.get('classification'),
                            datetime.now()
                        ))
                    
                    # Insert actions if available
                    actions = bill.get('actions', [])
                    for i, action in enumerate(actions):
                        action_id = f"{bill.get('id')}-action-{i}"
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
                            bill.get('id'),
                            action.get('organization'),
                            action.get('description'),
                            action.get('date'),
                            action.get('classification'),
                            i,
                            datetime.now()
                        ))
                    
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing bill {bill.get('id', 'unknown')}: {e}")
                    continue
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing bills data: {e}")
            raise
    
    def _store_jurisdictions_data(self, jurisdictions_data: List[Dict]) -> int:
        """
        Store processed jurisdictions data in the database.
        
        Args:
            jurisdictions_data: List of processed jurisdictions data
            
        Returns:
            Number of jurisdictions successfully stored
        """
        if not self.db_connection_string:
            logger.warning("No database connection string provided")
            return 0
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            stored_count = 0
            
            for jurisdiction in jurisdictions_data:
                try:
                    # Insert jurisdiction
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
                        jurisdiction.get('division_id'),
                        jurisdiction.get('division_name'),
                        jurisdiction.get('url'),
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing jurisdiction {jurisdiction.get('id', 'unknown')}: {e}")
                    continue
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing jurisdictions data: {e}")
            raise
    
    def run_full_pipeline(self, data_batches: Dict[str, Dict[str, List[Dict]]]) -> Dict[str, int]:
        """
        Run the full data processing pipeline on all data batches.
        
        Args:
            data_batches: Dictionary with data batches for each source and entity type
            
        Returns:
            Dictionary with processing results for each source and entity type
        """
        logger.info("Running full data processing pipeline")
        
        results = {}
        
        try:
            for source, entities in data_batches.items():
                results[source] = {}
                
                # Process jurisdictions
                if 'jurisdictions' in entities:
                    count = self.process_jurisdictions_data(entities['jurisdictions'], source)
                    results[source]['jurisdictions'] = count
                
                # Process people
                if 'people' in entities:
                    count = self.process_people_data(entities['people'], source)
                    results[source]['people'] = count
                
                # Process bills
                if 'bills' in entities:
                    count = self.process_bills_data(entities['bills'], source)
                    results[source]['bills'] = count
            
            logger.info("Full data processing pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error running full data processing pipeline: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Example of how to use the data processing pipeline
    # pipeline = DataProcessingPipeline(
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse"
    # )
    # 
    # # Example data batches
    # data_batches = {
    #     'openstates': {
    #         'jurisdictions': [
    #             {
    #                 'id': 'ocd-jurisdiction/country:us/state:ca/government',
    #                 'name': 'California',
    #                 'classification': 'state'
    #             }
    #         ],
    #         'people': [
    #             {
    #                 'id': 'ocd-person/123',
    #                 'name': 'John Doe',
    #                 'party': [{'name': 'Democratic'}]
    #             }
    #         ],
    #         'bills': [
    #             {
    #                 'id': 'ocd-bill/456',
    #                 'identifier': 'AB 1234',
    #                 'title': 'Sample Bill'
    #             }
    #         ]
    #     }
    # }
    # 
    # # Run the pipeline
    # results = pipeline.run_full_pipeline(data_batches)
    # print(f"Pipeline results: {results}")
    pass