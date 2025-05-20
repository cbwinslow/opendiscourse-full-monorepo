#!/bin/bash

# Download required packages
wget https://download.docker.com/linux/ubuntu/gpg -O docker.gpg
wget https://get.docker.com -O get-docker.sh
wget https://get.helm.sh/helm-v3.12.3-linux-amd64.tar.gz
wget https://github.com/derailed/k9s/releases/download/v0.30.0/k9s_Linux_x86_64.tar.gz

# Download kubeadm, kubelet, kubectl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Create directories
mkdir -p /tmp/ceph /tmp/kubernetes /tmp/docker /tmp/helm /tmp/k9s

# Move files to appropriate locations
mv docker.gpg /tmp/docker/
mv get-docker.sh /tmp/docker/
mv helm-v3.12.3-linux-amd64.tar.gz /tmp/helm/
mv k9s_Linux_x86_64.tar.gz /tmp/k9s/

# Create setup script
sudo tee /tmp/setup.sh > /dev/null << 'EOL'
#!/bin/bash

# Update system
apt-get update && apt-get upgrade -y

# Install basic tools
apt-get install -y curl wget git htop vim lsb-release

# Install Docker
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
apt-key add /tmp/docker/docker.gpg
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Ceph dependencies
apt-get install -y ceph-deploy

# Install Kubernetes dependencies
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

# Enable br_netfilter
modprobe br_netfilter
echo '1' | tee /proc/sys/net/bridge/bridge-nf-call-iptables

# Configure Docker for Kubernetes
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

# Restart Docker
systemctl restart docker

# Configure swap
swapoff -a
sed -i '/ swap / s/^/#/' /etc/fstab

# Configure firewall
ufw allow 6443/tcp
ufw allow 10250/tcp
ufw allow 10251/tcp
ufw allow 10252/tcp
ufw allow 2379:2380/tcp
ufw allow 10255/tcp
ufw allow 30000:32767/tcp

# Install Ceph prerequisites
apt-get install -y ceph-common ceph-fuse rbdmap

# Install NFS server for shared storage
apt-get install -y nfs-kernel-server

# Create shared directories
mkdir -p /mnt/ceph /mnt/k8s /mnt/shared
chmod 777 /mnt/ceph /mnt/k8s /mnt/shared

# Export NFS shares
echo "/mnt/ceph *(rw,sync,no_subtree_check)" >> /etc/exports
echo "/mnt/k8s *(rw,sync,no_subtree_check)" >> /etc/exports
echo "/mnt/shared *(rw,sync,no_subtree_check)" >> /etc/exports
exportfs -a
systemctl restart nfs-kernel-server

# Install Helm and k9s
tar -zxvf /tmp/helm/helm-v3.12.3-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm
tar -zxvf /tmp/k9s/k9s_Linux_x86_64.tar.gz
mv k9s /usr/local/bin/k9s

# Make scripts executable
chmod +x /tmp/setup.sh
EOL

# Make scripts executable
chmod +x /tmp/setup.sh
