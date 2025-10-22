"""
Unified Data Collection Manager

This module coordinates data collection from all government data sources.
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

from opendiscourse.data_collection.openstates_collector import OpenStatesDataCollector
from opendiscourse.data_collection.congress_gov_collector import CongressGovDataCollector
from opendiscourse.data_collection.openlegislation_collector import OpenLegislationDataCollector
from opendiscourse.data_collection.govinfo_collector import GovInfoDataCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedDataCollector:
    """Coordinates data collection from all government data sources."""
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize the unified data collector.
        
        Args:
            config: Configuration dictionary with API keys and database connection string
        """
        self.config = config
        self.db_connection_string = config.get('db_connection_string')
        
        # Initialize collectors for each data source
        self.openstates_collector = None
        self.congress_gov_collector = None
        self.openlegislation_collector = None
        self.govinfo_collector = None
        
        # Create collectors based on available configuration
        if config.get('openstates_api_key'):
            self.openstates_collector = OpenStatesDataCollector(
                config.get('openstates_api_key'),
                self.db_connection_string
            )
        
        if config.get('congress_gov_api_key'):
            self.congress_gov_collector = CongressGovDataCollector(
                config.get('congress_gov_api_key'),
                self.db_connection_string
            )
        
        if config.get('openlegislation_api_key'):
            self.openlegislation_collector = OpenLegislationDataCollector(
                config.get('openlegislation_api_key'),
                self.db_connection_string
            )
        
        self.govinfo_collector = GovInfoDataCollector(self.db_connection_string)
        
        logger.info("Unified data collector initialized")
    
    def collect_all_jurisdictions(self) -> None:
        """
        Collect jurisdictions from all available data sources.
        """
        logger.info("Collecting jurisdictions from all data sources")
        
        # Collect from OpenStates (state jurisdictions)
        if self.openstates_collector:
            try:
                self.openstates_collector.collect_jurisdictions()
            except Exception as e:
                logger.error(f"Error collecting jurisdictions from OpenStates: {e}")
        
        # Collect federal jurisdiction information
        try:
            # Federal jurisdiction is handled in other collectors
            # but we can add a record for it here
            self._insert_federal_jurisdiction()
        except Exception as e:
            logger.error(f"Error inserting federal jurisdiction: {e}")
    
    def _insert_federal_jurisdiction(self) -> None:
        """
        Insert federal jurisdiction record into the database.
        """
        if not self.db_connection_string:
            return
            
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                INSERT INTO jurisdictions (id, name, classification, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    classification = EXCLUDED.classification,
                    updated_at = EXCLUDED.updated_at
            """, (
                "ocd-jurisdiction/country:us/government",
                "United States Federal Government",
                "country",
                datetime.now(),
                datetime.now()
            ))
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
        except Exception as e:
            logger.error(f"Error inserting federal jurisdiction: {e}")
            raise
    
    def collect_people(self, jurisdiction_id: Optional[str] = None) -> None:
        """
        Collect people from all available data sources.
        
        Args:
            jurisdiction_id: Optional jurisdiction ID to filter by
        """
        logger.info("Collecting people from all data sources")
        
        # Collect from OpenStates (state legislators)
        if self.openstates_collector:
            try:
                self.openstates_collector.collect_people(jurisdiction_id)
            except Exception as e:
                logger.error(f"Error collecting people from OpenStates: {e}")
        
        # Collect from Congress.gov (federal legislators)
        if self.congress_gov_collector:
            try:
                # Collect current Congress members
                # This would need to be called for each Congress and chamber
                pass  # Implementation would require specific Congress/chamber parameters
            except Exception as e:
                logger.error(f"Error collecting people from Congress.gov: {e}")
    
    def collect_bills(self, jurisdiction_id: Optional[str] = None, 
                     session: Optional[str] = None) -> None:
        """
        Collect bills from all available data sources.
        
        Args:
            jurisdiction_id: Optional jurisdiction ID to filter by
            session: Optional session identifier
        """
        logger.info("Collecting bills from all data sources")
        
        # Collect from OpenStates (state bills)
        if self.openstates_collector:
            try:
                if jurisdiction_id:
                    self.openstates_collector.collect_bills(jurisdiction_id, session)
                else:
                    # Collect from a few sample jurisdictions
                    # In a real implementation, this would iterate through all jurisdictions
                    pass
            except Exception as e:
                logger.error(f"Error collecting bills from OpenStates: {e}")
        
        # Collect from Congress.gov (federal bills)
        if self.congress_gov_collector:
            try:
                # Collect introduced bills from recent Congress
                # This would need to be called with specific parameters
                pass  # Implementation would require specific Congress/bill_type parameters
            except Exception as e:
                logger.error(f"Error collecting bills from Congress.gov: {e}")
        
        # Collect from OpenLegislation (NY state bills)
        if self.openlegislation_collector:
            try:
                # Collect bills for recent years
                current_year = datetime.now().year
                for year in range(current_year - 1, current_year + 1):
                    self.openlegislation_collector.collect_bills(str(year))
            except Exception as e:
                logger.error(f"Error collecting bills from OpenLegislation: {e}")
        
        # Collect from GovInfo.gov (federal documents)
        if self.govinfo_collector:
            try:
                # Collect information about bulk data collections
                self.govinfo_collector.collect_bulk_data_info()
            except Exception as e:
                logger.error(f"Error collecting bulk data info from GovInfo.gov: {e}")
    
    def collect_votes(self, member_id: Optional[str] = None) -> None:
        """
        Collect votes from all available data sources.
        
        Args:
            member_id: Optional member ID to filter by
        """
        logger.info("Collecting votes from all data sources")
        
        # Collect from Congress.gov (federal votes)
        if self.congress_gov_collector and member_id:
            try:
                self.congress_gov_collector.collect_votes(member_id)
            except Exception as e:
                logger.error(f"Error collecting votes from Congress.gov: {e}")
        
        # Collect from OpenLegislation (NY state votes)
        # Votes are collected along with bills in the OpenLegislation collector
    
    def collect_events(self) -> None:
        """
        Collect events (meetings, sessions) from all available data sources.
        """
        logger.info("Collecting events from all data sources")
        
        # Collect from OpenLegislation (NY state meetings)
        if self.openlegislation_collector:
            try:
                # This would require specific dates to collect meetings
                # In a real implementation, we would iterate through recent dates
                pass
            except Exception as e:
                logger.error(f"Error collecting events from OpenLegislation: {e}")
    
    def collect_all_data(self) -> None:
        """
        Collect all available data from all sources.
        """
        logger.info("Starting full data collection from all sources")
        
        try:
            # Collect jurisdictions first
            self.collect_all_jurisdictions()
            
            # Collect people
            self.collect_people()
            
            # Collect bills
            self.collect_bills()
            
            # Collect events
            self.collect_events()
            
            logger.info("Full data collection completed successfully")
            
        except Exception as e:
            logger.error(f"Error during full data collection: {e}")
            raise
    
    def close(self) -> None:
        """Close all database connections."""
        if self.openstates_collector:
            self.openstates_collector.close()
        if self.congress_gov_collector:
            self.congress_gov_collector.close()
        if self.openlegislation_collector:
            self.openlegislation_collector.close()
        if self.govinfo_collector:
            self.govinfo_collector.close()

# Example usage and configuration
def get_default_config() -> Dict[str, str]:
    """
    Get default configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    return {
        'openstates_api_key': os.getenv('OPENSTATES_API_KEY', ''),
        'congress_gov_api_key': os.getenv('CONGRESS_GOV_API_KEY', ''),
        'openlegislation_api_key': os.getenv('OPENLEGISLATION_API_KEY', ''),
        'db_connection_string': os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/opendiscourse')
    }

# Example usage
if __name__ == "__main__":
    # Example of how to use the unified data collector
    # config = get_default_config()
    # collector = UnifiedDataCollector(config)
    # 
    # # Collect all data
    # collector.collect_all_data()
    # 
    # collector.close()
    pass