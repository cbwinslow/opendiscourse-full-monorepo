-- Consolidated Database Migration Script
-- Creates all tables needed for OpenStates, Congress.gov, and GovInfo data ingestion
-- Run this script to set up the complete database schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==================== OPENSTATES TABLES ====================
-- Based on Open Civic Data standard

-- Jurisdictions (states, territories, federal)
CREATE TABLE IF NOT EXISTS opencivicdata_jurisdiction (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    classification TEXT NOT NULL,
    division_id TEXT,
    latest_bill_update TIMESTAMP,
    latest_people_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legislative Sessions
CREATE TABLE IF NOT EXISTS opencivicdata_legislativesession (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identifier TEXT NOT NULL,
    name TEXT,
    classification TEXT DEFAULT '',
    start_date TEXT DEFAULT '',
    end_date TEXT DEFAULT '',
    jurisdiction_id TEXT REFERENCES opencivicdata_jurisdiction(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations (committees, parties, etc.)
CREATE TABLE IF NOT EXISTS opencivicdata_organization (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    classification TEXT,
    parent_id TEXT,
    links JSONB,
    sources JSONB,
    extras JSONB DEFAULT '{}',
    jurisdiction_id TEXT REFERENCES opencivicdata_jurisdiction(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- People (legislators, governors, etc.)
CREATE TABLE IF NOT EXISTS opencivicdata_person (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    family_name TEXT DEFAULT '',
    given_name TEXT DEFAULT '',
    image TEXT DEFAULT '',
    gender TEXT DEFAULT '',
    email TEXT DEFAULT '',
    biography TEXT DEFAULT '',
    birth_date TEXT DEFAULT '',
    death_date TEXT DEFAULT '',
    primary_party TEXT,
    current_role JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extras JSONB DEFAULT '{}',
    current_jurisdiction_id TEXT REFERENCES opencivicdata_jurisdiction(id)
);

-- Bills
CREATE TABLE IF NOT EXISTS opencivicdata_bill (
    id TEXT PRIMARY KEY,
    identifier TEXT,
    title TEXT,
    classification TEXT[],
    subject TEXT[],
    extras JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    from_organization_id TEXT REFERENCES opencivicdata_organization(id),
    legislative_session_id UUID REFERENCES opencivicdata_legislativesession(id),
    -- Computed fields
    first_action_date TEXT,
    latest_action_date TEXT,
    latest_action_description TEXT,
    latest_passage_date TEXT
);

-- Bill Actions
CREATE TABLE IF NOT EXISTS opencivicdata_billaction (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_id TEXT REFERENCES opencivicdata_bill(id),
    organization_id TEXT REFERENCES opencivicdata_organization(id),
    description TEXT,
    date TEXT,
    classification TEXT[] DEFAULT '{}',
    "order" INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vote Events
CREATE TABLE IF NOT EXISTS opencivicdata_voteevent (
    id TEXT PRIMARY KEY,
    identifier TEXT,
    motion_text TEXT,
    motion_classification TEXT[] DEFAULT '{}',
    start_date TEXT,
    result TEXT,
    extras JSONB DEFAULT '{}',
    organization_id TEXT REFERENCES opencivicdata_organization(id),
    legislative_session_id UUID REFERENCES opencivicdata_legislativesession(id),
    bill_id TEXT REFERENCES opencivicdata_bill(id),
    bill_action_id UUID REFERENCES opencivicdata_billaction(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== FEDERAL CONGRESS.GOV TABLES ====================

-- Federal Members
CREATE TABLE IF NOT EXISTS federal_members (
    id BIGSERIAL PRIMARY KEY,
    bioguide_id VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    party VARCHAR(10),
    state VARCHAR(2),
    chamber VARCHAR(10),  -- house, senate, joint
    current_member BOOLEAN DEFAULT FALSE,
    terms JSONB,  -- Array of term objects
    committees JSONB,  -- Array of committee assignments
    social_media JSONB,  -- {twitter: handle, facebook: id, etc.}
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Federal Bills
CREATE TABLE IF NOT EXISTS federal_bills (
    id BIGSERIAL PRIMARY KEY,
    source_url VARCHAR(500) UNIQUE NOT NULL,  -- Idempotency key from API
    congress INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL,  -- bill, amendment, resolution
    title TEXT,
    summary TEXT,
    date_local TIMESTAMP,
    metadata JSONB,  -- Raw API payload + extras
    full_text TEXT,
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Bill-specific fields
    print_no VARCHAR(50) NOT NULL,
    session_year INTEGER NOT NULL,
    bill_type VARCHAR(10),  -- hr, s, hres, sres, etc.
    number INTEGER,
    sponsor VARCHAR(200),
    status VARCHAR(50),
    introduced_date TIMESTAMP,
    last_action_date TIMESTAMP,
    amends_source_url VARCHAR(500),  -- For amendments
    amendment_number INTEGER
);

-- Federal Committees
CREATE TABLE IF NOT EXISTS federal_committees (
    id BIGSERIAL PRIMARY KEY,
    committee_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    chamber VARCHAR(10),  -- house, senate, joint
    type VARCHAR(50),  -- standing, select, joint
    jurisdiction TEXT,
    members JSONB,  -- Array of {name, role, party}
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Federal Hearings
CREATE TABLE IF NOT EXISTS federal_hearings (
    id BIGSERIAL PRIMARY KEY,
    hearing_id VARCHAR(100) UNIQUE NOT NULL,
    congress INTEGER NOT NULL,
    committee_code VARCHAR(50) REFERENCES federal_committees(committee_code),
    date TIMESTAMP NOT NULL,
    location VARCHAR(200),
    witnesses JSONB,  -- Array of {name, title, testimony}
    summary TEXT,
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Congressional Records
CREATE TABLE IF NOT EXISTS federal_records (
    id BIGSERIAL PRIMARY KEY,
    record_id VARCHAR(100) UNIQUE NOT NULL,
    congress INTEGER NOT NULL,
    date DATE NOT NULL,
    chamber VARCHAR(10),
    speakers JSONB,  -- Array of {name, party, state, text}
    text TEXT,
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Federal Register Documents
CREATE TABLE IF NOT EXISTS federal_register_docs (
    id BIGSERIAL PRIMARY KEY,
    docket_id VARCHAR(100) UNIQUE NOT NULL,
    congress INTEGER,
    agencies JSONB,  -- Array of {name, type}
    publication_date DATE,
    text TEXT,
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Laws
CREATE TABLE IF NOT EXISTS federal_laws (
    id BIGSERIAL PRIMARY KEY,
    public_law_number VARCHAR(50) UNIQUE NOT NULL,
    congress INTEGER NOT NULL,
    sections JSONB,  -- Array of {number, title, text}
    enacted_date DATE,
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nominations
CREATE TABLE IF NOT EXISTS federal_nominations (
    id BIGSERIAL PRIMARY KEY,
    nomination_number VARCHAR(50) UNIQUE NOT NULL,
    congress INTEGER NOT NULL,
    nominee_name VARCHAR(200),
    position VARCHAR(200),
    status VARCHAR(50),
    committee VARCHAR(100),
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Treaties
CREATE TABLE IF NOT EXISTS federal_treaties (
    id BIGSERIAL PRIMARY KEY,
    treaty_doc_number VARCHAR(50) UNIQUE NOT NULL,
    congress INTEGER NOT NULL,
    title TEXT,
    status VARCHAR(50),
    signatories JSONB,  -- Array of {country, date, representative}
    source_url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== GOVINFO TABLES ====================

-- GovInfo Bill Metadata
CREATE TABLE IF NOT EXISTS govinfo_bill (
    id SERIAL PRIMARY KEY,
    bill_print_no VARCHAR(50) NOT NULL,
    session_year INTEGER NOT NULL,
    bill_type VARCHAR(10) NOT NULL,  -- H, S
    title TEXT,
    short_title TEXT,
    summary TEXT,
    congress INTEGER NOT NULL,
    sponsor_name VARCHAR(200),
    sponsor_party VARCHAR(10),
    sponsor_state VARCHAR(2),
    introduced_date TIMESTAMP,
    active_version VARCHAR(50),
    modified_date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, bill_print_no, session_year)
);

-- GovInfo Bill Actions
CREATE TABLE IF NOT EXISTS govinfo_bill_action (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES govinfo_bill(id),
    action_code VARCHAR(20),
    text TEXT,
    action_date TIMESTAMP,
    sequence_no INTEGER,
    chamber VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GovInfo Bill Cosponsors
CREATE TABLE IF NOT EXISTS govinfo_bill_cosponsor (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES govinfo_bill(id),
    sponsor_name VARCHAR(200),
    party VARCHAR(10),
    state VARCHAR(2),
    role VARCHAR(20) DEFAULT 'cosponsor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GovInfo Bill Committees
CREATE TABLE IF NOT EXISTS govinfo_bill_committee (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES govinfo_bill(id),
    committee_name VARCHAR(200),
    activity VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== INGESTION TRACKING TABLES ====================

-- Generic Ingestion Status (for all data types)
CREATE TABLE IF NOT EXISTS master_ingestion_status (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'unknown',
    ingestion_status TEXT NOT NULL CHECK (ingestion_status IN ('pending', 'in_progress', 'completed', 'failed')),
    last_attempted_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    failure_reason TEXT,
    metadata JSONB,
    processing_priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    ingestion_session_id TEXT,
    UNIQUE(table_name, record_id, source)
);

-- Federal Member Ingestion Status (specific for federal members)
CREATE TABLE IF NOT EXISTS federal_member_ingestion_status (
    id BIGSERIAL PRIMARY KEY,
    bioguide_id VARCHAR(20) NOT NULL,
    ingestion_session_id TEXT NOT NULL,
    ingestion_status TEXT NOT NULL CHECK (ingestion_status IN ('pending', 'in_progress', 'completed', 'failed')),
    last_attempted_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    failure_reason TEXT,
    processing_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(bioguide_id, ingestion_session_id)
);

-- ==================== INDEXES FOR PERFORMANCE ====================

-- OpenStates indexes
CREATE INDEX IF NOT EXISTS idx_jurisdiction_classification ON opencivicdata_jurisdiction(classification);
CREATE INDEX IF NOT EXISTS idx_legislative_session_jurisdiction ON opencivicdata_legislativesession(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_organization_jurisdiction ON opencivicdata_organization(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_organization_classification ON opencivicdata_organization(classification);
CREATE INDEX IF NOT EXISTS idx_person_name ON opencivicdata_person(name);
CREATE INDEX IF NOT EXISTS idx_person_jurisdiction ON opencivicdata_person(current_jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_bill_organization ON opencivicdata_bill(from_organization_id);
CREATE INDEX IF NOT EXISTS idx_bill_session ON opencivicdata_bill(legislative_session_id);
CREATE INDEX IF NOT EXISTS idx_bill_action_bill ON opencivicdata_billaction(bill_id);
CREATE INDEX IF NOT EXISTS idx_bill_action_date ON opencivicdata_billaction(date);
CREATE INDEX IF NOT EXISTS idx_vote_event_organization ON opencivicdata_voteevent(organization_id);
CREATE INDEX IF NOT EXISTS idx_vote_event_date ON opencivicdata_voteevent(start_date);

-- Federal indexes
CREATE INDEX IF NOT EXISTS idx_federal_members_bioguide ON federal_members(bioguide_id);
CREATE INDEX IF NOT EXISTS idx_federal_members_state ON federal_members(state);
CREATE INDEX IF NOT EXISTS idx_federal_members_chamber ON federal_members(chamber);
CREATE INDEX IF NOT EXISTS idx_federal_members_party ON federal_members(party);
CREATE INDEX IF NOT EXISTS idx_federal_bills_congress ON federal_bills(congress);
CREATE INDEX IF NOT EXISTS idx_federal_bills_type ON federal_bills(document_type);
CREATE INDEX IF NOT EXISTS idx_federal_bills_printno ON federal_bills(print_no, session_year);
CREATE INDEX IF NOT EXISTS idx_federal_committees_code ON federal_committees(committee_code);
CREATE INDEX IF NOT EXISTS idx_federal_hearings_congress ON federal_hearings(congress);
CREATE INDEX IF NOT EXISTS idx_federal_records_congress_date ON federal_records(congress, date);
CREATE INDEX IF NOT EXISTS idx_federal_laws_congress ON federal_laws(congress);
CREATE INDEX IF NOT EXISTS idx_federal_nominations_congress ON federal_nominations(congress);
CREATE INDEX IF NOT EXISTS idx_federal_treaties_congress ON federal_treaties(congress);

-- GovInfo indexes
CREATE INDEX IF NOT EXISTS idx_govinfo_bill_congress ON govinfo_bill(congress);
CREATE INDEX IF NOT EXISTS idx_govinfo_bill_congress_number ON govinfo_bill(congress, bill_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_action_date ON govinfo_bill_action(action_date);
CREATE INDEX IF NOT EXISTS idx_govinfo_cosponsor_name ON govinfo_bill_cosponsor(sponsor_name);
CREATE INDEX IF NOT EXISTS idx_govinfo_committee_name ON govinfo_bill_committee(committee_name);

-- Ingestion tracking indexes
CREATE INDEX IF NOT EXISTS idx_ingestion_status_table_record ON master_ingestion_status(table_name, record_id, source);
CREATE INDEX IF NOT EXISTS idx_ingestion_status_status ON master_ingestion_status(ingestion_status);
CREATE INDEX IF NOT EXISTS idx_ingestion_status_session ON master_ingestion_status(ingestion_session_id);
CREATE INDEX IF NOT EXISTS idx_federal_member_status_bioguide ON federal_member_ingestion_status(bioguide_id);
CREATE INDEX IF NOT EXISTS idx_federal_member_status_session ON federal_member_ingestion_status(ingestion_session_id);

-- ==================== FUNCTIONS AND TRIGGERS ====================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_opencivicdata_jurisdiction_updated_at BEFORE UPDATE ON opencivicdata_jurisdiction
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opencivicdata_legislativesession_updated_at BEFORE UPDATE ON opencivicdata_legislativesession
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opencivicdata_organization_updated_at BEFORE UPDATE ON opencivicdata_organization
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opencivicdata_person_updated_at BEFORE UPDATE ON opencivicdata_person
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opencivicdata_bill_updated_at BEFORE UPDATE ON opencivicdata_bill
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opencivicdata_billaction_updated_at BEFORE UPDATE ON opencivicdata_billaction
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opencivicdata_voteevent_updated_at BEFORE UPDATE ON opencivicdata_voteevent
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_members_updated_at BEFORE UPDATE ON federal_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_bills_updated_at BEFORE UPDATE ON federal_bills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_committees_updated_at BEFORE UPDATE ON federal_committees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_hearings_updated_at BEFORE UPDATE ON federal_hearings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_records_updated_at BEFORE UPDATE ON federal_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_register_docs_updated_at BEFORE UPDATE ON federal_register_docs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_laws_updated_at BEFORE UPDATE ON federal_laws
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_nominations_updated_at BEFORE UPDATE ON federal_nominations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_treaties_updated_at BEFORE UPDATE ON federal_treaties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_govinfo_bill_updated_at BEFORE UPDATE ON govinfo_bill
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ingestion_status_updated_at BEFORE UPDATE ON master_ingestion_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_member_ingestion_status_updated_at BEFORE UPDATE ON federal_member_ingestion_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== COMMENTS FOR DOCUMENTATION ====================

COMMENT ON TABLE opencivicdata_jurisdiction IS 'State and territorial jurisdictions following Open Civic Data standard';
COMMENT ON TABLE opencivicdata_legislativesession IS 'Legislative sessions for each jurisdiction';
COMMENT ON TABLE opencivicdata_organization IS 'Organizations including committees, parties, and government bodies';
COMMENT ON TABLE opencivicdata_person IS 'Individual people including legislators and officials';
COMMENT ON TABLE opencivicdata_bill IS 'Legislative bills from all jurisdictions';
COMMENT ON TABLE opencivicdata_billaction IS 'Actions taken on bills';
COMMENT ON TABLE opencivicdata_voteevent IS 'Vote events and roll calls';

COMMENT ON TABLE federal_members IS 'Federal legislators from Congress.gov API';
COMMENT ON TABLE federal_bills IS 'Federal bills, amendments, and resolutions from Congress.gov API';
COMMENT ON TABLE federal_committees IS 'Federal committees from Congress.gov API';
COMMENT ON TABLE federal_hearings IS 'Federal hearings from Congress.gov API';
COMMENT ON TABLE federal_records IS 'Congressional records from Congress.gov API';
COMMENT ON TABLE federal_register_docs IS 'Federal register documents from Congress.gov API';
COMMENT ON TABLE federal_laws IS 'Federal laws from Congress.gov API';
COMMENT ON TABLE federal_nominations IS 'Federal nominations from Congress.gov API';
COMMENT ON TABLE federal_treaties IS 'Federal treaties from Congress.gov API';

COMMENT ON TABLE govinfo_bill IS 'Bill metadata from GovInfo.gov';
COMMENT ON TABLE govinfo_bill_action IS 'Bill action history from GovInfo.gov';
COMMENT ON TABLE govinfo_bill_cosponsor IS 'Bill cosponsors from GovInfo.gov';
COMMENT ON TABLE govinfo_bill_committee IS 'Bill committee assignments from GovInfo.gov';

COMMENT ON TABLE master_ingestion_status IS 'Generic ingestion tracking for all data types';
COMMENT ON TABLE federal_member_ingestion_status IS 'Specific ingestion tracking for federal members';

-- Verification query (run after migration)
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;