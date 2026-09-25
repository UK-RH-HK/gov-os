#!/usr/bin/env python3
"""Bounding policy (ARCHITECTURE.md section 7.3, ``config/budgets.yaml``). Budgets are UTF-8 bytes; a profile is
chosen per task class by ``task_spec['budget_profile']``.

**A is never truncated** (ARCHITECTURE.md section 5.3 rule 6). Items with delivery ``MANDATORY`` or ``PINNED`` are
never displaced by budget in ANY section -- "pinned: delivered deterministically, never displaced by budget, never
ranked" (section 7.2). Only ``RETRIEVED``/``DERIVED`` items are ever dropped, lowest in the section's own sort order
first, one whole item at a time, never mid-item. If section A's own bytes exceed the profile's total budget, A's
oversized items (over ``per_item_cap_bytes``) are converted to by-reference delivery (an exact pointer plus a
read-token obligation) rather than dropped -- and if EVEN THAT still will not fit, the compiler emits
``BLOCKED_BUDGET`` (never drops a mandatory item -- W4, "explicit governed failure").
"""
from __future__ import annotations

import dataclasses
from typing import Optional

from govbridge.core.yamlutil import load_yaml_file

STATUS_OK = "OK"
STATUS_BLOCKED_BUDGET = "BLOCKED_BUDGET"

NEVER_DROPPED_DELIVERIES = ("MANDATORY", "PINNED")


@dataclasses.dataclass(frozen=True)
class BudgetProfile:
    name: str
    total_bytes: int
    section_caps_bytes: dict  # {"A": None, "B": int, ...} -- None means "no independent cap" (A, I, J)
    per_item_cap_bytes: int
    rrf_k: int
    graph_neighbour_depth: int
    parent_expansion_top_n: int
    max_slice_chars: int


def load_profiles(path: str) -> dict:
    doc = load_yaml_file(path)
    out = {}
    for name, p in doc["profiles"].items():
        caps = {k: (int(v) * 1024 if v is not None else None) for k, v in (p.get("section_caps_kb") or {}).items()}
        out[name] = BudgetProfile(
            name=name, total_bytes=int(p["total_kb"]) * 1024, section_caps_bytes=caps,
            per_item_cap_bytes=int(doc.get("per_item_cap_kb", 24)) * 1024,
            rrf_k=int(doc.get("rrf_k", 60)), graph_neighbour_depth=int(doc.get("graph_neighbour_depth", 1)),
            parent_expansion_top_n=int(doc.get("parent_expansion_top_n", 3)),
            max_slice_chars=int(doc.get("max_slice_chars", 1600)),
        )
    return out


def _default_budgets_path() -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "budgets.yaml")


def load_profile(profile_name: str, path: Optional[str] = None) -> BudgetProfile:
    profiles = load_profiles(path or _default_budgets_path())
    if profile_name not in profiles:
        raise ValueError(f"unknown budget_profile {profile_name!r} (known: {sorted(profiles)})")
    return profiles[profile_name]


def _item_bytes(item) -> int:
    return len((item.text or "").encode("utf-8"))


def _as_reference(item, reason: str = "BUDGET"):
    """A copy of ``item`` with its body replaced by an exact-reference pointer (ARCHITECTURE.md section 5.3 rule 6:
    "delivered by exact reference (path@commit, line range, sha256), with a read-token obligation"), never dropped."""
    pointer = f"[by reference: {item.path}@{item.commit}"
    if item.line_start is not None:
        pointer += f":{item.line_start}-{item.line_end}"
    pointer += f", sha256={item.content_sha256}] (over the per-item cap; read the source and acknowledge its" \
               f" content_sha256 in your receipt's external_reads or inputs_consumed)"
    return dataclasses.replace(item, text=pointer, by_reference=True)


def enforce_section_a(a_items: list, profile: BudgetProfile) -> tuple:
    """Returns ``(items_after, blocked_budget)``. Every item in ``a_items`` has delivery MANDATORY; none is ever
    dropped. If A's total bytes exceed the profile's total budget, oversized items become by-reference first; if
    that still does not fit, ``blocked_budget`` is True and the caller emits status ``BLOCKED_BUDGET`` -- A's items
    themselves are returned UNCHANGED in that case (a blocked packet still names every mandatory input exactly)."""
    total = sum(_item_bytes(i) for i in a_items)
    if total <= profile.total_bytes:
        return a_items, False

    shrunk = [
        _as_reference(i, "OVER_PER_ITEM_CAP") if _item_bytes(i) > profile.per_item_cap_bytes else i
        for i in a_items
    ]
    total2 = sum(_item_bytes(i) for i in shrunk)
    if total2 <= profile.total_bytes:
        return shrunk, False
    return a_items, True


def _sort_key_of(item) -> tuple:
    from govbridge.compile.packet import sort_key
    return sort_key(item)


