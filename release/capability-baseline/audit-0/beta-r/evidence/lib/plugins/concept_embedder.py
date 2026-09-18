#!/usr/bin/env python3
"""P2-AR-0009 independent `embed` plugin (gov-capability/1): a tiny concept-level embedder.

Words are mapped to concept ids through a synonym lexicon before hashing, so token-overlap-free paraphrases that share
concepts land near each other. Deterministic, dependency-free. Authored by the auditor; not a product component.
"""
import hashlib, json, math, re, sys

LEX = {
    "money": "C_MONEY", "cash": "C_MONEY", "currency": "C_MONEY", "cents": "C_MONEY", "cent": "C_MONEY", "dollars": "C_MONEY",
    "dollar": "C_MONEY", "funds": "C_MONEY", "monetary": "C_MONEY", "amounts": "C_MONEY", "amount": "C_MONEY",
    "float": "C_PREC", "floating": "C_PREC", "decimal": "C_PREC", "rounding": "C_PREC", "drift": "C_PREC", "precision": "C_PREC",
    "inexact": "C_PREC", "imprecise": "C_PREC", "exact": "C_PREC", "integer": "C_PREC",
    "reconcile": "C_RECON", "reconciliation": "C_RECON", "reconciles": "C_RECON", "settle": "C_RECON", "settlement": "C_RECON",
    "match": "C_RECON", "balancing": "C_RECON", "balance": "C_RECON",
    "store": "C_STORE", "stored": "C_STORE", "represent": "C_STORE", "represented": "C_STORE", "persist": "C_STORE", "keep": "C_STORE",
    "cache": "C_CACHE", "caching": "C_CACHE", "cached": "C_CACHE", "memoize": "C_CACHE",
    "latency": "C_SPEED", "slow": "C_SPEED", "fast": "C_SPEED", "speed": "C_SPEED", "p95": "C_SPEED", "quicker": "C_SPEED",
    "export": "C_EXPORT", "exports": "C_EXPORT", "feed": "C_EXPORT", "dump": "C_EXPORT", "extract": "C_EXPORT",
    "why": "C_WHY", "rationale": "C_WHY", "reason": "C_WHY", "because": "C_WHY",
}
TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_]+|\d+")


def embed(text, dim):
    v = [0.0] * dim
    for t in TOK.findall(text.lower()):
        c = LEX.get(t, "W_" + t)
        w = 3.0 if c.startswith("C_") else 0.3
        h = int(hashlib.sha256(c.encode()).hexdigest(), 16)
        v[h % dim] += w if (h >> 8) & 1 else -w
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


req = json.loads(sys.stdin.read() or "{}")
if req.get("protocol") != "gov-capability/1":
    print(json.dumps({"protocol": "gov-capability/1", "ok": False, "provider": {"id": "concept-embedder", "version": "1"},
                      "error": {"code": "PROTOCOL_MISMATCH", "message": "expected gov-capability/1"}}))
    sys.exit(0)
dim = int(req["inputs"].get("dimensions") or 256)
vecs = [embed(t, dim) for t in req["inputs"].get("texts", [])]
print(json.dumps({"protocol": "gov-capability/1", "ok": True, "provider": {"id": "concept-embedder", "version": "1"},
                  "request_id": req.get("request_id"), "outputs": {"vectors": vecs, "dim": dim}}))
