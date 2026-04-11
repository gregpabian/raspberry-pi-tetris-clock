#!/bin/bash
# Install script for Tetris Clock on Raspberry Pi
# Run as root: sudo bash install.sh

set -e

echo "=== Tetris Clock Installer ==="

# Save project directory before any cd
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash install.sh"
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y build-essential git

# Install rpi-rgb-led-matrix
if [ ! -d "/opt/rpi-rgb-led-matrix" ]; then
    echo "Cloning rpi-rgb-led-matrix..."
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git /opt/rpi-rgb-led-matrix
fi

echo "Building rpi-rgb-led-matrix..."
cd /opt/rpi-rgb-led-matrix
make -C lib
make install-shared DESTDIR=/usr/local

# Build tetris-clock
echo "Building tetris-clock..."
cd "$SCRIPT_DIR"
make

# Configure boot settings
echo "Configuring boot settings..."
CONFIG="/boot/config.txt"
if [ -f "/boot/firmware/config.txt" ]; then
    CONFIG="/boot/firmware/config.txt"
fi

if ! grep -q "dtparam=audio=off" "$CONFIG"; then
    echo "dtparam=audio=off" >> "$CONFIG"
    echo "  Disabled onboard audio (PWM conflict)"
fi

if ! grep -q "dtoverlay=disable-bt" "$CONFIG"; then
    echo "dtoverlay=disable-bt" >> "$CONFIG"
    echo "  Disabled Bluetooth"
fi

# Install systemd service
echo "Installing systemd service..."

# Update service file with actual path
sed "s|/home/pi/tetris-clock|${SCRIPT_DIR}|g" "${SCRIPT_DIR}/tetris-clock.service" > /etc/systemd/system/tetris-clock.service

systemctl daemon-reload
systemctl enable tetris-clock.service

echo ""
echo "=== Installation complete ==="
echo ""
echo "Start the clock:  sudo systemctl start tetris-clock"
echo "View logs:         journalctl -u tetris-clock -f"
echo "Stop the clock:    sudo systemctl stop tetris-clock"
echo ""
echo "NOTE: A reboot is recommended for boot config changes to take effect."
