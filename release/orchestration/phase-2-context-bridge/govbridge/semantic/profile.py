"""Semantic embed-profile interpreter (node B4; ARCHITECTURE.md section 4.5, SEMANTIC_ROUTE.md section 3,
``config/embed-profile.yaml``).

Generic by construction (OC-BR-02): this module knows the *shape* of an embed profile (a kind allowlist with an
optional per-kind size cap, plus a per-ref layer gate) and how to evaluate it against one blob/ref pair. It does
not know or care what any particular path, ref or repository contains. Nothing here names Review 8, a phase or a
specific file.

Two independent gates decide whether a chunk is embedded:

1. **Kind admission** (``embed_kinds`` / ``embed_kinds_size_le``): the blob's extension must be on the allowlist,
   and if that kind carries a size cap, the blob must be at or under it. This is deliberately narrower than
   ``config/corpus-rules.yaml``'s own INCLUDE/LEXICAL_ONLY split -- a kind absent from both lists (for example
   ``.csv``) is corpus-INCLUDED (so the lexical and exact routes see it) but never embedded.
2. **Ref eligibility** (``history_role_embedded``): a blob is embedded only if at least one of its occurrences is
   in a ref whose ``config/canonical-view.yaml`` entry lists ``semantic`` in ``layers`` (or omits ``layers``
   entirely, meaning "every layer"). This reads the already-parsed ``ResolvedView``/``RefSpec.layers`` field B1
   provides for exactly this purpose; it never hard-codes a role name such as "history".
"""
from __future__ import annotations

import dataclasses
from typing import Optional

from govbridge.core.yamlutil import load_yaml_file
from govbridge.core.view import ResolvedView


@dataclasses.dataclass(frozen=True)
class EmbedProfile:
    embed_kinds: frozenset
    embed_kinds_size_le: dict
    lexical_only_kinds: frozenset
    lexical_only_kinds_size_gt: dict
    history_role_embedded: bool
    layer_name: str
    raw: dict


def load_profile(path: str) -> EmbedProfile:
    doc = load_yaml_file(path)
    return EmbedProfile(
        embed_kinds=frozenset(doc.get("embed_kinds") or []),
        embed_kinds_size_le=dict(doc.get("embed_kinds_size_le") or {}),
        lexical_only_kinds=frozenset(doc.get("lexical_only_kinds") or []),
        lexical_only_kinds_size_gt=dict(doc.get("lexical_only_kinds_size_gt") or {}),
        history_role_embedded=bool(doc.get("history_role_embedded", False)),
        layer_name=str(doc.get("layer_name", "semantic")),
        raw=doc,
    )


def kind_of(path: str) -> str:
    base = path.rsplit("/", 1)[-1]
    if "." not in base:
        return ""
    return base.rsplit(".", 1)[-1].lower()


def kind_admitted(profile: EmbedProfile, path: str, size: int) -> bool:
    """True when this (path, size) pair is inside the embed profile's positive admission list. Independent of
    any corpus-rules.yaml effect -- a caller that also wants corpus admissibility must check that separately."""
    kind = kind_of(path)
    if kind not in profile.embed_kinds:
        return False
    cap = profile.embed_kinds_size_le.get(kind)
    if cap is not None and size > int(cap):
        return False
    return True


def _admits(spec, profile: EmbedProfile) -> bool:
    """A RefSpec admits this profile's layer when its own ``layers`` list names it explicitly. When the spec
    omits ``layers`` altogether, a history-role spec falls back to the profile's ``history_role_embedded``
    default (the fixed point for a view that never says); any other role defaults to admitted (unrestricted)."""
    if spec.layers is not None:
        return profile.layer_name in spec.layers
    if spec.role == "history":
        return profile.history_role_embedded
    return True


def eligible_ref_names(resolved: ResolvedView, profile: EmbedProfile) -> set:
    """The set of ref names (named refs, plus every individual history-glob ref) whose ``layers`` admit this
    profile's layer. A RefSpec with ``layers: None`` admits every layer except the history role (the "collapses
    to {primary: HEAD}" single-ref case, ARCHITECTURE.md section 10, has no history ref at all)."""
    admitted: set = set()
    for name in resolved.named:
        spec = next((r for r in resolved.config.refs if r.name == name), None)
        if spec is None or _admits(spec, profile):
            admitted.add(name)
    if resolved.history:
        history_spec = next((r for r in resolved.config.refs if r.ref_glob is not None), None)
        if history_spec is None or _admits(history_spec, profile):
            for hist_name, _commit in resolved.history:
                admitted.add(hist_name)
    return admitted
