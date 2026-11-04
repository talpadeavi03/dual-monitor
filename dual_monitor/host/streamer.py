"""
Host Video Streamer.
Hooks into Mutter PipeWire ScreenCast (Wayland) or x11grab (X11) and streams
zero-latency video frames over UDP RTP.
"""

import os
import sys
import time
import signal
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gio, GLib, Gst

Gst.init(None)

class HostStreamer:
    def __init__(self, target_ip="192.168.99.2", target_port=1234, monitor_name="Virtual-1", codec="mjpeg", quality=80, bitrate=6000):
        self.target_ip = target_ip
        self.target_port = target_port
        self.monitor_name = monitor_name
        self.codec = codec
        self.quality = quality
        self.bitrate = bitrate
        self.session_type = os.environ.get("XDG_SESSION_TYPE", "wayland").lower()
        self.running = True

    def _setup_signal_handlers(self):
        def sig_handler(sig, frame):
            print("\n[Host] Stopping streamer...")
            self.running = False
            sys.exit(0)
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)

    def _build_pipeline_string(self, node_id=None, x=1920, y=0, width=1366, height=768):
        if self.session_type == "wayland":
            src = f"pipewiresrc path={node_id} do-timestamp=true keepalive-time=1000 ! videoconvert ! video/x-raw,format=I420"
        else:
            src = f"ximagesrc startx={x} starty={y} endx={x+width-1} endy={y+height-1} use-damage=false ! videoconvert ! video/x-raw,format=I420"

        if self.codec == "mjpeg":
            enc = f"jpegenc quality={self.quality} idct-method=ifast ! rtpjpegpay"
        else:
            enc = (
                f"x264enc speed-preset=ultrafast tune=zerolatency bitrate={self.bitrate} "
                "key-int-max=30 sliced-threads=true sync-lookahead=0 rc-lookahead=0 ! "
                "h264parse config-interval=-1 ! rtph264pay config-interval=1 pt=96"
            )

        sink = f"udpsink host={self.target_ip} port={self.target_port} sync=false"
        return f"{src} ! {enc} ! {sink}"

    def run_wayland_stream(self):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        screencast = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.gnome.Mutter.ScreenCast",
            "/org/gnome/Mutter/ScreenCast",
            "org.gnome.Mutter.ScreenCast",
            None,
        )

        try:
            session_path = screencast.call_sync(
                "CreateSession",
                GLib.Variant("(a{sv})", ({},)),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            ).unpack()[0]
        except Exception as e:
            print(f"[Host] Error creating Mutter ScreenCast session: {e}")
            return False

        session = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.gnome.Mutter.ScreenCast",
            session_path,
            "org.gnome.Mutter.ScreenCast.Session",
            None,
        )

        try:
            stream_path = session.call_sync(
                "RecordMonitor",
                GLib.Variant("(sa{sv})", (self.monitor_name, {"cursor-mode": GLib.Variant("u", 1)})),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            ).unpack()[0]
        except Exception as e:
            print(f"[Host] Error recording monitor {self.monitor_name}: {e}")
            return False

        loop = GLib.MainLoop()
        node_id_container = []

        def on_stream_added(connection, sender, path, iface, signal_name, params):
            node_id = params.unpack()[0]
            node_id_container.append(node_id)
            loop.quit()

        bus.signal_subscribe(
            "org.gnome.Mutter.ScreenCast",
            "org.gnome.Mutter.ScreenCast.Stream",
            "PipeWireStreamAdded",
            stream_path,
            None,
            Gio.DBusSignalFlags.NONE,
            on_stream_added,
        )

        try:
            session.call_sync("Start", None, Gio.DBusCallFlags.NONE, -1, None)
            loop.run()
        except Exception as e:
            print(f"[Host] Error starting ScreenCast session: {e}")
            return False

        if not node_id_container:
            return False

        node_id = node_id_container[0]
        print(f"[Host] Connected to Wayland PipeWire node {node_id}")
        pipeline_str = self._build_pipeline_string(node_id=node_id)
        print(f"[Host] Streaming via RTP-{self.codec.upper()} to {self.target_ip}:{self.target_port}...")

        pipe = Gst.parse_launch(pipeline_str)
        pipe.set_state(Gst.State.PLAYING)

        bus_gst = pipe.get_bus()
        while self.running:
            msg = bus_gst.timed_pop_filtered(
                1 * Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS
            )
            if msg:
                if msg.type == Gst.MessageType.ERROR:
                    err, debug = msg.parse_error()
                    print(f"[Host] Stream error: {err}")
                break

        pipe.set_state(Gst.State.NULL)
        try:
            session.call_sync("Stop", None, Gio.DBusCallFlags.NONE, -1, None)
        except Exception:
            pass
        return True

    def start(self):
        self._setup_signal_handlers()
        print(f"[Host] Dual-Monitor Host service starting ({self.session_type.upper()})...")
        while self.running:
            if self.session_type == "wayland":
                success = self.run_wayland_stream()
            else:
                pipeline_str = self._build_pipeline_string()
                pipe = Gst.parse_launch(pipeline_str)
                pipe.set_state(Gst.State.PLAYING)
                bus_gst = pipe.get_bus()
                msg = bus_gst.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)
                pipe.set_state(Gst.State.NULL)
                success = False

            if not self.running:
                break
            if not success:
                time.sleep(1)
            else:
                time.sleep(0.5)
