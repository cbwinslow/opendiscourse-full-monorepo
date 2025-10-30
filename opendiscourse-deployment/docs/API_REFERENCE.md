# OpenDiscourse Queue System - API Reference

## Table of Contents

1. [Queue Manager API](#1-queue-manager-api)
2. [Job Scheduler API](#2-job-scheduler-api)
3. [Monitoring API](#3-monitoring-api)
4. [Data Ingestion APIs](#4-data-ingestion-apis)
5. [Web Dashboard API](#5-web-dashboard-api)
6. [Configuration API](#6-configuration-api)
7. [Database Schema Reference](#7-database-schema-reference)

---

## 1. Queue Manager API

### 1.1 QueueManager Class

The `QueueManager` class handles job submission, status tracking, and queue management.

#### Methods

##### `submit_openstates_job(data_types, sample_mode, batch_size)`

Submit an OpenStates data ingestion job.

**Parameters:**
- `data_types` (list): Data types to ingest. Options: `['jurisdictions', 'people', 'bills', 'organizations', 'events']`. Default: all types.
- `sample_mode` (bool): Run in sample mode for testing. Default: `False`.
- `batch_size` (int): Number of records per batch. Default: `100`.

**Returns:**
- `str`: Job ID for tracking.

**Example:**
```python
queue_manager = QueueManager()
job_id = queue_manager.submit_openstates_job(
    data_types=['people', 'bills'],
    sample_mode=True,
    batch_size=50
)
print(f"Job submitted: {job_id}")
```

##### `submit_congress_job(data_types, congress, sample_mode, batch_size)`

Submit a Congress.gov data ingestion job.

**Parameters:**
- `data_types` (list): Data types to ingest. Options: `['members', 'bills', 'committees', 'hearings', 'records', 'register', 'laws', 'nominations', 'treaties']`.
- `congress` (int): Congress number (e.g., 119 for 2025-2027).
- `sample_mode` (bool): Run in sample mode. Default: `False`.
- `batch_size` (int): Records per batch. Default: `50`.

**Returns:**
- `str`: Job ID.

**Example:**
```python
job_id = queue_manager.submit_congress_job(
    data_types=['members', 'bills'],
    congress=119,
    sample_mode=False
)
```

##### `submit_govinfo_job(data_types, sample_mode)`

Submit a GovInfo data ingestion job.

**Parameters:**
- `data_types` (list): Data types. Options: `['bills', 'bill_actions']`.
- `sample_mode` (bool): Run in sample mode. Default: `False`.

**Returns:**
- `str`: Job ID.

##### `submit_monitoring_job()`

Submit a monitoring and health check job.

**Returns:**
- `str`: Job ID.

##### `get_job_status(job_id)`

Get detailed status for a specific job.

**Parameters:**
- `job_id` (str): Job identifier.

**Returns:**
- `dict`: Job status information including:
  - `id`: Job ID
  - `status`: Current status ('pending', 'running', 'completed', 'failed')
  - `created_at`: Creation timestamp
  - `started_at`: Start timestamp
  - `ended_at`: End timestamp
  - `result`: Job result data
  - `exc_info`: Exception information if failed
  - `failure_reason`: Reason for failure

**Example:**
```python
status = queue_manager.get_job_status('abc123-def456')
print(f"Job status: {status['status']}")
print(f"Result: {status['result']}")
```

##### `get_queue_stats()`

Get statistics for all queues.

**Returns:**
- `dict`: Queue statistics including:
  - `total_jobs`: Total jobs in queue
  - `started_jobs`: Jobs currently running
  - `finished_jobs`: Completed jobs
  - `failed_jobs`: Failed jobs
  - `deferred_jobs`: Deferred jobs
  - `scheduled_jobs`: Scheduled jobs

**Example:**
```python
stats = queue_manager.get_queue_stats()
for queue_name, queue_stats in stats.items():
    print(f"{queue_name}: {queue_stats['total_jobs']} jobs")
```

### 1.2 WorkerManager Class

Manages RQ workers for job processing.

#### Methods

##### `start_workers(num_workers_per_queue)`

Start workers for all queues.

**Parameters:**
- `num_workers_per_queue` (int): Number of workers per queue. Default: `1`.

##### `stop_workers()`

Stop all running workers.

##### `get_worker_stats()`

Get statistics for all workers.

**Returns:**
- `dict`: Worker statistics including:
  - `state`: Worker state ('idle', 'busy', 'suspended')
  - `queue`: Queue names
  - `current_job`: Current job ID
  - `failed_job_count`: Number of failed jobs
  - `succeeded_job_count`: Number of successful jobs
  - `total_working_time`: Total working time

---

## 2. Job Scheduler API

### 2.1 JobScheduler Class

Manages scheduled job execution with cron-like functionality.

#### Methods

##### `schedule_openstates_ingestion()`

Schedule OpenStates ingestion job with configured parameters.

##### `schedule_congress_ingestion()`

Schedule Congress.gov ingestion job for current congress.

##### `schedule_govinfo_ingestion()`

Schedule GovInfo ingestion job.

##### `schedule_health_check()`

Schedule system health check.

##### `schedule_cleanup()`

Schedule cleanup tasks (logs, old data, etc.).

##### `trigger_immediate_job(job_type, **kwargs)`

Trigger a job to run immediately.

**Parameters:**
- `job_type` (str): Job type ('openstates', 'congress', 'govinfo', 'monitoring').
- `**kwargs`: Additional job parameters.

**Returns:**
- `str`: Job ID or `None` if failed.

**Example:**
```python
scheduler = JobScheduler()
job_id = scheduler.trigger_immediate_job(
    'openstates',
    sample_mode=True,
    batch_size=25
)
```

##### `get_status()`

Get comprehensive scheduler status.

**Returns:**
- `dict`: Status information including:
  - `running`: Boolean indicating if scheduler is running
  - `next_runs`: List of upcoming scheduled jobs
  - `recent_jobs`: Recent job submissions
  - `queue_stats`: Current queue statistics

##### `setup_schedule()`

Configure the job schedule based on `SCHEDULE_CONFIG`.

---

## 3. Monitoring API

### 3.1 MonitoringSystem Class

Provides comprehensive system monitoring and health checks.

#### Methods

##### `run_all_checks()`

Execute all monitoring checks.

**Returns:**
- `dict`: Comprehensive check results including:
  - `timestamp`: Check timestamp
  - `checks_performed`: Number of checks completed
  - `alerts_triggered`: Number of alerts triggered
  - `overall_status`: Overall system status
  - `details`: Detailed results for each check

**Example:**
```python
monitor = MonitoringSystem()
results = monitor.run_all_checks()
print(f"Overall status: {results['overall_status']}")
```

#### 3.2 Individual Check Methods

##### `_check_database_connectivity()`

Check database connectivity and performance.

**Returns:**
- `dict`: Database health information:
  - `status`: 'healthy' or 'error'
  - `response_time`: Database response time in seconds
  - `database_version`: PostgreSQL version
  - `recent_jobs`: Recent ingestion job status

##### `_check_redis_connectivity()`

Check Redis connectivity and status.

**Returns:**
- `dict`: Redis health information:
  - `status`: 'healthy' or 'error'
  - `response_time`: Response time in seconds
  - `redis_version`: Redis version
  - `memory_usage`: Memory usage information
  - `connected_clients`: Number of connected clients

##### `_check_queue_health()`

Check health of all job queues.

**Returns:**
- `dict`: Queue health for each queue:
  - `status`: 'healthy', 'degraded', or 'error'
  - `started_jobs`: Number of started jobs
  - `finished_jobs`: Completed jobs
  - `failed_jobs`: Failed jobs
  - `success_rate`: Success rate percentage
  - `stuck_jobs`: Number of stuck jobs

##### `_check_job_health()`

Analyze overall job execution patterns.

**Returns:**
- `dict`: Job health analysis:
  - `last_24h_stats`: Job statistics for last 24 hours
  - `weekly_trends`: Weekly job trend analysis
  - `overall_status`: Overall job health status
  - `overall_success_rate`: System-wide success rate

##### `_check_system_resources()`

Monitor system resource utilization.

**Returns:**
- `dict`: System resource information:
  - `cpu`: CPU usage percentage and count
  - `memory`: Memory usage statistics
  - `disk`: Disk usage statistics
  - `alerts`: Any resource-related alerts

##### `_check_data_freshness()`

Verify data freshness across all sources.

**Returns:**
- `dict`: Data freshness information:
  - `data_sources`: Freshness info for each source
  - `fresh_sources`: Count of fresh data sources
  - `stale_sources`: Count of stale data sources
  - `no_data_sources`: Count of sources with no data

##### `_check_api_health()`

Monitor external API availability.

**Returns:**
- `dict`: API health for each external service:
  - `openstates`: OpenStates API status
  - `congress`: Congress.gov API status
  - `govinfo`: GovInfo API status

##### `generate_health_report()`

Generate human-readable health report.

**Returns:**
- `str`: Formatted health report.

---

## 4. Data Ingestion APIs

### 4.1 OpenStatesIngestor Class

#### Methods

##### `__init__(db_config)`

Initialize OpenStates ingestor with database configuration.

**Parameters:**
- `db_config` (DatabaseConfig): Database connection configuration.

##### `test_api_connection()`

Test OpenStates API connectivity.

**Returns:**
- `bool`: True if connection successful.

##### `ingest_data_type(data_type, jurisdiction)`

Ingest a specific data type for a jurisdiction.

**Parameters:**
- `data_type` (str): Data type to ingest.
- `jurisdiction` (str): Jurisdiction identifier (e.g., 'ca', 'ny').

**Returns:**
- `bool`: True if ingestion successful.

##### `ingest_all_data_types(jurisdictions)`

Ingest all supported data types for specified jurisdictions.

**Parameters:**
- `jurisdictions` (list): List of jurisdiction IDs.

**Returns:**
- `bool`: True if all ingestion successful.

##### `run_sample_ingestion()`

Run a sample ingestion with limited data for testing.

**Returns:**
- `bool`: True if sample ingestion successful.

**Data Types:**
- `jurisdictions`: State/territory information
- `people`: Legislators and officials
- `bills`: State legislation
- `organizations`: Committees and caucuses
- `events`: Legislative events and meetings

### 4.2 CongressGovIngestor Class

#### Methods

##### `ingest_data_type(data_type, congress)`

Ingest a specific data type for a congress.

**Parameters:**
- `data_type` (str): Data type to ingest.
- `congress` (int): Congress number (e.g., 119).

**Returns:**
- `bool`: True if ingestion successful.

##### `ingest_all_data_types(congress)`

Ingest all data types for specified congress.

**Parameters:**
- `congress` (int): Congress number.

**Returns:**
- `bool`: True if all ingestion successful.

##### `run_sample_ingestion(congress)`

Run sample ingestion for testing.

**Parameters:**
- `congress` (int): Congress number.

**Returns:**
- `bool`: True if successful.

**Data Types:**
- `members`: Congressional members
- `bills`: Federal legislation
- `committees`: Congressional committees
- `hearings`: Committee hearings
- `records`: Congressional Record entries
- `register`: Federal Register documents
- `laws`: Enacted laws
- `nominations`: Presidential nominations
- `treaties`: International treaties

### 4.3 GovInfoIngestor Class

#### Methods

##### `process_xml_files(data_type, xml_dir)`

Process XML files for a specific data type.

**Parameters:**
- `data_type` (str): Data type ('bills' or 'bill_actions').
- `xml_dir` (str): Directory containing XML files.

**Returns:**
- `bool`: True if processing successful.

##### `download_sample_bills(congress, limit)`

Download sample bill XML files for testing.

**Parameters:**
- `congress` (int): Congress number.
- `limit` (int): Number of files to download.

**Returns:**
- `bool`: True if download successful.

##### `run_sample_ingestion()`

Run complete sample ingestion.

**Returns:**
- `bool`: True if successful.

**Data Types:**
- `bills`: Bill document metadata
- `bill_actions`: Bill action history

---

## 5. Web Dashboard API

### 5.1 Flask Application Endpoints

#### GET `/`

Main dashboard page.

**Returns:**
- HTML page with dashboard interface.

#### GET `/api/status`

Get system status in JSON format.

**Returns:**
```json
{
  "services": {
    "queue_manager": "running",
    "job_scheduler": "running", 
    "redis": "running",
    "database": "running"
  },
  "queues": {
    "openstates": {
      "total_jobs": 5,
      "failed_jobs": 0,
      "success_rate": 100.0
    }
  },
  "recent_jobs": [
    {
      "source_name": "openstates",
      "status": "completed",
      "updated_at": "2025-10-30T16:30:00",
      "success_records": 150
    }
  ]
}
```

#### GET `/api/health`

Get detailed health check results.

**Returns:**
- JSON response from `monitoring_system.run_all_checks()`.

#### GET `/api/jobs`

Get recent job history.

**Returns:**
- JSON array of recent jobs with status information.

### 5.2 Dashboard Configuration

#### Flask Configuration

```python
DASHBOARD_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'secret_key': 'your-secret-key',
    'refresh_interval': 30  # seconds
}
```

---

## 6. Configuration API

### 6.1 Environment Variables

#### Database Configuration
```bash
DB_HOST=172.28.82.205
DB_PORT=5432
DB_NAME=opendiscourse
DB_USER=opendiscourse
DB_PASSWORD=opendiscourse123
```

#### Redis Configuration
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

#### API Keys
```bash
OPENSTATES_API_KEY=your_openstates_api_key
CONGRESS_API_KEY=your_congress_api_key
GOVINFO_API_KEY=your_govinfo_api_key
```

#### Alert Configuration
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
EMAIL_ALERT_TO=admin@yourdomain.com
EMAIL_ALERT_FROM=noreply@opendiscourse.org
```

### 6.2 Configuration Files

#### queue_config.py Configuration

**Queue Settings:**
```python
QUEUES = {
    QUEUE_OPENSTATES: {
        'connection': REDIS_CONFIG,
        'default_timeout': 7200,  # 2 hours
        'result_ttl': 86400,      # 24 hours
    }
}
```

**Schedule Configuration:**
```python
SCHEDULE_CONFIG = {
    'openstates': {
        'frequency': 'daily',
        'time': '02:00',
        'priority': 1,
    }
}
```

**Alert Thresholds:**
```python
ALERT_THRESHOLDS = {
    'job_failure_rate': 0.1,        # 10%
    'cpu_usage_threshold': 80,      # 80%
    'memory_usage_threshold': 80,   # 80%
}
```

---

## 7. Database Schema Reference

### 7.1 OpenStates Tables

#### `opencivicdata_jurisdiction`
```sql
CREATE TABLE opencivicdata_jurisdiction (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT,
    classification VARCHAR(50),
    division_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `opencivicdata_person`
```sql
CREATE TABLE opencivicdata_person (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    family_name VARCHAR(100),
    given_name VARCHAR(100),
    image TEXT,
    gender VARCHAR(50),
    email VARCHAR(255),
    biography TEXT,
    birth_date DATE,
    death_date DATE,
    primary_party VARCHAR(100),
    current_role JSONB,
    extras JSONB,
    current_jurisdiction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `opencivicdata_bill`
```sql
CREATE TABLE opencivicdata_bill (
    id VARCHAR(255) PRIMARY KEY,
    identifier VARCHAR(100) NOT NULL,
    title TEXT,
    classification JSONB,
    subject JSONB,
    extras JSONB,
    from_organization_id VARCHAR(255),
    legislative_session_id VARCHAR(255),
    first_action_date DATE,
    latest_action_date DATE,
    latest_action_description TEXT,
    latest_passage_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 Federal Tables

#### `federal_members`
```sql
CREATE TABLE federal_members (
    id SERIAL PRIMARY KEY,
    bioguide_id VARCHAR(50) UNIQUE NOT NULL,
    api_url TEXT,
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    party VARCHAR(50),
    state VARCHAR(2),
    chamber VARCHAR(20),
    current_member BOOLEAN DEFAULT FALSE,
    terms JSONB,
    committees JSONB,
    social_media JSONB,
    source_url TEXT,
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `federal_bills`
```sql
CREATE TABLE federal_bills (
    id SERIAL PRIMARY KEY,
    source_url TEXT UNIQUE NOT NULL,
    congress INTEGER,
    document_type VARCHAR(50),
    title TEXT,
    summary TEXT,
    session_year INTEGER,
    metadata JSONB,
    source VARCHAR(50) DEFAULT 'federal',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Bill-specific fields
    print_no VARCHAR(50),
    bill_type VARCHAR(10),
    number INTEGER,
    sponsor VARCHAR(255),
    status VARCHAR(100),
    introduced_date DATE,
    amends_source_url TEXT,
    amendment_number VARCHAR(50)
);
```

### 7.3 GovInfo Tables

#### `govinfo_bill`
```sql
CREATE TABLE govinfo_bill (
    id SERIAL PRIMARY KEY,
    bill_print_no VARCHAR(50) NOT NULL,
    session_year INTEGER,
    bill_type VARCHAR(10),
    title TEXT,
    short_title TEXT,
    summary TEXT,
    congress INTEGER,
    sponsor_name VARCHAR(255),
    sponsor_party VARCHAR(10),
    sponsor_state VARCHAR(2),
    introduced_date DATE,
    active_version VARCHAR(50),
    modified_date_time TIMESTAMP,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, bill_print_no, session_year)
);
```

#### `govinfo_bill_action`
```sql
CREATE TABLE govinfo_bill_action (
    id SERIAL PRIMARY KEY,
    action_code VARCHAR(20),
    text TEXT,
    action_date TIMESTAMP,
    sequence_no INTEGER,
    chamber VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7.4 Monitoring Tables

#### `master_ingestion_status`
```sql
CREATE TABLE master_ingestion_status (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    ingestion_type VARCHAR(20) DEFAULT 'full',
    total_records INTEGER DEFAULT 0,
    processed_records INTEGER DEFAULT 0,
    success_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    skipped_records INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    last_checkpoint TEXT,
    batch_size INTEGER DEFAULT 100,
    rate_limit_delay FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_name, data_type, ingestion_type)
);
```

---

This API reference provides comprehensive documentation for all programmatic interfaces in the OpenDiscourse Queue System. Each API endpoint, method, and parameter is documented with examples to facilitate integration and customization.