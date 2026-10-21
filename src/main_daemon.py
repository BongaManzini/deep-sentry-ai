import threading
import asyncio
import signal
import sys
import json
import cv2

# Natively map to the nested sub-packages you created
from audio.capture_desktop import DesktopAudioStream
from video.capture import VideoCaptureEngine
from network.ipc_server import IPCServer

class SentryCoreEngine:
    def __init__(self):
        self.ipc = IPCServer(host="127.0.0.1", port=8888)
        self.audio = DesktopAudioStream(on_data_callback=self.handle_audio_metrics)
        self.video = VideoCaptureEngine(on_frame_callback=self.handle_video_metrics)

    def handle_audio_metrics(self, risk_score):
        sys.stdout.write(f"\r[AUDIO FILTER] Synthetic Risk Factor: {risk_score}% | Connected Dashboards: {len(self.ipc.connected_clients)}")
        sys.stdout.flush()
        self._dispatch_broadcast({"channel": "audio", "risk": risk_score})

    def handle_video_metrics(self, risk_score):
        if risk_score > 50:
            sys.stdout.write(f"\r[VIDEO ATTACK DETECTED] Spatial liveness mesh tracking breached baseline parameters! ")
            sys.stdout.flush()
        self._dispatch_broadcast({"channel": "video", "risk": risk_score})

    def _dispatch_broadcast(self, payload):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.ipc.broadcast(payload))
        except RuntimeError:
            asyncio.run(self.ipc.broadcast(payload))

    def shutdown(self, signum, frame):
        print("\nReleasing local multimedia locks. Shutting down Sentry daemon process...")
        self.audio.stop()
        self.video.stop()
        sys.exit(0)

if __name__ == "__main__":
    engine = SentryCoreEngine()
    signal.signal(signal.SIGINT, engine.shutdown)
    
    print("🛡️ Booting Deepfake Sentry Native Core Service on Linux...")
    threading.Thread(target=engine.audio.start, daemon=True).start()
    threading.Thread(target=engine.video.start, daemon=True).start()
    
    print("🟢 Identity Firewall Daemon Running. Broadcasters Listening on Local Loopback Port 8888.")
    asyncio.run(engine.ipc.start_server())
