#!/bin/bash

# Initialize Ceph cluster
sudo ceph-deploy new cbwdellr720 cbwhpz

# Install Ceph on all nodes
sudo ceph-deploy install cbwdellr720 cbwhpz

# Copy admin key and configuration
sudo ceph-deploy admin cbwdellr720 cbwhpz
sudo chmod +r /etc/ceph/ceph.client.admin.keyring

# Create initial monitor
sudo ceph-deploy mon create-initial

# Create OSDs on each node
for node in cbwdellr720 cbwhpz; do
    for disk in sdb sdc sdd sde sdf sdg sdh sdi sdj sdk sdl sdm sdn sdo sdp sdq sdr sds sdt sdu sdv sdw sdx sdy sdz; do
        sudo ceph-deploy osd create $node:/dev/$disk
    done
    sudo ceph-deploy osd activate $node:/dev/$disk

done

# Create CephFS
sudo ceph-deploy mds create cbwdellr720
sudo ceph-deploy mds create cbwhpz

# Create shared directories
sudo mkdir -p /mnt/ceph/fs1 /mnt/ceph/fs2
sudo ceph-deploy fs create cephfs cephfs_data cephfs_metadata
sudo ceph-deploy fs add_data cephfs cephfs_data
sudo ceph-deploy fs add_metadata cephfs cephfs_metadata

# Mount CephFS
sudo mount -t ceph 172.28.158.179:6789:/ /mnt/ceph/fs1 -o name=admin,secret=$(ceph auth get-key client.admin)
sudo mount -t ceph 172.28.158.179:6789:/ /mnt/ceph/fs2 -o name=admin,secret=$(ceph auth get-key client.admin)

# Create NFS exports
sudo mkdir -p /mnt/nfs/ceph
sudo mount -t ceph 172.28.158.179:6789:/ /mnt/nfs/ceph -o name=admin,secret=$(ceph auth get-key client.admin)

# Export NFS shares
sudo bash -c 'echo "/mnt/nfs/ceph *(rw,sync,no_subtree_check)" >> /etc/exports'
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
