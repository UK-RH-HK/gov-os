"""probe_batch.py <root> [n_batches]: read-only on the store; send the first missing chunk batches, as _build forms
them, to the shared runner once each, and print the HTTP status, the time and any error body (never a vector)."""
import json
import math
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from gov.retrieval import ollama, semantic
from gov.store import STORE_REL

root = Path(sys.argv[1])
batches = int(sys.argv[2]) if len(sys.argv) > 2 else 1
connection = sqlite3.connect((root / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
wanted = semantic._wanted(root, connection)
have = {c for (c,) in connection.execute("SELECT chunk_id FROM semantic_vector")}
missing = [c for c in wanted if c not in have]
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
host = "http://" + ollama.DEFAULT_HOST if "://" not in ollama.DEFAULT_HOST else ollama.DEFAULT_HOST
for b in range(batches):
    batch = missing[b * semantic.BATCH:(b + 1) * semantic.BATCH]
    texts = [connection.execute(semantic._TEXT, (c,)).fetchone()[0][:semantic.EMBED_CHARS] for c in batch]
    body = json.dumps({"model": semantic.MODEL, "input": texts}).encode()
    request = urllib.request.Request(host.rstrip("/") + "/api/embed", data=body,
                                     headers={"Content-Type": "application/json"})
    start = time.monotonic()
    try:
        with opener.open(request, timeout=300) as reply:
            answer = json.load(reply)
        vectors = answer.get("embeddings") or []
        bad = sum(1 for v in vectors if any(not math.isfinite(x) for x in v))
        print(f"batch {b}: HTTP 200 in {time.monotonic() - start:.1f} s, {len(vectors)}/{len(texts)} vectors, "
              f"{bad} with a non-finite value")
    except urllib.error.HTTPError as exc:
        print(f"batch {b}: HTTP {exc.code} in {time.monotonic() - start:.1f} s: {exc.read()[:400]!r}")
        for i, text in enumerate(texts):
            print(f"  text {i}: {len(text)} chars, {len(text.encode())} bytes, path chunk {batch[i]}")
    except Exception as exc:  # noqa: BLE001 - a diagnostic: print whatever ended it
        print(f"batch {b}: {type(exc).__name__} in {time.monotonic() - start:.1f} s: {exc}")
