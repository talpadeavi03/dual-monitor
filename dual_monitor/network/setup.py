"""
Ethernet Network Auto-Configuration for Direct Cable Connection.
"""

import subprocess
import shutil

class NetworkConfigurator:
    @staticmethod
    def get_ethernet_interfaces():
        try:
            out = subprocess.check_output(["ip", "-o", "link"]).decode()
            interfaces = []
            for line in out.splitlines():
                parts = line.split(":")
                if len(parts) >= 2:
                    name = parts[1].strip()
                    if name.startswith(("en", "eth")):
                        interfaces.append(name)
            return interfaces
        except Exception:
            return []

    @staticmethod
    def configure_interface(interface, ip_address, netmask=24):
        print(f"[Network] Configuring interface {interface} with {ip_address}/{netmask}...")
        # Check if nmcli exists
        if shutil.which("nmcli"):
            try:
                con_name = f"DualMonitor-{interface}"
                # Check if connection already exists
                cons = subprocess.check_output(["nmcli", "-t", "-f", "NAME", "connection", "show"]).decode()
                if con_name in cons.splitlines():
                    subprocess.run(["nmcli", "connection", "delete", con_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                subprocess.run([
                    "nmcli", "connection", "add", "type", "ethernet",
                    "ifname", interface, "con-name", con_name,
                    "ip4", f"{ip_address}/{netmask}"
                ], check=True)
                subprocess.run(["nmcli", "connection", "up", con_name], check=True)
                print(f"[Network] NetworkManager connection '{con_name}' activated successfully.")
                return True
            except Exception as e:
                print(f"[Network] nmcli configuration failed ({e}), falling back to 'ip' command...")

        # Fallback to ip command
        try:
            subprocess.run(["sudo", "ip", "addr", "flush", "dev", interface], check=True)
            subprocess.run(["sudo", "ip", "addr", "add", f"{ip_address}/{netmask}", "dev", interface], check=True)
            subprocess.run(["sudo", "ip", "link", "set", "up", "dev", interface], check=True)
            print(f"[Network] Interface {interface} set to {ip_address}/{netmask} via ip command.")
            return True
        except Exception as e:
            print(f"[Network] Failed to set IP on {interface}: {e}")
            return False
