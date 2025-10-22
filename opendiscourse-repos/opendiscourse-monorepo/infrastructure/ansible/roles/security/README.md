# Security Role

This role implements advanced security measures to harden the OpenDiscourse infrastructure.

## Features

- Fail2ban configuration for SSH and web services
- Intrusion detection with AIDE (Advanced Intrusion Detection Environment)
- Security audit with Lynis
- Malware scanning with ClamAV
- Rootkit detection with rkhunter
- System hardening with CIS benchmarks
- Security headers for web services
- SSL/TLS configuration
- Security-related cron jobs

## Requirements

- Common role (for base system configuration)
- Root or sudo access
- Internet access for package installation

## Role Variables

### Required Variables

- `fail2ban_ignoreip`: List of IPs to exclude from Fail2ban

### Optional Variables

- `security_audit_enabled`: Run security audit (default: true)
- `malware_scan_enabled`: Enable malware scanning (default: true)
- `rootkit_scan_enabled`: Enable rootkit detection (default: true)
- `cis_hardening_enabled`: Apply CIS benchmarks (default: true)
- `security_headers_enabled`: Add security headers (default: true)
- `fail2ban_jails`: Custom Fail2ban jails
  ```yaml
  fail2ban_jails:
    - name: sshd
      enabled: true
      port: ssh
      filter: sshd
      logpath: /var/log/auth.log
      maxretry: 3
      findtime: 600
      bantime: 3600
  ```

## Dependencies

- common

## Example Playbook

```yaml
- hosts: all
  become: true
  roles:
    - role: security
      vars:
        fail2ban_ignoreip: ['127.0.0.1/8', '192.168.1.0/24']
        security_audit_enabled: true
        malware_scan_enabled: true
        rootkit_scan_enabled: true
        cis_hardening_enabled: true
        security_headers_enabled: true
```

## Security Measures

### 1. Fail2ban Configuration
- Protects against brute force attacks
- Custom jails for different services
- Email notifications for banned IPs
- Whitelist trusted IPs

### 2. Intrusion Detection (AIDE)
- Monitors file system for changes
- Daily integrity checks
- Email alerts on changes

### 3. Security Audit (Lynis)
- System hardening index
- Security controls testing
- Compliance with standards
- Detailed reporting

### 4. Malware Scanning (ClamAV)
- Daily malware scans
- Quarantine of infected files
- Email notifications

### 5. Rootkit Detection (rkhunter)
- System binary checks
- Rootkit signatures
- Suspicious file detection

### 6. CIS Hardening
- System-wide security baselines
- Kernel parameter tuning
- Service hardening
- File system permissions

## Maintenance

### Security Updates
- Automatic security updates
- Regular vulnerability scanning
- Patch management

### Logging and Monitoring
- Centralized logging
- Security event correlation
- Real-time alerts

## Backup and Recovery
- Configuration backups
- Incident response plan
- Disaster recovery procedures

## Tags

- `security:fail2ban`: Configure Fail2ban
- `security:audit`: Run security audit
- `security:malware`: Malware scanning
- `security:rootkit`: Rootkit detection
- `security:cis`: CIS hardening
- `security:headers`: Security headers

## License

Proprietary - All rights reserved
