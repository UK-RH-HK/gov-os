"""Throwaway TCP listener(s) on 127.0.0.1 for the B3 probe. Usage: listener.py LOG PORT [PORT ...]
Each accepted connection is logged (port, peer address) and answered with 'B3-OK <port>' after the client sends a line."""
import socket, sys, threading, time
log, ports = sys.argv[1], [int(p) for p in sys.argv[2:]]
lock = threading.Lock()
def note(s):
    with lock, open(log, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {s}\n")
def serve(port):
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port)); s.listen(8)
    while True:
        c, peer = s.accept()
        note(f"port {port} accepted from {peer}")
        def one(c=c, port=port):
            try:
                c.settimeout(3); data = c.recv(256)
                note(f"port {port} got {data[:40]!r}")
                c.sendall(f"B3-OK {port}\n".encode())
            except Exception as e:
                note(f"port {port} error {e!r}")
            finally:
                c.close()
        threading.Thread(target=one, daemon=True).start()
for p in ports:
    threading.Thread(target=serve, args=(p,), daemon=True).start()
note(f"listening {ports} pid")
while True:
    time.sleep(1)
