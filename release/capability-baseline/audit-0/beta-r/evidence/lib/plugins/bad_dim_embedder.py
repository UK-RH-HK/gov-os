#!/usr/bin/env python3
"""P2-AR-0009 malformed `embed` plugin: always returns 3-dimensional vectors (fail-closed probe)."""
import json, sys
req = json.loads(sys.stdin.read() or "{}")
texts = req.get("inputs", {}).get("texts", [])
print(json.dumps({"protocol": "gov-capability/1", "ok": True, "provider": {"id": "bad-dim", "version": "1"},
                  "outputs": {"vectors": [[0.1, 0.2, 0.3] for _ in texts]}}))
