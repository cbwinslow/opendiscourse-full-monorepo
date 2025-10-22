# Langfuse Role

This role deploys and configures Langfuse, an open-source observability and analytics platform for LLM applications, for the OpenDiscourse platform.

## Features

- Langfuse server deployment
- PostgreSQL database setup
- Redis caching layer
- S3-compatible storage for artifacts
- Authentication and user management
- Integration with monitoring stack
- Backup and restore functionality
- Environment-specific configurations
- Health checks and monitoring
- Secure configuration management

## Requirements

- Docker and Docker Compose
- PostgreSQL 13+
- Redis 6+
- S3-compatible storage (MinIO, AWS S3, etc.)
- Minimum 4GB RAM (8GB+ recommended)
- Ports: 3000 (Web UI), 3001 (API), 3002 (Ingestion)

## Role Variables

### Required Variables

```yaml
# Core Configuration
langfuse_enabled: true
langfuse_version: "latest"
langfuse_secret: "{{ vault_langfuse_secret }}"
langfuse_salt_rounds: 10

# Database Configuration
langfuse_database:
  host: "postgres"
  port: 5432
  name: "langfuse"
  user: "langfuse"
  password: "{{ vault_langfuse_db_password }}"

# Redis Configuration
langfuse_redis:
  host: "redis"
  port: 6379
  password: "{{ vault_redis_password }}"

# Storage Configuration (S3)
langfuse_storage:
  provider: "s3"
  endpoint: "https://s3.example.com"
  region: "us-east-1"
  bucket: "langfuse"
  access_key: "{{ vault_s3_access_key }}"
  secret_key: "{{ vault_s3_secret_key }}"
```

### Optional Variables

```yaml
# Authentication
langfuse_auth:
  enabled: true
  admin_email: "admin@example.com"
  admin_password: "{{ vault_langfuse_admin_password }}"
  oauth_providers: []  # List of OAuth providers

# API Configuration
langfuse_api:
  host: "0.0.0.0"
  port: 3001
  environment: "production"
  log_level: "info"

# Web UI Configuration
langfuse_web:
  enabled: true
  port: 3000
  public_url: "https://langfuse.example.com"
  disable_signup: false

# Ingestion API
langfuse_ingestion:
  port: 3002
  batch_size: 100
  batch_timeout: 5

# Monitoring
langfuse_monitoring:
  prometheus_enabled: true
  sentry_dsn: ""
  datadog_enabled: false
  datadog_agent_host: ""

# Rate Limiting
langfuse_rate_limit:
  enabled: true
  window_ms: 60000
  max_requests: 1000

# CORS
langfuse_cors:
  allowed_origins: ["*"]
  allowed_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
  allowed_headers: ["*"]
  allow_credentials: true
```

## Dependencies

- docker
- postgresql (or external PostgreSQL service)
- redis (or external Redis service)
- object storage (S3-compatible)

## Example Playbook

```yaml
- hosts: langfuse_servers
  become: true
  roles:
    - role: langfuse
      vars:
        langfuse_enabled: true
        langfuse_version: "latest"
        langfuse_secret: "{{ vault_langfuse_secret }}"
        
        langfuse_database:
          host: "postgres"
          name: "langfuse"
          user: "langfuse"
          password: "{{ vault_langfuse_db_password }}"
        
        langfuse_redis:
          host: "redis"
          password: "{{ vault_redis_password }}"
        
        langfuse_storage:
          provider: "s3"
          endpoint: "{{ s3_endpoint }}"
          bucket: "langfuse"
          access_key: "{{ vault_s3_access_key }}"
          secret_key: "{{ vault_s3_secret_key }}"
        
        langfuse_auth:
          admin_email: "admin@example.com"
          admin_password: "{{ vault_langfuse_admin_password }}"
        
        langfuse_web:
          public_url: "https://langfuse.example.com"
```

## Configuration

### File Structure

```
/opt/langfuse/
├── docker-compose.yml
├── .env
├── config/
│   ├── nginx/
│   │   └── nginx.conf
│   └── prometheus/
│       └── prometheus.yml
├── data/
│   ├── postgres/
│   └── redis/
└── backups/
```

### Environment Variables

Key environment variables:

- `LANGFUSE_SECRET`: Secret key for encryption
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `S3_*`: S3 storage configuration
- `NEXTAUTH_SECRET`: NextAuth.js secret
- `NEXTAUTH_URL`: Base URL for authentication
- `NODE_ENV`: Environment (production/development)

### Authentication

Supported authentication methods:

1. Email/Password
2. OAuth providers (Google, GitHub, GitLab, etc.)
3. API keys
4. JWT tokens

## Integration

### Python SDK

```python
from langfuse import Langfuse

# Initialize client
langfuse = Langfuse(
    public_key="your-public-key",
    secret_key="your-secret-key",
    host="https://langfuse.example.com"
)

# Log a trace
trace = langfuse.trace(
    name="user-query",
    user_id="user-123",
    metadata={"environment": "production"}
)

# Log a generation
generation = trace.generation(
    name="summarize",
    model="gpt-4",
    input={"text": "Long document text..."},
    output={"summary": "Summary of the document..."},
    metadata={"tokens": 42}
)
```

### JavaScript/TypeScript SDK

```typescript
import { Langfuse } from 'langfuse';

const langfuse = new Langfuse({
  publicKey: 'your-public-key',
  secretKey: 'your-secret-key',
  baseUrl: 'https://langfuse.example.com'
});

// Log a trace
const trace = langfuse.trace({
  name: 'user-query',
  userId: 'user-123',
  metadata: { environment: 'production' }
});

// Log a generation
const generation = trace.generation({
  name: 'summarize',
  model: 'gpt-4',
  input: { text: 'Long document text...' },
  output: { summary: 'Summary of the document...' },
  metadata: { tokens: 42 }
});
```

## Security

### Data Protection

- All sensitive data encrypted at rest
- Secure communication with TLS
- API key authentication
- Rate limiting
- CORS protection
- Input validation

### Access Control

- Role-based access control (RBAC)
- Project-level permissions
- Audit logging
- Session management

## Monitoring

### Built-in Metrics

- Request/response metrics
- Error rates
- Latency percentiles
- Resource usage

### Integration

- Prometheus metrics endpoint
- Grafana dashboards
- Alerting rules
- Log aggregation

## Backup and Recovery

### Database Backup

```bash
# Create backup
pg_dump -U langfuse -d langfuse > langfuse_backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U langfuse -d langfuse < langfuse_backup_20230101.sql
```

### S3 Backup

```bash
# Sync data to S3
aws s3 sync /opt/langfuse/data/ s3://langfuse-backups/$(date +%Y%m%d)/

# Restore from S3
aws s3 sync s3://langfuse-backups/20230101/ /opt/langfuse/data/
```

## Scaling

### Vertical Scaling

- Increase CPU/memory resources
- Optimize database performance
- Tune Redis cache

### Horizontal Scaling

- Deploy multiple instances
- Use a load balancer
- Configure database read replicas
- Shard data if necessary

## Tags

- `langfuse:install`: Installation tasks
- `langfuse:config`: Configuration tasks
- `langfuse:auth`: Authentication setup
- `langfuse:backup`: Backup configuration
- `langfuse:monitoring`: Monitoring setup

## License

Proprietary - All rights reserved
