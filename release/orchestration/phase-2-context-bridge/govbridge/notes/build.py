#!/usr/bin/env python3
"""Constructs a hierarchical evidence note (REPAIR_PLAN.md section 2.10) and computes/recomputes its
``built_from_sha256``, so a note can be rebuilt from the same sources and the rebuild checked byte for byte
(OD-BR-06 section 4: "be rebuildable from original evidence"). This module never touches Git and never decides
whether a source resolves -- ``govbridge.notes.validate`` does that; ``build`` only shapes claims into a note and
hashes them deterministically.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.core.yamlutil import load_yaml_file, sha256_text
from govbridge.notes.schema import NOTE_CLASS


def compute_built_from_sha256(claims: list) -> str:
    """sha256 over the SORTED ``content_sha256`` of every source across every claim, newline-joined
    (REPAIR_PLAN.md section 2.10: "built_from_sha256, over the sorted source hashes, so the note can be
    rebuilt"). Sorting makes the hash independent of claim order and of source order within a claim, so two
    builds from the same underlying evidence -- gathered in a different order, or re-serialised -- yield an
    identical hash (the rebuild-determinism acceptance case)."""
    hashes = []
    for claim in claims:
        for source in claim.get("sources", []) or []:
            content_sha256 = source.get("content_sha256")
            if content_sha256 is not None:
                hashes.append(content_sha256)
    return sha256_text("\n".join(sorted(hashes)))


def build_note(note_id: str, claims: list, unresolved: Optional[list] = None) -> dict:
    """Builds a DERIVED_NOTE dict from ``claims`` (a list of {claim_id, text, sources[]}). ``unresolved`` is
    mandatory in the resulting note (defaults to ``[]``, never omitted -- OD-BR-06 section 4: "disclose unresolved
    evidence"). Does not validate the result; call ``govbridge.notes.validate.validate_note`` on it before use."""
    return {
        "note_id": note_id,
        "class": NOTE_CLASS,
        "claims": claims,
        "unresolved": list(unresolved) if unresolved is not None else [],
        "built_from_sha256": compute_built_from_sha256(claims),
    }


def rebuild(note: dict) -> dict:
    """Rebuilds ``note`` from its own recorded ``claims`` and ``unresolved``, recomputing ``built_from_sha256``
    fresh. Used by the validator to detect a hash mismatch (the recorded hash no longer matches what the current
    claims/sources hash to) and by tests to prove that rebuilding twice from the same sources is deterministic."""
    return build_note(note.get("note_id"), note.get("claims", []) or [], note.get("unresolved"))


def _load_spec(path: str) -> dict:
    if path.endswith((".yaml", ".yml")):
        return load_yaml_file(path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: Optional[list] = None) -> int:
    """``govbridge notes build <spec>``: reads a {note_id, claims[], unresolved?} spec (.yaml/.yml or .json) with
    claims already carrying their sources, and prints the built note (with ``built_from_sha256`` computed) as
    JSON. Does not validate the result -- pipe it to ``govbridge notes validate`` for that."""
    p = argparse.ArgumentParser(prog="govbridge notes build")
    p.add_argument("spec", help="a {note_id, claims[], unresolved?} spec file (.yaml/.yml or .json)")
    args = p.parse_args(argv)

    spec = _load_spec(args.spec)
    note = build_note(spec.get("note_id"), spec.get("claims", []) or [], spec.get("unresolved"))
    print(json.dumps(note, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
