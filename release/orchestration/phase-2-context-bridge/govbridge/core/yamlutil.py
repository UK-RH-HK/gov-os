"""A duplicate-key-refusing YAML loader and a canonical hash, the same technique
release/orchestration/phase-2-context-bridge/tools/check_state.py uses for the orchestrator's own state file. Built
independently here (BUILD, not REUSE) so that govbridge/core has no import dependency on the orchestrator's tooling
script, which is not part of this package and is not meant to be imported as a library. Config files and state files
alike must fail loudly on a duplicate key rather than silently taking the last one.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: yaml.SafeLoader, node: yaml.Node, deep: bool = False) -> dict:
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key {key!r}", key_node.start_mark
            )
        seen.add(key)
    return loader.construct_mapping(node, deep)


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_yaml_text(text: str) -> Any:
    """Parse YAML text, refusing duplicate mapping keys."""
    return yaml.load(text, Loader=UniqueKeyLoader)


def load_yaml_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return load_yaml_text(fh.read())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, compact separators, no NaN/Infinity."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_hash(obj: Any) -> str:
    """sha256 of an object's canonical JSON form -- used for manifest hashes and config shas."""
    return sha256_text(canonical_json(obj))
