-- Migration 004_create_openlegislation_tables.sql
-- Create tables for OpenLegislation data

-- Bills table
CREATE TABLE IF NOT EXISTS openlegislation_bills (
    id TEXT PRIMARY KEY,
    year TEXT,
    senate_bill_no TEXT,
    assembly_bill_no TEXT,
    title TEXT,
    law_section TEXT,
    same_as TEXT,
    previous_versions JSONB,
    sponsor_name TEXT,
    sponsor_fullname TEXT,
    co_sponsors JSONB,
    multi_sponsors JSONB,
    summary TEXT,
    current_committee TEXT,
    actions JSONB,
    full_text TEXT,
    memo TEXT,
    law TEXT,
    votes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bill actions table
CREATE TABLE IF NOT EXISTS openlegislation_bill_actions (
    id SERIAL PRIMARY KEY,
    bill_id TEXT REFERENCES openlegislation_bills(id),
    action_date BIGINT,
    action_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bill votes table
CREATE TABLE IF NOT EXISTS openlegislation_bill_votes (
    id SERIAL PRIMARY KEY,
    bill_id TEXT REFERENCES openlegislation_bills(id),
    vote_type TEXT,
    vote_date BIGINT,
    ayes JSONB,
    nays JSONB,
    abstains JSONB,
    excused JSONB,
    ayeswr JSONB,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meetings table
CREATE TABLE IF NOT EXISTS openlegislation_meetings (
    id TEXT PRIMARY KEY,
    meeting_date_time BIGINT,
    meet_day TEXT,
    location TEXT,
    committee_name TEXT,
    committee_chair TEXT,
    bills JSONB,
    notes TEXT,
    addendums JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meeting bills table (for normalized structure)
CREATE TABLE IF NOT EXISTS openlegislation_meeting_bills (
    id SERIAL PRIMARY KEY,
    meeting_id TEXT REFERENCES openlegislation_meetings(id),
    bill_year TEXT,
    bill_senate_no TEXT,
    bill_title TEXT,
    bill_same_as TEXT,
    bill_sponsor_fullname TEXT,
    bill_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calendars table
CREATE TABLE IF NOT EXISTS openlegislation_calendars (
    id TEXT PRIMARY KEY,
    year TEXT,
    calendar_type TEXT,
    session_year TEXT,
    calendar_no TEXT,
    supplementals JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calendar entries table (for normalized structure)
CREATE TABLE IF NOT EXISTS openlegislation_calendar_entries (
    id SERIAL PRIMARY KEY,
    calendar_id TEXT REFERENCES openlegislation_calendars(id),
    entry_no TEXT,
    bill_year TEXT,
    bill_senate_no TEXT,
    bill_title TEXT,
    bill_same_as TEXT,
    bill_sponsor_fullname TEXT,
    bill_summary TEXT,
    bill_high BOOLEAN,
    sub_bill TEXT,
    motion_date BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transcripts table
CREATE TABLE IF NOT EXISTS openlegislation_transcripts (
    id TEXT PRIMARY KEY,
    time_stamp BIGINT,
    location TEXT,
    session_type TEXT,
    transcript_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_openlegislation_bills_year ON openlegislation_bills(year);
CREATE INDEX IF NOT EXISTS idx_openlegislation_bills_senate_no ON openlegislation_bills(senate_bill_no);
CREATE INDEX IF NOT EXISTS idx_openlegislation_bills_sponsor ON openlegislation_bills(sponsor_fullname);
CREATE INDEX IF NOT EXISTS idx_openlegislation_bills_updated_at ON openlegislation_bills(updated_at);
CREATE INDEX IF NOT EXISTS idx_openlegislation_bill_actions_bill ON openlegislation_bill_actions(bill_id);
CREATE INDEX IF NOT EXISTS idx_openlegislation_bill_actions_date ON openlegislation_bill_actions(action_date);
CREATE INDEX IF NOT EXISTS idx_openlegislation_bill_votes_bill ON openlegislation_bill_votes(bill_id);
CREATE INDEX IF NOT EXISTS idx_openlegislation_bill_votes_date ON openlegislation_bill_votes(vote_date);
CREATE INDEX IF NOT EXISTS idx_openlegislation_meetings_date ON openlegislation_meetings(meeting_date_time);
CREATE INDEX IF NOT EXISTS idx_openlegislation_meetings_committee ON openlegislation_meetings(committee_name);
CREATE INDEX IF NOT EXISTS idx_openlegislation_meeting_bills_meeting ON openlegislation_meeting_bills(meeting_id);
CREATE INDEX IF NOT EXISTS idx_openlegislation_calendars_year ON openlegislation_calendars(year);
CREATE INDEX IF NOT EXISTS idx_openlegislation_calendars_type ON openlegislation_calendars(calendar_type);
CREATE INDEX IF NOT EXISTS idx_openlegislation_calendar_entries_calendar ON openlegislation_calendar_entries(calendar_id);
CREATE INDEX IF NOT EXISTS idx_openlegislation_transcripts_date ON openlegislation_transcripts(time_stamp);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_openlegislation_bills_fts ON openlegislation_bills USING gin(to_tsvector('english', title || ' ' || coalesce(summary, '') || ' ' || coalesce(memo, '')));
CREATE INDEX IF NOT EXISTS idx_openlegislation_bill_actions_fts ON openlegislation_bill_actions USING gin(to_tsvector('english', action_text));
CREATE INDEX IF NOT EXISTS idx_openlegislation_meetings_fts ON openlegislation_meetings USING gin(to_tsvector('english', committee_name || ' ' || coalesce(notes, '')));
CREATE INDEX IF NOT EXISTS idx_openlegislation_transcripts_fts ON openlegislation_transcripts USING gin(to_tsvector('english', transcript_text));