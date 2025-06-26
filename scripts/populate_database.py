import logging
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from scrape_documents import scrape_documents

from opendiscourse.services.entity_extractor import process_document

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("populate_database.log"), logging.StreamHandler()],
)

# Load environment variables
load_dotenv()


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )


def create_tables():
    """Create necessary database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Create documents table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT,
                title TEXT,
                source_url TEXT,
                source_id TEXT,
                source_type TEXT,
                source_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create entities table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id SERIAL PRIMARY KEY,
                text TEXT,
                entity_type TEXT,
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create entity_mentions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_mentions (
                id SERIAL PRIMARY KEY,
                document_id INTEGER REFERENCES documents(id),
                entity_id INTEGER REFERENCES entities(id),
                start_index INTEGER,
                end_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create entity_relationships table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_relationships (
                id SERIAL PRIMARY KEY,
                entity1_id INTEGER REFERENCES entities(id),
                entity2_id INTEGER REFERENCES entities(id),
                relationship_type TEXT,
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        logging.info("Database tables created successfully")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error creating tables: {e!s}")
        raise
    finally:
        cursor.close()
        conn.close()


def populate_database():
    """Scrape documents and process them for entities."""
    # Scrape documents
    logging.info("Starting document scraping...")
    scrape_documents()

    # Process documents for entities
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Get all documents
        cursor.execute(
            "SELECT id, content, title, source_url, source_id, source_type, source_date FROM documents"
        )
        documents = cursor.fetchall()

        for doc in documents:
            logging.info(f"Processing document {doc['id']}: {doc['title']}")
            try:
                # Process document for entities
                process_document(
                    document_id=doc["id"],
                    content=doc["content"],
                    metadata={
                        "title": doc["title"],
                        "source_url": doc["source_url"],
                        "source_id": doc["source_id"],
                        "source_type": doc["source_type"],
                        "source_date": doc["source_date"],
                    },
                )
            except Exception as e:
                logging.error(f"Error processing document {doc['id']}: {e!s}")
                continue

        logging.info("Database population completed")

    except Exception as e:
        logging.error(f"Error populating database: {e!s}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Create tables
    create_tables()

    # Populate database
    populate_database()
