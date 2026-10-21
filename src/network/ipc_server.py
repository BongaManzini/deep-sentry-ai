import asyncio
import json
import logging
from typing import Set, Dict, Any

logger = logging.getLogger(__name__)

class IPCServer:
    """Asynchronous WebSocket and HTTP IPC server for DeepSentry telemetry."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        self.host = host
        self.port = port
        self.connected_clients: Set[Any] = set()
        self.server = None
        self._loop = None

    async def _handle_connection(self, websocket):
        """Handle individual WebSocket client connection."""
        self.connected_clients.add(websocket)
        logger.info(f"UI Console connected from {websocket.remote_address}. Total clients: {len(self.connected_clients)}")
        try:
            # Send initial handshake message
            await websocket.send(json.dumps({
                "type": "handshake",
                "status": "online",
                "engine": "DeepSentry Core 1.0"
            }))
            async for message in websocket:
                # Process any incoming telemetry or control commands from the UI
                pass
        except Exception as e:
            logger.debug(f"Client connection closed: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"UI Console disconnected. Remaining clients: {len(self.connected_clients)}")

    async def broadcast(self, payload: Dict[str, Any]):
        """Broadcast payload to all connected browser dashboards."""
        if not self.connected_clients:
            return
        message = json.dumps(payload)
        stale = set()
        for client in self.connected_clients:
            try:
                await client.send(message)
            except Exception:
                stale.add(client)
        self.connected_clients.difference_update(stale)

    async def start_server(self):
        """Start WebSocket server on the configured host and port."""
        self._loop = asyncio.get_running_loop()
        try:
            import websockets
            self.server = await websockets.serve(self._handle_connection, self.host, self.port)
            logger.info(f"DeepSentry IPC WebSocket Server listening on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Keep running indefinitely
        except ImportError:
            logger.warning("websockets package not installed. Running asyncio socket fallback server.")
            server = await asyncio.start_server(self._handle_socket_client, self.host, self.port)
            async with server:
                await server.serve_forever()

    async def _handle_socket_client(self, reader, writer):
        # Basic raw TCP / HTTP handshake fallback
        request = await reader.read(1024)
        if b"Upgrade: websocket" in request:
            # Note websockets module requirement for RFC6455
            writer.write(b"HTTP/1.1 400 WebSockets library required\r\n\r\n")
        else:
            response = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"status\":\"online\"}"
            writer.write(response)
        await writer.drain()
        writer.close()
