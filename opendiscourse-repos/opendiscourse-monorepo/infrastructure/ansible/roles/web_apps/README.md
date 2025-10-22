# Web Applications Role

This role deploys and manages web applications in the OpenDiscourse infrastructure, including OpenDiscourse, LocalAI, and FastAPI services.

## Features

### OpenDiscourse
- Deployment of OpenDiscourse platform
- Theme and plugin management
- Configuration management
- Backup and restore
- Performance optimization

### LocalAI
- LLM inference service setup
- Model management
- API configuration
- Integration with applications

### FastAPI
- Application deployment
- Gunicorn configuration
- ASGI/WSGI setup
- Environment management

### Graphite
- Metrics collection
- Dashboard configuration
- Storage schemas
- Data aggregation

## Requirements

- Docker role (for containerized deployment)
- Database role (for data persistence)
- Reverse proxy role (for routing)
- Sufficient system resources

## Role Variables

### OpenDiscourse

```yaml
opendiscourse_enabled: true
opendiscourse_version: "latest"
opendiscourse_hostname: "discourse.example.com"
opendiscourse_smtp:
  address: smtp.example.com
  port: 587
  user_name: user@example.com
  password: "{{ vault_smtp_password }}"
opendiscourse_admin:
  username: admin
  email: admin@example.com
  password: "{{ vault_discourse_admin_password }}"
```

### LocalAI

```yaml
localai_enabled: true
localai_version: "v2.0.0"
localai_models:
  - name: gpt-4
    url: "https://huggingface.co/TheBloke/gpt4-x-vicuna-13B-GGUF/resolve/main/gpt4-x-vicuna-13B.Q4_K_M.gguf"
localai_config:
  context_size: 2048
  threads: 4
  f16: true
```

### FastAPI

```yaml
fastapi_apps:
  - name: myapp
    path: /opt/apps/myapp
    port: 8000
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
    command: "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app"
```

### Graphite

```yaml
graphite_enabled: true
graphite_version: "1.1.10"
graphite_storage_schemas:
  - name: default
    pattern: .*
    retentions: 10s:6h,1m:7d,10m:5y
```

## Dependencies

- docker
- database
- reverse_proxy
- monitoring (for metrics)

## Example Playbook

```yaml
- hosts: app_servers
  become: true
  roles:
    - role: web_apps
      vars:
        opendiscourse_enabled: true
        localai_enabled: true
        fastapi_apps:
          - name: api
            path: /opt/apps/api
            port: 8000
        graphite_enabled: true
```

## Configuration

### OpenDiscourse

- Data directory: `/var/discourse`
- Configuration: `containers/app.yml`
- Plugins: Managed via admin interface or configuration
- Themes: Stored in shared volume

### LocalAI

- Models directory: `/models`
- Configuration: `/etc/localai/config.yaml`
- API endpoint: `http://localhost:8080/v1`
- Authentication: API key or JWT

### FastAPI

- Application code: `/opt/apps/{name}`
- Virtual environment: `/opt/venvs/{name}`
- Logs: `/var/log/{name}.log`
- Systemd service: `/etc/systemd/system/{name}.service`

### Graphite

- Data directory: `/opt/graphite/storage`
- Configuration: `/opt/graphite/conf`
- Web interface: `http://localhost:80`

## Security

- Container isolation
- Network segmentation
- Rate limiting
- Authentication
- HTTPS enforcement

## Monitoring

- Application metrics
- Request logging
- Error tracking
- Performance monitoring

## Backup and Recovery

### OpenDiscourse

```bash
# Backup
docker exec -t $(docker ps -qf "name=discourse") backup

# Restore
# Upload backup file and run restore from admin interface
```

### LocalAI

Backup the models directory:
```bash
tar czf localai_models_$(date +%Y%m%d).tar.gz /models
```

### FastAPI

Backup the application directory and database:
```bash
# Application
rsync -avz /opt/apps/ /backups/apps/

# Database
pg_dump -U user -d dbname > backup.sql
```

### Graphite

```bash
# Backup whisper files
rsync -avz /opt/graphite/storage/whisper/ /backups/graphite/
```

## Tags

- `opendiscourse`: OpenDiscourse tasks
- `localai`: LocalAI tasks
- `fastapi`: FastAPI tasks
- `graphite`: Graphite tasks
- `web_apps:deploy`: Deployment tasks
- `web_apps:config`: Configuration tasks
- `web_apps:backup`: Backup tasks

## License

Proprietary - All rights reserved
