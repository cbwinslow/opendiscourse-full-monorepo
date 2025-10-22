# NLP Integration with OpenDiscourse Database

## Overview
This document outlines how to integrate NLP analysis results with the existing OpenDiscourse database schema, including new tables and modifications to store NLP-derived insights.

## Database Schema Extensions

### 1. NLP Analysis Results Tables

#### Bill Embeddings Table
```sql
CREATE TABLE IF NOT EXISTS nlp_bill_embeddings (
    bill_id INTEGER REFERENCES master_bills(id),
    model_name TEXT NOT NULL,
    embedding VECTOR(384),  -- Adjust size based on embedding model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (bill_id, model_name)
);

-- Index for similarity search
CREATE INDEX IF NOT EXISTS idx_bill_embeddings_model ON nlp_bill_embeddings(model_name);
```

#### Entity Extraction Results Table
```sql
CREATE TABLE IF NOT EXISTS nlp_entity_extraction (
    id SERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,  -- 'bill', 'statement', 'social_post'
    source_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,  -- 'PERSON', 'ORG', 'LAW', 'CITATION', etc.
    entity_text TEXT NOT NULL,
    start_position INTEGER,
    end_position INTEGER,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_entity_extraction_source ON nlp_entity_extraction(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_entity_extraction_type ON nlp_entity_extraction(entity_type);
CREATE INDEX IF NOT EXISTS idx_entity_extraction_text ON nlp_entity_extraction(entity_text);
```

#### Sentiment Analysis Results Table
```sql
CREATE TABLE IF NOT EXISTS nlp_sentiment_analysis (
    id SERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,  -- 'statement', 'social_post'
    source_id INTEGER NOT NULL,
    method TEXT NOT NULL,       -- 'VADER', 'TextBlob', 'BERT'
    sentiment_label TEXT,       -- 'positive', 'negative', 'neutral'
    confidence_score DECIMAL(3,2),
    positive_score DECIMAL(3,2),
    negative_score DECIMAL(3,2),
    neutral_score DECIMAL(3,2),
    compound_score DECIMAL(4,3), -- For VADER
    polarity_score DECIMAL(3,2), -- For TextBlob
    subjectivity_score DECIMAL(3,2), -- For TextBlob
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sentiment_source ON nlp_sentiment_analysis(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_method ON nlp_sentiment_analysis(method);
CREATE INDEX IF NOT EXISTS idx_sentiment_label ON nlp_sentiment_analysis(sentiment_label);
```

#### Topic Modeling Results Table
```sql
CREATE TABLE IF NOT EXISTS nlp_topic_modeling (
    id SERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,  -- 'bill', 'statement', 'social_post'
    source_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    probability DECIMAL(4,3) NOT NULL,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_topic_source ON nlp_topic_modeling(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_topic_id ON nlp_topic_modeling(topic_id);
CREATE INDEX IF NOT EXISTS idx_topic_probability ON nlp_topic_modeling(probability);
```

#### Topics Dictionary Table
```sql
CREATE TABLE IF NOT EXISTS nlp_topics (
    id SERIAL PRIMARY KEY,
    topic_name TEXT NOT NULL,
    keywords JSONB,  -- Top keywords for this topic
    description TEXT,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for topic search
CREATE INDEX IF NOT EXISTS idx_topics_name ON nlp_topics(topic_name);
```

### 2. Enhanced Master Tables

#### Enhanced Master Legislators Table
```sql
-- Add columns for NLP-derived metrics
ALTER TABLE master_legislators 
ADD COLUMN IF NOT EXISTS avg_sentiment_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS sentiment_consistency_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS communication_complexity_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS topic_diversity_score DECIMAL(3,2);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_legislators_sentiment ON master_legislators(avg_sentiment_score);
CREATE INDEX IF NOT EXISTS idx_legislators_consistency ON master_legislators(sentiment_consistency_score);
```

#### Enhanced Master Bills Table
```sql
-- Add columns for NLP-derived metrics
ALTER TABLE master_bills 
ADD COLUMN IF NOT EXISTS complexity_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS sentiment_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS controversy_score DECIMAL(3,2);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bills_complexity ON master_bills(complexity_score);
CREATE INDEX IF NOT EXISTS idx_bills_sentiment ON master_bills(sentiment_score);
```

### 3. Discrepancy Analysis Tables

