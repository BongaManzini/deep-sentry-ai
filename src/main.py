import threading
import asyncio
import signal
import sys
from audio.capture_desktop import DesktopAudioStream
from video.capture import VideoCaptureEngine
from network.ipc_server import IPCServer

class SentryCoreEngine:
    def __init__(self):
        self.running = True
        self.ipc = IPCServer(host="127.0.0.1", port=8888)
        self.audio = DesktopAudioStream(on_data_callback=self.handle_audio_metrics)
        self.video = VideoCaptureEngine(on_frame_callback=self.handle_video_metrics)

    def handle_audio_metrics(self, risk_score):
        """Dispatches real-time calculations to the UI thread via local network."""
        asyncio.run(self.ipc.broadcast({"channel": "audio", "risk": risk_score}))

    def handle_video_metrics(self, risk_score):
        asyncio.run(self.ipc.broadcast({"channel": "video", "risk": risk_score}))

    def shutdown(self, signum, frame):
        print("\nStopping Sentry Background Daemon...")
        self.audio.stop()
        self.video.stop()
        sys.exit(0)

if __name__ == "__main__":
    engine = SentryCoreEngine()
    # Intercept system termination signals (e.g., Ctrl+C) for clean hardware releases
    signal.signal(signal.SIGINT, engine.shutdown)
    
    # Fire up hardware monitoring modules in independent background threads
    threading.Thread(target=engine.audio.start, daemon=True).start()
    threading.Thread(target=engine.video.start, daemon=True).start()
    
    # Run the communication server on the main execution thread
    asyncio.run(engine.ipc.start_server())