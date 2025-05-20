#!/bin/bash

# Check Ceph status on both nodes
for node in "172.28.158.179" "172.28.16.143"; do
    echo "=== Checking node $node ==="
    ssh cbwinslow@$node "
        echo "=== Ceph Status ==="
        ceph -s 2>/dev/null || echo "Ceph not installed"
        
        echo "=== Installed Ceph Packages ==="
        dpkg -l | grep ceph
        
        echo "=== Available Disks ==="
        lsblk
        
        echo "=== Mounted Filesystems ==="
        df -h
        
        echo "=== Network Interfaces ==="
        ip addr show
        
        echo "=== Firewall Status ==="
        sudo ufw status 2>/dev/null || echo "ufw not installed"
    "
done
