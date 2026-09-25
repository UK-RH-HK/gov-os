#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001) -- not bridge code. Feasibility of ONE provisional local embedding model behind the
gov-capability/1 `embed` request/response shape: throughput on real corpus chunks, run-to-run and thread-count
determinism, and a three-query smoke check (NOT a bake-off; no other model is evaluated).

usage: embed_spike.py MODEL_DIR REF N_CHUNKS THREADS OUT_NPY [--query]
"""
import hashlib, json, subprocess, sys, time
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

EMBED_EXT = (".md", ".yaml", ".yml", ".rs", ".py", ".toml", ".txt", ".sh")
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "   # model card, bge-*-en-v1.5


def chunks_at(ref, n):
    ls = subprocess.run(["git", "ls-tree", "-r", "-l", ref], capture_output=True, text=True, check=True).stdout
    out = []
    for line in sorted(ls.splitlines(), key=lambda l: l.split("\t", 1)[1]):
        meta, path = line.split("\t", 1)
        _, typ, oid, size = meta.split()
        if typ != "blob" or not path.endswith(EMBED_EXT) or int(size) > (1 << 20):
            continue
        text = subprocess.run(["git", "cat-file", "blob", oid], capture_output=True).stdout.decode("utf-8", "replace")
        for s in range(0, max(1, len(text)), 1080):
            out.append((path, s, text[s:s + 1200]))
            if len(out) >= n:
                return out
    return out


class Embedder:
    def __init__(self, model_dir, threads):
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.use_deterministic_compute = True
        self.sess = ort.InferenceSession(f"{model_dir}/onnx/model.onnx", so, providers=["CPUExecutionProvider"])
        self.tok = Tokenizer.from_file(f"{model_dir}/tokenizer.json")
        self.tok.enable_truncation(max_length=512)
        self.inputs = [i.name for i in self.sess.get_inputs()]

    def embed(self, texts, batch=32):
        vecs = []
        for i in range(0, len(texts), batch):
            b = texts[i:i + batch]
            self.tok.enable_padding(pad_id=0, pad_token="[PAD]")
            enc = self.tok.encode_batch(b)
            feed = {"input_ids": np.array([e.ids for e in enc], dtype=np.int64),
                    "attention_mask": np.array([e.attention_mask for e in enc], dtype=np.int64)}
            if "token_type_ids" in self.inputs:
                feed["token_type_ids"] = np.array([e.type_ids for e in enc], dtype=np.int64)
            last = self.sess.run(None, feed)[0]
            cls = last[:, 0, :]                                         # CLS pooling (1_Pooling/config.json)
            cls = cls / np.linalg.norm(cls, axis=1, keepdims=True)
            vecs.append(cls.astype(np.float32))
        return np.concatenate(vecs) if vecs else np.zeros((0, 384), np.float32)


def main():
    model_dir, ref, n, threads, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    t0 = time.time(); ch = chunks_at(ref, n); t1 = time.time()
    emb = Embedder(model_dir, threads); t2 = time.time()
    v = emb.embed([c[2] for c in ch]); t3 = time.time()
    np.save(out, v)
    print(json.dumps({"onnxruntime": ort.__version__, "threads": threads, "chunks": len(ch),
                      "chars": sum(len(c[2]) for c in ch), "dim": int(v.shape[1]),
                      "load_chunks_s": round(t1 - t0, 2), "load_model_s": round(t2 - t1, 2),
                      "embed_s": round(t3 - t2, 2), "chunks_per_s": round(len(ch) / (t3 - t2), 1),
                      "vectors_sha256_float32": hashlib.sha256(v.tobytes()).hexdigest(),
                      "vectors_sha256_rounded6": hashlib.sha256(np.round(v, 6).tobytes()).hexdigest()}))
    if "--query" in sys.argv:
        for q in ["why does the sandbox exemption exist and who consumes it",
                  "which rule wins when two path rules match the same file",
                  "how is a checkpoint made mandatory for a worker"]:
            qv = emb.embed([QUERY_PREFIX + q])[0]
            top = np.argsort(-(v @ qv))[:3]
            print(json.dumps({"query": q, "top3": [[ch[i][0], ch[i][1], round(float(v[i] @ qv), 4)] for i in top]}))


if __name__ == "__main__":
    main()
