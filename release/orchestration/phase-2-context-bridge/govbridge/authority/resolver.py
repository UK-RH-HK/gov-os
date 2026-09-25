#!/usr/bin/env python3
"""The mandatory-input resolver (ARCHITECTURE.md section 5.3 rule 1, section 7.1's ``required_inputs``,
``ARCHITECTURE/schemas/task-spec.yaml``). Section A of a packet is filled ONLY by this module.

``MandatoryItem`` is a frozen dataclass constructed only here -- no route, and no other module in this package,
builds one. Every ``required_inputs`` row is resolved to an exact occurrence (or set of occurrences, for a
``[*]``-suffixed state_ref) with a sha256 check against ``content_hash`` (path_form/id_form) or the row's own
recorded ``sha256`` (state_form, when the state row carries one); a missing input or a hash mismatch makes the
WHOLE resolution ``BLOCKED`` (W3/W4) -- a mandatory input is never partially satisfied.

Imports nothing from ``govbridge.lexical``/``.semantic``/``.code``/``.graph``/``.route`` (enforced by
tests/authority/test_import_boundary.py, an ``ast`` check).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import registry as registrymod
from govbridge.core import gitobj, view as viewmod
from govbridge.core.yamlutil import load_yaml_file, load_yaml_text, sha256_bytes

STATUS_OK = "OK"
STATUS_BLOCKED = "BLOCKED"

def _load_state_aliases() -> dict:
    """The alias -> path table, moved to ``config/state-aliases.yaml`` (routed issue B5/BR-AR-0007: "hard-coded
    state aliases in resolver.py"; I1/BR-AR-0009 closes it, near-frozen-module carve-out: "moving hard-coded path
    constants into config"). Read once, at import time, from the domain's own config directory -- the same way
    every other bridge config file (corpus-rules.yaml, budgets.yaml, ...) is read off disk, never through Git."""
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    path = os.path.join(GOV_BRIDGE_DOMAIN, "config", "state-aliases.yaml")
    return dict(load_yaml_file(path)["aliases"])


STATE_ALIASES = _load_state_aliases()

STATE_REF_RE = re.compile(r"^state:(?P<alias>[^#]+)#(?P<key>.+?)(?P<star>\[\*\])?$")
PATH_FORM_RE = re.compile(r"^(?P<path>[^@]+)@(?P<ref>[^:]+)(?::(?P<l1>\d+)(?:-(?P<l2>\d+))?)?$")


@dataclasses.dataclass(frozen=True)
class MandatoryItem:
    """Section A's only admissible unit (ARCHITECTURE.md section 5.3 rule 1). Frozen: never mutated after
    construction; no conversion function exists to or from RetrievedItem/DerivedItem."""
    id: str
    cls: str
    lifecycle: str
    path: Optional[str]
    commit: Optional[str]
    blob: Optional[str]
    line_start: Optional[int]
    line_end: Optional[int]
    sha256: Optional[str]
    reason: str
    source_row: str  # which required_inputs entry (its state_ref/id/path) produced this item

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ResolveResult:
    status: str
    items: list  # [MandatoryItem]
    blocked_reasons: list

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "items": [i.to_dict() for i in self.items],
            "blocked_reasons": self.blocked_reasons,
        }


def _resolve_view(view_path: str, repo: Optional[str] = None) -> "viewmod.ResolvedView":
    vc = viewmod.load_view(view_path)
    return viewmod.resolve_view(vc, repo=repo)


def _get_key_path(doc: dict, key_path: str):
    node = doc
    for part in key_path.split("."):
        if isinstance(node, dict):
            if part not in node:
                raise KeyError(f"{key_path!r}: no key {part!r}")
            node = node[part]
        else:
            raise KeyError(f"{key_path!r}: {part!r} is not inside a mapping")
    return node


def _load_state_doc(alias: str, resolved_view: "viewmod.ResolvedView", repo: Optional[str] = None) -> tuple:
    if alias not in STATE_ALIASES:
        raise ValueError(f"unknown state alias {alias!r} (known: {sorted(STATE_ALIASES)})")
    path = STATE_ALIASES[alias]
    classification = resolved_view.classify_occurrence(path, resolved_view.ref_commit("records"))
    commit = classification.canonical_commit
    text = gitobj.read_path(commit, path, repo=repo)
    if text is None:
        raise FileNotFoundError(f"{commit}:{path} not found")
    return load_yaml_text(text.decode("utf-8")), path, commit


def _sha256_of(path: str, commit: str, repo: Optional[str] = None) -> Optional[str]:
    blob = gitobj.blob_at(commit, path, repo=repo)
    if blob is None:
        return None
    raw = gitobj.read_blob(blob, repo=repo)
    if raw is None:
        return None
    return sha256_bytes(raw)


def _one_mandatory_item(this_id: str, path: str, base_item_id: str, row: dict,
                         resolved_view: "viewmod.ResolvedView", reg: registrymod.Registry,
                         mandatory_items_index: dict, source_row: str, reason: str,
                         repo: Optional[str] = None) -> tuple:
    """Resolves ONE (id, path) pair to a MandatoryItem. ``this_id`` is what the returned item is identified by
    (the row's own id for a single-path row, or an ``id#pathN`` for the 2nd+ path of a multi-path row -- see
    ``_mandatory_item_from_row``); ``base_item_id`` is the row's real id, used for every registry/mandatory-items
    lookup (the registry and ``mandatory_bridge_inputs`` know nothing about a synthetic ``#pathN`` suffix).
    Returns (MandatoryItem_or_None, blocked_reason_or_None)."""
    expected_sha256 = row.get("sha256")
    commit_hint = row.get("commit")

    if commit_hint:
        commit = gitobj.resolve_commit(commit_hint, repo=repo) or commit_hint
    else:
        classification = resolved_view.classify_occurrence(path, resolved_view.ref_commit("records"))
        commit = classification.canonical_commit

    is_directory = path.endswith("/")
    entry = gitobj.ls_tree_path(commit, path.rstrip("/"), repo=repo)
    if entry is None:
        return None, f"{this_id}: {path} not found at {commit}"
    blob = entry.oid  # a tree id for a directory entry, a blob id otherwise -- both are valid Git object ids

    if expected_sha256 and not is_directory:
        actual = _sha256_of(path, commit, repo=repo)
        if actual != expected_sha256:
            return None, f"{this_id}: sha256 mismatch at {path}@{commit} (expected {expected_sha256}, got {actual})"

    cls = row.get("class")
    line_start = line_end = None
    anchor = reg.anchor_by_item_id(base_item_id)
    if anchor is not None:
        line_start, line_end = anchor.line_start, anchor.line_end
        if cls is None:
            cls = anchor.cls

    if is_directory:
        # a directory entry (e.g. REVIEW-8-PROBES' probes/P2-AR-0097/) carries no text to read metadata from; its
        # class is given by the row, and its lifecycle defaults ACTIVE (the task-spec's own default for a resolved
        # required_input) unless a registry entry restricts it.
        override = reg.lifecycle_override_for(base_item_id)
        lifecycle = override.lifecycle if override is not None else classesmod.LIFECYCLE_ACTIVE
        if cls is None:
            cls = "UNCLASSIFIED"
        sha256_val = expected_sha256
    else:
        classification = lifecyclemod.classify(base_item_id, path=path, commit=commit, line_start=line_start,
                                                line_end=line_end, reg=reg, mandatory_items=mandatory_items_index,
                                                repo=repo)
        if cls is None:
            cls = classification.cls
        lifecycle = classification.lifecycle
        sha256_val = expected_sha256 or _sha256_of(path, commit, repo=repo)

    item = MandatoryItem(
        id=this_id, cls=cls, lifecycle=lifecycle, path=path, commit=commit, blob=blob,
        line_start=line_start, line_end=line_end, sha256=sha256_val,
        reason=reason, source_row=source_row,
    )
    return item, None


def _mandatory_item_from_row(row: dict, resolved_view: "viewmod.ResolvedView", reg: registrymod.Registry,
                              mandatory_items_index: dict, source_row: str, reason: str,
                              repo: Optional[str] = None) -> tuple:
    """Returns (MandatoryItem_or_None, blocked_reason_or_None) -- one item per row, its PRIMARY occurrence
    (``path``, or ``paths[0]`` for a multi-path row), exactly as originally. Routed issue B5/BR-AR-0007 OI-3 ("a
    multi-path mandatory item resolves only its first path") is closed below: EVERY listed path is now verified to
    exist at the resolved commit (a mandatory input is never partially satisfied -- a missing second path BLOCKS
    the whole row, not just a missing first one), which is the actual gap B5 found ("both paths still verify to
    exist" only because nothing had checked the second one). This deliberately still yields exactly one
    MandatoryItem per row: an earlier version of this fix emitted a second item (``id#path2``) for the extra path,
    but that changed section A's real-view item set and broke an existing, frozen acceptance test
    (tests/compile/test_compile_real_view_mandatory_in_a.py's ``EXPECTED_IN_A``/``lifecycle_notices`` assertions,
    written under B6R against exactly one item per REVIEW-8-PROBES row) -- existing tests are frozen, so the extra
    path is validated but not turned into new, separately-classified section-A evidence."""
    item_id = row.get("id") or source_row
    path = row.get("path")
    paths = row.get("paths")

    if path is None and paths:
        path = paths[0]  # the primary occurrence
    if path is None:
        anchor = reg.anchor_by_item_id(item_id)
        if anchor is not None:
            path = anchor.path

    if path is None:
        return None, f"{item_id}: no path, paths[] or registry section_anchor to resolve an occurrence from"

    item, blocked = _one_mandatory_item(item_id, path, item_id, row, resolved_view, reg, mandatory_items_index,
                                         source_row, reason, repo=repo)
    if item is None:
        return None, blocked

    if paths and len(paths) > 1:
        for extra_path in paths[1:]:
            if extra_path == path:
                continue
            if gitobj.ls_tree_path(item.commit, extra_path.rstrip("/"), repo=repo) is None:
                return None, f"{item_id}: additional path {extra_path} not found at {item.commit}"

    return item, None


def resolve(task_spec: dict, repo: Optional[str] = None, registry_path: Optional[str] = None) -> ResolveResult:
    view_path = task_spec["view"]
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    if not os.path.isabs(view_path):
        view_path = os.path.join(GOV_BRIDGE_DOMAIN, view_path) if not os.path.exists(view_path) else view_path
    resolved_view = _resolve_view(view_path, repo=repo)
    reg = registrymod.load(registry_path or registrymod._default_registry_path(), verify_commit="records",
                            view_path=view_path, repo=repo)
    mandatory_items_index = lifecyclemod._load_mandatory_items(repo=repo, view_path=view_path)

    items: list = []
    blocked: list = []

    for entry in task_spec.get("required_inputs", []):
        reason = entry.get("reason", "")
        if "state_ref" in entry:
            m = STATE_REF_RE.match(entry["state_ref"])
            if not m:
                blocked.append(f"malformed state_ref: {entry['state_ref']!r}")
                continue
            alias, key_path, star = m.group("alias"), m.group("key"), m.group("star")
            try:
                doc, state_path, state_commit = _load_state_doc(alias, resolved_view, repo=repo)
                value = _get_key_path(doc, key_path)
            except (KeyError, ValueError, FileNotFoundError) as e:
                blocked.append(f"{entry['state_ref']}: {e}")
                continue
            rows = value if star else [value]
            if not isinstance(rows, list):
                rows = [rows]
            for idx, row in enumerate(rows):
                source_row = f"{entry['state_ref']}[{idx}]" if star else entry["state_ref"]
                if not isinstance(row, dict):
                    # a scalar/leaf value (e.g. contract_v3.sha256 alone) -- not expected from these three inputs,
                    # but handled generically: no occurrence to check beyond the state file that carries it.
                    blocked.append(f"{source_row}: not a mapping, cannot resolve an occurrence ({row!r})")
                    continue
                item, reason_blocked = _mandatory_item_from_row(
                    row, resolved_view, reg, mandatory_items_index, source_row, reason, repo=repo)
                if item is None:
                    blocked.append(reason_blocked)
                else:
                    items.append(item)

        elif "id" in entry:
            item_id = entry["id"]
            required_status = entry.get("required_status") or classesmod.LIFECYCLE_ACTIVE
            found = lifecyclemod._find_definition(item_id, repo=repo, view_path=view_path)
            anchor = reg.anchor_by_item_id(item_id)
            if found is None and anchor is None:
                blocked.append(f"{item_id}: no definition found (id_form required_input)")
                continue
            path, commit, line_start, line_end = found if found else (anchor.path, resolved_view.ref_commit("records"),
                                                                        anchor.line_start, anchor.line_end)
            classification = lifecyclemod.classify(item_id, path=path, commit=commit, line_start=line_start,
                                                     line_end=line_end, reg=reg,
                                                     mandatory_items=mandatory_items_index, repo=repo)
            if classification.lifecycle != required_status:
                blocked.append(f"{item_id}: lifecycle {classification.lifecycle} != required_status {required_status}")
                continue
            content_hash = entry.get("content_hash")
            actual = _sha256_of(path, commit, repo=repo) if path and commit else None
            if content_hash and actual != content_hash:
                blocked.append(f"{item_id}: content_hash mismatch (expected {content_hash}, got {actual})")
                continue
            blob = gitobj.blob_at(commit, path, repo=repo) if path and commit else None
            items.append(MandatoryItem(id=item_id, cls=classification.cls, lifecycle=classification.lifecycle,
                                        path=path, commit=commit, blob=blob, line_start=line_start,
                                        line_end=line_end, sha256=actual, reason=reason, source_row=f"id:{item_id}"))

        elif "path" in entry:
            m = PATH_FORM_RE.match(entry["path"])
            if not m:
                blocked.append(f"malformed path_form: {entry['path']!r}")
                continue
            path, ref = m.group("path"), m.group("ref")
            commit = resolved_view.ref_commit(ref) or gitobj.resolve_commit(ref, repo=repo)
            if commit is None:
                blocked.append(f"{entry['path']}: ref {ref!r} does not resolve")
                continue
            blob = gitobj.blob_at(commit, path, repo=repo)
            if blob is None:
                blocked.append(f"{entry['path']}: {path} not found at {commit}")
                continue
            content_hash = entry.get("content_hash")
            actual = _sha256_of(path, commit, repo=repo)
            if content_hash and actual != content_hash:
                blocked.append(f"{entry['path']}: content_hash mismatch (expected {content_hash}, got {actual})")
                continue
            l1 = int(m.group("l1")) if m.group("l1") else None
            l2 = int(m.group("l2")) if m.group("l2") else l1
            classification = lifecyclemod.classify(path, path=path, commit=commit, line_start=l1, line_end=l2,
                                                     reg=reg, mandatory_items=mandatory_items_index, repo=repo)
            items.append(MandatoryItem(id=path, cls=classification.cls, lifecycle=classification.lifecycle,
                                        path=path, commit=commit, blob=blob, line_start=l1, line_end=l2,
                                        sha256=actual, reason=reason, source_row=f"path:{entry['path']}"))
        else:
            blocked.append(f"required_inputs entry has none of state_ref/id/path: {entry!r}")

    status = STATUS_BLOCKED if blocked else STATUS_OK
    return ResolveResult(status=status, items=items, blocked_reasons=blocked)


def resolve_file(task_spec_path: str, repo: Optional[str] = None) -> ResolveResult:
    task_spec = load_yaml_file(task_spec_path)
    return resolve(task_spec, repo=repo)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.authority.resolver")
    p.add_argument("task_spec")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    args = p.parse_args(argv)

    result = resolve_file(args.task_spec)
    print(json.dumps(result.to_dict(), indent=1, sort_keys=True))
    return 0 if result.status == STATUS_OK else 1


if __name__ == "__main__":
    sys.exit(main())