def enforce_section(section: str, items: list, profile: BudgetProfile) -> tuple:
    """Returns ``(items_after, drops)``. ``drops`` is a list of ``{item_id, unit, reason, score, bytes}`` dicts,
    ARCHITECTURE.md section 7.3's manifest shape. Never-dropped items (MANDATORY/PINNED) are always kept, in their
    given order, first; droppable items (RETRIEVED/DERIVED) are kept in the section's own sort order while bytes
    remain, dropped lowest-priority-first otherwise -- never mid-item."""
    cap = profile.section_caps_bytes.get(section)
    never_drop = [i for i in items if i.delivery in NEVER_DROPPED_DELIVERIES]
    droppable = sorted((i for i in items if i.delivery not in NEVER_DROPPED_DELIVERIES), key=_sort_key_of)

    kept = list(never_drop)
    used = sum(_item_bytes(i) for i in never_drop)
    drops = []
    if cap is None:
        kept.extend(droppable)
        return kept, drops

    for item in droppable:
        b = _item_bytes(item)
        if used + b <= cap:
            kept.append(item)
            used += b
        else:
            drops.append({
                "item_id": item.item_id, "unit": {"kind": item.unit_kind, "id": item.unit_id},
                "reason": "BUDGET", "score": item.fused_score, "bytes": b, "_section": section,
            })
    # restore a stable, section-ordered arrangement (never_drop items keep their placement order relative to kept
    # droppable ones via the shared sort key, applied uniformly across the whole kept list by the caller).
    return kept, drops


def enforce_combined(letter: str, subsections: dict, profile: BudgetProfile) -> tuple:
    """Like ``enforce_section``, but for a section split into sub-blocks that share ONE byte cap (D: D.1/D.2/D.3,
    ARCHITECTURE.md section 7.3: "D 40 (D.2/D.3 pinned)"). D.2/D.3 are entirely PINNED (never dropped); only D.1's
    RETRIEVED/DERIVED entries are ever droppable, and only after every sub-block's never-dropped items are counted
    against the shared cap. Returns ``(subsections_after, drops)``."""
    cap = profile.section_caps_bytes.get(letter)
    never_drop: dict = {}
    droppable_all: list = []
    for sub, items in subsections.items():
        never_drop[sub] = [i for i in items if i.delivery in NEVER_DROPPED_DELIVERIES]
        droppable_all.extend((sub, i) for i in items if i.delivery not in NEVER_DROPPED_DELIVERIES)
    droppable_all.sort(key=lambda pair: _sort_key_of(pair[1]))

    kept = {sub: list(nd) for sub, nd in never_drop.items()}
    used = sum(_item_bytes(i) for nd in never_drop.values() for i in nd)
    drops: list = []
    if cap is None:
        for sub, item in droppable_all:
            kept[sub].append(item)
        return kept, drops
    for sub, item in droppable_all:
        b = _item_bytes(item)
        if used + b <= cap:
            kept[sub].append(item)
            used += b
        else:
            drops.append({
                "item_id": item.item_id, "unit": {"kind": item.unit_kind, "id": item.unit_id},
                "reason": "BUDGET", "score": item.fused_score, "bytes": b, "_section": sub,
            })
    return kept, drops


def apply_budgets(sections: dict, profile: BudgetProfile) -> tuple:
    """``sections``: ``{letter_or_subblock: [PacketItem, ...]}``, already fully assembled (pre-budget). Returns
    ``(sections_after, all_drops, blocked_budget)``. Section A (and A alone) uses ``enforce_section_a``; D's three
    sub-blocks (D.1/D.2/D.3, if present) share ARCHITECTURE.md section 7.3's one "D" cap via ``enforce_combined``;
    every other section uses ``enforce_section``."""
    out: dict = {}
    all_drops: list = []
    blocked_budget = False

    if "A" in sections:
        out["A"], blocked_budget = enforce_section_a(sections["A"], profile)

    d_keys = [k for k in sections if k in ("D.1", "D.2", "D.3")]
    if d_keys:
        d_out, d_drops = enforce_combined("D", {k: sections[k] for k in d_keys}, profile)
        out.update(d_out)
        all_drops.extend(d_drops)

    for key, items in sections.items():
        if key == "A" or key in d_keys:
            continue
        kept, drops = enforce_section(key, items, profile)
        out[key] = kept
        all_drops.extend(drops)

    return out, all_drops, blocked_budget


def main(argv=None) -> int:  # pragma: no cover
    import argparse
    import json
    p = argparse.ArgumentParser(prog="govbridge.compile.budgets")
    p.add_argument("profile")
    p.add_argument("--path")
    args = p.parse_args(argv)
    prof = load_profile(args.profile, path=args.path)
    print(json.dumps(dataclasses.asdict(prof), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
