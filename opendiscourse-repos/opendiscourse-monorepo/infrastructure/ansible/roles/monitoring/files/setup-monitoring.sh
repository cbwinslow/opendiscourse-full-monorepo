#!/bin/bash
# Setup monitoring stack for opendiscourse.net

# Create Docker network if it doesn't exist
docker network create monitoring 2>/dev/null || true

# Create directories for persistent storage
mkdir -p /data/{grafana,prometheus,loki,alertmanager}
chown -R 472:0 /data/grafana
chmod -R 775 /data/grafana

# Create docker-compose file
cat > /opt/monitoring/docker-compose.yml << 'EOL'
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - /opt/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - /data/prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports: ["9090:9090"]
    networks: [monitoring]

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    volumes:
      - /data/grafana:/var/lib/grafana
      - /opt/monitoring/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    ports: ["3000:3000"]
    networks: [monitoring]

  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    volumes: [/data/loki:/loki]
    ports: ["3100:3100"]
    networks: [monitoring]

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    restart: unless-stopped
    volumes:
      - /var/log:/var/log
      - /opt/monitoring/promtail-config.yaml:/etc/promtail/config.yaml
    command: -config.file=/etc/promtail/config.yaml
    networks: [monitoring]

networks:
  monitoring:
    external: true
EOL

# Create Prometheus config
cat > /opt/monitoring/prometheus.yml << 'EOL'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs: [{targets: ['localhost:9090']}]
  - job_name: 'node'
    static_configs: [{targets: ['node-exporter:9100']}]
  - job_name: 'opendiscourse'
    metrics_path: '/metrics'
    static_configs: [{targets: ['opendiscourse:8000']}]
EOL

# Create Promtail config
cat > /opt/monitoring/promtail-config.yaml << 'EOL'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets: [localhost]
        labels:
          job: varlogs
          __path__: /var/log/*log
EOL

echo "Monitoring stack configuration complete. Run with:"
echo "cd /opt/monitoring && docker-compose up -d"
