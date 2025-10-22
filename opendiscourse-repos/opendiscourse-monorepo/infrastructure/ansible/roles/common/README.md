# Common Role

This role provides base system configuration and security hardening that applies to all servers in the OpenDiscourse infrastructure.

## Features

- System updates and package management
- User and group management
- SSH server hardening
- UFW firewall configuration
- System timezone and NTP configuration
- System monitoring tools
- Common utilities installation

## Requirements

- Ubuntu 20.04/22.04
- Root or sudo access
- Internet access for package installation

## Role Variables

### Required Variables

- `admin_users`: List of admin users to create
  ```yaml
  admin_users:
    - name: admin
      ssh_key: "ssh-rsa AAAA..."
  ```

### Optional Variables

- `timezone`: System timezone (default: "America/New_York")
- `ntp_servers`: List of NTP servers
- `ssh_port`: SSH server port (default: 2222)
- `ssh_password_authentication`: Allow password authentication (default: false)
- `ssh_root_login`: Allow root login (default: false)
- `ufw_default_deny_policy`: Default UFW policy (default: "deny")
- `ufw_rules`: List of UFW rules to apply
  ```yaml
  ufw_rules:
    - { port: 22, proto: tcp, src: 192.168.1.0/24 }
    - { port: 80, proto: tcp }
    - { port: 443, proto: tcp }
  ```

## Dependencies

None. This is a base role that other roles depend on.

## Example Playbook

```yaml
- hosts: all
  become: true
  roles:
    - role: common
      vars:
        admin_users:
          - name: admin
            ssh_key: "{{ vault_admin_ssh_key }}"
        ssh_port: 2222
        ufw_rules:
          - { port: 2222, proto: tcp, src: 0.0.0.0/0 }
          - { port: 80, proto: tcp }
          - { port: 443, proto: tcp }
```

## Security Hardening

This role implements several security best practices:

1. **SSH Hardening**
   - Disables root login
   - Disables password authentication (key-based only)
   - Changes default SSH port (configurable)
   - Uses strong key exchange algorithms
   - Enables X11 forwarding

2. **Firewall**
   - Enables UFW (Uncomplicated Firewall)
   - Default deny policy
   - Configurable rules for services

3. **System Hardening**
   - Automatic security updates
   - Removes unnecessary packages
   - Configures secure sysctl parameters
   - Sets up automatic security updates

## Backup and Restore

This role includes backup and restore scripts in the `files/` directory:

- `backup.sh`: Creates backups of system configuration and data
- `restore.sh`: Restores from backups
- `setup-backup.sh`: Sets up automated backup system

## Maintenance

A maintenance script is included at `files/maintenance.sh` that provides:
- Disk and memory usage
- Running containers
- Service status
- Log error checking
- SSL certificate expiration
- Backup status
- System updates

## Tags

This role supports the following tags for selective execution:

- `common`: Run all tasks
- `common:users`: Only user management tasks
- `common:ssh`: Only SSH configuration
- `common:firewall`: Only firewall configuration
- `common:packages`: Only package management

## License

Proprietary - All rights reserved
