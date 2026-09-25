#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001). Is a chunk's vector a function of its text alone, independent of batch composition
(needed so that an incremental build reproduces a full build bit-for-bit)? And what does each batching mode cost?

usage: embed_batching_spike.py MODEL_DIR REF N_CHUNKS THREADS
"""
import hashlib, json, sys, time
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from embed_spike import Embedder, chunks_at


def run(emb, texts, batch, sort):
    order = sorted(range(len(texts)), key=lambda i: len(texts[i])) if sort else list(range(len(texts)))
    t = time.time(); out = np.zeros((len(texts), 384), np.float32)
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        out[idx] = emb.embed([texts[i] for i in idx], batch=batch)
    return out, time.time() - t


def main():
    model_dir, ref, n, threads = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    texts = [c[2] for c in chunks_at(ref, n)]
    emb = Embedder(model_dir, threads)
    res = {}
    for name, batch, sort in [("batch32_unsorted", 32, False), ("batch32_length_sorted", 32, True), ("batch1", 1, False)]:
        v, dt = run(emb, texts, batch, sort)
        res[name] = (v, dt)
        print(json.dumps({"mode": name, "chunks": len(texts), "threads": threads, "embed_s": round(dt, 2),
                          "chunks_per_s": round(len(texts) / dt, 1), "sha256": hashlib.sha256(v.tobytes()).hexdigest()}))
    base = res["batch1"][0]
    for name in ("batch32_unsorted", "batch32_length_sorted"):
        v = res[name][0]
        print(json.dumps({"compare": f"{name} vs batch1", "bitwise_equal": bool((v == base).all()),
                          "max_abs_diff": float(abs(v - base).max()),
                          "min_cosine": float(np.min(np.sum(v * base, axis=1))),
                          "equal_after_round6": bool((np.round(v, 6) == np.round(base, 6)).all()),
                          "equal_after_round4": bool((np.round(v, 4) == np.round(base, 4)).all())}))


if __name__ == "__main__":
    main()
