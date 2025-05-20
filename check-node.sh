#!/bin/bash

# Check if we're running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Check system info
echo "=== System Info ==="
lsb_release -a 2>/dev/null || cat /etc/os-release

# Check Docker status
echo "=== Docker Status ==="
docker --version
docker info

# Check Kubernetes components
echo "=== Kubernetes Components ==="
which kubeadm && kubeadm version
which kubelet && kubelet --version
which kubectl && kubectl version --client

# Check network interfaces
echo "=== Network Interfaces ==="
ip addr show

# Check firewall status
echo "=== Firewall Status ==="
ufw status 2>/dev/null || echo "ufw not installed"

# Check Ceph status
echo "=== Ceph Status ==="
which ceph-deploy && ceph-deploy --version
which ceph && ceph -s 2>/dev/null
