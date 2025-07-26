# client_sync.py
import threading, time
from kcp import KCPClientSync

# address, port, conv_id, no_delay, update_interval, resend_count,
# no_congestion_control, receive_window_size, send_window_size
client = KCPClientSync("127.0.0.1", 9999, 1,
                       True, 10, 2, False, 128, 128)

@client.on_start
def _():
    print("✓ connected – sending test packets")
    for i in range(3):
        client.send(f"ping {i}".encode())
        time.sleep(0.3)

@client.on_data
def _(data: bytes):
    print("⇒ echo", data)

threading.Thread(target=client.start, daemon=True).start()

while True:        # keep main thread alive
    time.sleep(1)
