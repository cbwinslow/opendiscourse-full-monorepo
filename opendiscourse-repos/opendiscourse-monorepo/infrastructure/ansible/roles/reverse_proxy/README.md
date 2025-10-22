# Reverse Proxy Role

This role sets up and configures Traefik as a reverse proxy with automatic SSL certificate management.

## Features

- Traefik v2 installation and configuration
- Automatic SSL certificates with Let's Encrypt
- HTTP/2 and HTTP/3 support
- Basic authentication
- Rate limiting
- Request logging
- Health checks
- Load balancing
- Middleware configuration
- Docker Swarm support

## Requirements

- Docker role (for container runtime)
- Common role (for system configuration)
- Ports 80 and 443 available
- Valid domain name pointing to server

## Role Variables

### Required Variables

- `traefik_domain`: Primary domain for the Traefik dashboard
- `traefik_email`: Email for Let's Encrypt
- `traefik_basic_auth`: Basic auth credentials for dashboard
  ```yaml
  traefik_basic_auth:
    - "admin:$apr1$ruca84Hq$mbjdMxzA9zKc6l6aUMSxN0"
  ```

### Optional Variables

- `traefik_version`: Traefik version (default: v2.10.0)
- `traefik_ssl`: Enable SSL (default: true)
- `traefik_letsencrypt`: Enable Let's Encrypt (default: true)
- `traefik_letsencrypt_staging`: Use Let's Encrypt staging (default: false)
- `traefik_http_port`: HTTP port (default: 80)
- `traefik_https_port`: HTTPS port (default: 443)
- `traefik_dashboard`: Enable dashboard (default: true)
- `traefik_middlewares`: Custom middlewares
  ```yaml
  traefik_middlewares:
    - name: https-redirect
      redirectScheme:
        scheme: https
        permanent: true
  ```

## Dependencies

- docker
- common

## Example Playbook

```yaml
- hosts: proxy_servers
  become: true
  roles:
    - role: reverse_proxy
      vars:
        traefik_domain: "traefik.example.com"
        traefik_email: "admin@example.com"
        traefik_basic_auth:
          - "admin:$apr1$ruca84Hq$mbjdMxzA9zKc6l6aUMSxN0"
        traefik_middlewares:
          - name: https-redirect
            redirectScheme:
              scheme: https
              permanent: true
```

## Configuration

### Static Configuration

Main configuration is in `templates/traefik.yml.j2` which includes:
- Entry points (HTTP/HTTPS)
- API and dashboard configuration
- Let's Encrypt settings
- Logging configuration
- Access logs

### Dynamic Configuration

Docker labels are used for dynamic configuration of routes and services.

Example Docker Compose service with Traefik labels:

```yaml
services:
  whoami:
    image: containous/whoami
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(`whoami.example.com`)"
      - "traefik.http.routers.whoami.entrypoints=websecure"
      - "traefik.http.routers.whoami.tls=true"
```

## Security

- Dashboard protected with basic auth
- Default HTTPS redirect
- Secure TLS configuration
- Rate limiting
- IP whitelisting available

## Monitoring

Prometheus metrics are exposed at `/metrics` endpoint.

## Tags

- `traefik:install`: Install Traefik
- `traefik:config`: Configure Traefik
- `traefik:middlewares`: Configure middlewares
- `traefik:tls`: Configure TLS

## License

Proprietary - All rights reserved
