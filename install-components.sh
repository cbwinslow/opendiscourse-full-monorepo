#!/bin/bash
set -euo pipefail

# install-components.sh - Install Docker, Kubernetes, and Ceph components
#
# USAGE:
#   sudo ./install-components.sh [--help]
#
# DESCRIPTION:
#   This script automatically detects the operating system and installs
#   the required components for the OpenDiscourse infrastructure:
#   - Docker and Docker Compose
#   - Kubernetes (kubelet, kubeadm, kubectl)
#   - Ceph storage cluster tools
#   - Basic system utilities
#
# REQUIREMENTS:
#   - Must be run as root or with sudo
#   - Internet connection for downloading packages
#   - Supported OS: Ubuntu or Red Hat Enterprise Linux
#
# ENVIRONMENT:
#   No special environment variables required
#
# EXAMPLES:
#   sudo ./install-components.sh
#   sudo ./install-components.sh --help

# Function to display help
show_help() {
    echo "install-components.sh - Install Docker, Kubernetes, and Ceph components"
    echo ""
    echo "USAGE:"
    echo "  sudo ./install-components.sh [--help]"
    echo ""
    echo "OPTIONS:"
    echo "  --help, -h    Show this help message and exit"
    echo ""
    echo "DESCRIPTION:"
    echo "  Automatically detects OS and installs required infrastructure components"
    echo ""
    echo "SUPPORTED OS:"
    echo "  - Ubuntu"
    echo "  - Red Hat Enterprise Linux"
    echo ""
    echo "COMPONENTS INSTALLED:"
    echo "  - Docker CE and containerd"
    echo "  - Kubernetes (kubelet, kubeadm, kubectl)"
    echo "  - Ceph deployment tools"
    echo "  - System utilities (curl, wget, git, htop, vim)"
    exit 0
}

# Check for help flag
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    show_help
fi

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root or with sudo" >&2
   echo "Usage: sudo $0" >&2
   exit 1
fi

# Verify internet connectivity
if ! ping -c 1 google.com &> /dev/null; then
    echo "Error: No internet connection detected. Please check your network." >&2
    exit 1
fi

# Function to install components on Ubuntu
install_ubuntu() {
    echo "Installing components on Ubuntu..."
    
    # Update system
    echo "Updating package repositories..."
    apt-get update && apt-get upgrade -y
    
    # Install basic tools
    echo "Installing basic system utilities..."
    apt-get install -y curl wget git htop vim
    
    # Install Docker
    echo "Installing Docker..."
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    systemctl enable docker
    systemctl start docker
    
    # Install Ceph
    echo "Installing Ceph deployment tools..."
    apt-get install -y ceph-deploy
    
    # Install Kubernetes
    echo "Installing Kubernetes components..."
    curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
    apt-get update
    apt-get install -y kubelet kubeadm kubectl
    apt-mark hold kubelet kubeadm kubectl
    
    echo "Ubuntu installation completed successfully!"
}

# Function to install components on RHEL
install_rhel() {
    echo "Installing components on RHEL..."
    
    # Install basic tools
    echo "Installing basic system utilities..."
    dnf install -y curl wget git htop vim
    
    # Install Docker
    echo "Installing Docker..."
    dnf install -y yum-utils
    dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    dnf install -y docker-ce docker-ce-cli containerd.io
    systemctl enable --now docker
    
    # Install Ceph
    echo "Installing Ceph deployment tools..."
    dnf install -y ceph-deploy
    
    # Install Kubernetes
    echo "Installing Kubernetes components..."
    dnf config-manager --add-repo https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
    dnf install -y https://packages.cloud.google.com/yum/doc/yum-key.gpg
    dnf install -y https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
    dnf install -y kubelet kubeadm kubectl
    systemctl enable --now kubelet
    
    echo "RHEL installation completed successfully!"
}

# Detect OS and install appropriate components
echo "Detecting operating system..."
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    echo "Detected OS: $NAME"
    
    case "$NAME" in
        "Ubuntu")
            install_ubuntu
            ;;
        "Red Hat Enterprise Linux"*)
            install_rhel
            ;;
        *)
            echo "Error: Unsupported OS: $NAME" >&2
            echo "This script supports Ubuntu and Red Hat Enterprise Linux only." >&2
            exit 1
            ;;
    esac
else
    echo "Error: Cannot detect operating system. /etc/os-release not found." >&2
    exit 1
fi

echo ""
echo "Installation completed successfully!"
echo "Docker, Kubernetes, and Ceph components have been installed."
echo ""
echo "Next steps:"
echo "1. Add your user to the docker group: sudo usermod -aG docker \$USER"
echo "2. Log out and log back in for group changes to take effect"
echo "3. Verify Docker installation: docker --version"
echo "4. Verify Kubernetes installation: kubectl version --client"
