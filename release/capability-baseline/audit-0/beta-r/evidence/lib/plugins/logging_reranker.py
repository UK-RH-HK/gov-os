#!/usr/bin/env python3
"""P2-AR-0009 independent `rerank` plugin: scores by query-term overlap and LOGS every candidate it receives
(id + first 80 chars) to ./.probe-rerank-log.jsonl in the plugin cwd (the governed project root), so the auditor can
see exactly which content crossed the plugin boundary."""
import json, re, sys
req = json.loads(sys.stdin.read() or "{}")
inp = req.get("inputs", {})
qt = set(re.findall(r"[a-z0-9]+", inp.get("query", "").lower()))
scores = []
with open(".probe-rerank-log.jsonl", "a") as f:
    for c in inp.get("candidates", []):
        f.write(json.dumps({"id": c.get("id"), "text": c.get("text", "")[:80]}) + "\n")
        ct = set(re.findall(r"[a-z0-9]+", c.get("text", "").lower()))
        scores.append({"id": c.get("id"), "score": float(len(qt & ct))})
print(json.dumps({"protocol": "gov-capability/1", "ok": True, "provider": {"id": "logging-reranker", "version": "1"},
                  "request_id": req.get("request_id"), "outputs": {"scores": scores}}))
