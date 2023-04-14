#!/bin/bash

# Run the command with sudo and redirect the input to the file
sudo bash -c "cat > /etc/systemd/system/gunicorn.socket <<EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF"