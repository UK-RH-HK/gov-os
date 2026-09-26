#!/usr/bin/env python3
"""The independent validator (ARCHITECTURE.md section 5.3 rule 4): recomputes ``govbridge.authority.resolver``
**from scratch** and refuses a packet whose section A differs, in order and in every field. It also checks the
placement admissibility of every item in every section, that every mandatory class banner is present (and, per
BR-ARCH-RULING-1, that every non-ACTIVE A item carries its lifecycle banner), and the ordering invariant of rule 5
(no item with a worse ``(rank, lifecycle)`` precedes a better one).

BR-ARCH-RULING-1: section A membership is decided by the resolver together with the class's admissibility in A --
never by lifecycle. ``verify_section_a``'s re-derivation already enforces this (it re-derives A through
``packet.place_item``, the single fixed function), so a resolver-returned, A-admissible item placed anywhere other
than A now fails re-derivation; ``verify_placement`` no longer refuses a non-ACTIVE lifecycle inside A.

This is a SEPARATE module from ``packet.py``: the compiler, ``packet verify``, the receipt checker
(``receipt.py``) and any grader all call INTO this module; nothing here imports ``packet.py`` at module load time
(only lazily, inside two functions, to read ``place_item``/``sort_key``/``LIFECYCLE_BANNERS`` without a circular
import at import time).
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.authority import records as recordsmod
from govbridge.authority import resolver as resolvermod
from govbridge.core.yamlutil import load_yaml_file


def _a_tuple(mi_id, cls, lifecycle, commit, path, blob, l1, l2, sha256) -> tuple:
    return (mi_id, cls, lifecycle, commit, path, blob, l1, l2, sha256)


def pinned_view_from_manifest(manifest: dict, task_spec: dict, repo: Optional[str] = None):
    """BR-DAG-AMEND-R1-1: reconstructs the resolved view EXACTLY as this packet's own manifest recorded it --
    every named ref pinned to the exact commit ``manifest['view']`` lists, never re-resolved at the repository's
    moving tip. This is what lets a stored packet stay re-verifiable at any LATER time (ARCHITECTURE.md section
    5.3 rule 4), even after a new mandatory record has since been committed to the same ref -- the exact failure
    the R1-RG quarantined check hit ("packet verify re-derives section A at the CURRENT tip: 24 expected vs 20 --
    OD-BR-03..06 became mandatory after run-1").

    ``history`` (a ``ref_glob`` of many equally-historical tips, never one designated ref) is not itemised in
    ``manifest['view']`` and is left un-pinned here; mandatory-item resolution reaches it only through a
    partition's fallback chain when a path is absent from every named ref, a rare path this amendment's own
    regression test does not exercise. Every NAMED ref the manifest recorded is pinned."""
    from govbridge.core import view as viewmod

    view_path = task_spec["view"]
    if not os.path.isabs(view_path) and not os.path.exists(view_path):
        from govbridge import GOV_BRIDGE_DOMAIN
        view_path = os.path.join(GOV_BRIDGE_DOMAIN, view_path)
    config = viewmod.load_view(view_path)
    named = {row["name"]: viewmod.ResolvedRef(name=row["name"], commit=row["commit"], status=viewmod.REF_OK)
             for row in (manifest.get("view") or []) if row.get("commit")}
    return viewmod.ResolvedView(view_id=config.view_id, config=config, named=named, history=[], repo=repo)


def recompute_section_a(task_spec: dict, repo: Optional[str] = None,
                         registry_path: Optional[str] = None, resolved_view=None) -> tuple:
    """Recomputes the resolver from scratch and returns ``(expected_a_tuples, resolve_result)``. The tuples are in
    the SAME canonical order ``govbridge.compile.packet`` renders A in (ARCHITECTURE.md section 5.3 rule 5: ordered
    by authority rank, since every A item shares tier=MANDATORY and lifecycle=ACTIVE by construction).

    ``resolved_view``, when given, overrides live resolution (BR-DAG-AMEND-R1-1: ``verify_section_a`` below always
    passes the packet's OWN recorded view; a caller that wants today's live-tip behaviour -- there is none left in
    this package -- would omit it)."""
    from govbridge.compile import packet as packetmod  # lazy: avoid a module-load-time circular import

    grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
    result = resolvermod.resolve(task_spec, repo=repo, registry_path=registry_path, resolved_view=resolved_view)
    a_items = []
    for mi in result.items:
        if not isinstance(mi, resolvermod.MandatoryItem):
            continue
        section, _ = packetmod.place_item(mi.cls, mi.lifecycle, packetmod.delivery_for_mandatory(mi.cls), mi.id,
                                           grammar)
        if section == "A":
            a_items.append(mi)
    a_items.sort(key=lambda mi: packetmod.sort_key(packetmod.PacketItem(
        unit_kind="record", unit_id=mi.id, section="A", delivery="MANDATORY", cls=mi.cls, lifecycle=mi.lifecycle,
        version_status=None, ref=None, commit=mi.commit, path=mi.path, blob=mi.blob, line_start=mi.line_start,
        line_end=mi.line_end, text="", content_sha256=None, by_reference=False, route="resolver", raw_score=None,
        rank=None, fused_score=None, edge_path=(), reason=None, banner=None,
    )))
    expected = [_a_tuple(mi.id, mi.cls, mi.lifecycle, mi.commit, mi.path, mi.blob, mi.line_start, mi.line_end,
                          mi.sha256) for mi in a_items]
    return expected, result


def _manifest_a_tuples(manifest: dict) -> list:
    rows = manifest["sections"]["A"]["items"]
    out = []
    for r in rows:
        src = r["source"]
        out.append(_a_tuple(r["unit"]["id"], r["authority_class"], r["lifecycle"], src["commit"], src["path"],
                             src["blob"], src["line_start"], src["line_end"], r["content_sha256"]))
    return out


def verify_section_a(manifest: dict, task_spec: dict, repo: Optional[str] = None,
                      registry_path: Optional[str] = None) -> list:
    """BR-DAG-AMEND-R1-1: re-derives section A at the VIEW RECORDED IN THIS PACKET'S OWN MANIFEST (pinned
    refs/commits), never at the repository's moving tip -- so a stored packet stays re-verifiable at any later
    time, even after a new mandatory record has since been committed to the same ref."""
    pinned_view = pinned_view_from_manifest(manifest, task_spec, repo=repo)
    expected, _ = recompute_section_a(task_spec, repo=repo, registry_path=registry_path, resolved_view=pinned_view)
    actual = _manifest_a_tuples(manifest)
    if expected != actual:
        return [f"section A does not equal the freshly recomputed resolver output (at the packet's own recorded "
                f"view {manifest.get('view')!r}): expected {len(expected)} item(s), packet has {len(actual)}; "
                f"expected={expected!r} actual={actual!r}"]
    return []


def verify_delivered_fidelity(manifest: dict) -> list:
    """BR-DAG node R1-RM (REPAIR_PLAN.md section 3 rule 4): "the receipt acknowledges delivered_sha256 separately
    from source_sha256... must not appear to acknowledge content that was never delivered." The concrete
    historical failure (run-1, ``DEMONSTRATION/run-1/receipt.yaml``): a by-reference A item carried NO recorded
    hash at all, so a receipt could only acknowledge it as the degenerate ``"ID@None"``. Every A item must
    therefore carry a non-None ``source_sha256`` (a directory item's is now derived from its own member manifest --
    ``resolver.py`` -- rather than left ``None`` when the row declares no explicit hash) and a non-None
    ``delivered_sha256`` for whatever this packet actually placed in that item's body.

    This deliberately does NOT assert ``source_sha256 == delivered_sha256``: an ANCHORED item's source_sha256 is
    the whole occurrence's file-level integrity hash (ARCHITECTURE.md section 5.3 rule 4's own re-derivation keys
    on exactly that), while its delivered_sha256 is the hash of its own anchored slice -- the two legitimately
    differ for every anchored mandatory item, whole-file or not, and that is not a fidelity gap."""
    problems = []
    for row in manifest["sections"]["A"]["items"]:
        if row.get("source_sha256") is None:
            problems.append(f"A/{row['unit']['id']}: source_sha256 is missing -- inputs_consumed could only "
                             f"acknowledge this item as '{row['unit']['id']}@None'")
        if row.get("delivered_sha256") is None:
            problems.append(f"A/{row['unit']['id']}: delivered_sha256 is missing -- the receipt cannot honestly "
                             f"acknowledge what this packet actually delivered")
    return problems


def _rows_of(manifest: dict) -> list:
    """``[(section_label, row), ...]`` across every section, D's three sub-blocks counted as their own labels."""
    out = []
    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub, subsec in sec["subblocks"].items():
                out.extend((sub, row) for row in subsec["items"])
        else:
            out.extend((letter, row) for row in sec["items"])
    return out


