# Database Schema Design - OpenDiscourse

## Overview
This document outlines the proposed database schema for the OpenDiscourse platform, designed to store and organize data from multiple government sources including OpenStates, Congress.gov, GovInfo.gov, and OpenLegislation, along with social media data and user-generated content.

## Core Entities

### 1. Jurisdictions
```sql
CREATE TABLE jurisdictions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,  -- e.g., 'CA', 'US', 'FED'
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,         -- 'state', 'federal', 'municipal'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Legislators
```sql
CREATE TABLE legislators (
    id SERIAL PRIMARY KEY,
    openstates_person_id VARCHAR(100) UNIQUE,     -- OpenStates ID
    bioguide_id VARCHAR(20) UNIQUE,               -- Congress.gov ID
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    gender VARCHAR(10),
    email VARCHAR(200),
    party VARCHAR(50),
    photo_url TEXT,
    website_url TEXT,
    facebook_url TEXT,
    twitter_handle VARCHAR(50),
    youtube_url TEXT,
    instagram_handle VARCHAR(50),
    linkedin_url TEXT,
    birth_date DATE,
    death_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Legislative Sessions
```sql
CREATE TABLE legislative_sessions (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    name VARCHAR(200) NOT NULL,
    identifier VARCHAR(100) NOT NULL,
    classification VARCHAR(50),        -- 'primary', 'special'
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Bills
```sql
CREATE TABLE bills (
    id SERIAL PRIMARY KEY,
    openstates_bill_id VARCHAR(100) UNIQUE,       -- OpenStates ID
    congress_gov_bill_id VARCHAR(100) UNIQUE,     -- Congress.gov ID
    bill_type VARCHAR(50),                        -- 'bill', 'resolution', 'joint resolution'
    bill_number VARCHAR(20),
    title TEXT,
    description TEXT,
    subject TEXT,
    chamber VARCHAR(20),                          -- 'upper', 'lower', 'joint'
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    session_id INTEGER REFERENCES legislative_sessions(id),
    introduced_date DATE,
    sponsor_id INTEGER REFERENCES legislators(id),
    status VARCHAR(50),                           -- 'introduced', 'passed', 'failed', 'enacted'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Bill Co-sponsors
```sql
CREATE TABLE bill_cosponsors (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id),
    legislator_id INTEGER REFERENCES legislators(id),
    cosponsor_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. Bill Actions
```sql
CREATE TABLE bill_actions (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id),
    action_type VARCHAR(100),
    description TEXT,
    date DATE,
    actor VARCHAR(50),                            -- 'upper', 'lower', 'executive'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. Votes
```sql
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    openstates_vote_id VARCHAR(100) UNIQUE,       -- OpenStates ID
    congress_gov_vote_id VARCHAR(100) UNIQUE,     -- Congress.gov ID
    bill_id INTEGER REFERENCES bills(id),
    motion_text TEXT,
    motion_type VARCHAR(100),
    result VARCHAR(50),                           -- 'pass', 'fail'
    date DATE,
    chamber VARCHAR(20),                          -- 'upper', 'lower', 'joint'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 8. Vote Details
```sql
CREATE TABLE vote_details (
    id SERIAL PRIMARY KEY,
    vote_id INTEGER REFERENCES votes(id),
    legislator_id INTEGER REFERENCES legislators(id),
    vote_option VARCHAR(20),                      -- 'yes', 'no', 'absent', 'abstain'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 9. Committees
```sql
CREATE TABLE committees (
    id SERIAL PRIMARY KEY,
    openstates_committee_id VARCHAR(100) UNIQUE,  -- OpenStates ID
    congress_gov_committee_id VARCHAR(100) UNIQUE, -- Congress.gov ID
    name VARCHAR(200),
    chamber VARCHAR(20),                          -- 'upper', 'lower', 'joint'
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 10. Committee Memberships
```sql
CREATE TABLE committee_memberships (
    id SERIAL PRIMARY KEY,
    committee_id INTEGER REFERENCES committees(id),
    legislator_id INTEGER REFERENCES legislators(id),
    role VARCHAR(50),                             -- 'chair', 'member', 'ranking'
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11. Social Media Posts
```sql
CREATE TABLE social_media_posts (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES legislators(id),
    platform VARCHAR(20),                         -- 'twitter', 'facebook', 'youtube'
    post_id VARCHAR(100),                         -- Platform-specific ID
    content TEXT,
    posted_at TIMESTAMP,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 12. Legislator Profiles
```sql
CREATE TABLE legislator_profiles (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES legislators(id),
    bio TEXT,
    education TEXT,
    professional_experience TEXT,
    political_experience TEXT,
    committees TEXT,
    key_votes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 13. Discrepancy Reports
```sql
CREATE TABLE discrepancy_reports (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES legislators(id),
    bill_id INTEGER REFERENCES bills(id),
    vote_position VARCHAR(20),                    -- 'yes', 'no', 'absent', 'abstain'
    statement_content TEXT,
    statement_source VARCHAR(20),                 -- 'twitter', 'facebook', 'speech'
    discrepancy_type VARCHAR(50),                 -- 'contradiction', 'inconsistency'
    confidence_score DECIMAL(3,2),                -- 0.00 to 1.00
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 14. KPI Scores
```sql
CREATE TABLE kpi_scores (
    id SERIAL PRIMARY KEY,
    legislator_id INTEGER REFERENCES legislators(id),
    metric_name VARCHAR(100),                     -- 'consistency', 'truthfulness', 'engagement'
    score DECIMAL(5,2),
    calculation_date DATE,
    calculation_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 15. User Accounts
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(200),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 16. Comments
```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subject_type VARCHAR(20),                     -- 'legislator', 'bill', 'vote'
    subject_id INTEGER,                           -- ID of the subject entity
    content TEXT,
    parent_comment_id INTEGER REFERENCES comments(id),
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 17. Message Board Threads
```sql
CREATE TABLE message_threads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    user_id INTEGER REFERENCES users(id),
    category VARCHAR(50),                         -- 'general', 'bills', 'legislators'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 18. Message Board Posts
```sql
CREATE TABLE message_posts (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES message_threads(id),
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    parent_post_id INTEGER REFERENCES message_posts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes for Performance

```sql
-- Performance indexes
CREATE INDEX idx_bills_jurisdiction ON bills(jurisdiction_id);
CREATE INDEX idx_bills_session ON bills(session_id);
CREATE INDEX idx_bills_sponsor ON bills(sponsor_id);
CREATE INDEX idx_bills_type_number ON bills(bill_type, bill_number);
CREATE INDEX idx_votes_bill ON votes(bill_id);
CREATE INDEX idx_vote_details_vote ON vote_details(vote_id);
CREATE INDEX idx_vote_details_legislator ON vote_details(legislator_id);
CREATE INDEX idx_social_media_legislator ON social_media_posts(legislator_id);
CREATE INDEX idx_social_media_posted_at ON social_media_posts(posted_at);
CREATE INDEX idx_discrepancy_reports_legislator ON discrepancy_reports(legislator_id);
CREATE INDEX idx_kpi_scores_legislator ON kpi_scores(legislator_id);
CREATE INDEX idx_kpi_scores_date ON kpi_scores(calculation_date);
CREATE INDEX idx_comments_subject ON comments(subject_type, subject_id);
```

## Views for Common Queries

### 1. Legislator Voting Summary
```sql
CREATE VIEW legislator_voting_summary AS
SELECT 
    l.id AS legislator_id,
    l.full_name,
    COUNT(vd.id) AS total_votes,
    COUNT(CASE WHEN vd.vote_option = 'yes' THEN 1 END) AS yes_votes,
    COUNT(CASE WHEN vd.vote_option = 'no' THEN 1 END) AS no_votes,
    COUNT(CASE WHEN vd.vote_option = 'absent' THEN 1 END) AS absent_votes,
    COUNT(CASE WHEN vd.vote_option = 'abstain' THEN 1 END) AS abstain_votes,
    ROUND(
        COUNT(CASE WHEN vd.vote_option = 'yes' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(vd.id), 0), 2
    ) AS yes_percentage
FROM legislators l
LEFT JOIN vote_details vd ON l.id = vd.legislator_id
GROUP BY l.id, l.full_name;
```

### 2. Bill Summary with Sponsor Information
```sql
CREATE VIEW bill_summary AS
SELECT 
    b.id,
    b.bill_number,
    b.title,
    b.status,
    j.name AS jurisdiction_name,
    l.full_name AS sponsor_name,
    b.introduced_date,
    COUNT(bc.id) AS cosponsor_count
FROM bills b
JOIN jurisdictions j ON b.jurisdiction_id = j.id
LEFT JOIN legislators l ON b.sponsor_id = l.id
LEFT JOIN bill_cosponsors bc ON b.id = bc.bill_id
GROUP BY b.id, b.bill_number, b.title, b.status, j.name, l.full_name, b.introduced_date;
```

### 3. Recent Activity Feed
```sql
CREATE VIEW recent_activity AS
SELECT 
    'bill' AS activity_type,
    b.id AS subject_id,
    b.title AS subject_title,
    b.updated_at AS activity_time
FROM bills b
WHERE b.updated_at > NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'vote' AS activity_type,
    v.id AS subject_id,
    v.motion_text AS subject_title,
    v.updated_at AS activity_time
FROM votes v
WHERE v.updated_at > NOW() - INTERVAL '30 days'

UNION ALL

SELECT 
    'social_post' AS activity_type,
    s.id AS subject_id,
    LEFT(s.content, 100) AS subject_title,
    s.posted_at AS activity_time
FROM social_media_posts s
WHERE s.posted_at > NOW() - INTERVAL '30 days'

ORDER BY activity_time DESC;
```

## Data Relationships Diagram

```
Jurisdictions
    |
    |-- Legislative Sessions
    |       |
    |       |-- Bills
    |       |   |-- Bill Actions
    |       |   |-- Bill Co-sponsors
    |       |   |-- Votes
    |       |       |-- Vote Details
    |
    |-- Committees
    |   |-- Committee Memberships
    |
    |-- Legislators
        |-- Legislator Profiles
        |-- Social Media Posts
        |-- Discrepancy Reports
        |-- KPI Scores
        |-- Comments (as subject)
```

## Data Storage Considerations

### Text Search
- Use PostgreSQL full-text search capabilities for content indexing
- Create tsvector columns for bills, social media posts, and comments
- Implement ranking for search result relevance

### Historical Data
- Implement soft deletes where appropriate
- Use timestamp columns to track data changes
- Consider partitioning for large tables (e.g., social_media_posts by date)

### Data Archiving
- Archive old sessions and their associated data
- Implement compression for text-heavy columns
- Plan for data retention policies

## Scalability Features

### Horizontal Partitioning
- Social media posts by date
- Vote details by legislative session
- Comments by creation date

### Read Replicas
- Separate read replicas for reporting queries
- Dedicated database for search indexing
- Caching layer for frequently accessed data

### Data Warehousing
- Consider separate analytics database for complex reporting
- Implement ETL processes for data transformation
- Use columnar storage for analytical queries