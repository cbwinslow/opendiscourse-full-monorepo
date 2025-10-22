-- Migration 002_create_congressgov_tables.sql
-- Create tables for Congress.gov data

-- Members table
CREATE TABLE IF NOT EXISTS congressgov_members (
    id TEXT PRIMARY KEY,
    title TEXT,
    short_title TEXT,
    api_uri TEXT,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    suffix TEXT,
    date_of_birth DATE,
    gender TEXT,
    party TEXT,
    leadership_role TEXT,
    twitter_account TEXT,
    facebook_account TEXT,
    youtube_account TEXT,
    govtrack_id TEXT,
    cspan_id TEXT,
    votesmart_id TEXT,
    icpsr_id TEXT,
    crp_id TEXT,
    google_entity_id TEXT,
    fec_candidate_id TEXT,
    url TEXT,
    rss_url TEXT,
    contact_form TEXT,
    in_office BOOLEAN,
    cook_pvi TEXT,
    dw_nominate TEXT,
    ideal_point TEXT,
    seniority TEXT,
    next_election TEXT,
    total_votes INTEGER,
    missed_votes INTEGER,
    total_present INTEGER,
    last_updated TIMESTAMP,
    ocd_id TEXT,
    office TEXT,
    phone TEXT,
    fax TEXT,
    state TEXT,
    senate_class TEXT,
    state_rank TEXT,
    district TEXT,
    at_large BOOLEAN,
    geoid TEXT,
    missed_votes_pct DECIMAL(5,2),
    votes_with_party_pct DECIMAL(5,2),
    votes_against_party_pct DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills table
CREATE TABLE IF NOT EXISTS congressgov_bills (
    bill_id TEXT PRIMARY KEY,
    bill_type TEXT,
    number TEXT,
    bill_uri TEXT,
    title TEXT,
    short_title TEXT,
    sponsor_id TEXT REFERENCES congressgov_members(id),
    congressdotgov_url TEXT,
    govtrack_url TEXT,
    introduced_date DATE,
    active BOOLEAN,
    last_vote DATE,
    house_passage DATE,
    senate_passage DATE,
    enacted DATE,
    vetoed DATE,
    cosponsors INTEGER,
    cosponsors_by_party JSONB,
    committees TEXT,
    primary_subject TEXT,
    summary TEXT,
    summary_short TEXT,
    latest_major_action_date DATE,
    latest_major_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Votes table
CREATE TABLE IF NOT EXISTS congressgov_votes (
    id SERIAL PRIMARY KEY,
    member_id TEXT REFERENCES congressgov_members(id),
    chamber TEXT,
    congress TEXT,
    session TEXT,
    roll_call TEXT,
    vote_uri TEXT,
    bill JSONB,
    amendment JSONB,
    description TEXT,
    question TEXT,
    result TEXT,
    date DATE,
    time TIME,
    position TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Committees table
CREATE TABLE IF NOT EXISTS congressgov_committees (
    id TEXT PRIMARY KEY,
    name TEXT,
    chamber TEXT,
    url TEXT,
    minority_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Committee memberships table
CREATE TABLE IF NOT EXISTS congressgov_committee_memberships (
    id SERIAL PRIMARY KEY,
    committee_id TEXT REFERENCES congressgov_committees(id),
    member_id TEXT REFERENCES congressgov_members(id),
    name TEXT,
    party TEXT,
    rank INTEGER,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nominations table
CREATE TABLE IF NOT EXISTS congressgov_nominations (
    nomination_id TEXT PRIMARY KEY,
    number TEXT,
    nomination_type TEXT,
    received_date DATE,
    received_from TEXT,
    status TEXT,
    status_date DATE,
    committee_id TEXT,
    committee_name TEXT,
    nomination_title TEXT,
    organization TEXT,
    reported_to_senate DATE,
    nomination_resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Treaties table
CREATE TABLE IF NOT EXISTS congressgov_treaties (
    treaty_id TEXT PRIMARY KEY,
    number TEXT,
    topic TEXT,
    type TEXT,
    date DATE,
    parties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_congressgov_members_state ON congressgov_members(state);
CREATE INDEX IF NOT EXISTS idx_congressgov_members_party ON congressgov_members(party);
CREATE INDEX IF NOT EXISTS idx_congressgov_members_in_office ON congressgov_members(in_office);
CREATE INDEX IF NOT EXISTS idx_congressgov_members_last_name ON congressgov_members(last_name);
CREATE INDEX IF NOT EXISTS idx_congressgov_members_updated_at ON congressgov_members(updated_at);
CREATE INDEX IF NOT EXISTS idx_congressgov_bills_sponsor ON congressgov_bills(sponsor_id);
CREATE INDEX IF NOT EXISTS idx_congressgov_bills_introduced_date ON congressgov_bills(introduced_date);
CREATE INDEX IF NOT EXISTS idx_congressgov_bills_primary_subject ON congressgov_bills(primary_subject);
CREATE INDEX IF NOT EXISTS idx_congressgov_bills_bill_type ON congressgov_bills(bill_type);
CREATE INDEX IF NOT EXISTS idx_congressgov_bills_updated_at ON congressgov_bills(updated_at);
CREATE INDEX IF NOT EXISTS idx_congressgov_votes_member ON congressgov_votes(member_id);
CREATE INDEX IF NOT EXISTS idx_congressgov_votes_date ON congressgov_votes(date);
CREATE INDEX IF NOT EXISTS idx_congressgov_votes_bill ON congressgov_votes((bill->>'bill_id'));
CREATE INDEX IF NOT EXISTS idx_congressgov_committees_chamber ON congressgov_committees(chamber);
CREATE INDEX IF NOT EXISTS idx_congressgov_committee_memberships_committee ON congressgov_committee_memberships(committee_id);
CREATE INDEX IF NOT EXISTS idx_congressgov_committee_memberships_member ON congressgov_committee_memberships(member_id);
CREATE INDEX IF NOT EXISTS idx_congressgov_nominations_status ON congressgov_nominations(status);
CREATE INDEX IF NOT EXISTS idx_congressgov_nominations_committee ON congressgov_nominations(committee_id);
CREATE INDEX IF NOT EXISTS idx_congressgov_treaties_date ON congressgov_treaties(date);
CREATE INDEX IF NOT EXISTS idx_congressgov_treaties_type ON congressgov_treaties(type);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_congressgov_bills_fts ON congressgov_bills USING gin(to_tsvector('english', title || ' ' || coalesce(short_title, '') || ' ' || coalesce(summary, '')));
CREATE INDEX IF NOT EXISTS idx_congressgov_members_fts ON congressgov_members USING gin(to_tsvector('english', first_name || ' ' || last_name || ' ' || coalesce(middle_name, '')));