#!/bin/bash

# Install Python packages
python3 -m pip install -r requirements.txt

# Copy API files
sudo cp opendiscourse-api.py /usr/local/bin/
sudo cp opendiscourse-api.service /etc/systemd/system/

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable opendiscourse-api
sudo systemctl start opendiscourse-api
