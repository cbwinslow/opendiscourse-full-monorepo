from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg2
from dotenv import load_dotenv
from transformers import pipeline

from .vector_database import VectorDatabase

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("entity_extractor.log"), logging.StreamHandler()],
)

# Load environment variables
load_dotenv()

# Initialize transformers pipeline
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")

# Initialize vector database
vector_db = VectorDatabase()

# Define entity patterns
ENTITY_PATTERNS = {
    "GOVERNMENT_BODY": [
        r"\b(111th|112th|113th|114th|115th|116th|117th|118th) Congress\b",
        r"\bHouse of Representatives\b",
        r"\bSenate\b",
        r"\bSupreme Court\b",
        r"\bExecutive Branch\b",
        r"\bLegislative Branch\b",
        r"\bJudicial Branch\b",
    ],
    "LEGISLATIVE_BODY": [
        r"\bHouse Committee\b",
        r"\bSenate Committee\b",
        r"\bJoint Committee\b",
    ],
    "PERSON": [
        r"\b(Senator|Representative|Congressman|Congresswoman)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
        r"\bPresident\s+[A-Z][a-z]+\b",
        r"\bVice President\s+[A-Z][a-z]+\b",
    ],
}

# Map transformer entity types to our entity types
ENTITY_TYPE_MAP = {
    "PER": "PERSON",
    "ORG": "ORGANIZATION",
    "MISC": "ORGANIZATION",
    "LOC": "ORGANIZATION",
}


@dataclass
class Entity:
    text: str
    label: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if not self.text or not isinstance(self.text, str):
            msg = "Entity text must be a non-empty string"
            raise ValueError(msg)
        if not self.label or not isinstance(self.label, str):
            msg = "Entity label must be a non-empty string"
            raise ValueError(msg)


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        dbname="opendiscourse",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
    )


def extract_entities(text: str, document_id: int) -> list[dict[str, Any]]:
    """Extract entities from text using transformers and custom patterns."""
    try:
        # Process with transformers
        entities = ner_pipeline(text)

        # Convert logits to probabilities
        probabilities = torch.softmax(torch.tensor(entities), dim=-1)

        # Get the predicted labels
        torch.argmax(probabilities, dim=-1)

        # Convert token IDs to tokens
        tokens = [entity["word"] for entity in entities]

        # Get the predicted labels
        predicted_labels = [entity["entity"] for entity in entities]

        transformer_entities: list[dict[str, Any]] = []
        current_entity: Entity | None = None
        current_entity_text = ""

        for token, label in zip(tokens, predicted_labels):
            if label != "O":  # O means no entity
                if current_entity is None:
                    current_entity = Entity(
                        text=token,
                        label=label,
                        start=0,  # Will be updated later
                        end=0,  # Will be updated later
                    )
                    current_entity_text = token
                elif label == current_entity.label:
                    current_entity_text += " " + token
                else:
                    _process_entity_text(
                        current_entity_text,
                        current_entity.label,
                        text,
                        probabilities,
                        transformer_entities,
                    )
                    current_entity = Entity(
                        text=token,
                        label=label,
                        start=0,  # Will be updated later
                        end=0,  # Will be updated later
                    )
                    current_entity_text = token

        if current_entity is not None:
            _process_entity_text(
                current_entity_text,
                current_entity.label,
                text,
                probabilities,
                transformer_entities,
            )

        return _process_entity_list(transformer_entities, document_id, text)

    except Exception as e:
        error_msg = f"Error extracting entities: {e!s}"
        logging.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def _process_entity_text(
    entity_text: str,
    label: str,
    text: str,
    probabilities: torch.Tensor,
    entities_list: list[dict[str, Any]],
) -> None:
    """Process a single entity's text and add it to the entities list."""
    clean_text = entity_text.replace("##", "").strip()
    start_pos = text.find(clean_text)
    if start_pos >= 0:  # Only add if found
        entities_list.append(
            {
                "entity": clean_text,
                "start": start_pos,
                "end": start_pos + len(clean_text),
                "score": float(probabilities[0][start_pos].max().item()),
                "label": label,
            }
        )


