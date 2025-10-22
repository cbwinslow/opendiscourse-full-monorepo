-- Migration 001_create_openstates_tables.sql
-- Create tables for OpenStates data

-- Jurisdictions table
CREATE TABLE IF NOT EXISTS openstates_jurisdictions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    classification TEXT NOT NULL,
    url TEXT,
    division JSONB,
    legislative_sessions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- People (Legislators) table
CREATE TABLE IF NOT EXISTS openstates_people (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    given_name TEXT,
    family_name TEXT,
    email TEXT,
    gender TEXT,
    biography TEXT,
    birth_date DATE,
    death_date DATE,
    image TEXT,
    links JSONB,
    sources JSONB,
    extras JSONB,
    offices JSONB,
    party JSONB,
    roles JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legislative sessions table
CREATE TABLE IF NOT EXISTS openstates_sessions (
    id TEXT PRIMARY KEY,
    jurisdiction_id TEXT REFERENCES openstates_jurisdictions(id),
    name TEXT NOT NULL,
    identifier TEXT NOT NULL,
    classification TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills table
CREATE TABLE IF NOT EXISTS openstates_bills (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES openstates_sessions(id),
    jurisdiction_id TEXT REFERENCES openstates_jurisdictions(id),
    identifier TEXT NOT NULL,
    title TEXT NOT NULL,
    classification TEXT[],
    subject TEXT[],
    extras JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    openstates_url TEXT,
    sponsorships JSONB,
    actions JSONB,
    votes JSONB,
    versions JSONB,
    documents JSONB,
    sources JSONB
);

-- Committees table
CREATE TABLE IF NOT EXISTS openstates_committees (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    chamber TEXT,
    jurisdiction_id TEXT REFERENCES openstates_jurisdictions(id),
    members JSONB,
    sources JSONB,
    links JSONB,
    extras JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events table
CREATE TABLE IF NOT EXISTS openstates_events (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    jurisdiction_id TEXT REFERENCES openstates_jurisdictions(id),
    description TEXT,
    classification TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    all_day BOOLEAN,
    status TEXT,
    location JSONB,
    media JSONB,
    documents JSONB,
    links JSONB,
    sources JSONB,
    participants JSONB,
    agenda JSONB,
    extras JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Votes table
CREATE TABLE IF NOT EXISTS openstates_votes (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES openstates_bills(id),
    motion_text TEXT,
    motion_type TEXT,
    result TEXT,
    date DATE,
    chamber TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sources JSONB,
    votes JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_openstates_bills_jurisdiction ON openstates_bills(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_openstates_bills_session ON openstates_bills(session_id);
CREATE INDEX IF NOT EXISTS idx_openstates_bills_identifier ON openstates_bills(identifier);
CREATE INDEX IF NOT EXISTS idx_openstates_bills_created_at ON openstates_bills(created_at);
CREATE INDEX IF NOT EXISTS idx_openstates_bills_updated_at ON openstates_bills(updated_at);
CREATE INDEX IF NOT EXISTS idx_openstates_people_name ON openstates_people(name);
CREATE INDEX IF NOT EXISTS idx_openstates_people_updated_at ON openstates_people(updated_at);
CREATE INDEX IF NOT EXISTS idx_openstates_sessions_jurisdiction ON openstates_sessions(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_openstates_sessions_identifier ON openstates_sessions(identifier);
CREATE INDEX IF NOT EXISTS idx_openstates_committees_jurisdiction ON openstates_committees(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_openstates_events_jurisdiction ON openstates_events(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_openstates_events_date ON openstates_events(start_date);
CREATE INDEX IF NOT EXISTS idx_openstates_votes_bill ON openstates_votes(bill_id);
CREATE INDEX IF NOT EXISTS idx_openstates_votes_date ON openstates_votes(date);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_openstates_bills_fts ON openstates_bills USING gin(to_tsvector('english', title || ' ' || array_to_string(subject, ' ')));
CREATE INDEX IF NOT EXISTS idx_openstates_people_fts ON openstates_people USING gin(to_tsvector('english', name || ' ' || coalesce(biography, '')));