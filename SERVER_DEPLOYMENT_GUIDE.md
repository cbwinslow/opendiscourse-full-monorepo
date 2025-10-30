# OpenDiscourse Queue System - Server Deployment Guide

## Overview

This guide provides complete instructions for deploying the OpenDiscourse Data Ingestion Queue System on a production server. The system uses Redis for job queuing, PostgreSQL for data storage, and systemd for process management.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Job Scheduler │    │  Queue Workers  │    │  Monitoring     │
│   (Background)  │───▶│  (Background)   │───▶│  (Background)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Redis Queue                              │
│                    (Job Management)                             │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  OpenStates API │    │ Congress.gov API│    │  GovInfo.gov    │
│   (Port 443)    │    │   (Port 443)    │    │   (Port 443)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                          │
│              (172.28.82.205:5432/opendiscourse)                │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: Minimum 50GB free space
- **Network**: Internet access for API calls
- **Privileges**: sudo access for installation

### External Dependencies
- **Database**: PostgreSQL server at `172.28.82.205:5432`
- **API Keys**: 
  - OpenStates API key
  - Congress.gov API key  
  - GovInfo API key (optional)

## Installation

### Step 1: Upload Files to Server

Upload all queue system files to your server:

```bash
# Create deployment package
tar -czf opendiscourse-queue.tar.gz \
  queue_config.py \
  queue_workers.py \
  job_scheduler.py \
  monitoring_system.py \
  ingest_openstates_data.py \
  ingest_congressgov_data.py \
  ingest_govinfo_data.py \
  run_all_ingestions.py \
  setup_database.py \
  consolidated_database_migration.sql \
  requirements-queue.txt \
  database_config.env \
  opendiscourse-queue-manager.service \
  opendiscourse-job-scheduler.service \
  install_server.sh

# Upload to server
scp opendiscourse-queue.tar.gz user@your-server:/tmp/

# On server:
cd /tmp
tar -xzf opendiscourse-queue.tar.gz
```

### Step 2: Run Installation Script

```bash
# Make installation script executable
chmod +x install_server.sh

# Run as root
sudo ./install_server.sh
```

The installation script will:
- ✅ Install system dependencies (Python, Redis, PostgreSQL client)
- ✅ Create service user and directory structure  
- ✅ Set up Python virtual environment
- ✅ Configure systemd services
- ✅ Set up logging and monitoring
- ✅ Create management scripts
- ✅ Initialize database schema

### Step 3: Configure API Keys

```bash
# Edit configuration
sudo nano /etc/opendiscourse/queue.env

# Update these values:
OPENSTATES_API_KEY=your_actual_openstates_api_key
CONGRESS_API_KEY=your_actual_congress_api_key
GOVINFO_API_KEY=your_actual_govinfo_api_key
```

**Getting API Keys:**
- **OpenStates**: https://openstates.org/accounts/register/
- **Congress.gov**: https://api.congress.gov/sign-up/
- **GovInfo**: https://api.govinfo.gov/docs/

### Step 4: Start Services

```bash
# Start all services
sudo /opt/opendiscourse/queue-system/scripts/start_services.sh

# Check status
sudo /opt/opendiscourse/queue-system/scripts/status.sh

# Run health check
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh
```

## Service Management

### System Commands

```bash
# Start services
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# Stop services
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler

# Enable auto-start on boot
sudo systemctl enable opendiscourse-queue-manager opendiscourse-job-scheduler

# Check status
sudo systemctl status opendiscourse-queue-manager opendiscourse-job-scheduler

# View logs
sudo journalctl -u opendiscourse-queue-manager -f
sudo journalctl -u opendiscourse-job-scheduler -f
```

### Management Scripts

```bash
# Available management scripts
/opt/opendiscourse/queue-system/scripts/
├── start_services.sh    # Start all services
├── stop_services.sh     # Stop all services
├── status.sh           # Check service status
└── health_check.sh     # Run health check
```

## Job Management

### Submit Jobs Manually

```bash
# Submit OpenStates ingestion
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type openstates

# Submit Congress.gov ingestion  
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type congress

# Submit GovInfo ingestion
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type govinfo

# Submit monitoring check
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type monitoring
```

### Monitor Queue Status

```bash
# Check queue statistics
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py status

# Check specific job
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/monitoring_system.py check

# View recent jobs in database
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "
SELECT source_name, status, updated_at, success_records 
FROM master_ingestion_status 
ORDER BY updated_at DESC 
LIMIT 10;"
```

## Configuration

### Environment Variables

Key configuration in `/etc/opendiscourse/queue.env`:

```bash
# Database Configuration
DB_HOST=172.28.82.205
DB_PORT=5432
DB_NAME=opendiscourse
DB_USER=opendiscourse
DB_PASSWORD=opendiscourse123

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Keys
OPENSTATES_API_KEY=your_key
CONGRESS_API_KEY=your_key
GOVINFO_API_KEY=your_key

# Scheduling (24-hour format)
SCHEDULE_OPENSTATES=02:00
SCHEDULE_CONGRESS=03:00
SCHEDULE_GOVINFO=04:00
```

### Log Configuration

```bash
# Application logs
/var/log/opendiscourse/queue.log
/var/log/opendiscourse/monitor.log
/var/log/opendiscourse/scheduler.log

# System logs
sudo journalctl -u opendiscourse-queue-manager
sudo journalctl -u opendiscourse-job-scheduler

# Redis logs
sudo journalctl -u redis-server

# Log rotation (30 days retention)
/etc/logrotate.d/opendiscourse
```

