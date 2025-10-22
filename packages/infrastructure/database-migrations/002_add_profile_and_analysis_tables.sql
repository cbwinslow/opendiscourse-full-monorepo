-- Migration: Add member profiles table
-- Description: Create table for storing generated member profiles

-- Member profiles table
CREATE TABLE member_profiles (
    person_id TEXT PRIMARY KEY,
    profile_data JSONB NOT NULL,
    profile_score NUMERIC(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for better query performance
CREATE INDEX idx_member_profiles_score 
ON member_profiles (profile_score DESC);

CREATE INDEX idx_member_profiles_updated 
ON member_profiles (updated_at DESC);

CREATE INDEX idx_member_profiles_name 
ON member_profiles ((profile_data->'basic_info'->>'name'));

-- Update the jurisdictions table to add more fields
ALTER TABLE jurisdictions
ADD COLUMN IF NOT EXISTS population INTEGER,
ADD COLUMN IF NOT EXISTS founded_date DATE,
ADD COLUMN IF NOT EXISTS government_type TEXT;

-- Update the people table to add more fields
ALTER TABLE people
ADD COLUMN IF NOT EXISTS office TEXT,
ADD COLUMN IF NOT EXISTS phone TEXT,
ADD COLUMN IF NOT EXISTS fax TEXT,
ADD COLUMN IF NOT EXISTS contact_form TEXT,
ADD COLUMN IF NOT EXISTS website TEXT;

-- Create a table for storing NLP analysis results
CREATE TABLE IF NOT EXISTS nlp_analysis (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL, -- 'person', 'bill', 'statement', etc.
    entity_id TEXT NOT NULL,   -- ID of the entity being analyzed
    analysis_type TEXT NOT NULL, -- 'sentiment', 'topic', 'entity_extraction', etc.
    results JSONB NOT NULL,
    confidence_score NUMERIC(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for NLP analysis table
CREATE INDEX IF NOT EXISTS idx_nlp_analysis_entity 
ON nlp_analysis (entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_nlp_analysis_type 
ON nlp_analysis (analysis_type);

CREATE INDEX IF NOT EXISTS idx_nlp_analysis_confidence 
ON nlp_analysis (confidence_score DESC);

-- Create a table for storing discrepancy findings
CREATE TABLE IF NOT EXISTS discrepancies (
    id TEXT PRIMARY KEY,
    person_id TEXT NOT NULL REFERENCES people(id),
    issue TEXT NOT NULL,
    vote_position TEXT,
    statement_position TEXT,
    confidence_score NUMERIC(3,2),
    evidence JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for discrepancies table
CREATE INDEX IF NOT EXISTS idx_discrepancies_person 
ON discrepancies (person_id);

CREATE INDEX IF NOT EXISTS idx_discrepancies_issue 
ON discrepancies (issue);

CREATE INDEX IF NOT EXISTS idx_discrepancies_confidence 
ON discrepancies (confidence_score DESC);

CREATE INDEX IF NOT EXISTS idx_discrepancies_resolved 
ON discrepancies (resolved);