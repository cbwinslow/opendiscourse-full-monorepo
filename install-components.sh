#!/bin/bash

# Function to install components on Ubuntu
install_ubuntu() {
    echo "Installing components on Ubuntu..."
    
    # Update system
    apt-get update && apt-get upgrade -y
    
    # Install basic tools
    apt-get install -y curl wget git htop vim
    
    # Install Docker
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Install Ceph
    apt-get install -y ceph-deploy
    
    # Install Kubernetes
    curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
    apt-get update
    apt-get install -y kubelet kubeadm kubectl
    apt-mark hold kubelet kubeadm kubectl
}

# Function to install components on RHEL
install_rhel() {
    echo "Installing components on RHEL..."
    
    # Install basic tools
    dnf install -y curl wget git htop vim
    
    # Install Docker
    dnf install -y yum-utils
    dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    dnf install -y docker-ce docker-ce-cli containerd.io
    systemctl enable --now docker
    
    # Install Ceph
    dnf install -y ceph-deploy
    
    # Install Kubernetes
    dnf config-manager --add-repo https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
    dnf install -y https://packages.cloud.google.com/yum/doc/yum-key.gpg
    dnf install -y https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
    dnf install -y kubelet kubeadm kubectl
    systemctl enable --now kubelet
}

# Detect OS and install appropriate components
if [ -f /etc/os-release ]; then
    . /etc/os-release
    
    case $NAME in
        "Ubuntu")
            install_ubuntu
            ;;
        "Red Hat Enterprise Linux"*)
            install_rhel
            ;;
        *)
            echo "Unsupported OS: $NAME"
            exit 1
            ;;
    esac
fi
