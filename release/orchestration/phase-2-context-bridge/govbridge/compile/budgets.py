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
import hashlib
from typing import Optional

from govbridge.core.yamlutil import load_yaml_file

STATUS_OK = "OK"
STATUS_BLOCKED_BUDGET = "BLOCKED_BUDGET"

NEVER_DROPPED_DELIVERIES = ("MANDATORY", "PINNED")

#: a drop record's ``sample_ids`` never carries more than this many unit ids (BR-AR-0015 reopening, defect 4:
#: "a count, sha256 over the sorted dropped unit ids, and the first 50 ids").
DROP_SAMPLE_LIMIT = 50


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
    # BR-AR-0015 reopening: the fixed, per-SECTION rendered-bytes allowance (title/queries-log/drop-footer/
    # read-token lines -- never an item), and the per-symbol fan-out caps G's T2 expansion is bound by. Defaulted
    # (never required) so an existing direct ``BudgetProfile(...)`` construction -- e.g. a pre-reopening test --
    # keeps working unmodified; ``load_profiles`` below always supplies both explicitly from config/budgets.yaml.
    section_header_bytes: int = 0
    g_fanout: dict = dataclasses.field(default_factory=dict)


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
            section_header_bytes=int(doc.get("section_header_bytes", 0)),
            g_fanout=dict(p.get("g_fanout") or {}),
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
    """BR-AR-0015 reopening, defect 1 ("the budget is bypassed by rendering"): measures the item's REAL rendered
    form -- the "- unit: ...(delivery=..., route=..., class=..., lifecycle=...)" line, the "source: path@commit:
    L1-L2" line, any banner/reason lines, THEN the body -- via ``govbridge.compile.render._render_item_body``, the
    exact function that writes packet.md. Budget enforcement and the worker's own rendered bytes can now never
    diverge: previously this counted ``item.text`` alone, so a section whose content fit its cap could still
    render to several times its cap once per-item metadata (~300 bytes/item, measured on the real demonstration
    packet) was included."""
    from govbridge.compile import render as rendermod
    return len(rendermod._render_item_body(item).encode("utf-8"))


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
                "tier": getattr(item, "tier", None),
            })
    # restore a stable, section-ordered arrangement (never_drop items keep their placement order relative to kept
    # droppable ones via the shared sort key, applied uniformly across the whole kept list by the caller).
    return kept, drops


def enforce_section_g(items: list, profile: BudgetProfile) -> tuple:
    """G's own tiered enforcement (BR-AR-0015 reopening, defect 2): T1 items (delivery PINNED -- every code/test
    citation the seed records themselves make, plus its enclosing definition) are NEVER dropped, matching
    ``enforce_section_a``'s own discipline but scoped to this one section -- "T1 is pinned inside G". If T1's own
    rendered bytes exceed G's cap, T1 items over the per-item cap become by-reference (never lose citation
    coverage -- "deliver T1 items by exact reference... rather than dropping them") and a notice is returned so
    the caller can flag it in J. T2/T3/T4 (droppable RETRIEVED content) are then filled into whatever budget
    remains, in TIER order (``sort_key`` already orders T2 before T3 before T4), so expansion/retrieval noise is
    dropped before ANY T1 anchor ever would be -- "expansion is dropped first". Returns ``(items_after, drops,
    notices)``."""
    cap = profile.section_caps_bytes.get("G")
    t1 = [i for i in items if i.delivery in NEVER_DROPPED_DELIVERIES]
    droppable = sorted((i for i in items if i.delivery not in NEVER_DROPPED_DELIVERIES), key=_sort_key_of)

    notices: list = []
    t1_bytes = sum(_item_bytes(i) for i in t1)
    if cap is not None and t1_bytes > cap:
        t1 = [_as_reference(i, "G_T1_OVER_BUDGET") if _item_bytes(i) > profile.per_item_cap_bytes else i for i in t1]
        t1_bytes = sum(_item_bytes(i) for i in t1)
        notices.append({"type": "G_T1_OVER_BUDGET", "bytes": t1_bytes, "cap": cap})

    kept = list(t1)
    used = t1_bytes
    drops: list = []
    if cap is None:
        kept.extend(droppable)
        return kept, drops, notices

    for item in droppable:
        b = _item_bytes(item)
        if used + b <= cap:
            kept.append(item)
            used += b
        else:
            drops.append({
                "item_id": item.item_id, "unit": {"kind": item.unit_kind, "id": item.unit_id},
                "reason": "BUDGET", "score": item.fused_score, "bytes": b, "_section": "G",
                "tier": getattr(item, "tier", None),
            })
    return kept, drops, notices


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
                "tier": getattr(item, "tier", None),
            })
    return kept, drops


