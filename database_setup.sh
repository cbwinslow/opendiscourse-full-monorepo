#!/bin/bash
# database_setup.sh - Script to set up PostgreSQL with pgvector extension

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if PostgreSQL is installed
    if ! command -v psql &> /dev/null; then
        print_error "PostgreSQL is not installed. Please install PostgreSQL first."
        exit 1
    fi
    
    # Check if pg_isready is available
    if ! command -v pg_isready &> /dev/null; then
        print_error "pg_isready is not available. Please ensure PostgreSQL client tools are installed."
        exit 1
    fi
    
    # Check if PostgreSQL is running
    if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        print_error "PostgreSQL is not running on localhost:5432"
        print_warning "Please start PostgreSQL service before running this script."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to check if pgvector is installed
check_pgvector() {
    print_status "Checking if pgvector extension is installed..."
    
    # Check if pgvector extension is available
    if sudo -u postgres psql -c "SELECT name FROM pg_available_extensions WHERE name = 'vector';" | grep -q "vector"; then
        print_success "pgvector extension is available"
        return 0
    else
        print_warning "pgvector extension is not installed"
        return 1
    fi
}

# Function to install pgvector (Ubuntu/Debian)
install_pgvector_debian() {
    print_status "Installing pgvector extension for PostgreSQL (Debian/Ubuntu)..."
    
    # Get PostgreSQL version
    PG_VERSION=$(psql --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    PG_MAJOR_VERSION=$(echo $PG_VERSION | cut -d. -f1)
    
    # Install pgvector
    if sudo apt-get update && sudo apt-get install -y postgresql-$PG_MAJOR_VERSION-pgvector; then
        print_success "pgvector installed successfully"
        return 0
    else
        print_error "Failed to install pgvector"
        return 1
    fi
}

# Function to install pgvector (using pip method as fallback)
install_pgvector_pip() {
    print_status "Installing pgvector using pip method..."
    
    # Try to install using pip
    if pip3 install pgvector; then
        print_success "pgvector installed via pip"
        return 0
    else
        print_error "Failed to install pgvector via pip"
        return 1
    fi
}

# Function to create database and user
create_database_user() {
    print_status "Creating database and user..."
    
    # Create user
    sudo -u postgres psql -c "CREATE USER opendiscourse WITH PASSWORD 'opendiscourse';" 2>/dev/null || true
    
    # Create database
    sudo -u postgres psql -c "CREATE DATABASE opendiscourse OWNER opendiscourse;" 2>/dev/null || true
    
    # Grant privileges
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE opendiscourse TO opendiscourse;" 2>/dev/null || true
    
    print_success "Database and user created (or already existed)"
}

# Function to enable pgvector extension
enable_pgvector_extension() {
    print_status "Enabling pgvector extension..."
    
    # Enable extension in the database
    sudo -u postgres psql -d opendiscourse -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true
    
    print_success "pgvector extension enabled"
}

# Function to create core tables
create_core_tables() {
    print_status "Creating core database tables..."
    
    # SQL to create tables
    SQL_COMMANDS="
    -- Create documents table
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
    
    -- Create a function to update the updated_at timestamp
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS \$\$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    \$\$ language 'plpgsql';
    
    -- Create triggers to automatically update the updated_at column
    CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    "
    
    # Execute the SQL commands
    sudo -u postgres psql -d opendiscourse -c "$SQL_COMMANDS" 2>/dev/null || true
    
    print_success "Core database tables created"
}

# Function to grant privileges to user
grant_privileges() {
    print_status "Granting database privileges to opendiscourse user..."
    
    # Grant privileges to the opendiscourse user
    GRANT_COMMANDS="
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
    "
    
    # Execute the grant commands
    sudo -u postgres psql -d opendiscourse -c "$GRANT_COMMANDS" 2>/dev/null || true
    
    print_success "Database privileges granted"
}

# Function to test database connection
test_connection() {
    print_status "Testing database connection..."
    
    # Test connection with the created user
    if PGPASSWORD=opendiscourse psql -h localhost -p 5432 -U opendiscourse -d opendiscourse -c "SELECT version();" >/dev/null 2>&1; then
        print_success "Database connection successful"
        return 0
    else
        print_error "Failed to connect to database with opendiscourse user"
        return 1
    fi
}

# Function to show connection details
show_connection_details() {
    echo ""
    echo "==========================================="
    echo "    Database Connection Details"
    echo "==========================================="
    echo ""
    echo "Host: localhost"
    echo "Port: 5432"
    echo "Database: opendiscourse"
    echo "Username: opendiscourse"
    echo "Password: opendiscourse"
    echo ""
    echo "Connection String: postgresql://opendiscourse:opendiscourse@localhost:5432/opendiscourse"
    echo ""
    print_warning "Important: Change the default password in production environments!"
    echo ""
}

# Main function
main() {
    print_status "Starting OpenDiscourse Database Setup"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Check if pgvector is installed
    if ! check_pgvector; then
        print_warning "Attempting to install pgvector..."
        if ! install_pgvector_debian; then
            print_warning "Trying alternative installation method..."
            if ! install_pgvector_pip; then
                print_error "Failed to install pgvector. Please install it manually."
                exit 1
            fi
        fi
    fi
    
    # Create database and user
    create_database_user
    
    # Enable pgvector extension
    enable_pgvector_extension
    
    # Create core tables
    create_core_tables
    
    # Grant privileges
    grant_privileges
    
    # Test connection
    if test_connection; then
        print_success "Database setup completed successfully!"
        show_connection_details
    else
        print_error "Database setup completed but connection test failed"
        exit 1
    fi
}

# Run main function
main