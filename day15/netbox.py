# netbox.py
import threading, json
from kcp import KCPClientSync
from kcp.server import KCPServerAsync, Connection

class GameSyncNet:
    def __init__(self, mode, host='127.0.0.1', port=9999, player_id=0):
        self.mode = mode
        self.player_id = player_id
        self.positions = {}   # {id: {'x':..., 'y':...}}
        self.running = True

        if mode == 'server':
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
                    # Assign unique id if new connection
                    if addr not in self.server_players:
                        self.server_players[addr] = self.server_next_id
                        print(f"[SERVER] New client {addr} assigned id {self.server_next_id}")
                        self.server_next_id += 1
                    pid = self.server_players[addr]
                    self.positions[pid] = payload['pos']
                    # Send full state to all
                    state = {'positions': self.positions}
                    data_out = json.dumps(state).encode()
                    for conn2 in self.server.connections:
                        conn2.enqueue(data_out)
                except Exception as e:
                    print("[SERVER] on_data error:", e)

            threading.Thread(target=self.server.start, daemon=True).start()

        elif mode == 'client':
            self.client = KCPClientSync(host, port, 1, True, 10, 2, False, 128, 128)
            self.connected = False

            @self.client.on_start
            def _():
                print("[CLIENT] Connected")
                self.connected = True

            @self.client.on_data
            def _(data):
                try:
                    state = json.loads(bytes(data).decode())
                    self.positions = state['positions']
                except Exception as e:
                    print("[CLIENT] on_data error:", e)

            threading.Thread(target=self.client.start, daemon=True).start()

    def send_position(self, x, y):
        packet = {'pos': {'x': x, 'y': y}}
        data = json.dumps(packet).encode()
        if self.mode == 'client':
            self.client.send(data)
        # server doesn't send positions (observer only)

    def get_positions(self):
        return dict(self.positions)

    def close(self):
        self.running = False

