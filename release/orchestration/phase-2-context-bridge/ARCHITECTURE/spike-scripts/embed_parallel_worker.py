#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001). One worker of a P-process parallel embed: embeds chunk shard K of P (batch 1)."""
import hashlib, json, sys, time
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
from embed_spike import Embedder, chunks_at
model_dir, ref, n, threads, k, p = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
texts = [c[2] for c in chunks_at(ref, n)][k::p]
emb = Embedder(model_dir, threads); t = time.time()
v = np.concatenate([emb.embed([x], batch=1) for x in texts])
print(json.dumps({"shard": k, "of": p, "threads": threads, "chunks": len(texts), "embed_s": round(time.time() - t, 2),
                  "sha256": hashlib.sha256(v.tobytes()).hexdigest()}))
