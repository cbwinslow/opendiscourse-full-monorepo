# Traefik Role

This role installs and configures Traefik as a reverse proxy and load balancer for the OpenDiscourse platform.

## Features

- Traefik installation and configuration
- Automatic SSL certificates with Let's Encrypt
- HTTP/2 and HTTP/3 support
- Load balancing
- Circuit breakers
- Retries
- Rate limiting
- Middleware (headers, auth, redirects, etc.)
- Metrics and monitoring
- Access logs
- Docker and Kubernetes integration

## Requirements

- Linux (Ubuntu/Debian/CentOS)
- Docker and Docker Compose
- Ports: 80 (HTTP), 443 (HTTPS), 8080 (Dashboard)
- DNS records pointing to the server
- Email for Let's Encrypt notifications

## Role Variables

### Required Variables

```yaml
# Core Configuration
traefik_enabled: true
traefik_version: "2.10"
traefik_domain: "example.com"
traefik_email: "admin@example.com"

# Docker Configuration
traefik_docker:
  network: "traefik_public"
  socket: "/var/run/docker.sock"

# Let's Encrypt Configuration
traefik_certificates:
  enabled: true
  email: "admin@example.com"
  staging: false
  dns_challenge:
    enabled: false
    provider: ""
    delay_before_check: 0
```

### Optional Variables

```yaml
# Network Configuration
traefik_network:
  name: "traefik_public"
  driver: "bridge"
  attachable: true
  external: false

# EntryPoints
traefik_entrypoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"
    http2: true
  metrics:
    address: ":8082"

# Dashboard Configuration
traefik_dashboard:
  enabled: true
  domain: "dashboard.example.com"
  auth:
    enabled: true
    users:
      - "admin:$apr1$ruca84Hq$mbjdMxzA0WkMwGl3rJ8lw/"  # admin:password

# Logging Configuration
traefik_log:
  level: "INFO"
  file_path: "/var/log/traefik/traefik.log"
  max_size: 10
  max_age: 28
  max_backups: 5

# Metrics Configuration
traefik_metrics:
  prometheus:
    enabled: true
    entryPoint: "metrics"
    addEntryPointsLabels: true
    addServicesLabels: true

# Access Logs
traefik_access_logs:
  enabled: true
  file_path: "/var/log/traefik/access.log"
  format: "json"
  fields:
    default_mode: "keep"
    names: {}
    headers:
      default_mode: "keep"
      names: {}

# Middleware Configuration
traefik_middlewares:
  default-headers:
    headers:
      browserXssFilter: true
      contentTypeNosniff: true
      forceSTSHeader: true
      frameDeny: true
      sslRedirect: true
      stsIncludeSubdomains: true
      stsPreload: true
      stsSeconds: 15552000

# Rate Limiting
traefik_rate_limit:
  enabled: true
  average: 100
  burst: 50

# Docker Provider Configuration
traefik_docker_provider:
  enabled: true
  exposed_by_default: false
  network: "traefik_public"
  watch: true
  swarm_mode: false

# File Provider Configuration
traefik_file_provider:
  enabled: true
  directory: "/etc/traefik/config"
  watch: true

# API Configuration
traefik_api:
  enabled: true
  dashboard: true
  debug: false
  insecure: false

# Ping Configuration
traefik_ping:
  enabled: true
  entryPoint: "traefik"
  manual_routing: false

# Tracing Configuration
traefik_tracing:
  enabled: false
  service_name: "traefik"
  span_name_limit: 0
  jaeger:
    enabled: false
    sampling_server_url: "http://localhost:5778/sampling"
    sampling_type: "const"
    sampling_param: 1.0
    local_agent_host_port: "127.0.0.1:6831"
    gen128_bit: true
    propagation: "jaeger"
    trace_context_header_name: "uber-trace-id"
    disable_attempt_reconnecting: false
    collector:
      endpoint: ""
      user: ""
      password: ""
    local_agent:
      host_port: "127.0.0.1:6831"

# Servers Transport Configuration
traefik_servers_transport:
  insecure_skip_verify: false
  root_cas: []
  max_idle_conns_per_host: 200
  forwarding_timeout: 0

# Experimental Features
traefik_experimental:
  http3: true
  plugins: {}
```

## Dependencies

- docker
- python3
- docker-compose

## Example Playbook

```yaml
- hosts: traefik_servers
  become: true
  roles:
    - role: traefik
      vars:
        traefik_enabled: true
        traefik_version: "2.10"
        traefik_domain: "example.com"
        traefik_email: "admin@example.com"
        
        traefik_docker:
          network: "traefik_public"
          socket: "/var/run/docker.sock"
        
        traefik_certificates:
          enabled: true
          email: "admin@example.com"
          staging: false
        
        traefik_dashboard:
          enabled: true
          domain: "dashboard.example.com"
          auth:
            enabled: true
            users:
              - "admin:$apr1$ruca84Hq$mbjdMxzA0WkMwGl3rJ8lw/"  # admin:password
```

