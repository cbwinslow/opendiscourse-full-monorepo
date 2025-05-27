import difflib
import hashlib
import json
import logging
import os
from typing import Any, Dict, Optional
from xml.etree import ElementTree as ET

import psycopg2
import requests
import xmlschema
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("govinfo_document_processor.log"),
        logging.StreamHandler(),
    ],
)

# Load environment variables
load_dotenv()

# Define collection types
COLLECTION_TYPES = {
    "BILLS": "Bills",
    "CFR": "Code of Federal Regulations",
    "FR": "Federal Register",
    "CHRG": "Committee Hearings",
}

# Schema validation
SCHEMA_VERSIONS = {
    "BILLS": "uslm-2.1.0.xsd",
    "CFR": "uslm-2.1.0.xsd",
    "FR": "uslm-2.1.0.xsd",
    "CHRG": "uslm-2.1.0.xsd",
}


# Document status constants
class DocumentStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"


# Error types
class ErrorType:
    SCHEMA_VALIDATION = "schema_validation"
    METADATA_VALIDATION = "metadata_validation"
    VERSION_CONFLICT = "version_conflict"
    PROCESSING_ERROR = "processing_error"


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "news_aggregator"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "your_password"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )


def validate_schema(content: str, collection: str) -> Dict[str, Any]:
    """Validate XML content against USLM schema."""
    try:
        schema_path = f"/media/cbwinslow/CBWHDD/opendiscourse/docs/ref/uslm/{SCHEMA_VERSIONS[collection]}"
        schema = xmlschema.XMLSchema(schema_path)
        validation_result = schema.validate(content)

        return {
            "is_valid": True,
            "errors": [],
            "schema_version": SCHEMA_VERSIONS[collection],
        }
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [str(e)],
            "schema_version": SCHEMA_VERSIONS.get(collection, "unknown"),
        }


def validate_metadata(metadata: Dict[str, Any], collection: str) -> Dict[str, Any]:
    """Validate document metadata."""
    required_fields = {
        "BILLS": ["title", "version", "document_id"],
        "CFR": ["title", "version", "document_id"],
        "FR": ["title", "version", "document_id"],
        "CHRG": ["title", "version", "document_id"],
    }

    errors = []
    for field in required_fields.get(collection, []):
        if not metadata.get(field):
            errors.append(f"Missing required field: {field}")

    return {"is_valid": len(errors) == 0, "errors": errors}


def calculate_content_hash(content: str) -> str:
    """Calculate hash of content for version tracking."""
    return hashlib.sha256(content.encode()).hexdigest()


def find_previous_version(
    doc_id: str, collection: str, conn: psycopg2.extensions.connection
) -> Optional[Dict[str, Any]]:
    """Find previous version of a document."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, content, version 
            FROM documents 
            WHERE collection_type = %s 
            AND document_id = %s 
            AND status = 'completed' 
            ORDER BY processed_at DESC 
            LIMIT 1
        """,
            (collection, doc_id),
        )

        result = cursor.fetchone()
        if result:
            return {"id": result[0], "content": result[1], "version": result[2]}
        return None
    finally:
        cursor.close()


