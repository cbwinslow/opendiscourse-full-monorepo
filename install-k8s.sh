#!/bin/bash

# Function to install Kubernetes on Ubuntu
install_k8s_ubuntu() {
    echo "Installing Kubernetes on Ubuntu..."
    
    # Add Kubernetes repository
    sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    
    # Install Kubernetes components
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
    
    # Enable br_netfilter
    sudo modprobe br_netfilter
    echo '1' | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables
    
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
}

# Function to install Kubernetes on RHEL
install_k8s_rhel() {
    echo "Installing Kubernetes on RHEL..."
    
    # Install required packages
    sudo dnf install -y yum-utils device-mapper-persistent-data lvm2
    
    # Add Kubernetes repository
    sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo dnf config-manager --add-repo https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
    sudo dnf install -y https://packages.cloud.google.com/yum/doc/yum-key.gpg
    sudo dnf install -y https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
    
    # Install Kubernetes components
    sudo dnf install -y kubelet kubeadm kubectl docker-ce docker-ce-cli containerd.io
    sudo systemctl enable --now kubelet
    sudo systemctl enable --now docker
    
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
}

# Detect OS and install appropriate components
if [ -f /etc/os-release ]; then
    . /etc/os-release
    
    case $NAME in
        "Ubuntu")
            install_k8s_ubuntu
            ;;
        "Red Hat Enterprise Linux"*)
            install_k8s_rhel
            ;;
        *)
            echo "Unsupported OS: $NAME"
            exit 1
            ;;
    esac
fi
