import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import time
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrape_documents.log'),
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

def scrape_government_db():
    """Scrape documents from the government database."""
    base_url = f"https://api.govinfo.gov/v1/packages?collectionCode=BILLS&offset=0&pageSize=10&api_key={os.getenv('GOVINFO_API_KEY')}"  # Using packages endpoint with smaller page size  # Using packages endpoint with proper parameters  # Using bulkdata endpoint with proper parameters  # Using bulkdata endpoint for BILLS collection  # BILLS collection endpoint
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'OpenDiscourse/1.0',
        'X-Api-Key': os.getenv('GOVINFO_API_KEY')
    }
    
    try:
        # Get the packages list
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Process each document
        for package in data.get('packages', []):
            doc_id = package.get('packageId')
            if not doc_id:
                continue
            
            # Get the document details
            doc_url = f"https://api.govinfo.gov/v1/packages/{doc_id}/content?api_key={os.getenv('GOVINFO_API_KEY')}"
            try:
                doc_response = requests.get(doc_url, headers=headers, timeout=10)
                doc_response.raise_for_status()
                doc_response.raise_for_status()
                
                # Save the document
                save_document(
                    title=package.get('title', ''),
                    content=doc_response.text,
                    metadata={
                        'package_id': doc_id,
                        'collection': package.get('collectionCode'),
                        'date': package.get('granuleDate'),
                        'type': package.get('documentType')
                    }
                )
                logging.info(f"Successfully saved document {doc_id}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt failed for {doc_url}: {str(e)}")
                continue
                
            try:
                # Get document details
                doc_response = requests.get(doc_url)
                doc_response.raise_for_status()
                
                # Parse document page
                doc_soup = BeautifulSoup(doc_response.text, 'html.parser')
                title = doc_soup.find('h1').text.strip()
                content = doc_soup.find('div', class_='document-content').text.strip()
                
                # Get metadata
                metadata = {
                    'source': 'government_database',
                    'url': doc_url,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Save to database
                save_document(title, content, metadata)
                
                logging.info(f"Successfully processed document: {title}")
                
            except Exception as e:
                logging.error(f"Error processing document {doc_url}: {str(e)}")
                
    except Exception as e:
        logging.error(f"Error scraping government database: {str(e)}")

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
    logging.info("Starting document scraping...")
    scrape_government_db()
    logging.info("Document scraping completed")

if __name__ == "__main__":
    main()
