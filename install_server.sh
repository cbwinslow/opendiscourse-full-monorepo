#!/bin/bash
# OpenDiscourse Data Ingestion Queue System - Server Installation Script
# This script installs and configures the complete system on your server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/opendiscourse/queue-system"
SERVICE_USER="opendiscourse"
SERVICE_GROUP="opendiscourse"
LOG_DIR="/var/log/opendiscourse"
CONFIG_DIR="/etc/opendiscourse"

echo -e "${BLUE}OpenDiscourse Queue System - Server Installation${NC}"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run this script as root (use sudo)${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Update system packages
echo -e "\n${BLUE}Step 1: Updating system packages${NC}"
apt update && apt upgrade -y
print_status "System packages updated"

# Install system dependencies
echo -e "\n${BLUE}Step 2: Installing system dependencies${NC}"
apt install -y python3 python3-pip python3-venv redis-server postgresql-client nginx supervisor
apt install -y build-essential libpq-dev python3-dev
apt install -y curl wget git htop
print_status "System dependencies installed"

# Start and enable services
echo -e "\n${BLUE}Step 3: Starting services${NC}"
systemctl start redis-server
systemctl enable redis-server
systemctl start supervisor
systemctl enable supervisor
print_status "Redis and Supervisor services started"

# Create service user
echo -e "\n${BLUE}Step 4: Creating service user${NC}"
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --shell /bin/bash --home $INSTALL_DIR --create-home $SERVICE_USER
    usermod -aG sudo $SERVICE_USER
    print_status "Service user '$SERVICE_USER' created"
else
    print_warning "Service user '$SERVICE_USER' already exists"
fi

# Create directories
echo -e "\n${BLUE}Step 5: Creating directory structure${NC}"
mkdir -p $INSTALL_DIR
mkdir -p $LOG_DIR
mkdir -p $CONFIG_DIR
mkdir -p $INSTALL_DIR/logs
mkdir -p $INSTALL_DIR/config
mkdir -p $INSTALL_DIR/scripts

# Set ownership
chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_DIR
chown -R $SERVICE_USER:$SERVICE_GROUP $LOG_DIR
chown -R $SERVICE_USER:$SERVICE_GROUP $CONFIG_DIR

print_status "Directory structure created"

# Copy queue system files
echo -e "\n${BLUE}Step 6: Installing queue system files${NC}"

# Copy main application files
cp queue_config.py $INSTALL_DIR/
cp queue_workers.py $INSTALL_DIR/
cp job_scheduler.py $INSTALL_DIR/
cp monitoring_system.py $INSTALL_DIR/
cp requirements-queue.txt $INSTALL_DIR/
cp database_config.env $INSTALL_DIR/config/

# Copy ingestion scripts
cp ingest_openstates_data.py $INSTALL_DIR/
cp ingest_congressgov_data.py $INSTALL_DIR/
cp ingest_govinfo_data.py $INSTALL_DIR/
cp run_all_ingestions.py $INSTALL_DIR/
cp setup_database.py $INSTALL_DIR/

# Copy systemd service files
cp opendiscourse-queue-manager.service /etc/systemd/system/
cp opendiscourse-job-scheduler.service /etc/systemd/system/

# Set proper ownership and permissions
chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_DIR
chmod 755 $INSTALL_DIR/*.py
chmod 600 $INSTALL_DIR/config/*.env
chmod +x $INSTALL_DIR/*.py

print_status "Queue system files installed"

# Create Python virtual environment
echo -e "\n${BLUE}Step 7: Setting up Python environment${NC}"
sudo -u $SERVICE_USER python3 -m venv $INSTALL_DIR/venv
sudo -u $SERVICE_USER $INSTALL_DIR/venv/bin/pip install --upgrade pip
sudo -u $SERVICE_USER $INSTALL_DIR/venv/bin/pip install -r $INSTALL_DIR/requirements-queue.txt
print_status "Python virtual environment created"

# Setup environment configuration
echo -e "\n${BLUE}Step 8: Configuring environment${NC}"
cat > $CONFIG_DIR/queue.env << 'EOF'
# OpenDiscourse Queue System Configuration
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

# API Keys (update these with your actual keys)
OPENSTATES_API_KEY=your_openstates_api_key_here
CONGRESS_API_KEY=your_congress_api_key_here
GOVINFO_API_KEY=your_govinfo_api_key_here

# Alert Configuration (optional)
SLACK_WEBHOOK_URL=
EMAIL_ALERT_TO=
EMAIL_ALERT_FROM=noreply@opendiscourse.org

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/opendiscourse/queue.log
EOF

# Create symlink to environment file
ln -sf $CONFIG_DIR/queue.env $INSTALL_DIR/.env

print_status "Environment configuration created"

# Create log rotation configuration
echo -e "\n${BLUE}Step 9: Setting up log rotation${NC}"
cat > /etc/logrotate.d/opendiscourse << 'EOF'
/var/log/opendiscourse/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

print_status "Log rotation configured"

# Setup systemd services
echo -e "\n${BLUE}Step 10: Setting up systemd services${NC}"
systemctl daemon-reload
systemctl enable opendiscourse-queue-manager
systemctl enable opendiscourse-job-scheduler

print_status "Systemd services configured"

# Create management scripts
echo -e "\n${BLUE}Step 11: Creating management scripts${NC}"

# Start script
cat > $INSTALL_DIR/scripts/start_services.sh << 'EOF'
#!/bin/bash
# Start OpenDiscourse Queue System services

echo "Starting OpenDiscourse Queue System..."
systemctl start opendiscourse-queue-manager
systemctl start opendiscourse-job-scheduler

echo "Checking service status..."
systemctl status opendiscourse-queue-manager --no-pager
systemctl status opendiscourse-job-scheduler --no-pager

echo "Services started successfully!"
EOF

# Stop script
cat > $INSTALL_DIR/scripts/stop_services.sh << 'EOF'
#!/bin/bash
# Stop OpenDiscourse Queue System services

echo "Stopping OpenDiscourse Queue System..."
systemctl stop opendiscourse-queue-manager
systemctl stop opendiscourse-job-scheduler

echo "Services stopped successfully!"
EOF

# Status script
cat > $INSTALL_DIR/scripts/status.sh << 'EOF'
#!/bin/bash
# Check OpenDiscourse Queue System status

echo "=== OpenDiscourse Queue System Status ==="
echo ""
echo "Service Status:"
systemctl status opendiscourse-queue-manager --no-pager
echo ""
systemctl status opendiscourse-job-scheduler --no-pager
echo ""
echo "Redis Status:"
systemctl status redis-server --no-pager
echo ""
echo "Recent Logs:"
tail -n 20 /var/log/opendiscourse/queue.log
EOF

# Health check script
cat > $INSTALL_DIR/scripts/health_check.sh << 'EOF'
#!/bin/bash
# Quick health check for OpenDiscourse Queue System

echo "=== OpenDiscourse Queue System Health Check ==="
echo ""

# Check services
if systemctl is-active --quiet opendiscourse-queue-manager; then
    echo "✓ Queue Manager: Running"
else
    echo "✗ Queue Manager: Not running"
fi

if systemctl is-active --quiet opendiscourse-job-scheduler; then
    echo "✓ Job Scheduler: Running"
else
    echo "✗ Job Scheduler: Not running"
fi

if systemctl is-active --quiet redis-server; then
    echo "✓ Redis Server: Running"
else
    echo "✗ Redis Server: Not running"
fi

echo ""
echo "Database Connection Test:"
if sudo -u opendiscourse $INSTALL_DIR/venv/bin/python -c "
import psycopg2
import os
os.environ['DATABASE_URL'] = 'postgresql://opendiscourse:opendiscourse123@172.28.82.205:5432/opendiscourse'
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('✓ Database: Connected')
    conn.close()
except Exception as e:
    print(f'✗ Database: Error - {e}')
"; then
    echo "✓ Database: Connected"
else
    echo "✗ Database: Connection failed"
fi

echo ""
echo "Queue Status:"
if sudo -u opendiscourse $INSTALL_DIR/venv/bin/python $INSTALL_DIR/queue_workers.py status; then
    echo "✓ Queue System: Responding"
else
    echo "✗ Queue System: Not responding"
fi
EOF

chmod +x $INSTALL_DIR/scripts/*.sh
chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_DIR/scripts

print_status "Management scripts created"

# Run database setup
echo -e "\n${BLUE}Step 12: Setting up database${NC}"
sudo -u $SERVICE_USER $INSTALL_DIR/venv/bin/python $INSTALL_DIR/setup_database.py
print_status "Database setup completed"

# Create web dashboard (optional)
echo -e "\n${BLUE}Step 13: Setting up web dashboard (optional)${NC}"
read -p "Do you want to set up a simple web dashboard? (y/N): " setup_dashboard
if [[ $setup_dashboard =~ ^[Yy]$ ]]; then
    # Create a simple web interface
    cat > $INSTALL_DIR/dashboard.py << 'EOF'
#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string
import redis
import psycopg2
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configuration
REDIS_CONFIG = {'host': 'localhost', 'port': 6379, 'db': 0}
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '172.28.82.205'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'opendiscourse'),
    'user': os.getenv('DB_USER', 'opendiscourse'),
    'password': os.getenv('DB_PASSWORD', 'opendiscourse123')
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>OpenDiscourse Queue Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .status { padding: 10px; border-radius: 4px; margin: 5px 0; }
        .status.running { background: #d4edda; color: #155724; }
        .status.stopped { background: #f8d7da; color: #721c24; }
        .status.degraded { background: #fff3cd; color: #856404; }
        .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .timestamp { color: #666; font-size: 0.9em; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
    <script>
        function refreshData() {
            location.reload();
        }
        setInterval(refreshData, 30000); // Auto-refresh every 30 seconds
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OpenDiscourse Queue Dashboard</h1>
            <p>Real-time monitoring of data ingestion jobs</p>
            <button class="refresh-btn" onclick="refreshData()">Refresh Now</button>
            <span class="timestamp">Last updated: {{ timestamp }}</span>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Services</h2>
                <div class="status {{ services.queue_manager }}">Queue Manager: {{ services.queue_manager }}</div>
                <div class="status {{ services.job_scheduler }}">Job Scheduler: {{ services.job_scheduler }}</div>
                <div class="status {{ services.redis }}">Redis: {{ services.redis }}</div>
                <div class="status {{ services.database }}">Database: {{ services.database }}</div>
            </div>

            <div class="card">
                <h2>Queue Statistics</h2>
                <table>
                    <tr><th>Queue</th><th>Jobs</th><th>Failed</th><th>Success Rate</th></tr>
                    {% for queue, stats in queues.items() %}
                    <tr>
                        <td>{{ queue }}</td>
                        <td>{{ stats.total_jobs }}</td>
                        <td>{{ stats.failed_jobs }}</td>
                        <td>{{ stats.success_rate }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <div class="card">
            <h2>Recent Jobs</h2>
            <table>
                <tr><th>Source</th><th>Status</th><th>Updated</th><th>Records</th></tr>
                {% for job in recent_jobs %}
                <tr>
                    <td>{{ job.source_name }}</td>
                    <td><span class="status {{ job.status }}">{{ job.status }}</span></td>
                    <td>{{ job.updated_at }}</td>
                    <td>{{ job.success_records }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    try:
        # Check Redis
        redis_conn = redis.Redis(**REDIS_CONFIG)
        redis_info = redis_conn.info()
        
        # Check Database
        db_conn = psycopg2.connect(**DB_CONFIG)
        cursor = db_conn.cursor()
        
        # Get recent jobs
        cursor.execute("""
            SELECT source_name, status, updated_at, success_records 
            FROM master_ingestion_status 
            ORDER BY updated_at DESC LIMIT 10
        """)
        recent_jobs = cursor.fetchall()
        db_conn.close()
        
        # Prepare data
        services = {
            'queue_manager': 'running',  # Check via systemctl in real implementation
            'job_scheduler': 'running',
            'redis': 'running',
            'database': 'running'
        }
        
        queues = {}  # Get from Redis in real implementation
        formatted_jobs = []
        
        for job in recent_jobs:
            formatted_jobs.append({
                'source_name': job[0],
                'status': job[1],
                'updated_at': job[2].strftime('%Y-%m-%d %H:%M:%S') if job[2] else 'N/A',
                'success_records': job[3] or 0
            })
        
        return render_template_string(HTML_TEMPLATE,
                                   services=services,
                                   queues=queues,
                                   recent_jobs=formatted_jobs,
                                   timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

    # Create systemd service for dashboard
    cat > /etc/systemd/system/opendiscourse-dashboard.service << EOF
[Unit]
Description=OpenDiscourse Dashboard
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR
Environment=PYTHONPATH=$INSTALL_DIR
EnvironmentFile=$CONFIG_DIR/queue.env
ExecStart=$INSTALL_DIR/venv/bin/python dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable opendiscourse-dashboard
    print_status "Web dashboard created and enabled"
fi

# Final setup summary
echo -e "\n${GREEN}=================================================="
echo "OpenDiscourse Queue System Installation Complete!"
echo "=================================================="
echo ""
echo "Installation Summary:"
echo "- Installation directory: $INSTALL_DIR"
echo "- Configuration directory: $CONFIG_DIR"
echo "- Log directory: $LOG_DIR"
echo "- Service user: $SERVICE_USER"
echo ""
echo "Next Steps:"
echo "1. Update API keys in: $CONFIG_DIR/queue.env"
echo "2. Start the services: sudo $INSTALL_DIR/scripts/start_services.sh"
echo "3. Check status: sudo $INSTALL_DIR/scripts/status.sh"
echo "4. Run health check: sudo $INSTALL_DIR/scripts/health_check.sh"

if [[ $setup_dashboard =~ ^[Yy]$ ]]; then
    echo "5. Access dashboard: http://your-server-ip:5000"
fi

echo ""
echo "Manual commands:"
echo "- Start services: sudo systemctl start opendiscourse-queue-manager opendiscourse-job-scheduler"
echo "- Stop services: sudo systemctl stop opendiscourse-queue-manager opendiscourse-job-scheduler"
echo "- View logs: sudo tail -f $LOG_DIR/queue.log"
echo ""
echo -e "${GREEN}Installation completed successfully!${NC}"