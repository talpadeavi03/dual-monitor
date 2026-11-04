"""
Virtual Display Manager for Host.
Supports Wayland (GNOME / Mutter / Gala) via D-Bus org.gnome.Mutter.DisplayConfig
and X11 via xrandr.
"""

import os
import subprocess
import gi
from gi.repository import Gio, GLib

class VirtualDisplayManager:
    def __init__(self, monitor_name="Virtual-1"):
        self.monitor_name = monitor_name
        self.session_type = os.environ.get("XDG_SESSION_TYPE", "wayland").lower()

    def enable_wayland(self, width=1366, height=768, refresh_rate=60.0, position="right"):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.gnome.Mutter.DisplayConfig",
            "/org/gnome/Mutter/DisplayConfig",
            "org.gnome.Mutter.DisplayConfig",
            None,
        )

        state = proxy.call_sync("GetCurrentState", None, Gio.DBusCallFlags.NONE, -1, None)
        serial, monitors, logical_monitors, properties = state.unpack()

        # Find primary physical monitor (eDP-1 or HDMI-1)
        primary_mon = None
        for m in monitors:
            name = m[0][0]
            if name != self.monitor_name:
                primary_mon = m
                break

        if not primary_mon:
            raise RuntimeError("No primary monitor detected.")

        primary_name = primary_mon[0][0]
        # Get active mode or preferred mode of primary monitor
        prim_mode = primary_mon[1][0][0]
        prim_w = primary_mon[1][0][1]
        prim_h = primary_mon[1][0][2]
        for mode in primary_mon[1]:
            props = mode[6] if len(mode) > 6 else {}
            if props.get("is-current") or props.get("is-preferred"):
                prim_mode = mode[0]
                prim_w = mode[1]
                prim_h = mode[2]
                break

        # Find best mode for virtual display matching requested width x height
        v_mode_id = None
        for m in monitors:
            if m[0][0] == self.monitor_name:
                for mode in m[1]:
                    if mode[1] == width and mode[2] == height:
                        v_mode_id = mode[0]
                        break
                if not v_mode_id and len(m[1]) > 0:
                    v_mode_id = m[1][0][0]
                break

        if not v_mode_id:
            v_mode_id = f"{width}x{height}@{refresh_rate:.3f}"

        # Calculate position coordinates
        if position == "right":
            v_x = prim_w
            v_y = 0
        elif position == "left":
            v_x = -width
            v_y = 0
        elif position == "above":
            v_x = 0
            v_y = -height
        elif position == "below":
            v_x = 0
            v_y = prim_h
        else:
            v_x = prim_w
            v_y = 0

        # Primary logical monitor at (0, 0)
        logical_mons = [
            (0, 0, 1.0, 0, True, [(primary_name, prim_mode, {})]),
            (v_x, v_y, 1.0, 0, False, [(self.monitor_name, v_mode_id, {})]),
        ]

        param = GLib.Variant("(uua(iiduba(ssa{sv}))a{sv})", (serial, 2, logical_mons, {}))
        proxy.call_sync("ApplyMonitorsConfig", param, Gio.DBusCallFlags.NONE, -1, None)
        return True

    def disable_wayland(self):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.gnome.Mutter.DisplayConfig",
            "/org/gnome/Mutter/DisplayConfig",
            "org.gnome.Mutter.DisplayConfig",
            None,
        )

        state = proxy.call_sync("GetCurrentState", None, Gio.DBusCallFlags.NONE, -1, None)
        serial, monitors, logical_monitors, properties = state.unpack()

        primary_mon = None
        for m in monitors:
            name = m[0][0]
            if name != self.monitor_name:
                primary_mon = m
                break

        if not primary_mon:
            return False

        primary_name = primary_mon[0][0]
        prim_mode = primary_mon[1][0][0]
        for mode in primary_mon[1]:
            props = mode[6] if len(mode) > 6 else {}
            if props.get("is-current") or props.get("is-preferred"):
                prim_mode = mode[0]
                break

        logical_mons = [
            (0, 0, 1.0, 0, True, [(primary_name, prim_mode, {})]),
        ]
        param = GLib.Variant("(uua(iiduba(ssa{sv}))a{sv})", (serial, 2, logical_mons, {}))
        proxy.call_sync("ApplyMonitorsConfig", param, Gio.DBusCallFlags.NONE, -1, None)
        return True

    def enable_x11(self, output="HDMI-1", width=1366, height=768, refresh_rate=60.0, position="right"):
        mode_name = f"{width}x{height}_{refresh_rate:.2f}"
        gtf_out = subprocess.check_output(["gtf", str(width), str(height), str(refresh_rate)]).decode()
        modeline = None
        for line in gtf_out.splitlines():
            if "Modeline" in line:
                modeline = line.split("Modeline")[1].strip()
                break

        if modeline:
            subprocess.run(["xrandr", "--newmode"] + modeline.split(), stderr=subprocess.DEVNULL)
            subprocess.run(["xrandr", "--addmode", output, mode_name], stderr=subprocess.DEVNULL)
            subprocess.run(["xrandr", "--output", output, "--mode", mode_name, f"--{position}-of", "eDP-1"])
            return True
        return False

    def disable_x11(self, output="HDMI-1"):
        subprocess.run(["xrandr", "--output", output, "--off"])
        return True

    def enable(self, width=1366, height=768, refresh_rate=60.0, position="right"):
        if self.session_type == "wayland":
            return self.enable_wayland(width, height, refresh_rate, position)
        else:
            return self.enable_x11(width=width, height=height, refresh_rate=refresh_rate, position=position)

    def disable(self):
        if self.session_type == "wayland":
            return self.disable_wayland()
        else:
            return self.disable_x11()
