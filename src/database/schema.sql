-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- News Sources table
CREATE TABLE news_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- rss, api, web
    category VARCHAR(50),
    bias_score DECIMAL(4,2),
    reliability_score DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES news_sources(id),
    title TEXT NOT NULL,
    content TEXT,
    url VARCHAR(255) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    bias_score DECIMAL(4,2),
    sentiment_score DECIMAL(4,2),
    fact_check_status VARCHAR(20),
    fact_check_score DECIMAL(4,2)
);

-- Political Figures table
CREATE TABLE political_figures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    party VARCHAR(50),
    jurisdiction VARCHAR(100),
    twitter_handle VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Figure Mentions table
CREATE TABLE figure_mentions (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    figure_id INTEGER REFERENCES political_figures(id),
    context TEXT,
    sentiment_score DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Statements table
CREATE TABLE statements (
    id SERIAL PRIMARY KEY,
    figure_id INTEGER REFERENCES political_figures(id),
    content TEXT NOT NULL,
    source_type VARCHAR(50), -- news, twitter, speech
    source_url VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE,
    fact_check_status VARCHAR(20),
    fact_check_score DECIMAL(4,2),
    sentiment_score DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI Agents table
CREATE TABLE ai_agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50), -- content_analysis, fact_check, bias_detection
    model_name VARCHAR(100),
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    payload JSONB,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Embeddings table
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL,
    content_id INTEGER NOT NULL,
    vector BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- TV Streams table
CREATE TABLE tv_streams (
    id SERIAL PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    status VARCHAR(20),
    last_transcribed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Financial News table
CREATE TABLE financial_news (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES news_sources(id),
    title TEXT NOT NULL,
    content TEXT,
    url VARCHAR(255) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    sentiment_score DECIMAL(4,2),
    market_impact_score DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Legislative Documents table
CREATE TABLE legislative_documents (
    id SERIAL PRIMARY KEY,
    package_id VARCHAR(50) UNIQUE NOT NULL,
    collection_code VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    date_issued TIMESTAMP WITH TIME ZONE,
    last_modified TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    document_type VARCHAR(50),
    version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document Analysis table
CREATE TABLE document_analysis (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES legislative_documents(id),
    summary TEXT,
    key_points TEXT[],
    legal_analysis TEXT,
    impact_analysis TEXT,
    sentiment_score DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Entities table
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- person, organization, location, concept
    description TEXT,
    jurisdiction VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document-Entity Relationships
CREATE TABLE document_entities (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES legislative_documents(id),
    entity_id INTEGER REFERENCES entities(id),
    relationship_type VARCHAR(50), -- mentioned, affected, regulated, etc.
    context TEXT,
    sentiment_score DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
