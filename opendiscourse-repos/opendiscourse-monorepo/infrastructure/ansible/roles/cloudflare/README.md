# Cloudflare Role

This role manages Cloudflare DNS, WAF, and security settings for the OpenDiscourse infrastructure.

## Features

- DNS record management
- WAF rule configuration
- Page Rules setup
- SSL/TLS configuration
- Security level settings
- Caching configuration
- Rate limiting
- Workers configuration
- Argo Tunnel setup
- Load balancer configuration

## Requirements

- Cloudflare API token with appropriate permissions
- Python `cloudflare` package
- Domain managed in Cloudflare

## Role Variables

### Required Variables

- `cloudflare_api_token`: Cloudflare API token
- `cloudflare_zone_id`: Cloudflare Zone ID
- `cloudflare_domain`: Domain managed by Cloudflare

### Optional Variables

- `cloudflare_dns_records`: List of DNS records to manage
  ```yaml
  cloudflare_dns_records:
    - name: "example.com"
      type: A
      content: "203.0.113.1"
      proxied: true
      ttl: 1
    - name: "www"
      type: CNAME
      content: "example.com"
      proxied: true
  ```
- `cloudflare_waf_rules`: WAF rules to configure
- `cloudflare_page_rules`: Page Rules to configure
- `cloudflare_ssl_mode`: SSL mode (off, flexible, full, strict, origin_pull)
- `cloudflare_security_level`: Security level (off, essentially_off, low, medium, high, under_attack)

## Dependencies

- python3-pip
- python3-cloudflare (installed by the role)

## Example Playbook

```yaml
- hosts: localhost
  connection: local
  roles:
    - role: cloudflare
      vars:
        cloudflare_api_token: "{{ vault_cloudflare_api_token }}"
        cloudflare_zone_id: "{{ vault_cloudflare_zone_id }}"
        cloudflare_domain: "example.com"
        cloudflare_dns_records:
          - name: "example.com"
            type: A
            content: "203.0.113.1"
            proxied: true
          - name: "www"
            type: CNAME
            content: "example.com"
            proxied: true
        cloudflare_ssl_mode: "full"
        cloudflare_security_level: "high"
```

## Configuration

### DNS Records

Manage DNS records through the `cloudflare_dns_records` list. Each record can have:
- `name`: Record name
- `type`: Record type (A, AAAA, CNAME, MX, etc.)
- `content`: Record content
- `proxied`: Whether to proxy through Cloudflare (default: false)
- `ttl`: TTL in seconds (1 = auto)
- `priority`: Priority for MX/SRV records

### WAF Rules

Configure WAF rules through the `cloudflare_waf_rules` list. Example:

```yaml
cloudflare_waf_rules:
  - description: "Block bad bots"
    expression: "(cf.client.bot) or (cf.threat_score gt 14)"
    action: "block"
    enabled: true
```

### Page Rules

Configure Page Rules through the `cloudflare_page_rules` list. Example:

```yaml
cloudflare_page_rules:
  - targets:
      - "www.example.com/*"
    actions:
      - id: "forwarding_url"
        value:
          url: "https://example.com/$1"
          status_code: 301
    status: "active"
```

## Security

- Uses API tokens with least privilege
- Encrypts sensitive data with Ansible Vault
- Validates all API responses
- Implements idempotent operations

## Tags

- `cloudflare:dns`: Manage DNS records
- `cloudflare:waf`: Configure WAF
- `cloudflare:ssl`: Configure SSL/TLS
- `cloudflare:security`: Configure security settings
- `cloudflare:cache`: Configure caching

## License

Proprietary - All rights reserved
