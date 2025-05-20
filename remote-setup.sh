#!/bin/bash

# Function to run commands on remote nodes
run_on_node() {
    local node=$1
    shift
    local commands="$@"
    
    ssh -i /home/cbwinslow/CascadeProjects/windsurf-project/ssh-keys/cluster-key cbwinslow@$node "sudo bash -c '$commands'"
}

# Nodes to configure
NODES=("172.28.158.179" "172.28.16.143")

# Basic system setup
for node in "${NODES[@]}"; do
    echo "Setting up basic system on $node..."
    run_on_node $node "
        apt-get update && apt-get upgrade -y
        apt-get install -y curl wget git htop vim lsb-release
        apt-get install -y apt-transport-https ca-certificates curl software-properties-common
        apt-get install -y ceph-deploy
        apt-get install -y kubelet kubeadm kubectl
        apt-mark hold kubelet kubeadm kubectl
        modprobe br_netfilter
        echo '1' | tee /proc/sys/net/bridge/bridge-nf-call-iptables
        mkdir -p /etc/docker
        echo '{
          \"exec-opts\": [\"native.cgroupdriver=systemd\"],
          \"log-driver\": \"json-file\",
          \"log-opts\": {
            \"max-size\": \"100m\"
          },
          \"storage-driver\": \"overlay2\"
        }' > /etc/docker/daemon.json
        systemctl restart docker
        swapoff -a
        sed -i '/ swap / s/^/#/' /etc/fstab
        ufw allow 6443/tcp
        ufw allow 10250/tcp
        ufw allow 10251/tcp
        ufw allow 10252/tcp
        ufw allow 2379:2380/tcp
        ufw allow 10255/tcp
        ufw allow 30000:32767/tcp
        apt-get install -y ceph-common ceph-fuse rbdmap
        apt-get install -y nfs-kernel-server
        mkdir -p /mnt/ceph /mnt/k8s /mnt/shared
        chmod 777 /mnt/ceph /mnt/k8s /mnt/shared
        echo '/mnt/ceph *(rw,sync,no_subtree_check)' >> /etc/exports
        echo '/mnt/k8s *(rw,sync,no_subtree_check)' >> /etc/exports
        echo '/mnt/shared *(rw,sync,no_subtree_check)' >> /etc/exports
        exportfs -a
        systemctl restart nfs-kernel-server
    "
done

# Initialize Ceph cluster on master node
echo "Initializing Ceph cluster on master node..."
run_on_node 172.28.158.179 "
    ceph-deploy new cbwdellr720 cbwhpz
    ceph-deploy install cbwdellr720 cbwhpz
    ceph-deploy admin cbwdellr720 cbwhpz
    chmod +r /etc/ceph/ceph.client.admin.keyring
    ceph-deploy mon create-initial
    for disk in sdb sdc sdd sde sdf sdg sdh sdi sdj sdk sdl sdm sdn sdo sdp sdq sdr sds sdt sdu sdv sdw sdx sdy sdz; do
        ceph-deploy osd create cbwdellr720:/dev/$disk
        ceph-deploy osd create cbwhpz:/dev/$disk
    done
    ceph-deploy mds create cbwdellr720
    ceph-deploy mds create cbwhpz
    mkdir -p /mnt/ceph/fs1 /mnt/ceph/fs2
    ceph-deploy fs create cephfs cephfs_data cephfs_metadata
    ceph-deploy fs add_data cephfs cephfs_data
    ceph-deploy fs add_metadata cephfs cephfs_metadata
    mount -t ceph 172.28.158.179:6789:/ /mnt/ceph/fs1 -o name=admin,secret=$(ceph auth get-key client.admin)
    mount -t ceph 172.28.158.179:6789:/ /mnt/ceph/fs2 -o name=admin,secret=$(ceph auth get-key client.admin)
    mkdir -p /mnt/nfs/ceph
    mount -t ceph 172.28.158.179:6789:/ /mnt/nfs/ceph -o name=admin,secret=$(ceph auth get-key client.admin)
    echo '/mnt/nfs/ceph *(rw,sync,no_subtree_check)' >> /etc/exports
    exportfs -a
    systemctl restart nfs-kernel-server
"

# Initialize Kubernetes on master node
echo "Initializing Kubernetes on master node..."
run_on_node 172.28.158.179 "
    kubeadm init --pod-network-cidr=10.244.0.0/16 --control-plane-endpoint=\"172.28.158.179:6443\"
    mkdir -p $HOME/.kube
    cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    chown $(id -u):$(id -g) $HOME/.kube/config
    kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
    wget https://get.helm.sh/helm-v3.12.3-linux-amd64.tar.gz
    tar -zxvf helm-v3.12.3-linux-amd64.tar.gz
    mv linux-amd64/helm /usr/local/bin/helm
    wget https://github.com/derailed/k9s/releases/download/v0.30.0/k9s_Linux_x86_64.tar.gz
    tar -zxvf k9s_Linux_x86_64.tar.gz
    mv k9s /usr/local/bin/k9s
    helm repo add ceph-csi https://ceph.github.io/csi-charts
    helm repo update
    helm install ceph-csi ceph-csi/ceph-csi-rbd --namespace kube-system
    kubectl apply -f - << 'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ceph-rbd
provisioner: ceph.com/rbd
parameters:
  monitors: 172.28.158.179:6789,172.28.16.143:6789
  adminId: admin
  adminSecretName: ceph-secret
  adminSecretNamespace: kube-system
  pool: replicapool
  userId: kube
  userSecretName: ceph-secret-user
  imageFeatures: layering
  imageFormat: 2
  fsType: ext4
reclaimPolicy: Retain
EOF
    kubectl apply -f - << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ceph-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: ceph-rbd
EOF
    kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ceph-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ceph-app
  template:
    metadata:
      labels:
        app: ceph-app
    spec:
      containers:
      - name: ceph-container
        image: nginx:latest
        volumeMounts:
        - mountPath: /data
          name: ceph-pvc
      volumes:
      - name: ceph-pvc
        persistentVolumeClaim:
          claimName: ceph-pvc
EOF
"
