import threading
import asyncio
import signal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio.capture_desktop import DesktopAudioStream
from video.capture import VideoCaptureEngine
from network.ipc_server import IPCServer

class SentryDaemonEngine:
    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        self.loop = None
        self.ipc = IPCServer(host=host, port=port)
        self.audio = DesktopAudioStream(on_data_callback=self.handle_audio_metrics)
        self.video = VideoCaptureEngine(on_frame_callback=self.handle_video_metrics)

    def _dispatch_broadcast(self, payload):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.ipc.broadcast(payload), self.loop)

    def handle_audio_metrics(self, risk_score):
        sys.stdout.write(f"\r[AUDIO FILTER] Synthetic Risk: {risk_score}% | Active Dashboards: {len(self.ipc.connected_clients)} ")
        sys.stdout.flush()
        self._dispatch_broadcast({"channel": "audio", "risk": risk_score})

    def handle_video_metrics(self, risk_score):
        if risk_score > 50:
            sys.stdout.write(f"\r[VIDEO ATTACK DETECTED] Biometric liveness breach! Risk: {risk_score}% ")
            sys.stdout.flush()
        self._dispatch_broadcast({"channel": "video", "risk": risk_score})

    def shutdown(self, signum=None, frame=None):
        print("\nReleasing multimedia locks. Shutting down Sentry daemon...")
        self.audio.stop()
        self.video.stop()
        sys.exit(0)

    async def run(self):
        self.loop = asyncio.get_running_loop()
        print("️ Booting Deepfake Sentry Native Core Service...")
        threading.Thread(target=self.audio.start, daemon=True).start()
        threading.Thread(target=self.video.start, daemon=True).start()
        print(" Identity Firewall Daemon Running. Listening on port 8888.")
        await self.ipc.start_server()

if __name__ == "__main__":
    engine = SentryDaemonEngine()
    signal.signal(signal.SIGINT, engine.shutdown)
    try:
        asyncio.run(engine.run())
    except (KeyboardInterrupt, SystemExit):
        engine.shutdown()
