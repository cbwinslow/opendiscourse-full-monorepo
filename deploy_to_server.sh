#!/bin/bash
# Create deployment package for server transfer

echo "Creating OpenDiscourse Queue System deployment package..."

# Create deployment directory
mkdir -p opendiscourse-deployment
cd opendiscourse-deployment

# Copy all required files
cp ../queue_config.py .
cp ../queue_workers.py .
cp ../job_scheduler.py .
cp ../monitoring_system.py .
cp ../ingest_openstates_data.py .
cp ../ingest_congressgov_data.py .
cp ../ingest_govinfo_data.py .
cp ../run_all_ingestions.py .
cp ../setup_database.py .
cp ../consolidated_database_migration.sql .
cp ../requirements-queue.txt .
cp ../database_config.env .
cp ../opendiscourse-queue-manager.service .
cp ../opendiscourse-job-scheduler.service .
cp ../install_server.sh .

# Create README for deployment
cat > README.md << 'EOF'
# OpenDiscourse Queue System - Server Deployment

## Quick Installation

1. Upload this folder to your server
2. Run: `sudo bash install_server.sh`
3. Configure API keys: `sudo nano /etc/opendiscourse/queue.env`
4. Start services: `sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler`
5. Check status: `sudo /opt/opendiscourse/queue-system/scripts/health_check.sh`

## Required Files

- install_server.sh - Main installation script
- queue_config.py - Queue configuration
- queue_workers.py - Queue workers and job management
- job_scheduler.py - Scheduled job execution
- monitoring_system.py - Health monitoring
- ingest_*.py - Data ingestion scripts
- setup_database.py - Database setup
- *.service - Systemd service files

## Next Steps After Installation

1. Get API keys:
   - OpenStates: https://openstates.org/accounts/register/
   - Congress.gov: https://api.congress.gov/sign-up/
   - GovInfo: https://api.govinfo.gov/docs/

2. Configure API keys in /etc/opendiscourse/queue.env

3. Start the services and verify everything works
EOF

# Make installation script executable
chmod +x install_server.sh

# Create tarball for easy transfer
tar -czf opendiscourse-queue-system-v1.0.tar.gz .
cd ..

echo "Deployment package created: opendiscourse-deployment/opendiscourse-queue-system-v1.0.tar.gz"
echo ""
echo "Next steps:"
echo "1. Upload opendiscourse-deployment/opendiscourse-queue-system-v1.0.tar.gz to your server"
echo "2. Extract: tar -xzf opendiscourse-queue-system-v1.0.tar.gz"
echo "3. cd opendiscourse-queue-system"
echo "4. Run: sudo bash install_server.sh"