#### Statement-Vote Discrepancy Table
```sql
CREATE TABLE IF NOT EXISTS nlp_discrepancy_analysis (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES master_legislators(id),
    bill_id INTEGER REFERENCES master_bills(id),
    statement_id INTEGER,  -- Reference to social media or public statement
    vote_position TEXT,    -- 'yes', 'no', 'abstain'
    statement_sentiment TEXT,  -- 'support', 'oppose', 'neutral'
    sentiment_confidence DECIMAL(3,2),
    discrepancy_type TEXT,     -- 'direct', 'indirect', 'ambiguous'
    discrepancy_score DECIMAL(3,2),  -- 0-1 scale
    explanation TEXT,        -- Human-readable explanation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_discrepancy_legislator ON nlp_discrepancy_analysis(legislator_id);
CREATE INDEX IF NOT EXISTS idx_discrepancy_bill ON nlp_discrepancy_analysis(bill_id);
CREATE INDEX IF NOT EXISTS idx_discrepancy_type ON nlp_discrepancy_analysis(discrepancy_type);
CREATE INDEX IF NOT EXISTS idx_discrepancy_score ON nlp_discrepancy_analysis(discrepancy_score);
```

## Data Processing Pipeline

### 1. Bill Analysis Pipeline

#### Embedding Generation Process
```sql
-- Insert bill embeddings after processing
INSERT INTO nlp_bill_embeddings (bill_id, model_name, embedding)
VALUES (%s, %s, %s)
ON CONFLICT (bill_id, model_name) 
DO UPDATE SET 
    embedding = EXCLUDED.embedding,
    updated_at = CURRENT_TIMESTAMP;
```

#### Entity Extraction Process
```sql
-- Insert extracted entities
INSERT INTO nlp_entity_extraction 
(source_type, source_id, entity_type, entity_text, start_position, end_position, confidence_score)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
```

#### Topic Assignment Process
```sql
-- Insert topic assignments
INSERT INTO nlp_topic_modeling 
(source_type, source_id, topic_id, probability, model_version)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
```

### 2. Social Media Analysis Pipeline

#### Sentiment Analysis Process
```sql
-- Insert sentiment analysis results
INSERT INTO nlp_sentiment_analysis 
(source_type, source_id, method, sentiment_label, confidence_score, 
 positive_score, negative_score, neutral_score, compound_score, 
 polarity_score, subjectivity_score)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
```

#### Discrepancy Detection Process
```sql
-- Insert discrepancy analysis results
INSERT INTO nlp_discrepancy_analysis 
(legislator_id, bill_id, statement_id, vote_position, statement_sentiment, 
 sentiment_confidence, discrepancy_type, discrepancy_score, explanation)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
```

## Views for Analysis and Reporting

### 1. Bill Similarity View
```sql
CREATE OR REPLACE VIEW bill_similarity_view AS
SELECT 
    mb1.id as bill_id_1,
    mb1.bill_number as bill_number_1,
    mb1.title as title_1,
    mb2.id as bill_id_2,
    mb2.bill_number as bill_number_2,
    mb2.title as title_2,
    -- Calculate cosine similarity between embeddings
    -- This would require a vector similarity function
    nbe1.model_name,
    CURRENT_TIMESTAMP as last_updated
FROM master_bills mb1
JOIN master_bills mb2 ON mb1.id != mb2.id
JOIN nlp_bill_embeddings nbe1 ON mb1.id = nbe1.bill_id
JOIN nlp_bill_embeddings nbe2 ON mb2.id = nbe2.bill_id
WHERE nbe1.model_name = nbe2.model_name
  AND nbe1.model_name = 'sentence-bert';
```

### 2. Legislator Sentiment Analysis View
```sql
CREATE OR REPLACE VIEW legislator_sentiment_view AS
SELECT 
    ml.id as legislator_id,
    ml.full_name,
    ml.party,
    ml.state,
    COUNT(nsa.id) as total_analyses,
    AVG(nsa.compound_score) as avg_sentiment,
    STDDEV(nsa.compound_score) as sentiment_variance,
    COUNT(CASE WHEN nsa.sentiment_label = 'positive' THEN 1 END) * 100.0 / COUNT(*) as positive_percentage,
    COUNT(CASE WHEN nsa.sentiment_label = 'negative' THEN 1 END) * 100.0 / COUNT(*) as negative_percentage,
    COUNT(CASE WHEN nsa.sentiment_label = 'neutral' THEN 1 END) * 100.0 / COUNT(*) as neutral_percentage
FROM master_legislators ml
LEFT JOIN master_social_media_posts msmp ON ml.id = msmp.legislator_id
LEFT JOIN nlp_sentiment_analysis nsa ON msmp.id = nsa.source_id AND nsa.source_type = 'social_post'
GROUP BY ml.id, ml.full_name, ml.party, ml.state;
```

