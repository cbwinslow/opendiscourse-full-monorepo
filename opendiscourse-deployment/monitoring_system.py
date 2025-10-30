#!/usr/bin/env python3
"""
Monitoring System for OpenDiscourse Data Ingestion
Health checks, performance monitoring, and alerting
"""

import os
import time
import psutil
import logging
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import psycopg2
from queue_config import (
    get_redis_connection,
    get_all_queues,
    DATABASE_CONFIG,
    ALERT_THRESHOLDS,
    logger as config_logger
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoringSystem:
    """Comprehensive monitoring for the data ingestion system"""
    
    def __init__(self):
        self.redis_conn = get_redis_connection()
        self.queues = get_all_queues()
        self.checks_performed = 0
        self.alerts_triggered = 0
        
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all monitoring checks"""
        logger.info("Starting comprehensive system checks")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'checks_performed': 0,
            'alerts_triggered': 0,
            'overall_status': 'unknown',
            'details': {}
        }
        
        try:
            # Database connectivity check
            db_check = self._check_database_connectivity()
            results['details']['database'] = db_check
            results['checks_performed'] += 1
            
            # Redis connectivity check
            redis_check = self._check_redis_connectivity()
            results['details']['redis'] = redis_check
            results['checks_performed'] += 1
            
            # Queue health checks
            queue_checks = self._check_queue_health()
            results['details']['queues'] = queue_checks
            results['checks_performed'] += len(queue_checks)
            
            # Job health checks
            job_checks = self._check_job_health()
            results['details']['jobs'] = job_checks
            results['checks_performed'] += 1
            
            # System resource checks
            system_checks = self._check_system_resources()
            results['details']['system'] = system_checks
            results['checks_performed'] += 1
            
            # Data freshness checks
            data_checks = self._check_data_freshness()
            results['details']['data_freshness'] = data_checks
            results['checks_performed'] += 1
            
            # API health checks
            api_checks = self._check_api_health()
            results['details']['apis'] = api_checks
            results['checks_performed'] += len(api_checks)
            
            # Overall status determination
            results['overall_status'] = self._determine_overall_status(results['details'])
            
            logger.info(f"Monitoring checks completed. Status: {results['overall_status']}")
            
        except Exception as e:
            logger.error(f"Error during monitoring checks: {e}")
            logger.error(traceback.format_exc())
            results['error'] = str(e)
            results['overall_status'] = 'error'
        
        return results
    
    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            start_time = time.time()
            conn = psycopg2.connect(**DATABASE_CONFIG)
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT 1, current_timestamp, version()")
            result = cursor.fetchone()
            
            response_time = time.time() - start_time
            
            # Check recent ingestion status
            cursor.execute("""
                SELECT source_name, status, updated_at, success_records 
                FROM master_ingestion_status 
                WHERE updated_at > CURRENT_DATE - INTERVAL '7 days'
                ORDER BY updated_at DESC
                LIMIT 20
            """)
            recent_jobs = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'status': 'healthy',
                'response_time': round(response_time, 3),
                'database_version': result[2] if len(result) > 2 else 'unknown',
                'recent_jobs': [
                    {
                        'source': row[0],
                        'status': row[1],
                        'updated_at': row[2].isoformat() if row[2] else None,
                        'records': row[3] or 0
                    } for row in recent_jobs
                ]
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_redis_connectivity(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            start_time = time.time()
            
            # Test basic Redis operations
            self.redis_conn.ping()
            info = self.redis_conn.info()
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': round(response_time, 3),
                'redis_version': info.get('redis_version', 'unknown'),
                'memory_usage': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_queue_health(self) -> Dict[str, Any]:
        """Check health of all queues"""
        queue_health = {}
        
        for queue_name, queue in self.queues.items():
            try:
                # Get queue statistics
                started_jobs = queue.started_job_registry.count
                finished_jobs = queue.finished_job_registry.count
                failed_jobs = queue.failed_job_registry.count
                deferred_jobs = queue.deferred_job_registry.count
                
                # Calculate job success rate
                total_finished = finished_jobs + failed_jobs
                success_rate = (finished_jobs / total_finished * 100) if total_finished > 0 else 0
                
                # Check for stuck jobs (started but not finished for > 1 hour)
                stuck_jobs = self._find_stuck_jobs(queue)
                
                queue_health[queue_name] = {
                    'status': 'healthy' if failed_jobs == 0 else 'degraded',
                    'started_jobs': started_jobs,
                    'finished_jobs': finished_jobs,
                    'failed_jobs': failed_jobs,
                    'deferred_jobs': deferred_jobs,
                    'success_rate': round(success_rate, 2),
                    'stuck_jobs': len(stuck_jobs),
                    'stuck_job_details': stuck_jobs[:5]  # Show first 5 stuck jobs
                }
                
                # Alert on high failure rate
                if failed_jobs > 0 and success_rate < (100 - ALERT_THRESHOLDS['job_failure_rate'] * 100):
                    self._trigger_alert(f"High failure rate in {queue_name}: {success_rate:.1f}%")
                    
            except Exception as e:
                queue_health[queue_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return queue_health
    
    def _find_stuck_jobs(self, queue) -> List[Dict[str, Any]]:
        """Find jobs that have been running for too long"""
        stuck_jobs = []
        
        try:
            # Get jobs from started registry
            for job_id in queue.started_job_registry.get_job_ids():
                try:
                    job = queue.connection.hgetall(f'rq:job:{job_id}')
                    if job and job.get('started_at'):
                        started_at = datetime.fromisoformat(job['started_at'].decode())
                        age = datetime.now() - started_at
                        
                        if age > timedelta(hours=1):  # Stuck if running for > 1 hour
                            stuck_jobs.append({
                                'job_id': job_id,
                                'started_at': started_at.isoformat(),
                                'age_hours': round(age.total_seconds() / 3600, 1),
                                'function': job.get('func_name', 'unknown')
                            })
                except Exception as e:
                    logger.error(f"Error checking job {job_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error finding stuck jobs: {e}")
        
        return stuck_jobs
    
    def _check_job_health(self) -> Dict[str, Any]:
        """Check overall job health and patterns"""
        try:
            # Get job statistics from database
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            # Jobs in last 24 hours
            cursor.execute("""
                SELECT 
                    source_name,
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_jobs,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_jobs,
                    AVG(CASE WHEN completed_at IS NOT NULL AND started_at IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (completed_at - started_at)) 
                        ELSE NULL END) as avg_duration_seconds
                FROM master_ingestion_status 
                WHERE updated_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                GROUP BY source_name
            """)
            
            job_stats = cursor.fetchall()
            
            # Jobs in last week for trend analysis
            cursor.execute("""
                SELECT 
                    DATE(updated_at) as job_date,
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_jobs
                FROM master_ingestion_status 
                WHERE updated_at > CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(updated_at)
                ORDER BY job_date
            """)
            
            weekly_trends = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Calculate success rates
            job_health = {
                'last_24h_stats': [
                    {
                        'source': stat[0],
                        'total_jobs': stat[1],
                        'successful_jobs': stat[2],
                        'failed_jobs': stat[3],
                        'success_rate': round((stat[2] / stat[1] * 100) if stat[1] > 0 else 0, 2),
                        'avg_duration_minutes': round((stat[4] / 60) if stat[4] else 0, 1)
                    } for stat in job_stats
                ],
                'weekly_trends': [
                    {
                        'date': trend[0].isoformat(),
                        'total_jobs': trend[1],
                        'failed_jobs': trend[2],
                        'failure_rate': round((trend[2] / trend[1] * 100) if trend[1] > 0 else 0, 2)
                    } for trend in weekly_trends
                ]
            }
            
            # Overall health assessment
            total_recent_jobs = sum(stat[1] for stat in job_stats)
            total_failures = sum(stat[3] for stat in job_stats)
            overall_success_rate = ((total_recent_jobs - total_failures) / total_recent_jobs * 100) if total_recent_jobs > 0 else 0
            
            job_health['overall_status'] = 'healthy' if overall_success_rate >= 90 else 'degraded' if overall_success_rate >= 70 else 'unhealthy'
            job_health['overall_success_rate'] = round(overall_success_rate, 2)
            
            return job_health
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Load average (Unix-like systems)
            load_avg = None
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'load_average': load_avg
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 2)
                },
                'alerts': []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_data_freshness(self) -> Dict[str, Any]:
        """Check freshness of data in database"""
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            # Check last update times for each data source
            cursor.execute("""
                SELECT 
                    source_name,
                    MAX(updated_at) as last_update,
                    COUNT(*) as total_records
                FROM master_ingestion_status 
                GROUP BY source_name
            """)
            
            data_sources = cursor.fetchall()
            
            freshness_info = []
            for source, last_update, total_records in data_sources:
                if last_update:
                    age_hours = (datetime.now() - last_update).total_seconds() / 3600
                    freshness_info.append({
                        'source': source,
                        'last_update': last_update.isoformat(),
                        'age_hours': round(age_hours, 2),
                        'status': 'fresh' if age_hours < 24 else 'stale',
                        'total_records': total_records
                    })
                else:
                    freshness_info.append({
                        'source': source,
                        'last_update': None,
                        'age_hours': None,
                        'status': 'no_data',
                        'total_records': total_records
                    })
            
            cursor.close()
            conn.close()
            
            return {
                'data_sources': freshness_info,
                'fresh_sources': len([s for s in freshness_info if s['status'] == 'fresh']),
                'stale_sources': len([s for s in freshness_info if s['status'] == 'stale']),
                'no_data_sources': len([s for s in freshness_info if s['status'] == 'no_data'])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check health of external APIs"""
        api_checks = {}
        
        # Check OpenStates API
        api_checks['openstates'] = self._check_api_endpoint(
            'https://openstates.org/api/v3/',
            os.getenv('OPENSTATES_API_KEY')
        )
        
        # Check Congress.gov API
        api_checks['congress'] = self._check_api_endpoint(
            'https://api.congress.gov/v3/',
            os.getenv('CONGRESS_API_KEY')
        )
        
        # Check GovInfo API
        api_checks['govinfo'] = self._check_api_endpoint(
            'https://api.govinfo.gov/',
            os.getenv('GOVINFO_API_KEY')
        )
        
        return api_checks
    
    def _check_api_endpoint(self, base_url: str, api_key: Optional[str]) -> Dict[str, Any]:
        """Check health of a specific API endpoint"""
        try:
            import requests
            
            headers = {}
            if api_key:
                headers['X-Api-Key'] = api_key
            
            start_time = time.time()
            response = requests.get(base_url, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy' if response.status_code < 400 else 'error',
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                'accessible': response.status_code < 500
            }
            
        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': 'connection_error', 'error': 'Connection failed'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _determine_overall_status(self, details: Dict[str, Any]) -> str:
        """Determine overall system status based on check results"""
        issues = []
        
        # Check database
        if details.get('database', {}).get('status') == 'error':
            issues.append('Database connectivity')
        
        # Check Redis
        if details.get('redis', {}).get('status') == 'error':
            issues.append('Redis connectivity')
        
        # Check queues
        for queue_name, queue_info in details.get('queues', {}).items():
            if queue_info.get('status') == 'error':
                issues.append(f'{queue_name} queue error')
            if queue_info.get('failed_jobs', 0) > 5:
                issues.append(f'{queue_name} high failure rate')
        
        # Check system resources
        system_info = details.get('system', {})
        if system_info.get('cpu', {}).get('usage_percent', 0) > ALERT_THRESHOLDS['cpu_usage_threshold']:
            issues.append('High CPU usage')
        if system_info.get('memory', {}).get('usage_percent', 0) > ALERT_THRESHOLDS['memory_usage_threshold']:
            issues.append('High memory usage')
        
        # Determine overall status
        if len(issues) == 0:
            return 'healthy'
        elif len(issues) <= 2:
            return 'degraded'
        else:
            return 'unhealthy'
    
    def _trigger_alert(self, message: str):
        """Trigger an alert for system issues"""
        self.alerts_triggered += 1
        logger.warning(f"ALERT: {message}")
        
        # You can implement additional alerting mechanisms here:
        # - Slack notifications
        # - Email alerts
        # - PagerDuty integration
        # - SMS alerts
        # - etc.
        
        try:
            if os.getenv('SLACK_WEBHOOK_URL'):
                self._send_slack_alert(message)
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def _send_slack_alert(self, message: str):
        """Send alert to Slack"""
        import requests
        
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        payload = {
            'text': f'🚨 OpenDiscourse Monitoring Alert',
            'attachments': [{
                'color': 'warning',
                'text': message,
                'footer': 'OpenDiscourse Monitor',
                'ts': int(time.time())
            }]
        }
        
        requests.post(webhook_url, json=payload)
    
    def generate_health_report(self) -> str:
        """Generate a human-readable health report"""
        check_results = self.run_all_checks()
        
        report = f"""
OpenDiscourse Data Ingestion - Health Report
============================================
Generated: {check_results['timestamp']}
Overall Status: {check_results['overall_status'].upper()}
Checks Performed: {check_results['checks_performed']}
Alerts Triggered: {check_results.get('alerts_triggered', 0)}

Database Status: {check_results['details'].get('database', {}).get('status', 'unknown')}
Redis Status: {check_results['details'].get('redis', {}).get('status', 'unknown')}

Queue Health:
"""
        
        for queue_name, queue_info in check_results['details'].get('queues', {}).items():
            report += f"  {queue_name}: {queue_info.get('status', 'unknown')} "
            report += f"({queue_info.get('finished_jobs', 0)} finished, "
            report += f"{queue_info.get('failed_jobs', 0)} failed)\n"
        
        report += f"""
System Resources:
  CPU: {check_results['details'].get('system', {}).get('cpu', {}).get('usage_percent', 0)}%
  Memory: {check_results['details'].get('system', {}).get('memory', {}).get('usage_percent', 0)}%
  Disk: {check_results['details'].get('system', {}).get('disk', {}).get('usage_percent', 0)}%

Data Freshness:
  Fresh sources: {check_results['details'].get('data_freshness', {}).get('fresh_sources', 0)}
  Stale sources: {check_results['details'].get('data_freshness', {}).get('stale_sources', 0)}
  No data sources: {check_results['details'].get('data_freshness', {}).get('no_data_sources', 0)}
"""
        
        if 'error' in check_results:
            report += f"\nERROR: {check_results['error']}\n"
        
        return report

# Command line interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitoring System for OpenDiscourse')
    parser.add_argument('command', choices=['check', 'report'],
                       help='Command to execute')
    parser.add_argument('--continuous', action='store_true',
                       help='Run checks continuously')
    parser.add_argument('--interval', type=int, default=300,
                       help='Interval in seconds for continuous monitoring (default: 300)')
    
    args = parser.parse_args()
    
    monitor = MonitoringSystem()
    
    if args.command == 'check':
        results = monitor.run_all_checks()
        print(json.dumps(results, indent=2))
    
    elif args.command == 'report':
        report = monitor.generate_health_report()
        print(report)
    
    elif args.command == 'check' and args.continuous:
        try:
            while True:
                results = monitor.run_all_checks()
                print(f"[{datetime.now()}] Status: {results['overall_status']}")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopping continuous monitoring...")