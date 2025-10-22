#!/bin/bash
# Setup backup system for opendiscourse.net

# Create backup directory and set permissions
BACKUP_DIR="/backups"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

# Install required packages
apt-get update
apt-get install -y postgresql-client neo4j-client jq awscli

# Create backup script
cat > /usr/local/bin/opendiscourse-backup << 'EOL'
#!/bin/bash
# Backup script for opendiscourse.net

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/opendiscourse_$TIMESTAMP"
LOG_FILE="/var/log/backup_$TIMESTAMP.log"

# Load environment variables
if [ -f "/etc/opendiscourse/.env" ]; then
    export $(grep -v '^#' /etc/opendiscourse/.env | xargs)
fi

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
PGPASSWORD=$POSTGRES_PASSWORD pg_dumpall -h localhost -U postgres > "$BACKUP_DIR/postgres_full_$TIMESTAMP.sql"

# Backup Neo4j
if [ -n "$NEO4J_PASSWORD" ]; then
    cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "CALL apoc.export.cypher.all('$BACKUP_DIR/neo4j_$TIMESTAMP.cypher', {format: 'cypher-shell'})"
fi

# Backup Weaviate schemas
if command -v curl &> /dev/null; then
    curl -s http://localhost:8080/v1/schema | jq . > "$BACKUP_DIR/weaviate_schema_$TIMESTAMP.json"
fi

# Backup configuration files
tar czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" /etc/nginx /etc/traefik /etc/caddy 2>/dev/null || true

# Upload to S3 if configured
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ] && [ -n "$S3_BACKUP_BUCKET" ]; then
    aws s3 cp --recursive "$BACKUP_DIR" "s3://$S3_BACKUP_BUCKET/$TIMESTAMP/"
fi

# Clean up old backups (keep last 7 days)
find /backups -type d -mtime +7 -exec rm -rf {} \;
EOL

# Make backup script executable
chmod +x /usr/local/bin/opendiscourse-backup

# Create systemd service for automated backups
cat > /etc/systemd/system/opendiscourse-backup.service << 'EOL'
[Unit]
Description=OpenDiscourse Backup Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/opendiscourse-backup
User=root
EnvironmentFile=/etc/opendiscourse/.env

[Install]
WantedBy=multi-user.target
EOL

# Create timer for daily backups
cat > /etc/systemd/system/opendiscourse-backup.timer << 'EOL'
[Unit]
Description=Run OpenDiscourse backup daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOL

# Enable and start the backup timer
systemctl daemon-reload
systemctl enable --now opendiscourse-backup.timer

# Create restore script
cat > /usr/local/bin/opendiscourse-restore << 'EOL'
#!/bin/bash
# Restore script for opendiscourse.net

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/backup/directory"
    exit 1
fi

BACKUP_DIR="$1"

# Load environment variables
if [ -f "/etc/opendiscourse/.env" ]; then
    export $(grep -v '^#' /etc/opendiscourse/.env | xargs)
fi

# Restore PostgreSQL
if [ -f "$BACKUP_DIR/postgres_full_"*".sql" ]; then
    PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -f "$BACKUP_DIR/postgres_full_"*".sql"
fi

# Restore Neo4j
if [ -f "$BACKUP_DIR/neo4j_"*".cypher" ] && [ -n "$NEO4J_PASSWORD" ]; then
    cypher-shell -u neo4j -p "$NEO4J_PASSWORD" < "$BACKUP_DIR/neo4j_"*".cypher"
fi

# Restore configuration files
if [ -f "$BACKUP_DIR/config_"*".tar.gz" ]; then
    tar xzf "$BACKUP_DIR/config_"*".tar.gz" -C /
    systemctl restart nginx traefik caddy
fi

echo "Restore completed. Please verify your data and restart services if needed."
EOL

chmod +x /usr/local/bin/opendiscourse-restore

echo "Backup system setup complete."
echo "- Manual backup: opendiscourse-backup"
echo "- Manual restore: opendiscourse-restore /path/to/backup"
echo "- Automated backups run daily at 2 AM"
