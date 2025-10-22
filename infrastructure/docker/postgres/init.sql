-- init.sql
-- PostgreSQL initialization script for OpenDiscourse

-- Create the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables for document storage
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(1536)  -- Adjust dimension based on your embedding model
);

-- Create indexes for faster similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING hnsw (embedding vector_cosine_ops);

-- Create table for document metadata
CREATE TABLE IF NOT EXISTS document_metadata (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    key TEXT,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for processed entities
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    entity_type TEXT,
    entity_text TEXT,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for relationships between entities
CREATE TABLE IF NOT EXISTS entity_relationships (
    id SERIAL PRIMARY KEY,
    source_entity_id INTEGER REFERENCES entities(id),
    target_entity_id INTEGER REFERENCES entities(id),
    relationship_type TEXT,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for search queries
CREATE TABLE IF NOT EXISTS search_queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT,
    query_embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for search results
CREATE TABLE IF NOT EXISTS search_results (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES search_queries(id),
    document_id INTEGER REFERENCES documents(id),
    similarity_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update the updated_at column
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create user preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    preference_key VARCHAR(100),
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create triggers for user_preferences
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create sessions table for tracking user sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_entities_document_id ON entities(document_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_document_metadata_document_id ON document_metadata(document_id);
CREATE INDEX IF NOT EXISTS idx_document_metadata_key ON document_metadata(key);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

-- Grant permissions to the opendiscourse user
GRANT ALL PRIVILEGES ON TABLE documents TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE document_metadata TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE entities TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE entity_relationships TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE search_queries TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE search_results TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE users TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE user_preferences TO opendiscourse;
GRANT ALL PRIVILEGES ON TABLE user_sessions TO opendiscourse;

-- Grant permissions on sequences
GRANT ALL PRIVILEGES ON SEQUENCE documents_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE document_metadata_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE entities_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE entity_relationships_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE search_queries_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE search_results_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE users_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE user_preferences_id_seq TO opendiscourse;
GRANT ALL PRIVILEGES ON SEQUENCE user_sessions_id_seq TO opendiscourse;