#!/usr/bin/env bash
# Make Dual-Monitor Client permanent across all reboots on Arch Linux / Client machine
set -e

echo "=== Setting Up Permanent Dual-Monitor Client ==="

# 1. Detect Ethernet interface
IFACE=$(ip -o link | awk -F': ' '{print $2}' | grep -E '^en|^eth' | head -n 1)

if [ -z "$IFACE" ]; then
    echo "[Error] No wired Ethernet interface found."
    exit 1
fi

echo "[Client] Detected Ethernet Interface: $IFACE"

# 2. Configure permanent NetworkManager connection
if command -v nmcli >/dev/null 2>&1; then
    echo "[Client] Configuring permanent NetworkManager connection 'DirectHP'..."
    # Remove old connection if exists
    nmcli connection delete "DirectHP" 2>/dev/null || true
    # Add new permanent autoconnect profile
    nmcli connection add type ethernet ifname "$IFACE" con-name "DirectHP" ip4 192.168.99.2/24 connection.autoconnect yes
    nmcli connection up "DirectHP"
    echo "[Client] Permanent Ethernet profile 'DirectHP' activated."
else
    echo "[Client] NetworkManager not found. Falling back to temporary IP assignment..."
    sudo ip addr add 192.168.99.2/24 dev "$IFACE" 2>/dev/null || true
    sudo ip link set up dev "$IFACE"
fi

# 3. Setup systemd user service for auto-start
echo "[Client] Installing systemd auto-start service..."
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
mkdir -p ~/.config/systemd/user
cp "$DIR/systemd/dual-monitor-client.service" ~/.config/systemd/user/
sed -i "s|/usr/local/bin/dual-monitor|$DIR/dual_monitor/cli.py|g" ~/.config/systemd/user/dual-monitor-client.service
systemctl --user daemon-reload
systemctl --user enable dual-monitor-client.service

echo ""
echo "=== Permanent Client Setup Complete ==="
echo "The Dell Vostro will now automatically connect to the HP on every boot!"
echo "To test the connection now:"
echo "  ping -c 3 192.168.99.1"
