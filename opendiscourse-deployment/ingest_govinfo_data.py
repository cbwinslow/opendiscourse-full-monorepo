#!/usr/bin/env python3
"""
GovInfo.gov Data Ingestion Workflow
Ingests federal legislative data from GovInfo.gov API into the PostgreSQL database.
Supports bill data, actions, cosponsors, and committees.
"""

import os
import sys
import json
import time
import logging
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

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
        logging.FileHandler('govinfo_ingestion.log'),
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

class GovInfoIngestor:
    """GovInfo.gov data ingestion workflow."""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.api_key = os.getenv('GOVINFO_API_KEY', '')
        self.base_url = 'https://www.govinfo.gov'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OpenDiscourse-Ingestor/1.0'
        })
        
        # Data type configurations
        self.data_types = {
            'bills': {
                'collection': 'BILLS',
                'table': 'govinfo_bill',
                'xml_pattern': 'BILLS-*.xml'
            },
            'bill_actions': {
                'collection': 'BILLSTATUS',
                'table': 'govinfo_bill_action',
                'xml_pattern': 'BILLSTATUS-*.xml'
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
        """Test GovInfo API connection."""
        try:
            # Test basic connectivity
            response = self.session.get(f"{self.base_url}/app/search/", timeout=10)
            response.raise_for_status()
            logger.info("✅ GovInfo.gov connectivity successful")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ GovInfo.gov connection failed: {e}")
            return False
    
    def extract_bill_id_from_path(self, file_path: str) -> Optional[str]:
        """Extract bill ID from file path (e.g., BILLS-119hr1ih.xml -> H1-119)."""
        filename = os.path.basename(file_path)
        
        # Match pattern: BILLS-{congress}{type}{number}{stage}.xml
        if not filename.startswith("BILLS-") or not filename.endswith(".xml"):
            return None
        
        # Remove BILLS- and .xml
        parts = filename[6:-4]  # Remove 'BILLS-' and '.xml'
        
        try:
            # Parse congress number
            congress_end = 0
            while congress_end < len(parts) and parts[congress_end].isdigit():
                congress_end += 1
            
            congress = int(parts[:congress_end])
            remaining = parts[congress_end:]
            
            # Parse bill type (h or s)
            if remaining.startswith("h"):
                bill_type = "H"
                remaining = remaining[1:]
            elif remaining.startswith("s"):
                bill_type = "S"
                remaining = remaining[1:]
            else:
                return None
            
            # Skip any additional type indicators (like 'r' in 'hr1ih')
            if remaining.startswith("r"):
                remaining = remaining[1:]
            
            # Parse bill number
            number_end = 0
            while number_end < len(remaining) and remaining[number_end].isdigit():
                number_end += 1
            
            bill_number = remaining[:number_end]
            
            return f"{bill_type}{bill_number}-{congress}"
            
        except (ValueError, IndexError):
            return None
    
    def parse_bill_xml(self, xml_file: str) -> Optional[Dict[str, Any]]:
        """Parse GovInfo bill XML file and extract bill data."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Extract basic bill info
            bill_number_elem = root.find(".//billNumber")
            bill_number = ""
            bill_type = "H"  # default
            
            if bill_number_elem is not None:
                bill_number_text = bill_number_elem.text.strip()
                # Parse bill number like "H.R. 1" or "S. 2"
                if bill_number_text.startswith("H.R."):
                    bill_type = "H"
                    bill_number = "H" + bill_number_text.replace("H.R.", "").strip()
                elif bill_number_text.startswith("S."):
                    bill_type = "S"
                    bill_number = "S" + bill_number_text.replace("S.", "").strip()
                else:
                    bill_number = bill_number_text
            
            congress_elem = root.get("congress")
            congress = int(congress_elem) if congress_elem else 0
            
            title = self._text(root.find(".//officialTitle"))
            short_title = self._text(root.find(".//shortTitle"))
            summary = self._text(root.find(".//summaryText"))
            
            sponsor = None
            sponsor_elem = root.find(".//sponsor")
            if sponsor_elem is not None:
                sponsor = {
                    'name': self._text(sponsor_elem.find(".//fullName")) or "",
                    'party': self._text(sponsor_elem.find(".//party")),
                    'state': self._text(sponsor_elem.find(".//state")),
                }
            
            introduced_date = self._parse_datetime(self._text(root.find(".//introducedDate")))
            
            bill_print_no = bill_number.replace(" ", "")
            if not bill_print_no:
                logger.error(f"Missing bill number in XML: {xml_file}")
                return None
            
            return {
                'bill_print_no': bill_print_no,
                'session_year': congress,
                'bill_type': bill_type,
                'title': title,
                'short_title': short_title,
                'summary': summary,
                'congress': congress,
                'sponsor_name': sponsor['name'] if sponsor else None,
                'sponsor_party': sponsor['party'] if sponsor else None,
                'sponsor_state': sponsor['state'] if sponsor else None,
                'introduced_date': introduced_date,
                'active_version': "",
                'modified_date_time': datetime.now(),
                'source_url': f"file://{xml_file}",
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"XML parsing error for {xml_file}: {e}")
            return None
    
    def parse_bill_actions_xml(self, xml_file: str) -> List[Dict[str, Any]]:
        """Parse GovInfo bill actions XML file."""
        actions = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Find the associated bill
            bill_id_elem = root.find(".//billId")
            if bill_id_elem is None:
                logger.warning(f"No bill ID found in {xml_file}")
                return actions
            
            # This would need to be linked to the actual bill record
            # For now, we'll extract the actions
            
            for action_elem in root.findall(".//actions/action"):
                text_value = self._text(action_elem.find(".//text"))
                if not text_value:
                    continue
                    
                action = {
                    'action_code': self._text(action_elem.find(".//actionCode")),
                    'text': text_value,
                    'action_date': self._parse_datetime(self._text(action_elem.find(".//actionDate"))),
                    'sequence_no': int(self._text(action_elem.find(".//sequenceNumber")) or 0),
                    'chamber': self._text(action_elem.find(".//chamber")),
                    'created_at': datetime.now()
                }
                actions.append(action)
                
        except Exception as e:
            logger.error(f"Error parsing actions XML {xml_file}: {e}")
        
        return actions
    
    def _text(self, element: Optional[ET.Element]) -> Optional[str]:
        """Extract text from XML element."""
        if element is None or element.text is None:
            return None
        value = element.text.strip()
        return value or None
    
    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not value:
            return None
        value = value.strip()
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", ""))
        except ValueError:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        logger.warning("Unable to parse datetime '%s'", value)
        return None
    
    def insert_bill_batch(self, data: List[Dict[str, Any]]) -> bool:
        """Insert a batch of bill data into the database."""
        if not data:
            return True
        
        try:
            conn = self.get_database_connection()
            with conn.cursor() as cursor:
                # Build the INSERT query
                insert_query = """
                    INSERT INTO govinfo_bill (
                        bill_print_no, session_year, bill_type, title, short_title,
                        summary, congress, sponsor_name, sponsor_party, sponsor_state,
                        introduced_date, active_version, modified_date_time, source_url,
                        created_at, updated_at
                    ) VALUES %s
                    ON CONFLICT (congress, bill_print_no, session_year) DO UPDATE SET
                        title = EXCLUDED.title,
                        short_title = EXCLUDED.short_title,
                        summary = EXCLUDED.summary,
                        sponsor_name = EXCLUDED.sponsor_name,
                        sponsor_party = EXCLUDED.sponsor_party,
                        sponsor_state = EXCLUDED.sponsor_state,
                        introduced_date = EXCLUDED.introduced_date,
                        modified_date_time = EXCLUDED.modified_date_time,
                        updated_at = EXCLUDED.updated_at
                """
                
                # Prepare values
                columns = [
                    'bill_print_no', 'session_year', 'bill_type', 'title', 'short_title',
                    'summary', 'congress', 'sponsor_name', 'sponsor_party', 'sponsor_state',
                    'introduced_date', 'active_version', 'modified_date_time', 'source_url',
                    'created_at', 'updated_at'
                ]
                
                values = []
                for record in data:
                    row_values = []
                    for col in columns:
                        value = record.get(col)
                        if col in ['introduced_date', 'modified_date_time', 'created_at', 'updated_at']:
                            row_values.append(value)
                        else:
                            row_values.append(value)
                    values.append(tuple(row_values))
                
                # Execute batch insert
                execute_values(cursor, insert_query, values, template=None)
                conn.commit()
                
                logger.info(f"✅ Inserted {len(data)} bills into govinfo_bill")
                return True
                
        except psycopg2.Error as e:
            logger.error(f"❌ Database error for govinfo_bill: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error for govinfo_bill: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def insert_actions_batch(self, data: List[Dict[str, Any]]) -> bool:
        """Insert a batch of bill actions into the database."""
        if not data:
            return True
        
        try:
            conn = self.get_database_connection()
            with conn.cursor() as cursor:
                # Build the INSERT query
                insert_query = """
                    INSERT INTO govinfo_bill_action (
                        action_code, text, action_date, sequence_no, chamber, created_at
                    ) VALUES %s
                """
                
                # Prepare values
                columns = [
                    'action_code', 'text', 'action_date', 'sequence_no', 'chamber', 'created_at'
                ]
                
                values = []
                for record in data:
                    row_values = []
                    for col in columns:
                        value = record.get(col)
                        row_values.append(value)
                    values.append(tuple(row_values))
                
                # Execute batch insert
                execute_values(cursor, insert_query, values, template=None)
                conn.commit()
                
                logger.info(f"✅ Inserted {len(data)} actions into govinfo_bill_action")
                return True
                
        except psycopg2.Error as e:
            logger.error(f"❌ Database error for govinfo_bill_action: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error for govinfo_bill_action: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def process_xml_files(self, data_type: str, xml_dir: str) -> bool:
        """Process XML files for a specific data type."""
        if data_type not in self.data_types:
            logger.error(f"❌ Unknown data type: {data_type}")
            return False
        
        config = self.data_types[data_type]
        xml_pattern = config['xml_pattern']
        
        logger.info(f"🔄 Processing {data_type} XML files from {xml_dir}")
        
        # Find XML files
        xml_path = Path(xml_dir)
        if not xml_path.exists():
            logger.error(f"❌ XML directory does not exist: {xml_dir}")
            return False
        
        xml_files = list(xml_path.glob(xml_pattern))
        logger.info(f"📁 Found {len(xml_files)} XML files for {data_type}")
        
        if not xml_files:
            logger.warning(f"No XML files found matching pattern {xml_pattern}")
            return True
        
        processed = 0
        successful = 0
        
        for xml_file in xml_files:
            try:
                logger.info(f"📄 Processing {xml_file.name}")
                
                if data_type == 'bills':
                    # Parse bill data
                    bill_data = self.parse_bill_xml(str(xml_file))
                    if bill_data:
                        if self.insert_bill_batch([bill_data]):
                            successful += 1
                
                elif data_type == 'bill_actions':
                    # Parse bill actions
                    actions_data = self.parse_bill_actions_xml(str(xml_file))
                    if actions_data:
                        if self.insert_actions_batch(actions_data):
                            successful += len(actions_data)
                
                processed += 1
                
                # Update statistics
                self.stats['total_processed'] += 1
                self.stats['successful'] += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error processing {xml_file.name}: {e}")
                self.stats['failed'] += 1
                continue
        
        logger.info(f"✅ Completed {data_type}: {successful}/{processed} successful")
        return True
    
    def download_sample_bills(self, congress: int = 119, limit: int = 5) -> bool:
        """Download sample bill XML files for testing."""
        logger.info(f"📥 Downloading {limit} sample bill XML files for Congress {congress}")
        
        # Create output directory
        output_dir = Path("sample_govinfo_bills")
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Use GovInfo bulk data API
            url = f"{self.base_url}/bulkdata/BILLS/{congress}/BILLS.zip"
            
            logger.info(f"📥 Downloading from {url}")
            
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Save the zip file
            zip_path = output_dir / f"BILLS-{congress}.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract a few files for testing
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of bill files
                bill_files = [f for f in zip_ref.namelist() if f.startswith('BILLS/') and f.endswith('.xml')][:limit]
                
                for bill_file in bill_files:
                    # Extract just the filename
                    filename = os.path.basename(bill_file)
                    target_path = output_dir / filename
                    
                    with zip_ref.open(bill_file) as source, open(target_path, 'wb') as target:
                        target.write(source.read())
                    
                    logger.info(f"📄 Extracted {filename}")
            
            logger.info(f"✅ Downloaded sample bills to {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error downloading sample bills: {e}")
            return False
    
    def run_sample_ingestion(self) -> bool:
        """Run a sample ingestion with downloaded files."""
        logger.info("🧪 Running sample GovInfo ingestion")
        
        # Test API connection
        if not self.test_api_connection():
            return False
        
        # Download sample files
        if not self.download_sample_bills():
            logger.error("❌ Failed to download sample files")
            return False
        
        # Process the downloaded files
        xml_dir = "sample_govinfo_bills"
        
        # Process bills
        logger.info("📊 Processing bill files...")
        if not self.process_xml_files('bills', xml_dir):
            logger.error("❌ Failed to process bill files")
            return False
        
        # Process bill actions (if available)
        logger.info("⚖️ Processing bill status/action files...")
        if not self.process_xml_files('bill_actions', xml_dir):
            logger.warning("⚠️ Failed to process action files, but continuing")
        
        logger.info("✅ Sample ingestion completed successfully!")
        return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='GovInfo.gov Data Ingestion Workflow')
    parser.add_argument('--mode', choices=['sample', 'full'], default='sample',
                       help='Ingestion mode: sample (downloaded files) or full (processing directory)')
    parser.add_argument('--xml-dir', help='Directory containing XML files for processing')
    parser.add_argument('--data-type', choices=['bills', 'bill_actions'],
                       help='Specific data type to process')
    parser.add_argument('--congress', type=int, default=119,
                       help='Congress number for sample download')
    parser.add_argument('--limit', type=int, default=5,
                       help='Number of files to download for sample mode')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = DatabaseConfig(
        host=os.getenv('DB_HOST', '172.28.82.205'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'opendiscourse'),
        user=os.getenv('DB_USER', 'opendiscourse'),
        password=os.getenv('DB_PASSWORD', 'opendiscourse123')
    )
    
    # Create ingestor
    ingestor = GovInfoIngestor(db_config)
    
    logger.info("🚀 Starting GovInfo.gov Data Ingestion")
    logger.info("=" * 50)
    
    if args.mode == 'sample':
        success = ingestor.run_sample_ingestion()
    else:
        if not args.xml_dir:
            logger.error("❌ XML directory required for full mode. Use --xml-dir")
            sys.exit(1)
        
        if args.data_type:
            success = ingestor.process_xml_files(args.data_type, args.xml_dir)
        else:
            # Process all data types
            success = True
            for data_type in ingestor.data_types.keys():
                if not ingestor.process_xml_files(data_type, args.xml_dir):
                    success = False
                    logger.error(f"❌ Failed to process {data_type}")
    
    if success:
        logger.info("🎉 GovInfo.gov ingestion completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 GovInfo.gov ingestion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()