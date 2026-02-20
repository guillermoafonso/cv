#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash install.sh"
    exit 1
fi

echo "=== Screen Timer Installer ==="

# Install dependencies
echo "Installing dependencies..."
apt-get update -qq
apt-get install -y python3 python3-gi gir1.2-gtk-3.0 gir1.2-gtklayershell-0.1

# Install the main script
echo "Installing screen-timer..."
cp screen-timer.py /usr/local/bin/screen-timer
chmod 755 /usr/local/bin/screen-timer

# Create directories
mkdir -p /etc/screen-timer
mkdir -p /var/lib/screen-timer

# Install config (preserve existing)
if [ ! -f /etc/screen-timer/config.json ]; then
    cp config.json /etc/screen-timer/config.json
    echo "Default config installed to /etc/screen-timer/config.json"
else
    echo "Config already exists, not overwriting."
fi

# Lock down state directory
chmod 700 /var/lib/screen-timer

# Install and enable systemd service
cp screen-timer.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable screen-timer
systemctl start screen-timer

echo ""
echo "=== Installation complete ==="
echo ""
echo "IMPORTANT: Edit the config to set your child's username:"
echo "  sudo nano /etc/screen-timer/config.json"
echo "  Change \"watch_user\" from \"CHANGEME\" to the actual username."
echo ""
echo "Admin commands (run as root):"
echo "  screen-timer --status          Show remaining time"
echo "  screen-timer --reset           Reset to full daily allowance"
echo "  screen-timer --add-time 15     Add 15 minutes"
echo "  screen-timer --set-time 45     Set remaining time to 45 minutes"
echo ""
echo "Config:  /etc/screen-timer/config.json"
echo "State:   /var/lib/screen-timer/state.json"
echo "Service: systemctl status screen-timer"
