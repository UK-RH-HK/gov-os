"""Read ``config/model-pin.yaml`` (B1's file; never edited here) and compute/verify the pin id
(SEMANTIC_ROUTE.md section 2, ``config/model-pin.yaml`` ``pin_id_formula``). Shared by the ONNX adapter (which
fails closed on a mismatch, PIN_MISMATCH) and by the semantic layer's manifest block (which records the pin id
every reader can recompute the same way).

Nothing here is specific to ``bge-small-en-v1.5``: every field read out of ``model-pin.yaml`` is used generically,
so pointing this file at a different model/revision under the same schema (SEMANTIC_ROUTE.md section 5,
"Replacement") needs no code change here.
"""
from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from typing import Optional

from govbridge.core.yamlutil import canonical_json, load_yaml_file, sha256_file, sha256_text


class ModelUnavailable(RuntimeError):
    """A declared artefact is missing or unreadable at the resolved model directory."""


class PinMismatch(RuntimeError):
    """A resolved artefact's sha256 does not match config/model-pin.yaml, or a caller-asserted pin id disagrees
    with the one this environment computes."""


@dataclasses.dataclass(frozen=True)
class Artefact:
    path: str
    sha256: str
    local_name: str


@dataclasses.dataclass(frozen=True)
class ModelPin:
    model_id: str
    revision: str
    licence: str
    artefacts: tuple  # tuple[Artefact, ...]
    dimensions: int
    pooling: str
    normalize: str
    max_tokens: int
    query_prefix: str
    runtime: dict
    raw: dict


def load_model_pin(path: str) -> ModelPin:
    doc = load_yaml_file(path)
    m = doc["model"]
    # Resolved by `path` verbatim (subdirectories preserved, e.g. "onnx/model.onnx"), never by the YAML's
    # `local_name` field: config/model-pin.yaml declares `local_name: pooling_config.json` for the
    # `1_Pooling/config.json` artefact (presumably to avoid colliding with the top-level config.json), but the
    # real, already-downloaded shared cache (B1's bootstrap) preserves the original nested path instead --
    # verified on disk (`1_Pooling/config.json`, not `pooling_config.json`). Matching observed reality rather
    # than the aspirational field avoids a spurious MODEL_UNAVAILABLE; flagged as an open issue for B1/
    # bootstrap.sh reconciliation. `local_name` is still parsed and kept on the dataclass for visibility.
    artefacts = tuple(
        Artefact(path=a["path"], sha256=a["sha256"], local_name=a.get("local_name") or a["path"])
        for a in m["artefacts"]
    )
    return ModelPin(
        model_id=m["id"], revision=m["revision"], licence=m.get("licence", ""), artefacts=artefacts,
        dimensions=int(m["dimensions"]), pooling=m["pooling"], normalize=m["normalize"],
        max_tokens=int(m["max_tokens"]), query_prefix=m["query_prefix"], runtime=dict(doc["runtime"]), raw=doc,
    )


def model_slug(model_id: str) -> str:
    return model_id.replace("/", "-")


def model_dir(pin: ModelPin, models_root: Path) -> Path:
    return models_root / model_slug(pin.model_id) / pin.revision


def compute_pin_id(pin: ModelPin) -> str:
    """sha256(model.id || model.revision || sorted(artefact sha256s) || runtime.onnxruntime ||
    runtime.tokenizers || runtime.session || model.pooling || model.query_prefix), as
    ``config/model-pin.yaml``'s ``pin_id_formula`` defines it, serialised deterministically (canonical JSON) so
    every reader that loads the same pin file computes byte-identical ids."""
    payload = {
        "model_id": pin.model_id,
        "revision": pin.revision,
        "artefact_sha256_sorted": sorted(a.sha256 for a in pin.artefacts),
        "runtime_onnxruntime": pin.runtime.get("onnxruntime"),
        "runtime_tokenizers": pin.runtime.get("tokenizers"),
        "runtime_session": pin.runtime.get("session"),
        "pooling": pin.pooling,
        "query_prefix": pin.query_prefix,
    }
    return sha256_text(canonical_json(payload))


def resolve_and_verify(pin: ModelPin, models_root: Path,
                        override_dir: Optional[str] = None) -> Path:
    """Resolve the on-disk directory for ``pin`` and verify every declared artefact's sha256. Raises
    ``ModelUnavailable`` if the directory or a file is missing/unreadable, ``PinMismatch`` if a present file's
    bytes do not hash to the declared sha256 (tamper/drift -- never silently served).

    ``override_dir`` lets a caller (the adapter's own ``--model-dir``, or a test) point at a directory other than
    the shared, read-only cache, without ever touching that shared cache."""
    d = Path(override_dir) if override_dir else model_dir(pin, models_root)
    if not d.is_dir():
        raise ModelUnavailable(f"model directory not found: {d}")
    for a in pin.artefacts:
        p = d / a.path
        if not p.is_file():
            raise ModelUnavailable(f"missing model artefact: {p}")
        got = sha256_file(str(p))
        if got != a.sha256:
            raise PinMismatch(f"{p} hashes to {got}, config/model-pin.yaml declares {a.sha256}")
    return d


def default_models_root(gov_bridge_home: Optional[Path] = None) -> Path:
    from govbridge.core.store import gov_bridge_home as home_fn
    return (gov_bridge_home or home_fn()) / "models"


def default_pin_path(gov_bridge_domain: Optional[str] = None) -> str:
    domain = gov_bridge_domain or os.environ.get("GOV_BRIDGE_DOMAIN")
    if not domain:
        from govbridge import GOV_BRIDGE_DOMAIN
        domain = GOV_BRIDGE_DOMAIN
    return str(Path(domain) / "config" / "model-pin.yaml")
