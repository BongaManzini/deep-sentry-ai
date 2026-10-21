# DeepSentryAI – Real-Time Deepfake Detection for Call Centers

> An enterprise-grade multimodal identity firewall that detects deepfake audio and video threats in real time, purpose-built for call center environments.

---

## Overview

DeepSentryAI is a background daemon service that continuously monitors webcam feeds and desktop audio streams for signs of synthetic media manipulation. When a threat is detected — such as AI-generated voice cloning or face-swap video attacks — it broadcasts risk scores in real time to a browser-based console UI over a local WebSocket connection.

It is designed to be invisible to the caller yet always active, running silently in the background while agents interact with customers.

---

## Features

- **Deepfake Audio Detection** — Analyses live desktop audio using spectral feature variance and acoustic timbre profiling to flag AI-synthesised voice streams
- **Deepfake Video Detection** — Monitors webcam feeds for static geometric coordinates, missing blink profiles, and spatial liveness mesh anomalies
- **Real-Time Risk Scoring** — Continuously computes and broadcasts per-channel threat levels (0–100%) to connected dashboards
- **Local IPC via WebSocket** — Daemon communicates with the UI over `127.0.0.1:8888` using an async WebSocket broadcast server
- **Call Center Console UI** — Dark-themed, Tailwind CSS dashboard with live video, audio telemetry, and security assessment panels
- **Clean Signal Handling** — Captures `SIGINT` for graceful hardware release and daemon shutdown
- **Threaded Architecture** — Audio and video capture run in independent daemon threads; the IPC server runs on the main thread

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ |
| Video Capture | OpenCV (`cv2`) |
| Audio Capture | Custom desktop audio stream module |
| Async Networking | `asyncio`, WebSockets |
| Frontend | HTML5, Tailwind CSS (CDN) |
| ML / AI | Planned: `.h5` / `.pt` model files for deepfake classifiers |

---

## Project Structure

```
DeepSentryAI/
├── index.html              # Call center console UI
├── requirements.txt        # Python dependencies
├── src/
│   ├── main.py             # Core engine entry point
│   ├── main_daemon.py      # Full daemon with verbose terminal output
│   ├── audio/
│   │   └── capture_desktop.py   # Desktop audio stream & analysis
│   ├── video/
│   │   └── capture.py           # Webcam frame capture & analysis
│   └── network/
│       └── ipc_server.py        # WebSocket IPC broadcast server
└── models/                 # (gitignored) ML model weights
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- A webcam and microphone accessible to the OS
- A modern browser (for the console UI)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/DeepSentryAI.git
cd DeepSentryAI
```

### 2. Create and activate a virtual environment

```bash
python -m venv sentry_env
source sentry_env/bin/activate        # Linux / macOS
# sentry_env\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the detection daemon

```bash
python src/main.py
```

For verbose terminal output (recommended for monitoring):

```bash
python src/main_daemon.py
```

The daemon will start listening on `127.0.0.1:8888`.

### 5. Open the console UI

Open `index.html` directly in your browser. The dashboard will connect to the daemon automatically and begin displaying live risk scores.

---

## Usage

Once running, the system operates automatically:

| Event | Behaviour |
|-------|-----------|
| Audio risk score rises | Dashboard updates spectral variance metrics in real time |
| Video risk score > 50% | `[VIDEO ATTACK DETECTED]` alert printed to terminal + HUD alert shown in UI |
| `Ctrl+C` pressed | Daemon gracefully releases hardware locks and exits |

### Risk Score Interpretation

| Score | Status |
|-------|--------|
| 0–30% | ✅ Target Compliant |
| 31–60% | ⚠️ Elevated Suspicion |
| 61–100% | 🚨 Biometric Tampering Detected |

---

## Configuration

The IPC server binds to `127.0.0.1:8888` by default. To change the host or port, edit the constructor in [`src/main.py`](src/main.py):

```python
self.ipc = IPCServer(host="127.0.0.1", port=8888)
```

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 DeepSentryAI Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