def process_uslm(
    doc_id: str, content: str, collection: str
) -> Optional[Dict[str, Any]]:
    """Process a USLM document with all validation and version tracking."""
    try:
        # Parse XML content
        root = ET.fromstring(content)

        # Extract metadata
        metadata = {
            "type": "uslm",
            "collection": collection,
            "title": (
                root.find(".//title").text if root.find(".//title") is not None else ""
            ),
            "date": (
                root.find(".//date").text if root.find(".//date") is not None else ""
            ),
            "version": (
                root.find(".//version").text
                if root.find(".//version") is not None
                else ""
            ),
            "document_id": (
                root.find(".//documentId").text
                if root.find(".//documentId") is not None
                else ""
            ),
        }

        # Validate schema
        schema_validation = validate_schema(content, collection)
        if not schema_validation["is_valid"]:
            logging.error(
                f"Schema validation failed for {doc_id}: {schema_validation['errors']}"
            )
            return None

        # Validate metadata
        metadata_validation = validate_metadata(metadata, collection)
        if not metadata_validation["is_valid"]:
            logging.error(
                f"Metadata validation failed for {doc_id}: {metadata_validation['errors']}"
            )
            return None

        # Extract main content
        text = ""
        for section in root.findall(".//section"):
            text += ET.tostring(section, encoding="unicode")

        # Calculate content hash for version tracking
        content_hash = calculate_content_hash(text)

        # Check for previous version
        conn = get_db_connection()
        previous_version = find_previous_version(doc_id, collection, conn)

        # Compare with previous version if exists
        if previous_version:
            previous_content_hash = calculate_content_hash(previous_version["content"])
            if content_hash == previous_content_hash:
                logging.info(
                    f"Document {doc_id} has not changed since version {previous_version['version']}"
                )
                return None

            # Calculate changes
            diff = difflib.unified_diff(
                previous_version["content"].splitlines(), text.splitlines()
            )
            changes = list(diff)

            metadata["changes"] = changes
            metadata["previous_version"] = previous_version["version"]

        return {
            "content": text,
            "metadata": metadata,
            "schema_validation": schema_validation,
            "metadata_validation": metadata_validation,
            "status": DocumentStatus.COMPLETED,
        }
    except Exception as e:
        logging.error(f"Error processing USLM document {doc_id}: {e!s}")
        return None
    finally:
        if "conn" in locals():
            conn.close()


def process_bill(doc_id, content):
    """Process a bill document."""
    return process_uslm(doc_id, content, "BILLS")


def process_cfr(doc_id, content):
    """Process a CFR document."""
    try:
        # Parse XML content
        root = ET.fromstring(content)

        # Extract metadata
        metadata = {
            "type": "cfr",
            "title": root.find(".//title").text,
            "part": root.find(".//part").text,
            "section": root.find(".//section").text,
            "effective_date": root.find(".//effectiveDate").text,
            "updated_date": root.find(".//updatedDate").text,
        }

        # Extract main content
        text = ET.tostring(root.find(".//text"), encoding="unicode")

        return {"content": text, "metadata": metadata}
    except Exception as e:
        logging.error(f"Error processing CFR {doc_id}: {e!s}")
        return None


def process_federal_register(doc_id, content):
    """Process a Federal Register document."""
    try:
        # Parse XML content
        root = ET.fromstring(content)

        # Extract metadata
        metadata = {
            "type": "federal_register",
            "document_number": root.find(".//documentNumber").text,
            "title": root.find(".//title").text,
            "agency": root.find(".//agency").text,
            "published_date": root.find(".//publishedDate").text,
            "document_type": root.find(".//documentType").text,
        }

        # Extract main content
        text = ET.tostring(root.find(".//text"), encoding="unicode")

        return {"content": text, "metadata": metadata}
    except Exception as e:
        logging.error(f"Error processing Federal Register {doc_id}: {e!s}")
        return None


