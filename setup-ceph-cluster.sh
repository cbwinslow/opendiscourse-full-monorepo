#!/bin/bash

# Function to install Ceph on Ubuntu
install_ceph_ubuntu() {
    echo "Installing Ceph on Ubuntu..."
    
    # Add Ceph repository
    wget -q -O- 'https://download.ceph.com/keys/release.asc' | apt-key add -
    echo deb https://download.ceph.com/debian-nautilus/ $(lsb_release -sc) main | tee /etc/apt/sources.list.d/ceph.list
    
    # Install Ceph packages
    apt-get update
    apt-get install -y ceph-deploy ceph-common ceph-fuse rbdmap
}

# Function to install Ceph on RHEL
install_ceph_rhel() {
    echo "Installing Ceph on RHEL..."
    
    # Install required packages
    dnf install -y yum-utils
    
    # Add Ceph repository
    dnf config-manager --add-repo https://download.ceph.com/rpm-nautilus/el8/ceph.repo
    
    # Install Ceph packages
    dnf install -y ceph-deploy ceph-common ceph-fuse rbdmap
}

# Function to initialize Ceph cluster
init_ceph_cluster() {
    # Create Ceph configuration directory
    mkdir -p ~/ceph-config
    cd ~/ceph-config
    
    # Initialize cluster
    ceph-deploy new cbwdellr720 cbwhpz
    
    # Update configuration file
    sed -i '/mon_initial_members/c\mon_initial_members = cbwdellr720,cbwhpz' ceph.conf
    sed -i '/mon_host/c\mon_host = 172.28.158.179,172.28.16.143' ceph.conf
    
    # Install Ceph on all nodes
    ceph-deploy install cbwdellr720 cbwhpz
    
    # Copy admin key and configuration
    ceph-deploy admin cbwdellr720 cbwhpz
    chmod +r /etc/ceph/ceph.client.admin.keyring
    
    # Create initial monitor
    ceph-deploy mon create-initial
    
    # Create OSDs on each node
    for node in cbwdellr720 cbwhpz; do
        for disk in sdb sdc sdd sde sdf sdg sdh sdi sdj sdk sdl sdm sdn sdo sdp sdq sdr sds sdt sdu sdv sdw sdx sdy sdz; do
            ceph-deploy osd create $node:/dev/$disk
        done
    done
    
    # Create CephFS
    ceph-deploy mds create cbwdellr720
    ceph-deploy mds create cbwhpz
    
    # Create shared directories
    mkdir -p /mnt/ceph/fs1 /mnt/ceph/fs2
    
    # Mount CephFS
    mount -t ceph 172.28.158.179:6789:/ /mnt/ceph/fs1 -o name=admin,secret=$(ceph auth get-key client.admin)
    mount -t ceph 172.28.158.179:6789:/ /mnt/ceph/fs2 -o name=admin,secret=$(ceph auth get-key client.admin)
    
    # Create NFS exports
    mkdir -p /mnt/nfs/ceph
    mount -t ceph 172.28.158.179:6789:/ /mnt/nfs/ceph -o name=admin,secret=$(ceph auth get-key client.admin)
    
    # Export NFS shares
    echo '/mnt/nfs/ceph *(rw,sync,no_subtree_check)' >> /etc/exports
    exportfs -a
    systemctl restart nfs-kernel-server
}

# Detect OS and install Ceph
if [ -f /etc/os-release ]; then
    . /etc/os-release
    
    case $NAME in
        "Ubuntu")
            install_ceph_ubuntu
            ;;
        "Red Hat Enterprise Linux"*)
            install_ceph_rhel
            ;;
        *)
            echo "Unsupported OS: $NAME"
            exit 1
            ;;
    esac
fi

# Initialize Ceph cluster if we're on the master node
if [ "$HOSTNAME" = "cbwdellr720" ]; then
    init_ceph_cluster
fi
