#!/usr/bin/env python3
"""USAGE-1: collect usage metadata from Claude Code transcripts since the week's reset.

Reads ONLY metadata: model, usage fields, timestamps, session/agent ids, cwd, effort, system subtypes
(compactions), tool names, Read paths (hashed, never printed), tool-result sizes (lengths only), and the first
user message (used only for a regex ticket id and a coarse kind; never written out).
Skips any path containing the held-out folder's name.

    python3 -I collect.py            writes calls.jsonl and sessions.json beside this file
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = Path.home() / ".claude/projects"
RESET = datetime(2026, 11, 8, 9, 0, tzinfo=timezone.utc)
RESET_TS = RESET.timestamp()
CUTOFF = os.environ.get("USAGE_CUTOFF", "2026-11-10T11:36:43")  # the last meter reading used (UTC)
SKIP = "gov-os-" + "eval"  # never opened
MAIN = "-home-usain-Dynamic-Agentic-Engineering-OS"
CTO = "ad44f5fe-276d-46b7-85cd-df9f8d97a3ec"
SENTINEL = "b6a01869-d922-4803-afab-e986fcc71663"
TICKET_RE = re.compile(r"\b(W[12]-\d+[a-z]?|ACT-[A-Z0-9-]+|DAEO-[a-z0-9]{4}|D-?\d{1,2}\b)")

# list prices, USD per MTok: base input, 5m write, 1h write, cache read, output
# (platform.claude.com/docs/en/about-claude/pricing, fetched 2026-11-10)
PRICES = {
    "claude-opus-5-5": (4.0, 5.0, 8.0, 0.20, 20.0),
    "claude-sonnet-5-5": (2.0, 2.5, 4.0, 0.10, 10.0),
    "claude-haiku-5-5": (0.10, 0.125, 0.20, 0.01, 0.50),       # prompt <= 100k
    "claude-haiku-5-5>100k": (0.50, 0.625, 1.0, 0.05, 2.50),   # prompt > 100k
    "claude-fable-5-1": (10.0, 12.5, 20.0, 0.25, 50.0),
}
FAST = {"claude-opus-5-5": 2.0}  # fast mode: $8/$40 = 2x standard


def price(model, inp, w5, w1, cr, out, speed):
    if model not in PRICES:
        return None
    key = model
    if model == "claude-haiku-5-5" and inp + w5 + w1 + cr > 100_000:
        key = "claude-haiku-5-5>100k"
    p = PRICES[key]
    c = (inp * p[0] + w5 * p[1] + w1 * p[2] + cr * p[3] + out * p[4]) / 1e6
    if speed == "fast":
        c *= FAST.get(model, 1.0)
    return c


def classify(folder, rel):
    """source kind from the transcript's place (refined later by first prompt)."""
    if folder == MAIN:
        if rel.startswith(CTO + "/"):
            return "cto-helper"
        if rel == CTO + ".jsonl":
            return "cto"
        if rel.startswith(SENTINEL):
            return "sentinel" if rel.endswith(".jsonl") and "/" not in rel else "sentinel-helper"
        return "main-other"
    if folder == "-tmp":
        return "tmp"
    if folder.startswith("-home-usain-gov-os-worktrees-"):
        return "worktree"
    if folder.startswith("-home-usain-gov-os-runs-"):
        return "runs"
    if folder.startswith("-tmp-claude-1000-") and "scratchpad" in folder:
        return "cto-scratch-tests"
    if folder.startswith("-tmp-gov-accept-") or folder.startswith("-tmp-gov-os-emg-"):
        return "accept-tests"
    if folder == "-home-usain-gov-os-writer":
        return "writer"
    return "other"


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                return b.get("text", "")
    return ""


