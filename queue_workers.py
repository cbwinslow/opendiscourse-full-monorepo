#!/usr/bin/env python3
"""
Redis Queue Workers for OpenDiscourse Data Ingestion
"""

import sys
import os
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import rq
from rq import Queue, Worker
from rq.decorators import job
from queue_config import (
    get_redis_connection,
    get_queue,
    QUEUE_OPENSTATES,
    QUEUE_CONGRESS,
    QUEUE_GOVINFO,
    QUEUE_MONITORING,
    WORKER_CONFIG,
    DATABASE_CONFIG,
    ALERT_THRESHOLDS
)

# Import our ingestion scripts
try:
    from ingest_openstates_data import ingest_openstates_data
    from ingest_congressgov_data import ingest_congressgov_data
    from ingest_govinfo_data import ingest_govinfo_data
    from monitoring_system import MonitoringSystem
except ImportError as e:
    print(f"Warning: Could not import ingestion modules: {e}")
    # Create mock functions for testing
    def mock_ingest_openstates_data(*args, **kwargs):
        return {"status": "success", "records_processed": 100}
    
    def mock_ingest_congressgov_data(*args, **kwargs):
        return {"status": "success", "records_processed": 200}
    
    def mock_ingest_govinfo_data(*args, **kwargs):
        return {"status": "success", "records_processed": 50}
    
    def mock_monitoring_system(*args, **kwargs):
        return {"status": "success", "checks_performed": 10}
    
    # Use mock functions
    ingest_openstates_data = mock_ingest_openstates_data
    ingest_congressgov_data = mock_ingest_congressgov_data
    ingest_govinfo_data = mock_ingest_govinfo_data
    MonitoringSystem = mock_monitoring_system

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('queue_workers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QueueManager:
    """Manages queue operations and job submission"""
    
    def __init__(self):
        self.redis_conn = get_redis_connection()
        self.queues = {
            'openstates': get_queue(QUEUE_OPENSTATES),
            'congress': get_queue(QUEUE_CONGRESS),
            'govinfo': get_queue(QUEUE_GOVINFO),
            'monitoring': get_queue(QUEUE_MONITORING),
        }
    
    def submit_openstates_job(self, data_types: list = None, sample_mode: bool = False, 
                            batch_size: int = 100) -> str:
        """Submit OpenStates ingestion job"""
        try:
            if data_types is None:
                data_types = ['jurisdictions', 'people', 'bills', 'organizations', 'events']
            
            job_args = {
                'data_types': data_types,
                'sample_mode': sample_mode,
                'batch_size': batch_size
            }
            
            job = self.queues['openstates'].enqueue(
                ingest_openstates_ingestion,
                job_args,
                timeout=WORKER_CONFIG['ingestion_worker_timeout'],
                retry=WORKER_CONFIG['max_retries']
            )
            
            logger.info(f"Submitted OpenStates job: {job.id}")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to submit OpenStates job: {e}")
            raise
    
    def submit_congress_job(self, data_types: list = None, congress: int = 118,
                          sample_mode: bool = False, batch_size: int = 50) -> str:
        """Submit Congress.gov ingestion job"""
        try:
            if data_types is None:
                data_types = ['members', 'bills', 'committees', 'hearings', 'records', 
                             'register', 'laws', 'nominations', 'treaties']
            
            job_args = {
                'data_types': data_types,
                'congress': congress,
                'sample_mode': sample_mode,
                'batch_size': batch_size
            }
            
            job = self.queues['congress'].enqueue(
                ingest_congress_ingestion,
                job_args,
                timeout=WORKER_CONFIG['ingestion_worker_timeout'],
                retry=WORKER_CONFIG['max_retries']
            )
            
            logger.info(f"Submitted Congress job: {job.id}")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to submit Congress job: {e}")
            raise
    
    def submit_govinfo_job(self, data_types: list = None, sample_mode: bool = False) -> str:
        """Submit GovInfo ingestion job"""
        try:
            if data_types is None:
                data_types = ['bill_documents', 'bill_actions']
            
            job_args = {
                'data_types': data_types,
                'sample_mode': sample_mode
            }
            
            job = self.queues['govinfo'].enqueue(
                ingest_govinfo_ingestion,
                job_args,
                timeout=WORKER_CONFIG['ingestion_worker_timeout'],
                retry=WORKER_CONFIG['max_retries']
            )
            
            logger.info(f"Submitted GovInfo job: {job.id}")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to submit GovInfo job: {e}")
            raise
    
    def submit_monitoring_job(self) -> str:
        """Submit monitoring and health check job"""
        try:
            job = self.queues['monitoring'].enqueue(
                run_monitoring_checks,
                timeout=WORKER_CONFIG['monitoring_worker_timeout'],
                retry=WORKER_CONFIG['max_retries']
            )
            
            logger.info(f"Submitted monitoring job: {job.id}")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to submit monitoring job: {e}")
            raise
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status and results"""
        try:
            job = rq.job.Job.fetch(job_id, connection=self.redis_conn)
            
            return {
                'id': job.id,
                'status': job.get_status(),
                'created_at': job.created_at,
                'started_at': job.started_at,
                'ended_at': job.ended_at,
                'result': job.result,
                'exc_info': job.exc_info,
                'failure_reason': job.failure_reason,
                'is_failed': job.is_failed,
                'is_finished': job.is_finished,
                'is_started': job.is_started,
            }
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return {'error': str(e)}
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues"""
        stats = {}
        for name, queue in self.queues.items():
            try:
                job_ids = queue.get_job_ids()
                stats[name] = {
                    'total_jobs': len(job_ids),
                    'started_jobs': queue.started_job_registry.count,
                    'finished_jobs': queue.finished_job_registry.count,
                    'failed_jobs': queue.failed_job_registry.count,
                    'deferred_jobs': queue.deferred_job_registry.count,
                    'scheduled_jobs': queue.scheduled_job_registry.count,
                }
            except Exception as e:
                logger.error(f"Failed to get stats for queue {name}: {e}")
                stats[name] = {'error': str(e)}
        
        return stats

# Worker Functions
def ingest_openstates_ingestion(job_args: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for OpenStates ingestion"""
    logger.info("Starting OpenStates ingestion job")
    
    try:
        # Update job status in database
        update_job_status('openstates', 'running')
        
        # Call the actual ingestion function
        result = ingest_openstates_data(**job_args)
        
        # Update final status
        update_job_status('openstates', 'completed', result)
        
        logger.info("OpenStates ingestion job completed successfully")
        return result
        
    except Exception as e:
        error_msg = f"OpenStates ingestion failed: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Update job status
        update_job_status('openstates', 'failed', error_msg)
        
        # Re-raise the exception for RQ retry handling
        raise

def ingest_congress_ingestion(job_args: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for Congress.gov ingestion"""
    logger.info("Starting Congress.gov ingestion job")
    
    try:
        # Update job status in database
        update_job_status('congress', 'running')
        
        # Call the actual ingestion function
        result = ingest_congressgov_data(**job_args)
        
        # Update final status
        update_job_status('congress', 'completed', result)
        
        logger.info("Congress.gov ingestion job completed successfully")
        return result
        
    except Exception as e:
        error_msg = f"Congress.gov ingestion failed: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Update job status
        update_job_status('congress', 'failed', error_msg)
        
        # Re-raise the exception for RQ retry handling
        raise

def ingest_govinfo_ingestion(job_args: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for GovInfo ingestion"""
    logger.info("Starting GovInfo ingestion job")
    
    try:
        # Update job status in database
        update_job_status('govinfo', 'running')
        
        # Call the actual ingestion function
        result = ingest_govinfo_data(**job_args)
        
        # Update final status
        update_job_status('govinfo', 'completed', result)
        
        logger.info("GovInfo ingestion job completed successfully")
        return result
        
    except Exception as e:
        error_msg = f"GovInfo ingestion failed: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Update job status
        update_job_status('govinfo', 'failed', error_msg)
        
        # Re-raise the exception for RQ retry handling
        raise

def run_monitoring_checks() -> Dict[str, Any]:
    """Run monitoring and health checks"""
    logger.info("Starting monitoring job")
    
    try:
        # Run monitoring system checks
        monitor = MonitoringSystem()
        result = monitor.run_all_checks()
        
        logger.info("Monitoring job completed successfully")
        return result
        
    except Exception as e:
        error_msg = f"Monitoring job failed: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Re-raise the exception for RQ retry handling
        raise

def update_job_status(source: str, status: str, result: Any = None, error: str = None):
    """Update job status in the database"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        query = """
        INSERT INTO master_ingestion_status 
        (source_name, data_type, ingestion_type, status, success_records, error_message, updated_at)
        VALUES (%s, 'all', 'full', %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (source_name, data_type, ingestion_type)
        DO UPDATE SET 
            status = %s,
            success_records = %s,
            error_message = %s,
            updated_at = CURRENT_TIMESTAMP
        """
        
        success_count = result.get('records_processed', 0) if isinstance(result, dict) else 0
        error_msg = error or (result.get('error') if isinstance(result, dict) else None)
        
        cursor.execute(query, (source, status, success_count, error_msg, status, success_count, error_msg))
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to update job status: {e}")

# Worker Management
class WorkerManager:
    """Manages RQ workers"""
    
    def __init__(self):
        self.queues = [
            get_queue(QUEUE_OPENSTATES),
            get_queue(QUEUE_CONGRESS),
            get_queue(QUEUE_GOVINFO),
            get_queue(QUEUE_MONITORING),
        ]
        self.workers = []
    
    def start_workers(self, num_workers_per_queue: int = 1):
        """Start workers for all queues"""
        logger.info(f"Starting {num_workers_per_queue} workers per queue")
        
        for queue in self.queues:
            for i in range(num_workers_per_queue):
                worker_name = f"{queue.name}_worker_{i}"
                worker = Worker(
                    [queue],
                    connection=queue.connection,
                    name=worker_name
                )
                self.workers.append(worker)
                
                # Start worker in a separate thread
                import threading
                worker_thread = threading.Thread(
                    target=worker.work,
                    kwargs={'burst': False},  # Continuous operation
                    name=f"{worker_name}_thread"
                )
                worker_thread.daemon = True
                worker_thread.start()
                
                logger.info(f"Started worker: {worker_name}")
    
    def stop_workers(self):
        """Stop all workers"""
        for worker in self.workers:
            try:
                worker.quit()
                logger.info(f"Stopped worker: {worker.name}")
            except Exception as e:
                logger.error(f"Failed to stop worker {worker.name}: {e}")
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        stats = {}
        for worker in self.workers:
            try:
                job = worker.get_current_job()
                stats[worker.name] = {
                    'state': worker.state,
                    'queue': worker.queue_names,
                    'current_job': job.id if job else None,
                    'failed_job_count': worker.failed_job_count,
                    'succeeded_job_count': worker.succeeded_job_count,
                    'total_working_time': worker.total_working_time,
                }
            except Exception as e:
                stats[worker.name] = {'error': str(e)}
        
        return stats

# Command line interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Queue Worker Manager')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'submit'],
                       help='Command to execute')
    parser.add_argument('--job-type', choices=['openstates', 'congress', 'govinfo', 'monitoring'],
                       help='Type of job to submit')
    parser.add_argument('--sample-mode', action='store_true',
                       help='Run in sample mode for testing')
    parser.add_argument('--workers', type=int, default=1,
                       help='Number of workers to start')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        manager = WorkerManager()
        manager.start_workers(args.workers)
        logger.info("Workers started. Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Shutting down workers...")
            manager.stop_workers()
    
    elif args.command == 'submit':
        queue_manager = QueueManager()
        
        if args.job_type == 'openstates':
            job_id = queue_manager.submit_openstates_job(sample_mode=args.sample_mode)
        elif args.job_type == 'congress':
            job_id = queue_manager.submit_congress_job(sample_mode=args.sample_mode)
        elif args.job_type == 'govinfo':
            job_id = queue_manager.submit_govinfo_job(sample_mode=args.sample_mode)
        elif args.job_type == 'monitoring':
            job_id = queue_manager.submit_monitoring_job()
        else:
            print("Please specify --job-type")
            sys.exit(1)
        
        print(f"Submitted job: {job_id}")
    
    elif args.command == 'status':
        queue_manager = QueueManager()
        stats = queue_manager.get_queue_stats()
        
        for queue_name, queue_stats in stats.items():
            print(f"\n{queue_name.upper()} Queue:")
            for key, value in queue_stats.items():
                print(f"  {key}: {value}")
    
    else:
        parser.print_help()