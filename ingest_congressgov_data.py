#!/usr/bin/env python3
"""
Congress.gov Data Ingestion Workflow
Ingests federal legislative data from Congress.gov API into the PostgreSQL database.
Supports multiple data types: members, bills, committees, hearings, records, etc.
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
        logging.FileHandler('congressgov_ingestion.log'),
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

class CongressGovIngestor:
    """Congress.gov data ingestion workflow."""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.api_key = os.getenv('CONGRESS_API_KEY', '')
        self.base_url = 'https://api.congress.gov/v3'
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'User-Agent': 'OpenDiscourse-Ingestor/1.0'
        })
        
        # Data type configurations
        self.data_types = {
            'members': {
                'endpoint': '/member',
                'table': 'federal_members',
                'batch_size': 50
            },
            'bills': {
                'endpoint': '/bill',
                'table': 'federal_bills',
                'batch_size': 100
            },
            'committees': {
                'endpoint': '/committee',
                'table': 'federal_committees',
                'batch_size': 100
            },
            'hearings': {
                'endpoint': '/hearing',
                'table': 'federal_hearings',
                'batch_size': 100
            },
            'records': {
                'endpoint': '/congressional-record',
                'table': 'federal_records',
                'batch_size': 100
            },
            'register': {
                'endpoint': '/federal-register',
                'table': 'federal_register_docs',
                'batch_size': 100
            },
            'laws': {
                'endpoint': '/law',
                'table': 'federal_laws',
                'batch_size': 100
            },
            'nominations': {
                'endpoint': '/nomination',
                'table': 'federal_nominations',
                'batch_size': 100
            },
            'treaties': {
                'endpoint': '/treaty',
                'table': 'federal_treaties',
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
        """Test Congress.gov API connection."""
        try:
            response = self.session.get(f"{self.base_url}/member", params={'limit': 1})
            response.raise_for_status()
            logger.info("✅ Congress.gov API connection successful")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Congress.gov API connection failed: {e}")
            return False
    
    def fetch_data_batch(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Fetch a batch of data from Congress.gov API."""
        if params is None:
            params = {}
        
        params.update({
            'api_key': self.api_key,
            'format': 'json',
            'limit': 100
        })
        
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract results based on endpoint
            endpoint_key = endpoint.lstrip('/').split('/')[0]
            return data.get(endpoint_key, [])
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return []
    
    def map_member_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov member data to database schema."""
        member = item.get('member', {})
        social_media = {
            "twitter": member.get("twitterAccount"),
            "facebook": member.get("facebookAccount"),
            "youtube": member.get("youtubeAccount"),
        }
        
        return {
            'bioguide_id': member.get('bioguideId'),
            'full_name': member.get('name'),
            'first_name': member.get('firstName'),
            'last_name': member.get('lastName'),
            'party': member.get('party'),
            'state': member.get('state'),
            'chamber': (member.get('chamber') or '').lower() or None,
            'current_member': bool(member.get('currentMember', False)),
            'terms': json.dumps(member.get('terms', [])),
            'committees': json.dumps(member.get('committees', [])),
            'social_media': json.dumps(social_media),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_bill_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov bill data to database schema."""
        bill = item.get('bill', {})
        sponsors = bill.get('sponsors', []) or []
        actions = bill.get('actions', []) or []
        doc_type = 'bill'
        amends_url = None
        amendment_num = None
        
        if 'amendment' in item:
            doc_type = 'amendment'
            amends_url = item.get('amendsBill', {}).get('url')
            amendment_num = item.get('amendmentNumber')
        elif bill.get('type') in ['hres', 'sres', 'hjres', 'sjres']:
            doc_type = 'resolution'
        
        return {
            'source_url': item.get('url', ''),
            'congress': item.get('congress'),
            'document_type': doc_type,
            'title': bill.get('title'),
            'summary': bill.get('summary', ''),
            'date_local': item.get('sessionYear') or item.get('session_year'),
            'metadata': json.dumps(item),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now(),
            # Bill-specific fields
            'print_no': f"{bill.get('type', '')}{bill.get('number', '')}",
            'session_year': item.get('sessionYear') or item.get('session_year'),
            'bill_type': bill.get('type'),
            'number': bill.get('number'),
            'sponsor': sponsors[0].get('name') if sponsors else None,
            'status': bill.get('status', ''),
            'introduced_date': bill.get('dateOfIntroduction'),
            'amends_source_url': amends_url,
            'amendment_number': amendment_num
        }
    
    def map_committee_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov committee data to database schema."""
        committee = item.get('committee', {})
        members = committee.get('members', []) or []
        
        return {
            'committee_code': committee.get('committeeCode'),
            'name': committee.get('name'),
            'chamber': committee.get('chamber', '').lower(),
            'type': committee.get('type'),
            'jurisdiction': committee.get('jurisdiction', ''),
            'members': json.dumps([{"name": m.get('name'), "role": m.get('role')} for m in members]),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_hearing_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov hearing data to database schema."""
        hearing = item.get('hearing', {})
        witnesses = hearing.get('witnesses', []) or []
        
        return {
            'hearing_id': hearing.get('hearingId'),
            'congress': item.get('congress'),
            'committee_code': hearing.get('committee', {}).get('systemCode'),
            'date': hearing.get('hearingDate'),
            'location': hearing.get('location', ''),
            'witnesses': json.dumps([{"name": w.get('name'), "title": w.get('title')} for w in witnesses]),
            'summary': hearing.get('summary', ''),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_record_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov record data to database schema."""
        record = item.get('congressionalRecord', {})
        
        return {
            'record_id': record.get('recordId'),
            'congress': item.get('congress'),
            'date': record.get('date'),
            'chamber': record.get('chamber', '').lower(),
            'speakers': json.dumps(record.get('speakers', [])),
            'text': record.get('text', ''),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_register_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov register data to database schema."""
        register = item.get('federalRegister', {})
        agencies = register.get('agencies', []) or []
        
        return {
            'docket_id': register.get('docketId'),
            'congress': item.get('congress'),
            'agencies': json.dumps([{"name": a.get('name')} for a in agencies]),
            'publication_date': register.get('publicationDate'),
            'text': register.get('text', ''),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_law_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov law data to database schema."""
        law = item.get('law', {})
        sections = law.get('sections', []) or []
        
        return {
            'public_law_number': law.get('publicLawNumber'),
            'congress': item.get('congress'),
            'sections': json.dumps([{"number": s.get('number'), "text": s.get('text')} for s in sections]),
            'enacted_date': law.get('enactedDate'),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_nomination_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov nomination data to database schema."""
        nomination = item.get('nomination', {})
        
        return {
            'nomination_number': nomination.get('nominationNumber'),
            'congress': item.get('congress'),
            'nominee_name': nomination.get('nomineeName'),
            'position': nomination.get('position'),
            'status': nomination.get('status'),
            'committee': nomination.get('committee', {}).get('name', ''),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def map_treaty_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map Congress.gov treaty data to database schema."""
        treaty = item.get('treaty', {})
        signatories = treaty.get('signatories', []) or []
        
        return {
            'treaty_doc_number': treaty.get('treatyDocNumber'),
            'congress': item.get('congress'),
            'title': treaty.get('title'),
            'status': treaty.get('status'),
            'signatories': json.dumps([{"country": s.get('country'), "date": s.get('date')} for s in signatories]),
            'source_url': item.get('url', ''),
            'source': 'federal',
            'ingested_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def get_mapper(self, data_type: str):
        """Get the appropriate data mapper."""
        mappers = {
            'members': self.map_member_data,
            'bills': self.map_bill_data,
            'committees': self.map_committee_data,
            'hearings': self.map_hearing_data,
            'records': self.map_record_data,
            'register': self.map_register_data,
            'laws': self.map_law_data,
            'nominations': self.map_nomination_data,
            'treaties': self.map_treaty_data
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
                if table == 'federal_bills':
                    # Special handling for bills table with composite unique constraint
                    insert_query = f"""
                        INSERT INTO {table} ({', '.join(columns)}) 
                        VALUES %s
                        ON CONFLICT (source_url) DO UPDATE SET
                            updated_at = EXCLUDED.updated_at,
                            metadata = EXCLUDED.metadata
                    """
                elif table == 'federal_members':
                    # Special handling for members table with bioguide_id unique constraint
                    insert_query = f"""
                        INSERT INTO {table} ({', '.join(columns)}) 
                        VALUES %s
                        ON CONFLICT (bioguide_id) DO UPDATE SET
                            updated_at = EXCLUDED.updated_at,
                            terms = EXCLUDED.terms,
                            committees = EXCLUDED.committees
                    """
                else:
                    # Generic handling for other tables
                    insert_query = f"""
                        INSERT INTO {table} ({', '.join(columns)}) 
                        VALUES %s
                        ON CONFLICT DO NOTHING
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
    
    def ingest_data_type(self, data_type: str, congress: int = 119) -> bool:
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
        
        logger.info(f"🔄 Starting ingestion of {data_type} for Congress {congress}")
        
        # Build API parameters
        params = {'congress': congress}
        
        offset = 0
        total_processed = 0
        successful = 0
        
        while True:
            logger.info(f"📄 Fetching {data_type} batch at offset {offset}")
            
            # Add pagination
            current_params = params.copy()
            current_params.update({
                'limit': config['batch_size'],
                'offset': offset
            })
            
            # Fetch data
            batch_data = self.fetch_data_batch(endpoint, current_params)
            
            if not batch_data:
                logger.info(f"📄 No more data for {data_type} (offset {offset})")
                break
            
            # Map data
            mapped_data = []
            for item in batch_data:
                try:
                    mapped_item = mapper(item)
                    if mapped_item and self._has_required_fields(mapped_item, table):
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
            offset += config['batch_size']
            
            # Rate limiting
            time.sleep(0.5)
        
        # Update statistics
        self.stats['total_processed'] += total_processed
        self.stats['successful'] += successful
        
        logger.info(f"✅ Completed {data_type}: {successful}/{total_processed} successful")
        return True
    
    def _has_required_fields(self, record: Dict[str, Any], table: str) -> bool:
        """Check if record has required fields for the table."""
        if table == 'federal_members':
            return bool(record.get('bioguide_id'))
        elif table == 'federal_bills':
            return bool(record.get('source_url'))
        elif table == 'federal_committees':
            return bool(record.get('committee_code'))
        else:
            return True  # Default: assume record is valid
    
    def ingest_all_data_types(self, congress: int = 119) -> bool:
        """Ingest all data types for the specified Congress."""
        if not self.test_api_connection():
            return False
        
        logger.info(f"🚀 Starting comprehensive Congress.gov data ingestion for Congress {congress}")
        
        success = True
        
        # Define ingestion order (members and committees first as they may be referenced by other data)
        priority_order = ['members', 'committees', 'bills', 'hearings', 'records', 'register', 'laws', 'nominations', 'treaties']
        
        for data_type in priority_order:
            if data_type in self.data_types:
                if success:  # Only continue if previous types were successful
                    logger.info(f"🏛️ Ingesting {data_type}...")
                    if not self.ingest_data_type(data_type, congress):
                        success = False
                        logger.error(f"❌ Failed to ingest {data_type}")
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
    
    def run_sample_ingestion(self, congress: int = 119) -> bool:
        """Run a sample ingestion with limited data for testing."""
        logger.info("🧪 Running sample Congress.gov ingestion")
        
        # Test API connection
        if not self.test_api_connection():
            return False
        
        # Test with members first (simplest data type)
        logger.info("👥 Testing member ingestion...")
        if not self.ingest_data_type('members', congress):
            logger.error("❌ Sample member ingestion failed")
            return False
        
        # Test with a small batch of committees
        logger.info("🏛️ Testing committee ingestion...")
        if not self.ingest_data_type('committees', congress):
            logger.error("❌ Sample committee ingestion failed")
            return False
        
        logger.info("✅ Sample ingestion completed successfully!")
        return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Congress.gov Data Ingestion Workflow')
    parser.add_argument('--mode', choices=['sample', 'full'], default='sample',
                       help='Ingestion mode: sample (limited data) or full (all data)')
    parser.add_argument('--congress', type=int, default=119,
                       help='Congress number (e.g., 119 for 2025-2027)')
    parser.add_argument('--data-type', choices=['members', 'bills', 'committees', 'hearings', 'records', 'register', 'laws', 'nominations', 'treaties'],
                       help='Specific data type to ingest')
    parser.add_argument('--api-key', help='Congress.gov API key (overrides env var)')
    
    args = parser.parse_args()
    
    # Override API key if provided
    if args.api_key:
        os.environ['CONGRESS_API_KEY'] = args.api_key
    
    # Database configuration
    db_config = DatabaseConfig(
        host=os.getenv('DB_HOST', '172.28.82.205'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'opendiscourse'),
        user=os.getenv('DB_USER', 'opendiscourse'),
        password=os.getenv('DB_PASSWORD', 'opendiscourse123')
    )
    
    # Create ingestor
    ingestor = CongressGovIngestor(db_config)
    
    # Check for API key
    if not ingestor.api_key:
        logger.error("❌ Congress.gov API key not found. Set CONGRESS_API_KEY environment variable.")
        sys.exit(1)
    
    logger.info("🚀 Starting Congress.gov Data Ingestion")
    logger.info("=" * 50)
    
    if args.mode == 'sample':
        success = ingestor.run_sample_ingestion(args.congress)
    else:
        if args.data_type:
            success = ingestor.ingest_data_type(args.data_type, args.congress)
        else:
            success = ingestor.ingest_all_data_types(args.congress)
    
    if success:
        logger.info("🎉 Congress.gov ingestion completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Congress.gov ingestion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()