def main():
    calls, sessions = [], {}
    for folder in sorted(os.listdir(PROJ)):
        if SKIP in folder:
            continue
        root = PROJ / folder
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if SKIP in dirpath:
                continue
            dirnames[:] = [d for d in dirnames if d != "tool-results"]
            for fn in filenames:
                if not fn.endswith(".jsonl"):
                    continue
                path = Path(dirpath) / fn
                if path.stat().st_mtime < RESET_TS:
                    continue
                rel = str(path.relative_to(root))
                kind = classify(folder, rel)
                meta = {}
                mp = path.with_suffix(".meta.json")
                if mp.exists():
                    try:
                        m = json.loads(mp.read_text())
                        meta = {k: m.get(k) for k in ("agentType", "description", "spawnDepth", "pickedEffortModel",
                                                      "requestShape")}
                    except ValueError:
                        pass
                key = f"{folder}/{rel}"
                s = dict(key=key, folder=folder, rel=rel, kind=kind, meta=meta, first_ts=None, last_ts=None,
                         session_id=None, agent_id=None, cwd=None, entrypoint=None, efforts={}, models={},
                         calls=0, human_turns=0, compactions=0, api_errors=0, tools={}, reads=0, read_paths=set(),
                         result_chars={}, ids=[], first_kind=None, wake_kinds={}, ctx=[])
                seen = set()
                tool_names = {}
                first_user_done = False
                with open(path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                        except ValueError:
                            continue
                        t = d.get("type")
                        ts = d.get("timestamp")
                        s["session_id"] = s["session_id"] or d.get("sessionId")
                        s["agent_id"] = s["agent_id"] or d.get("agentId")
                        s["cwd"] = s["cwd"] or d.get("cwd")
                        s["entrypoint"] = s["entrypoint"] or d.get("entrypoint")
                        if t == "system":
                            st = d.get("subtype")
                            if ts and ts >= "2026-11-08T09:00":
                                if st == "compact_boundary":
                                    s["compactions"] += 1
                                elif st == "api_error":
                                    s["api_errors"] += 1
                            continue
                        if t == "user":
                            msg = d.get("message") or {}
                            c = msg.get("content")
                            is_tool_result = isinstance(c, list) and any(
                                isinstance(b, dict) and b.get("type") == "tool_result" for b in c)
                            if is_tool_result:
                                if ts and ts >= "2026-11-08T09:00":
                                    for b in c:
                                        if isinstance(b, dict) and b.get("type") == "tool_result":
                                            n = len(json.dumps(b.get("content"), ensure_ascii=False))
                                            nm = tool_names.get(b.get("tool_use_id"), "?")
                                            s["result_chars"][nm] = s["result_chars"].get(nm, 0) + n
                                continue
                            if d.get("isMeta"):
                                continue
                            txt = text_of(c)
                            if not first_user_done:
                                first_user_done = True
                                s["ids"] = sorted(set(TICKET_RE.findall(txt[:4000])))[:6]
                                head = txt.lstrip()[:120]
                                if head.startswith("/usage"):
                                    s["first_kind"] = "usage-cmd"
                                elif head.startswith("Load the PushNotification tool"):
                                    s["first_kind"] = "push"
                                elif "sandbox check" in head or head.startswith("Step 0"):
                                    s["first_kind"] = "launched-brief"
                            if ts and ts >= "2026-11-08T09:00":
                                s["human_turns"] += 1
                                m = re.match(r"\s*<([a-z][a-z0-9-]{2,30})", txt)
                                wk = m.group(1) if m else "text"
                                s["wake_kinds"][wk] = s["wake_kinds"].get(wk, 0) + 1
                            continue
                        if t != "assistant":
                            continue
                        msg = d.get("message") or {}
                        for b in msg.get("content") or []:
                            if isinstance(b, dict) and b.get("type") == "tool_use":
                                tool_names[b.get("id")] = b.get("name")
                                if ts and ts >= "2026-11-08T09:00":
                                    s["tools"][b.get("name")] = s["tools"].get(b.get("name"), 0) + 1
                                    if b.get("name") == "Read":
                                        fp = str((b.get("input") or {}).get("file_path", ""))
                                        s["reads"] += 1
                                        s["read_paths"].add(hashlib.sha1(fp.encode()).hexdigest()[:12])
                        mid = msg.get("id") or d.get("requestId") or d.get("uuid")
                        if mid in seen:
                            continue
                        seen.add(mid)
                        u = msg.get("usage")
                        model = msg.get("model")
                        if not u or model == "<synthetic>" or not ts or ts < "2026-11-08T09:00" or ts[:19] > CUTOFF:
                            continue
                        cc = u.get("cache_creation") or {}
                        w5 = cc.get("ephemeral_5m_input_tokens")
                        w1 = cc.get("ephemeral_1h_input_tokens")
                        ccin = u.get("cache_creation_input_tokens") or 0
                        if w5 is None and w1 is None:
                            w5, w1 = ccin, 0
                        w5, w1 = w5 or 0, w1 or 0
                        inp = u.get("input_tokens") or 0
                        cr = u.get("cache_read_input_tokens") or 0
                        out = u.get("output_tokens") or 0
                        speed = u.get("speed")
                        think = (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
                        cost = price(model, inp, w5, w1, cr, out, speed)
                        calls.append(dict(key=key, kind=kind, ts=ts, model=model, inp=inp, w5=w5, w1=w1, cr=cr,
                                          out=out, think=think, cost=cost, speed=speed, effort=d.get("effort")))
                        s["calls"] += 1
                        s["models"][model] = s["models"].get(model, 0) + 1
                        e = str(d.get("effort"))
                        s["efforts"][e] = s["efforts"].get(e, 0) + 1
                        s["ctx"].append(inp + cr)
                        s["first_ts"] = s["first_ts"] or ts
                        s["last_ts"] = ts
                s["read_distinct"] = len(s.pop("read_paths"))
                sessions[key] = s
    with open(HERE / "calls.jsonl", "w") as f:
        for c in calls:
            f.write(json.dumps(c) + "\n")
    (HERE / "sessions.json").write_text(json.dumps(sessions, indent=0))
    print(f"{len(sessions)} transcripts, {len(calls)} calls")


if __name__ == "__main__":
    main()