def verify_placement(manifest: dict) -> list:
    """Every item's section is admissible for its (class, lifecycle, delivery) -- ARCHITECTURE.md section 5.1/5.3."""
    problems = []
    for section, row in _rows_of(manifest):
        cls, lifecycle, delivery = row["authority_class"], row["lifecycle"], row["delivery"]
        spec = classesmod.ALL_CLASSES.get(cls)

        if section == "A":
            if delivery != "MANDATORY":
                problems.append(f"A/{row['item_id']}: delivery {delivery!r} != MANDATORY")
            if spec is None or not spec.ladder or not spec.admissible_in_a:
                problems.append(f"A/{row['item_id']}: class {cls!r} is not admissible in A")
            # BR-ARCH-RULING-1: lifecycle no longer decides A membership -- a mandatory, A-admissible item stays
            # in A whatever its lifecycle (was: "lifecycle != ACTIVE" refused here). Its lifecycle must still be
            # honest: verify_banners checks that a non-ACTIVE A item carries its lifecycle banner.
            continue

        if section == "D.1":
            if lifecycle != classesmod.LIFECYCLE_ACTIVE:
                problems.append(f"D.1/{row['item_id']}: lifecycle {lifecycle!r} != ACTIVE")
            if cls not in ("OWNER_DECISION", "ARCHITECTURE_DECISION", "ORCHESTRATION_RECORD"):
                problems.append(f"D.1/{row['item_id']}: class {cls!r} is not D.1-admissible")
            continue

        if section == "D.2" and cls != "OWNER_DIRECTION_TO_TEST":
            problems.append(f"D.2/{row['item_id']}: class {cls!r} != OWNER_DIRECTION_TO_TEST")
        if section == "D.3" and cls != "HYPOTHESIS_TO_TEST":
            problems.append(f"D.3/{row['item_id']}: class {cls!r} != HYPOTHESIS_TO_TEST")

        if spec is not None and not spec.ladder:
            allowed = set(spec.allowed_sections) | ({"E"} if cls == "EVIDENCE_WITHDRAWN" else set())
            if section not in allowed:
                problems.append(f"{section}/{row['item_id']}: class {cls!r} not allowed in {section} "
                                 f"(allowed: {sorted(allowed)})")
    return problems


