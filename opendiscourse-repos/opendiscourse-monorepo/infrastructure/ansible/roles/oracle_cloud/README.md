# Oracle Cloud Role

This role manages Oracle Cloud Infrastructure (OCI) resources for the OpenDiscourse platform, including compute instances, databases, and storage.

## Features

### Compute Management
- VM instance provisioning
- Instance configuration
- SSH key management
- Security list configuration
- Boot volume management

### Database Management
- Autonomous Database provisioning
- Database backups
- Performance tuning
- User management

### Storage Management
- Block Volume provisioning
- File Storage setup
- Object Storage configuration
- Backup policies

### Networking
- VCN (Virtual Cloud Network) setup
- Subnet configuration
- Internet Gateway
- NAT Gateway
- Service Gateway
- Load Balancer
- DNS configuration

## Requirements

- OCI CLI installed and configured
- Required Python packages:
  - oci
  - oci-cli
- Sufficient OCI service limits
- Appropriate IAM policies

## Role Variables

### Required Variables

```yaml
# OCI Authentication
oci_config_file: "~/.oci/config"
oci_profile: "DEFAULT"
oci_compartment_id: "ocid1.compartment.oc1..example"
oci_region: "us-ashburn-1"

# SSH Keys
oci_ssh_public_key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
oci_ssh_private_key: "{{ lookup('file', '~/.ssh/id_rsa') }}"
```

### Optional Variables

```yaml
# Compute Instance
oci_compute_instances:
  - name: "opendiscourse-app"
    availability_domain: "XXXX:US-ASHBURN-AD-1"
    shape: "VM.Standard.E4.Flex"
    ocpus: 2
    memory_in_gbs: 16
    source_id: "ocid1.image.oc1..example"
    subnet_id: "ocid1.subnet.oc1.iad.example"
    assign_public_ip: true
    boot_volume_size_in_gbs: 100
    metadata:
      ssh_authorized_keys: "{{ oci_ssh_public_key }}"

# Autonomous Database
oci_autonomous_databases:
  - name: "opendiscourse-db"
    db_name: "opendiscourse"
    admin_password: "{{ vault_oci_db_password }}"
    cpu_core_count: 1
    data_storage_size_in_tbs: 1
    license_model: "LICENSE_INCLUDED"
    is_free_tier: true

# Block Volume
oci_block_volumes:
  - name: "opendiscourse-data"
    availability_domain: "XXXX:US-ASHBURN-AD-1"
    size_in_gbs: 200
    vpus_per_gb: 10
    backup_policy: "Bronze"
```

## Dependencies

- python3-pip
- oci-cli (installed by the role)
- oci-python-sdk (installed by the role)

## Example Playbook

```yaml
- hosts: localhost
  connection: local
  roles:
    - role: oracle_cloud
      vars:
        oci_config_file: "~/.oci/config"
        oci_profile: "DEFAULT"
        oci_compartment_id: "{{ vault_oci_compartment_id }}"
        oci_region: "us-ashburn-1"
        
        oci_compute_instances:
          - name: "opendiscourse-app"
            availability_domain: "XXXX:US-ASHBURN-AD-1"
            shape: "VM.Standard.E4.Flex"
            ocpus: 2
            memory_in_gbs: 16
            source_id: "ocid1.image.oc1..example"
            subnet_id: "{{ oci_subnet_id }}"
            assign_public_ip: true
            metadata:
              ssh_authorized_keys: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
```

## Configuration

### OCI CLI Configuration

1. Install OCI CLI:
   ```bash
   bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
   ```

2. Configure OCI CLI:
   ```bash
   oci setup config
   ```

3. Upload API signing key to OCI console

### Terraform Integration

This role can work alongside Terraform for infrastructure management:

```hcl
# Example Terraform configuration for OCI
provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  region       = var.region
}

resource "oci_core_instance" "opendiscourse" {
  # Instance configuration
}
```

## Security

- Use instance principals where possible
- Encrypt sensitive data with Ansible Vault
- Implement least privilege IAM policies
- Enable VCN flow logs
- Use security lists and NSGs

## Monitoring

- OCI Monitoring service integration
- Custom metrics and alarms
- Service Connector Hub for logs
- Notifications via ONS

## Backup and Recovery

### Compute Instances
- Custom image creation
- Boot volume backups
- Instance configurations

### Databases
- Automated backups
- Manual backups
- Point-in-time recovery

### Block Volumes
- Volume backups
- Volume group backups
- Cross-region replication

## Tags

- `oci:compute`: Compute instance tasks
- `oci:database`: Database tasks
- `oci:storage`: Storage tasks
- `oci:network`: Networking tasks
- `oci:config`: Configuration tasks

## License

Proprietary - All rights reserved
