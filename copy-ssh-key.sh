#!/bin/bash

# Copy SSH key to both nodes
ssh-copy-id -i /home/cbwinslow/CascadeProjects/windsurf-project/ssh-keys/cluster-key.pub cbwinslow@172.28.158.179
ssh-copy-id -i /home/cbwinslow/CascadeProjects/windsurf-project/ssh-keys/cluster-key.pub cbwinslow@172.28.16.143

# Verify connectivity
ssh -i /home/cbwinslow/CascadeProjects/windsurf-project/ssh-keys/cluster-key cbwinslow@172.28.158.179 echo "SSH to cbwdellr720 successful"
ssh -i /home/cbwinslow/CascadeProjects/windsurf-project/ssh-keys/cluster-key cbwinslow@172.28.16.143 echo "SSH to cbwhpz successful"