def verify_banners(manifest: dict) -> list:
    """Every PINNED non-ladder item carries its mandatory class banner verbatim (ARCHITECTURE.md section 5.1).
    Every A item whose lifecycle is not ACTIVE carries its lifecycle banner verbatim (BR-ARCH-RULING-1 rule 2:
    "lifecycle stays visible and honest... carries a lifecycle banner")."""
    from govbridge.compile import packet as packetmod  # lazy: avoid a module-load-time circular import

    problems = []
    for section, row in _rows_of(manifest):
        if section == "A" and row["lifecycle"] != classesmod.LIFECYCLE_ACTIVE:
            expected = packetmod.LIFECYCLE_BANNERS.get(row["lifecycle"])
            if expected is not None and row.get("banner") != expected:
                problems.append(f"A/{row['item_id']}: lifecycle banner {row.get('banner')!r} != {expected!r}")

        if row["delivery"] != "PINNED":
            continue
        spec = classesmod.ALL_CLASSES.get(row["authority_class"])
        if spec is not None and spec.banner and row.get("banner") != spec.banner:
            problems.append(f"{section}/{row['item_id']}: banner {row.get('banner')!r} != {spec.banner!r}")
    return problems


def _rank_lifecycle_tier(row: dict) -> tuple:
    spec = classesmod.ALL_CLASSES.get(row["authority_class"])
    rank = spec.rank if (spec is not None and spec.ladder) else len(classesmod.LADDER) + 1
    try:
        lc = classesmod.LIFECYCLE_ORDER.index(row["lifecycle"])
    except ValueError:
        lc = len(classesmod.LIFECYCLE_ORDER) - 1
    tier = 0 if row["delivery"] in ("MANDATORY", "PINNED") else 1
    return tier, rank, lc


def verify_ordering(manifest: dict) -> list:
    """ARCHITECTURE.md section 5.3 rule 5: "no item with a worse (rank, lifecycle) precedes a better one"; fused
    score may only reorder items that already share the same (tier, rank, lifecycle)."""
    problems = []
    by_section: dict = {}
    for section, row in _rows_of(manifest):
        by_section.setdefault(section, []).append(row)
    for section, rows in by_section.items():
        for a, b in zip(rows, rows[1:]):
            if _rank_lifecycle_tier(a) > _rank_lifecycle_tier(b):
                problems.append(f"{section}: order inverted -- {a['item_id']} ({_rank_lifecycle_tier(a)}) precedes "
                                 f"{b['item_id']} ({_rank_lifecycle_tier(b)})")
    return problems


def verify_packet(manifest: dict, task_spec: dict, repo: Optional[str] = None,
                   registry_path: Optional[str] = None) -> list:
    """Every check this module knows, combined. An empty list means the packet is valid."""
    problems = []
    problems += verify_section_a(manifest, task_spec, repo=repo, registry_path=registry_path)
    problems += verify_placement(manifest)
    problems += verify_banners(manifest)
    problems += verify_ordering(manifest)
    problems += verify_delivered_fidelity(manifest)
    return problems


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.compile.validate")
    p.add_argument("task_spec")
    p.add_argument("--fake-routes", action="store_true")
    p.add_argument("--registry")
    p.add_argument("--budgets")
    args = p.parse_args(argv)

    from govbridge.compile import packet as packetmod
    task_spec = load_yaml_file(args.task_spec)
    result = packetmod.compile_packet(task_spec, routes=packetmod.FAKE_ROUTES, registry_path=args.registry,
                                       budgets_path=args.budgets)
    problems = verify_packet(result["manifest"], task_spec, registry_path=result["registry_path"])
    print(json.dumps({"status": "VALID" if not problems else "INVALID", "problems": problems}, indent=1,
                      sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