### 3. Discrepancy Analysis View
```sql
CREATE OR REPLACE VIEW discrepancy_analysis_view AS
SELECT 
    nda.legislator_id,
    ml.full_name,
    ml.party,
    ml.state,
    nda.bill_id,
    mb.bill_number,
    mb.title,
    nda.vote_position,
    nda.statement_sentiment,
    nda.discrepancy_score,
    nda.discrepancy_type,
    nda.explanation,
    nda.created_at
FROM nlp_discrepancy_analysis nda
JOIN master_legislators ml ON nda.legislator_id = ml.id
JOIN master_bills mb ON nda.bill_id = mb.id
WHERE nda.discrepancy_score > 0.5  -- Only show significant discrepancies
ORDER BY nda.discrepancy_score DESC, nda.created_at DESC;
```

## Integration with Existing Data Sources

### 1. OpenStates Integration
```sql
-- Link NLP results to OpenStates data
CREATE OR REPLACE VIEW openstates_nlp_view AS
SELECT 
    osb.id as openstates_bill_id,
    osb.identifier as bill_number,
    osb.title,
    nbe.embedding,
    nee.entity_type,
    nee.entity_text,
    ntm.topic_id,
    nt.topic_name,
    nsa.sentiment_label,
    nsa.compound_score
FROM openstates_bills osb
LEFT JOIN master_bills mb ON osb.id = mb.openstates_bill_id
LEFT JOIN nlp_bill_embeddings nbe ON mb.id = nbe.bill_id
LEFT JOIN nlp_entity_extraction nee ON mb.id = nee.source_id AND nee.source_type = 'bill'
LEFT JOIN nlp_topic_modeling ntm ON mb.id = ntm.source_id AND ntm.source_type = 'bill'
LEFT JOIN nlp_topics nt ON ntm.topic_id = nt.id
LEFT JOIN nlp_sentiment_analysis nsa ON mb.id = nsa.source_id AND nsa.source_type = 'bill';
```

### 2. Congress.gov Integration
```sql
-- Link NLP results to Congress.gov data
CREATE OR REPLACE VIEW congressgov_nlp_view AS
SELECT 
    cgb.bill_id as congressgov_bill_id,
    cgb.number as bill_number,
    cgb.title,
    nbe.embedding,
    nee.entity_type,
    nee.entity_text,
    ntm.topic_id,
    nt.topic_name,
    nsa.sentiment_label,
    nsa.compound_score
FROM congressgov_bills cgb
LEFT JOIN master_bills mb ON cgb.bill_id = mb.congressgov_bill_id
LEFT JOIN nlp_bill_embeddings nbe ON mb.id = nbe.bill_id
LEFT JOIN nlp_entity_extraction nee ON mb.id = nee.source_id AND nee.source_type = 'bill'
LEFT JOIN nlp_topic_modeling ntm ON mb.id = ntm.source_id AND ntm.source_type = 'bill'
LEFT JOIN nlp_topics nt ON ntm.topic_id = nt.id
LEFT JOIN nlp_sentiment_analysis nsa ON mb.id = nsa.source_id AND nsa.source_type = 'bill';
```

## Performance Considerations

### 1. Indexing Strategy
```sql
-- Additional indexes for NLP tables
CREATE INDEX IF NOT EXISTS idx_bill_embeddings_embedding ON nlp_bill_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_entity_extraction_text_gin ON nlp_entity_extraction 
USING gin(entity_text gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_sentiment_compound ON nlp_sentiment_analysis(compound_score);
```

