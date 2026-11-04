# Dual-Monitor 🖥️⚡

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-blue.svg)](https://www.kernel.org)
[![Wayland / X11](https://img.shields.io/badge/Display-Wayland%20%7C%20X11-green.svg)](https://wayland.freedesktop.org)

**Dual-Monitor** is a bare-metal, ultra-low-latency Linux second-screen utility designed to turn any spare Linux laptop or desktop into a smooth, zero-bloat extended monitor over a direct Ethernet cable or local network.

Tested and optimized for modern Wayland hosts (e.g. **elementary OS 8 / GNOME / Ubuntu**) connected directly to older legacy laptops (e.g. **Dell Vostro 1015 on Arch Linux**).

---

## 🚀 Why Bare-Metal?

| Feature | Conventional Solutions (Deskreen, VNC) | **Dual-Monitor** |
| :--- | :--- | :--- |
| **Technology** | Electron, WebRTC, Browser | Native PipeWire + SIMD RTP-JPEG |
| **Decode Latency** | 30ms – 100ms (High lag) | **~1 ms** (via `libjpeg-turbo` SIMD) |
| **Old Laptop CPU Load** | 100% (Laggy, frame drops) | **< 5%** (Smooth 60 FPS on Core 2 Duo) |
| **Network Latency** | Variable | **< 0.3 ms** (over direct Cat5e/6 cable) |
| **Compositor Support** | Needs dummy HDMI / Xwayland hacks | Native **Mutter / Wayland Virtual Display** |

---

## 🛠️ Architecture

```
[ HOST: HP Pavilion (elementary OS 8 / Wayland) ]
  │
  ├─► Mutter DisplayConfig D-Bus (Creates "Virtual-1" 1366x768 @ 60Hz)
  ├─► Mutter ScreenCast (Zero-copy PipeWire Framebuffer capture)
  └─► GStreamer Hardware Pipeline (RTP-JPEG stream over UDP)
        │
        ▼ (Direct Ethernet Cable: 192.168.99.1 -> 192.168.99.2)
        │
[ CLIENT: Dell Vostro (Arch Linux) ]
  │
  ├─► Zero-Latency UDP Receiver
  ├─► SIMD Hardware JPEG Decoder (< 1ms per frame)
  └─► Native GTK3 Borderless Fullscreen Display
```

---

## 📦 Installation

Clone the repository on both machines:

```bash
git clone https://github.com/talpadeavi03/dual-monitor.git
cd dual-monitor
chmod +x install.sh
sudo ./install.sh
```

### Manual Dependency Installation

* **Arch Linux (Client / Host):**
  ```bash
  sudo pacman -S --needed python python-gobject gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad libjpeg-turbo wmctrl
  ```

* **Ubuntu / elementary OS / Debian (Host / Client):**
  ```bash
  sudo apt-get install -y python3 python3-gi gir1.2-gtk-3.0 gir1.2-gstreamer-1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-pipewire wmctrl
  ```

---

## ⚡ Quickstart

### Step 1: Direct Ethernet Link

Connect your two laptops directly with an Ethernet cable.

* **On Host:**
  ```bash
  dual-monitor network host
  ```
  *(Assigns `192.168.99.1` to your Ethernet port)*

* **On Client:**
  ```bash
  dual-monitor network client
  ```
  *(Assigns `192.168.99.2` to your Ethernet port)*

---

### Step 2: Start the Screen

* **On Host (Primary Laptop):**
  ```bash
  dual-monitor host
  ```
  *Creates the virtual monitor on the right of your primary screen and starts streaming at 60 FPS.*

* **On Client (Second Screen Laptop):**
  ```bash
  dual-monitor client
  ```
  *Opens the zero-lag fullscreen display immediately.*

---

## 🎮 Controls & Shortcuts (Client)

* **`F11`**: Toggle Fullscreen / Windowed mode.
* **`Esc`**: Exit Fullscreen.
* **`q`**: Quit the client viewer.

---

## ⚙️ Advanced Options

### Custom Resolution & Refresh Rate
```bash
# Host on 1080p client:
dual-monitor host --width 1920 --height 1080 --fps 60

# Host positioned to the left of the main screen:
dual-monitor host --position left
```

### Video Codec Selection
* **`--codec mjpeg`** *(Default)*: Extremely low CPU usage on client (~1ms decode), ideal for older laptops (Core 2 Duo, Intel GMA).
* **`--codec h264`**: Higher compression ratio, recommended for modern clients with hardware H.264 decoding support.

### Independent Virtual Display Controls
```bash
dual-monitor display enable --width 1366 --height 768 --position right
dual-monitor display disable
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **Avinash Talpade** ([@talpadeavi03](https://github.com/talpadeavi03)).
