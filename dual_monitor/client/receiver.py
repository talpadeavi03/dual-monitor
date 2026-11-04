"""
Client Receiver CLI runner.
"""

from .gtk_viewer import GTKClientViewer

class ClientReceiver:
    def __init__(self, port=1234, codec="mjpeg", fullscreen=True):
        self.port = port
        self.codec = codec
        self.fullscreen = fullscreen

    def start(self):
        print(f"[Client] Dual-Monitor Client starting on port {self.port} (Codec: {self.codec.upper()})...")
        print("[Client] Press 'F11' to toggle Fullscreen, 'Esc' to exit Fullscreen, 'q' to Quit.")
        viewer = GTKClientViewer(port=self.port, codec=self.codec, fullscreen=self.fullscreen)
        viewer.run()
