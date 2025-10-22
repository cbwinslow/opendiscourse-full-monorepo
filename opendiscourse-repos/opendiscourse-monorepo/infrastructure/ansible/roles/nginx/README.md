# Nginx Role

This role installs and configures Nginx as a high-performance web server, reverse proxy, and load balancer for the OpenDiscourse platform.

## Features

- Nginx installation and configuration
- SSL/TLS termination with Let's Encrypt
- HTTP/2 and HTTP/3 support
- Reverse proxy configuration
- Load balancing
- Rate limiting
- Gzip compression
- Security headers
- Access and error logging
- Custom error pages
- Virtual hosts management

## Requirements

- Linux (Ubuntu/Debian/CentOS)
- Ports: 80 (HTTP), 443 (HTTPS)
- Root or sudo access
- DNS records pointing to the server
- Email for Let's Encrypt notifications (if using SSL)

## Role Variables

### Required Variables

```yaml
# Core Configuration
nginx_enabled: true
nginx_user: "www-data"
nginx_worker_processes: "auto"
nginx_worker_connections: 1024
nginx_multi_accept: "on"
nginx_sendfile: "on"

tcp_nopush: "on"
tcp_nodelay: "on"

# Server Names Hash
server_names_hash_bucket_size: 64
server_names_hash_max_size: 2048

# MIME Types
include_mime_types: true

default_type: "application/octet-stream"

# Logging
error_log: "/var/log/nginx/error.log warn"
access_log: "/var/log/nginx/access.log combined"

# SSL Configuration
ssl_protocols: "TLSv1.2 TLSv1.3"
ssl_ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384"
ssl_prefer_server_ciphers: "on"
ssl_session_cache: "shared:SSL:10m"
ssl_session_timeout: 1d
ssl_session_tickets: "off"
ssl_stapling: "on"
ssl_stapling_verify: "on"

# Gzip Configuration
gzip: "on"
gzip_vary: "on"
gzip_proxied: "any"
gzip_comp_level: 6
gzip_buffers: "16 8k"
gzip_http_version: "1.1"
gzip_min_length: 256
gzip_types: |
  application/atom+xml
  application/geo+json
  application/javascript
  application/x-javascript
  application/json
  application/ld+json
  application/manifest+json
  application/rdf+xml
  application/rss+xml
  application/vnd.ms-fontobject
  application/wasm
  application/x-web-app-manifest+json
  application/xhtml+xml
  application/xml
  font/eot
  font/otf
  font/ttf
  image/bmp
  image/svg+xml
  text/cache-manifest
  text/calendar
  text/css
  text/javascript
  text/markdown
  text/plain
  text/xml
  text/vcard
  text/vnd.rim.location.xloc
  text/vtt
  text/x-component
  text/x-cross-domain-policy
  text/xml

# Virtual Hosts
nginx_vhosts:
  - listen: "80"
    server_name: "example.com www.example.com"
    root: "/var/www/example.com"
    index: "index.html index.htm"
    access_log: "/var/log/nginx/example.com.access.log"
    error_log: "/var/log/nginx/example.com.error.log"
    locations:
      - location: "/"
        try_files: "$uri $uri/ /index.html"
    ssl:
      enabled: true
      certificate: "/etc/letsencrypt/live/example.com/fullchain.pem"
      certificate_key: "/etc/letsencrypt/live/example.com/privkey.pem"
      protocols: "TLSv1.2 TLSv1.3"
      ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384"
      ssl_session_cache: "shared:SSL:10m"
      ssl_session_timeout: "1d"
      ssl_session_tickets: "off"
      ssl_stapling: "on"
      ssl_stapling_verify: "on"
      http2: true
      http3: true
      hsts: "max-age=63072000; includeSubDomains; preload"
      ocsp_stapling: true
      ocsp_cache_shared: "shared:OCSP:10m"
      resolver: "1.1.1.1 1.0.0.1 8.8.8.8 8.8.4.4 valid=300s"
      resolver_timeout: "5s"

# Rate Limiting
nginx_rate_limit:
  enabled: true
  limit_req_zone: |
    $binary_remote_addr zone=one:10m rate=10r/s;
    $binary_remote_addr zone=two:10m rate=5r/s;
  limit_conn_zone: |
    $binary_remote_addr zone=addr:10m;

# Security Headers
nginx_security_headers:
  X-Frame-Options: "SAMEORIGIN"
  X-Content-Type-Options: "nosniff"
  X-XSS-Protection: "1; mode=block"
  Referrer-Policy: "strict-origin-when-cross-origin"
  Content-Security-Policy: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' data: https:; connect-src 'self' https:;"
  Permissions-Policy: "geolocation=(), microphone=(), camera=()"
  Cross-Origin-Embedder-Policy: "require-corp"
  Cross-Origin-Opener-Policy: "same-origin"
  Cross-Origin-Resource-Policy: "same-site"
  X-Permitted-Cross-Domain-Policies: "none"
  Strict-Transport-Security: "max-age=63072000; includeSubDomains; preload"

# Performance Tuning
nginx_performance:
  keepalive_timeout: 65
  keepalive_requests: 100
  client_max_body_size: "64M"
  client_body_buffer_size: "128k"
  client_header_buffer_size: "1k"
  large_client_header_buffers: "4 8k"
  send_timeout: 60
  client_body_timeout: 60
  client_header_timeout: 60
  reset_timedout_connection: "on"
  types_hash_max_size: 2048
  server_tokens: "off"
  server_names_hash_bucket_size: 64
  server_names_hash_max_size: 2048

# Logging Configuration
nginx_logging:
  access_log: "/var/log/nginx/access.log combined buffer=512k flush=1m"
  error_log: "/var/log/nginx/error.log warn"
  log_format: |
    '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for"';

# Let's Encrypt Configuration
letsencrypt_enabled: true
letsencrypt_email: "admin@example.com"
letsencrypt_webroot: "/var/www/letsencrypt"
letsencrypt_cert_dir: "/etc/letsencrypt"
letsencrypt_renewal_command: "systemctl reload nginx"
letsencrypt_renewal_frequency: "weekly"
letsencrypt_renewal_day: "0"
letsencrypt_renewal_hour: "2"
letsencrypt_renewal_minute: "0"

# Firewall Configuration
nginx_firewall_allow: ["80/tcp", "443/tcp"]

# Monitoring
nginx_status:
  enabled: true
  listen: "127.0.0.1:8080"
  allow: ["127.0.0.1", "::1"]
  location: "/nginx_status"
  stub_status: true

# Modules
nginx_modules:
  - http_ssl
  - http_v2
  - http_gzip_static
  - http_gunzip
  - http_realip
  - http_secure_link
  - http_sub
  - http_xslt
  - mail_ssl
  - stream_ssl_module
  - stream_ssl_preread_module

# Custom Configuration
nginx_custom_conf: |
  # Custom Nginx configuration can be added here
  # This will be included in the main nginx.conf

nginx_custom_http: |
  # Custom HTTP block configuration

nginx_custom_events: |
  # Custom events block configuration

# Templates
nginx_templates:
  - src: "nginx.conf.j2"
    dest: "/etc/nginx/nginx.conf"
  - src: "mime.types.j2"
    dest: "/etc/nginx/mime.types"
  - src: "sites-available/default.j2"
    dest: "/etc/nginx/sites-available/default"

# Services
nginx_services:
  - name: "nginx"
    state: "started"
    enabled: true
    reload: true

# Dependencies
nginx_dependencies:
  - nginx
  - nginx-common
  - nginx-full
  - certbot
  - python3-certbot-nginx

# SSL Configuration
nginx_ssl:
  dhparam:
    enabled: true
    path: "/etc/nginx/ssl/dhparam.pem"
    size: 2048
  ssl_session_cache: "shared:SSL:10m"
  ssl_session_timeout: "1d"
  ssl_session_tickets: "off"
  ssl_stapling: "on"
  ssl_stapling_verify: "on"
  resolver: "1.1.1.1 1.0.0.1 8.8.8.8 8.8.4.4 valid=300s"
  resolver_timeout: "5s"

# HTTP/3 Configuration
nginx_http3:
  enabled: true
  listen_http3: true
  listen_http3_required: true
  http3_hq: true
  http3_stream_buffer_size: "64k"
  http3_max_concurrent_streams: 256
  http3_initial_max_data: "512k"
  http3_initial_max_stream_data_bidi_local: "256k"
  http3_initial_max_stream_data_bidi_remote: "256k"
  http3_initial_max_stream_data_uni: "256k"
  http3_initial_max_streams_bidi: 128
  http3_initial_max_streams_uni: 128
  http3_ack_delay_exponent: 3
  http3_max_ack_delay: "25ms"
  http3_active_connection_id_limit: 8
  http3_idle_timeout: "30s"
  http3_retry_timeout: "5s"
  http3_max_udp_payload_size: "1452"
  http3_max_concurrent_streams: 128
  http3_max_header_size: "16k"
  http3_max_field_size: "4k"
  http3_max_requests: 1000
  http3_max_header_size: "16k"
  http3_max_field_size: "4k"
  http3_max_requests: 1000
```

