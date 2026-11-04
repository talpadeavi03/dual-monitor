#!/usr/bin/env python3
"""
Dual-Monitor CLI: Main entry point for the dual-monitor software suite.
"""

import sys
import os

# Ensure package can be imported when running script directly
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import argparse
from dual_monitor.host import VirtualDisplayManager, HostStreamer
from dual_monitor.client import ClientReceiver
from dual_monitor.network import NetworkConfigurator

def main():
    parser = argparse.ArgumentParser(
        prog="dual-monitor",
        description="Bare-metal ultra-low latency second screen system over direct Ethernet for Linux."
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # Host command
    parser_host = subparsers.add_parser("host", help="Run the Host server (streams display)")
    parser_host.add_argument("--target-ip", default="192.168.99.2", help="Client IP address (default: 192.168.99.2)")
    parser_host.add_argument("--port", type=int, default=1234, help="Target UDP port (default: 1234)")
    parser_host.add_argument("--monitor", default="Virtual-1", help="Virtual monitor name (default: Virtual-1)")
    parser_host.add_argument("--width", type=int, default=1366, help="Screen width in pixels (default: 1366)")
    parser_host.add_argument("--height", type=int, default=768, help="Screen height in pixels (default: 768)")
    parser_host.add_argument("--fps", type=float, default=60.0, help="Refresh rate (default: 60.0)")
    parser_host.add_argument("--position", choices=["right", "left", "above", "below"], default="right", help="Position relative to primary display")
    parser_host.add_argument("--codec", choices=["mjpeg", "h264"], default="mjpeg", help="Video codec (default: mjpeg for legacy/low CPU)")
    parser_host.add_argument("--quality", type=int, default=80, help="JPEG quality 1-100 (default: 80)")
    parser_host.add_argument("--no-virtual-display", action="store_true", help="Do not create or enable a virtual display, just stream")

    # Client command
    parser_client = subparsers.add_parser("client", help="Run the Client receiver (displays screen)")
    parser_client.add_argument("--port", type=int, default=1234, help="Listening UDP port (default: 1234)")
    parser_client.add_argument("--codec", choices=["mjpeg", "h264"], default="mjpeg", help="Video codec (default: mjpeg)")
    parser_client.add_argument("--windowed", action="store_true", help="Launch in windowed mode instead of fullscreen")

    # Network command
    parser_net = subparsers.add_parser("network", help="Network configuration helper")
    parser_net.add_argument("role", choices=["host", "client", "list"], help="Role to configure (host: 192.168.99.1, client: 192.168.99.2)")
    parser_net.add_argument("--interface", help="Ethernet interface name (e.g. eno1, enp9s0)")

    # Display command
    parser_disp = subparsers.add_parser("display", help="Manage virtual displays independently")
    parser_disp.add_argument("action", choices=["enable", "disable"], help="Enable or disable virtual display")
    parser_disp.add_argument("--width", type=int, default=1366, help="Width in pixels (default: 1366)")
    parser_disp.add_argument("--height", type=int, default=768, help="Height in pixels (default: 768)")
    parser_disp.add_argument("--position", choices=["right", "left", "above", "below"], default="right")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "host":
        if not args.no_virtual_display:
            vdm = VirtualDisplayManager(monitor_name=args.monitor)
            print(f"[Host] Setting up virtual display {args.monitor} ({args.width}x{args.height} @ {args.fps}Hz {args.position} of primary)...")
            try:
                vdm.enable(width=args.width, height=args.height, refresh_rate=args.fps, position=args.position)
            except Exception as e:
                print(f"[Host] Warning: Could not configure virtual display: {e}")

        streamer = HostStreamer(
            target_ip=args.target_ip,
            target_port=args.port,
            monitor_name=args.monitor,
            codec=args.codec,
            quality=args.quality
        )
        streamer.start()

    elif args.command == "client":
        receiver = ClientReceiver(
            port=args.port,
            codec=args.codec,
            fullscreen=not args.windowed
        )
        receiver.start()

    elif args.command == "network":
        interfaces = NetworkConfigurator.get_ethernet_interfaces()
        if args.role == "list":
            print("[Network] Available Ethernet interfaces:")
            for iface in interfaces:
                print(f"  - {iface}")
            return

        iface = args.interface
        if not iface:
            if not interfaces:
                print("[Network] Error: No Ethernet interfaces detected.")
                sys.exit(1)
            iface = interfaces[0]
            print(f"[Network] Using detected interface: {iface}")

        ip = "192.168.99.1" if args.role == "host" else "192.168.99.2"
        NetworkConfigurator.configure_interface(iface, ip)

    elif args.command == "display":
        vdm = VirtualDisplayManager()
        if args.action == "enable":
            vdm.enable(width=args.width, height=args.height, position=args.position)
            print(f"[Display] Virtual display enabled ({args.width}x{args.height} {args.position}).")
        else:
            vdm.disable()
            print("[Display] Virtual display disabled.")

if __name__ == "__main__":
    main()
