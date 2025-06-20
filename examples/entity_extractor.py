import logging
from typing import Any, Dict, List

from dotenv import load_dotenv
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize NER pipeline
ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")


def extract_entities(text: str) -> List[Dict[str, Any]]:
    """Extract named entities from text using transformers pipeline.

    Args:
        text: Input text to analyze

    Returns:
        List of dictionaries containing entity information
    """
    try:
        entities = ner_pipeline(text)
        logger.info("Extracted %d entities from text", len(entities))
        return entities
    except Exception as e:
        logger.error("Error extracting entities: %s", e, exc_info=True)
        return []


def group_entities_by_type(entities: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Group entities by their type (e.g., PERSON, ORGANIZATION).

    Args:
        entities: List of entity dictionaries

    Returns:
        Dictionary mapping entity types to lists of entity values
    """
    grouped = {}
    for entity in entities:
        entity_type = entity["entity"]
        if entity_type not in grouped:
            grouped[entity_type] = []
        grouped[entity_type].append(entity["word"])
    return grouped


def extract_and_group_entities(text: str) -> Dict[str, List[str]]:
    """Extract and group entities from text in one step.

    Args:
        text: Input text to analyze

    Returns:
        Dictionary mapping entity types to lists of entity values
    """
    entities = extract_entities(text)
    return group_entities_by_type(entities)


def process_document(doc_id: int, content: str) -> Dict[str, Any]:
    """Process a document by extracting and grouping entities.

    Args:
        doc_id: Unique identifier for the document
        content: Document content to analyze

    Returns:
        Dictionary containing document ID and grouped entities
    """
    try:
        logger.info("Processing document %s", doc_id)
        entities = extract_and_group_entities(content)
        return {"doc_id": doc_id, "entities": entities}
    except Exception as e:
        logger.error("Error processing document %s: %s", doc_id, e, exc_info=True)
        return {"doc_id": doc_id, "error": str(e)}


if __name__ == "__main__":
    # Example usage
    sample_text = "Apple Inc. is headquartered in Cupertino, California."
    result = process_document(1, sample_text)
    logger.info("Processed document result: %s", result)
