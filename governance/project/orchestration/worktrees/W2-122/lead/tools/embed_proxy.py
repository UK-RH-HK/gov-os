"""A counting pass-through in front of the shared embedding server, for W2-122's KPI 3 measurement.

Usage: python3 embed_proxy.py <listen port> <count file>
Forwards every request to 127.0.0.1:11434 unchanged and, for each POST to /api/embed, adds one request and the number
of inputs to the counts, written as JSON to <count file> after every request.
"""

import http.client
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = ("127.0.0.1", 11434)
PORT = int(sys.argv[1])
COUNT_FILE = sys.argv[2]
_lock = threading.Lock()
_counts = {"embed_requests": 0, "embed_inputs": 0, "other_requests": 0}


def _write():
    with open(COUNT_FILE, "w") as handle:
        json.dump(_counts, handle)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _forward(self, method):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        with _lock:
            if method == "POST" and self.path.startswith("/api/embed"):
                _counts["embed_requests"] += 1
                try:
                    given = json.loads(body or b"{}").get("input")
                    _counts["embed_inputs"] += len(given) if isinstance(given, list) else 1
                except ValueError:
                    pass
            else:
                _counts["other_requests"] += 1
            _write()
        connection = http.client.HTTPConnection(*UPSTREAM, timeout=600)
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "connection")}
        connection.request(method, self.path, body=body, headers=headers)
        answer = connection.getresponse()
        data = answer.read()
        self.send_response(answer.status)
        for key, value in answer.getheaders():
            if key.lower() not in ("transfer-encoding", "connection", "content-length"):
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        connection.close()

    def do_GET(self):
        self._forward("GET")

    def do_POST(self):
        self._forward("POST")

    def do_HEAD(self):
        self._forward("HEAD")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    _write()
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
