#!/usr/bin/env bash
# Dual-Monitor Universal Installer for Linux (Arch, Ubuntu/Debian/elementary, Fedora)
set -e

echo "=========================================="
echo "    Dual-Monitor Installer for Linux      "
echo "=========================================="

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Detect package manager
if command -v pacman >/dev/null 2>&1; then
    echo "[Installer] Detected Arch Linux (pacman)."
    echo "[Installer] Installing dependencies..."
    sudo pacman -S --needed --noconfirm \
        python python-pip python-gobject gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad libjpeg-turbo wmctrl networkmanager
elif command -v apt-get >/dev/null 2>&1; then
    echo "[Installer] Detected Debian/Ubuntu/elementary OS (apt)."
    echo "[Installer] Installing dependencies..."
    sudo apt-get update
    sudo apt-get install -y \
        python3 python3-pip python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gstreamer-1.0 \
        gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
        gstreamer1.0-pipewire wmctrl network-manager
elif command -v dnf >/dev/null 2>&1; then
    echo "[Installer] Detected Fedora/RHEL (dnf)."
    sudo dnf install -y \
        python3 python3-pip python3-gobject gtk3 gstreamer1 gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad-free wmctrl NetworkManager
else
    echo "[Installer] Warning: Unknown package manager. Please ensure Python 3, GStreamer, and PyGObject are installed."
fi

# Install Python package in editable mode
echo "[Installer] Installing Python package into user environment..."
python3 -m pip install --break-system-packages -e "$DIR" || python3 -m pip install -e "$DIR" || true

# Make scripts executable
chmod +x "$DIR/dual_monitor/cli.py"
chmod +x "$DIR/scripts/"*.sh

# Symlink to ~/.local/bin and /usr/local/bin
mkdir -p "$HOME/.local/bin"
ln -sf "$DIR/dual_monitor/cli.py" "$HOME/.local/bin/dual-monitor"
sudo ln -sf "$DIR/dual_monitor/cli.py" /usr/local/bin/dual-monitor 2>/dev/null || true

echo ""
echo "=========================================="
echo "   Installation completed successfully!   "
echo "=========================================="
echo "Usage:"
echo "  Run Host   : dual-monitor host"
echo "  Run Client : dual-monitor client"
echo ""
echo "To make it permanent across every reboot:"
echo "  On HP (Host)   : ./scripts/setup-host-permanent.sh"
echo "  On Dell (Client): ./scripts/setup-client-permanent.sh"
echo "=========================================="
