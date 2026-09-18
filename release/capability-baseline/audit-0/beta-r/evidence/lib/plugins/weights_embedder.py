#!/usr/bin/env python3
"""P2-AR-0009 `embed` plugin whose behaviour depends on an external weights file (./weights.json next to this script),
standing in for a model-weights artefact or inference runtime that is separate from the adapter script."""
import hashlib, json, math, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(here, "weights.json")))
req = json.loads(sys.stdin.read() or "{}")
dim = int(req.get("inputs", {}).get("dimensions") or 64)
out = []
for t in req.get("inputs", {}).get("texts", []):
    v = [0.0] * dim
    for tok in re.findall(r"[a-z0-9]+", t.lower()):
        h = int(hashlib.sha256((W["salt"] + tok).encode()).hexdigest(), 16)
        v[h % dim] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    out.append([x / n for x in v])
print(json.dumps({"protocol": "gov-capability/1", "ok": True, "provider": {"id": "weights-embedder", "version": "1"}, "outputs": {"vectors": out}}))