def apply_budgets(sections: dict, profile: BudgetProfile) -> tuple:
    """``sections``: ``{letter_or_subblock: [PacketItem, ...]}``, already fully assembled (pre-budget). Returns
    ``(sections_after, all_drops, blocked_budget, notices)``. Section A (and A alone) uses ``enforce_section_a``;
    D's three sub-blocks (D.1/D.2/D.3, if present) share ARCHITECTURE.md section 7.3's one "D" cap via
    ``enforce_combined``; G uses ``enforce_section_g`` (BR-AR-0015 reopening: T1 pinned/by-reference, T2/T3/T4
    dropped in tier order); every other section uses ``enforce_section``."""
    out: dict = {}
    all_drops: list = []
    blocked_budget = False
    notices: list = []

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
        if key == "G":
            kept, drops, g_notices = enforce_section_g(items, profile)
            notices.extend(g_notices)
        else:
            kept, drops = enforce_section(key, items, profile)
        out[key] = kept
        all_drops.extend(drops)

    return out, all_drops, blocked_budget, notices


def compact_drops(drops_list: list, compact_sections: tuple = ("G",)) -> dict:
    """BR-AR-0015 reopening, defect 4 ("drop records bloat the manifest" -- G's own drop list alone was 3.27 MB of
    the real demonstration packet's 6.1 MB manifest, because G alone can propose tens of thousands of T2/T3/T4
    candidates). Every section in ``compact_sections`` (G, by default -- the one section fan-out ever makes large)
    is grouped by ``(_section, tier)`` and each group replaced with a compact summary: a count, the sha256 of its
    SORTED dropped unit ids (newline-joined), and the first ``DROP_SAMPLE_LIMIT`` of those same sorted ids --
    never the full per-item list. Truncation stays fully recorded (every drop is counted and hashed), never
    silent; only the MANIFEST's own representation of a large drop list is bounded. Every OTHER section keeps its
    pre-reopening raw per-item drop list unchanged (``{item_id, unit, reason, score, bytes, tier}``) -- those
    sections never produce enough drops to matter, and node B6's own test_budget_pressure (one of the six named
    ARCHITECTURE.md section 5.3 invariant tests) asserts that exact raw shape for H. Returns
    ``{section: [...]}``."""
    groups: dict = {}
    for d in drops_list:
        key = (d.get("_section", "?"), d.get("tier"))
        groups.setdefault(key, []).append(d)

    out: dict = {}
    for (section, tier), items in groups.items():
        if section not in compact_sections:
            out.setdefault(section, []).extend({k: v for k, v in it.items() if k != "_section"} for it in items)
            continue
        ids = sorted(f"{it['unit']['kind']}:{it['unit']['id']}" for it in items)
        digest = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()
        out.setdefault(section, []).append({
            "tier": tier,
            "count": len(items),
            "bytes": sum(it.get("bytes", 0) for it in items),
            "dropped_ids_sha256": digest,
            "sample_ids": ids[:DROP_SAMPLE_LIMIT],
        })
    for section in compact_sections:
        if section in out:
            out[section].sort(key=lambda g: (g["tier"] or "", -g["count"]))
    return out


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
