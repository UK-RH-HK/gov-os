"""B3 probe, run inside the sandbox: can a sandboxed process reach a loopback TCP listener? (direct, HTTP CONNECT, SOCKS5)
Env: PROBE_OUT (dir, writable), PROBE_P1, PROBE_P2 (throwaway listener ports). Also one GET /api/version at Ollama 127.0.0.1:11434."""
import os, socket, json, re, urllib.parse, base64
P1, P2 = int(os.environ["PROBE_P1"]), int(os.environ["PROBE_P2"])
T = 4
def redact(v):  # the proxy's per-session credential is not recorded
    return re.sub(r"//[^@/]*@", "//<cred>@", v) if "@" in v else v
res = {"env": {k: redact(v) for k, v in os.environ.items() if re.search("proxy", k, re.I) and "PASSWORD" not in k and "USERNAME" not in k}}

def direct(host, port, payload=b"HELLO\n"):
    try:
        s = socket.create_connection((host, port), timeout=T); s.sendall(payload); s.settimeout(T)
        d = s.recv(300); s.close(); return {"ok": True, "reply": d.decode("latin1")[:200]}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

def proxy_of(*names):
    for n in names:
        for k in (n, n.upper(), n.lower()):
            if os.environ.get(k): return os.environ[k]
def via_http(host, port, payload=b"HELLO\n"):
    pr = proxy_of("http_proxy", "https_proxy", "all_proxy")
    if not pr or not pr.startswith("http"): return {"ok": False, "error": "no http proxy in env"}
    u = urllib.parse.urlparse(pr)
    try:
        s = socket.create_connection((u.hostname, u.port), timeout=T); s.settimeout(T)
        auth = ""
        if u.username:
            auth = "Proxy-Authorization: Basic " + base64.b64encode(f"{urllib.parse.unquote(u.username)}:{urllib.parse.unquote(u.password or '')}".encode()).decode() + "\r\n"
        s.sendall(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n{auth}\r\n".encode())
        head = b""
        while b"\r\n\r\n" not in head and len(head) < 4000:
            c = s.recv(1024)
            if not c: break
            head += c
        first = head.split(b"\r\n")[0].decode("latin1")
        out = {"proxy": redact(pr), "connect_status": first, "head": head.decode("latin1")[:300]}
        if " 200" in first:
            s.sendall(payload); body = head.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in head else b""
            try: body += s.recv(600)
            except Exception as e: out["recv_error"] = repr(e)
            out["ok"] = True; out["reply"] = body.decode("latin1")[:300]
        else: out["ok"] = False
        s.close(); return out
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "proxy": redact(pr)}

def via_socks(host, port, payload=b"HELLO\n"):
    pr = proxy_of("all_proxy")
    if not pr or not pr.startswith("socks"): 
        for k, v in os.environ.items():
            if v.startswith("socks"): pr = v
    if not pr or not pr.startswith("socks"): return {"ok": False, "error": "no socks proxy in env"}
    u = urllib.parse.urlparse(pr)
    try:
        s = socket.create_connection((u.hostname, u.port), timeout=T); s.settimeout(T)
        s.sendall(b"\x05\x01\x00"); g = s.recv(2)
        hb = host.encode()
        s.sendall(b"\x05\x01\x00\x03" + bytes([len(hb)]) + hb + port.to_bytes(2, "big"))
        r = s.recv(10); out = {"proxy": redact(pr), "greeting": g.hex(), "connect_reply": r.hex()}
        if len(r) > 1 and r[1] == 0:
            s.sendall(payload)
            try: out["reply"] = s.recv(600).decode("latin1")[:300]
            except Exception as e: out["recv_error"] = repr(e)
            out["ok"] = True
        else: out["ok"] = False
        s.close(); return out
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "proxy": redact(pr)}

GET = lambda h, p: f"GET /api/version HTTP/1.1\r\nHost: {h}:{p}\r\nConnection: close\r\n\r\n".encode()
targets = [("127.0.0.1", P1), ("127.0.0.1", P2), ("localhost", P1), ("localhost", P2)]
for h, p in targets:
    k = f"{h}:{p}"
    res["direct " + k] = direct(h, p)
    res["http_connect " + k] = via_http(h, p)
    res["socks5 " + k] = via_socks(h, p)
# item 3: Ollama, one GET /api/version, nothing else
for h in ("127.0.0.1", "localhost"):
    k = f"{h}:11434"
    res["OLLAMA direct " + k] = direct(h, 11434, GET(h, 11434))
    res["OLLAMA http_connect " + k] = via_http(h, 11434, GET(h, 11434))
    res["OLLAMA socks5 " + k] = via_socks(h, 11434, GET(h, 11434))
out = os.path.join(os.environ.get("PROBE_OUT", "/tmp"), "probe.json")
try: open(out, "w").write(json.dumps(res, indent=1) + "\n")
except Exception as e: res["write_error"] = repr(e)
print(json.dumps(res))
