"""gov-capability/1 ``embed`` adapter, ONNX Runtime backend (node B4; SEMANTIC_ROUTE.md, ARCHITECTURE.md section 9).

PROVENANCE (mutation_scope discipline: this is an ADAPT of a COPY, never an edit of the original):
  adapted_from: capabilities/python/govos_capabilities/embed_sentence_transformers.py
  at_commit:    6e7a2a3
  blob_sha1:    7b1411bf97b22aacb318ef907436c0d7c93592c8   (git hash-object; unchanged at HEAD, verified BR-AR-0006)
  what changed: the sentence-transformers/PyTorch backend is replaced by ONNX Runtime CPU against the pinned,
    provisional ``BAAI/bge-small-en-v1.5`` model (``config/model-pin.yaml``, B1); the protocol-level ``ok``/``error``
    envelope and the ``--model``-style CLI-argument convention are kept. Added beyond the original: an explicit
    CAPABILITY_MISMATCH check (the original checked protocol only), a PIN_MISMATCH check (sha256-verifies every
    declared artefact against config/model-pin.yaml before any inference, and rejects a caller-asserted pin id that
    disagrees), a ``mode: query|passage`` input (PROTOCOL.md's embed shape; the query prefix is applied here, never
    by a caller), and full-precision vector output (no 6-decimal rounding -- SEMANTIC_ROUTE.md claims bitwise
    determinism across processes/threads/batch compositions, and JSON's shortest-round-trip float formatting
    preserves a float32 value exactly through float64 widening/narrowing, so rounding would only ever lose bits).

This is invoked directly as a subprocess (the bridge does not call ``gov plugins register`` -- ARCHITECTURE.md
section 9); it never imports anything from ``govbridge.core`` beyond the pin/config readers in
``govbridge.semantic.modelpin``, so it stays a standalone, replaceable executable exactly as PROTOCOL.md and
SEMANTIC_ROUTE.md section 9's "Replacement" procedure require. Nothing below names a review, a phase or a
particular file (OC-BR-02): every parameter comes from ``config/model-pin.yaml`` or the request.

Request:  {"protocol": "gov-capability/1", "capability": "embed",
           "inputs": {"texts": [str, ...], "dimensions": int?, "mode": "query"|"passage"?}}
Response: {"protocol", "ok", "provider": {"id", "version"}, "request_id",
           "outputs": {"vectors": [[float,...],...], "dim", "model", "runtime", "pin_id"}}
       or {"protocol", "ok": false, "provider", "request_id", "error": {"code", "message"}}

Typed, fail-closed error codes: BAD_REQUEST, PROTOCOL_MISMATCH, CAPABILITY_MISMATCH, MODEL_UNAVAILABLE,
DIMENSION_MISMATCH, PIN_MISMATCH. Never a fake or degraded vector (D-0005).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

PROTOCOL = "gov-capability/1"
CAPABILITY = "embed"
PROVIDER_ID = "onnx-bge-embed"

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # release/orchestration/phase-2-context-bridge

from govbridge.semantic import modelpin  # noqa: E402


def _respond(ok: bool, provider_version: str, outputs: Optional[dict] = None, error: Optional[dict] = None,
             request_id=None) -> None:
    resp = {"protocol": PROTOCOL, "ok": ok, "provider": {"id": PROVIDER_ID, "version": provider_version},
            "request_id": request_id}
    if ok:
        resp["outputs"] = outputs or {}
    else:
        resp["error"] = error
    sys.stdout.write(json.dumps(resp))
    sys.stdout.flush()


class Embedder:
    """CLS-pooled, L2-normalised ONNX Runtime encoder (SEMANTIC_ROUTE.md section 2: pooling ``cls``, ``l2``,
    ``max_tokens 512``). Session options match the pin exactly (``inter_op_num_threads 1``, ``ORT_SEQUENTIAL``,
    ``use_deterministic_compute True``); ``intra_op_num_threads`` is deliberately NOT part of the pin id (measured
    bitwise-identical at 4 and 16, SO-09) and defaults to 4 here to share this machine's CPU politely with other
    parallel builders (SO-11's concurrent-load configuration)."""

    def __init__(self, model_dir: Path, pin: "modelpin.ModelPin", threads: int = 4):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = int(pin.runtime.get("session", {}).get("inter_op_num_threads", 1))
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.use_deterministic_compute = True
        self.sess = ort.InferenceSession(
            str(model_dir / "onnx" / "model.onnx"), so, providers=["CPUExecutionProvider"]
        )
        self.tok = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self.tok.enable_truncation(max_length=pin.max_tokens)
        self.input_names = {i.name for i in self.sess.get_inputs()}
        self.pin = pin

    def embed(self, texts: list, batch_size: int = 1):
        import numpy as np

        if not texts:
            return np.zeros((0, self.pin.dimensions), dtype=np.float32)
        self.tok.enable_padding(pad_id=0, pad_token="[PAD]")
        out = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i:i + batch_size]
            enc = self.tok.encode_batch(chunk)
            feed = {
                "input_ids": np.array([e.ids for e in enc], dtype=np.int64),
                "attention_mask": np.array([e.attention_mask for e in enc], dtype=np.int64),
            }
            if "token_type_ids" in self.input_names:
                feed["token_type_ids"] = np.array([e.type_ids for e in enc], dtype=np.int64)
            last_hidden = self.sess.run(None, feed)[0]
            cls = last_hidden[:, 0, :]  # CLS pooling, 1_Pooling/config.json pooling_mode_cls_token: true
            cls = cls / np.linalg.norm(cls, axis=1, keepdims=True)
            out.append(cls.astype(np.float32))
        return np.concatenate(out)


