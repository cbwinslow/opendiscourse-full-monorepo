import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict
from vector_database import VectorDatabase
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('entity_extractor.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Initialize transformers pipeline
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

# Initialize vector database
vector_db = VectorDatabase()

# Define entity patterns
ENTITY_PATTERNS = {
    'GOVERNMENT_BODY': [
        r'\b(111th|112th|113th|114th|115th|116th|117th|118th) Congress\b',
        r'\bHouse of Representatives\b',
        r'\bSenate\b',
        r'\bSupreme Court\b',
        r'\bExecutive Branch\b',
        r'\bLegislative Branch\b',
        r'\bJudicial Branch\b'
    ],
    'LEGISLATIVE_BODY': [
        r'\bHouse Committee\b',
        r'\bSenate Committee\b',
        r'\bJoint Committee\b'
    ],
    'PERSON': [
        r'\b(Senator|Representative|Congressman|Congresswoman)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        r'\bPresident\s+[A-Z][a-z]+\b',
        r'\bVice President\s+[A-Z][a-z]+\b'
    ]
}

# Map transformer entity types to our entity types
ENTITY_TYPE_MAP = {
    'PER': 'PERSON',
    'ORG': 'ORGANIZATION',
    'MISC': 'ORGANIZATION',
    'LOC': 'ORGANIZATION'
}

def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        dbname='opendiscourse',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5432'
    )

def extract_entities(text: str, document_id: int) -> List[Dict[str, Any]]:
    """Extract entities from text using transformers and custom patterns."""
    # Process with transformers
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    
    # Convert logits to probabilities
    probabilities = torch.softmax(outputs.logits, dim=-1)
    
    # Get the predicted labels
    predictions = torch.argmax(probabilities, dim=-1)
    
    # Convert token IDs to tokens
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    
    # Get the predicted labels
    predicted_labels = [model.config.id2label[p.item()] for p in predictions[0]]
    
    transformer_entities = []
    current_entity = None
    current_entity_text = ""
    
    for token, label in zip(tokens, predicted_labels):
        if label != "O":  # O means no entity
            if current_entity is None:
                current_entity = label
                current_entity_text = token
            elif label == current_entity:
                current_entity_text += " " + token
            else:
                transformer_entities.append({
                    "entity": current_entity_text,
                    "start": text.find(current_entity_text),
                    "end": text.find(current_entity_text) + len(current_entity_text),
                    "score": float(probabilities[0][text.find(current_entity_text)].max().item()),
                    "label": current_entity
                })
                current_entity = label
                current_entity_text = token
    
    if current_entity is not None:
        transformer_entities.append({
            "entity": current_entity_text,
            "start": text.find(current_entity_text),
            "end": text.find(current_entity_text) + len(current_entity_text),
            "score": float(probabilities[0][text.find(current_entity_text)].max().item()),
            "label": current_entity
        })
    
    # Convert transformer entities to our format
    entities = []
    seen_entities: Set[str] = set()
    
    # Get transformer entities
    for ent in transformer_entities:
        if ent['entity'] in ENTITY_TYPE_MAP:
            entity_text = ent['word']
            if entity_text not in seen_entities:
                seen_entities.add(entity_text)
                entities.append({
                    'text': entity_text,
                    'type': ENTITY_TYPE_MAP[ent['entity']],
                    'start': ent['start'],
                    'end': ent['end'],
                    'confidence': ent['score']
                })
                
                # Check if this is a new entity
                try:
                    # Get similar entities from vector database
                    similar_entities = vector_db.search_similar(entity_text, k=3)
                    
                    # If no similar entities found, add this as new
                    if not similar_entities:
                        # Create embedding for new entity
                        embedding = vector_db.embeddings.embed_query(entity_text)
                        vector_db.vector_store.add_texts(
                            texts=[entity_text],
                            metadatas=[{
                                'entity_type': ENTITY_TYPE_MAP[ent['entity']],
                                'source_document': document_id,
                                'confidence': ent['score']
                            }],
                            embeddings=[embedding]
                        )
                        vector_db.persist()
                except Exception as e:
                    logging.error(f"Error processing new entity {entity_text}: {str(e)}")
    
    # Apply custom patterns
    for entity_type, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity_text = match.group()
                if entity_text not in seen_entities:
                    seen_entities.add(entity_text)
                    entities.append({
                        'text': entity_text,
                        'type': entity_type,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8  # Custom pattern confidence
                    })
    
    return entities

