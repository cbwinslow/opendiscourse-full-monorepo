-- Migration 005_create_master_tables.sql
-- Create master tables that combine data from all sources

-- Master legislators table
CREATE TABLE IF NOT EXISTS master_legislators (
    id SERIAL PRIMARY KEY,
    bioguide_id TEXT UNIQUE,
    openstates_id TEXT UNIQUE,
    congressgov_id TEXT UNIQUE,
    full_name TEXT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    suffix TEXT,
    gender TEXT,
    date_of_birth DATE,
    party TEXT,
    state TEXT,
    chamber TEXT,
    district TEXT,
    senate_class TEXT,
    in_office BOOLEAN,
    twitter_account TEXT,
    facebook_account TEXT,
    youtube_account TEXT,
    website_url TEXT,
    contact_form TEXT,
    office_address TEXT,
    phone TEXT,
    fax TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master bills table
CREATE TABLE IF NOT EXISTS master_bills (
    id SERIAL PRIMARY KEY,
    bill_id TEXT UNIQUE,
    openstates_bill_id TEXT,
    congressgov_bill_id TEXT,
    govinfo_bill_id TEXT,
    openlegislation_bill_id TEXT,
    bill_type TEXT,
    bill_number TEXT,
    congress_number INTEGER,
    state TEXT,
    jurisdiction TEXT,
    title TEXT,
    short_title TEXT,
    summary TEXT,
    introduced_date DATE,
    sponsor_id INTEGER REFERENCES master_legislators(id),
    sponsor_name TEXT,
    committees JSONB,
    primary_subject TEXT,
    latest_action_date DATE,
    latest_action TEXT,
    house_passage DATE,
    senate_passage DATE,
    enacted_date DATE,
    vetoed_date DATE,
    active BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master votes table
CREATE TABLE IF NOT EXISTS master_votes (
    id SERIAL PRIMARY KEY,
    vote_id TEXT UNIQUE,
    openstates_vote_id TEXT,
    congressgov_vote_id TEXT,
    openlegislation_vote_id TEXT,
    bill_id INTEGER REFERENCES master_bills(id),
    legislator_id INTEGER REFERENCES master_legislators(id),
    vote_date DATE,
    vote_time TIME,
    chamber TEXT,
    motion_text TEXT,
    motion_type TEXT,
    result TEXT,
    vote_position TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master committees table
CREATE TABLE IF NOT EXISTS master_committees (
    id SERIAL PRIMARY KEY,
    committee_id TEXT UNIQUE,
    openstates_committee_id TEXT,
    congressgov_committee_id TEXT,
    name TEXT,
    chamber TEXT,
    state TEXT,
    jurisdiction TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master committee memberships table
CREATE TABLE IF NOT EXISTS master_committee_memberships (
    id SERIAL PRIMARY KEY,
    master_committee_id INTEGER REFERENCES master_committees(id),
    master_legislator_id INTEGER REFERENCES master_legislators(id),
    rank INTEGER,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master social media posts table
CREATE TABLE IF NOT EXISTS master_social_media_posts (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES master_legislators(id),
    platform TEXT,
    post_id TEXT,
    content TEXT,
    posted_at TIMESTAMP,
    likes INTEGER,
    shares INTEGER,
    comments INTEGER,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master discrepancy reports table
CREATE TABLE IF NOT EXISTS master_discrepancy_reports (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES master_legislators(id),
    bill_id INTEGER REFERENCES master_bills(id),
    vote_position TEXT,
    statement_content TEXT,
    statement_source TEXT,
    discrepancy_type TEXT,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master KPI scores table
CREATE TABLE IF NOT EXISTS master_kpi_scores (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES master_legislators(id),
    metric_name TEXT,
    score DECIMAL(5,2),
    calculation_date DATE,
    calculation_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_master_legislators_bioguide ON master_legislators(bioguide_id);
CREATE INDEX IF NOT EXISTS idx_master_legislators_name ON master_legislators(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_master_legislators_state ON master_legislators(state);
CREATE INDEX IF NOT EXISTS idx_master_legislators_party ON master_legislators(party);
CREATE INDEX IF NOT EXISTS idx_master_legislators_in_office ON master_legislators(in_office);
CREATE INDEX IF NOT EXISTS idx_master_bills_bill_id ON master_bills(bill_id);
CREATE INDEX IF NOT EXISTS idx_master_bills_congress ON master_bills(congress_number);
CREATE INDEX IF NOT EXISTS idx_master_bills_state ON master_bills(state);
CREATE INDEX IF NOT EXISTS idx_master_bills_sponsor ON master_bills(sponsor_id);
CREATE INDEX IF NOT EXISTS idx_master_bills_introduced_date ON master_bills(introduced_date);
CREATE INDEX IF NOT EXISTS idx_master_bills_subject ON master_bills(primary_subject);
CREATE INDEX IF NOT EXISTS idx_master_votes_bill ON master_votes(bill_id);
CREATE INDEX IF NOT EXISTS idx_master_votes_legislator ON master_votes(legislator_id);
CREATE INDEX IF NOT EXISTS idx_master_votes_date ON master_votes(vote_date);
CREATE INDEX IF NOT EXISTS idx_master_committees_name ON master_committees(name);
CREATE INDEX IF NOT EXISTS idx_master_committee_memberships_committee ON master_committee_memberships(master_committee_id);
CREATE INDEX IF NOT EXISTS idx_master_committee_memberships_legislator ON master_committee_memberships(master_legislator_id);
CREATE INDEX IF NOT EXISTS idx_master_social_media_legislator ON master_social_media_posts(legislator_id);
CREATE INDEX IF NOT EXISTS idx_master_social_media_date ON master_social_media_posts(posted_at);
CREATE INDEX IF NOT EXISTS idx_master_discrepancy_legislator ON master_discrepancy_reports(legislator_id);
CREATE INDEX IF NOT EXISTS idx_master_discrepancy_bill ON master_discrepancy_reports(bill_id);
CREATE INDEX IF NOT EXISTS idx_master_kpi_legislator ON master_kpi_scores(legislator_id);
CREATE INDEX IF NOT EXISTS idx_master_kpi_metric ON master_kpi_scores(metric_name);
CREATE INDEX IF NOT EXISTS idx_master_kpi_date ON master_kpi_scores(calculation_date);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_master_legislators_fts ON master_legislators USING gin(to_tsvector('english', full_name || ' ' || coalesce(party, '') || ' ' || coalesce(state, '')));
CREATE INDEX IF NOT EXISTS idx_master_bills_fts ON master_bills USING gin(to_tsvector('english', title || ' ' || coalesce(short_title, '') || ' ' || coalesce(summary, '')));
CREATE INDEX IF NOT EXISTS idx_master_social_media_fts ON master_social_media_posts USING gin(to_tsvector('english', content));