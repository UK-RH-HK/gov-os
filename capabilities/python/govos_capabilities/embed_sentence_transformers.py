"""Optional gov-capability/1 embed plugin backed by a local sentence-embedding model (D-0006, candidate class 1).

Not a kernel dependency. Fails closed: when `sentence-transformers` or the configured model is unavailable the plugin
answers ok=false with a typed error and the core reports EMBEDDER_UNAVAILABLE-class failures — it never silently
degrades. Model id and dimensions are pinned by the descriptor / MEMORY_POLICY; changing them is a measured migration.

Descriptor example (register with `gov plugins register --descriptor <file>`):
  plugin_id: st-embed
  capability: embed
  version: "1"
  command: [python3, -m, govos_capabilities.embed_sentence_transformers, --model, sentence-transformers/all-MiniLM-L6-v2]
  cwd: capabilities/python
  health_check: {kind: protocol_ping}
  purpose: paraphrase-capable local embeddings (benchmark before pinning)
"""
import argparse
import json
import sys


def respond(ok, outputs=None, error=None, provider_version="1"):
    r = {"protocol": "gov-capability/1", "ok": ok, "provider": {"id": "st-embed", "version": provider_version}}
    if ok:
        r["outputs"] = outputs
    else:
        r["error"] = error
    sys.stdout.write(json.dumps(r))
    sys.stdout.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    args = ap.parse_args()
    req = json.loads(sys.stdin.read() or "{}")
    if req.get("protocol") != "gov-capability/1":
        respond(False, error={"code": "PROTOCOL_MISMATCH", "message": "expected gov-capability/1"})
        return
    texts = (req.get("inputs") or {}).get("texts") or []
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as exc:  # library absent: fail closed, never a fake vector
        respond(False, error={"code": "MODEL_UNAVAILABLE", "message": f"sentence-transformers not installed: {exc}"})
        return
    try:
        model = SentenceTransformer(args.model)
        vecs = model.encode(texts, normalize_embeddings=True).tolist() if texts else []
        dim = int(model.get_sentence_embedding_dimension())
    except Exception as exc:
        respond(False, error={"code": "MODEL_UNAVAILABLE", "message": f"model {args.model} unavailable: {exc}"})
        return
    want = (req.get("inputs") or {}).get("dimensions")
    if want and int(want) != dim:
        respond(False, error={"code": "DIMENSION_MISMATCH", "message": f"model produces {dim}-d vectors; pinned {want}"})
        return
    respond(True, outputs={"vectors": [[round(float(x), 6) for x in v] for v in vecs], "dim": dim}, provider_version=args.model)


if __name__ == "__main__":
    main()
