#!/bin/bash

# Initialize master node
sudo kubeadm init --config=/etc/kubernetes/kubeadm-config.yaml --control-plane-endpoint="172.28.158.179:6443"

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

# Install Ceph CSI driver
helm repo add ceph-csi https://ceph.github.io/csi-charts
helm repo update
helm install ceph-csi ceph-csi/ceph-csi-rbd --namespace kube-system

# Create storage classes
kubectl apply -f - <<EOF
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

# Create persistent volume claims
kubectl apply -f - <<EOF
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

# Create deployment using Ceph storage
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ceph-app
spec:
  replicas: 2  # Reduced from 3 to match our 2-node cluster
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
