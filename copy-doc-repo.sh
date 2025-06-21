#!/bin/bash
set -euo pipefail
# DEPRECATED: This script was used for a one-off server setup and should
# not be run in modern deployments.

# Copy files to master node
scp doc-repo-api.py doc-repo-api.service requirements.txt cbwinslow@172.28.158.179:/home/cbwinslow/

# Run setup script on master node
ssh cbwinslow@172.28.158.179 "bash -c '
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib
    python3 -m pip install -r requirements.txt
    sudo -u postgres psql -c \"CREATE DATABASE doc_repo;\"
    sudo -u postgres psql -c \"CREATE USER doc_user WITH PASSWORD \'doc_password123\';\"
    sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE doc_repo TO doc_user;\"
    sudo -u postgres psql doc_repo << EOF
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB
    );
    
    CREATE TABLE IF NOT EXISTS document_versions (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id),
        version_number INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB
    );
    
    CREATE INDEX idx_documents_title ON documents(title);
    CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);
    CREATE INDEX idx_document_versions_document_id ON document_versions(document_id);
    EOF
    
    sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'\" /etc/postgresql/*/main/postgresql.conf
    echo \"host all all 0.0.0.0/0 md5\" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
    sudo systemctl restart postgresql
    
    sudo mkdir -p /var/lib/doc-repo
    sudo chown postgres:postgres /var/lib/doc-repo
    sudo chmod 700 /var/lib/doc-repo
    
    sudo cp doc-repo-api.py /usr/local/bin/
    sudo cp doc-repo-api.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable doc-repo-api
    sudo systemctl start doc-repo-api
    '
