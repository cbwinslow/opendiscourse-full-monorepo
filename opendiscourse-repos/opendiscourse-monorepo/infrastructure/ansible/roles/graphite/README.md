# Graphite Role

This role installs and configures Graphite, a real-time graphing system, for the OpenDiscourse platform.

## Features

- Graphite-web installation and configuration
- Carbon (cache and relay) setup
- Whisper database configuration
- StatsD integration
- Grafana integration
- Authentication and authorization
- Data retention policies
- Monitoring and alerting
- Backup and restore

## Requirements

- Python 3.6+
- PostgreSQL or SQLite
- Redis (for caching)
- Minimum 4GB RAM (8GB+ recommended for production)
- Sufficient disk space for time-series data
- Ports: 80/443 (HTTP/HTTPS), 2003-2004 (Carbon), 8125 (StatsD), 8126 (StatsD admin)

## Role Variables

### Required Variables

```yaml
# Core Configuration
graphite_enabled: true
graphite_version: "1.1.10"
graphite_timezone: "UTC"

# Database Configuration
graphite_database:
  engine: "postgresql"  # or "sqlite3"
  name: "graphite"
  user: "graphite"
  password: "{{ vault_graphite_db_password }}"
  host: "localhost"
  port: 5432

# Secret Key
graphite_secret_key: "{{ vault_graphite_secret_key }}"

# Admin User
graphite_admin_user: "admin"
graphite_admin_email: "admin@example.com"
graphite_admin_password: "{{ vault_graphite_admin_password }}"
```

### Optional Variables

```yaml
# Web Server
graphite_web:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  log_level: "INFO"
  timezone: "UTC"
  memcached_servers: ["localhost:11211"]

# Carbon Cache
carbon_cache:
  enabled: true
  max_cache_size: "inf"
  max_updates_per_second: 500
  max_creates_per_minute: 50
  line_receiver_interface: "0.0.0.0"
  line_receiver_port: 2003
  pickle_receiver_interface: "0.0.0.0"
  pickle_receiver_port: 2004
  cache_query_interface: "0.0.0.0"
  cache_query_port: 7002

# Carbon Relay
carbon_relay:
  enabled: false
  relay_method: "consistent-hashing"
  destinations: []
  replication_factor: 1
  max_datapoints_per_message: 500
  max_queue_size: 10000

# StatsD
statsd:
  enabled: true
  host: "0.0.0.0"
  port: 8125
  admin_interface: "0.0.0.0"
  admin_port: 8126
  flush_interval: 10000
  percent_threshold: [90]

# Storage Schemas
storage_schemas:
  - name: "carbon"
    pattern: "^carbon\."
    retentions: "60s:90d"
  - name: "default"
    pattern: ".*"
    retentions: "10s:6h,1m:7d,10m:5y"

# Storage Aggregation
storage_aggregation:
  - pattern: "\.min$"
    x_files_factor: 0.1
    aggregation_method: "min"
  - pattern: "\.max$"
    x_files_factor: 0.1
    aggregation_method: "max"
  - pattern: "\.count$"
    x_files_factor: 0
    aggregation_method: "sum"
  - pattern: "\.avg$"
    x_files_factor: 0.1
    aggregation_method: "average"

# Authentication
graphite_auth:
  enabled: true
  backend: "django.contrib.auth.backends.ModelBackend"
  ldap_enabled: false
  ldap_uri: "ldap://ldap.example.com"
  ldap_bind_dn: ""
  ldap_bind_password: ""
  ldap_user_search_base: "ou=users,dc=example,dc=com"
  ldap_user_search_filter: "(uid=%(user)s)"

# Monitoring
graphite_monitoring:
  enabled: true
  carbon_metrics_enabled: true
  statsd_metrics_enabled: true
  collectd_metrics_enabled: false
  node_exporter_metrics_enabled: true

# Backup
graphite_backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention_days: 30
  target: "local"  # local, s3, gcs
  s3_bucket: ""
  s3_path: "backups/graphite/"
```

## Dependencies

- python3
- postgresql (or sqlite3)
- redis
- nginx (recommended)
- memcached (recommended)

## Example Playbook

```yaml
- hosts: graphite_servers
  become: true
  roles:
    - role: graphite
      vars:
        graphite_enabled: true
        graphite_version: "1.1.10"
        
        graphite_database:
          engine: "postgresql"
          name: "graphite"
          user: "graphite"
          password: "{{ vault_graphite_db_password }}"
          host: "localhost"
          port: 5432
        
        graphite_admin_user: "admin"
        graphite_admin_email: "admin@example.com"
        graphite_admin_password: "{{ vault_graphite_admin_password }}"
        
        graphite_web:
          host: "0.0.0.0"
          port: 8000
          workers: 4
        
        carbon_cache:
          enabled: true
          max_cache_size: "8g"
        
        statsd:
          enabled: true
          host: "0.0.0.0"
          port: 8125
```

