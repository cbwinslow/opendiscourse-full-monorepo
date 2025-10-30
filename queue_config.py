#!/usr/bin/env python3
"""
Redis Queue Configuration for OpenDiscourse Data Ingestion
"""

import os
import redis
from rq import Queue
from redis import Redis
import logging
from typing import Dict, Any

# Queue Names
QUEUE_DEFAULT = 'default'
QUEUE_OPENSTATES = 'openstates'
QUEUE_CONGRESS = 'congress'
QUEUE_GOVINFO = 'govinfo'
QUEUE_MONITORING = 'monitoring'

# Job Queue Configuration
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', '6379')),
    'db': int(os.getenv('REDIS_DB', '0')),
    'password': os.getenv('REDIS_PASSWORD', None),
    'decode_responses': True
}

# Worker Configuration
WORKER_CONFIG = {
    'default_worker_timeout': 3600,  # 1 hour
    'ingestion_worker_timeout': 7200,  # 2 hours
    'monitoring_worker_timeout': 300,  # 5 minutes
    'max_retries': 3,
    'retry_delay': 300,  # 5 minutes
    'result_ttl': 86400,  # 24 hours
    'failure_ttl': 604800,  # 7 days
}

# Queue Connection Settings
QUEUES = {
    QUEUE_DEFAULT: {
        'connection': REDIS_CONFIG,
        'default_timeout': WORKER_CONFIG['default_worker_timeout'],
        'result_ttl': WORKER_CONFIG['result_ttl'],
    },
    QUEUE_OPENSTATES: {
        'connection': REDIS_CONFIG,
        'default_timeout': WORKER_CONFIG['ingestion_worker_timeout'],
        'result_ttl': WORKER_CONFIG['result_ttl'],
    },
    QUEUE_CONGRESS: {
        'connection': REDIS_CONFIG,
        'default_timeout': WORKER_CONFIG['ingestion_worker_timeout'],
        'result_ttl': WORKER_CONFIG['result_ttl'],
    },
    QUEUE_GOVINFO: {
        'connection': REDIS_CONFIG,
        'default_timeout': WORKER_CONFIG['ingestion_worker_timeout'],
        'result_ttl': WORKER_CONFIG['result_ttl'],
    },
    QUEUE_MONITORING: {
        'connection': REDIS_CONFIG,
        'default_timeout': WORKER_CONFIG['monitoring_worker_timeout'],
        'result_ttl': WORKER_CONFIG['result_ttl'],
    },
}

# Job Status
JOB_STATUS = {
    'PENDING': 'pending',
    'RUNNING': 'running',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'RETRYING': 'retrying',
    'CANCELLED': 'cancelled'
}

# Ingestion Scheduling Configuration
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

# Alert Thresholds
ALERT_THRESHOLDS = {
    'job_failure_rate': 0.1,  # 10% failure rate
    'job_duration_threshold': 7200,  # 2 hours
    'queue_age_threshold': 3600,  # 1 hour
    'consecutive_failures': 3,
    'memory_usage_threshold': 80,  # 80%
    'cpu_usage_threshold': 80,  # 80%
}

# Database Configuration (same as existing)
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', '172.28.82.205'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'opendiscourse'),
    'user': os.getenv('DB_USER', 'opendiscourse'),
    'password': os.getenv('DB_PASSWORD', 'opendiscourse123')
}

def get_redis_connection() -> Redis:
    """Get Redis connection instance"""
    return Redis(**REDIS_CONFIG)

def get_queue(queue_name: str) -> Queue:
    """Get queue instance by name"""
    if queue_name not in QUEUES:
        raise ValueError(f"Unknown queue: {queue_name}")
    
    redis_conn = get_redis_connection()
    return Queue(
        queue_name,
        connection=redis_conn,
        **QUEUES[queue_name]
    )

def get_all_queues() -> Dict[str, Queue]:
    """Get all queue instances"""
    return {name: get_queue(name) for name in QUEUES.keys()}

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)