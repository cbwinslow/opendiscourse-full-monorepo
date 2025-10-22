# Neo4j Role

This role installs and configures Neo4j, a graph database management system, for the OpenDiscourse platform.

## Features

- Neo4j Community or Enterprise Edition installation
- Single instance or cluster deployment
- Memory and performance optimization
- Backup and restore functionality
- User and role management
- APOC and GDS plugin support
- SSL/TLS configuration
- Monitoring and metrics
- Backup and restore procedures

## Requirements

- Java 11 or later
- Minimum 2GB RAM (8GB+ recommended for production)
- Sufficient disk space for database files
- Ports: 7474 (HTTP), 7473 (HTTPS), 7687 (Bolt), 5000 (Backup)

## Role Variables

### Required Variables

```yaml
# Core Configuration
neo4j_edition: "enterprise"  # or "community"
neo4j_version: "5.12.0"
neo4j_password: "{{ vault_neo4j_password }}"

# Network Configuration
neo4j_http_port: 7474
neo4j_https_port: 7473
neo4j_bolt_port: 7687
neo4j_backup_port: 5000

# Memory Configuration
neo4j_memory_heap_initial_size: "1G"
neo4j_memory_heap_max_size: "4G"
neo4j_memory_pagecache_size: "2G"
```

### Optional Variables

```yaml
# Authentication
neo4j_auth_enabled: true
neo4j_auth_realm: "native"

# Clustering (Enterprise only)
neo4j_mode: "SINGLE"  # SINGLE, CORE, or READ_REPLICA
neo4j_initial_members: ""
neo4j_discovery_type: "LIST"
neo4j_raft_advertised_address: ""

# Backup Configuration
neo4j_backup_enabled: true
neo4j_backup_path: "/var/lib/neo4j/backups"
neo4j_backup_retention_days: 7

# SSL Configuration
neo4j_ssl_policy: "https"  # https, bolt, cluster, backup, or ha
neo4j_ssl_certificate: ""
neo4j_ssl_private_key: ""
neo4j_ssl_trusted_certificates: []

# Plugins
neo4j_plugins:
  - apoc
  - graph-data-science
  - apoc-extended
  - n10s

# APOC Configuration
neo4j_apoc_export_file_enabled: true
neo4j_apoc_import_file_enabled: true
neo4j_apoc_import_file_use_neo4j_config: true

# Monitoring
neo4j_metrics_enabled: true
neo4j_metrics_csv_enabled: true
neo4j_metrics_prometheus_enabled: true
neo4j_metrics_prometheus_endpoint: "/metrics"
```

## Dependencies

- java (installed by the role)
- systemd (for service management)

## Example Playbook

```yaml
- hosts: neo4j_servers
  become: true
  roles:
    - role: neo4j
      vars:
        neo4j_edition: "enterprise"
        neo4j_version: "5.12.0"
        neo4j_password: "{{ vault_neo4j_password }}"
        neo4j_memory_heap_max_size: "8G"
        neo4j_memory_pagecache_size: "4G"
        neo4j_plugins:
          - apoc
          - graph-data-science
        neo4j_metrics_prometheus_enabled: true
```

## Configuration

### File Locations

- Configuration: `/etc/neo4j/neo4j.conf`
- Logs: `/var/log/neo4j/`
- Data: `/var/lib/neo4j/data`
- Certificates: `/var/lib/neo4j/certificates`
- Plugins: `/var/lib/neo4j/plugins`
- Metrics: `/var/lib/neo4j/metrics`

### Memory Configuration

Memory settings are critical for performance. The main settings are:

- `dbms.memory.heap.initial_size`: Initial heap size
- `dbms.memory.heap.max_size`: Maximum heap size
- `dbms.memory.pagecache.size`: Page cache size

As a rule of thumb:
- Heap size: 50% of available RAM, up to 32GB
- Page cache: 50% of available RAM, minus heap size
- Leave some RAM for the OS and filesystem cache

### Plugins

Commonly used plugins:

1. **APOC** (Awesome Procedures On Cypher)
   - Provides hundreds of procedures and functions
   - Data import/export, graph algorithms, utilities

2. **Graph Data Science**
   - Graph algorithms (PageRank, Louvain, etc.)
   - Machine learning pipelines
   - Graph embeddings

3. **n10s**
   - RDF and semantic web support
   - SPARQL to Cypher translation

## Security

### Authentication

- Password policies
- Role-based access control (RBAC)
- LDAP/Active Directory integration
- Kerberos support

### Encryption

- Encrypted connections (TLS/SSL)
- Encrypted backups
- Encrypted data at rest (Enterprise)

### Network

- Firewall rules
- IP whitelisting
- Reverse proxy configuration

## Backup and Recovery

### Full Backup

```bash
# Create backup
neo4j-admin database backup neo4j --to-path=/backups/neo4j_backup_$(date +%Y%m%d)

# Restore from backup
neo4j-admin database restore --from-path=/backups/neo4j_backup_20230101 neo4j
```

### Online Backup (Enterprise)

```bash
# Create online backup
neo4j-admin database backup --name=backup --to-path=/backups --database=neo4j

# Restore from online backup
neo4j-admin database restore --from-path=/backups/backup --database=neo4j --force
```

### Dump/Load

```bash
# Dump database
neo4j-admin database dump neo4j --to-path=/backups/neo4j.dump

# Load dump
neo4j-admin database load --from-path=/backups/neo4j.dump --database=neo4j
```

## Monitoring

### Built-in Metrics

- JVM metrics
- Database metrics
- Transaction metrics
- Page cache metrics
- Bolt metrics

### Integration

- Prometheus endpoint
- JMX metrics
- Log files
- Query logging

## Performance Tuning

1. **Indexes**
   - Create appropriate indexes for frequently queried properties
   - Use composite indexes for multiple properties
   - Monitor index usage

2. **Query Optimization**
   - Use `EXPLAIN` and `PROFILE` to analyze queries
   - Avoid cartesian products
   - Use parameters instead of literals

3. **Memory**
   - Tune heap and page cache sizes
   - Monitor garbage collection
   - Configure off-heap memory for large result sets

## High Availability (Enterprise)

### Causal Cluster

- Deploy multiple instances
- Automatic failover
- Load balancing
- Read replicas

### Configuration

```properties
# Core server
dbms.mode=CORE
dbms.clustering.raft.advertised_address=:7000
dbms.clustering.raft.listen_address=:7000

# Read replica
dbms.mode=READ_REPLICA
dbms.clustering.raft.advertised_address=:7001
dbms.clustering.raft.listen_address=:7001
```

## Tags

- `neo4j:install`: Installation tasks
- `neo4j:config`: Configuration tasks
- `neo4j:plugins`: Plugin management
- `neo4j:backup`: Backup tasks
- `neo4j:security`: Security configuration
- `neo4j:monitoring`: Monitoring setup

## License

Proprietary - All rights reserved
