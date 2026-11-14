"""B3 extra, inside the sandbox with the port-scoped entry: do alias spellings of the denied listener (127.0.0.1:P2) or a
second spelling of the allowed one (P1) pass the proxy's allow list? Only my own throwaway listeners are targeted."""
import os, socket, json, base64, urllib.parse
P1, P2 = int(os.environ["PROBE_P1"]), int(os.environ["PROBE_P2"])
u = urllib.parse.urlparse(os.environ["HTTPS_PROXY"])
auth = base64.b64encode(f"{urllib.parse.unquote(u.username)}:{urllib.parse.unquote(u.password)}".encode()).decode()
def connect(host, port):
    try:
        s = socket.create_connection((u.hostname, u.port), timeout=4); s.settimeout(4)
        s.sendall(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\nProxy-Authorization: Basic {auth}\r\n\r\n".encode())
        head = s.recv(1024).decode("latin1"); first = head.split("\r\n")[0]; out = {"status": first}
        if " 200" in first:
            s.sendall(b"HELLO\n"); out["reply"] = s.recv(100).decode("latin1")
        s.close(); return out
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
res = {}
for host, port in [("127.0.0.1", P1), ("127.0.0.1", P2), ("127.1", P2), ("127.0.0.1.", P2), ("0x7f.0.0.1", P2),
                   ("2130706433", P2), ("::1", P2), ("[::1]", P2), ("127.0.0.2", P2), ("LOCALHOST", P2), ("127.0.0.1", 0),
                   ("127.1", P1), ("127.0.0.1.", P1), ("127.0.0.1:" + str(P2), P1)]:
    res[f"{host}:{port}"] = connect(host, port)
out = os.path.join(os.environ["PROBE_OUT"], "alias.json")
try: open(out, "w").write(json.dumps(res, indent=1) + "\n")
except Exception as e: res["write_error"] = repr(e)
print(json.dumps(res))
