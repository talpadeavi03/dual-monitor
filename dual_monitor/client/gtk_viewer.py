"""
Client GTK3 Video Viewer.
Embeds GStreamer pipeline into a native GTK3 fullscreen window with zero lag.
"""

import sys
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gtk, Gdk, Gst, GstVideo, GLib

Gst.init(None)

class GTKClientViewer:
    def __init__(self, port=1234, codec="mjpeg", fullscreen=True):
        self.port = port
        self.codec = codec
        self.is_fullscreen = fullscreen

        self.win = Gtk.Window(title="Dual-Monitor Screen")
        self.win.connect("destroy", self.on_destroy)
        self.win.connect("key-press-event", self.on_key_press)

        # Black background
        self.win.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("black"))

        self.da = Gtk.DrawingArea()
        self.win.add(self.da)

        self.pipeline = self._create_pipeline()
        self.da.connect("realize", self.on_realize)

    def _create_pipeline(self):
        if self.codec == "mjpeg":
            caps = 'application/x-rtp,encoding-name=JPEG,payload=26'
            depay = 'rtpjpegdepay ! jpegdec'
        else:
            caps = 'application/x-rtp,encoding-name=H264,payload=96'
            depay = 'rtph264depay ! h264parse ! avdec_h264'

        pipeline_str = (
            f"udpsrc port={self.port} caps=\"{caps}\" ! "
            f"{depay} ! videoconvert ! autovideosink sync=false"
        )
        return Gst.parse_launch(pipeline_str)

    def on_realize(self, widget):
        xid = widget.get_window().get_xid()
        self.pipeline.get_bus().set_sync_handler(self.on_sync_message, xid)
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_sync_message(self, bus, msg, xid):
        if GstVideo.is_video_overlay_prepare_window_handle_message(msg):
            msg.src.set_window_handle(xid)
        return Gst.BusSyncReply.PASS

    def on_key_press(self, widget, event):
        keyval = event.keyval
        # F11 toggles fullscreen
        if keyval == Gdk.KEY_F11:
            if self.is_fullscreen:
                self.win.unfullscreen()
                self.is_fullscreen = False
            else:
                self.win.fullscreen()
                self.is_fullscreen = True
            return True
        # Escape exits fullscreen
        elif keyval == Gdk.KEY_Escape:
            if self.is_fullscreen:
                self.win.unfullscreen()
                self.is_fullscreen = False
                return True
        # q or Q quits
        elif keyval in (Gdk.KEY_q, Gdk.KEY_Q):
            self.on_destroy(widget)
            return True
        return False

    def on_destroy(self, widget):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def run(self):
        if self.is_fullscreen:
            self.win.fullscreen()
        self.win.show_all()
        Gtk.main()