### 2. Partitioning for Large Datasets
```sql
-- Partition sentiment analysis by date for large datasets
CREATE TABLE IF NOT EXISTS nlp_sentiment_analysis_partitioned (
    LIKE nlp_sentiment_analysis INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE nlp_sentiment_analysis_2023 PARTITION OF nlp_sentiment_analysis_partitioned
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE nlp_sentiment_analysis_2024 PARTITION OF nlp_sentiment_analysis_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## Data Quality and Validation

### 1. NLP Results Validation Table
```sql
CREATE TABLE IF NOT EXISTS nlp_validation_results (
    id SERIAL PRIMARY KEY,
    analysis_type TEXT NOT NULL,  -- 'entity_extraction', 'sentiment_analysis', etc.
    source_id INTEGER NOT NULL,
    validation_score DECIMAL(3,2),
    validator_type TEXT,          -- 'human', 'automated'
    validation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_validation_type ON nlp_validation_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_validation_score ON nlp_validation_results(validation_score);
```

### 2. Model Performance Tracking
```sql
CREATE TABLE IF NOT EXISTS nlp_model_performance (
    id SERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    task_type TEXT NOT NULL,      -- 'entity_extraction', 'sentiment_analysis', etc.
    dataset_name TEXT,
    accuracy_score DECIMAL(4,3),
    precision_score DECIMAL(4,3),
    recall_score DECIMAL(4,3),
    f1_score DECIMAL(4,3),
    evaluation_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_model_performance_name ON nlp_model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_model_performance_task ON nlp_model_performance(task_type);
```

## API Integration Points

### 1. REST API Endpoints for NLP Data
```sql
-- Example query for API endpoint: /api/bills/{bill_id}/analysis
SELECT 
    mb.id,
    mb.title,
    nbe.embedding,
    json_agg(
        json_build_object(
            'type', nee.entity_type,
            'text', nee.entity_text,
            'confidence', nee.confidence_score
        )
    ) as entities,
    json_agg(
        json_build_object(
            'topic_id', ntm.topic_id,
            'topic_name', nt.topic_name,
            'probability', ntm.probability
        )
    ) as topics
FROM master_bills mb
LEFT JOIN nlp_bill_embeddings nbe ON mb.id = nbe.bill_id
LEFT JOIN nlp_entity_extraction nee ON mb.id = nee.source_id AND nee.source_type = 'bill'
LEFT JOIN nlp_topic_modeling ntm ON mb.id = ntm.source_id AND ntm.source_type = 'bill'
LEFT JOIN nlp_topics nt ON ntm.topic_id = nt.id
WHERE mb.id = %s
GROUP BY mb.id, mb.title, nbe.embedding;
```

### 2. Search Integration
```sql
-- Enhanced search with NLP features
CREATE OR REPLACE VIEW enhanced_search_view AS
SELECT 
    'bill' as result_type,
    mb.id as result_id,
    mb.title as result_title,
    mb.summary as result_description,
    ts_rank_cd(to_tsvector('english', mb.title || ' ' || mb.summary), query) as relevance_score,
    json_build_object(
        'complexity', mb.complexity_score,
        'sentiment', mb.sentiment_score,
        'topics', (
            SELECT json_agg(nt.topic_name)
            FROM nlp_topic_modeling ntm
            JOIN nlp_topics nt ON ntm.topic_id = nt.id
            WHERE ntm.source_id = mb.id AND ntm.source_type = 'bill'
        )
    ) as nlp_features
FROM master_bills mb, to_tsquery('english', %s) query
WHERE to_tsvector('english', mb.title || ' ' || mb.summary) @@ query

UNION ALL

SELECT 
    'legislator' as result_type,
    ml.id as result_id,
    ml.full_name as result_title,
    ml.party || ' - ' || ml.state as result_description,
    ts_rank_cd(to_tsvector('english', ml.full_name || ' ' || coalesce(ml.party, '')), query) as relevance_score,
    json_build_object(
        'avg_sentiment', ml.avg_sentiment_score,
        'consistency', ml.sentiment_consistency_score
    ) as nlp_features
FROM master_legislators ml, to_tsquery('english', %s) query
WHERE to_tsvector('english', ml.full_name || ' ' || coalesce(ml.party, '')) @@ query

ORDER BY relevance_score DESC;
```

## Migration Script
```sql
-- Migration script to add NLP tables to existing database
-- This would be added to the migrations directory as 007_create_nlp_tables.sql

-- Run the CREATE TABLE statements above
-- Add any necessary constraints or foreign keys
-- Update existing views to include NLP data where appropriate
```

This database integration provides a comprehensive framework for storing and analyzing NLP results within the OpenDiscourse platform. The schema extensions allow for efficient storage of embeddings, entity extractions, sentiment analysis results, and topic modeling outputs, while the views provide easy access to integrated insights for reporting and analysis.