# OAuth Role

This role sets up and configures OAuth2 authentication for the OpenDiscourse infrastructure using OAuth2 Proxy and Keycloak.

## Features

- OAuth2 Proxy deployment and configuration
- Keycloak identity provider setup
- Multiple OAuth2 providers support (Google, GitHub, GitLab, etc.)
- Session management
- Token validation and refresh
- Role-based access control (RBAC)
- Single Sign-On (SSO) integration
- User provisioning
- Audit logging

## Requirements

- Docker role (for containerized deployment)
- Reverse proxy role (for routing)
- Database role (for user storage)
- Domain name with valid SSL certificate

## Role Variables

### Required Variables

```yaml
oauth2_proxy:
  client_id: "{{ vault_oauth_client_id }}"
  client_secret: "{{ vault_oauth_client_secret }}"
  cookie_secret: "{{ vault_oauth_cookie_secret }}"
  email_domains: ["example.com"]
  upstream: "http://app:8000"
  provider: "keycloak"
  redirect_url: "https://auth.example.com/oauth2/callback"
  oidc_issuer_url: "https://keycloak.example.com/auth/realms/myrealm"
```

### Optional Variables

```yaml
oauth2_proxy_extra_env:
  - name: OAUTH2_PROXY_SKIP_PROVIDER_BUTTON
    value: "true"
  - name: OAUTH2_PROXY_EMAIL_DOMAINS
    value: "example.com,example.org"
  - name: OAUTH2_PROXY_WHITELIST_DOMAINS
    value: ".example.com"

keycloak_enabled: true
keycloak_admin_username: admin
keycloak_admin_password: "{{ vault_keycloak_admin_password }}"
keycloak_realm: myrealm
keycloak_clients:
  - clientId: myapp
    name: My Application
    enabled: true
    publicClient: false
    redirectUris: ["https://app.example.com/*"]
    webOrigins: ["+"]
    protocolMappers:
      - name: "groups"
        protocol: openid-connect
        protocolMapper: oidc-group-membership-mapper
        config:
          claim.name: "groups"
          jsonType.label: "String"
          full.path: "false"
          userinfo.token.claim: "true"
```

## Dependencies

- docker
- reverse_proxy
- database (if using Keycloak with external database)

## Example Playbook

```yaml
- hosts: auth_servers
  become: true
  roles:
    - role: oauth
      vars:
        oauth2_proxy:
          client_id: "{{ vault_oauth_client_id }}"
          client_secret: "{{ vault_oauth_client_secret }}"
          cookie_secret: "{{ vault_oauth_cookie_secret }}"
          email_domains: ["example.com"]
          upstream: "http://app:8000"
          provider: "keycloak"
          redirect_url: "https://auth.example.com/oauth2/callback"
          oidc_issuer_url: "https://keycloak.example.com/auth/realms/myrealm"
        
        keycloak_enabled: true
        keycloak_admin_username: admin
        keycloak_admin_password: "{{ vault_keycloak_admin_password }}"
        keycloak_realm: myrealm
```

## Configuration

### OAuth2 Proxy

- Configuration file: `/etc/oauth2-proxy.cfg`
- Environment variables: Loaded from `/etc/oauth2-proxy.env`
- Docker container: `quay.io/oauth2-proxy/oauth2-proxy`
- Port: 4180

### Keycloak

- Admin console: `https://keycloak.example.com/auth/admin`
- Data directory: `/opt/keycloak/data`
- Configuration: `/opt/keycloak/conf`
- Database: PostgreSQL (external) or embedded H2

## Security

- All traffic over HTTPS
- Secure cookie settings
- CSRF protection
- Rate limiting
- Token encryption
- Regular security updates

## Integration

### Web Applications

To protect a web application with OAuth2 Proxy:

1. Configure the reverse proxy to route requests through OAuth2 Proxy
2. Set the `X-Auth-Request-*` headers in your application
3. Validate the `X-Auth-Request-User` header

### API Authentication

For API authentication:

1. Use the `Authorization: Bearer <token>` header
2. Validate the token using the OIDC discovery endpoint
3. Check token claims for authorization

## Backup and Recovery

### OAuth2 Proxy

No persistent data, just configuration:
```bash
# Backup configuration
cp /etc/oauth2-proxy.cfg /backups/oauth2-proxy.cfg
```

### Keycloak

```bash
# Export realm
docker exec -it keycloak /opt/keycloak/bin/kc.sh export \
  --file /backups/realm-export.json \
  --realm myrealm

# Backup database
pg_dump -U keycloak -d keycloak > /backups/keycloak_db_$(date +%Y%m%d).sql
```

## Monitoring

- OAuth2 Proxy metrics endpoint: `/metrics`
- Keycloak metrics: `/auth/realms/myrealm/metrics`
- Logs: Sent to centralized logging
- Alerts: Failed login attempts, token validation errors

## Tags

- `oauth:proxy`: OAuth2 Proxy tasks
- `oauth:keycloak`: Keycloak tasks
- `oauth:config`: Configuration tasks
- `oauth:users`: User management tasks

## License

Proprietary - All rights reserved