## Configuration

### File Structure

```
/opt/graphite/
├── bin/                     # Scripts and binaries
├── conf/                    # Configuration files
│   ├── carbon.conf          # Carbon daemon configuration
│   ├── storage-schemas.conf # Retention policies
│   ├── storage-aggregation.conf # Aggregation rules
│   ├── graphite.wsgi        # WSGI application
│   └── graphite_local_settings.py # Local settings
├── lib/                    # Python libraries
├── log/                    # Log files
│   ├── carbon-cache/
│   ├── carbon-relay/
│   ├── statsd/
│   └── webapp/
├── storage/                # Whisper database files
│   ├── whisper/
│   └── lists/
└── webapp/                 # Graphite web application
```

### Data Retention

Configured in `storage-schemas.conf`:

```
[carbon]
pattern = ^carbon\\.
retentions = 60s:90d

[default]
pattern = .*
retentions = 10s:6h,1m:7d,10m:5y
```

### Aggregation

Configured in `storage-aggregation.conf`:

```
[min]
pattern = \\.min$
xFilesFactor = 0.1
aggregationMethod = min

[max]
pattern = \\.max$
xFilesFactor = 0.1
aggregationMethod = max

[default_average]
pattern = .*
xFilesFactor = 0.3
aggregationMethod = average
```

## Integration

### StatsD

```javascript
// Example Node.js application
const StatsD = require('node-statsd');
const client = new StatsD({
  host: 'graphite.example.com',
  port: 8125,
  prefix: 'myapp.'
});

// Increment a counter
client.increment('page.views');

// Record timing
const start = new Date();
// ... do work ...
client.timing('page.render', new Date() - start);

// Record a gauge
client.gauge('users.online', 42);
```

### Carbon

Plaintext protocol (port 2003):
```
echo "myapp.page.views 1 $(date +%s)" | nc -q0 graphite.example.com 2003
```

Pickle protocol (port 2004):
```python
import pickle
import socket
import time

metrics = [
    ('myapp.page.views', (int(time.time()), 1)),
    ('myapp.response.time', (int(time.time()), 42.5))
]

payload = pickle.dumps(metrics, protocol=2)
header = struct.pack("!L", len(payload))
message = header + payload

sock = socket.socket()
sock.connect(('graphite.example.com', 2004))
sock.sendall(message)
sock.close()
```

## Security

### Authentication

- Built-in user authentication
- LDAP/Active Directory integration
- API key authentication
- Rate limiting

### Network Security

- Firewall rules
- TLS/SSL encryption
- IP whitelisting
- Request validation

## Monitoring

### Built-in Metrics

- Carbon metrics (cache size, updates, etc.)
- StatsD metrics
- System metrics (CPU, memory, disk, etc.)
- Application metrics

### Integration

- Grafana dashboards
- Prometheus metrics
- Alerting rules
- Log aggregation

## Backup and Recovery

### Data Backup

```bash
# Backup Whisper files
rsync -avz /opt/graphite/storage/whisper/ /backup/graphite/whisper/

# Backup PostgreSQL database
pg_dump -U graphite -d graphite > /backup/graphite/graphite_$(date +%Y%m%d).sql

# Backup configuration
rsync -avz /opt/graphite/conf/ /backup/graphite/conf/
```

### Restoration

```bash
# Restore Whisper files
rsync -avz /backup/graphite/whisper/ /opt/graphite/storage/whisper/

# Restore PostgreSQL database
dropdb -U graphite graphite
createdb -U graphite graphite
psql -U graphite -d graphite < /backup/graphite/graphite_20230101.sql

# Restore configuration
rsync -avz /backup/graphite/conf/ /opt/graphite/conf/
```

## Scaling

### Vertical Scaling

- Increase CPU/memory resources
- Optimize storage performance
- Tune cache settings

### Horizontal Scaling

- Deploy multiple Carbon caches
- Use Carbon relay for load balancing
- Shard metrics across multiple servers
- Implement high availability

## Tags

- `graphite:install`: Installation tasks
- `graphite:config`: Configuration tasks
- `graphite:carbon`: Carbon setup
- `graphite:web`: Web interface setup
- `graphite:statsd`: StatsD setup
- `graphite:backup`: Backup configuration
- `graphite:monitoring`: Monitoring setup

## License

Proprietary - All rights reserved
