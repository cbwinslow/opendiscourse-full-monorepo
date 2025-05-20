#!/bin/bash

# Check if we're running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Check system info
echo "=== System Info ==="
lsb_release -a 2>/dev/null || cat /etc/os-release

# Check Ceph packages
echo "=== Installed Ceph Packages ==="
dpkg -l | grep ceph

# Check available disks
echo "=== Available Disks ==="
lsblk

# Check mounted filesystems
echo "=== Mounted Filesystems ==="
df -h

# Check NFS status
echo "=== NFS Status ==="
showmount -e localhost

# Check Ceph status if installed
echo "=== Ceph Status ==="
which ceph && ceph -s 2>/dev/null