def _process_entity_list(
    entities: list[dict[str, Any]], document_id: int, text: str
) -> list[dict[str, Any]]:
    """Process the list of extracted entities."""
    result: list[dict[str, Any]] = []
    seen_entities: set[str] = set()

    for ent in entities:
        entity_text = ent["entity"]
        if entity_text in ENTITY_TYPE_MAP and entity_text not in seen_entities:
            seen_entities.add(entity_text)
            result.append(
                {
                    "text": entity_text,
                    "type": ENTITY_TYPE_MAP[entity_text],
                    "start": ent["start"],
                    "end": ent["end"],
                    "confidence": ent["score"],
                }
            )

            # Check if this is a new entity
            _process_vector_db_entity(entity_text, ent, document_id)

    return result


def _process_vector_db_entity(
    entity_text: str, entity: dict[str, Any], document_id: int
) -> None:
    """Process an entity for vector database operations."""
    try:
        # Search for similar entities in the vector database
        search_results = vector_db.search(query=entity_text, k=3) if vector_db else []

        # If no similar entities found, add this as new
        if not search_results:
            # Create embedding for new entity
            embedding = vector_db.embeddings.embed_query(entity_text)
            _ = vector_db.vector_store.add_texts(
                texts=[entity_text],
                metadatas=[
                    {
                        "entity_type": ENTITY_TYPE_MAP.get(entity.get("label", "")),
                        "source_document": document_id,
                        "confidence": entity.get("score", 0.0),
                    }
                ],
                embeddings=[embedding],
            )
            vector_db.persist()
    except Exception as e:
        logging.error(
            "Error in vector database operation for entity %s: %s", entity_text, str(e)
        )
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity_text = match.group()
                if entity_text not in seen_entities:
                    seen_entities.add(entity_text)
                    entities.append(
                        {
                            "text": entity_text,
                            "type": entity_type,
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.8,  # Custom pattern confidence
                        }
                    )

    return entities


