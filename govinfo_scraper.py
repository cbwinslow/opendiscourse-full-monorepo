import requests
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from xml.etree import ElementTree as ET

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('govinfo_scraper.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        dbname="opendiscourse",
        user="doc_user",
        password="doc_password123",
        host="localhost"
    )

def fetch_govinfo_metadata():
    """Fetch metadata from GovInfo API."""
    base_url = "https://api.govinfo.gov"
    api_key = os.getenv('GOVINFO_API_KEY')  # Add this to your .env file
    
    # Get collections
    collections_url = f"{base_url}/collections?api_key={api_key}"
    response = requests.get(collections_url)
    response.raise_for_status()
    collections = response.json()
    
    # Process each collection
    for collection in collections['collections']:
        collection_name = collection['collectionCode']
        
        # Get documents for collection
        documents_url = f"{base_url}/packages?collectionCode={collection_name}&api_key={api_key}"
        response = requests.get(documents_url)
        response.raise_for_status()
        documents = response.json()
        
        # Process each document
        for doc in documents['packages']:
            try:
                # Get document details
                doc_url = f"{base_url}/packages/{doc['packageId']}/summary?api_key={api_key}"
                doc_response = requests.get(doc_url)
                doc_response.raise_for_status()
                doc_details = doc_response.json()
                
                # Parse XML content if available
                content_url = f"{base_url}/packages/{doc['packageId']}/content-detail.xml?api_key={api_key}"
                content_response = requests.get(content_url)
                
                if content_response.status_code == 200:
                    try:
                        root = ET.fromstring(content_response.text)
                        content = ET.tostring(root, encoding='unicode')
                    except ET.ParseError:
                        content = content_response.text
                else:
                    content = ""  # No content available
                    
                # Get metadata
                metadata = {
                    'source': 'govinfo',
                    'package_id': doc['packageId'],
                    'collection': collection_name,
                    'title': doc_details.get('title', ''),
                    'date_issued': doc_details.get('dateIssued', ''),
                    'date_last_modified': doc_details.get('dateLastModified', ''),
                    'api_key': api_key,
                    'url': f"https://www.govinfo.gov/content/pkg/{doc['packageId']}/html/{doc['packageId']}.htm"
                }
                
                # Save to database
                save_document(doc_details.get('title', ''), content, metadata)
                
                logging.info(f"Processed document: {doc['packageId']}")
                
            except Exception as e:
                logging.error(f"Error processing document {doc['packageId']}: {str(e)}")

def save_document(title, content, metadata):
    """Save document to PostgreSQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert document
        cursor.execute("""
            INSERT INTO documents (title, content, metadata, created_at, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
        """, (title, content, metadata))
        
        doc_id = cursor.fetchone()[0]
        conn.commit()
        
        logging.info(f"Saved document with ID: {doc_id}")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error saving document: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function to run the scraper."""
    logging.info("Starting GovInfo document scraping...")
    fetch_govinfo_metadata()
    logging.info("GovInfo document scraping completed")

if __name__ == "__main__":
    main()
