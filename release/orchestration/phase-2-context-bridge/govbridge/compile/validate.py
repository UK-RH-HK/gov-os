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
from govbridge.compile import render as rendermod
from govbridge.core.yamlutil import load_yaml_file, sha256_text


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
    """Recomputes the resolver from scratch and returns ``(expected_a_tuples, resolve_result, a_items)``. The
    tuples/items are in the SAME canonical order ``govbridge.compile.packet`` renders A in (ARCHITECTURE.md
    section 5.3 rule 5: ordered by authority rank, since every A item shares tier=MANDATORY and lifecycle=ACTIVE
    by construction). ``a_items`` (the raw ``MandatoryItem`` list) lets a caller (``verify_declared_and_delivered``)
    recompute a PER-ITEM declared span too, not just the tuple used for section-A membership/ordering.

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
    return expected, result, a_items


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
    expected, _, _ = recompute_section_a(task_spec, repo=repo, registry_path=registry_path,
                                          resolved_view=pinned_view)
    actual = _manifest_a_tuples(manifest)
    if expected != actual:
        return [f"section A does not equal the freshly recomputed resolver output (at the packet's own recorded "
                f"view {manifest.get('view')!r}): expected {len(expected)} item(s), packet has {len(actual)}; "
                f"expected={expected!r} actual={actual!r}"]
    return []


def _line_ranges(rows: list) -> list:
    return [(r.get("line_start"), r.get("line_end")) for r in rows]


def _tiles_exactly(declared_ranges: list, disclosed_ranges: list) -> bool:
    """True iff ``disclosed_ranges`` (a notice's ``delivered`` + ``undelivered_ranges``, combined) partitions the
    UNION of ``declared_ranges`` EXACTLY -- same total line coverage, no gaps, no overlaps. Line-set based (not
    merge-interval arithmetic) for a direct, hard-to-get-subtly-wrong implementation; mandatory items are bounded
    in size (the whole point of the per-item cap this checks around), so this is cheap in practice."""
    def _expand(ranges):
        s: set = set()
        for a, b in ranges:
            if a is None or b is None:
                continue
            s.update(range(a, b + 1))
        return s
    declared_set = _expand(declared_ranges)
    usable_disclosed = [(a, b) for a, b in disclosed_ranges if a is not None and b is not None]
    disclosed_set = _expand(usable_disclosed)
    if declared_set != disclosed_set:
        return False
    total = sum(b - a + 1 for a, b in usable_disclosed)
    return total == len(disclosed_set)  # equal iff no two disclosed ranges overlapped


def verify_declared_and_delivered(manifest: dict, a_items: list, repo: Optional[str] = None) -> list:
    """BR-DAG-AMEND reopening ("packet verify cannot detect silent truncation"): for every A item, recomputes
    ``declared_sha256``/``declared_bytes`` FRESH from Git at the packet's own recorded view (never trusts the
    stored value -- a compiler that cut a body could just as easily have written a wrong hash for the cut), then
    requires ONE of:

    (a) ``delivered_sha256 == declared_sha256`` (computed the SAME way -- ``resolver.hash_pieces`` over the exact
        same ordered raw pieces both times, so this is a real byte-level equality, not two different schemes that
        happen to look similar); or
    (b) a ``MANDATORY_PARTIAL_DELIVERY`` notice for that item whose ``delivered`` + ``undelivered_ranges``,
        combined, exactly TILE the declared span (every declared line accounted for exactly once -- no gaps, no
        overlaps), with every disclosed range's own sha256 independently re-verified against Git at the recorded
        view (never trusted from the notice itself).

    A directory item is skipped here (its declared form is the member manifest, checked by
    ``resolver.declared_regions``'s caller elsewhere -- ``is_directory``/``directory_members`` are already
    presence-checked structurally by the manifest schema itself)."""
    problems: list = []
    a_items_by_id = {mi.id: mi for mi in a_items}
    notices_by_id: dict = {}
    for n in (manifest.get("notices") or []):
        if n.get("type") == "MANDATORY_PARTIAL_DELIVERY":
            notices_by_id.setdefault(n.get("id"), []).append(n)

    for row in manifest["sections"]["A"]["items"]:
        uid = row["unit"]["id"]
        if row.get("is_directory"):
            continue
        mi = a_items_by_id.get(uid)
        if mi is None:
            problems.append(f"A/{uid}: not found in the freshly re-derived resolver output at the recorded view "
                             f"-- cannot verify declared_sha256")
            continue

        fresh_parts = resolvermod.declared_parts(mi, repo=repo)
        fresh_declared_sha256, fresh_declared_bytes = resolvermod.declared_hash_and_bytes(fresh_parts)

        if row.get("declared_sha256") != fresh_declared_sha256:
            problems.append(f"A/{uid}: declared_sha256 {row.get('declared_sha256')!r} does not match the source "
                             f"at the recorded view (recomputed {fresh_declared_sha256!r})")
            continue  # the stored value is already untrustworthy; nothing further to check against it
        if row.get("declared_bytes") != fresh_declared_bytes:
            problems.append(f"A/{uid}: declared_bytes {row.get('declared_bytes')!r} != recomputed "
                             f"{fresh_declared_bytes!r}")

        delivered_sha256 = row.get("delivered_sha256")
        if delivered_sha256 is not None and delivered_sha256 == fresh_declared_sha256:
            continue  # (a): full, honest delivery -- confirmed by an exact, independently-recomputed hash

        # (a) does not hold -- (b) is the only remaining honest possibility.
        item_notices = notices_by_id.get(uid) or []
        if not item_notices:
            problems.append(f"A/{uid}: delivered_sha256 {delivered_sha256!r} != declared_sha256 "
                             f"{fresh_declared_sha256!r}, and no MANDATORY_PARTIAL_DELIVERY notice explains the "
                             f"gap -- undisclosed truncation")
            continue

        notice = item_notices[0]
        declared_ranges = _line_ranges(fresh_parts)
        disclosed = list(notice.get("delivered") or []) + list(notice.get("undelivered_ranges") or [])
        disclosed_ranges = _line_ranges(disclosed)
        if not _tiles_exactly(declared_ranges, disclosed_ranges):
            problems.append(f"A/{uid}: MANDATORY_PARTIAL_DELIVERY notice's delivered+undelivered ranges do not "
                             f"exactly tile the declared span {declared_ranges} (a gap or an overlap) -- "
                             f"disclosed={disclosed_ranges}")
            continue

        for d in disclosed:
            d_path = d.get("path") or notice.get("path")
            d_commit = d.get("commit") or notice.get("commit")
            text = resolvermod._read_git_slice(d_path, d_commit, d.get("line_start"), d.get("line_end"), repo=repo)
            if text is None:
                problems.append(f"A/{uid}: disclosed range {d.get('name')!r} ({d_path}@{d_commit}:"
                                 f"{d.get('line_start')}-{d.get('line_end')}) could not be re-read from Git at "
                                 f"the recorded view")
                continue
            actual = sha256_text(text)
            if d.get("sha256") != actual:
                problems.append(f"A/{uid}: disclosed range {d.get('name')!r} sha256 {d.get('sha256')!r} != "
                                 f"recomputed {actual!r} at the recorded view")
    return problems


def _composition_context_class(packetmod):
    """Builds a minimal ``govbridge.compile.packet.Compiler`` SUBCLASS whose ``__init__`` skips all the real,
    expensive work the real one does (view/registry resolution, task-context setup, ...) and sets only the three
    attributes ``Compiler._mandatory_text`` -- and the private per-shape renderers it dispatches to
    (``_render_selected_parts``/``_render_oversize_no_selector``/``_render_directory_manifest``) -- actually read:
    ``repo``, ``per_item_cap_bytes`` and ``notices`` (a scratch list; its informational appends, e.g. the
    keys/entries "here is what else exists" disclosure, are discarded -- this module only wants the returned
    TEXT). It MUST be a real subclass, never a duck-typed stand-in: those private methods call ``self.
    _render_whatever(...)`` internally, which Python resolves through the instance's actual class -- a plain
    object with the same three attributes has no such method to find. Built lazily, inside this function, so
    ``govbridge.compile.packet`` (already imported lazily by every caller, to avoid a module-load-time
    circular import) never needs a module-level import here either. Nothing here reimplements packet.py's own
    composition, and packet.py itself is never edited (R1-GA3 is its next editor)."""

    class _CompositionContext(packetmod.Compiler):
        def __init__(self, repo: Optional[str], per_item_cap_bytes: int):  # noqa: super().__init__ deliberately
            self.repo = repo                                               # never called -- it does real work
            self.per_item_cap_bytes = per_item_cap_bytes                   # (view/registry resolution) this
            self.notices: list = []                                        # module must never trigger.

    return _CompositionContext


def _per_item_cap_bytes(manifest: dict, budgets_path: Optional[str]) -> int:
    """The per-item cap the ORIGINAL compile used, re-derived the same way ``govbridge.compile.budgets`` itself
    does (``config/budgets.yaml``'s ``per_item_cap_kb``, a document-level setting shared by every profile --
    never profile-specific), so an oversize/no-selector item's recomposed section-map header text
    ("exceeds the N-byte per-item cap") matches exactly. Falls back to the documented default (24 KB) only if no
    budget_profile is recorded at all (a manifest built before that field existed)."""
    from govbridge.compile import budgets as budgetsmod

    profile_name = manifest.get("budget_profile")
    if not profile_name:
        return 24 * 1024
    return budgetsmod.load_profile(profile_name, path=budgets_path).per_item_cap_bytes


def verify_rendered_delivery(manifest: dict, rendered: str, a_items: list, repo: Optional[str] = None,
                              budgets_path: Optional[str] = None) -> list:
    """BR-DAG-AMEND-R1-10 (routed from BR-AR-0022's open issue; reopened on BR-AR-0025 pass 1 for not being EXACT
    for every shape): independently re-extracts each A item's DELIVERED BODY from the RENDERED packet text itself
    (``govbridge.compile.render.extract_item_delivered_body`` -- never trusts anything the manifest claims about
    what was delivered), INDEPENDENTLY RECOMPOSES the body that item should have (from Git, at the packet's own
    recorded view, via ``resolver.declared_parts`` and ``packet.Compiler._mandatory_text`` -- the SAME composition
    function the compiler itself calls, imported read-only; ``govbridge/compile/packet.py`` is never edited by
    this node), and requires the two to be EXACTLY equal, for every one of the four shapes ``_mandatory_text``
    produces:

    * a directory item's member manifest;
    * a keys/entries/paths-selector item's piece headers plus pieces;
    * an oversize/no-selector item's section map plus its ``MANDATORY_PARTIAL_DELIVERY`` disclosure text;
    * the plain, whole-occurrence body (delivered in full, the common RC-1-relevant case).

    An exact string comparison over the FULL composed body catches content inserted anywhere within it (between
    two selector pieces, inside a section-map line, an extra directory-manifest member line, ...) -- never only a
    hash of the whole item or a containment check over a subset of it, both of which a sufficiently placed
    insertion could survive."""
    from govbridge.compile import packet as packetmod

    composition_context_cls = _composition_context_class(packetmod)
    problems: list = []
    a_items_by_id = {mi.id: mi for mi in a_items}
    per_item_cap_bytes = _per_item_cap_bytes(manifest, budgets_path)

    for row in manifest["sections"]["A"]["items"]:
        uid = row["unit"]["id"]
        unit_kind = row["unit"]["kind"]
        mi = a_items_by_id.get(uid)
        if mi is None:
            problems.append(f"A/{uid}: not found in the freshly re-derived resolver output at the recorded view "
                             f"-- cannot independently recompose its expected body")
            continue

        found, body, ambiguous = rendermod.extract_item_delivered_body(rendered, "A", unit_kind, uid)
        if ambiguous:
            problems.append(f"A/{uid}: more than one delivered-body marker pair for this item in the rendered "
                             f"packet's section A -- cannot unambiguously re-extract")
            continue
        if not found:
            problems.append(f"A/{uid}: no delivered-body marker pair found for this item in the rendered "
                             f"packet's section A -- the renderer did not emit it")
            continue

        # the SAME independent third measurement verify_declared_and_delivered already takes (fresh from Git,
        # never trusting the row's own declared_parts) -- reused here rather than recomputed a second, possibly
        # diverging way.
        dparts = resolvermod.declared_parts(mi, repo=repo)
        ctx = composition_context_cls(repo=repo, per_item_cap_bytes=per_item_cap_bytes)
        expected_text, _ = ctx._mandatory_text(mi, dparts)
        expected_body = (expected_text or "").rstrip("\n")

        if body != expected_body:
            problems.append(
                f"A/{uid}: the body re-extracted from the RENDERED packet does not EXACTLY match the "
                f"independently recomposed expected body (Git at the recorded view, via "
                f"packet.Compiler._mandatory_text) -- the renderer may have dropped, altered or had content "
                f"inserted into it. rendered={body!r} expected={expected_body!r}")
    return problems


def verify_supplementary_packet(manifest: dict) -> list:
    """A supplementary packet (REPAIR_PLAN.md section 2.9, node R1-RS) carries retrieval EVIDENCE only -- never
    authority. It has no real section A (there is no task-spec-shaped resolver run for a bare query command's own
    JSON result to re-derive against), so ``verify_section_a`` does not apply to it; every OTHER structural check
    still does (placement, banners, ordering), PLUS a hard refusal of any MANDATORY/PINNED item and of a non-empty
    section A -- a supplementary packet must never carry, or be mistaken for, authority."""
    problems: list = []
    if manifest["sections"]["A"]["items"]:
        problems.append("supplementary packet section A is non-empty -- authority never enters a supplementary "
                         "packet")
    for section, row in _rows_of(manifest):
        if row["delivery"] in ("MANDATORY", "PINNED"):
            problems.append(f"{section}/{row['item_id']}: delivery {row['delivery']!r} in a supplementary packet "
                             f"-- supplementary packets carry RETRIEVED/DERIVED evidence only")
    problems += verify_placement(manifest)
    problems += verify_banners(manifest)
    problems += verify_ordering(manifest)
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
                   registry_path: Optional[str] = None, rendered: Optional[str] = None,
                   budgets_path: Optional[str] = None) -> list:
    """Every check this module knows, combined. An empty list means the packet is valid.

    ``rendered`` (BR-DAG-AMEND-R1-10): the packet's own rendered ``packet.md`` TEXT, when the caller has it (every
    CLI path does -- ``govbridge packet verify DIR``/``govbridge receipt check`` both read it off disk alongside
    ``manifest.json``). When given, ``verify_rendered_delivery`` independently RECOMPOSES each A item's expected
    body from Git (at the recorded view) and compares it EXACTLY against what the rendered bytes actually
    contain -- catching a renderer that drops, alters or has content inserted into it, for every mandatory-item
    shape (directory, selector, oversize/section-map, and the plain whole-occurrence body) -- something no other
    check here can see, since every other check reads only the manifest. ``None`` only for a caller with no
    rendered text at all (a pre-existing direct unit-test call of this function); such a caller does not get the
    R1-10 guarantee, so a new caller should always pass it. ``budgets_path`` lets that recomposition use the SAME
    ``config/budgets.yaml`` the original compile did, when it was not the default one."""
    problems = []
    problems += verify_section_a(manifest, task_spec, repo=repo, registry_path=registry_path)
    problems += verify_placement(manifest)
    problems += verify_banners(manifest)
    problems += verify_ordering(manifest)
    # BR-DAG-AMEND reopening: recompute at the packet's OWN recorded view (never live), same as verify_section_a.
    pinned_view = pinned_view_from_manifest(manifest, task_spec, repo=repo)
    _, _, a_items = recompute_section_a(task_spec, repo=repo, registry_path=registry_path,
                                         resolved_view=pinned_view)
    problems += verify_declared_and_delivered(manifest, a_items, repo=repo)
    if rendered is not None:
        problems += verify_rendered_delivery(manifest, rendered, a_items, repo=repo, budgets_path=budgets_path)
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
    problems = verify_packet(result["manifest"], task_spec, registry_path=result["registry_path"],
                              rendered=result["rendered"])
    print(json.dumps({"status": "VALID" if not problems else "INVALID", "problems": problems}, indent=1,
                      sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