def deduplicate_entities(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate entities based on text and type."""
    seen = set()
    unique_entities = []

    for entity in entities:
        key = (entity["text"].lower(), entity["type"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)

    return unique_entities


def infer_relationships(
    entities: list[dict[str, Any]], text: str
) -> list[dict[str, Any]]:
    """Infer relationships between entities based on context."""
    relationships = []

    # Create entity text mapping
    entity_map = {e["text"].lower(): e for e in entities}

    # Look for membership relationships
    membership_patterns = [
        r"\b(\w+)\s+of\s+(\w+)\b",
        r"\b(\w+)\s+in\s+(\w+)\b",
        r"\b(\w+)\s+with\s+(\w+)\b",
    ]

    for pattern in membership_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            member = match.group(1)
            group = match.group(2)

            if member.lower() in entity_map and group.lower() in entity_map:
                relationships.append(
                    {
                        "entity_id": entity_map[member.lower()]["id"],
                        "related_entity_id": entity_map[group.lower()]["id"],
                        "relationship_type": "MEMBER_OF",
                        "confidence": 0.7,
                    }
                )

    return relationships


def extract_declarations(
    entities: list[dict[str, Any]], text: str
) -> list[dict[str, Any]]:
    """Extract declarations from text."""
    declarations = []

    # Look for declarative patterns
    declaration_patterns = [
        r"\bshall\b",
        r"\bmust\b",
        r"\bwill\b",
        r"\brequired\b",
        r"\bprohibited\b",
        r"\bmandated\b",
    ]

    for entity in entities:
        # Look for declarations near entity mentions
        for pattern in declaration_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get context around declaration
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]

                declarations.append(
                    {
                        "entity_text": entity["text"],
                        "declaration_text": context,
                        "declaration_type": "ACTIONABLE",
                        "confidence": 0.7,
                    }
                )

    return declarations


def save_entity(entity: dict[str, Any]) -> int:
    """Save entity to database.

    Args:
        entity: Dictionary containing entity information with keys:
               - text: The entity text
               - type: The entity type
               - confidence: Optional confidence score

    Returns:
        int: The database ID of the saved entity

    Raises:
        Exception: If there's an error saving the entity
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO entities (text, type, metadata, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                ON CONFLICT (text, type) DO UPDATE
                SET updated_at = NOW()
                RETURNING id
            """,
                (
                    entity["text"],
                    entity["type"],
                    json.dumps({"confidence": entity.get("confidence", 0.0)}),
                ),
            )
            result = cur.fetchone()
            if not result:
                msg = "Failed to save entity: no ID returned"
                raise ValueError(msg)
            entity_id = result["id"]
            conn.commit()
            return entity_id
    except Exception as e:
        logging.error(f"Error saving entity: {e!s}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


def save_entity_relationship(relationship: dict[str, Any]) -> None:
    """Save entity relationship to database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
        INSERT INTO entity_relationships (entity_id, related_entity_id, relationship_type, confidence, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """.strip(),
            (
                relationship["entity_id"],
                relationship["related_entity_id"],
                relationship["relationship_type"],
                relationship.get("confidence", 0.5),
                datetime.now(),
            ),
        )

        conn.commit()
    except Exception as e:
        logging.error(f"Error saving entity relationship: {e!s}")
    finally:
        cursor.close()
        conn.close()


def save_entity_mention(
    mention: dict[str, Any], document_id: int, entity_id: int
) -> None:
    """Save entity mention to database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO entity_mentions (text, type, confidence, document_id, entity_id, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                mention["text"],
                mention["type"],
                mention["confidence"],
                document_id,
                entity_id,
                datetime.now(),
            ),
        )

        conn.commit()
    except Exception as e:
        logging.error(f"Error saving entity mention: {e!s}")
    finally:
        cursor.close()
        conn.close()


def save_declaration(declaration: dict[str, Any], document_id: int) -> None:
    """Save declaration to database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO declarations (document_id, entity_id, declaration_text, declaration_type, confidence, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                document_id,
                declaration["entity_id"],
                declaration["declaration_text"],
                declaration["declaration_type"],
                declaration["confidence"],
                datetime.now(),
            ),
        )

        conn.commit()
    except Exception as e:
        logging.error(f"Error saving declaration: {e!s}")
    finally:
        cursor.close()
        conn.close()


def process_document(document_id: int, content: str, metadata: dict[str, str]) -> None:
    """Process a document for entity extraction."""
    try:
        # Extract entities with continuous discovery
        entities = extract_entities(content, document_id)

        # Deduplicate entities
        entities = deduplicate_entities(entities)

        # Infer relationships
        relationships = infer_relationships(entities, content)

        # Extract declarations
        declarations = extract_declarations(entities, content)

        # Save to vector database
        vector_db.add_document(document_id, content, metadata)

        # Save entities and relationships
        for entity in entities:
            entity_id = save_entity(entity)
            if entity_id:
                save_entity_mention(entity, document_id, entity_id)

        for relationship in relationships:
            save_entity_relationship(relationship)

        for declaration in declarations:
            save_declaration(declaration, document_id)

    except Exception as e:
        logging.error(f"Error processing document {document_id}: {e!s}")


def main():
    """Main function to process documents."""
    logging.info("Starting entity extraction...")

    # Get unprocessed documents
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, content
            FROM documents
            WHERE status = 'completed'
            AND NOT EXISTS (SELECT 1 FROM entity_mentions WHERE document_id = documents.id)
            LIMIT 100
        """
        )

        documents = cursor.fetchall()

        for doc_id, content in documents:
            process_document(doc_id, content)

    except Exception as e:
        logging.error(f"Error in main processing: {e!s}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
