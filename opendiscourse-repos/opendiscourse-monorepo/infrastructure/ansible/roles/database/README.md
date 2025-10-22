# Database Role

This role manages database servers and services for the OpenDiscourse infrastructure, including PostgreSQL, Neo4j, and OpenSearch.

## Features

### PostgreSQL
- Installation and configuration
- Database and user management
- Extensions support (including pgvector)
- Backup and restore
- Replication setup
- Connection pooling with pgbouncer

### Neo4j
- Installation and configuration
- Database initialization
- User and role management
- Backup and restore
- APOC and GDS plugins

### OpenSearch
- Cluster setup
- Index templates
- Snapshot repositories
- Security configuration
- Performance tuning

## Requirements

- Docker role (for containerized deployment)
- Common role (for system configuration)
- Sufficient disk space for databases
- Appropriate system resources (CPU, RAM)

## Role Variables

### PostgreSQL Variables

```yaml
postgresql_enabled: true
postgresql_version: "14"
postgresql_data_dir: "/var/lib/postgresql/data"
postgresql_conf:
  max_connections: "100"
  shared_buffers: "1GB"
  effective_cache_size: "3GB"
postgresql_users:
  - name: "app_user"
    password: "{{ vault_postgres_password }}"
    databases: ["app_db"]
    priv: "ALL"
postgresql_databases:
  - name: "app_db"
    encoding: "UTF8"
    collation: "en_US.UTF-8"
    template: "template0"
```

### Neo4j Variables

```yaml
neo4j_enabled: true
neo4j_edition: "enterprise"
neo4j_version: "4.4"
neo4j_password: "{{ vault_neo4j_password }}"
neo4j_memory:
  heap_initial_size: "1G"
  heap_max_size: "2G"
  pagecache_size: "1G"
```

### OpenSearch Variables

```yaml
opensearch_enabled: true
opensearch_version: "2.8"
opensearch_cluster_name: "opendiscourse"
opensearch_node_roles: ["data", "master"]
opensearch_network_host: "0.0.0.0"
opensearch_initial_master_nodes: ["opensearch-node-1"]
opensearch_plugins: ["repository-s3"]
```

## Dependencies

- docker
- common

## Example Playbook

```yaml
- hosts: database_servers
  become: true
  roles:
    - role: database
      vars:
        postgresql_enabled: true
        neo4j_enabled: true
        opensearch_enabled: true
        postgresql_users:
          - name: "app_user"
            password: "{{ vault_postgres_password }}"
            databases: ["app_db"]
        neo4j_password: "{{ vault_neo4j_password }}"
```

## Configuration

### PostgreSQL Configuration

- Data directory: `/var/lib/postgresql/data`
- Configuration: `/etc/postgresql/{version}/main/postgresql.conf`
- Authentication: `/etc/postgresql/{version}/main/pg_hba.conf`
- Extensions: pgvector, pg_stat_statements, etc.

### Neo4j Configuration

- Data directory: `/var/lib/neo4j/data`
- Configuration: `/etc/neo4j/neo4j.conf`
- Plugins: APOC, Graph Data Science
- Memory settings tuned for available system resources

### OpenSearch Configuration

- Data directory: `/var/lib/opensearch`
- Configuration: `/etc/opensearch/opensearch.yml`
- JVM options: `/etc/opensearch/jvm.options`
- Security: TLS, user authentication

## Backup and Recovery

### PostgreSQL

```bash
# Backup
pg_dump -U postgres -d dbname > backup.sql

# Restore
psql -U postgres -d dbname < backup.sql
```

### Neo4j

```bash
# Backup
neo4j-admin backup --backup-dir=/backups --name=neo4j_backup

# Restore
neo4j-admin restore --from=/backups/neo4j_backup --database=neo4j --force
```

### OpenSearch

```bash
# Create snapshot repository
PUT /_snapshot/backup
{
  "type": "fs",
  "settings": {
    "location": "/backups/opensearch"
  }
}

# Create snapshot
PUT /_snapshot/backup/snapshot_1?wait_for_completion=true
```

## Security

- Encrypted connections (TLS)
- Role-based access control
- Network isolation
- Regular security updates
- Audit logging

## Monitoring

- Prometheus metrics endpoints
- Log aggregation with Loki
- Alerting rules
- Performance dashboards

## Tags

- `postgresql`: PostgreSQL tasks
- `neo4j`: Neo4j tasks
- `opensearch`: OpenSearch tasks
- `database:backup`: Backup tasks
- `database:restore`: Restore tasks
- `database:config`: Configuration tasks

## License

Proprietary - All rights reserved
