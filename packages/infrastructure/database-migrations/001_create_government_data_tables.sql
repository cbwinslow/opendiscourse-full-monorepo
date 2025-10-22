-- Migration: Create government data tables
-- Description: Initial schema for storing government legislative data from multiple sources

-- Jurisdictions table (for state and federal entities)
CREATE TABLE jurisdictions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    classification TEXT,
    division_id TEXT,
    division_name TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legislative sessions table
CREATE TABLE legislative_sessions (
    id TEXT PRIMARY KEY,
    jurisdiction_id TEXT REFERENCES jurisdictions(id),
    identifier TEXT,
    name TEXT,
    classification TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- People table (legislators, governors, etc.)
CREATE TABLE people (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    given_name TEXT,
    family_name TEXT,
    email TEXT,
    gender TEXT,
    biography TEXT,
    birth_date DATE,
    image_url TEXT,
    source_url TEXT,
    source_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Person roles table (tracking positions over time)
CREATE TABLE person_roles (
    id SERIAL PRIMARY KEY,
    person_id TEXT REFERENCES people(id),
    type TEXT,
    district TEXT,
    jurisdiction_id TEXT REFERENCES jurisdictions(id),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Political parties table
CREATE TABLE parties (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Person party affiliations table
CREATE TABLE person_party_affiliations (
    id SERIAL PRIMARY KEY,
    person_id TEXT REFERENCES people(id),
    party_id INTEGER REFERENCES parties(id),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills table
CREATE TABLE bills (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES legislative_sessions(id),
    jurisdiction_id TEXT REFERENCES jurisdictions(id),
    identifier TEXT,
    title TEXT,
    classification TEXT[],
    subject TEXT[],
    extras JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    openstates_url TEXT,
    congress_gov_url TEXT,
    govinfo_url TEXT
);

-- Bill sponsors table
CREATE TABLE bill_sponsors (
    id SERIAL PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    person_id TEXT REFERENCES people(id),
    organization_name TEXT,
    entity_type TEXT,
    primary_sponsor BOOLEAN,
    classification TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bill actions table
CREATE TABLE bill_actions (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    organization_name TEXT,
    description TEXT,
    date DATE,
    classification TEXT[],
    order_num INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Votes table
CREATE TABLE votes (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    motion_text TEXT,
    result TEXT,
    date DATE,
    organization_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vote details table
CREATE TABLE vote_details (
    id SERIAL PRIMARY KEY,
    vote_id TEXT REFERENCES votes(id),
    person_id TEXT REFERENCES people(id),
    option TEXT, -- yes, no, abstain, not voting
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bill versions table (different versions of the same bill)
CREATE TABLE bill_versions (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    note TEXT,
    date DATE,
    url TEXT,
    media_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bill documents table (supporting documents)
CREATE TABLE bill_documents (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    note TEXT,
    date DATE,
    url TEXT,
    media_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Committees table
CREATE TABLE committees (
    id TEXT PRIMARY KEY,
    name TEXT,
    chamber TEXT,
    jurisdiction_id TEXT REFERENCES jurisdictions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Committee memberships table
CREATE TABLE committee_memberships (
    id SERIAL PRIMARY KEY,
    committee_id TEXT REFERENCES committees(id),
    person_id TEXT REFERENCES people(id),
    role TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events table (committee meetings, sessions, etc.)
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    name TEXT,
    jurisdiction_id TEXT REFERENCES jurisdictions(id),
    description TEXT,
    classification TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    all_day BOOLEAN,
    status TEXT,
    location_name TEXT,
    location_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event participants table
CREATE TABLE event_participants (
    id SERIAL PRIMARY KEY,
    event_id TEXT REFERENCES events(id),
    person_id TEXT REFERENCES people(id),
    name TEXT,
    entity_type TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event agenda items table
CREATE TABLE event_agenda_items (
    id SERIAL PRIMARY KEY,
    event_id TEXT REFERENCES events(id),
    description TEXT,
    order_num INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social media platforms table
CREATE TABLE social_media_platforms (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    base_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Person social media accounts table
CREATE TABLE person_social_media_accounts (
    id SERIAL PRIMARY KEY,
    person_id TEXT REFERENCES people(id),
    platform_id INTEGER REFERENCES social_media_platforms(id),
    username TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social media posts table
CREATE TABLE social_media_posts (
    id TEXT PRIMARY KEY,
    person_id TEXT REFERENCES people(id),
    platform_id INTEGER REFERENCES social_media_platforms(id),
    post_id TEXT,
    content TEXT,
    post_url TEXT,
    posted_at TIMESTAMP,
    likes_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    sentiment_score NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Post topics table (for categorizing social media content)
CREATE TABLE post_topics (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social media post topics table (many-to-many relationship)
CREATE TABLE social_media_post_topics (
    id SERIAL PRIMARY KEY,
    post_id TEXT REFERENCES social_media_posts(id),
    topic_id INTEGER REFERENCES post_topics(id),
    confidence_score NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for better query performance
CREATE INDEX idx_bills_jurisdiction ON bills(jurisdiction_id);
CREATE INDEX idx_bills_session ON bills(session_id);
CREATE INDEX idx_bills_created_at ON bills(created_at);
CREATE INDEX idx_bills_updated_at ON bills(updated_at);
CREATE INDEX idx_bills_identifier ON bills(identifier);
CREATE INDEX idx_people_name ON people(name);
CREATE INDEX idx_people_updated_at ON people(updated_at);
CREATE INDEX idx_bill_actions_date ON bill_actions(date);
CREATE INDEX idx_bill_actions_bill_id ON bill_actions(bill_id);
CREATE INDEX idx_votes_bill_id ON votes(bill_id);
CREATE INDEX idx_votes_date ON votes(date);
CREATE INDEX idx_social_media_posts_person_id ON social_media_posts(person_id);
CREATE INDEX idx_social_media_posts_posted_at ON social_media_posts(posted_at);
CREATE INDEX idx_social_media_posts_sentiment ON social_media_posts(sentiment_score);
CREATE INDEX idx_events_jurisdiction_id ON events(jurisdiction_id);
CREATE INDEX idx_events_start_date ON events(start_date);
CREATE INDEX idx_committees_jurisdiction_id ON committees(jurisdiction_id);

-- Insert default political parties
INSERT INTO parties (name) VALUES 
('Democratic'),
('Republican'),
('Independent'),
('Libertarian'),
('Green'),
('Other');

-- Insert default social media platforms
INSERT INTO social_media_platforms (name, base_url) VALUES 
('Twitter', 'https://twitter.com/'),
('Facebook', 'https://facebook.com/'),
('YouTube', 'https://youtube.com/'),
('Instagram', 'https://instagram.com/'),
('LinkedIn', 'https://linkedin.com/in/');