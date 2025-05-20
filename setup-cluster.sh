#!/bin/bash

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install basic tools
sudo apt-get install -y curl wget git htop vim

# Install Docker
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Ceph dependencies
sudo apt-get install -y ceph-deploy

# Install Kubernetes dependencies
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Enable br_netfilter
sudo modprobe br_netfilter
sudo echo '1' | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables

# Configure Docker for Kubernetes
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<<'{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}'

# Restart Docker
sudo systemctl restart docker

# Configure swap
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# Configure firewall
sudo ufw allow 6443/tcp
sudo ufw allow 10250/tcp
sudo ufw allow 10251/tcp
sudo ufw allow 10252/tcp
sudo ufw allow 2379:2380/tcp
sudo ufw allow 10255/tcp
sudo ufw allow 30000:32767/tcp

# Install Ceph prerequisites
sudo apt-get install -y ceph-common ceph-fuse rbdmap

# Install NFS server for shared storage
sudo apt-get install -y nfs-kernel-server

# Create shared directories
sudo mkdir -p /mnt/ceph /mnt/k8s /mnt/shared
sudo chmod 777 /mnt/ceph /mnt/k8s /mnt/shared

# Export NFS shares
sudo bash -c 'echo "/mnt/ceph *(rw,sync,no_subtree_check)" >> /etc/exports'
sudo bash -c 'echo "/mnt/k8s *(rw,sync,no_subtree_check)" >> /etc/exports'
sudo bash -c 'echo "/mnt/shared *(rw,sync,no_subtree_check)" >> /etc/exports'
sudo exportfs -a
sudo systemctl restart nfs-kernel-server

# Install Ceph
sudo ceph-deploy install cbwdellr720 cbwhpz
sudo ceph-deploy mon create-initial
sudo ceph-deploy admin cbwdellr720 cbwhpz
sudo chmod +r /etc/ceph/ceph.client.admin.keyring

# Initialize Kubernetes
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --control-plane-endpoint="172.28.158.179:6443"

# Configure kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install network plugin
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# Install Helm
wget https://get.helm.sh/helm-v3.12.3-linux-amd64.tar.gz
tar -zxvf helm-v3.12.3-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm

# Install k9s
wget https://github.com/derailed/k9s/releases/download/v0.30.0/k9s_Linux_x86_64.tar.gz
tar -zxvf k9s_Linux_x86_64.tar.gz
sudo mv k9s /usr/local/bin/k9s
