#!/bin/bash

# Check if Ceph is installed
if ! command -v ceph &> /dev/null; then
    echo "Ceph is not installed"
    exit 1
fi

# Check if we're running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Check Ceph cluster status
echo "=== Detailed Ceph Status ==="
ceph -s

# Check OSD status
echo "=== OSD Status ==="
ceph osd stat
ceph osd tree

# Check MDS status
echo "=== MDS Status ==="
ceph mds stat

# Check FS status
echo "=== Filesystem Status ==="
ceph fs ls

# Check mounted filesystems
echo "=== Mounted Filesystems ==="
df -h /mnt/ceph/*

# Check Ceph configuration
echo "=== Ceph Configuration ==="
ls -la /etc/ceph/

# Check Ceph logs
echo "=== Recent Ceph Logs ==="
journalctl -u ceph-mon -u ceph-osd -n 20

# Check Ceph health in detail
echo "=== Detailed Health Check ==="
ceph health detail
