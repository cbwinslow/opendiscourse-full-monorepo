#!/usr/bin/env python3
"""
Unified Data Ingestion Orchestration Script
Runs all data ingestion workflows (OpenStates, Congress.gov, GovInfo) in sequence.
Provides comprehensive status reporting and error handling.
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Load environment variables
from dotenv import load_dotenv
load_dotenv('database_config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_ingestion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowStatus:
    """Status tracking for each workflow."""
    name: str
    script: str
    status: str  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[str] = None
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    error_message: str = ""
    output_log: str = ""

class UnifiedIngestionOrchestrator:
    """Orchestrates all data ingestion workflows."""
    
    def __init__(self):
        self.workflows = [
            WorkflowStatus(
                name="Database Setup",
                script="setup_database.py",
                status="pending"
            ),
            WorkflowStatus(
                name="OpenStates Data",
                script="ingest_openstates_data.py",
                status="pending"
            ),
            WorkflowStatus(
                name="Congress.gov Data",
                script="ingest_congressgov_data.py",
                status="pending"
            ),
            WorkflowStatus(
                name="GovInfo Data",
                script="ingest_govinfo_data.py",
                status="pending"
            )
        ]
        
        self.overall_start_time = datetime.now()
        self.results = {
            'overall_status': 'pending',
            'start_time': self.overall_start_time.isoformat(),
            'end_time': None,
            'duration': None,
            'workflows': []
        }
    
    def run_workflow(self, workflow: WorkflowStatus, args: List[str] = None) -> bool:
        """Run a single workflow with the given arguments."""
        if args is None:
            args = ['--mode', 'sample']  # Default to sample mode
        
        logger.info(f"🚀 Starting workflow: {workflow.name}")
        workflow.status = 'running'
        workflow.start_time = datetime.now()
        
        try:
            # Run the workflow script
            cmd = [sys.executable, workflow.script] + args
            
            logger.info(f"📋 Running command: {' '.join(cmd)}")
            
            # Run with timeout and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Capture output in real-time
            output_lines = []
            for line in process.stdout:
                output_lines.append(line.rstrip())
                print(line.rstrip())  # Also print to console
                
                # Check for key metrics in output
                if 'Total processed:' in line:
                    try:
                        total = int(line.split('Total processed:')[1].strip())
                        workflow.records_processed = total
                    except (ValueError, IndexError):
                        pass
                
                if 'Successful:' in line:
                    try:
                        successful = int(line.split('Successful:')[1].strip())
                        workflow.records_successful = successful
                    except (ValueError, IndexError):
                        pass
            
            # Wait for process to complete
            return_code = process.wait()
            
            workflow.end_time = datetime.now()
            workflow.output_log = '\n'.join(output_lines)
            
            if return_code == 0:
                workflow.status = 'completed'
                workflow.duration = str(workflow.end_time - workflow.start_time)
                logger.info(f"✅ Completed workflow: {workflow.name}")
                return True
            else:
                workflow.status = 'failed'
                workflow.error_message = f"Process exited with code {return_code}"
                logger.error(f"❌ Failed workflow: {workflow.name} - {workflow.error_message}")
                return False
                
        except subprocess.TimeoutExpired:
            workflow.status = 'failed'
            workflow.error_message = "Process timed out"
            logger.error(f"⏰ Timeout for workflow: {workflow.name}")
            return False
        except Exception as e:
            workflow.status = 'failed'
            workflow.error_message = str(e)
            logger.error(f"💥 Error running workflow {workflow.name}: {e}")
            return False
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity before starting workflows."""
        logger.info("🔍 Testing database connectivity...")
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', '172.28.82.205'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'opendiscourse'),
                user=os.getenv('DB_USER', 'opendiscourse'),
                password=os.getenv('DB_PASSWORD', 'opendiscourse123')
            )
            conn.close()
            logger.info("✅ Database connectivity test passed")
            return True
        except Exception as e:
            logger.error(f"❌ Database connectivity test failed: {e}")
            return False
    
    def run_sample_ingestions(self) -> bool:
        """Run sample ingestions for all workflows."""
        logger.info("🧪 Starting sample data ingestion for all workflows")
        
        # First, set up the database
        db_workflow = next(w for w in self.workflows if w.name == "Database Setup")
        db_success = self.run_workflow(db_workflow, [])
        
        if not db_success:
            logger.error("❌ Database setup failed, cannot proceed")
            return False
        
        # Run sample ingestions for each data source
        ingestion_workflows = [w for w in self.workflows if w.name != "Database Setup"]
        
        overall_success = True
        
        for workflow in ingestion_workflows:
            logger.info(f"🎯 Running sample ingestion for {workflow.name}")
            
            if workflow.name == "OpenStates Data":
                # For OpenStates, we need an API key
                if not os.getenv('OPENSTATES_API_KEY'):
                    logger.warning("⚠️ OpenStates API key not found, skipping OpenStates ingestion")
                    workflow.status = 'skipped'
                    workflow.error_message = "API key not configured"
                    continue
                
                args = ['--mode', 'sample']
                
            elif workflow.name == "Congress.gov Data":
                # For Congress.gov, we need an API key
                if not os.getenv('CONGRESS_API_KEY'):
                    logger.warning("⚠️ Congress.gov API key not found, skipping Congress.gov ingestion")
                    workflow.status = 'skipped'
                    workflow.error_message = "API key not configured"
                    continue
                
                args = ['--mode', 'sample', '--congress', '119']
                
            elif workflow.name == "GovInfo Data":
                # For GovInfo, no API key needed for sample
                args = ['--mode', 'sample', '--congress', '119', '--limit', '3']
            
            # Run the workflow
            if not self.run_workflow(workflow, args):
                overall_success = False
                logger.error(f"❌ {workflow.name} failed, but continuing with other workflows")
        
        return overall_success
    
    def run_full_ingestions(self, openstates_jurisdictions: List[str] = None, congress: int = 119) -> bool:
        """Run full ingestions for all workflows."""
        logger.info("🚀 Starting full data ingestion for all workflows")
        
        # First, set up the database
        db_workflow = next(w for w in self.workflows if w.name == "Database Setup")
        db_success = self.run_workflow(db_workflow, [])
        
        if not db_success:
            logger.error("❌ Database setup failed, cannot proceed")
            return False
        
        # Run full ingestions for each data source
        overall_success = True
        
        # OpenStates ingestion
        openstates_workflow = next(w for w in self.workflows if w.name == "OpenStates Data")
        if os.getenv('OPENSTATES_API_KEY'):
            args = ['--mode', 'full']
            if openstates_jurisdictions:
                args.extend(['--jurisdiction', ','.join(openstates_jurisdictions)])
            
            if not self.run_workflow(openstates_workflow, args):
                overall_success = False
        else:
            logger.warning("⚠️ OpenStates API key not found, skipping OpenStates ingestion")
            openstates_workflow.status = 'skipped'
        
        # Congress.gov ingestion
        congress_workflow = next(w for w in self.workflows if w.name == "Congress.gov Data")
        if os.getenv('CONGRESS_API_KEY'):
            args = ['--mode', 'full', '--congress', str(congress)]
            
            if not self.run_workflow(congress_workflow, args):
                overall_success = False
        else:
            logger.warning("⚠️ Congress.gov API key not found, skipping Congress.gov ingestion")
            congress_workflow.status = 'skipped'
        
        # GovInfo ingestion
        govinfo_workflow = next(w for w in self.workflows if w.name == "GovInfo Data")
        args = ['--mode', 'full']  # Requires --xml-dir to be specified
        
        if not self.run_workflow(govinfo_workflow, args):
            logger.warning("⚠️ GovInfo ingestion requires XML directory, skipping")
            govinfo_workflow.status = 'skipped'
        
        return overall_success
    
    def generate_report(self) -> str:
        """Generate a comprehensive ingestion report."""
        report = []
        report.append("=" * 80)
        report.append("UNIFIED DATA INGESTION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Overall Duration: {datetime.now() - self.overall_start_time}")
        report.append("")
        
        # Overall status
        completed_workflows = [w for w in self.workflows if w.status == 'completed']
        failed_workflows = [w for w in self.workflows if w.status == 'failed']
        skipped_workflows = [w for w in self.workflows if w.status == 'skipped']
        
        report.append("SUMMARY:")
        report.append(f"  ✅ Completed: {len(completed_workflows)}")
        report.append(f"  ❌ Failed: {len(failed_workflows)}")
        report.append(f"  ⏭️ Skipped: {len(skipped_workflows)}")
        report.append("")
        
        # Detailed workflow results
        report.append("WORKFLOW DETAILS:")
        for workflow in self.workflows:
            report.append(f"  {workflow.name}:")
            report.append(f"    Status: {workflow.status.upper()}")
            if workflow.start_time and workflow.end_time:
                report.append(f"    Duration: {workflow.duration}")
            if workflow.records_processed > 0:
                report.append(f"    Records Processed: {workflow.records_processed}")
                report.append(f"    Records Successful: {workflow.records_successful}")
                report.append(f"    Records Failed: {workflow.records_failed}")
            if workflow.error_message:
                report.append(f"    Error: {workflow.error_message}")
            report.append("")
        
        # API Key status
        report.append("CONFIGURATION:")
        report.append(f"  Database Host: {os.getenv('DB_HOST', '172.28.82.205')}")
        report.append(f"  OpenStates API Key: {'✅ Configured' if os.getenv('OPENSTATES_API_KEY') else '❌ Not configured'}")
        report.append(f"  Congress.gov API Key: {'✅ Configured' if os.getenv('CONGRESS_API_KEY') else '❌ Not configured'}")
        report.append(f"  GovInfo API Key: {'✅ Configured' if os.getenv('GOVINFO_API_KEY') else '❌ Not configured (not required)'}")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        if not os.getenv('OPENSTATES_API_KEY'):
            report.append("  - Obtain OpenStates API key from https://openstates.org/accounts/register/")
        if not os.getenv('CONGRESS_API_KEY'):
            report.append("  - Obtain Congress.gov API key from https://api.congress.gov/sign-up/")
        if not os.getenv('GOVINFO_API_KEY'):
            report.append("  - GovInfo API key is optional but recommended for higher rate limits")
        report.append("  - Monitor log files for detailed error information")
        report.append("  - Run individual workflows separately for debugging")
        report.append("")
        
        return '\n'.join(report)
    
    def save_results(self, filename: str = None):
        """Save results to JSON file."""
        if filename is None:
            filename = f"ingestion_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Update overall results
        self.results['overall_status'] = 'completed' if all(
            w.status in ['completed', 'skipped'] for w in self.workflows
        ) else 'partial'
        self.results['end_time'] = datetime.now().isoformat()
        self.results['duration'] = str(datetime.now() - self.overall_start_time)
        self.results['workflows'] = [asdict(w) for w in self.workflows]
        
        # Convert datetime objects to ISO strings
        for workflow_data in self.results['workflows']:
            if workflow_data['start_time']:
                workflow_data['start_time'] = workflow_data['start_time'].isoformat()
            if workflow_data['end_time']:
                workflow_data['end_time'] = workflow_data['end_time'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"📊 Results saved to {filename}")
        return filename

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Unified Data Ingestion Orchestrator')
    parser.add_argument('--mode', choices=['sample', 'full'], default='sample',
                       help='Ingestion mode: sample (limited data) or full (comprehensive data)')
    parser.add_argument('--openstates-jurisdictions', 
                       help='Comma-separated list of OpenStates jurisdictions (e.g., "ca,ny,tx")')
    parser.add_argument('--congress', type=int, default=119,
                       help='Congress number for federal data (default: 119)')
    parser.add_argument('--govinfo-xml-dir',
                       help='Directory containing GovInfo XML files for full ingestion')
    parser.add_argument('--skip-db-setup', action='store_true',
                       help='Skip database setup (assume already done)')
    parser.add_argument('--report-file', 
                       help='Custom filename for results report')
    
    args = parser.parse_args()
    
    # Parse jurisdictions if provided
    jurisdictions = None
    if args.openstates_jurisdictions:
        jurisdictions = [j.strip() for j in args.openstates_jurisdictions.split(',')]
    
    logger.info("🚀 Starting Unified Data Ingestion Orchestrator")
    logger.info("=" * 60)
    
    # Create orchestrator
    orchestrator = UnifiedIngestionOrchestrator()
    
    # Test database connectivity first
    if not orchestrator.test_database_connectivity():
        logger.error("❌ Database connectivity test failed. Please check your configuration.")
        sys.exit(1)
    
    success = False
    
    if args.mode == 'sample':
        logger.info("🧪 Running sample ingestion mode")
        success = orchestrator.run_sample_ingestions()
    else:
        logger.info("🚀 Running full ingestion mode")
        success = orchestrator.run_full_ingestions(jurisdictions, args.congress)
    
    # Generate and display report
    report = orchestrator.generate_report()
    print("\n" + report)
    
    # Save results
    results_file = orchestrator.save_results(args.report_file)
    
    # Final status
    if success:
        logger.info("🎉 Unified ingestion completed successfully!")
        print(f"\n📊 Full report saved to: {results_file}")
        sys.exit(0)
    else:
        logger.error("💥 Unified ingestion completed with errors!")
        print(f"\n📊 Check {results_file} for detailed results and error information")
        sys.exit(1)

if __name__ == "__main__":
    main()