# Docker Role

This role installs and configures Docker and Docker Compose on the target hosts.

## Features

- Docker CE installation
- Docker Compose installation
- Docker daemon configuration
- Docker network setup
- Docker storage configuration
- Docker logging configuration
- Non-root user access configuration

## Requirements

- Common role (for base system configuration)
- Ubuntu 20.04/22.04 or compatible
- Internet access for package installation

## Role Variables

### Required Variables

- `docker_users`: List of users to add to the docker group
  ```yaml
  docker_users:
    - deploy
    - admin
  ```

### Optional Variables

- `docker_version`: Docker version to install (default: latest)
- `docker_compose_version`: Docker Compose version (default: v2.20.0)
- `docker_storage_driver`: Storage driver (default: overlay2)
- `docker_log_driver`: Logging driver (default: json-file)
- `docker_log_opts`: Logging options
  ```yaml
  docker_log_opts:
    max-size: "10m"
    max-file: "3"
  ```
- `docker_registry_mirrors`: List of registry mirrors
- `docker_insecure_registries`: List of insecure registries
- `docker_daemon_config`: Additional daemon.json configuration

## Dependencies

- common

## Example Playbook

```yaml
- hosts: docker_hosts
  become: true
  roles:
    - role: docker
      vars:
        docker_users: ['deploy', 'admin']
        docker_daemon_config:
          log-driver: json-file
          log-opts:
            max-size: 10m
            max-file: "3"
          storage-driver: overlay2
          storage-opts:
            - "overlay2.override_kernel_check=true"
```

## Configuration

### Docker Daemon

The Docker daemon configuration is managed through `/etc/docker/daemon.json`. The template can be found in `templates/daemon.json.j2`.

### Docker Networks

By default, the following networks are created:
- `monitoring`
- `backend`
- `frontend`
- `database`

### Storage

- Default storage driver: `overlay2`
- Data root: `/var/lib/docker`
- Configured to use `aufs` if `overlay2` is not available

## Security

- Non-root user access configured
- TLS for Docker daemon (optional)
- AppArmor profile loaded
- Seccomp profile applied

## Tags

- `docker:install`: Install Docker and dependencies
- `docker:config`: Configure Docker daemon
- `docker:compose`: Install Docker Compose
- `docker:networks`: Create Docker networks

## License

Proprietary - All rights reserved