def deduplicate_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate entities based on text and type."""
    seen = set()
    unique_entities = []
    
    for entity in entities:
        key = (entity['text'].lower(), entity['type'])
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities

def infer_relationships(entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    """Infer relationships between entities based on context."""
    relationships = []
    
    # Create entity text mapping
    entity_map = {e['text'].lower(): e for e in entities}
    
    # Look for membership relationships
    membership_patterns = [
        r'\b(\w+)\s+of\s+(\w+)\b',
        r'\b(\w+)\s+in\s+(\w+)\b',
        r'\b(\w+)\s+with\s+(\w+)\b'
    ]
    
    for pattern in membership_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            member = match.group(1)
            group = match.group(2)
            
            if member.lower() in entity_map and group.lower() in entity_map:
                relationships.append({
                    'entity_id': entity_map[member.lower()]['id'],
                    'related_entity_id': entity_map[group.lower()]['id'],
                    'relationship_type': 'MEMBER_OF',
                    'confidence': 0.7
                })
    
    return relationships

def extract_declarations(entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    """Extract declarations from text."""
    declarations = []
    
    # Look for declarative patterns
    declaration_patterns = [
        r'\bshall\b',
        r'\bmust\b',
        r'\bwill\b',
        r'\brequired\b',
        r'\bprohibited\b',
        r'\bmandated\b'
    ]
    
    for entity in entities:
        # Look for declarations near entity mentions
        for pattern in declaration_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get context around declaration
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]
                
                declarations.append({
                    'entity_text': entity['text'],
                    'declaration_text': context,
                    'declaration_type': 'ACTIONABLE',
                    'confidence': 0.7
                })
    
    return declarations

def save_entity(entity: Dict[str, Any]) -> Optional[int]:
    """Save entity to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO entities (
                entity_type,
                name,
                description,
                metadata
            ) VALUES (
                %s,
                %s,
                %s,
                %s
            ) ON CONFLICT (name)
            DO UPDATE SET 
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            entity['type'],
            entity['text'],
            None,
            json.dumps({
                'confidence': entity.get('confidence', 0.0),
                'source': 'pattern' if 'confidence' in entity else 'transformer'
            })
        ))
        
        entity_id = cursor.fetchone()[0]
        conn.commit()
        return entity_id
    except Exception as e:
        logging.error(f"Error saving entity: {str(e)}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def save_entity_relationship(relationship: Dict[str, Any]) -> None:
    """Save entity relationship to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO entity_relationships (entity_id, related_entity_id, relationship_type, confidence, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """.strip(), (
            relationship['entity_id'],
            relationship['related_entity_id'],
            relationship['relationship_type'],
            relationship.get('confidence', 0.5),
            datetime.now()
        ))
        
        conn.commit()
    except Exception as e:
        logging.error(f"Error saving entity relationship: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def save_entity_mention(mention: Dict[str, Any], document_id: int, entity_id: int) -> None:
    """Save entity mention to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO entity_mentions (text, type, confidence, document_id, entity_id, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (
            mention['text'],
            mention['type'],
            mention['confidence'],
            document_id,
            entity_id,
            datetime.now()
        ))
        
        conn.commit()
    except Exception as e:
        logging.error(f"Error saving entity mention: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def save_declaration(declaration: Dict[str, Any], document_id: int) -> None:
    """Save declaration to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO declarations (document_id, entity_id, declaration_text, declaration_type, confidence, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (
            document_id,
            declaration['entity_id'],
            declaration['declaration_text'],
            declaration['declaration_type'],
            declaration['confidence'],
            datetime.now()
        ))
        
        conn.commit()
    except Exception as e:
        logging.error(f"Error saving declaration: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def process_document(document_id: int, content: str, metadata: Dict[str, str]) -> None:
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
        logging.error(f"Error processing document {document_id}: {str(e)}")

def main():
    """Main function to process documents."""
    logging.info("Starting entity extraction...")
    
    # Get unprocessed documents
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, content 
            FROM documents 
            WHERE status = 'completed' 
            AND NOT EXISTS (SELECT 1 FROM entity_mentions WHERE document_id = documents.id) 
            LIMIT 100
        """)
        
        documents = cursor.fetchall()
        
        for doc_id, content in documents:
            process_document(doc_id, content)
            
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
