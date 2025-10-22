# RabbitMQ Ansible Role

This role installs and configures RabbitMQ message broker with support for clustering, SSL/TLS, monitoring, and more.

## Features

- Install and configure RabbitMQ server
- Configure users, vhosts, and permissions
- Set up SSL/TLS encryption
- Configure clustering
- Enable monitoring via Prometheus
- LDAP authentication support
- Resource limits and performance tuning
- Systemd service management
- Logging configuration

## Requirements

- Ansible 2.9+
- Debian/Ubuntu Linux
- Root privileges

## Role Variables

All variables have sensible defaults. The main configuration options are:

### Core Configuration

- `rabbitmq_service_name`: Service name (default: `rabbitmq-server`)
- `rabbitmq_tcp_port`: AMQP port (default: `5672`)
- `rabbitmq_management_port`: Management UI port (default: `15672`)
- `rabbitmq_management_bind_ip`: Management interface binding (default: `0.0.0.0`)

### SSL/TLS Configuration

- `rabbitmq_ssl_enabled`: Enable SSL (default: `false`)
- `rabbitmq_ssl_port`: SSL port (default: `5671`)
- `rabbitmq_ssl_ca_cert`: CA certificate path
- `rabbitmq_ssl_cert`: Server certificate path
- `rabbitmq_ssl_key`: Server private key path

### Authentication

- `rabbitmq_default_user`: Default user (default: `guest`)
- `rabbitmq_default_pass`: Default password (default: `guest`)
- `rabbitmq_allow_guest`: Allow guest access (default: `false`)
- `rabbitmq_users`: List of users to create
- `rabbitmq_vhosts`: List of vhosts to create

### Performance Tuning

- `rabbitmq_memory_high_watermark`: Memory threshold (default: `0.4`)
- `rabbitmq_disk_free_limit`: Disk space threshold (default: `2GB`)
- `rabbitmq_nofile_limit`: File descriptor limit (default: `65536`)
- `rabbitmq_max_connections`: Max connections (default: `1000`)
- `rabbitmq_max_channels`: Max channels per connection (default: `128`)

### Monitoring

- `rabbitmq_prometheus_enabled`: Enable Prometheus metrics (default: `true`)
- `rabbitmq_prometheus_port`: Prometheus metrics port (default: `15692`)

## Dependencies

- `common` role (base system configuration)
- `monitoring` role (when Prometheus is enabled)
- `security` role (when SSL is enabled)

## Example Playbook

```yaml
- hosts: rabbitmq_servers
  roles:
    - role: rabbitmq
      rabbitmq_users:
        - user: admin
          password: "{{ vault_rabbitmq_admin_password }}"
          vhost: /
          configure_priv: '.*'
          write_priv: '.*'
          read_priv: '.*'
          tags: administrator
        - user: worker
          password: "{{ vault_rabbitmq_worker_password }}"
          vhost: /ai
          configure_priv: ''
          write_priv: '.*'
          read_priv: '.*'
          tags: monitoring
      
      rabbitmq_ssl_enabled: true
      rabbitmq_ssl_ca_cert: /etc/ssl/certs/ca-cert.pem
      rabbitmq_ssl_cert: /etc/ssl/certs/rabbitmq.pem
      rabbitmq_ssl_key: /etc/ssl/private/rabbitmq-key.pem
      
      rabbitmq_policies:
        - name: ha-policy
          vhost: /
          pattern: '^ha\..*'
          definition:
            ha-mode: all
            ha-sync-mode: automatic
          priority: 0
          apply-to: all
```

## Testing

To test the role with Molecule:

```bash
molecule test
```

## License

MIT

## Author Information

Windsurf Project
