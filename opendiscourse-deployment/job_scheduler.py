#!/usr/bin/env python3
"""
Job Scheduler for OpenDiscourse Data Ingestion
Cron-like scheduling for automated job execution
"""

import os
import time
import schedule
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from queue_workers import QueueManager
from queue_config import SCHEDULE_CONFIG, logger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobScheduler:
    """Manages scheduled jobs for data ingestion"""
    
    def __init__(self):
        self.queue_manager = QueueManager()
        self.running = False
        self.job_history = []
        self.max_history = 1000  # Keep last 1000 job submissions
        
    def schedule_openstates_ingestion(self):
        """Schedule OpenStates ingestion"""
        try:
            logger.info("Scheduled OpenStates ingestion starting")
            
            job_id = self.queue_manager.submit_openstates_job(
                sample_mode=False,
                batch_size=100
            )
            
            self._record_job_submission('openstates', job_id)
            logger.info(f"OpenStates ingestion job submitted: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule OpenStates ingestion: {e}")
            self._send_alert(f"OpenStates scheduling failed: {e}")
    
    def schedule_congress_ingestion(self):
        """Schedule Congress.gov ingestion"""
        try:
            logger.info("Scheduled Congress.gov ingestion starting")
            
            job_id = self.queue_manager.submit_congress_job(
                congress=118,  # Current congress
                sample_mode=False,
                batch_size=50
            )
            
            self._record_job_submission('congress', job_id)
            logger.info(f"Congress.gov ingestion job submitted: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule Congress.gov ingestion: {e}")
            self._send_alert(f"Congress scheduling failed: {e}")
    
    def schedule_govinfo_ingestion(self):
        """Schedule GovInfo ingestion"""
        try:
            logger.info("Scheduled GovInfo ingestion starting")
            
            job_id = self.queue_manager.submit_govinfo_job(
                sample_mode=False
            )
            
            self._record_job_submission('govinfo', job_id)
            logger.info(f"GovInfo ingestion job submitted: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule GovInfo ingestion: {e}")
            self._send_alert(f"GovInfo scheduling failed: {e}")
    
    def schedule_health_check(self):
        """Schedule monitoring and health checks"""
        try:
            logger.info("Scheduled health check starting")
            
            job_id = self.queue_manager.submit_monitoring_job()
            
            self._record_job_submission('monitoring', job_id)
            logger.info(f"Health check job submitted: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule health check: {e}")
            self._send_alert(f"Health check scheduling failed: {e}")
    
    def schedule_cleanup(self):
        """Schedule cleanup tasks"""
        try:
            logger.info("Scheduled cleanup starting")
            
            # Run cleanup tasks
            self._cleanup_old_jobs()
            self._cleanup_old_logs()
            self._cleanup_old_data()
            
            logger.info("Cleanup tasks completed")
            
        except Exception as e:
            logger.error(f"Failed to run cleanup: {e}")
            self._send_alert(f"Cleanup failed: {e}")
    
    def _record_job_submission(self, source: str, job_id: str):
        """Record job submission in history"""
        self.job_history.append({
            'source': source,
            'job_id': job_id,
            'submitted_at': datetime.now(),
            'status': 'submitted'
        })
        
        # Trim history if too long
        if len(self.job_history) > self.max_history:
            self.job_history = self.job_history[-self.max_history:]
    
    def _send_alert(self, message: str):
        """Send alert (implement with your preferred notification system)"""
        logger.warning(f"ALERT: {message}")
        
        # Example: Send to Slack, email, etc.
        # You can implement Slack, email, or other notification systems here
        try:
            if os.getenv('SLACK_WEBHOOK_URL'):
                self._send_slack_alert(message)
            if os.getenv('EMAIL_ALERT_TO'):
                self._send_email_alert(message)
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def _send_slack_alert(self, message: str):
        """Send alert to Slack"""
        import requests
        
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        payload = {
            'text': f'🚨 OpenDiscourse Data Ingestion Alert',
            'attachments': [{
                'color': 'danger',
                'text': message,
                'footer': 'OpenDiscourse Scheduler',
                'ts': int(time.time())
            }]
        }
        
        requests.post(webhook_url, json=payload)
    
    def _send_email_alert(self, message: str):
        """Send alert via email"""
        import smtplib
        from email.mime.text import MIMEText
        
        smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', '25'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        from_email = os.getenv('EMAIL_ALERT_FROM', 'noreply@opendiscourse.org')
        to_email = os.getenv('EMAIL_ALERT_TO')
        
        msg = MIMEText(f"OpenDiscourse Data Ingestion Alert\n\n{message}\n\nTimestamp: {datetime.now()}")
        msg['Subject'] = 'OpenDiscourse Alert'
        msg['From'] = from_email
        msg['To'] = to_email
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
    
    def _cleanup_old_jobs(self):
        """Clean up old job records"""
        # Keep only last 30 days of job history
        cutoff_date = datetime.now() - timedelta(days=30)
        self.job_history = [
            job for job in self.job_history 
            if job['submitted_at'] > cutoff_date
        ]
        logger.info(f"Cleaned up old job records. {len(self.job_history)} remaining.")
    
    def _cleanup_old_logs(self):
        """Clean up old log files"""
        import glob
        import glob
        
        log_files = glob.glob('*.log*')
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for log_file in log_files:
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < cutoff_date:
                    os.remove(log_file)
                    logger.info(f"Removed old log file: {log_file}")
            except Exception as e:
                logger.error(f"Failed to remove log file {log_file}: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data (implement based on your retention policy)"""
        try:
            import psycopg2
            from queue_config import DATABASE_CONFIG
            
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()
            
            # Keep only last 90 days of ingestion status records
            cursor.execute("""
                DELETE FROM master_ingestion_status 
                WHERE updated_at < CURRENT_DATE - INTERVAL '90 days'
            """)
            
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old ingestion status records")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def setup_schedule(self):
        """Setup the job schedule based on configuration"""
        logger.info("Setting up job schedule")
        
        # Schedule OpenStates ingestion
        openstates_config = SCHEDULE_CONFIG['openstates']
        if openstates_config['frequency'] == 'daily':
            schedule.every().day.at(openstates_config['time']).do(
                self.schedule_openstates_ingestion
            )
        
        # Schedule Congress.gov ingestion
        congress_config = SCHEDULE_CONFIG['congress']
        if congress_config['frequency'] == 'daily':
            schedule.every().day.at(congress_config['time']).do(
                self.schedule_congress_ingestion
            )
        
        # Schedule GovInfo ingestion
        govinfo_config = SCHEDULE_CONFIG['govinfo']
        if govinfo_config['frequency'] == 'daily':
            schedule.every().day.at(govinfo_config['time']).do(
                self.schedule_govinfo_ingestion
            )
        
        # Schedule health checks
        health_config = SCHEDULE_CONFIG['health_check']
        if health_config['frequency'] == 'hourly':
            schedule.every().hour.do(
                self.schedule_health_check
            )
        
        # Schedule cleanup
        cleanup_config = SCHEDULE_CONFIG['cleanup']
        if 'Sunday' in cleanup_config['time']:
            # Parse "Sunday 01:00"
            time_part = cleanup_config['time'].split()[1]
            schedule.every().sunday.at(time_part).do(
                self.schedule_cleanup
            )
        
        # Schedule initial health check
        schedule.every(5).minutes.do(
            self.schedule_health_check
        ).tag('initial')  # Only run for the first few times
        
        logger.info("Job schedule setup completed")
    
    def run_schedule(self):
        """Run the scheduler loop"""
        self.running = True
        logger.info("Job scheduler started")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self._send_alert(f"Scheduler error: {e}")
        
        finally:
            logger.info("Job scheduler stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status and statistics"""
        return {
            'running': self.running,
            'next_runs': [
                {
                    'job': str(job.job_func),
                    'next_run': job.next_run
                }
                for job in schedule.jobs
            ],
            'recent_jobs': [
                {
                    'source': job['source'],
                    'job_id': job['job_id'],
                    'submitted_at': job['submitted_at'].isoformat(),
                    'status': job['status']
                }
                for job in self.job_history[-10:]  # Last 10 jobs
            ],
            'queue_stats': self.queue_manager.get_queue_stats()
        }
    
    def trigger_immediate_job(self, job_type: str, **kwargs) -> Optional[str]:
        """Trigger a job immediately"""
        try:
            if job_type == 'openstates':
                job_id = self.queue_manager.submit_openstates_job(**kwargs)
            elif job_type == 'congress':
                job_id = self.queue_manager.submit_congress_job(**kwargs)
            elif job_type == 'govinfo':
                job_id = self.queue_manager.submit_govinfo_job(**kwargs)
            elif job_type == 'monitoring':
                job_id = self.queue_manager.submit_monitoring_job()
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            self._record_job_submission(job_type, job_id)
            logger.info(f"Immediate {job_type} job triggered: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to trigger immediate {job_type} job: {e}")
            return None

# Command line interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Job Scheduler for OpenDiscourse')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'trigger'],
                       help='Command to execute')
    parser.add_argument('--job-type', choices=['openstates', 'congress', 'govinfo', 'monitoring'],
                       help='Type of job to trigger')
    parser.add_argument('--sample-mode', action='store_true',
                       help='Run in sample mode for testing')
    
    args = parser.parse_args()
    
    scheduler = JobScheduler()
    
    if args.command == 'start':
        scheduler.setup_schedule()
        scheduler.run_schedule()
    
    elif args.command == 'stop':
        scheduler.stop()
    
    elif args.command == 'status':
        status = scheduler.get_status()
        print("Scheduler Status:")
        print(f"Running: {status['running']}")
        print(f"\nNext Scheduled Jobs:")
        for job in status['next_runs']:
            print(f"  {job['job']}: {job['next_run']}")
        print(f"\nRecent Jobs:")
        for job in status['recent_jobs']:
            print(f"  {job['source']}: {job['job_id']} ({job['status']})")
        print(f"\nQueue Stats:")
        for queue, stats in status['queue_stats'].items():
            print(f"  {queue}: {stats}")
    
    elif args.command == 'trigger':
        if not args.job_type:
            print("Please specify --job-type")
            sys.exit(1)
        
        kwargs = {}
        if args.sample_mode:
            kwargs['sample_mode'] = True
        
        job_id = scheduler.trigger_immediate_job(args.job_type, **kwargs)
        if job_id:
            print(f"Triggered job: {job_id}")
        else:
            print("Failed to trigger job")
            sys.exit(1)
    
    else:
        parser.print_help()