# Caddy Role

This role installs and configures Caddy, a powerful, enterprise-ready, open-source web server with automatic HTTPS.

## Features

- Automatic HTTPS with Let's Encrypt
- HTTP/2 and HTTP/3 support
- Reverse proxy with load balancing
- Static file serving
- Security headers
- Rate limiting
- Logging
- Docker integration

## Requirements

- Linux (Ubuntu/Debian/CentOS/RHEL)
- Root or sudo access
- Ports: 80 (HTTP), 443 (HTTPS)
- DNS records pointing to the server
- Email for Let's Encrypt

## Role Variables

### Core Configuration

```yaml
caddy_enabled: true
caddy_version: "2.7.5"
caddy_user: "www-data"
caddy_group: "www-data"

# Service Configuration
caddy_service:
  enabled: true
  state: "started"
  restart_on_change: true

# SSL Configuration
caddy_ssl:
  email: "admin@example.com"
  key_type: "p384"
  issuer: "letsencrypt"

# Global Options
caddy_global_options:
  admin: "localhost:2019"
  log: "/var/log/caddy/access.log"
  log_format: "json"
  log_level: "INFO"

# Sites Configuration
caddy_sites:
  - server_name: "example.com www.example.com"
    listen: [":80", ":443"]
    root: "/var/www/example.com"
    tls: true
    redirect_www: true
    gzip: true
    reverse_proxy: ["localhost:3000"]
    headers:
      Strict-Transport-Security: "max-age=31536000"
      X-Content-Type-Options: "nosniff"
      X-Frame-Options: "SAMEORIGIN"
      X-XSS-Protection: "1; mode=block"
    rate_limit:
      enabled: true
      rate: "100"
      burst: "50"
      except: ["127.0.0.1"]
```

## Example Playbook

```yaml
- hosts: web_servers
  become: true
  roles:
    - role: caddy
      vars:
        caddy_enabled: true
        caddy_ssl:
          email: "admin@example.com"
        caddy_sites:
          - server_name: "example.com"
            root: "/var/www/example.com"
            tls: true
            reverse_proxy: ["localhost:3000"]
```

## File Structure

```
/etc/caddy/
├── Caddyfile           # Main configuration
├── sites/              # Site configurations
│   └── example.com     # Example site config
├── ssl/                # SSL certificates
└── snippets/           # Reusable config snippets

/var/log/caddy/         # Log files
/var/www/               # Web root
```

## Security

- Automatic HTTPS with Let's Encrypt
- Security headers
- Rate limiting
- TLS 1.2/1.3 only
- Strong cipher suites
- HSTS
- OCSP stapling

## Monitoring

- Built-in metrics endpoint
- Access and error logs
- JSON log format
- Log rotation

## Tags

- `caddy:install`: Installation tasks
- `caddy:config`: Configuration tasks
- `caddy:ssl`: SSL configuration
- `caddy:security`: Security configuration
- `caddy:monitoring`: Monitoring setup

## License

Proprietary - All rights reserved