def handle(inputs: dict, pin_path: str, model_dir_override: Optional[str], threads: int,
           batch_size: int) -> tuple:
    """Returns (ok, outputs_or_None, error_or_None, provider_version). Never raises -- every failure is translated
    to a typed error so the caller (subprocess boundary) always gets a well-formed response."""
    try:
        pin = modelpin.load_model_pin(pin_path)
    except (OSError, KeyError) as exc:
        return False, None, {"code": "MODEL_UNAVAILABLE", "message": f"model-pin.yaml unreadable: {exc}"}, "unknown"

    provider_version = f"{pin.model_id}@{pin.revision}"

    try:
        resolved_dir = modelpin.resolve_and_verify(
            pin, modelpin.default_models_root(), override_dir=model_dir_override
        )
    except modelpin.ModelUnavailable as exc:
        return False, None, {"code": "MODEL_UNAVAILABLE", "message": str(exc)}, provider_version
    except modelpin.PinMismatch as exc:
        return False, None, {"code": "PIN_MISMATCH", "message": str(exc)}, provider_version

    computed_pin_id = modelpin.compute_pin_id(pin)
    asserted_pin_id = inputs.get("pin_id")
    if asserted_pin_id and asserted_pin_id != computed_pin_id:
        return False, None, {
            "code": "PIN_MISMATCH",
            "message": f"caller expects pin_id {asserted_pin_id}, this environment computes {computed_pin_id}",
        }, provider_version

    texts = inputs.get("texts") or []
    mode = inputs.get("mode") or "passage"
    if mode not in ("query", "passage"):
        return False, None, {"code": "BAD_REQUEST", "message": f"mode must be 'query' or 'passage', got {mode!r}"}, \
            provider_version
    if mode == "query":
        texts = [pin.query_prefix + t for t in texts]

    try:
        embedder = Embedder(resolved_dir, pin, threads=threads)
        vecs = embedder.embed(texts, batch_size=batch_size)
    except Exception as exc:  # noqa: BLE001 -- runtime/model load failure, never a crash across the plugin boundary
        return False, None, {"code": "MODEL_UNAVAILABLE", "message": f"inference failed: {exc}"}, provider_version

    dim = int(vecs.shape[1]) if len(vecs.shape) == 2 else pin.dimensions
    want = inputs.get("dimensions")
    if want and int(want) != dim:
        return False, None, {
            "code": "DIMENSION_MISMATCH", "message": f"model produces {dim}-d vectors; caller pinned {want}",
        }, provider_version

    outputs = {
        "vectors": [[float(x) for x in v] for v in vecs],
        "dim": dim,
        "model": {
            "id": pin.model_id, "revision": pin.revision,
            "artefacts": {a.local_name: a.sha256 for a in pin.artefacts},
        },
        "runtime": pin.runtime,
        "encoding": {"pooling": pin.pooling, "normalize": pin.normalize, "max_tokens": pin.max_tokens,
                     "query_prefix": pin.query_prefix},
        "pin_id": computed_pin_id,
    }
    return True, outputs, None, provider_version


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pin", default=None, help="path to model-pin.yaml (default: config/model-pin.yaml)")
    ap.add_argument("--model-dir", default=None, help="override the resolved model directory (tests only; never "
                                                        "the shared cache another builder may be using)")
    ap.add_argument("--threads", type=int, default=4, help="intra_op_num_threads (not part of the pin id)")
    ap.add_argument("--batch-size", type=int, default=1, help="onnxruntime batch size (measured fastest: 1)")
    args = ap.parse_args(argv)

    raw = sys.stdin.read()
    try:
        req = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        _respond(False, "unknown", error={"code": "BAD_REQUEST", "message": f"invalid JSON: {exc}"})
        return 0

    if req.get("protocol") != PROTOCOL:
        _respond(False, "unknown", error={"code": "PROTOCOL_MISMATCH", "message": f"expected {PROTOCOL}"})
        return 0
    if req.get("capability") != CAPABILITY:
        _respond(False, "unknown",
                  error={"code": "CAPABILITY_MISMATCH", "message": f"this plugin provides {CAPABILITY}"})
        return 0

    pin_path = args.pin or modelpin.default_pin_path()
    ok, outputs, error, provider_version = handle(
        req.get("inputs") or {}, pin_path, args.model_dir, args.threads, args.batch_size
    )
    _respond(ok, provider_version, outputs=outputs, error=error, request_id=req.get("request_id"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
