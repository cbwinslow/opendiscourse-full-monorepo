# OpenDiscourse Role

This role deploys and configures the OpenDiscourse application, a platform for analyzing political documentation.

## Features

- OpenDiscourse application deployment
- Database setup and migrations
- Background workers
- Caching layer
- Search integration
- File storage
- Email delivery
- Monitoring and logging
- Backup and restore
- Environment-specific configurations

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Elasticsearch/OpenSearch 7.10+ (optional)
- Minimum 8GB RAM (16GB+ recommended for production)
- Ports: 8000 (API), 3000 (Web UI), 9000 (Worker)

## Role Variables

### Required Variables

```yaml
# Core Configuration
opendiscourse_enabled: true
opendiscourse_version: "1.0.0"
opendiscourse_environment: "production"
opendiscourse_secret_key: "{{ vault_opendiscourse_secret_key }}"
opendiscourse_allowed_hosts: ["example.com"]
opendiscourse_admin_email: "admin@example.com"

# Database Configuration
opendiscourse_database:
  engine: "postgresql"
  name: "opendiscourse"
  user: "opendiscourse"
  password: "{{ vault_opendiscourse_db_password }}"
  host: "localhost"
  port: 5432

# Redis Configuration
opendiscourse_redis:
  host: "localhost"
  port: 6379
  password: "{{ vault_redis_password }}"
  db: 0

# Storage Configuration
opendiscourse_storage:
  type: "local"  # local, s3, gcs
  path: "/var/lib/opendiscourse/media"
  s3_bucket: ""
  s3_region: "us-east-1"
  s3_access_key: "{{ vault_s3_access_key }}"
  s3_secret_key: "{{ vault_s3_secret_key }}"
```

### Optional Variables

```yaml
# Web Server Configuration
opendiscourse_web:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  threads: 2
  log_level: "info"
  timeout: 120

# Celery Workers
opendiscourse_workers:
  enabled: true
  count: 4
  concurrency: 2
  log_level: "info"
  beat_enabled: true

# Search Configuration
opendiscourse_search:
  enabled: true
  engine: "opensearch"  # opensearch, elasticsearch, none
  hosts: ["http://localhost:9200"]
  index_prefix: "opendiscourse"
  username: ""
  password: ""

# Email Configuration
opendiscourse_email:
  backend: "smtp"  # smtp, console, file, dummy
  host: "smtp.example.com"
  port: 587
  use_tls: true
  username: "noreply@example.com"
  password: "{{ vault_email_password }}"
  from: "OpenDiscourse <noreply@example.com>"

# Authentication
opendiscourse_auth:
  registration_enabled: true
  email_verification: true
  password_reset_timeout: 86400  # 24 hours
  oauth_providers: []  # List of OAuth providers

# API Configuration
opendiscourse_api:
  default_page_size: 20
  max_page_size: 100
  throttle_anon: "100/day"
  throttle_user: "1000/day"

# Monitoring
opendiscourse_monitoring:
  prometheus_enabled: true
  sentry_dsn: ""
  log_level: "info"
  log_format: "json"

# Backup
opendiscourse_backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention_days: 30
  target: "local"  # local, s3, gcs
  s3_bucket: ""
  s3_path: "backups/opendiscourse/"
```

## Dependencies

- python3
- postgresql
- redis
- nginx (recommended)
- opensearch/elasticsearch (optional)

## Example Playbook

```yaml
- hosts: opendiscourse_servers
  become: true
  roles:
    - role: opendiscourse
      vars:
        opendiscourse_enabled: true
        opendiscourse_version: "1.0.0"
        opendiscourse_environment: "production"
        opendiscourse_secret_key: "{{ vault_opendiscourse_secret_key }}"
        
        opendiscourse_database:
          name: "opendiscourse"
          user: "opendiscourse"
          password: "{{ vault_opendiscourse_db_password }}"
          host: "localhost"
          port: 5432
        
        opendiscourse_redis:
          host: "localhost"
          port: 6379
          password: "{{ vault_redis_password }}"
        
        opendiscourse_storage:
          type: "local"
          path: "/var/lib/opendiscourse/media"
        
        opendiscourse_web:
          host: "0.0.0.0"
          port: 8000
          workers: 4
        
        opendiscourse_workers:
          enabled: true
          count: 4
          concurrency: 2
```

## Configuration