## Dependencies

- python3
- certbot
- openssl
- ufw (optional, for firewall)

## Example Playbook

```yaml
- hosts: nginx_servers
  become: true
  roles:
    - role: nginx
      vars:
        nginx_enabled: true
        nginx_user: "www-data"
        nginx_worker_processes: "auto"
        nginx_worker_connections: 1024
        
        nginx_vhosts:
          - listen: "80"
            server_name: "example.com www.example.com"
            root: "/var/www/example.com"
            index: "index.html index.htm"
            access_log: "/var/log/nginx/example.com.access.log"
            error_log: "/var/log/nginx/example.com.error.log"
            locations:
              - location: "/"
                try_files: "$uri $uri/ /index.html"
            ssl:
              enabled: true
              certificate: "/etc/letsencrypt/live/example.com/fullchain.pem"
              certificate_key: "/etc/letsencrypt/live/example.com/privkey.pem"
              protocols: "TLSv1.2 TLSv1.3"
              http2: true
              http3: true
        
        letsencrypt_enabled: true
        letsencrypt_email: "admin@example.com"
        
        nginx_security_headers:
          X-Frame-Options: "SAMEORIGIN"
          X-Content-Type-Options: "nosniff"
          X-XSS-Protection: "1; mode=block"
          Referrer-Policy: "strict-origin-when-cross-origin"
```

