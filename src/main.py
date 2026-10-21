import threading
import asyncio
import signal
import sys
import os

# Ensure src directory is in sys.path for cross-platform imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio.capture_desktop import DesktopAudioStream
from video.capture import VideoCaptureEngine
from network.ipc_server import IPCServer

class SentryCoreEngine:
    """Core multithreaded engine coordinating audio, video, and IPC broadcasting."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        self.running = True
        self.loop = None
        self.ipc = IPCServer(host=host, port=port)
        self.audio = DesktopAudioStream(on_data_callback=self.handle_audio_metrics)
        self.video = VideoCaptureEngine(on_frame_callback=self.handle_video_metrics)

    def _safe_broadcast(self, payload):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.ipc.broadcast(payload), self.loop)

    def handle_audio_metrics(self, risk_score):
        """Dispatches real-time calculations to the UI thread via local network."""
        self._safe_broadcast({"channel": "audio", "risk": risk_score})

    def handle_video_metrics(self, risk_score):
        self._safe_broadcast({"channel": "video", "risk": risk_score})

    def shutdown(self, signum=None, frame=None):
        print("\nStopping Sentry Background Daemon...")
        self.running = False
        self.audio.stop()
        self.video.stop()
        sys.exit(0)

    async def run(self):
        self.loop = asyncio.get_running_loop()
        print("🛡️ Booting Deepfake Sentry Core Service...")
        threading.Thread(target=self.audio.start, daemon=True).start()
        threading.Thread(target=self.video.start, daemon=True).start()
        print("🟢 Identity Firewall Running. Listening on ws://127.0.0.1:8888")
        await self.ipc.start_server()

if __name__ == "__main__":
    engine = SentryCoreEngine()
    signal.signal(signal.SIGINT, engine.shutdown)
    try:
        asyncio.run(engine.run())
    except (KeyboardInterrupt, SystemExit):
        engine.shutdown()