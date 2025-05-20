#!/bin/bash

# Install PostgreSQL
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Create document repository database and user
sudo -u postgres psql -c "CREATE DATABASE doc_repo;"
sudo -u postgres psql -c "CREATE USER doc_user WITH PASSWORD 'doc_password123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE doc_repo TO doc_user;"

# Enable remote connections
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'" /etc/postgresql/*/main/postgresql.conf
echo "host all all 0.0.0.0/0 md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
sudo systemctl restart postgresql

# Create document storage directory
sudo mkdir -p /var/lib/doc-repo
sudo chown postgres:postgres /var/lib/doc-repo
sudo chmod 700 /var/lib/doc-repo
