"""Shared pieces for the effort measurement (owner's question, 2026-11-13): prices, windows, transcript usage reader.
Reads only usage numbers, model names and timestamps from the CTO transcripts; never message text."""
import json, os, glob, datetime as dt
from datetime import timezone

ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
PROJ = "/home/usain/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS"
OUT = ORCH + "/drafts/effort-20261113"

def epoch(s):
    """UTC epoch from '2026-11-11 13:31[:ss]', ISO with T/Z, or None."""
    if s is None: return None
    s = str(s).strip().replace("T", " ").replace("Z", "")
    for f in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return dt.datetime.strptime(s[:26] if "%f" in f else s[:19 if "%S" in f else 16], f).replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass
    return None

def fmt(t):
    return dt.datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d %H:%M")

LIFT = epoch("2026-11-11 13:31")
NOW = float(os.environ.get("EFFORT_NOW") or epoch("2026-11-13 16:05"))
WINDOWS = {"A": (LIFT, NOW), "B": (NOW - 86400, NOW)}

# list prices, USD per million tokens (USAGE-1 §8, platform.claude.com/docs/en/about-claude/pricing, 2026-11-10):
# in, 5-min write, 1-h write, cache read, out. Haiku: up to 100k prompt / above.
PRICE = {
    "opus": (4.0, 5.0, 8.0, 0.20, 20.0),
    "sonnet": (2.0, 2.5, 4.0, 0.10, 10.0),
    "haiku_lo": (0.10, 0.125, 0.20, 0.01, 0.50),
    "haiku_hi": (0.50, 0.625, 1.0, 0.05, 2.50),
}

def tier(model):
    m = (model or "").lower()
    for t in ("opus", "sonnet", "haiku"):
        if t in m: return t
    return None

def cost_of(model, u):
    t = tier(model)
    if t is None: return None
    i = u.get("input_tokens") or 0
    cr = u.get("cache_read_input_tokens") or 0
    cw = u.get("cache_creation_input_tokens") or 0
    cc = u.get("cache_creation") or {}
    w5 = cc.get("ephemeral_5m_input_tokens"); w1 = cc.get("ephemeral_1h_input_tokens")
    if w5 is None and w1 is None: w5, w1 = cw, 0
    w5 = w5 or 0; w1 = w1 or 0
    o = u.get("output_tokens") or 0
    p = PRICE[t] if t != "haiku" else (PRICE["haiku_hi"] if (i + cr + cw) > 100000 else PRICE["haiku_lo"])
    return (i * p[0] + w5 * p[1] + w1 * p[2] + cr * p[3] + o * p[4]) / 1e6

def read_transcript(path):
    """-> list of (epoch, model, usd, out_tokens) one per assistant API message (de-duplicated by message id)."""
    best = {}
    try:
        f = open(path, errors="replace")
    except OSError:
        return []
    for l in f:
        if '"usage"' not in l: continue
        try: d = json.loads(l)
        except ValueError: continue
        m = d.get("message")
        if not isinstance(m, dict) or "usage" not in m: continue
        model = m.get("model")
        if tier(model) is None: continue
        key = m.get("id") or d.get("requestId") or d.get("uuid")
        u = m["usage"]
        t = epoch(d.get("timestamp"))
        if t is None: continue
        old = best.get(key)
        if old is None or (u.get("output_tokens") or 0) >= (old[1].get("output_tokens") or 0):
            best[key] = (t if old is None else old[0], u, model, d.get("isSidechain"))
    out = []
    for key, (t, u, model, side) in best.items():
        out.append((t, model, cost_of(model, u), u.get("output_tokens") or 0))
    out.sort()
    return out
