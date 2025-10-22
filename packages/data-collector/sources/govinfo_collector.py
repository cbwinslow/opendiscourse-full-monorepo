"""
GovInfo.gov Data Collection Module

This module handles the collection of data from GovInfo.gov and stores it in the database.
"""

import os
import sys
import logging
from typing import Dict, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
import requests
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.opendiscourse.govinfo_api import create_govinfo_client, GovInfoAPI
from opendiscourse.opendiscourse.unified_api import UnifiedAPISuite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GovInfoDataCollector:
    """Handles collection of data from GovInfo.gov."""
    
    def __init__(self, db_connection_string: str):
        """
        Initialize the GovInfo.gov data collector.
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.client = create_govinfo_client()
        self.db_conn = psycopg2.connect(db_connection_string)
        self.db_conn.autocommit = False
        
    def collect_bulk_data_info(self) -> None:
        """
        Collect information about available bulk data collections from GovInfo.gov.
        """
        logger.info("Collecting bulk data collection information from GovInfo.gov")
        
        try:
            collections_data = self.client.get_bulk_data_collections()
            collections = collections_data.get('collections', [])
            
            cursor = self.db_conn.cursor()
            
            # Store collection information in the database
            for collection_name in collections:
                # Create a unique jurisdiction ID for federal collections
                jurisdiction_id = "ocd-jurisdiction/country:us/government"
                
                # Insert or update jurisdiction
                cursor.execute("""
                    INSERT INTO jurisdictions (id, name, classification, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        classification = EXCLUDED.classification,
                        updated_at = EXCLUDED.updated_at
                """, (
                    jurisdiction_id,
                    "United States Federal Government",
                    "country",
                    datetime.now(),
                    datetime.now()
                ))
                
                # Log the available collection
                logger.info(f"Available collection: {collection_name}")
            
            self.db_conn.commit()
            cursor.close()
            logger.info(f"Collected information for {len(collections)} bulk data collections from GovInfo.gov")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting bulk data information: {e}")
            raise
    
    def collect_collection_data(self, collection: str, year: Optional[str] = None) -> None:
        """
        Collect data for a specific collection from GovInfo.gov.
        
        Args:
            collection: Collection name (e.g., "CFR", "FR", "USCODE")
            year: Year for the collection (if applicable)
        """
        logger.info(f"Collecting data for {collection} collection from GovInfo.gov")
        
        try:
            collection_data = self.client.get_collection_data(collection, year)
            
            # For now, we'll just log the collection data
            # In a real implementation, we would parse and store the actual documents
            logger.info(f"Collection data for {collection}: {collection_data}")
            
            # Store metadata about the collection in the database
            cursor = self.db_conn.cursor()
            
            # Create a unique session ID for this collection/year
            session_id = f"govinfo-{collection}"
            if year:
                session_id += f"-{year}"
            
            # Insert or update session
            cursor.execute("""
                INSERT INTO legislative_sessions (id, jurisdiction_id, identifier, name, classification, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    identifier = EXCLUDED.identifier,
                    name = EXCLUDED.name,
                    classification = EXCLUDED.classification,
                    updated_at = EXCLUDED.updated_at
            """, (
                session_id,
                "ocd-jurisdiction/country:us/government",  # Federal jurisdiction
                session_id,
                f"{collection} Collection" + (f" {year}" if year else ""),
                "collection",
                datetime.now(),
                datetime.now()
            ))
            
            self.db_conn.commit()
            cursor.close()
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error collecting collection data: {e}")
            raise
    
    def collect_documents_via_link_service(self, collection: str, params: Dict) -> None:
        """
        Collect documents using the GovInfo link service.
        
        Args:
            collection: Collection name
            params: Parameters for the link service
        """
        logger.info(f"Collecting documents from {collection} via GovInfo link service")
        
        try:
            # Create link service URL
            link_url = self.client.create_link_service_url(collection, params)
            logger.info(f"Link service URL: {link_url}")
            
            # For now, we'll just log the URL
            # In a real implementation, we would fetch and parse the document
            logger.info(f"Would fetch document from: {link_url}")
            
        except Exception as e:
            logger.error(f"Error creating link service URL: {e}")
            raise
    
    def collect_rss_feed(self, collection: str) -> None:
        """
        Collect RSS feed for a collection from GovInfo.gov.
        
        Args:
            collection: Collection name
        """
        logger.info(f"Collecting RSS feed for {collection} from GovInfo.gov")
        
        try:
            rss_url = self.client.get_rss_feed(collection)
            logger.info(f"RSS feed URL: {rss_url}")
            
            # Fetch RSS feed
            response = requests.get(rss_url)
            response.raise_for_status()
            
            # For now, we'll just log that we got the RSS feed
            # In a real implementation, we would parse the RSS and extract documents
            logger.info(f"RSS feed content length: {len(response.text)}")
            
        except Exception as e:
            logger.error(f"Error collecting RSS feed: {e}")
            raise
    
    def collect_congressional_documents(self, congress: str, doc_type: str) -> None:
        """
        Collect congressional documents like bills, resolutions, etc.
        
        Args:
            congress: Congress number (e.g., "117")
            doc_type: Document type (e.g., "bills", "resolutions", "laws")
        """
        logger.info(f"Collecting {doc_type} for Congress {congress} from GovInfo.gov")
        
        try:
            # Use link service to get documents
            params = {
                "congress": congress
            }
            
            # Create link service URL
            link_url = self.client.create_link_service_url(doc_type, params)
            logger.info(f"Link service URL for {doc_type}: {link_url}")
            
            # For now, we'll just log the URL
            # In a real implementation, we would fetch and parse the documents
            logger.info(f"Would fetch {doc_type} from: {link_url}")
            
        except Exception as e:
            logger.error(f"Error collecting congressional documents: {e}")
            raise
    
    def collect_federal_register_documents(self, year: str, month: Optional[str] = None) -> None:
        """
        Collect Federal Register documents.
        
        Args:
            year: Year
            month: Month (optional)
        """
        logger.info(f"Collecting Federal Register documents for {year}" + (f"-{month}" if month else ""))
        
        try:
            # Use bulk data collection
            collection_data = self.client.get_collection_data("FR", year)
            logger.info(f"Federal Register collection data: {collection_data}")
            
        except Exception as e:
            logger.error(f"Error collecting Federal Register documents: {e}")
            raise
    
    def collect_code_of_federal_regulations(self, title: str, year: str) -> None:
        """
        Collect Code of Federal Regulations documents.
        
        Args:
            title: CFR title number
            year: Year
        """
        logger.info(f"Collecting CFR Title {title} for {year}")
        
        try:
            # Use link service to get specific CFR title
            params = {
                "title": title,
                "year": year
            }
            
            # Create link service URL
            link_url = self.client.create_link_service_url("CFR", params)
            logger.info(f"CFR link service URL: {link_url}")
            
            # For now, we'll just log the URL
            # In a real implementation, we would fetch and parse the CFR content
            logger.info(f"Would fetch CFR Title {title} from: {link_url}")
            
        except Exception as e:
            logger.error(f"Error collecting CFR documents: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.db_conn:
            self.db_conn.close()

# Example usage
if __name__ == "__main__":
    # Example of how to use the GovInfo.gov data collector
    # collector = GovInfoDataCollector(
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse"
    # )
    # 
    # # Collect bulk data information
    # collector.collect_bulk_data_info()
    # 
    # # Collect a specific collection
    # collector.collect_collection_data("FR", "2021")
    # 
    # # Collect via link service
    # collector.collect_documents_via_link_service("CFR", {"title": "26", "part": "1"})
    # 
    # # Collect RSS feed
    # collector.collect_rss_feed("FR")
    # 
    # collector.close()
    pass