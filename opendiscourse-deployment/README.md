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
