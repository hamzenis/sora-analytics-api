#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Variables
SERVICE_NAME="sora-analytics-api.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
USER_NAME=$(whoami)
WORK_DIR="$SCRIPT_DIR"
EXEC_START="$WORK_DIR/.venv/bin/uvicorn api:app --host 0.0.0.0 --port 47474"

# Stop and disable the existing service if it is running
if systemctl list-units --full -all | grep -q "$SERVICE_NAME"; then
    echo "Stopping existing service..."
    sudo systemctl stop $SERVICE_NAME
    sudo systemctl disable $SERVICE_NAME
fi

# Remove old service file if it exists
if [ -f "$SERVICE_PATH" ]; then
    echo "Removing old service file..."
    sudo rm -f $SERVICE_PATH
fi

# Create the systemd service file with dynamic values
echo "Creating new systemd service file..."
echo "[Unit]
Description=FASTApi Sora Analytics
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$WORK_DIR
ExecStart=$EXEC_START
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_PATH > /dev/null

# Set correct permissions
sudo chmod 644 $SERVICE_PATH

# Reload systemd to recognize the new service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start the new service
echo "Enabling and starting the service..."
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Show service status
echo "Deployment completed. Service status:"
sudo systemctl status $SERVICE_NAME --no-pager
