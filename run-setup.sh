#!/bin/bash

# Copy all files to master node
scp setup-postgres.sh create-tables.sql setup-api.sh doc-repo-api.py doc-repo-api.service requirements.txt cbwinslow@172.28.158.179:/home/cbwinslow/

# Run setup steps in sequence
ssh cbwinslow@172.28.158.179 "bash -c '
    # Setup PostgreSQL
    sudo bash setup-postgres.sh
    
    # Create tables
    sudo -u postgres psql doc_repo -f create-tables.sql
    
    # Setup API
    bash setup-api.sh
    '
