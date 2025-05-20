#!/bin/bash

# Check Kubernetes installation on both nodes
for node in "172.28.158.179" "172.28.16.143"; do
    echo "Checking $node..."
    ssh -i ssh-keys/cluster-key cbwinslow@$node "
        echo "=== System Info ==="
        lsb_release -a 2>/dev/null || cat /etc/os-release
        echo "=== Docker Info ==="
        docker --version
        echo "=== Kubernetes Components ==="
        which kubeadm && kubeadm version
        which kubelet && kubelet --version
        which kubectl && kubectl version --client
        echo "=== Ceph Info ==="
        which ceph-deploy && ceph-deploy --version
        echo "=== Network Info ==="
        ip addr show
        echo "=== Firewall Status ==="
        ufw status
    "
done
