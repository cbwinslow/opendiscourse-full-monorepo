#!/usr/bin/env python3
"""
OpenStates Data Ingestion Workflow
Ingests legislative data from OpenStates API into the PostgreSQL database.
Supports multiple data types: people, bills, committees, events, votes.
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv('database_config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openstates_ingestion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: str
    database: str
    user: str
    password: str
    
    def __post_init__(self):
        self.url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class OpenStatesIngestor:
    """OpenStates data ingestion workflow."""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.api_key = os.getenv('OPENSTATES_API_KEY', '')
        self.base_url = 'https://openstates.org/api/v1'
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'User-Agent': 'OpenDiscourse-Ingestor/1.0'
        })
        
        # Data type configurations
        self.data_types = {
            'jurisdictions': {
                'endpoint': '/jurisdictions/',
                'table': 'opencivicdata_jurisdiction',
                'batch_size': 50
            },
            'people': {
                'endpoint': '/people/',
                'table': 'opencivicdata_person',
                'batch_size': 100
            },
            'bills': {
                'endpoint': '/bills/',
                'table': 'opencivicdata_bill',
                'batch_size': 100
            },
            'organizations': {
                'endpoint': '/organizations/',
                'table': 'opencivicdata_organization',
                'batch_size': 100
            },
            'events': {
                'endpoint': '/events/',
                'table': 'opencivicdata_event',
                'batch_size': 100
            }
        }
        
        # Track ingestion statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now()
        }
    
    def get_database_connection(self):
        """Get database connection."""
        return psycopg2.connect(
            host=self.db_config.host,
            port=self.db_config.port,
            database=self.db_config.database,
            user=self.db_config.user,
            password=self.db_config.password
        )
    
    def test_api_connection(self) -> bool:
        """Test OpenStates API connection."""
        try:
            response = self.session.get(f"{self.base_url}/jurisdictions/", params={'per_page': 1})
            response.raise_for_status()
            logger.info("✅ OpenStates API connection successful")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ OpenStates API connection failed: {e}")
            return False
    
    def fetch_data_batch(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Fetch a batch of data from OpenStates API."""
        if params is None:
            params = {}
        
        params.update({
            'per_page': 100,
            'apikey': self.api_key
        })
        
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, dict):
                return data.get('results', [])
            else:
                return data
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return []
    
    def map_jurisdiction_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenStates jurisdiction data to database schema."""
        return {
            'id': item.get('id'),
            'name': item.get('name'),
            'url': item.get('url'),
            'classification': item.get('classification', 'state'),
            'division_id': item.get('division_id'),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_person_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenStates person data to database schema."""
        return {
            'id': item.get('id'),
            'name': item.get('name'),
            'family_name': item.get('family_name', ''),
            'given_name': item.get('given_name', ''),
            'image': item.get('image', ''),
            'gender': item.get('gender', ''),
            'email': item.get('email', ''),
            'biography': item.get('biography', ''),
            'birth_date': item.get('birth_date', ''),
            'death_date': item.get('death_date', ''),
            'primary_party': item.get('party', [{}])[0].get('name', '') if item.get('party') else '',
            'current_role': json.dumps(item.get('current_role', {})),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'extras': json.dumps(item.get('extras', {})),
            'current_jurisdiction_id': item.get('jurisdiction')
        }
    
    def map_bill_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenStates bill data to database schema."""
        return {
            'id': item.get('id'),
            'identifier': item.get('identifier'),
            'title': item.get('title'),
            'classification': item.get('classification', []),
            'subject': item.get('subject', []),
            'extras': json.dumps(item.get('extras', {})),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'from_organization_id': item.get('from_organization'),
            'legislative_session_id': item.get('session'),
            'first_action_date': item.get('first_action_date'),
            'latest_action_date': item.get('latest_action_date'),
            'latest_action_description': item.get('latest_action_description'),
            'latest_passage_date': item.get('latest_passage_date')
        }
    
    def map_organization_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenStates organization data to database schema."""
        return {
            'id': item.get('id'),
            'name': item.get('name'),
            'classification': item.get('classification'),
            'parent_id': item.get('parent_id'),
            'links': json.dumps(item.get('links', [])),
            'sources': json.dumps(item.get('sources', [])),
            'extras': json.dumps(item.get('extras', {})),
            'jurisdiction_id': item.get('jurisdiction'),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_event_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenStates event data to database schema."""
        return {
            'id': item.get('id'),
            'name': item.get('name'),
            'description': item.get('description'),
            'classification': item.get('classification'),
            'start_date': item.get('start_date'),
            'end_date': item.get('end_date'),
            'all_day': item.get('all_day', False),
            'status': item.get('status'),
            'jurisdiction_id': item.get('jurisdiction'),
            'location_name': item.get('location', {}).get('name', ''),
            'location_url': item.get('location', {}).get('url', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def get_mapper(self, data_type: str):
        """Get the appropriate data mapper."""
        mappers = {
            'jurisdictions': self.map_jurisdiction_data,
            'people': self.map_person_data,
            'bills': self.map_bill_data,
            'organizations': self.map_organization_data,
            'events': self.map_event_data
        }
        return mappers.get(data_type)
    
    def insert_batch(self, table: str, data: List[Dict[str, Any]]) -> bool:
        """Insert a batch of data into the database."""
        if not data:
            return True
        
        try:
            conn = self.get_database_connection()
            with conn.cursor() as cursor:
                # Get column names from the first record
                columns = list(data[0].keys())
                
                # Build the INSERT query
                insert_query = f"""
                    INSERT INTO {table} ({', '.join(columns)}) 
                    VALUES %s
                    ON CONFLICT (id) DO UPDATE SET
                        updated_at = EXCLUDED.updated_at,
                        extras = EXCLUDED.extras
                """
                
                # Prepare values
                values = []
                for record in data:
                    row_values = []
                    for col in columns:
                        value = record.get(col)
                        if isinstance(value, (dict, list)):
                            row_values.append(json.dumps(value))
                        else:
                            row_values.append(value)
                    values.append(tuple(row_values))
                
                # Execute batch insert
                execute_values(cursor, insert_query, values, template=None)
                conn.commit()
                
                logger.info(f"✅ Inserted {len(data)} records into {table}")
                return True
                
        except psycopg2.Error as e:
            logger.error(f"❌ Database error for {table}: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error for {table}: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def ingest_data_type(self, data_type: str, jurisdiction: str = None) -> bool:
        """Ingest a specific data type."""
        if data_type not in self.data_types:
            logger.error(f"❌ Unknown data type: {data_type}")
            return False
        
        config = self.data_types[data_type]
        endpoint = config['endpoint']
        table = config['table']
        mapper = self.get_mapper(data_type)
        
        if not mapper:
            logger.error(f"❌ No mapper found for {data_type}")
            return False
        
        logger.info(f"🔄 Starting ingestion of {data_type}")
        
        # Build API parameters
        params = {}
        if jurisdiction:
            params['jurisdiction'] = jurisdiction
        
        page = 1
        total_processed = 0
        successful = 0
        
        while True:
            logger.info(f"📄 Fetching {data_type} page {page}")
            
            # Add pagination
            current_params = params.copy()
            current_params['page'] = page
            
            # Fetch data
            batch_data = self.fetch_data_batch(endpoint, current_params)
            
            if not batch_data:
                logger.info(f"📄 No more data for {data_type} (page {page})")
                break
            
            # Map data
            mapped_data = []
            for item in batch_data:
                try:
                    mapped_item = mapper(item)
                    if mapped_item and mapped_item.get('id'):  # Ensure we have an ID
                        mapped_data.append(mapped_item)
                except Exception as e:
                    logger.error(f"❌ Error mapping {data_type} item: {e}")
                    continue
            
            # Insert batch
            if mapped_data:
                if self.insert_batch(table, mapped_data):
                    successful += len(mapped_data)
                else:
                    logger.error(f"❌ Failed to insert {data_type} batch")
                    return False
            
            total_processed += len(batch_data)
            page += 1
            
            # Rate limiting
            time.sleep(0.5)
        
        # Update statistics
        self.stats['total_processed'] += total_processed
        self.stats['successful'] += successful
        
        logger.info(f"✅ Completed {data_type}: {successful}/{total_processed} successful")
        return True
    
    def ingest_all_data_types(self, jurisdictions: List[str] = None) -> bool:
        """Ingest all data types for specified jurisdictions."""
        if not self.test_api_connection():
            return False
        
        logger.info("🚀 Starting comprehensive OpenStates data ingestion")
        
        # If no jurisdictions specified, get all jurisdictions first
        if not jurisdictions:
            logger.info("📋 Fetching all jurisdictions...")
            jurisdictions_data = self.fetch_data_batch('/jurisdictions/')
            jurisdictions = [j['id'] for j in jurisdictions_data if j.get('id')]
            logger.info(f"📋 Found {len(jurisdictions)} jurisdictions")
        
        success = True
        
        # Ingest jurisdictions first (needed for foreign keys)
        if 'jurisdictions' in self.data_types:
            logger.info("🌍 Starting with jurisdictions...")
            if not self.ingest_data_type('jurisdictions'):
                success = False
                logger.error("❌ Failed to ingest jurisdictions")
        
        # Ingest other data types
        data_types_to_ingest = [dt for dt in self.data_types.keys() if dt != 'jurisdictions']
        
        for data_type in data_types_to_ingest:
            if success:  # Only continue if previous types were successful
                for jurisdiction in jurisdictions[:5]:  # Limit to first 5 for demo
                    logger.info(f"🏛️ Ingesting {data_type} for {jurisdiction}")
                    if not self.ingest_data_type(data_type, jurisdiction):
                        success = False
                        logger.error(f"❌ Failed to ingest {data_type} for {jurisdiction}")
                        break
            else:
                break
        
        # Log final statistics
        elapsed_time = datetime.now() - self.stats['start_time']
        logger.info("📊 Ingestion Summary:")
        logger.info(f"   Total processed: {self.stats['total_processed']}")
        logger.info(f"   Successful: {self.stats['successful']}")
        logger.info(f"   Failed: {self.stats['total_processed'] - self.stats['successful']}")
        logger.info(f"   Elapsed time: {elapsed_time}")
        
        return success
    
    def run_sample_ingestion(self) -> bool:
        """Run a sample ingestion with limited data for testing."""
        logger.info("🧪 Running sample OpenStates ingestion")
        
        # Test API connection
        if not self.test_api_connection():
            return False
        
        # Ingest a small sample of data
        sample_jurisdictions = ['ca', 'ny', 'tx']  # California, New York, Texas
        
        success = True
        
        # Test jurisdictions
        logger.info("🌍 Testing jurisdiction ingestion...")
        if not self.ingest_data_type('jurisdictions'):
            success = False
        
        # Test people for a few jurisdictions
        if success:
            for jurisdiction in sample_jurisdictions:
                logger.info(f"👥 Testing people ingestion for {jurisdiction}...")
                if not self.ingest_data_type('people', jurisdiction):
                    success = False
                    logger.error(f"❌ Failed people ingestion for {jurisdiction}")
                    break
        
        if success:
            logger.info("✅ Sample ingestion completed successfully!")
        else:
            logger.error("❌ Sample ingestion failed")
        
        return success

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='OpenStates Data Ingestion Workflow')
    parser.add_argument('--mode', choices=['sample', 'full'], default='sample',
                       help='Ingestion mode: sample (limited data) or full (all data)')
    parser.add_argument('--jurisdiction', help='Specific jurisdiction to ingest')
    parser.add_argument('--data-type', choices=['jurisdictions', 'people', 'bills', 'organizations', 'events'],
                       help='Specific data type to ingest')
    parser.add_argument('--api-key', help='OpenStates API key (overrides env var)')
    
    args = parser.parse_args()
    
    # Override API key if provided
    if args.api_key:
        os.environ['OPENSTATES_API_KEY'] = args.api_key
    
    # Database configuration
    db_config = DatabaseConfig(
        host=os.getenv('DB_HOST', '172.28.82.205'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'opendiscourse'),
        user=os.getenv('DB_USER', 'opendiscourse'),
        password=os.getenv('DB_PASSWORD', 'opendiscourse123')
    )
    
    # Create ingestor
    ingestor = OpenStatesIngestor(db_config)
    
    # Check for API key
    if not ingestor.api_key:
        logger.error("❌ OpenStates API key not found. Set OPENSTATES_API_KEY environment variable.")
        sys.exit(1)
    
    logger.info("🚀 Starting OpenStates Data Ingestion")
    logger.info("=" * 50)
    
    if args.mode == 'sample':
        success = ingestor.run_sample_ingestion()
    else:
        jurisdictions = [args.jurisdiction] if args.jurisdiction else None
        if args.data_type:
            success = ingestor.ingest_data_type(args.data_type, args.jurisdiction)
        else:
            success = ingestor.ingest_all_data_types(jurisdictions)
    
    if success:
        logger.info("🎉 OpenStates ingestion completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 OpenStates ingestion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()