## Configuration

### File Structure

```
/etc/nginx/
├── nginx.conf                  # Main configuration file
├── conf.d/                     # Additional configuration files
├── sites-available/            # Available site configurations
│   └── default                 # Default site configuration
├── sites-enabled/              # Enabled site configurations
│   └── default -> /etc/nginx/sites-available/default
├── modules-available/          # Available dynamic modules
├── modules-enabled/            # Enabled dynamic modules
├── snippets/                   # Configuration snippets
│   ├── ssl-params.conf        # SSL parameters
│   └── security-headers.conf   # Security headers
├── ssl/                       # SSL certificates and keys
│   ├── dhparam.pem            # DH parameters
│   └── ssl_certificate.crt    # SSL certificate
└── includes/                   # Included configuration files
```

### Virtual Host Configuration

Example virtual host configuration in `sites-available/example.com`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Root directory
    root /var/www/example.com;
    index index.html index.htm;
    
    # Logging
    access_log /var/log/nginx/example.com.access.log;
    error_log /var/log/nginx/example.com.error.log;
    
    # Locations
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Static files
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        access_log off;
        add_header Cache-Control "public, no-transform";
    }
    
    # API Proxy
    location /api/ {
        proxy_pass http://localhost:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Security
    location ~ /\.ht {
        deny all;
    }
}
```

## Security

### SSL Configuration

- TLS 1.2/1.3 only
- Strong cipher suites
- HSTS (HTTP Strict Transport Security)
- OCSP stapling
- Perfect Forward Secrecy (PFS)
- HTTP/2 and HTTP/3 support
- Certificate Transparency

### Security Headers

- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Content-Security-Policy
- Referrer-Policy
- Permissions-Policy
- Cross-Origin-Embedder-Policy
- Cross-Origin-Opener-Policy
- Cross-Origin-Resource-Policy
- X-Permitted-Cross-Domain-Policies

### Rate Limiting

- Request rate limiting
- Connection limiting
- Burst handling
- Delay handling

## Performance Tuning

### Gzip Compression

- Text compression
- MIME type configuration
- Compression level
- Buffer size
- Minimum length

### Caching

- Browser caching
- Proxy caching
- FastCGI caching
- Cache purging
- Cache locking

### Connection Handling

- Keepalive connections
- Connection timeouts
- Buffer sizes
- File descriptors
- Worker processes
- Worker connections

## Monitoring

### Status Page

```nginx
server {
    listen 127.0.0.1:8080;
    server_name 127.0.0.1;
    
    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
```

### Metrics

- Active connections
- Accepted connections
- Handled connections
- Requests per second
- Reading/Writing/Waiting connections

### Logging

- Access logs
- Error logs
- Custom log formats
- Log rotation
- Log levels

## Backup and Recovery

### Configuration Backup

```bash
# Backup Nginx configuration
rsync -avz /etc/nginx/ /backup/nginx/config/

# Backup Let's Encrypt certificates
rsync -avz /etc/letsencrypt/ /backup/letsencrypt/

# Backup web content
rsync -avz /var/www/ /backup/www/
```

### Restoration

```bash
# Restore Nginx configuration
rsync -avz /backup/nginx/config/ /etc/nginx/

# Restore Let's Encrypt certificates
rsync -avz /backup/letsencrypt/ /etc/letsencrypt/

# Restore web content
rsync -avz /backup/www/ /var/www/

# Test configuration and restart Nginx
nginx -t
systemctl restart nginx
```

## Scaling

### Vertical Scaling

- Increase worker processes
- Optimize worker connections
- Tune buffer sizes
- Adjust timeouts
- Optimize SSL/TLS

### Horizontal Scaling

- Load balancing
- Reverse proxy
- Caching layer
- CDN integration
- Global server load balancing (GSLB)

## Tags

- `nginx:install`: Installation tasks
- `nginx:config`: Configuration tasks
- `nginx:ssl`: SSL configuration
- `nginx:security`: Security configuration
- `nginx:performance`: Performance tuning
- `nginx:monitoring`: Monitoring setup
- `nginx:backup`: Backup configuration

## License

Proprietary - All rights reserved
