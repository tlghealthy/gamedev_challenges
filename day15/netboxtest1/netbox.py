# netbox.py
import threading, json, time
from kcp import KCPClientSync
from kcp.server import KCPServerAsync, Connection

class GameSyncNet:
    HANDSHAKE_PERIOD = 0.5          # seconds

    def __init__(self, mode, host='127.0.0.1', port=9999):
        self.mode = mode
        self.player_id = None
        self.positions = {}   # {id: {'x':..., 'y':...}}
        self.running = True
        self.connected = False

        if mode == 'server':
            # --- inside GameSyncNet.__init__, server branch ----
            self.server_conns = []    # NEW: list of active Connection objects
            self.server = KCPServerAsync(host, port, 1, no_delay=True, resend_count=2, send_window_size=128)
            self.server.set_performance_options(update_interval=10)
            self.server_players = {}   # addr -> player_id
            self.server_next_id = 1    # Start at 1 for clients

            @self.server.on_start
            async def _():
                print("[SERVER] Ready")

            @self.server.on_data
            async def _(conn: Connection, data):
                
                try:
                    payload = json.loads(bytes(data).decode())
                    addr = conn.address
                    # print("[SERVER] raw payload from", addr, ":", payload)

                    # Handshake: assign player_id only on {"hello": ...}
                    if addr not in self.server_players:
                        if "hello" in payload:
                            pid = self.server_next_id
                            self.server_players[addr] = pid
                            self.server_next_id += 1
                            self.server_conns.append(conn)             # <-- keep it
                            print(f"[SERVER] New client {addr} assigned id {pid}")
                            # Tell the new client their id
                            conn.enqueue(json.dumps({"your_id": pid}).encode())
                        # Ignore anything else until client gets its id
                        return

                    pid = self.server_players[addr]
                    # Only update positions for known players and valid packets
                    if 'pos' in payload:
                        self.positions[pid] = payload['pos']

                    # Broadcast all positions to all clients
                    state = {'positions': self.positions}
                    data_out = json.dumps(state).encode()
                    for conn2 in self.server_conns:
                        conn2.enqueue(data_out)
                except Exception as e:
                    print("[SERVER] on_data error:", e)

            threading.Thread(target=self.server.start, daemon=True).start()

        elif mode == 'client':
            self._last_hello = 0        # track last send time

            self.client = KCPClientSync(host, port, 1, True, 10, 2, False, 128, 128)

            @self.client.on_start
            def _():
                print("[CLIENT] Socket ready")
                self.connected = True
                self._send_hello()      # send first hello immediately

            @self.client.on_data
            def _(data):
                try:
                    msg = json.loads(bytes(data).decode())
                    # print("[CLIENT] got msg:", msg)
                    if "your_id" in msg:
                        self.player_id = msg["your_id"]
                        print(f"[CLIENT] Assigned player_id={self.player_id}")
                    elif "positions" in msg:
                        self.positions = msg["positions"]
                except Exception as e:
                    print("[CLIENT] on_data error:", e)

            threading.Thread(target=self.client.start, daemon=True).start()

    def _send_hello(self):
        self.client.send(json.dumps({"hello": 1}).encode())
        self._last_hello = time.time()

    def poll(self):
        """Call this once per frame from the game loop."""
        if self.mode == 'client' and self.player_id is None:
            if time.time() - self._last_hello >= self.HANDSHAKE_PERIOD:
                self._send_hello()

    def send_position(self, x, y):
        if self.mode == 'client' and self.player_id:
            packet = {'pos': {'x': x, 'y': y}}
            data = json.dumps(packet).encode()
            self.client.send(data)

    def get_positions(self):
        return dict(self.positions)

    def get_player_id(self):
        return self.player_id
