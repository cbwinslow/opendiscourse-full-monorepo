#!/bin/bash

# Add Ceph repository
wget -q -O- 'https://download.ceph.com/keys/release.asc' | apt-key add -
echo deb https://download.ceph.com/debian-nautilus/ $(lsb_release -sc) main | tee /etc/apt/sources.list.d/ceph.list

# Add Kubernetes repository
curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list

# Update package lists
apt-get update

# Install Ceph packages
apt-get install -y ceph-deploy ceph-common ceph-fuse rbdmap
