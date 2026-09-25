"""Labelled call resolution over a Rust symbol table (ARCHITECTURE.md section 4.6). Pure and in-memory: given the
definitions and call sites already parsed from a fixed set of blobs (one commit's ``.rs`` tree, govbridge.code.
symbols), decide a resolution label for each call. Never picks a single target among several surviving candidates
(BR-HO-0005: "An ambiguous call must never yield a single chosen target") -- HEURISTIC_AMBIGUOUS always carries
every candidate, and no code path here collapses that list to one.

Resolution is a function of the *whole commit's* symbol set, not of one call site in isolation -- a name that is
unique in one commit's tree can become ambiguous in another once a colliding file is added (or vice-versa once one
is removed). It is therefore never cached across commits; callers (govbridge.code.symbols) recompute it fresh, in
memory, from the persisted per-blob facts for exactly the blobs present at the commit being queried. This module
knows nothing about which commit, repository or symbol names are involved -- it operates only on the ``Definition``/
``CallSite`` objects it is handed.
"""
from __future__ import annotations

import dataclasses

EXACT_PATH = "EXACT_PATH"
HEURISTIC_TYPE_PATH = "HEURISTIC_TYPE_PATH"
HEURISTIC_SAME_FILE = "HEURISTIC_SAME_FILE"
HEURISTIC_UNIQUE_NAME = "HEURISTIC_UNIQUE_NAME"
HEURISTIC_AMBIGUOUS = "HEURISTIC_AMBIGUOUS"
UNRESOLVED_EXTERNAL = "UNRESOLVED_EXTERNAL"
MACRO = "MACRO"
HEURISTIC_MACRO_TOKEN = "HEURISTIC_MACRO_TOKEN"

ALL_LABELS = frozenset({
    EXACT_PATH, HEURISTIC_TYPE_PATH, HEURISTIC_SAME_FILE, HEURISTIC_UNIQUE_NAME, HEURISTIC_AMBIGUOUS,
    UNRESOLVED_EXTERNAL, MACRO, HEURISTIC_MACRO_TOKEN,
})

# The only labels a resolution may carry more than one target under -- every other label is single-target-or-none
# by construction (checked by resolve_call itself, and asserted again by tests/code/test_resolution_labels.py).
MULTI_TARGET_LABELS = frozenset({HEURISTIC_AMBIGUOUS})

_FN_KINDS = ("fn", "fn_sig")


@dataclasses.dataclass(frozen=True)
class Definition:
    symbol_id: str
    blob_id: str
    path: str
    kind: str  # fn | fn_sig | struct | enum | trait | mod | const | static | macro | type
    name: str
    qualified_name: str
    module_path: str


@dataclasses.dataclass(frozen=True)
class CallSite:
    call_site_id: str
    blob_id: str
    path: str
    line: int
    callee_text: str
    callee_name: str
    call_kind: str  # bare | path | method | macro | macro_token


@dataclasses.dataclass(frozen=True)
class Resolution:
    label: str
    target_symbol_ids: tuple[str, ...]
    n_candidates: int


@dataclasses.dataclass(frozen=True)
class Index:
    """A commit-scoped lookup over every definition parsed from the blobs present at that commit. Built once per
    query by the caller (govbridge.code.symbols); never mutated."""
    by_name: dict
    by_path: dict

    @staticmethod
    def build(definitions: list) -> "Index":
        by_name: dict = {}
        by_path: dict = {}
        for d in definitions:
            by_name.setdefault(d.name, []).append(d)
            by_path.setdefault(d.path, []).append(d)
        return Index(by_name=by_name, by_path=by_path)


def resolve_call(call: CallSite, index: Index) -> Resolution:
    """Label one call site against ``index`` (every definition visible at the same commit). Mirrors
    ARCHITECTURE.md section 4.6's label table row for row:

    * ``EXACT_PATH``: a ``crate::...::f`` path resolves to exactly one definition in the module the path names.
    * ``HEURISTIC_TYPE_PATH``: a ``Type::f`` (or other non-``crate::``-rooted) path matches one candidate.
    * ``HEURISTIC_SAME_FILE``: a bare call matches exactly one fn defined in the same file.
    * ``HEURISTIC_UNIQUE_NAME``: the callee name is unique across every definition visible at this commit.
    * ``HEURISTIC_AMBIGUOUS``: several candidates remain; all are returned, none is chosen.
    * ``UNRESOLVED_EXTERNAL``: no candidate at all (std, another crate, or simply not visible in this view).
    * ``MACRO``: the call is a macro invocation itself (``foo!(...)``) -- never resolved as a function.
    * ``HEURISTIC_MACRO_TOKEN``: a call-shaped token found by scanning inside a macro's opaque token tree.
    """
    if call.call_kind == "macro":
        return Resolution(MACRO, (), 0)
    if call.call_kind == "macro_token":
        return Resolution(HEURISTIC_MACRO_TOKEN, (), 0)

    candidates = [d for d in index.by_name.get(call.callee_name, []) if d.kind in _FN_KINDS]

    if call.call_kind == "path" and "::" in call.callee_text:
        prefix = call.callee_text.rsplit("::", 1)[0]
        last_segment = prefix.rsplit("::", 1)[-1]
        matched = [
            d for d in candidates
            if d.module_path.endswith(last_segment) or d.qualified_name.startswith(last_segment + "::")
        ]
        if len(matched) == 1:
            label = EXACT_PATH if prefix.startswith("crate::") else HEURISTIC_TYPE_PATH
            return Resolution(label, (matched[0].symbol_id,), 1)
        if matched:
            return Resolution(HEURISTIC_AMBIGUOUS, tuple(d.symbol_id for d in matched), len(matched))

    if call.call_kind == "bare":
        same_file = [d for d in index.by_path.get(call.path, []) if d.name == call.callee_name and d.kind == "fn"]
        if len(same_file) == 1:
            return Resolution(HEURISTIC_SAME_FILE, (same_file[0].symbol_id,), 1)

    if len(candidates) == 1:
        return Resolution(HEURISTIC_UNIQUE_NAME, (candidates[0].symbol_id,), 1)
    if candidates:
        return Resolution(HEURISTIC_AMBIGUOUS, tuple(d.symbol_id for d in candidates), len(candidates))
    return Resolution(UNRESOLVED_EXTERNAL, (), 0)


def resolve_all(calls: list, index: Index) -> dict:
    """{call_site_id: Resolution} for every call in ``calls``. A thin loop wrapper -- kept separate from
    ``resolve_call`` so callers that only need one call's label never pay for the rest."""
    return {c.call_site_id: resolve_call(c, index) for c in calls}
