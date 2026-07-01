# Slapx ⚡

A physical laptop slap and hit detection soundboard for Linux. When you slap or hit your laptop chassis, it automatically plays a random custom audio effect (up to 3 custom tracks) or retro synthesized sounds.

Slapx bridges physical user interactions with digital responses by turning your laptop chassis into an interactive touchpad. It is designed to be highly responsive, lightweight, and customizable.

---

## 📖 Table of Contents
- [Features](#features)
- [How it Works](#how-it-works)
- [Project Architecture (Modularized)](#project-architecture-modularized)
- [Dependencies & Installation](#dependencies--installation)
- [Usage](#usage)
  - [GUI Dashboard (Default)](#gui-dashboard-default)
  - [Headless CLI Mode](#headless-cli-mode)
- [Configuration (`config.json`)](#configuration-configjson)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## ✨ Features

- 🎧 **Chassis Hit Detection**: Uses ALSA's `arecord` to capture raw audio signals from your built-in microphone, detecting high-amplitude transients (spikes) caused by physical laptop slaps/taps.
- 🎛️ **Visual rolling waveform graph**: A real-time Tkinter Canvas dashboard showing rolling audio peaks relative to your threshold line.
- 🎨 **Futuristic UI Theme**: A stylish Catppuccin Mocha-inspired dark theme with responsive LED status colors.
- ⚡ **Zero-latency triggers**: Uses low-overhead, non-blocking `mpv` playback processes to ensure sounds trigger immediately.
- 🎹 **Built-in Sound Synthesizer**: Auto-generates three retro sound effects (`default_ouch.wav`, `default_laser.wav`, and `default_slap.wav`) on first boot, letting you test the app instantly.
- 🗃️ **Up to 3 Custom Audio Slots**: Link your own custom audio tracks (`.mp3`, `.wav`, `.ogg`, `.flac`, etc.) which are chosen at random upon detection.
- ⏱️ **Cooldown Guard**: Prevents double-triggering or audio feedback loops with an adjustable cooldown delay (from 0.1s up to 5.0s).
- 🖥️ **X11-Free Headless Mode**: Use `--headless` to run Slapx without X11/Tkinter dependencies, making it perfect for servers, remote SSH runs, or terminal daemons.
- ⚙️ **Persistent Configuration**: Automatically saves settings (sensitivity, cooldown, audio slots, total slaps) to `config.json` and restores them on launch.

---

## 🛠️ Project Architecture (Modularized)

The codebase has been refactored into a clean, modular structure. This separates concerns, avoids circular dependencies, and enables Tkinter to be skipped entirely in headless mode.

```
Slapx/
├── slapx.py               # Main CLI wrapper entrypoint (executes main.py)
├── config.json            # Automatically generated configuration storage
├── sounds/                # Directory containing synthesized default sound clips
│   ├── default_laser.wav
│   ├── default_ouch.wav
│   └── default_slap.wav
└── slapx/                 # Modular Python Package
    ├── __init__.py        # Package initialization file
    ├── constants.py       # Global constants (Sample rate, chunk sizes, max slots)
    ├── config.py          # ConfigManager class for state persistence
    ├── synthesizer.py     # Waveform synthesis algorithms for default retro audios
    ├── detector.py        # Subprocess manager for ALSA recording and MPV playback
    ├── gui.py             # Tkinter visualizer dashboard (lazy-loaded in GUI mode)
    └── main.py            # Central orchestrator and CLI argument parser
```

### Module Breakdown:
1. **[constants.py](file:///home/hangineering/Han/Projects/Slapx/slapx/constants.py)**: Centralizes parameters like `SAMPLE_RATE` (16kHz), `CHUNK_SIZE` (512), and `MAX_SLOTS` (3).
2. **[config.py](file:///home/hangineering/Han/Projects/Slapx/slapx/config.py)**: Defines `ConfigManager` to load settings, initialize default values, and write modifications safely.
3. **[synthesizer.py](file:///home/hangineering/Han/Projects/Slapx/slapx/synthesizer.py)**: Synthesizes mathematically modelled waveforms (frequency sweeps, exponential decays, white noise) and saves them as `.wav` files.
4. **[detector.py](file:///home/hangineering/Han/Projects/Slapx/slapx/detector.py)**: Pipes microphone byte stream from a background `arecord` process, calculates PCM peaks, detects amplitude triggers, and runs non-blocking `mpv` plays.
5. **[gui.py](file:///home/hangineering/Han/Projects/Slapx/slapx/gui.py)**: Main graphic interface built with Tkinter. Updates the waveform canvas at ~33 fps (every 30ms) using a thread-safe Queue, flashes red on slap triggers, and provides user sliders.
6. **[main.py](file:///home/hangineering/Han/Projects/Slapx/slapx/main.py)**: Instantiates modules, acts as the coordinator, and routes to CLI/GUI loops depending on CLI flags.

---

## 📥 Dependencies & Installation

Slapx runs on Linux. Before launching, install the system dependencies using your package manager.

### Debian / Ubuntu
```bash
sudo apt update
sudo apt install alsa-utils mpv python3-tk
```

### Arch Linux
```bash
sudo pacman -S alsa-utils mpv tk
```

### Fedora
```bash
sudo dnf install alsa-utils mpv python3-tkinter
```

---

## 🚀 Usage

First, make sure the entrypoint script is executable:
```bash
chmod +x slapx.py
```

### GUI Dashboard (Default)
To launch the graphical visualizer control panel:
```bash
./slapx.py
```
- Click **Start Listening** to turn on the microphone.
- Adjust **Sensitivity** to match your laptop's environment.
- Tap your laptop chassis near the keyboard or trackpad to test!
- Click the **Folder Icon (📂)** in any slot to select a custom sound file.

### Headless CLI Mode
To run inside a terminal or SSH session without displaying a window:
```bash
./slapx.py --headless
```

To override settings via the CLI:
```bash
./slapx.py --headless --sensitivity 9000 --cooldown 2.0
```

---

## ⚙️ Configuration (`config.json`)

The config file is generated automatically in the directory where the command is run. Here is its structure:

```json
{
    "sensitivity": 8000,
    "cooldown": 1.5,
    "sounds": [
        "/home/user/Projects/Slapx/sounds/default_ouch.wav",
        "/home/user/Projects/Slapx/sounds/default_laser.wav",
        "/home/user/Projects/Slapx/sounds/default_slap.wav"
    ],
    "total_slaps": 42
}
```

- **`sensitivity`** (Integer): The sound threshold value (range: `500` - `30000`). Lower numbers are more sensitive; higher numbers require a harder slap.
- **`cooldown`** (Float): The duration in seconds (range: `0.1` - `5.0`) during which new slaps will be ignored to prevent feedback loops.
- **`sounds`** (Array of strings): Absolute file paths for each of the three audio slots. If a slot is empty, it falls back to the default synthesized sounds.
- **`total_slaps`** (Integer): The lifetime count of detected slaps.

---

## 🔍 Troubleshooting

- **Microphone not capturing sound**:
  Ensure that ALSA utilities can see your capture devices:
  ```bash
  arecord -l
  ```
  Make sure your microphone is not muted and the input gain is turned up in your system volume mixer (e.g., `pavucontrol` or `alsamixer`).
- **Sound delay or lag**:
  Ensure `mpv` is installed and runs correctly from your terminal. If you experience latency, it might be due to PulseAudio/Pipewire buffer settings. Slapx spawns `mpv` with low latency arguments to keep it as quick as possible.
- **No Tkinter installed error**:
  If you see `ModuleNotFoundError: No module named '_tkinter'`, install `python3-tk` using your system manager. If you cannot install graphical components, run the script with the `--headless` flag.

---

## 📄 License
This project is open-source and free to modify or distribute. Enjoy slapping!

---

## ☕ Support Me

If you find this script useful, consider supporting me:

[![Donate via Saweria](https://blue.kumparan.com/image/upload/fl_progressive,fl_lossy,c_fill,q_auto:best,w_640/v1634025439/01gvcf9vy7dhk2nkx30j2wr6n5.png)](https://saweria.co/raiinime)
