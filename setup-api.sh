#!/bin/bash

# Install Python packages
python3 -m pip install -r requirements.txt

# Copy API files
sudo cp doc-repo-api.py /usr/local/bin/
sudo cp doc-repo-api.service /etc/systemd/system/

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable doc-repo-api
sudo systemctl start doc-repo-api
