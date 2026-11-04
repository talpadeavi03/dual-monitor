#!/usr/bin/env bash
# Make Dual-Monitor Host permanent across all reboots on elementary OS / Ubuntu / Host machine
set -e

echo "=== Setting Up Permanent Dual-Monitor Host ==="

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"

# 1. Detect Ethernet interface
IFACE=$(ip -o link | awk -F': ' '{print $2}' | grep -E '^en|^eth' | head -n 1)

if [ -z "$IFACE" ]; then
    echo "[Error] No wired Ethernet interface found."
    exit 1
fi

echo "[Host] Detected Ethernet Interface: $IFACE"

# 2. Configure permanent NetworkManager connection with shared DHCP
if command -v nmcli >/dev/null 2>&1; then
    echo "[Host] Configuring permanent NetworkManager connection with shared DHCP..."
    CON_NAME="DirectClient-$IFACE"
    nmcli connection delete "$CON_NAME" 2>/dev/null || true
    nmcli connection add type ethernet ifname "$IFACE" con-name "$CON_NAME" \
        ipv4.method shared ipv4.addresses 192.168.99.1/24 connection.autoconnect yes
    nmcli connection up "$CON_NAME"
    echo "[Host] Permanent Ethernet profile '$CON_NAME' activated with auto-DHCP."
fi

# 3. Setup systemd user service for auto-start
echo "[Host] Installing systemd auto-start service..."
mkdir -p ~/.config/systemd/user
cp "$DIR/systemd/dual-monitor-host.service" ~/.config/systemd/user/
sed -i "s|/usr/local/bin/dual-monitor|$DIR/dual_monitor/cli.py|g" ~/.config/systemd/user/dual-monitor-host.service
systemctl --user daemon-reload
systemctl --user enable --now dual-monitor-host.service

echo ""
echo "=== Permanent Host Setup Complete ==="
echo "The HP Pavilion will now automatically start the virtual monitor and streamer on every boot!"