### File Structure

```
/opt/opendiscourse/
├── bin/                     # Scripts and binaries
├── config/                  # Configuration files
│   ├── settings/            # Django settings
│   │   ├── base.py          # Base settings
│   │   ├── production.py    # Production settings
│   │   └── development.py   # Development settings
│   ├── gunicorn.conf.py     # Gunicorn configuration
│   └── celery.py            # Celery configuration
├── logs/                    # Log files
│   ├── gunicorn/
│   ├── celery/
│   └── django/
├── media/                   # User-uploaded files
│   ├── documents/
│   └── exports/
├── static/                  # Static files
│   ├── css/
│   ├── js/
│   └── images/
└── venv/                    # Python virtual environment
```

### Environment Variables

Key environment variables:

- `DJANGO_SETTINGS_MODULE`: Django settings module (e.g., "config.settings.production")
- `DATABASE_URL`: Database connection URL
- `REDIS_URL`: Redis connection URL
- `SECRET_KEY`: Secret key for cryptographic signing
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DEBUG`: Enable debug mode (True/False)
- `EMAIL_*`: Email configuration
- `AWS_*`: AWS S3 configuration (if using S3 storage)

## Deployment

### Initial Setup

1. Install dependencies:
   ```bash
   apt-get update
   apt-get install -y python3 python3-pip python3-venv postgresql redis-server
   ```

2. Create database and user:
   ```sql
   CREATE DATABASE opendiscourse;
   CREATE USER opendiscourse WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE opendiscourse TO opendiscourse;
   ```

3. Deploy application:
   ```bash
   ansible-playbook -i production site.yml --tags opendiscourse
   ```

4. Run migrations:
   ```bash
   cd /opt/opendiscourse
   source venv/bin/activate
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

5. Start services:
   ```bash
   systemctl start opendiscourse-web
   systemctl start opendiscourse-worker
   systemctl start opendiscourse-beat
   ```

### Upgrading

1. Pull latest changes:
   ```bash
   cd /opt/opendiscourse
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. Restart services:
   ```bash
   systemctl restart opendiscourse-web
   systemctl restart opendiscourse-worker
   systemctl restart opendiscourse-beat
   ```

## Security

### Authentication

- Built-in user authentication
- OAuth 2.0 and OpenID Connect support
- Two-factor authentication
- Password policies
- Session security

### Data Protection

- Encryption at rest
- Secure communication (HTTPS)
- Input validation
- CSRF protection
- XSS protection
- SQL injection protection
- Clickjacking protection
- Security headers

## Monitoring

### Built-in Metrics

- Request/response metrics
- Error rates
- Performance metrics
- Background job metrics
- Database query metrics
- Cache metrics

### Integration

- Prometheus metrics endpoint
- Grafana dashboards
- Sentry integration
- Log aggregation
- Alerting rules

## Backup and Recovery

### Data Backup

```bash
# Database backup
pg_dump -U opendiscourse -d opendiscourse > /backup/opendiscourse_$(date +%Y%m%d).sql

# Media files backup
rsync -avz /opt/opendiscourse/media/ /backup/opendiscourse/media/

# Configuration backup
rsync -avz /opt/opendiscourse/config/ /backup/opendiscourse/config/
```

### Restoration

```bash
# Restore database
dropdb -U opendiscourse opendiscourse
createdb -U opendiscourse opendiscourse
psql -U opendiscourse -d opendiscourse < /backup/opendiscourse_20230101.sql

# Restore media files
rsync -avz /backup/opendiscourse/media/ /opt/opendiscourse/media/

# Restore configuration
rsync -avz /backup/opendiscourse/config/ /opt/opendiscourse/config/
```

## Scaling

### Vertical Scaling

- Increase CPU/memory resources
- Optimize database performance
- Tune cache settings
- Enable query caching

### Horizontal Scaling

- Deploy multiple application servers
- Use a load balancer
- Database read replicas
- Cache cluster
- Background worker scaling

## Tags

- `opendiscourse:install`: Installation tasks
- `opendiscourse:config`: Configuration tasks
- `opendiscourse:web`: Web server setup
- `opendiscourse:worker`: Background worker setup
- `opendiscourse:db`: Database setup
- `opendiscourse:backup`: Backup configuration
- `opendiscourse:monitoring`: Monitoring setup

## License

Proprietary - All rights reserved
