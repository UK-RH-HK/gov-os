#!/usr/bin/env python3
"""Version reconciliation (REPAIR_PLAN.md section 2.7's ``versions`` facet; REPAIR_DAG.yaml node R1-GA2; OD-BR-05
section 6 "reconcile versions"). ``govbridge.gather.engine`` (R1-GA1) registers the ``versions`` facet as
``synthetic`` and always reports it ``MISSING`` -- "version reconciliation is REPAIR_DAG.yaml node R1-GA2, not yet
built" (``config/facets.yaml``). This module is that reconciliation: per-path blob identity across the view's
refs, and the canonical ref, for every distinct path a gather's merged evidence touched.

Generically by ROLE, never by ref NAME (this node's brief, and REPAIR_PLAN.md section 2.7): the only per-path
decision this module makes -- which ref is canonical for that path -- comes from
``govbridge.core.view.ResolvedView.partition_for`` (config/canonical-view.yaml's own partitions), exactly the way
``govbridge.code.lineage_layer``'s own ``_version_status`` and every real route's classification already do.
Nothing here is ever conditioned on a ref's NAME (a config could rename "product"/"records"/"evidence" freely and
this module's behaviour would not change) -- only on its declared ``role`` (the fixed, documented vocabulary
ARCHITECTURE.md section 1.2 names: "primary", "product", "evidence", "history", ...), read straight off
``ResolvedView.config.refs`` the SAME way ``govbridge.route.real_routes._product_commit`` already reads the
"product" role.
"""
from __future__ import annotations

import dataclasses
from typing import Optional

from govbridge.core import gitobj

#: how many of the (potentially many) refs a "history" ref_glob resolves to are reported individually before this
#: module summarises the rest by count -- REPAIR_PLAN.md section 2.4's "within budget" discipline, generalised to
#: this facet: a corpus with dozens of history tips must never make one gather call walk every one of them for
#: every path.
_MAX_HISTORY_REFS_LISTED = 5


@dataclasses.dataclass(frozen=True)
class RefIdentity:
    ref_name: str
    role: str
    commit: Optional[str]
    blob: Optional[str]
    status: str  # "CANONICAL" | "IDENTICAL" | "DIFFERENT" | "ABSENT"

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _role_for_ref_name(resolved_view, ref_name: str) -> str:
    for r in resolved_view.config.refs:
        if r.name == ref_name:
            return r.role
    return "history"  # every name in resolved_view.history came from a ref_glob role, by construction


def reconcile_path(resolved_view, path: str, repo: Optional[str] = None) -> dict:
    """Per-``(ref, path)`` blob identity for ONE path, across every ref the view resolves -- the canonical ref
    decided by ``partition_for`` (never a hardcoded name), every other ref's own blob compared against it. A ref
    absent from this path entirely (a genuine ``git ls-tree`` miss) is reported ``ABSENT``, never silently
    dropped -- the SAME "never a silent drop" discipline every other REPAIR-1 resolver in this domain follows."""
    part = resolved_view.partition_for(path)
    owner_ref = resolved_view.named.get(part.owner)
    canonical_commit = owner_ref.commit if owner_ref else None
    canonical_role = _role_for_ref_name(resolved_view, part.owner) if owner_ref else None
    canonical_blob = gitobj.blob_at(canonical_commit, path, repo=repo) if canonical_commit else None

    per_ref: list = []
    for ref_name, resolved_ref in sorted(resolved_view.named.items()):
        commit = resolved_ref.commit
        blob = gitobj.blob_at(commit, path, repo=repo)
        role = _role_for_ref_name(resolved_view, ref_name)
        if blob is None:
            status = "ABSENT"
        elif ref_name == part.owner:
            status = "CANONICAL"
        elif blob == canonical_blob:
            status = "IDENTICAL"
        else:
            status = "DIFFERENT"
        per_ref.append(RefIdentity(ref_name=ref_name, role=role, commit=commit, blob=blob, status=status))

    history_reported = 0
    history_differing = 0
    history_total = len(resolved_view.history)
    for hist_name, hist_commit in sorted(resolved_view.history):
        blob = gitobj.blob_at(hist_commit, path, repo=repo)
        status = "ABSENT" if blob is None else ("IDENTICAL" if blob == canonical_blob else "DIFFERENT")
        if status == "DIFFERENT":
            history_differing += 1
        if history_reported < _MAX_HISTORY_REFS_LISTED:
            per_ref.append(RefIdentity(ref_name=hist_name, role="history", commit=hist_commit, blob=blob,
                                        status=status))
            history_reported += 1

    identical = [r.ref_name for r in per_ref if r.status in ("CANONICAL", "IDENTICAL")]
    differing = [r.ref_name for r in per_ref if r.status == "DIFFERENT"]
    absent = [r.ref_name for r in per_ref if r.status == "ABSENT"]
    parts = []
    if identical:
        parts.append(f"identical at refs {', '.join(identical)}")
    if differing:
        parts.append(f"differs at {', '.join(differing)}")
    if absent:
        parts.append(f"absent at {', '.join(absent)}")
    if history_total > _MAX_HISTORY_REFS_LISTED:
        parts.append(f"{history_total - _MAX_HISTORY_REFS_LISTED} further history ref(s) not individually listed "
                      f"({history_differing} of the {history_total} history refs checked differ)")
    summary = "; ".join(parts) if parts else "no ref carries this path"

    return {
        "path": path, "canonical_ref": part.owner, "canonical_role": canonical_role,
        "canonical_commit": canonical_commit, "canonical_blob": canonical_blob,
        "per_ref": [r.to_dict() for r in per_ref], "summary": summary,
    }


def versions_facet(resolved_view, paths: list, repo: Optional[str] = None) -> dict:
    """The ``versions`` facet's real content (REPAIR_PLAN.md section 2.7), replacing
    ``govbridge.gather.engine``'s always-``MISSING`` synthetic placeholder for exactly this facet name --
    :mod:`govbridge.gather.followup` is the caller that splices this in, never ``engine.py`` itself (out of this
    node's mutation scope). ``paths``: the distinct occurrence paths of a gather's own merged evidence; an empty
    list is the ONE case this module still reports ``missing`` (nothing to reconcile), with the SAME disclosed
    honesty R1-GA1's placeholder already established -- never a bare, unexplained empty result."""
    distinct = sorted({p for p in paths if p})
    if resolved_view is None or not distinct:
        return {
            "facet": "versions", "missing": True,
            "missing_reason": ("no resolved view was available for this gather" if resolved_view is None
                                else "no path was resolvable from this gather's merged evidence to reconcile"),
            "items": [],
        }
    items = [reconcile_path(resolved_view, p, repo=repo) for p in distinct]
    return {"facet": "versions", "missing": False, "missing_reason": None, "items": items}
