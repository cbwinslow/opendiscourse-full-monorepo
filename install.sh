#!/bin/bash
set -euo pipefail

# One-click install script for local development
# Installs Python and Node dependencies, sets up Postgres, and starts services

# Install Python packages
python3 -m pip install -r requirements.txt

# Install Node packages if package.json exists
if [ -f package.json ]; then
  npm install
fi

# Initialize database (PostgreSQL)
./setup-postgres.sh

# Start API and supporting services via Docker Compose
./run-dev.sh