## Configuration

### File Structure

```
/etc/traefik/
├── traefik.yml             # Main configuration file
├── config/                 # Dynamic configuration files
│   ├── dynamic/            # Dynamic configuration
│   │   ├── middlewares.yml # Middleware configurations
│   │   ├── routers.yml     # Router configurations
│   │   └── services.yml    # Service configurations
│   └── static/             # Static configuration
│       └── tls.yml         # TLS configuration
├── acme/                   # Let's Encrypt certificates
│   └── acme.json           # ACME account data
└── logs/                   # Log files
    ├── traefik.log         # Traefik logs
    └── access.log          # Access logs
```

### Dynamic Configuration Example

`config/dynamic/middlewares.yml`:
```yaml
http:
  middlewares:
    default-headers:
      headers:
        browserXssFilter: true
        contentTypeNosniff: true
        forceSTSHeader: true
        frameDeny: true
        sslRedirect: true
        stsIncludeSubdomains: true
        stsPreload: true
        stsSeconds: 15552000
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
```

`config/dynamic/routers.yml`:
```yaml
http:
  routers:
    web-router:
      rule: "Host(`example.com`)"
      entryPoints:
        - "websecure"
      middlewares:
        - "default-headers"
        - "rate-limit"
      service: "web-service"
      tls: {}
```

`config/dynamic/services.yml`:
```yaml
http:
  services:
    web-service:
      loadBalancer:
        servers:
          - url: "http://web:80"
        healthCheck:
          path: "/health"
          interval: "10s"
          timeout: "5s"
```

## Integration

### Docker Compose Example

```yaml
version: '3'

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    restart: always
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/traefik.yml:ro
      - ./config/:/etc/traefik/config/
      - ./acme/:/acme/
      - ./logs/:/var/log/traefik/
    networks:
      - traefik_public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`dashboard.example.com`)"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=admin:$apr1$ruca84Hq$mbjdMxzA0WkMwGl3rJ8lw/"

networks:
  traefik_public:
    external: true
```

### Docker Labels Example

```yaml
version: '3'

services:
  whoami:
    image: containous/whoami
    container_name: whoami
    restart: always
    networks:
      - traefik_public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(`whoami.example.com`)"
      - "traefik.http.routers.whoami.entrypoints=websecure"
      - "traefik.http.routers.whoami.tls=true"
      - "traefik.http.services.whoami.loadbalancer.server.port=80"

networks:
  traefik_public:
    external: true
```

## Security

### Authentication

- Basic authentication
- Forward authentication
- OAuth2 proxy
- IP whitelisting
- Rate limiting

### TLS Configuration

- Automatic Let's Encrypt certificates
- Custom certificates
- Mutual TLS (mTLS)
- TLS 1.2/1.3 only
- Strong cipher suites
- HSTS
- OCSP stapling

## Monitoring

### Built-in Metrics

- Request/response metrics
- EntryPoint metrics
- Service metrics
- Router metrics
- Middleware metrics
- TLS metrics
- Go runtime metrics

### Integration

- Prometheus metrics
- Datadog metrics
- InfluxDB metrics
- StatsD metrics
- OpenTelemetry

## Backup and Recovery

### Data Backup

```bash
# Backup ACME certificates
rsync -avz /etc/traefik/acme/ /backup/traefik/acme/

# Backup configuration
rsync -avz /etc/traefik/ /backup/traefik/config/

# Backup logs
rsync -avz /var/log/traefik/ /backup/traefik/logs/
```

### Restoration

```bash
# Restore ACME certificates
rsync -avz /backup/traefik/acme/ /etc/traefik/acme/

# Restore configuration
rsync -avz /backup/traefik/config/ /etc/traefik/

# Restart Traefik
systemctl restart traefik
```

## Scaling

### Vertical Scaling

- Increase CPU/memory resources
- Tune Go GC
- Optimize connection pooling

### Horizontal Scaling

- Deploy multiple Traefik instances
- Use a load balancer
- Shared configuration
- Distributed rate limiting

## Tags

- `traefik:install`: Installation tasks
- `traefik:config`: Configuration tasks
- `traefik:tls`: TLS configuration
- `traefik:middleware`: Middleware configuration
- `traefik:monitoring`: Monitoring setup
- `traefik:backup`: Backup configuration

## License

Proprietary - All rights reserved
