import sys
sys.path.append('/home/cbwinslow/CascadeProjects/opendiscourse')

from entity_extractor import extract_entities, save_entity, save_entity_relationship, save_entity_mention
from datetime import datetime
import os

# Read test document
test_content = open('test_document.txt').read()

# Extract entities
entities = extract_entities(test_content)

print("\nExtracted Entities:")
for entity in entities:
    print(f"- {entity['text']} ({entity['type']})")

# Save entities to database
for entity in entities:
    entity_id = save_entity(entity)
    if entity_id is not None:
        print(f"Saved entity: {entity['text']} with ID: {entity_id}")

print("\nEntity Relationships:")
# Infer relationships
for i, entity in enumerate(entities):
    for j in range(i + 1, len(entities)):
        other_entity = entities[j]
        # Check for membership relationships
        if entity['type'] == 'GOVERNMENT_BODY' and other_entity['type'] == 'PERSON':
            print(f"- {other_entity['text']} is a member of {entity['text']}")
            entity_id = save_entity(entity)
            other_entity_id = save_entity(other_entity)
            if entity_id is not None and other_entity_id is not None:
                save_entity_relationship({
                    'entity_id': entity_id,
                    'related_entity_id': other_entity_id,
                    'relationship_type': 'MEMBER_OF',
                    'confidence': 0.8
                })

print("\nEntity Mentions:")
# Save entity mentions
for entity in entities:
    entity_id = save_entity(entity)
    if entity_id is not None:
        mention = {
            'text': entity['text'],
            'type': entity['type'],
            'confidence': entity['confidence']
        }
        save_entity_mention(mention, 1, entity_id)  # Using test document ID 1
        print(f"- Mention: {mention['text']}")
