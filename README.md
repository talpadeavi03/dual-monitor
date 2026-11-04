# Dual-Monitor 🖥️⚡

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-blue.svg)](https://www.kernel.org)
[![Wayland / X11](https://img.shields.io/badge/Display-Wayland%20%7C%20X11-green.svg)](https://wayland.freedesktop.org)
[![Framerate: 60 FPS](https://img.shields.io/badge/Framerate-60%20FPS%20Locked-success.svg)](https://github.com/talpadeavi03/dual-monitor)
[![Latency: ~1ms](https://img.shields.io/badge/Decode%20Latency-~1ms%20SIMD-orange.svg)](https://github.com/talpadeavi03/dual-monitor)

**Dual-Monitor** is a bare-metal, ultra-low-latency Linux second-screen utility designed to turn any spare Linux laptop or desktop into a smooth, zero-bloat extended monitor over a direct Ethernet cable or local network.

Specifically tested, engineered, and optimized for:
* **Host Laptop:** Modern Wayland compositors (e.g., **HP Pavilion on elementary OS 8 / GNOME / Ubuntu 24.04**).
* **Client Laptop:** Legacy, low-spec hardware (e.g., **Dell Vostro 1015 on Arch Linux with Intel Core 2 Duo & GMA 4500MHD graphics**).
* **Connection:** Direct point-to-point RJ-45 Ethernet cable (no router, switch, or DHCP server required).

---

## 🚀 Why "Bare-Metal"? (The Engineering Details)

Most wireless display solutions (such as Deskreen, spacedesk, or generic VNC) rely on heavy software stacks like Electron, WebRTC, Chromium browsers, or generic H.264 software decoders.

On older client machines (like a 2009 Intel Core 2 Duo), software-decoding 60 FPS H.264 pushes CPU usage to 100%, accumulating a 30ms–100ms frame backlog that makes mouse tracking feel floaty and unresponsive.

**Dual-Monitor replaces the entire stack with native Linux kernel and compositor primitives:**

| Architecture Component | Conventional Tools (Deskreen / VNC) | **Dual-Monitor (Bare-Metal)** |
| :--- | :--- | :--- |
| **Virtual Monitor Creation** | Dummy HDMI plugs or fake Xwayland hacks | Native **Mutter D-Bus DisplayConfig** (`Virtual-1`) |
| **Compositor Capture** | Slow X11 root grab (Xwayland black screen) | Zero-copy **Mutter ScreenCast -> PipeWire** |
| **Frame Encoding** | Heavy H.264 or WebRTC VP8/VP9 | **Spatial SIMD Motion-JPEG** (`ifast` IDCT) |
| **Client CPU Load** | 100% (High heat, dropped frames) | **< 5% CPU** on Intel Core 2 Duo |
| **Decode Time per Frame** | 30ms – 45ms (software H.264) | **~1.1 ms** (SIMD MMX/SSE2 via `libjpeg-turbo`) |
| **Cable Network Roundtrip** | Variable / buffering | **0.27 ms** over direct Cat5e/Cat6 Ethernet |
| **Presentation Pipeline** | Browser canvas render loop | Direct X11/Wayland hardware overlay (`sync=false`) |

---

## 🛠️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             HOST LAPTOP (e.g. HP Pavilion)                  │
│               elementary OS 8 / Wayland                     │
│                                                             │
│  1. Mutter DisplayConfig                                    │
│     └─► Creates virtual output "Virtual-1" (1366x768 @ 60Hz)│
│  2. Mutter ScreenCast D-Bus                                 │
│     └─► Hardware zero-copy compositor PipeWire node         │
│  3. GStreamer Zero-Latency Pipeline                         │
│     └─► pipewiresrc -> jpegenc (ifast) -> rtpjpegpay -> UDP │
└──────────────────────────────┬──────────────────────────────┘
                               │  Direct Cat5e/Cat6 Cable
                               │  Static IP: 192.168.99.1 -> 192.168.99.2
                               │  Roundtrip Latency: 0.27ms
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             CLIENT LAPTOP (e.g. Dell Vostro 1015)           │
│                    Arch Linux                               │
│                                                             │
│  1. UDP Port 1234 Listener                                  │
│  2. SIMD libjpeg-turbo Hardware Decoder (~1ms decode)       │
│  3. Native GTK3 Borderless Fullscreen Display Window        │
└─────────────────────────────────────────────────────────────┘
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

The installer detects your Linux distribution and installs the minimal dependencies:

* **Arch Linux:** `pacman -S python python-gobject gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad libjpeg-turbo wmctrl`
* **Ubuntu / elementary OS / Debian:** `apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-gstreamer-1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-pipewire wmctrl`
* **Fedora / RHEL:** `dnf install python3-gobject gtk3 gstreamer1 gstreamer1-plugins-base gstreamer1-plugins-good wmctrl`

---

## ⚡ How to Use the New Software

### Step 1: Establish the Direct Ethernet Cable Link

Plug an Ethernet cable directly between the two laptops (no router required).

* **On HP Pavilion (Host):**
  ```bash
  dual-monitor network host
  ```
  *(Configures `192.168.99.1/24` on your wired Ethernet interface)*

* **On Dell Vostro (Client):**
  ```bash
  dual-monitor network client
  ```
  *(Configures `192.168.99.2/24` on your wired Ethernet interface)*

* **Verify connection (from either machine):**
  ```bash
  ping 192.168.99.2
  ```

---

### Step 2: Start the System

#### On Your HP Pavilion (Host):
```bash
cd /home/sudo69/Projects/Project-Arch-Elementary
./scripts/start-host.sh

# Or using the global CLI:
dual-monitor host
```
*Creates the virtual monitor on the right of your primary screen and starts streaming at 60 FPS.*

#### On Your Dell Vostro (Client):
```bash
dual-monitor client
```
*Opens the zero-lag fullscreen display immediately. Your mouse cursor moves seamlessly across laptops.*

---

## 🎮 Client Controls & Shortcuts

| Key | Action |
| :--- | :--- |
| **`F11`** | Toggle Fullscreen / Windowed mode |
| **`Esc`** | Exit Fullscreen |
| **`q`** or **`Ctrl + C`** | Clean exit |

---

## ⚙️ Complete CLI Command Reference

### `dual-monitor host`
Streams the virtual display from the primary laptop:

```bash
dual-monitor host [OPTIONS]
```

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--target-ip <IP>` | `192.168.99.2` | Destination IP address of the client laptop |
| `--port <PORT>` | `1234` | UDP destination port |
| `--monitor <NAME>` | `Virtual-1` | Name of the virtual display connector in Mutter |
| `--width <PX>` | `1366` | Virtual display width (e.g. 1366, 1920) |
| `--height <PX>` | `768` | Virtual display height (e.g. 768, 1080) |
| `--fps <HZ>` | `60.0` | Target refresh rate |
| `--position <POS>` | `right` | Monitor placement: `right`, `left`, `above`, `below` |
| `--codec <CODEC>` | `mjpeg` | Video codec: `mjpeg` (lowest CPU) or `h264` |
| `--quality <1-100>` | `80` | JPEG compression quality |
| `--no-virtual-display` | `false` | Skip virtual display creation and stream existing display |

### `dual-monitor client`
Receives and renders the screen on the second laptop:

```bash
dual-monitor client [OPTIONS]
```

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--port <PORT>` | `1234` | UDP listening port |
| `--codec <CODEC>` | `mjpeg` | Stream codec (`mjpeg` or `h264`) |
| `--windowed` | `false` | Launch in windowed mode instead of fullscreen |

### `dual-monitor network`
Automates Ethernet link setup without manual IP configuration:

```bash
dual-monitor network [host|client|list] [--interface <IFACE>]
```

### `dual-monitor display`
Enables or disables virtual monitors independently of the streamer:

```bash
# Turn on virtual screen to the right of your laptop
dual-monitor display enable --width 1366 --height 768 --position right

# Turn off virtual screen
dual-monitor display disable
```

---

## 🔧 Running as a Background Systemd Service

To have the host or client start automatically whenever your desktop session starts:

### On Host:
```bash
cp systemd/dual-monitor-host.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now dual-monitor-host.service
```

### On Client:
```bash
cp systemd/dual-monitor-client.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now dual-monitor-client.service
```

---

## ❓ Troubleshooting & Technical FAQ

### 1. Why was the screen black when using standard `x11grab`?
elementary OS 8 (and modern Ubuntu/GNOME) runs on **Wayland** by default. `x11grab` reads from the Xwayland root window, which contains no wallpaper and does not render native Wayland client surfaces. `dual-monitor` bypasses X11 entirely by communicating with Mutter's D-Bus `ScreenCast` interface to capture raw GPU-backed PipeWire frames.

### 2. Why did H.264 cause mouse lag on the Dell Vostro?
The Dell Vostro 1015 features an Intel GM45 chipset with GMA 4500MHD graphics. Linux VA-API drivers do not support full H.264 hardware acceleration for GM45. Decoding 60 FPS in software pegged the Core 2 Duo CPU at 100%, causing a frame backlog. Switching to `mjpeg` uses SIMD `libjpeg-turbo`, which decodes in ~1ms and drops CPU usage to <5%.

### 3. Mouse cursor not crossing over?
Verify the position of your virtual screen. If your secondary laptop is physically to the right of your main laptop, ensure `--position right` is used. If it is on the left, use:
```bash
dual-monitor host --position left
```

### 4. How to verify Ethernet link state?
Check with `ip link`:
```bash
ip link show eno1    # on HP
ip link show enp9s0  # on Dell
```
Both interfaces should display `state UP` and `<BROADCAST,MULTICAST,UP,LOWER_UP>`.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Authored with ❤️ by **Avinash Talpade** ([@talpadeavi03](https://github.com/talpadeavi03)).
Contributions, bug reports, and suggestions are welcome via [GitHub Issues](https://github.com/talpadeavi03/dual-monitor/issues)!
