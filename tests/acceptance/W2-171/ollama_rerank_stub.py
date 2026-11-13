"""Stand-ins for the shared Ollama servers and the reranker service (F4), logging every request they receive.

``python3 ollama_rerank_stub.py <folder> [<rerank socket path>]`` starts two HTTP servers (stand-ins for the Ollama
servers on 11434 and 11435) on free loopback ports and, when a path is given, a unix-socket server (the reranker's
``rerank.sock``). It writes ``ports.json`` (``{"a": port, "b": port}``) when ready, one line per request to
``a.log``, ``b.log`` and ``rerank.log`` (JSON: method, path, body keys; or the socket line's ``op``), and a line to
``signals.log`` for every signal it receives (it ignores them, to be seen: F4 asserts none arrives).
"""
import http.server
import json
import os
import signal
import socket
import socketserver
import sys
import threading

FOLDER = sys.argv[1]
SOCK = sys.argv[2] if len(sys.argv) > 2 else None
LOCK = threading.Lock()


def log(name, obj):
    with LOCK, open(os.path.join(FOLDER, name), "a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")


def handler(name):
    class H(http.server.BaseHTTPRequestHandler):
        def _answer(self):
            size = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(size) if size else b""
            try:
                keys = sorted(json.loads(raw)) if raw else []
            except ValueError:
                keys = ["unparsed"]
            log(name + ".log", {"method": self.command, "path": self.path, "keys": keys})
            body = b'{"embeddings": [[0.0]]}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_POST = do_GET = do_DELETE = do_PUT = _answer

        def log_message(self, *args):
            pass
    return H


class Threaded(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def serve_rerank():
    server = socket.socket(socket.AF_UNIX)
    server.bind(SOCK)
    server.listen(16)
    while True:
        conn, _ = server.accept()
        with conn:
            line = conn.makefile("rb").readline()
            try:
                op = json.loads(line).get("op")
            except ValueError:
                op = "unparsed"
            log("rerank.log", {"op": op})
            conn.sendall(b"{}\n")


def main():
    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT, signal.SIGUSR1, signal.SIGUSR2, signal.SIGQUIT):
        signal.signal(sig, lambda s, f: log("signals.log", {"signal": int(s)}))
    servers = {n: Threaded(("127.0.0.1", 0), handler(n)) for n in ("a", "b")}
    for server in servers.values():
        threading.Thread(target=server.serve_forever, daemon=True).start()
    if SOCK:
        threading.Thread(target=serve_rerank, daemon=True).start()
    with open(os.path.join(FOLDER, "ports.json.tmp"), "w", encoding="utf-8") as f:
        json.dump({n: s.server_address[1] for n, s in servers.items()}, f)
    os.replace(os.path.join(FOLDER, "ports.json.tmp"), os.path.join(FOLDER, "ports.json"))
    while True:
        signal.pause()


if __name__ == "__main__":
    main()
