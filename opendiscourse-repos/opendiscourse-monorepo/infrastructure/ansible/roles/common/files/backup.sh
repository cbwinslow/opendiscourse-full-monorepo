#!/bin/bash
# Backup script for opendiscourse.net

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/opendiscourse_$TIMESTAMP"
LOG_FILE="/var/log/backup_$TIMESTAMP.log"

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
docker exec postgres pg_dumpall -U postgres > "$BACKUP_DIR/postgres_full_$TIMESTAMP.sql"

# Backup Neo4j
docker exec neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "CALL apoc.export.cypher.all('$BACKUP_DIR/neo4j_$TIMESTAMP.cypher', {format: 'cypher-shell'});"

# Backup Weaviate
docker exec weaviate curl -X GET "localhost:8080/v1/backup" > "$BACKUP_DIR/weaviate_backup_$TIMESTAMP.json"

# Backup configuration files
tar czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" /etc/nginx /etc/traefik /etc/caddy

# Upload to remote storage (example with S3)
aws s3 cp --recursive "$BACKUP_DIR" "s3://opendiscourse-backups/$TIMESTAMP/"

# Clean up old backups (keep last 7 days)
find /backups -type d -mtime +7 -exec rm -rf {} \;
