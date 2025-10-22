# Monitoring Role

This role sets up and configures the monitoring stack for OpenDiscourse, including:
- Prometheus for metrics collection
- Grafana for visualization
- Loki for log aggregation
- Promtail for log shipping

## Requirements

- Docker and Docker Compose
- Ports 3000 (Grafana), 9090 (Prometheus), 3100 (Loki) available
- Sufficient disk space for metrics and logs

## Role Variables

### Required Variables
- `grafana_admin_password`: Admin password for Grafana (should be stored in vault)
- `monitoring_dir`: Base directory for monitoring configuration (default: /opt/monitoring)

### Optional Variables
- `prometheus_retention`: How long to keep metrics (default: 15d)
- `loki_retention`: How long to keep logs (default: 30d)
- `enable_alerting`: Whether to enable alerting (default: false)
- `alertmanager_config`: Alertmanager configuration (if alerting is enabled)

## Dependencies

- Docker role (for Docker installation)
- Common role (for system configuration)

## Example Playbook

```yaml
- hosts: monitoring_servers
  roles:
    - role: monitoring
      vars:
        grafana_admin_password: "{{ vault_grafana_password }}"
        enable_alerting: true
        alertmanager_config:
          route:
            receiver: 'email'
          receivers:
            - name: 'email'
              email_configs:
                - to: 'alerts@example.com'
```

## Usage

### Accessing the dashboards
- Grafana: http://your-server:3000
- Prometheus: http://your-server:9090
- Loki: http://your-server:3100

### Importing dashboards
Pre-configured dashboards can be found in `templates/grafana-dashboard.json.j2` and will be automatically imported.

### Adding custom metrics
To add custom metrics to be scraped by Prometheus, add them to `files/prometheus.yml.j2`.

## Backup and Restore

Backup scripts are included in the common role to back up:
- Grafana dashboards and configuration
- Prometheus data
- Loki logs

## Security Considerations

- Always use HTTPS in production
- Set strong passwords for all services
- Limit access to monitoring endpoints using firewall rules
- Regularly update the monitoring stack components

## Troubleshooting

Check container logs:
```bash
docker logs prometheus
docker logs grafana
docker logs loki
docker logs promtail
```

Check service status:
```bash
docker ps -a
systemctl status docker
```

## License

Proprietary - All rights reserved
