#!/usr/bin/env python3
"""Structured current-state lookup (ARCHITECTURE.md section 4.1): ``govbridge state get <state-alias> <key.path>``.

Reads a YAML state file at its canonical occurrence with the duplicate-key-refusing loader
(``govbridge.core.yamlutil.UniqueKeyLoader``), and returns the value together with its provenance: (path, commit,
blob, key_path, line_start-line_end) from PyYAML node marks; seal status (SEAL_OK/SEAL_MISMATCH/UNSEALED), computed
with the SAME ``canonical_hash`` rule as ``tools/check_state.py`` (reimplemented independently here, the same way
``govbridge.core.yamlutil`` reimplements ``UniqueKeyLoader``, so this package has no import dependency on a script
that is not meant to be imported); and the last commit that changed those lines (``git blame -L``) and its date.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import re
import sys
from typing import Optional

import yaml

from govbridge.authority.resolver import STATE_ALIASES
from govbridge.core import gitobj, view as viewmod
from govbridge.core import taskctx as taskctxmod
from govbridge.core.yamlutil import UniqueKeyLoader

_STATE_HASH_LINE_RE = re.compile(r"(?m)^state_hash:.*$")


def canonical_hash(text: str) -> str:
    """The exact rule tools/check_state.py uses: sha256 of the file with state_hash blanked to null."""
    body = _STATE_HASH_LINE_RE.sub("state_hash: null", text)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclasses.dataclass
class StateLookupResult:
    alias: str
    key_path: str
    value: object
    path: str
    commit: str
    blob: str
    line_start: int
    line_end: int
    seal_status: str  # SEAL_OK | SEAL_MISMATCH | UNSEALED
    recorded_state_hash: Optional[str]
    computed_state_hash: str
    last_changed_commit: Optional[str]
    last_changed_date: Optional[str]
    # R1-RX (OBS-BR-08): the task's own retrieval_exclusions apply here too -- ``excluded`` withholds ``value``
    # (metadata/provenance stay), the same way govbridge.core.exact's corpus-rule EXCLUDE effect already does;
    # ``excluded_hits`` is always present (0 or 1) so the exclusion is disclosed even when it never fires.
    excluded: bool = False
    excluded_hits: int = 0

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _compose_and_find(text: str, key_path: str) -> tuple:
    """Parse ``text`` with the duplicate-key-refusing loader (correctness), and separately COMPOSE it (PyYAML node
    marks) to find the (line_start, line_end) span of ``key_path`` (a dotted path, optionally ending [N] on a list
    index). Returns (value, line_start, line_end), 1-indexed inclusive."""
    doc = yaml.load(text, Loader=UniqueKeyLoader)
    node = yaml.compose(text, Loader=UniqueKeyLoader)

    value = doc
    cur_node = node
    for part in key_path.split("."):
        list_index = None
        m = re.match(r"^(?P<name>[^\[\]]+)(?:\[(?P<idx>\d+)\])?$", part)
        name, idx = m.group("name"), m.group("idx")
        if isinstance(value, dict):
            value = value[name]
        else:
            raise KeyError(f"{key_path!r}: {name!r} is not inside a mapping")
        found_child = None
        for k_node, v_node in cur_node.value:
            if k_node.value == name:
                found_child = v_node
                break
        if found_child is None:
            raise KeyError(f"{key_path!r}: {name!r} not found while composing")
        cur_node = found_child
        if idx is not None:
            list_index = int(idx)
            value = value[list_index]
            cur_node = cur_node.value[list_index]

    start_line = cur_node.start_mark.line + 1
    end_line = cur_node.end_mark.line
    if cur_node.end_mark.column == 0 and end_line >= start_line:
        end_line -= 1
    end_line = max(end_line, start_line)
    return value, start_line, end_line


def get(alias: str, key_path: str, repo: Optional[str] = None, view_path: Optional[str] = None,
        task: Optional[taskctxmod.TaskContext] = None) -> StateLookupResult:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os

    if alias not in STATE_ALIASES:
        raise ValueError(f"unknown state alias {alias!r} (known: {sorted(STATE_ALIASES)})")
    path = STATE_ALIASES[alias]
    # R1-RX (OBS-BR-08): the task's own retrieval_exclusions apply to a state alias's canonical path too.
    task = task or taskctxmod.current()
    excluded = task.is_excluded(path)

    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    vc = viewmod.load_view(view_path)
    resolved_view = viewmod.resolve_view(vc, repo=repo)
    classification = resolved_view.classify_occurrence(path, resolved_view.ref_commit("records"))
    commit = classification.canonical_commit
    blob = classification.canonical_blob

    raw = gitobj.read_path(commit, path, repo=repo)
    if raw is None:
        raise FileNotFoundError(f"{commit}:{path} not found")
    text = raw.decode("utf-8")

    value, line_start, line_end = _compose_and_find(text, key_path)

    doc = yaml.load(text, Loader=UniqueKeyLoader)
    recorded_hash = doc.get("state_hash") if isinstance(doc, dict) else None
    computed_hash = canonical_hash(text)
    if recorded_hash is None:
        seal_status = "UNSEALED"
    elif recorded_hash == computed_hash:
        seal_status = "SEAL_OK"
    else:
        seal_status = "SEAL_MISMATCH"

    blame = gitobj.blame_last_change(path, line_start, line_end, commit=commit, repo=repo)
    last_changed_commit, last_changed_date = blame if blame else (None, None)

    return StateLookupResult(
        alias=alias, key_path=key_path, value=(None if excluded else value), path=path, commit=commit, blob=blob,
        line_start=line_start, line_end=line_end, seal_status=seal_status, recorded_state_hash=recorded_hash,
        computed_state_hash=computed_hash, last_changed_commit=last_changed_commit,
        last_changed_date=last_changed_date, excluded=excluded, excluded_hits=(1 if excluded else 0),
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.authority.state")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get")
    g.add_argument("alias")
    g.add_argument("key_path")
    g.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(g)
    args = p.parse_args(argv)

    ctx = taskctxmod.from_args(args)
    if args.cmd == "get":
        try:
            result = get(args.alias, args.key_path, task=ctx)
        except (KeyError, ValueError, FileNotFoundError) as e:
            print(json.dumps({"error": str(e)}, indent=1))
            return 1
        print(json.dumps(result.to_dict(), indent=1, sort_keys=True, default=str))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