## Monitoring

### Health Checks

The system automatically runs health checks:
- **Database connectivity**
- **Redis connectivity** 
- **Queue health and job status**
- **System resource usage**
- **External API availability**

### Web Dashboard (Optional)

If enabled during installation:
- **Access**: `http://your-server-ip:5000`
- **Status**: Real-time queue monitoring
- **Management**: Service control interface

### Alert Configuration

Set up alerts in `/etc/opendiscourse/queue.env`:

```bash
# Slack webhook for alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Email alerts
EMAIL_ALERT_TO=admin@yourdomain.com
EMAIL_ALERT_FROM=noreply@opendiscourse.org

# SMTP settings (if using email)
SMTP_SERVER=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
```

## Backup and Recovery

### Database Backup

```bash
# Manual backup
pg_dump -h 172.28.82.205 -U opendiscourse opendiscourse > backup_$(date +%Y%m%d).sql

# Automated backup script
cat > /usr/local/bin/backup_opendiscourse.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/opendiscourse"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -h 172.28.82.205 -U opendiscourse opendiscourse \
  | gzip > $BACKUP_DIR/opendiscourse_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup_opendiscourse.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup_opendiscourse.sh" | sudo crontab -
```

### Redis Backup

```bash
# Redis persistence is automatic, but you can force a save:
redis-cli BGSAVE

# Copy RDB file to backup location
sudo cp /var/lib/redis/dump.rdb /backup/opendiscourse/redis_$(date +%Y%m%d).rdb
```

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
sudo journalctl -u opendiscourse-queue-manager --no-pager -l
sudo journalctl -u opendiscourse-job-scheduler --no-pager -l

# Check permissions
ls -la /opt/opendiscourse/queue-system/
sudo chown -R opendiscourse:opendiscourse /opt/opendiscourse/queue-system/
```

**Database connection fails:**
```bash
# Test connection
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse

# Check firewall
sudo ufw status
sudo ufw allow 5432
```

**Redis connection fails:**
```bash
# Test Redis
redis-cli ping

# Restart Redis
sudo systemctl restart redis-server

# Check Redis configuration
sudo nano /etc/redis/redis.conf
```

**Jobs failing:**
```bash
# Check job status
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py status

# Run monitoring check
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/monitoring_system.py check
```

### Performance Tuning

**Redis Memory:**
```bash
# Increase Redis memory limit
sudo nano /etc/redis/redis.conf

# Set maxmemory (e.g., 2GB)
maxmemory 2gb
maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

**Worker Concurrency:**
```bash
# Edit systemd service to increase workers
sudo systemctl edit opendiscourse-queue-manager

[Service]
ExecStart=/opt/opendiscourse/venv/bin/python /opt/opendiscourse/queue-system/queue_workers.py start --workers 4

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart opendiscourse-queue-manager
```

## Security

### Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (adjust port as needed)
sudo ufw allow 22/tcp

# Allow web dashboard (if enabled)
sudo ufw allow 5000/tcp

# Allow Redis (local only)
sudo ufw allow from 127.0.0.1 to any port 6379

# Block PostgreSQL (external access not needed)
sudo ufw deny 5432/tcp

# Check status
sudo ufw status verbose
```

### File Permissions

```bash
# Secure configuration files
sudo chmod 600 /etc/opendiscourse/queue.env
sudo chmod 700 /opt/opendiscourse/queue-system/
sudo chmod 755 /opt/opendiscourse/queue-system/*.py

# Secure log files
sudo chmod 640 /var/log/opendiscourse/*.log
```

## Maintenance

### Regular Tasks

**Weekly:**
- Review job success rates
- Clean up old log files
- Check disk space usage
- Review monitoring alerts

**Monthly:**
- Update system packages
- Review and rotate backups
- Check API key validity
- Performance optimization review

**Quarterly:**
- Security audit
- Dependency updates
- Capacity planning review
- Disaster recovery testing

### Update Process

```bash
# Backup current installation
sudo tar -czf /backup/opendiscourse_queue_$(date +%Y%m%d).tar.gz \
  /opt/opendiscourse/queue-system /etc/opendiscourse

# Stop services
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler

# Update files
# (Copy new files to /opt/opendiscourse/queue-system/)

# Update dependencies
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip install -r \
  /opt/opendiscourse/queue-system/requirements-queue.txt

# Restart services
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# Verify functionality
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh
```

## Production Checklist

- [ ] Server meets minimum requirements
- [ ] Database is accessible and configured
- [ ] API keys are obtained and configured
- [ ] Systemd services are installed and enabled
- [ ] Firewall is configured appropriately
- [ ] Monitoring and alerting is set up
- [ ] Backup strategy is implemented
- [ ] Log rotation is configured
- [ ] Security hardening is applied
- [ ] Documentation is complete
- [ ] Team training is completed

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u opendiscourse-queue-manager -f`
2. Run health check: `sudo /opt/opendiscourse/queue-system/scripts/health_check.sh`
3. Review monitoring dashboard
4. Check GitHub issues for known problems

## System Information

- **Version**: 1.0.0
- **Last Updated**: October 30, 2025
- **Python**: 3.8+
- **Redis**: 6.0+
- **PostgreSQL**: 13+
- **Platform**: Linux (Ubuntu/CentOS)

---

**Note**: This system is designed for production use with automatic scheduling, monitoring, and alerting. Ensure all prerequisites are met before deployment.