def save_document(
    doc_id: str,
    content: str,
    metadata: Dict[str, Any],
    schema_validation: Dict[str, Any],
    metadata_validation: Dict[str, Any],
    status: str,
    collection: str,
) -> None:
    """Save document to PostgreSQL database with all validation and version tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert document
        cursor.execute(
            """
            INSERT INTO documents (
                document_id,
                title,
                content,
                metadata,
                schema_version,
                schema_validation_result,
                metadata_validation_result,
                collection_type,
                collection_metadata,
                status,
                processed_at,
                is_valid,
                validation_errors,
                version,
                previous_version_id,
                next_version_id
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            ) RETURNING id
        """,
            (
                doc_id,
                metadata.get("title", ""),
                content,
                metadata,
                schema_validation.get("schema_version", ""),
                json.dumps(schema_validation),
                json.dumps(metadata_validation),
                collection,
                json.dumps(
                    {
                        "collection_type": COLLECTION_TYPES.get(collection, "unknown"),
                        "collection_code": collection,
                    }
                ),
                status,
                schema_validation["is_valid"] and metadata_validation["is_valid"],
                json.dumps(
                    schema_validation.get("errors", [])
                    + metadata_validation.get("errors", [])
                ),
                metadata.get("version", ""),
                metadata.get("previous_version_id", None),
                None,  # Next version ID will be set when a new version is created
            ),
        )

        new_doc_id = cursor.fetchone()[0]
        conn.commit()

        # If this is a new version, update previous version's next_version_id
        if metadata.get("previous_version_id"):
            cursor.execute(
                """
                UPDATE documents 
                SET next_version_id = %s 
                WHERE id = %s
            """,
                (new_doc_id, metadata["previous_version_id"]),
            )
            conn.commit()

        logging.info(f"Saved document with ID: {new_doc_id}")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error saving document: {e!s}")
    finally:
        cursor.close()
        conn.close()


def process_document(doc_id: str, collection: str, content: str) -> None:
    """Process a document with full validation and error handling."""
    try:
        # Update document status to processing
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (document_id, collection_type, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (document_id, collection_type)
            DO UPDATE SET status = %s
        """,
            (doc_id, collection, DocumentStatus.PROCESSING, DocumentStatus.PROCESSING),
        )
        conn.commit()

        # Process using USLM schema
        result = process_uslm(doc_id, content, collection)

        if result:
            # Save document with validation results
            save_document(
                doc_id,
                result["content"],
                result["metadata"],
                result["schema_validation"],
                result["metadata_validation"],
                DocumentStatus.COMPLETED,
                collection,
            )
        else:
            # Update status to error if processing failed
            cursor.execute(
                """
                UPDATE documents 
                SET status = %s, 
                    error_message = %s, 
                    processed_at = CURRENT_TIMESTAMP
                WHERE document_id = %s 
                AND collection_type = %s
            """,
                (DocumentStatus.ERROR, "Processing failed", doc_id, collection),
            )
            conn.commit()

    except Exception as e:
        logging.error(f"Error processing document {doc_id}: {e!s}")
        try:
            # Update status to error if there was a database error
            cursor.execute(
                """
                UPDATE documents 
                SET status = %s, 
                    error_message = %s, 
                    processed_at = CURRENT_TIMESTAMP
                WHERE document_id = %s 
                AND collection_type = %s
            """,
                (DocumentStatus.ERROR, str(e), doc_id, collection),
            )
            conn.commit()
        except:
            pass  # Best effort to update status
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


def fetch_and_process_collection(collection):
    """Fetch and process documents from a specific collection."""
    base_url = "https://api.govinfo.gov"
    api_key = os.getenv("GOVINFO_API_KEY")

    # Get documents for collection
    documents_url = f"{base_url}/packages?collectionCode={collection}&api_key={api_key}"
    response = requests.get(documents_url)
    response.raise_for_status()
    documents = response.json()

    # Process each document
    for doc in documents["packages"]:
        try:
            # Get document content
            content_url = f"{base_url}/packages/{doc['packageId']}/content-detail.xml?api_key={api_key}"
            content_response = requests.get(content_url)

            if content_response.status_code == 200:
                process_document(doc["packageId"], collection, content_response.text)
            else:
                logging.warning(f"No content available for {doc['packageId']}")

        except Exception as e:
            logging.error(f"Error processing document {doc['packageId']}: {e!s}")


def main():
    """Main function to process all document collections."""
    logging.info("Starting document processing...")

    # List of collections to process
    collections = ["BILLS", "CFR", "FR"]

    for collection in collections:
        logging.info(f"Processing collection: {collection}")
        fetch_and_process_collection(collection)

    logging.info("Document processing completed")


if __name__ == "__main__":
    main()
