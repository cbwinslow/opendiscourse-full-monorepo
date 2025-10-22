#!/bin/bash
# Restore script for opendiscourse.net

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/backup/directory"
    exit 1
fi

BACKUP_DIR="$1"
LOG_FILE="/var/log/restore_$(date +%Y%m%d_%H%M%S).log"

# Restore PostgreSQL
if [ -f "$BACKUP_DIR/postgres_full_"*".sql" ]; then
    cat "$BACKUP_DIR/postgres_full_"*".sql" | docker exec -i postgres psql -U postgres
fi

# Restore Neo4j
if [ -f "$BACKUP_DIR/neo4j_"*".cypher" ]; then
    docker exec -i neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" < "$BACKUP_DIR/neo4j_"*".cypher"
fi

# Restore Weaviate
if [ -f "$BACKUP_DIR/weaviate_backup_"*".json" ]; then
    docker exec weaviate curl -X POST "localhost:8080/v1/restore" -H "Content-Type: application/json" -d @"$BACKUP_DIR/weaviate_backup_"*".json"
fi

# Restore configuration files
if [ -f "$BACKUP_DIR/config_"*".tar.gz" ]; then
    tar xzf "$BACKUP_DIR/config_"*".tar.gz" -C /
    # Restart services to apply configuration
    systemctl restart nginx
    systemctl restart traefik
    systemctl restart caddy
fi
