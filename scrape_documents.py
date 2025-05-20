import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Set up logging
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
    base_url = "https://www.govt.example.com/documents"  # Replace with actual URL
    
    try:
        # Get the main documents page
        response = requests.get(base_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all document links
        document_links = soup.find_all('a', class_='document-link')
        
        # Process each document
        for link in document_links:
            doc_url = link.get('href')
            if not doc_url:
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
