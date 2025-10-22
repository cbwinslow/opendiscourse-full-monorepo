# FastAPI Role

Deploys FastAPI applications with production configurations.

## Features

- FastAPI app deployment
- Uvicorn/Gunicorn setup
- Systemd service
- Environment management
- Logging
- Monitoring
- Security

## Requirements

- Python 3.8+
- Ports: 8000 (default)

## Variables

```yaml
# Core
fastapi_enabled: true
fastapi_app_name: "myapp"
fastapi_user: "fastapi"
fastapi_app_dir: "/opt/{{ fastapi_app_name }}"
fastapi_venv_dir: "{{ fastapi_app_dir }}/venv"
fastapi_log_dir: "/var/log/{{ fastapi_app_name }}"

# Gunicorn
fastapi_gunicorn:
  bind: "0.0.0.0:8000"
  workers: 4
  worker_class: "uvicorn.workers.UvicornWorker"
  timeout: 120

# App Settings
fastapi_settings:
  DEBUG: false
  SECRET_KEY: "{{ vault_fastapi_secret }}"
  DATABASE_URL: "postgresql://user:pass@db:5432/{{ fastapi_app_name }}"
  REDIS_URL: "redis://redis:6379/0"

# Monitoring
fastapi_monitoring:
  enabled: true
  prometheus_port: 8001
  health_check: "/health"

# Security
fastapi_security:
  cors_enabled: true
  rate_limit: "100/minute"
  auth_enabled: true
```

## Example Playbook

```yaml
- hosts: app_servers
  become: true
  roles:
    - role: fastapi
      vars:
        fastapi_app_name: "myapp"
        fastapi_settings:
          DATABASE_URL: "postgresql://user:{{ vault_db_pass }}@db:5432/myapp"
```

## File Structure

```
/opt/myapp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── core/
│   └── db/
├── .env
└── requirements.txt

/var/log/myapp/
├── access.log
└── error.log
```

## Security

- JWT Authentication
- CORS
- Rate limiting
- Input validation
- Security headers
- HTTPS
- CSRF protection
- SQL injection prevention
- XSS protection
- Password hashing
- Secure cookies
- Session management
- OAuth2
- API key auth
- Security headers
- Content Security Policy
- Secure file uploads
- Security audits
- Penetration testing
- Dependency scanning
- Container security
- Network security
- Secure configuration
- Secure logging
- Secure deployment
- Secure coding practices
```
