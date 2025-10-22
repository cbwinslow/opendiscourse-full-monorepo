#!/bin/bash
# Maintenance script for opendiscourse.net

# Check disk usage
echo "=== Disk Usage ==="
df -h

# Check memory usage
echo -e "\n=== Memory Usage ==="
free -h

# Check running containers
echo -e "\n=== Running Containers ==="
docker ps

# Check service status
echo -e "\n=== Service Status ==="
systemctl status nginx traefik caddy docker

# Check logs for errors
echo -e "\n=== Recent Errors in Logs ==="
journalctl -u nginx -u traefik -u caddy --since "24 hours ago" | grep -i error | tail -n 20

# Check certificate expiration
echo -e "\n=== SSL Certificate Expiration ==="
for domain in opendiscourse.net www.opendiscourse.net; do
    echo -n "$domain: "
    echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates
    echo "---"
done

# Check backup status
echo -e "\n=== Backup Status ==="
ls -lh /backups/

# Check scheduled tasks
echo -e "\n=== Scheduled Tasks ==="
ls -la /etc/cron.d/

# System updates
echo -e "\n=== Available Updates ==="
apt list --upgradable 2>/dev/null
