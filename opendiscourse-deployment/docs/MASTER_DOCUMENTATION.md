# OpenDiscourse Queue System - Complete Documentation

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Installation Guide](#3-installation-guide)
4. [Configuration](#4-configuration)
5. [Usage Guide](#5-usage-guide)
6. [Monitoring & Management](#6-monitoring--management)
7. [API Reference](#7-api-reference)
8. [Troubleshooting](#8-troubleshooting)
9. [Development Guide](#9-development-guide)
10. [Security](#10-security)
11. [Maintenance](#11-maintenance)

---

## 1. System Overview

### Purpose

The OpenDiscourse Queue System is a comprehensive, production-ready data ingestion platform designed to automate the collection, processing, and storage of US government legislative data from three primary sources:

- **OpenStates**: State legislative data
- **Congress.gov**: Federal legislative data  
- **GovInfo.gov**: Federal bill documents and actions

### Key Features

- **Automated Scheduling**: Cron-like scheduling for daily data ingestion
- **Queue Management**: Redis-based job queue with priority handling
- **Error Recovery**: Automatic retry mechanisms with exponential backoff
- **Monitoring**: Real-time health checks and performance monitoring
- **Scalability**: Multi-worker processing with configurable concurrency
- **Security**: Production-grade security with service isolation
- **Reliability**: Comprehensive logging and audit trails

### Data Sources

| Source | API | Data Types | Update Frequency |
|--------|-----|------------|------------------|
| OpenStates | REST API | Jurisdictions, People, Bills, Organizations, Events | Daily |
| Congress.gov | REST API | Members, Bills, Committees, Hearings, Records, Register, Laws, Nominations, Treaties | Daily |
| GovInfo.gov | XML/Bulk API | Bill Documents, Actions, Cosponsors | Daily |

### System Requirements

- **Operating System**: Ubuntu 20.04+ or CentOS 8+
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB available disk space
- **Network**: Internet access for API calls
- **Database**: PostgreSQL 12+ with existing database at 172.28.82.205:5432
- **Redis**: Version 6+ (installed automatically)

---

## 2. Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              Server-Side Queue System                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Job Scheduler │  │  Queue Workers  │  │  Monitoring     │ │
│  │   (Background)  │──▶│  (Background)   │──▶│  (Background)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                   │                   │           │
│           ▼                   ▼                   ▼           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Redis Queue Management                       │ │
│  │          (Job Queue & Processing)                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  OpenStates API │    │ Congress.gov API│    │  GovInfo.gov    │
│   (State Data)  │    │ (Federal Data)  │    │ (Bill Documents)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database                            │
│          (172.28.82.205:5432/opendiscourse)                 │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 2.1 Queue Manager (`queue_workers.py`)
- **Purpose**: Manages job submission and worker processes
- **Features**:
  - Job submission for all data sources
  - Worker lifecycle management
  - Job status tracking and retrieval
  - Queue statistics and monitoring

#### 2.2 Job Scheduler (`job_scheduler.py`)
- **Purpose**: Automated scheduling of ingestion jobs
- **Features**:
  - Cron-like scheduling configuration
  - Multiple frequency support (hourly, daily, weekly)
  - Job history tracking
  - Alert system integration

#### 2.3 Monitoring System (`monitoring_system.py`)
- **Purpose**: Health checks and performance monitoring
- **Features**:
  - Database connectivity checks
  - Redis connectivity checks
  - Queue health monitoring
  - System resource monitoring
  - Data freshness monitoring
  - API health checks

#### 2.4 Data Ingestion Scripts

**OpenStates Ingestion (`ingest_openstates_data.py`)**
- Jurisdictions, people, bills, organizations, events
- Rate-limited API calls with retry logic
- Batch processing with configurable sizes
- Open Civic Data (OCD) schema compliance

**Congress.gov Ingestion (`ingest_congressgov_data.py`)**
- Federal members, bills, committees, hearings, records
- Congressional Record, Federal Register, Laws, Nominations, Treaties
- Congress number support (current: 119)
- Rich metadata extraction

**GovInfo Ingestion (`ingest_govinfo_data.py`)**
- Bill documents and action history
- XML parsing with error handling
- Bulk data processing support
- Document classification and mapping

### Database Schema

#### 2.5 Database Tables

**OpenStates Tables**
- `opencivicdata_jurisdiction`: State/territory data
- `opencivicdata_person`: Legislator information
- `opencivicdata_bill`: State bills and resolutions
- `opencivicdata_organization`: Committees and organizations
- `opencivicdata_event`: Legislative events and meetings

**Federal Tables**
- `federal_members`: Congressional members
- `federal_bills`: Federal legislation
- `federal_committees`: Congressional committees
- `federal_hearings`: Committee hearings
- `federal_records`: Congressional Record entries
- `federal_register_docs`: Federal Register documents
- `federal_laws`: Enacted laws
- `federal_nominations`: Presidential nominations
- `federal_treaties`: International treaties

**GovInfo Tables**
- `govinfo_bill`: Bill document metadata
- `govinfo_bill_action`: Bill action history
- `govinfo_bill_cosponsor`: Bill cosponsor information

**Monitoring Tables**
- `master_ingestion_status`: Overall ingestion tracking
- `federal_member_ingestion_status`: Member ingestion specific tracking

### Configuration Structure

#### 2.6 Configuration Files

```
/opt/opendiscourse/queue-system/
├── config/
│   └── database_config.env          # Database connection settings
├── scripts/
│   ├── start_services.sh            # Service management
│   ├── stop_services.sh             # Service management
│   ├── status.sh                    # Status checking
│   └── health_check.sh              # Health monitoring
├── logs/                            # Application logs
├── queue_config.py                  # Queue configuration
├── queue_workers.py                 # Worker management
├── job_scheduler.py                 # Job scheduling
├── monitoring_system.py             # System monitoring
└── .env                             # Environment variables
```

---

## 3. Installation Guide

### Pre-Installation Checklist

- [ ] Server with Ubuntu 20.04+ or CentOS 8+
- [ ] Root or sudo access
- [ ] Internet connectivity
- [ ] PostgreSQL database accessible at 172.28.82.205:5432
- [ ] API keys for external services (see API Requirements below)

### API Requirements

#### 3.1 Required API Keys

**OpenStates API Key**
- URL: https://openstates.org/accounts/register/
- Type: REST API
- Usage: State legislative data ingestion
- Rate Limits: 1000 requests per day (free tier)

**Congress.gov API Key**
- URL: https://api.congress.gov/sign-up/
- Type: REST API
- Usage: Federal legislative data ingestion
- Rate Limits: 5000 requests per hour

**GovInfo API Key**
- URL: https://api.govinfo.gov/docs/
- Type: REST API
- Usage: Federal bill documents and actions
- Rate Limits: 1000 requests per hour

### Installation Methods

#### 3.1 Quick Installation (Recommended)

1. **Upload Package to Server**
   ```bash
   # Using SCP
   scp opendiscourse-queue-system-v1.0.tar.gz user@server:/tmp/
   
   # Using SFTP
   # Upload via SFTP client to /tmp/ directory
   ```

2. **Extract and Install**
   ```bash
   # SSH to server
   ssh user@server
   
   # Extract package
   cd /tmp
   tar -xzf opendiscourse-queue-system-v1.0.tar.gz
   cd opendiscourse-deployment
   
   # Run installation script
   sudo bash install_server.sh
   ```

3. **Configure API Keys**
   ```bash
   sudo nano /etc/opendiscourse/queue.env
   ```

   Update the following lines:
   ```bash
   OPENSTATES_API_KEY=your_actual_openstates_api_key
   CONGRESS_API_KEY=your_actual_congress_api_key
   GOVINFO_API_KEY=your_actual_govinfo_api_key
   ```

4. **Start Services**
   ```bash
   sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler
   sudo systemctl enable opendiscourse-queue-manager opendiscourse-job-scheduler
   ```

5. **Verify Installation**
   ```bash
   sudo /opt/opendiscourse/queue-system/scripts/health_check.sh
   ```

#### 3.2 Manual Installation

For development or custom installations:

1. **Install System Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv redis-server postgresql-client
   sudo apt install -y build-essential libpq-dev python3-dev curl wget git htop
   ```

2. **Setup Python Environment**
   ```bash
   sudo useradd --system --shell /bin/bash --home /opt/opendiscourse/queue-system --create-home opendiscourse
   sudo -u opendiscourse python3 -m venv /opt/opendiscourse/queue-system/venv
   sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip install --upgrade pip
   ```

3. **Install Application**
   ```bash
   sudo mkdir -p /opt/opendiscourse/queue-system
   sudo mkdir -p /var/log/opendiscourse
   sudo mkdir -p /etc/opendiscourse
   
   # Copy application files (from extracted package)
   sudo cp *.py /opt/opendiscourse/queue-system/
   sudo cp *.service /etc/systemd/system/
   sudo cp requirements-queue.txt /opt/opendiscourse/queue-system/
   sudo cp database_config.env /opt/opendiscourse/queue-system/config/
   
   # Set ownership
   sudo chown -R opendiscourse:opendiscourse /opt/opendiscourse/queue-system
   sudo chown -R opendiscourse:opendiscourse /var/log/opendiscourse
   sudo chown -R opendiscourse:opendiscourse /etc/opendiscourse
   ```

4. **Install Python Dependencies**
   ```bash
   sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip install -r /opt/opendiscourse/queue-system/requirements-queue.txt
   ```

5. **Configure Environment**
   ```bash
   sudo -u opendiscourse nano /etc/opendiscourse/queue.env
   ```

6. **Setup Systemd Services**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable opendiscourse-queue-manager opendiscourse-job-scheduler
   ```

#### 3.3 Docker Installation (Alternative)

For containerized deployment:

```bash
# Build image
docker build -t opendiscourse-queue .

# Run with environment variables
docker run -d \
  --name opendiscourse-queue \
  --restart unless-stopped \
  -e DB_HOST=172.28.82.205 \
  -e DB_PORT=5432 \
  -e DB_NAME=opendiscourse \
  -e DB_USER=opendiscourse \
  -e DB_PASSWORD=opendiscourse123 \
  -e OPENSTATES_API_KEY=your_key \
  -e CONGRESS_API_KEY=your_key \
  -e GOVINFO_API_KEY=your_key \
  -p 5000:5000 \
  opendiscourse-queue
```

### Post-Installation Verification

#### 3.4 Health Check Commands

```bash
# Check service status
sudo systemctl status opendiscourse-queue-manager
sudo systemctl status opendiscourse-job-scheduler
sudo systemctl status redis-server

# Run comprehensive health check
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh

# Check logs
sudo tail -f /var/log/opendiscourse/queue.log

# Test database connectivity
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
import psycopg2
conn = psycopg2.connect('postgresql://opendiscourse:opendiscourse123@172.28.82.205:5432/opendiscourse')
print('Database connection: SUCCESS')
conn.close()"

# Test Redis connectivity
redis-cli ping
```

#### 3.5 Common Installation Issues

**Issue**: Redis service fails to start
```bash
# Solution
sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server
```

**Issue**: Database connection fails
```bash
# Solution: Check network connectivity
telnet 172.28.82.205 5432
# If fails, check firewall rules and database permissions
```

**Issue**: Python dependencies fail to install
```bash
# Solution
sudo apt update
sudo apt install -y python3-dev build-essential
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip install --upgrade pip setuptools wheel
```

**Issue**: Permission denied errors
```bash
# Solution: Fix ownership
sudo chown -R opendiscourse:opendiscourse /opt/opendiscourse/queue-system
sudo chown -R opendiscourse:opendiscourse /var/log/opendiscourse
sudo chown -R opendiscourse:opendiscourse /etc/opendiscourse
```

---

## 4. Configuration

### Configuration Overview

The OpenDiscourse Queue System uses multiple configuration files for different aspects of system operation:

- Environment variables for API keys and sensitive data
- Database configuration for connection settings
- Queue configuration for system behavior
- Service configuration for systemd integration

### 4.1 Environment Configuration

**Location**: `/etc/opendiscourse/queue.env`

```bash
# OpenDiscourse Queue System Configuration
# ========================================

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
REDIS_PASSWORD=

# API Keys (REQUIRED - Update with your actual keys)
OPENSTATES_API_KEY=your_openstates_api_key_here
CONGRESS_API_KEY=your_congress_api_key_here
GOVINFO_API_KEY=your_govinfo_api_key_here

# Alert Configuration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
EMAIL_ALERT_TO=admin@yourdomain.com
EMAIL_ALERT_FROM=noreply@opendiscourse.org

# SMTP Configuration (for email alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/opendiscourse/queue.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=30

# Performance Configuration
WORKER_CONCURRENCY=2
INGESTION_BATCH_SIZE=100
RATE_LIMIT_DELAY=1.0
MAX_RETRIES=3
RETRY_DELAY=300

# Data Retention (days)
DATA_RETENTION_DAYS=90
CLEANUP_INTERVAL_DAYS=7

# Monitoring Thresholds
CPU_USAGE_THRESHOLD=80
MEMORY_USAGE_THRESHOLD=80
DISK_USAGE_THRESHOLD=85
JOB_FAILURE_RATE_THRESHOLD=10
JOB_DURATION_THRESHOLD_HOURS=2

# Security Settings
API_KEY_ENCRYPTION=true
ENABLE_AUDIT_LOGGING=true
AUDIT_LOG_RETENTION_DAYS=365

# Development Settings (set to false in production)
DEBUG_MODE=false
VERBOSE_LOGGING=false
ENABLE_PROFILING=false
```

### 4.2 Database Configuration

**Location**: `/opt/opendiscourse/queue-system/config/database_config.env`

```bash
# Database Connection Configuration
# Used by individual ingestion scripts

DB_HOST=172.28.82.205
DB_PORT=5432
DB_NAME=opendiscourse
DB_USER=opendiscourse
DB_PASSWORD=opendiscourse123

# Connection Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# SSL Configuration (if required)
DB_SSL_MODE=require
DB_SSL_CERT=/path/to/client-cert.pem
DB_SSL_KEY=/path/to/client-key.pem
DB_SSL_CA=/path/to/ca-cert.pem
```

### 4.3 Queue Configuration

**Location**: `/opt/opendiscourse/queue-system/queue_config.py`

Key configuration sections:

#### Queue Names and Settings
```python
# Queue Names
QUEUE_DEFAULT = 'default'
QUEUE_OPENSTATES = 'openstates'
QUEUE_CONGRESS = 'congress'
QUEUE_GOVINFO = 'govinfo'
QUEUE_MONITORING = 'monitoring'

# Worker Configuration
WORKER_CONFIG = {
    'default_worker_timeout': 3600,      # 1 hour
    'ingestion_worker_timeout': 7200,    # 2 hours
    'monitoring_worker_timeout': 300,    # 5 minutes
    'max_retries': 3,
    'retry_delay': 300,                  # 5 minutes
    'result_ttl': 86400,                 # 24 hours
    'failure_ttl': 604800,               # 7 days
}
```

#### Scheduling Configuration
```python
SCHEDULE_CONFIG = {
    'openstates': {
        'frequency': 'daily',
        'time': '02:00',  # 2 AM UTC
        'priority': 1,
    },
    'congress': {
        'frequency': 'daily', 
        'time': '03:00',  # 3 AM UTC
        'priority': 2,
    },
    'govinfo': {
        'frequency': 'daily',
        'time': '04:00',  # 4 AM UTC
        'priority': 3,
    },
    'health_check': {
        'frequency': 'hourly',
        'time': 'every_hour',
        'priority': 0,
    },
    'cleanup': {
        'frequency': 'weekly',
        'time': 'Sunday 01:00',  # Sunday 1 AM UTC
        'priority': 4,
    }
}
```

#### Alert Thresholds
```python
ALERT_THRESHOLDS = {
    'job_failure_rate': 0.1,        # 10% failure rate
    'job_duration_threshold': 7200,  # 2 hours
    'queue_age_threshold': 3600,     # 1 hour
    'consecutive_failures': 3,
    'memory_usage_threshold': 80,    # 80%
    'cpu_usage_threshold': 80,       # 80%
}
```

### 4.4 Systemd Service Configuration

#### Queue Manager Service
**Location**: `/etc/systemd/system/opendiscourse-queue-manager.service`

```ini
[Unit]
Description=OpenDiscourse Queue Manager
After=network.target redis.service postgresql.service
Wants=redis.service postgresql.service

[Service]
Type=simple
User=opendiscourse
Group=opendiscourse
WorkingDirectory=/opt/opendiscourse/queue-system
Environment=PYTHONPATH=/opt/opendiscourse/queue-system
EnvironmentFile=/opt/opendiscourse/queue-system/.env
ExecStart=/opt/opendiscourse/venv/bin/python queue_workers.py start --workers 2
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/opendiscourse/queue-system/logs

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

#### Job Scheduler Service
**Location**: `/etc/systemd/system/opendiscourse-job-scheduler.service`

```ini
[Unit]
Description=OpenDiscourse Job Scheduler
After=network.target redis.service postgresql.service
Wants=redis.service postgresql.service

[Service]
Type=simple
User=opendiscourse
Group=opendiscourse
WorkingDirectory=/opt/opendiscourse/queue-system
Environment=PYTHONPATH=/opt/opendiscourse/queue-system
EnvironmentFile=/opt/opendiscourse/queue-system/.env
ExecStart=/opt/opendiscourse/venv/bin/python job_scheduler.py start
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/opendiscourse/queue-system/logs

[Install]
WantedBy=multi-user.target
```

### 4.5 Web Dashboard Configuration (Optional)

If enabled during installation, the web dashboard uses Flask configuration:

```python
# Dashboard configuration
DASHBOARD_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'secret_key': 'your-secret-key-here',
    'refresh_interval': 30,  # seconds
}
```

### 4.6 Log Rotation Configuration

**Location**: `/etc/logrotate.d/opendiscourse`

```bash
/var/log/opendiscourse/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    sharedscripts
    postrotate
        systemctl reload opendiscourse-queue-manager || true
        systemctl reload opendiscourse-job-scheduler || true
    endscript
}
```

### 4.7 Firewall Configuration

For server security, configure firewall rules:

```bash
# Allow SSH (port 22)
sudo ufw allow 22/tcp

# Allow web dashboard (port 5000) - if enabled
sudo ufw allow 5000/tcp

# Allow Redis (port 6379) - localhost only
sudo ufw allow from 127.0.0.1 to any port 6379

# Deny all other incoming traffic
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

### 4.8 Configuration Validation

#### Configuration Validation Script

Create `/opt/opendiscourse/queue-system/scripts/validate_config.sh`:

```bash
#!/bin/bash

echo "=== OpenDiscourse Queue System Configuration Validation ==="

# Check environment file
if [ ! -f "/etc/opendiscourse/queue.env" ]; then
    echo "❌ Environment file missing: /etc/opendiscourse/queue.env"
    exit 1
fi

# Source environment file
source /etc/opendiscourse/queue.env

# Validate API keys
if [ "$OPENSTATES_API_KEY" = "your_openstates_api_key_here" ]; then
    echo "⚠️  Warning: OpenStates API key not configured"
fi

if [ "$CONGRESS_API_KEY" = "your_congress_api_key_here" ]; then
    echo "⚠️  Warning: Congress.gov API key not configured"
fi

if [ "$GOVINFO_API_KEY" = "your_govinfo_api_key_here" ]; then
    echo "⚠️  Warning: GovInfo API key not configured"
fi

# Test database connectivity
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='$DB_HOST',
        port='$DB_PORT',
        database='$DB_NAME',
        user='$DB_USER',
        password='$DB_PASSWORD'
    )
    print('✅ Database connection: SUCCESS')
    conn.close()
except Exception as e:
    print('❌ Database connection: FAILED -', e)
    exit(1)
"

# Test Redis connectivity
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis connection: SUCCESS"
else
    echo "❌ Redis connection: FAILED"
    exit(1
fi

# Check service files
for service in opendiscourse-queue-manager opendiscourse-job-scheduler; do
    if systemctl list-unit-files | grep -q "$service"; then
        echo "✅ Service configured: $service"
    else
        echo "❌ Service missing: $service"
    fi
done

echo "Configuration validation completed."
```

Run validation:
```bash
sudo /opt/opendiscourse/queue-system/scripts/validate_config.sh
```

---

## 5. Usage Guide

### 5.1 Basic Usage

#### Starting Services

```bash
# Start all services
sudo /opt/opendiscourse/queue-system/scripts/start_services.sh

# Or manually
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# Enable for automatic startup
sudo systemctl enable opendiscourse-queue-manager opendiscourse-job-scheduler
```

#### Stopping Services

```bash
# Stop all services
sudo /opt/opendiscourse/queue-system/scripts/stop_services.sh

# Or manually
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler
```

#### Checking Status

```bash
# Quick status check
sudo /opt/opendiscourse/queue-system/scripts/status.sh

# Detailed status
sudo systemctl status opendiscourse-queue-manager
sudo systemctl status opendiscourse-job-scheduler
sudo systemctl status redis-server

# Queue statistics
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py status
```

#### Health Checks

```bash
# Comprehensive health check
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh

# Run monitoring checks
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/monitoring_system.py check

# Generate health report
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/monitoring_system.py report
```

### 5.2 Job Management

#### Submitting Jobs Manually

```bash
# Submit OpenStates ingestion job
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type openstates

# Submit Congress.gov ingestion job
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type congress

# Submit GovInfo ingestion job
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type govinfo

# Submit monitoring job
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type monitoring

# Submit job in sample mode (for testing)
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/queue_workers.py submit --job-type openstates --sample-mode
```

#### Scheduling Jobs

```bash
# Trigger immediate job via scheduler
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/job_scheduler.py trigger --job-type openstates

# Check scheduler status and upcoming jobs
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/job_scheduler.py status
```

#### Monitoring Job Execution

```bash
# View real-time logs
sudo tail -f /var/log/opendiscourse/queue.log

# View specific ingestion logs
sudo tail -f /opt/opendiscourse/queue-system/openstates_ingestion.log
sudo tail -f /opt/opendiscourse/queue-system/congressgov_ingestion.log
sudo tail -f /opt/opendiscourse/queue-system/govinfo_ingestion.log

# View worker logs
sudo tail -f /opt/opendiscourse/queue-system/queue_workers.log

# View scheduler logs
sudo tail -f /opt/opendiscourse/queue-system/job_scheduler.log
```

### 5.3 Data Ingestion Usage

#### OpenStates Ingestion

```bash
# Full ingestion (all data types)
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_openstates_data.py --mode full

# Sample ingestion (limited data for testing)
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_openstates_data.py --mode sample

# Specific data type
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_openstates_data.py --data-type people --jurisdiction ca

# Specific jurisdiction
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_openstates_data.py --mode full --jurisdiction ny

# With custom API key
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_openstates_data.py --api-key your_key_here
```

**OpenStates Data Types:**
- `jurisdictions`: State and territory information
- `people`: Legislators and officials
- `bills`: State legislation
- `organizations`: Committees and caucuses
- `events`: Legislative events and meetings

#### Congress.gov Ingestion

```bash
# Full ingestion (all data types for Congress 119)
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_congressgov_data.py --mode full --congress 119

# Sample ingestion (limited data for testing)
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_congressgov_data.py --mode sample --congress 119

# Specific data type
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_congressgov_data.py --data-type members --congress 119

# Different Congress number
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_congressgov_data.py --mode full --congress 118
```

**Congress.gov Data Types:**
- `members`: Congressional members
- `bills`: Federal legislation
- `committees`: Congressional committees
- `hearings`: Committee hearings
- `records`: Congressional Record entries
- `register`: Federal Register documents
- `laws`: Enacted laws
- `nominations`: Presidential nominations
- `treaties`: International treaties

#### GovInfo Ingestion

```bash
# Sample ingestion (download and process sample files)
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_govinfo_data.py --mode sample

# Process existing XML directory
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_govinfo_data.py --mode full --xml-dir /path/to/xml/files

# Specific data type with Congress number
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_govinfo_data.py --data-type bills --congress 119

# Download sample files with custom limit
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/ingest_govinfo_data.py --mode sample --limit 10
```

**GovInfo Data Types:**
- `bills`: Bill document metadata
- `bill_actions`: Bill action history

### 5.4 Web Dashboard Usage

If enabled during installation, access the web dashboard at `http://your-server-ip:5000`

#### Dashboard Features

- **Real-time Status**: Service health and queue statistics
- **Job History**: Recent job executions and results
- **System Metrics**: CPU, memory, and disk usage
- **Data Freshness**: Last update times for each data source
- **Queue Monitoring**: Job counts, success rates, and failure analysis

#### Dashboard Management

```bash
# Access dashboard locally
curl http://localhost:5000

# Check dashboard logs
sudo tail -f /var/log/opendiscourse/dashboard.log

# Restart dashboard service
sudo systemctl restart opendiscourse-dashboard
```

### 5.5 Database Query Examples

#### Check Ingestion Status

```sql
-- Overall ingestion status
SELECT 
    source_name,
    data_type,
    status,
    success_records,
    started_at,
    updated_at
FROM master_ingestion_status
ORDER BY updated_at DESC
LIMIT 20;

-- Failed jobs in last 24 hours
SELECT 
    source_name,
    error_message,
    started_at
FROM master_ingestion_status
WHERE status = 'failed' 
  AND started_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY started_at DESC;

-- Data freshness by source
SELECT 
    source_name,
    MAX(updated_at) as last_update,
    COUNT(*) as total_runs
FROM master_ingestion_status
GROUP BY source_name;
```

#### Check Federal Data

```sql
-- Federal members by party
SELECT 
    party,
    COUNT(*) as member_count,
    string_agg(full_name, ', ' ORDER BY full_name) as members
FROM federal_members
WHERE current_member = true
GROUP BY party;

-- Recent federal bills
SELECT 
    bill_id,
    bill_type,
    congress,
    title,
    latest_action_date,
    is_law
FROM federal_bills
WHERE introduced_date > CURRENT_DATE - INTERVAL '30 days'
ORDER BY introduced_date DESC
LIMIT 10;

-- Committee membership
SELECT 
    fc.name as committee_name,
    fc.chamber,
    fm.full_name as member_name,
    fm.party,
    fm.state
FROM federal_committees fc
JOIN federal_members fm ON fc.committee_id = ANY(fm.committees::text[])
WHERE fc.chamber = 'house'
ORDER BY fc.name, fm.last_name;
```

#### Check State Data

```sql
-- Jurisdictions by classification
SELECT 
    classification,
    COUNT(*) as jurisdiction_count,
    string_agg(name, ', ' ORDER BY name) as jurisdictions
FROM opencivicdata_jurisdiction
GROUP BY classification;

-- Recent state bills
SELECT 
    identifier,
    title,
    latest_action_date,
    jurisdiction_id
FROM opencivicdata_bill
WHERE latest_action_date > CURRENT_DATE - INTERVAL '7 days'
ORDER BY latest_action_date DESC
LIMIT 20;
```

### 5.6 Log Analysis

#### Common Log Analysis Commands

```bash
# Find errors in last hour
sudo grep "ERROR" /var/log/opendiscourse/queue.log | tail -20

# Count successful vs failed jobs today
sudo grep "job completed successfully" /var/log/opendiscourse/queue.log | wc -l
sudo grep "job failed" /var/log/opendiscourse/queue.log | wc -l

# Monitor specific ingestion
sudo grep "OpenStates" /var/log/opendiscourse/queue.log | tail -10

# Check API call rates
sudo grep "API request" /var/log/opendiscourse/queue.log | tail -20

# Find slow jobs
sudo awk '/Started job/ { start = $1 " " $2 } /Completed job/ { print start, $1 " " $2, $0 }' /var/log/opendiscourse/queue.log | head -20
```

#### Log Rotation and Archiving

```bash
# Manually rotate logs
sudo logrotate -f /etc/logrotate.d/opendiscourse

# Archive old logs
sudo tar -czf /var/log/opendiscourse/archive-$(date +%Y%m%d).tar.gz /var/log/opendiscourse/*.log.* 

# Clean old archived logs
sudo find /var/log/opendiscourse -name "archive-*.tar.gz" -mtime +30 -delete
```

### 5.7 Performance Tuning

#### Worker Configuration

```bash
# Increase worker count for high-volume processing
sudo systemctl edit opendiscourse-queue-manager

# Add to override file:
[Service]
ExecStart=/opt/opendiscourse/venv/bin/python queue_workers.py start --workers 4
```

#### Database Optimization

```sql
-- Add indexes for better query performance
CREATE INDEX CONCURRENTLY idx_master_ingestion_status_source_updated 
ON master_ingestion_status(source_name, updated_at);

CREATE INDEX CONCURRENTLY idx_federal_bills_congress_updated 
ON federal_bills(congress, updated_at);

CREATE INDEX CONCURRENTLY idx_opencivicdata_bill_jurisdiction_updated 
ON opencivicdata_bill(jurisdiction_id, updated_at);
```

#### Redis Optimization

```bash
# Redis configuration
sudo nano /etc/redis/redis.conf

# Key settings to optimize:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 5.8 Backup and Recovery

#### Database Backup

```bash
# Create database backup
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
import psycopg2
import os
from datetime import datetime

# Create backup filename
backup_file = '/tmp/opendiscourse_backup_{}.sql'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

# Create backup
os.system('pg_dump -h 172.28.82.205 -U opendiscourse -d opendiscourse > {}'.format(backup_file))
print('Backup created: {}'.format(backup_file))
"

# Restore from backup
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse < /path/to/backup.sql
```

#### Configuration Backup

```bash
# Backup configuration
sudo tar -czf /tmp/opendiscourse_config_backup_$(date +%Y%m%d).tar.gz \
  /etc/opendiscourse/queue.env \
  /opt/opendiscourse/queue-system/config/

# Backup custom scripts
sudo tar -czf /tmp/opendiscourse_scripts_backup_$(date +%Y%m%d).tar.gz \
  /opt/opendiscourse/queue-system/scripts/
```

#### Redis Backup

```bash
# Create Redis backup
redis-cli BGSAVE

# Copy Redis dump file
sudo cp /var/lib/redis/dump.rdb /tmp/redis_backup_$(date +%Y%m%d).rdb

# Restore Redis backup
sudo cp /tmp/redis_backup_YYYYMMDD.rdb /var/lib/redis/dump.rdb
sudo systemctl restart redis-server
```

---

## 6. Monitoring & Management

### 6.1 Health Monitoring

#### Automated Health Checks

The system performs comprehensive health checks automatically:

**Frequency**: Hourly (configurable)
**Coverage**:
- Database connectivity and performance
- Redis connectivity and memory usage
- Queue health and job statistics
- System resource utilization
- External API availability
- Data freshness verification

#### Manual Health Checks

```bash
# Quick health assessment
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh

# Detailed health check with JSON output
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/monitoring_system.py check

# Generate formatted health report
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/monitoring_system.py report

# Continuous monitoring (every 5 minutes)
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python \
  /opt/opendiscourse/queue-system/monitoring_system.py check --continuous --interval 300
```

#### Health Check Components

**Database Health**
- Connection test with timing
- Query performance measurement
- Recent ingestion activity review
- Table size and growth monitoring

**Redis Health**
- Connectivity and response time
- Memory usage and configuration
- Client connections and operations
- Persistence and replication status

**Queue Health**
- Job queue lengths and aging
- Success/failure rate analysis
- Worker process status
- Stuck job detection

**System Resources**
- CPU usage and load average
- Memory usage and swap
- Disk usage and I/O
- Network connectivity

**External APIs**
- OpenStates API availability
- Congress.gov API availability
- GovInfo API availability
- Response time monitoring

### 6.2 Performance Monitoring

#### Key Performance Indicators (KPIs)

**System Performance**
- CPU usage < 80%
- Memory usage < 80%
- Disk usage < 85%
- Network latency < 100ms to APIs

**Data Ingestion Performance**
- Job success rate > 90%
- Average job duration < 2 hours
- Queue wait time < 1 hour
- API response time < 5 seconds

**Data Quality**
- Data freshness < 24 hours
- API error rate < 5%
- Database connection success > 99%
- Data completeness > 95%

#### Performance Monitoring Script

Create `/opt/opendiscourse/queue-system/scripts/performance_monitor.sh`:

```bash
#!/bin/bash

echo "=== OpenDiscourse Performance Monitor ==="
echo "Timestamp: $(date)"
echo

# System performance
echo "System Resources:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $5}')"
echo

# Database performance
echo "Database Performance:"
python3 -c "
import psycopg2
import time
try:
    start = time.time()
    conn = psycopg2.connect('postgresql://opendiscourse:opendiscourse123@172.28.82.205:5432/opendiscourse')
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    response_time = (time.time() - start) * 1000
    print(f'Connection time: {response_time:.1f}ms')
    
    # Recent job statistics
    cursor.execute('''
        SELECT source_name, status, COUNT(*) 
        FROM master_ingestion_status 
        WHERE updated_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
        GROUP BY source_name, status
    ''')
    stats = cursor.fetchall()
    print('Last 24h job statistics:')
    for source, status, count in stats:
        print(f'  {source} - {status}: {count}')
    
    conn.close()
except Exception as e:
    print(f'Database error: {e}')
"
echo

# Redis performance
echo "Redis Performance:"
echo "Memory usage: $(redis-cli info memory | grep used_memory_human | cut -d':' -f2 | tr -d '\r')"
echo "Connected clients: $(redis-cli info clients | grep connected_clients | cut -d':' -f2 | tr -d '\r')"
echo "Operations per second: $(redis-cli info stats | grep instantaneous_ops_per_sec | cut -d':' -f2 | tr -d '\r')"
echo

# Queue performance
echo "Queue Performance:"
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/queue_workers.py status

echo
echo "=== End Performance Report ==="
```

#### Performance Dashboard

For real-time performance monitoring, access the web dashboard:

```bash
# Access dashboard
curl http://localhost:5000 | head -20

# Monitor specific metrics
watch -n 30 'sudo /opt/opendiscourse/queue-system/scripts/performance_monitor.sh'
```

### 6.3 Alerting System

#### Alert Configuration

Alerts are configured in `/etc/opendiscourse/queue.env`:

```bash
# Slack alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Email alerts
EMAIL_ALERT_TO=admin@yourdomain.com
EMAIL_ALERT_FROM=noreply@opendiscourse.org

# SMTP configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### Alert Types

**Critical Alerts**
- Database connectivity loss
- Redis service failure
- Queue system failure
- High failure rate (>25%)

**Warning Alerts**
- API connectivity issues
- High resource usage (>80%)
- Slow job performance
- Data staleness (>48 hours)

**Info Alerts**
- Service restarts
- Configuration changes
- Successful completions (optional)

#### Alert Testing

```bash
# Test Slack alert
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
import os
import requests
webhook = os.getenv('SLACK_WEBHOOK_URL')
if webhook:
    payload = {
        'text': 'Test alert from OpenDiscourse Queue System',
        'attachments': [{
            'color': 'good',
            'text': 'This is a test notification',
            'footer': 'OpenDiscourse Monitor',
            'ts': int(time.time())
        }]
    }
    requests.post(webhook, json=payload)
    print('Slack test alert sent')
else:
    print('Slack webhook not configured')
"

# Test email alert
echo "Test email alert" | mail -s "OpenDiscourse Test Alert" admin@yourdomain.com
```

### 6.4 Log Management

#### Log Files

| File | Purpose | Location |
|------|---------|----------|
| `queue.log` | Main application log | `/var/log/opendiscourse/` |
| `queue_workers.log` | Worker process log | `/opt/opendiscourse/queue-system/` |
| `job_scheduler.log` | Scheduler log | `/opt/opendiscourse/queue-system/` |
| `monitoring.log` | Monitoring system log | `/opt/opendiscourse/queue-system/` |
| `openstates_ingestion.log` | OpenStates ingestion log | `/opt/opendiscourse/queue-system/` |
| `congressgov_ingestion.log` | Congress.gov ingestion log | `/opt/opendiscourse/queue-system/` |
| `govinfo_ingestion.log` | GovInfo ingestion log | `/opt/opendiscourse/queue-system/` |
| `dashboard.log` | Web dashboard log | `/var/log/opendiscourse/` |

#### Log Analysis

```bash
# Real-time log monitoring
sudo tail -f /var/log/opendiscourse/queue.log

# Error analysis
sudo grep -i error /var/log/opendiscourse/queue.log | tail -20

# Job completion analysis
sudo grep "completed successfully" /var/log/opendiscourse/queue.log | tail -10

# Performance analysis
sudo awk '/Started job/ {start[$1" "$2] = $0} /Completed job/ {if(start[$1" "$2]) print start[$1" "$2], $0}' /var/log/opendiscourse/queue.log | head -10

# API call analysis
sudo grep "API request" /var/log/opendiscourse/queue.log | awk '{print $8, $10}' | sort | uniq -c | sort -nr | head -10
```

#### Log Rotation

Automatic log rotation is configured via `/etc/logrotate.d/opendiscourse`:

```bash
# Manual log rotation
sudo logrotate -f /etc/logrotate.d/opendiscourse

# Check logrotate status
sudo logrotate -d /etc/logrotate.d/opendiscourse

# Archive old logs
sudo find /var/log/opendiscourse -name "*.log.*" -mtime +7 -exec tar czf /tmp/old_logs_{} \; -delete
```

### 6.5 Service Management

#### Service Control Commands

```bash
# Start services
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# Stop services
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler

# Restart services
sudo systemctl restart opendiscourse-queue-manager opendiscourse-job-scheduler

# Reload configuration
sudo systemctl reload opendiscourse-queue-manager opendiscourse-job-scheduler

# Enable automatic startup
sudo systemctl enable opendiscourse-queue-manager opendiscourse-job-scheduler

# Disable automatic startup
sudo systemctl disable opendiscourse-queue-manager opendiscourse-job-scheduler

# Check service status
sudo systemctl status opendiscourse-queue-manager
sudo systemctl status opendiscourse-job-scheduler

# View service logs
sudo journalctl -u opendiscourse-queue-manager -f
sudo journalctl -u opendiscourse-job-scheduler -f
```

#### Service Dependencies

```
network.target
    ├── redis.service (dependency)
    ├── postgresql.service (dependency)
    ├── opendiscourse-queue-manager.service
    └── opendiscourse-job-scheduler.service
```

#### Service Health Monitoring

```bash
# Check service dependencies
sudo systemctl list-dependencies opendiscourse-queue-manager

# Check service configuration
sudo systemctl cat opendiscourse-queue-manager

# Validate service file
sudo systemd-analyze verify opendiscourse-queue-manager.service

# Check service resource limits
sudo systemctl show opendiscourse-queue-manager | grep -E "LimitNOFILE|LimitNPROC|Memory"
```

### 6.6 Maintenance Operations

#### Regular Maintenance Tasks

**Daily**
- Monitor job success rates
- Check disk space usage
- Review error logs
- Verify API connectivity

**Weekly**
- Clean up old log files
- Review performance metrics
- Check database growth
- Test backup procedures

**Monthly**
- Update system packages
- Review and optimize database indexes
- Analyze long-term performance trends
- Review security configurations

#### Maintenance Script

Create `/opt/opendiscourse/queue-system/scripts/maintenance.sh`:

```bash
#!/bin/bash

echo "=== OpenDiscourse Maintenance Script ==="
echo "Started: $(date)"

# Log cleanup (keep last 30 days)
echo "Cleaning up old log files..."
find /var/log/opendiscourse -name "*.log.*" -mtime +30 -delete 2>/dev/null || true
find /opt/opendiscourse/queue-system -name "*.log.*" -mtime +30 -delete 2>/dev/null || true

# Database cleanup
echo "Cleaning up old ingestion records..."
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
import psycopg2
import os
from datetime import datetime, timedelta

conn = psycopg2.connect('postgresql://opendiscourse:opendiscourse123@172.28.82.205:5432/opendiscourse')
cursor = conn.cursor()

# Clean up old ingestion status (keep 90 days)
cutoff_date = datetime.now() - timedelta(days=90)
cursor.execute('DELETE FROM master_ingestion_status WHERE updated_at < %s', (cutoff_date,))
deleted_count = cursor.rowcount

conn.commit()
cursor.close()
conn.close()

print(f'Deleted {deleted_count} old ingestion records')
"

# Redis memory optimization
echo "Optimizing Redis memory..."
redis-cli MEMORY PURGE

# Check disk space
echo "Disk space usage:"
df -h / | tail -1

# Check service status
echo "Service status:"
for service in opendiscourse-queue-manager opendiscourse-job-scheduler redis-server; do
    status=$(systemctl is-active $service 2>/dev/null || echo "inactive")
    echo "  $service: $status"
done

# Performance health check
echo "Running health check..."
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh

echo "=== Maintenance completed: $(date) ==="
```

#### Scheduled Maintenance

Add to crontab for automated maintenance:

```bash
# Edit crontab
sudo crontab -e

# Add daily maintenance (runs at 2 AM)
0 2 * * * /opt/opendiscourse/queue-system/scripts/maintenance.sh >> /var/log/opendiscourse/maintenance.log 2>&1

# Add weekly performance report (runs Sunday at 1 AM)
0 1 * * 0 /opt/opendiscourse/queue-system/scripts/performance_monitor.sh > /var/log/opendiscourse/weekly_report.log 2>&1
```

---

This documentation continues in the next sections covering API Reference, Troubleshooting, Development Guide, Security, and Maintenance. Each section provides comprehensive coverage of its topic area with practical examples and troubleshooting guidance.

Would you like me to continue with the remaining sections (7-11) to complete this comprehensive documentation?