# server_async.py
from kcp.server import Connection, KCPServerAsync
from kcp.exceptions import KCPConvMismatchError

server = KCPServerAsync(
    "0.0.0.0",
    9999,
    1,                 # conv_id
    no_delay=True,
    resend_count=2,    # same knobs you used before
    send_window_size=128,
)

server.set_performance_options(update_interval=10)  # 10 ms flush loop

@server.on_start
async def _():
    print("🚀  KCP server ready")

@server.on_data
async def _(conn: Connection, data):
    print(f"⇐ {conn.address}  {data!r}")
    # Ensure data is bytes, not bytearray
    if isinstance(data, bytearray):
        data = bytes(data)
    conn.enqueue(data)

# @server.on_error
# async def _(conn, exc):
#     # Hide broadcast noise that doesn’t match conv_id
#     if isinstance(exc, KCPConvMismatchError):
#         return
#     raise exc                 # re-raise everything else so you notice

server.start()
