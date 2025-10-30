# OpenDiscourse Queue System - Troubleshooting Guide

## Table of Contents

1. [Common Issues](#1-common-issues)
2. [Service Problems](#2-service-problems)
3. [Database Issues](#3-database-issues)
4. [API Integration Problems](#4-api-integration-problems)
5. [Performance Issues](#5-performance-issues)
6. [Network and Connectivity](#6-network-and-connectivity)
7. [Log Analysis](#7-log-analysis)
8. [Recovery Procedures](#8-recovery-procedures)
9. [Emergency Procedures](#9-emergency-procedures)
10. [Getting Help](#10-getting-help)

---

## 1. Common Issues

### 1.1 Installation Problems

#### Issue: "Permission denied" during installation
**Symptoms:**
- Script fails with "Permission denied" errors
- Cannot create directories or files
- Service installation fails

**Diagnosis:**
```bash
# Check if running as root
whoami

# Check directory permissions
ls -la /opt/opendiscourse/
ls -la /etc/opendiscourse/

# Check user and group ownership
id opendiscourse
```

**Solutions:**
```bash
# Ensure running with sudo
sudo bash install_server.sh

# Fix ownership after installation
sudo chown -R opendiscourse:opendiscourse /opt/opendiscourse/queue-system
sudo chown -R opendiscourse:opendiscourse /var/log/opendiscourse
sudo chown -R opendiscourse:opendiscourse /etc/opendiscourse

# Fix permissions
sudo chmod 755 /opt/opendiscourse/queue-system
sudo chmod 600 /opt/opendiscourse/queue-system/config/*.env
```

#### Issue: Python dependencies fail to install
**Symptoms:**
- pip install fails with compilation errors
- Missing Python headers or build tools
- Virtual environment creation fails

**Diagnosis:**
```bash
# Check Python version
python3 --version

# Check available disk space
df -h

# Check internet connectivity
ping pypi.org
```

**Solutions:**
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-dev build-essential libpq-dev

# Upgrade pip and setuptools
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip install --upgrade pip setuptools wheel

# Clear pip cache and retry
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip cache purge
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip install -r requirements-queue.txt
```

### 1.2 Configuration Problems

#### Issue: Environment variables not loaded
**Symptoms:**
- Jobs fail with "API key not found" errors
- Database connection fails with wrong credentials
- Configuration values appear as default/empty

**Diagnosis:**
```bash
# Check environment file exists
ls -la /etc/opendiscourse/queue.env

# Check file permissions
cat /etc/opendiscourse/queue.env | head -10

# Verify environment is loaded
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
import os
print('DB_HOST:', os.getenv('DB_HOST'))
print('OPENSTATES_API_KEY:', os.getenv('OPENSTATES_API_KEY'))
"
```

**Solutions:**
```bash
# Fix environment file permissions
sudo chmod 600 /etc/opendiscourse/queue.env
sudo chown opendiscourse:opendiscourse /etc/opendiscourse/queue.env

# Check for syntax errors in environment file
sudo -u opendiscourse bash -c "source /etc/opendiscourse/queue.env && echo 'Environment loaded successfully'"

# Recreate environment file if corrupted
sudo cp /etc/opendiscourse/queue.env /etc/opendiscourse/queue.env.backup
sudo nano /etc/opendiscourse/queue.env  # Edit and save
```

#### Issue: API keys not working
**Symptoms:**
- Authentication failures from external APIs
- HTTP 401 or 403 errors in logs
- Jobs failing at API call stage

**Diagnosis:**
```bash
# Test API connectivity manually
curl -H "X-Api-Key: YOUR_OPENSTATES_KEY" https://openstates.org/api/v3/jurisdictions/

# Check API key format
echo $OPENSTATES_API_KEY | wc -c  # Should be > 10 characters

# Test Congress.gov API
curl -H "X-Api-Key: YOUR_CONGRESS_KEY" https://api.congress.gov/v3/member/
```

**Solutions:**
```bash
# Verify API key is correct
# Check with API provider dashboard

# Update environment file with correct key
sudo nano /etc/opendiscourse/queue.env

# Restart services to pick up new environment
sudo systemctl restart opendiscourse-queue-manager opendiscourse-job-scheduler

# Test with new key
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/ingest_openstates_data.py --mode sample
```

---

## 2. Service Problems

### 2.1 Services Won't Start

#### Issue: Queue manager service fails to start
**Symptoms:**
- `systemctl status opendiscourse-queue-manager` shows "failed"
- Service starts but immediately stops
- Error messages in journal logs

**Diagnosis:**
```bash
# Check service status
sudo systemctl status opendiscourse-queue-manager

# View detailed logs
sudo journalctl -u opendiscourse-queue-manager -f --no-pager

# Check Python path and dependencies
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "import sys; print('\\n'.join(sys.path))"
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip list"
```

**Solutions:**
```bash
# Fix virtual environment issues
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/pip install --force-reinstall -r /opt/opendiscourse/queue-system/requirements-queue.txt

# Check service file syntax
sudo systemd-analyze verify /etc/systemd/system/opendiscourse-queue-manager.service

# Test script manually
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/queue_workers.py status

# Restart daemon and service
sudo systemctl daemon-reload
sudo systemctl restart opendiscourse-queue-manager
```

#### Issue: Job scheduler service fails
**Symptoms:**
- Jobs not being scheduled automatically
- Scheduler service shows as failed or inactive
- No new jobs appearing in queue

**Diagnosis:**
```bash
# Check scheduler service
sudo systemctl status opendiscourse-job-scheduler

# Test scheduler manually
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/job_scheduler.py status

# Check schedule configuration
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
from job_scheduler import JobScheduler
scheduler = JobScheduler()
status = scheduler.get_status()
print('Scheduler running:', status['running'])
print('Next jobs:', status['next_runs'])
"
```

**Solutions:**
```bash
# Restart scheduler service
sudo systemctl restart opendiscourse-job-scheduler

# Check Redis connectivity
redis-cli ping

# Test with manual job submission
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/job_scheduler.py trigger --job-type openstates
```

### 2.2 Services Crashing

#### Issue: Services crash with memory errors
**Symptoms:**
- Out of memory errors in logs
- Services killed by OOM killer
- Frequent restarts

**Diagnosis:**
```bash
# Check system memory
free -h
cat /proc/meminfo

# Check service resource limits
sudo systemctl show opendiscourse-queue-manager | grep Memory

# Monitor memory usage during job execution
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/monitoring_system.py check
```

**Solutions:**
```bash
# Reduce worker concurrency
sudo systemctl edit opendiscourse-queue-manager
# Add: ExecStart=/opt/opendiscourse/venv/bin/python queue_workers.py start --workers 1

# Increase memory limits
sudo systemctl edit opendiscourse-queue-manager
# Add:
# [Service]
# MemoryMax=2G
# MemorySwapMax=0

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart opendiscourse-queue-manager
```

---

## 3. Database Issues

### 3.1 Connection Problems

#### Issue: Cannot connect to database
**Symptoms:**
- "Connection refused" or "Connection timeout" errors
- Database authentication failures
- Jobs failing with database errors

**Diagnosis:**
```bash
# Test network connectivity
telnet 172.28.82.205 5432

# Test database connection
psql -h 172.28.82.205 -p 5432 -U opendiscourse -d opendiscourse -c "SELECT 1;"

# Check database logs
# (Check with database administrator)
```

**Solutions:**
```bash
# Verify firewall rules
sudo ufw status
sudo iptables -L | grep 5432

# Test with different authentication method
psql -h 172.28.82.205 -p 5432 -U postgres -d opendiscourse

# Check environment variables
echo $DB_HOST $DB_PORT $DB_USER $DB_PASSWORD

# Fix environment configuration
sudo nano /etc/opendiscourse/queue.env
sudo systemctl restart opendiscourse-queue-manager opendiscourse-job-scheduler
```

#### Issue: Database schema mismatch
**Symptoms:**
- "relation does not exist" errors
- Column mismatch errors
- Foreign key constraint failures

**Diagnosis:**
```bash
# Check table existence
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "\dt"

# Check specific table structure
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "\d opencivicdata_jurisdiction"

# Check for missing tables
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
import psycopg2
conn = psycopg2.connect('postgresql://opendiscourse:opendiscourse123@172.28.82.205:5432/opendiscourse')
cursor = conn.cursor()
cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\")
tables = [row[0] for row in cursor.fetchall()]
print('Existing tables:', sorted(tables))
"
```

**Solutions:**
```bash
# Run database migration
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/setup_database.py

# Or manually run migration
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -f /opt/opendiscourse/queue-system/consolidated_database_migration.sql

# Check table structure matches expected schema
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python -c "
from queue_config import DATABASE_CONFIG
import psycopg2
conn = psycopg2.connect(**DATABASE_CONFIG)
# Verify critical tables exist
cursor = conn.cursor()
required_tables = ['master_ingestion_status', 'opencivicdata_jurisdiction', 'federal_members']
for table in required_tables:
    cursor.execute('SELECT COUNT(*) FROM ' + table)
    print(f'{table}: {cursor.fetchone()[0]} records')
"
```

### 3.2 Performance Issues

#### Issue: Slow database queries
**Symptoms:**
- Long job execution times
- Database connection timeouts
- High database CPU usage

**Diagnosis:**
```bash
# Check database performance
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Check table sizes
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**Solutions:**
```bash
# Add missing indexes
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_master_ingestion_status_source_updated 
ON master_ingestion_status(source_name, updated_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_federal_bills_congress_updated 
ON federal_bills(congress, updated_at);
"

# Analyze table statistics
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "ANALYZE;"

# Update configuration
sudo systemctl edit opendiscourse-queue-manager
# Add: Environment=DB_POOL_SIZE=5
```

---

## 4. API Integration Problems

### 4.1 OpenStates API Issues

#### Issue: OpenStates API rate limiting
**Symptoms:**
- HTTP 429 errors in logs
- Jobs failing with "rate limit exceeded"
- API calls timing out

**Diagnosis:**
```bash
# Check rate limit headers
curl -I -H "X-Api-Key: YOUR_KEY" https://openstates.org/api/v3/jurisdictions/

# Monitor API call frequency
grep "API request" /var/log/opendiscourse/queue.log | tail -20
```

**Solutions:**
```bash
# Reduce batch sizes
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/queue_workers.py submit --job-type openstates --batch-size 25

# Increase rate limiting delay
sudo nano /etc/opendiscourse/queue.env
# Add: RATE_LIMIT_DELAY=2.0

# Restart services
sudo systemctl restart opendiscourse-queue-manager opendiscourse-job-scheduler

# Implement exponential backoff
# (This requires code modification)
```

#### Issue: OpenStates data format changes
**Symptoms:**
- JSON parsing errors
- Missing fields in responses
- Schema validation failures

**Diagnosis:**
```bash
# Test API response format
curl -H "X-Api-Key: YOUR_KEY" https://openstates.org/api/v3/jurisdictions/ | jq .

# Check logs for parsing errors
sudo tail -f /opt/opendiscourse/queue-system/openstates_ingestion.log | grep ERROR
```

**Solutions:**
```bash
# Update to latest API version
# Check OpenStates API documentation

# Add error handling for missing fields
sudo nano /opt/opendiscourse/queue-system/ingest_openstates_data.py
# Add null checks in data mapping functions

# Run in debug mode to see full responses
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/ingest_openstates_data.py --mode sample --debug
```

### 4.2 Congress.gov API Issues

#### Issue: Congress.gov API authentication
**Symptoms:**
- HTTP 401 unauthorized errors
- API key rejected
- Authentication failures

**Diagnosis:**
```bash
# Test API key
curl -H "X-Api-Key: YOUR_KEY" https://api.congress.gov/v3/member/

# Check API key registration
# Visit https://api.congress.gov/sign-up/ to verify
```

**Solutions:**
```bash
# Register new API key if needed
# Generate new key at https://api.congress.gov/sign-up/

# Update environment
sudo nano /etc/opendiscourse/queue.env
# Update CONGRESS_API_KEY=your_new_key

# Test with new key
curl -H "X-Api-Key: your_new_key" https://api.congress.gov/v3/member/
```

#### Issue: Congress.gov data pagination
**Symptoms:**
- Incomplete data ingestion
- Missing recent records
- Pagination errors

**Diagnosis:**
```bash
# Check total record counts
curl -H "X-Api-Key: YOUR_KEY" "https://api.congress.gov/v3/member/?limit=1" | jq '.pagination.total-results'

# Monitor pagination in logs
sudo grep "pagination" /opt/opendiscourse/queue-system/congressgov_ingestion.log
```

**Solutions:**
```bash
# Increase offset limits
# This requires code modification to handle large offsets properly

# Check for rate limiting during pagination
sudo nano /opt/opendiscourse/queue-system/ingest_congressgov_data.py
# Add delays between pagination requests
```

### 4.3 GovInfo API Issues

#### Issue: GovInfo XML parsing errors
**Symptoms:**
- XML parsing failures
- Malformed document errors
- Data extraction problems

**Diagnosis:**
```bash
# Test XML file download
curl -o test.xml "https://www.govinfo.gov/content/pkg/BILLS-119hr1ih/xml/BILLS-119hr1ih.xml"

# Validate XML structure
xmllint --noout test.xml

# Check for character encoding issues
file test.xml
```

**Solutions:**
```bash
# Fix XML parsing with better error handling
sudo nano /opt/opendiscourse/queue-system/ingest_govinfo_data.py
# Add try-catch blocks around XML parsing

# Handle encoding issues
# Add encoding detection and conversion

# Skip malformed files and continue processing
```

---

## 5. Performance Issues

### 5.1 Slow Job Execution

#### Issue: Jobs taking too long to complete
**Symptoms:**
- Jobs running for hours instead of minutes
- Timeouts on long-running jobs
- System resources maxed out

**Diagnosis:**
```bash
# Monitor system resources during job execution
htop
iotop
netstat -i

# Check job execution times
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/queue_workers.py status

# Analyze job duration patterns
sudo awk '/Started job/ {start[$1" "$2] = $0} /Completed job/ {if(start[$1" "$2]) print start[$1" "$2], $0}' /var/log/opendiscourse/queue.log | head -10
```

**Solutions:**
```bash
# Reduce batch sizes
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/queue_workers.py submit --job-type openstates --batch-size 25

# Increase worker timeout
sudo nano /opt/opendiscourse/queue-system/queue_config.py
# Update WORKER_CONFIG['ingestion_worker_timeout'] = 14400  # 4 hours

# Run jobs during off-peak hours
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/job_scheduler.py trigger --job-type openstates --schedule-time "02:00"
```

### 5.2 Memory Issues

#### Issue: High memory usage
**Symptoms:**
- Out of memory errors
- System becoming unresponsive
- Services killed by OOM killer

**Diagnosis:**
```bash
# Monitor memory usage
free -h
ps aux --sort=-%mem | head -10

# Check for memory leaks
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/monitoring_system.py check
```

**Solutions:**
```bash
# Restart services to free memory
sudo systemctl restart opendiscourse-queue-manager opendiscourse-job-scheduler

# Reduce concurrent workers
sudo systemctl edit opendiscourse-queue-manager
# Change: --workers 1

# Add memory limits
sudo systemctl edit opendiscourse-queue-manager
# Add:
# [Service]
# MemoryMax=1G
# MemorySwapMax=0

# Implement garbage collection
# Add periodic memory cleanup in code
```

---

## 6. Network and Connectivity

### 6.1 Network Timeouts

#### Issue: API calls timing out
**Symptoms:**
- Connection timeout errors
- Slow API responses
- Network unreachable errors

**Diagnosis:**
```bash
# Test network connectivity
ping openstates.org
ping api.congress.gov
ping www.govinfo.gov

# Check DNS resolution
nslookup openstates.org
nslookup api.congress.gov

# Test SSL/TLS connectivity
openssl s_client -connect openstates.org:443
```

**Solutions:**
```bash
# Check firewall rules
sudo ufw status verbose

# Add firewall rules for API access
sudo ufw allow out to openstates.org port 443
sudo ufw allow out to api.congress.gov port 443
sudo ufw allow out to www.govinfo.gov port 443

# Increase timeout values
sudo nano /opt/opendiscourse/queue-system/ingest_openstates_data.py
# Update timeout values in requests calls

# Use different DNS servers
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
```

### 6.2 Firewall Issues

#### Issue: Firewall blocking connections
**Symptoms:**
- Connection refused errors
- Services unable to reach external APIs
- Database connection failures

**Diagnosis:**
```bash
# Check current firewall rules
sudo ufw status verbose
sudo iptables -L

# Test specific ports
nc -zv openstates.org 443
nc -zv api.congress.gov 443
nc -zv 172.28.82.205 5432
```

**Solutions:**
```bash
# Allow necessary outbound connections
sudo ufw allow out to any port 443
sudo ufw allow out to any port 80
sudo ufw allow out to 172.28.82.205 port 5432

# Allow Redis (localhost only)
sudo ufw allow from 127.0.0.1 to any port 6379

# Restart firewall
sudo ufw disable && sudo ufw enable
```

---

## 7. Log Analysis

### 7.1 Common Log Patterns

#### Error Patterns
```bash
# Find recent errors
sudo grep -i error /var/log/opendiscourse/queue.log | tail -20

# Find API errors
sudo grep -i "api.*error\|connection.*refused\|timeout" /var/log/opendiscourse/queue.log

# Find database errors
sudo grep -i "database\|psycopg2\|sql" /var/log/opendiscourse/queue.log
```

#### Performance Patterns
```bash
# Find slow operations
sudo grep -i "slow\|timeout\|took.*seconds" /var/log/opendiscourse/queue.log

# Find retry patterns
sudo grep -i "retry\|retrying" /var/log/opendiscourse/queue.log

# Find completed jobs
sudo grep -i "completed.*successfully" /var/log/opendiscourse/queue.log | tail -10
```

### 7.2 Log Analysis Scripts

#### Create log analysis script
```bash
# /opt/opendiscourse/queue-system/scripts/analyze_logs.sh
#!/bin/bash

echo "=== Log Analysis Report ==="
echo "Generated: $(date)"
echo

# Error summary
echo "Error Summary:"
ERROR_COUNT=$(sudo grep -i error /var/log/opendiscourse/queue.log | wc -l)
echo "Total errors: $ERROR_COUNT"

# Recent errors (last 24 hours)
echo -e "\nRecent Errors (last 24 hours):"
sudo grep "$(date +%Y-%m-%d)" /var/log/opendiscourse/queue.log | grep -i error | tail -5

# Job completion summary
echo -e "\nJob Completion (last 24 hours):"
COMPLETED=$(sudo grep "$(date +%Y-%m-%d)" /var/log/opendiscourse/queue.log | grep -i "completed.*successfully" | wc -l)
FAILED=$(sudo grep "$(date +%Y-%m-%d)" /var/log/opendiscourse/queue.log | grep -i "failed\|error" | wc -l)
echo "Completed: $COMPLETED"
echo "Failed: $FAILED"

# Performance summary
echo -e "\nSlow Operations:"
sudo grep -i "took.*[0-9][0-9][0-9]" /var/log/opendiscourse/queue.log | tail -5

# API issues
echo -e "\nAPI Issues:"
sudo grep -i "api.*error\|429\|401\|403" /var/log/opendiscourse/queue.log | tail -5
```

#### Database log analysis
```sql
-- Query to analyze job performance
SELECT 
    source_name,
    data_type,
    status,
    COUNT(*) as job_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_minutes,
    MIN(started_at) as first_run,
    MAX(started_at) as last_run
FROM master_ingestion_status 
WHERE started_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY source_name, data_type, status
ORDER BY avg_duration_minutes DESC;
```

---

## 8. Recovery Procedures

### 8.1 Data Recovery

#### Issue: Data corruption in database
**Symptoms:**
- Inconsistent data across tables
- Foreign key constraint violations
- Missing critical records

**Recovery Steps:**
```bash
# 1. Stop services to prevent further issues
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler

# 2. Create database backup
pg_dump -h 172.28.82.205 -U opendiscourse -d opendiscourse > /tmp/corruption_backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Analyze corruption scope
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "
-- Check for orphaned records
SELECT 'orphaned_bills' as issue_type, COUNT(*) as count 
FROM opencivicdata_bill b 
LEFT JOIN opencivicdata_jurisdiction j ON b.current_jurisdiction_id = j.id 
WHERE j.id IS NULL
UNION ALL
SELECT 'missing_ingestion_records' as issue_type, COUNT(*) as count
FROM opencivicdata_jurisdiction j
LEFT JOIN master_ingestion_status m ON j.id = m.source_name
WHERE m.source_name IS NULL;
"

# 4. Clean up corrupted data
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "
-- Remove orphaned records (adjust as needed)
DELETE FROM opencivicdata_bill 
WHERE current_jurisdiction_id NOT IN (SELECT id FROM opencivicdata_jurisdiction);

-- Rebuild ingestion status for missing records
INSERT INTO master_ingestion_status (source_name, data_type, status, updated_at)
SELECT DISTINCT id, 'jurisdiction', 'pending', CURRENT_TIMESTAMP
FROM opencivicdata_jurisdiction 
WHERE id NOT IN (SELECT source_name FROM master_ingestion_status WHERE data_type = 'jurisdiction');
"

# 5. Restart services
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# 6. Monitor for issues
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh
```

### 8.2 Queue Recovery

#### Issue: Redis data corruption
**Symptoms:**
- Queue system not responding
- Jobs stuck in queue
- Redis errors in logs

**Recovery Steps:**
```bash
# 1. Stop services
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler

# 2. Backup Redis data
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /tmp/redis_backup_$(date +%Y%m%d_%H%M%S).rdb

# 3. Clear Redis and restart
redis-cli FLUSHALL
sudo systemctl restart redis-server

# 4. Restart application services
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# 5. Resubmit stuck jobs
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/job_scheduler.py trigger --job-type openstates
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/job_scheduler.py trigger --job-type congress
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/job_scheduler.py trigger --job-type govinfo
```

### 8.3 Configuration Recovery

#### Issue: Corrupted configuration
**Symptoms:**
- Services failing to start
- Configuration syntax errors
- Missing environment variables

**Recovery Steps:**
```bash
# 1. Backup current (potentially corrupted) config
sudo cp /etc/opendiscourse/queue.env /etc/opendiscourse/queue.env.corrupted

# 2. Restore from backup if available
if [ -f "/etc/opendiscourse/queue.env.backup" ]; then
    sudo cp /etc/opendiscourse/queue.env.backup /etc/opendiscourse/queue.env
else
    # Recreate with defaults
    sudo bash /opt/opendiscourse/queue-system/install_server.sh --skip-dependencies
fi

# 3. Update API keys and critical settings
sudo nano /etc/opendiscourse/queue.env

# 4. Test configuration
sudo -u opendiscourse bash -c "source /etc/opendiscourse/queue.env && echo 'Config test passed'"

# 5. Restart services
sudo systemctl restart opendiscourse-queue-manager opendiscourse-job-scheduler
```

---

## 9. Emergency Procedures

### 9.1 System Recovery

#### Complete system failure
```bash
# 1. Immediate service restart
sudo systemctl restart redis-server
sudo systemctl restart opendiscourse-queue-manager
sudo systemctl restart opendiscourse-job-scheduler

# 2. Quick health check
sudo /opt/opendiscourse/queue-system/scripts/health_check.sh

# 3. If services still failing, restart from installation
cd /tmp/opendiscourse-deployment
sudo bash install_server.sh

# 4. Verify critical services
sudo systemctl status redis-server
sudo systemctl status postgresql
sudo netstat -tlnp | grep 6379  # Redis
sudo netstat -tlnp | grep 5432  # PostgreSQL
```

### 9.2 Data Emergency

#### Complete data loss
```bash
# 1. Stop all services
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler

# 2. Restore from database backup
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse < /path/to/latest_backup.sql

# 3. Restore Redis state if needed
redis-cli FLUSHALL
redis-cli --pipe < /path/to/redis_backup.rdb

# 4. Restart services
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# 5. Run fresh ingestion to verify data integrity
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/ingest_openstates_data.py --mode sample
```

### 9.3 API Key Emergency

#### All API keys compromised/expired
```bash
# 1. Stop services to prevent API errors
sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler

# 2. Generate new API keys:
# - OpenStates: https://openstates.org/accounts/register/
# - Congress.gov: https://api.congress.gov/sign-up/
# - GovInfo: Contact API support

# 3. Update environment
sudo nano /etc/opendiscourse/queue.env
# Update all API keys

# 4. Test new keys manually
curl -H "X-Api-Key: NEW_OPENSTATES_KEY" https://openstates.org/api/v3/jurisdictions/
curl -H "X-Api-Key: NEW_CONGRESS_KEY" https://api.congress.gov/v3/member/

# 5. Restart services
sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler

# 6. Run test ingestion
sudo -u opendiscourse /opt/opendiscourse/queue-system/venv/bin/python /opt/opendiscourse/queue-system/ingest_openstates_data.py --mode sample
```

---

## 10. Getting Help

### 10.1 Self-Diagnostic Tools

#### Create comprehensive diagnostic script
```bash
#!/bin/bash
# /opt/opendiscourse/queue-system/scripts/diagnostic_tool.sh

echo "=== OpenDiscourse Diagnostic Report ==="
echo "Generated: $(date)"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo

# System resources
echo "=== System Resources ==="
echo "CPU: $(nproc) cores"
echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $4}') free of $(df -h / | tail -1 | awk '{print $2}')"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
echo

# Service status
echo "=== Service Status ==="
for service in redis-server opendiscourse-queue-manager opendiscourse-job-scheduler; do
    status=$(systemctl is-active $service 2>/dev/null || echo "inactive")
    echo "$service: $status"
done
echo

# Network connectivity
echo "=== Network Connectivity ==="
echo "Redis: $(redis-cli ping 2>/dev/null && echo 'OK' || echo 'FAILED')"
echo "Database: $(timeout 5 psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c 'SELECT 1;' >/dev/null 2>&1 && echo 'OK' || echo 'FAILED')"
echo "OpenStates API: $(timeout 10 curl -s -o /dev/null -w '%{http_code}' https://openstates.org/api/v3/ >/dev/null 2>&1 && echo 'OK' || echo 'FAILED')"
echo "Congress API: $(timeout 10 curl -s -o /dev/null -w '%{http_code}' https://api.congress.gov/v3/ >/dev/null 2>&1 && echo 'OK' || echo 'FAILED')"
echo "GovInfo API: $(timeout 10 curl -s -o /dev/null -w '%{http_code}' https://www.govinfo.gov/ >/dev/null 2>&1 && echo 'OK' || echo 'FAILED')"
echo

# Configuration check
echo "=== Configuration Status ==="
if [ -f "/etc/opendiscourse/queue.env" ]; then
    echo "Environment file: EXISTS"
    echo "API keys configured: $(grep -c "API_KEY=.*[^_here]" /etc/opendiscourse/queue.env)/3"
else
    echo "Environment file: MISSING"
fi

# Recent job status
echo "=== Recent Jobs ==="
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -t -c "
SELECT 
    source_name,
    status,
    COUNT(*) as count,
    MAX(updated_at) as last_run
FROM master_ingestion_status 
WHERE updated_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY source_name, status
ORDER BY source_name, status;
" 2>/dev/null || echo "Database query failed"

echo
echo "=== End Diagnostic Report ==="
```

### 10.2 Support Contacts

#### Internal Support
- System Administrator: [admin@yourdomain.com]
- Database Administrator: [dba@yourdomain.com]
- Network Administrator: [netadmin@yourdomain.com]

#### External Support
- OpenStates API: https://github.com/openstates/api
- Congress.gov API: https://api.congress.gov/sign-up/
- GovInfo API: https://api.govinfo.gov/docs/
- Redis Support: https://redis.io/support
- PostgreSQL Support: https://www.postgresql.org/support/

### 10.3 Reporting Issues

#### Before reporting, collect:
1. Diagnostic report output
2. Recent log files (last 24 hours)
3. Service status information
4. Configuration file (sanitized)
5. Steps to reproduce the issue
6. Expected vs actual behavior

#### Template for issue reports:
```
ISSUE: [Brief description]
SEVERITY: [Critical/High/Medium/Low]
ENVIRONMENT: [Server details, OS version, etc.]

REPRODUCTION:
1. Step one
2. Step two
3. Error occurs

EXPECTED: What should happen
ACTUAL: What actually happened

LOGS: Relevant log entries
DIAGNOSTIC: Output from diagnostic tool

ATTEMPTS: What you've tried already
```

---

This troubleshooting guide covers the most common issues encountered with the OpenDiscourse Queue System. Keep this guide accessible and update it with new issues and solutions as they are discovered.