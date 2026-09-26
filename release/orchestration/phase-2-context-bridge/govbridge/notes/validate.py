#!/usr/bin/env python3
"""``govbridge notes validate <file>`` (REPAIR_PLAN.md section 2.10, ``config/notes-schema.yaml``). Refuses:

* a claim with no source;
* a source that does not resolve (its commit does not resolve, its path does not exist there, its recorded blob
  does not match the actual blob at path@commit, its lines fall outside the file, or its content_sha256 does not
  match the exact text of those lines);
* a note placed in section A -- class DERIVED_NOTE is never ladder-admissible in A (ARCHITECTURE.md section 5.1's
  DERIVED row), independent of the note's content;
* a built_from_sha256 mismatch.

Accepts a note rebuilt twice from the same sources with an identical hash, and requires ``unresolved[]`` present
(may be empty). Only this module talks to Git (via ``govbridge.core.gitobj``); ``govbridge.notes.build`` and
``govbridge.notes.schema`` are pure.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.core import gitobj
from govbridge.core.yamlutil import load_yaml_file, sha256_text
from govbridge.notes import build as buildmod
from govbridge.notes import schema as schemamod

#: sections a DERIVED_NOTE may never be placed in. Only "A" is named by REPAIR_PLAN.md section 2.10 ("is placed in
#: A"); kept as a tuple (not a single constant) so a future, equally non-ladder-admissible section can be added
#: here without changing the validator's call sites.
NEVER_ADMISSIBLE_SECTIONS = ("A",)


def _load_note_file(path: str) -> dict:
    if path.endswith((".yaml", ".yml")):
        return load_yaml_file(path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_source(source: dict, repo: Optional[str] = None) -> Optional[str]:
    """None if ``source`` resolves; otherwise a problem string. Re-derives everything from Git -- the recorded
    ``blob`` and ``content_sha256`` are never trusted, only checked."""
    if not isinstance(source, dict):
        return f"source is not a mapping: {source!r}"

    for key in ("path", "commit", "blob", "lines", "content_sha256"):
        if not source.get(key) and source.get(key) != 0:
            return f"source missing required field {key!r}: {source!r}"

    commit = source["commit"]
    path = source["path"]
    blob = source["blob"]
    lines = source["lines"]
    content_sha256 = source["content_sha256"]

    resolved_commit = gitobj.resolve_commit(commit, repo=repo)
    if resolved_commit is None:
        return f"source commit does not resolve: {commit!r}"

    actual_blob = gitobj.blob_at(resolved_commit, path, repo=repo)
    if actual_blob is None:
        return f"source path does not exist at commit: {path!r}@{commit!r}"

    if actual_blob != blob:
        return (f"source blob mismatch at {path!r}@{commit!r}: recorded {blob!r}, "
                f"actual {actual_blob!r} -- does not resolve")

    data = gitobj.read_blob(blob, repo=repo)
    if data is None:
        return f"source blob does not exist: {blob!r}"

    text = data.decode("utf-8", "replace")
    file_lines = text.splitlines()
    try:
        l1, l2 = int(lines[0]), int(lines[1])
    except (TypeError, ValueError, IndexError):
        return f"source lines is not a [line_start, line_end] pair: {lines!r}"
    if not (1 <= l1 <= l2 <= len(file_lines)):
        return f"source lines out of range: {lines!r} ({len(file_lines)} lines in {path!r}@{commit!r})"

    selected = "\n".join(file_lines[l1 - 1:l2])
    actual_sha256 = sha256_text(selected)
    if actual_sha256 != content_sha256:
        return (f"source content_sha256 mismatch at {path!r}:{l1}-{l2}@{commit!r}: "
                f"recorded {content_sha256!r}, actual {actual_sha256!r} -- does not resolve")

    return None


def validate_note(note: dict, repo: Optional[str] = None, target_section: Optional[str] = None,
                   schema: Optional[dict] = None) -> dict:
    """Validates ``note`` against ``config/notes-schema.yaml`` (structure), Git (source resolution and hash
    lineage) and placement admissibility. Returns ``{"status": "PASS"|"FAIL", "problems": [...]}``.

    ``target_section``, when given, is the section the caller is about to place this note in (as the packet
    compiler would); passing ``"A"`` is always refused, regardless of the note's own content, because class
    DERIVED_NOTE is never ladder-admissible in A. Passing ``None`` (the default, matching a bare `notes validate`
    with no placement decided yet) skips that one check -- every other refusal still applies."""
    schema = schema or schemamod.load_schema()
    problems: list = list(schemamod.structural_problems(note, schema=schema))

    # class check is partly structural (schema._check_fields already flags a wrong const), but the placement
    # invariant applies regardless of what the note claims its own class to be -- "is placed in A" is refused by
    # TYPE OF NOTE (a hierarchical evidence note), not merely by its self-reported class field.
    if target_section is not None and target_section.strip().upper() in NEVER_ADMISSIBLE_SECTIONS:
        problems.append(
            f"note placed in section {target_section!r}: class {schemamod.NOTE_CLASS} is never ladder-admissible "
            f"in section A (ARCHITECTURE.md section 5.1's DERIVED row); refused independent of note content"
        )

    claims = note.get("claims") if isinstance(note, dict) else None
    if isinstance(claims, list):
        for i, claim in enumerate(claims):
            if not isinstance(claim, dict):
                continue
            sources = claim.get("sources") or []
            if not sources:
                problems.append(f"note.claims[{i}] (claim_id={claim.get('claim_id')!r}) has no source; refused")
                continue
            for j, source in enumerate(sources):
                problem = resolve_source(source, repo=repo)
                if problem is not None:
                    problems.append(f"note.claims[{i}].sources[{j}]: {problem}")

    if isinstance(claims, list) and "built_from_sha256" in (note or {}):
        expected = buildmod.compute_built_from_sha256(claims)
        actual = note.get("built_from_sha256")
        if expected != actual:
            problems.append(
                f"built_from_sha256 mismatch: recorded {actual!r}, recomputed {expected!r} over current sources"
            )

    return {"status": "PASS" if not problems else "FAIL", "problems": problems}


def main(argv: Optional[list] = None) -> int:
    p = argparse.ArgumentParser(prog="govbridge notes validate")
    p.add_argument("file", help="a note file (.yaml/.yml or .json)")
    p.add_argument("--target-section", help="the section a caller is about to place the note in; "
                                             "'A' is always refused")
    p.add_argument("--repo", help="repository root (default: the repo containing the current working directory)")
    p.add_argument("--schema", help="path to notes-schema.yaml (default: config/notes-schema.yaml)")
    args = p.parse_args(argv)

    note = _load_note_file(args.file)
    schema = schemamod.load_schema(args.schema) if args.schema else None
    result = validate_note(note, repo=args.repo, target_section=args.target_section, schema=schema)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
