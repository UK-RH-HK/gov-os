"""The hard authority invariant (ARCHITECTURE.md section 5.3; node B6 acceptance): section A is filled ONLY by the
resolver, checked with isinstance; a superseded record that is the top hit of every route is never placed in D.1;
no line outside an anchored section of the disposition fixture is ever delivered as OWNER_DECISION.
"""
from govbridge.compile import packet as packetmod
from govbridge.compile import validate as validatemod
from govbridge.route.router import RouteHit, RouteOccurrence, RouteSet


def _rogue_packet_item(section="A"):
    return packetmod.PacketItem(
        unit_kind="record", unit_id="ROGUE-RETRIEVED", section=section, delivery="RETRIEVED",
        cls="ARCHITECTURE_DECISION", lifecycle="ACTIVE", version_status=None, ref=None, commit=None, path=None,
        blob=None, line_start=None, line_end=None, text="a route hit pretending to be authority",
        content_sha256=None, by_reference=False, route="lexical", raw_score=None, rank=1, fused_score=9.0,
        edge_path=(), reason=None, banner=None,
    )


def test_retrieved_cannot_enter_a(fixture_repo, view_path, registry_path, task_spec_factory):
    """``Compiler.add`` refuses section "A" outright -- only ``add_to_a`` may fill it, and it isinstance-checks."""
    task_spec = task_spec_factory(view_path)
    routes = RouteSet()
    c = packetmod.Compiler(task_spec, routes, str(fixture_repo.root), view_path, registry_path, 60, 1)

    rogue = _rogue_packet_item()
    try:
        c.add({"A": []}, "A", rogue)
        assert False, "Compiler.add accepted a RETRIEVED item into section A"
    except packetmod.SectionAViolation:
        pass

    try:
        c.add_to_a({"A": []}, rogue)  # rogue is a PacketItem, not a MandatoryItem -- must raise
        assert False, "Compiler.add_to_a accepted a non-MandatoryItem"
    except packetmod.SectionAViolation:
        pass


def test_hand_edited_packet_with_extra_a_item_fails_verify(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = result["manifest"]

    # a valid, freshly-compiled packet has no problems...
    assert validatemod.verify_packet(manifest, task_spec, repo=str(fixture_repo.root),
                                      registry_path=registry_path) == []

    # ...but a HAND-EDITED packet with one extra A item does.
    tampered = dict(manifest)
    tampered["sections"] = dict(manifest["sections"])
    tampered["sections"]["A"] = dict(manifest["sections"]["A"])
    extra_row = dict(manifest["sections"]["A"]["items"][0])
    extra_row = {**extra_row, "item_id": "hand-edited-extra-item"}
    tampered["sections"]["A"]["items"] = list(manifest["sections"]["A"]["items"]) + [extra_row]

    problems = validatemod.verify_packet(tampered, task_spec, repo=str(fixture_repo.root),
                                          registry_path=registry_path)
    assert problems, "an extra, hand-edited A item must fail packet verify"
    assert any("section A does not equal" in p for p in problems)


def test_semantic_trap(fixture_repo, view_path, registry_path, task_spec_factory):
    """A superseded record (CX-0001) that is the TOP hit of both lexical and semantic is never placed in D.1,
    appears only in E with its lifecycle banner, and sorts below the active record (CX-0002) wherever both would
    otherwise be compared."""
    occ = RouteOccurrence(ref="records", commit=fixture_repo.c2, path="spec/decisions/CX-0001.yaml",
                           version_status="CANONICAL")

    def fake_lexical(text=None, k=8, exclude=None, **kw):
        return [RouteHit(unit_id="CX-0001", unit_kind="record", route="lexical", rank=1, occurrences=(occ,),
                          text="CX-0001 is a strong lexical/semantic match", authority_class="ARCHITECTURE_DECISION",
                          lifecycle="SUPERSEDED")]

    def fake_semantic(text=None, k=8, exclude=None, **kw):
        return [RouteHit(unit_id="CX-0001", unit_kind="record", route="semantic", rank=1, occurrences=(occ,),
                          text="CX-0001 is a strong lexical/semantic match", authority_class="ARCHITECTURE_DECISION",
                          lifecycle="SUPERSEDED")]

    routes = RouteSet(lexical=fake_lexical, semantic=fake_semantic)
    task_spec = task_spec_factory(
        view_path, seeds=["CX-0001"],
        queries=[{"id": "q1", "text": "what replaces the fixture rule for CX-0001 exactly"}])
    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    m = result["manifest"]

    d1_ids = [it["unit"]["id"] for it in m["sections"]["D"]["subblocks"]["D.1"]["items"]]
    assert "CX-0001" not in d1_ids, "a SUPERSEDED record must never enter D.1"

    e_rows = {it["unit"]["id"]: it for it in m["sections"]["E"]["items"]}
    assert "CX-0001" in e_rows, "the superseded record must appear in E"
    assert e_rows["CX-0001"]["lifecycle"] == "SUPERSEDED"
    assert e_rows["CX-0001"]["banner"], "E's superseded item must carry its lifecycle banner"

    for letter in ("A", "D"):
        if letter == "D":
            all_ids = [it["unit"]["id"] for sub in m["sections"]["D"]["subblocks"].values() for it in sub["items"]]
        else:
            all_ids = [it["unit"]["id"] for it in m["sections"][letter]["items"]]
        assert "CX-0001" not in all_ids, f"CX-0001 must never reach {letter}"

    assert validatemod.verify_packet(m, task_spec, repo=str(fixture_repo.root), registry_path=registry_path) == []


def test_section_scoping(fixture_repo, view_path, registry_path, task_spec_factory):
    """No line of the shared disposition file outside an anchored item's section is ever delivered as
    OWNER_DECISION (or any other class) -- ARCHITECTURE.md section 5.2 rule 1."""
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    m = result["manifest"]

    disposition_path = "release/orchestration/cx/GATES/OWNER-DECISION-CX-0010A-B-DISPOSITION.md"
    a_rows = m["sections"]["A"]["items"]
    by_id = {r["unit"]["id"]: r for r in a_rows}

    assert by_id["CX-0010A"]["source"]["line_start"] == 9
    assert by_id["CX-0010A"]["source"]["line_end"] == 12
    assert by_id["CX-0010B"]["source"]["line_start"] == 13
    assert by_id["CX-0010B"]["source"]["line_end"] == 16
    # the two anchored A items never overlap, and neither spans the whole file (lines 1-6 -- the header table
    # before the first heading -- are UNCLASSIFIED per the registry's unanchored_lines_rule, never OWNER_DECISION).
    assert by_id["CX-0010A"]["source"]["path"] == disposition_path
    spans = [(r["source"]["line_start"], r["source"]["line_end"]) for r in a_rows
             if r["source"]["path"] == disposition_path]
    assert len(set(spans)) == len(spans), "every anchored item resolves to its own distinct span"
    for s, e in spans:
        assert not (s <= 1 <= e or s <= 6 <= e), "no anchored span reaches back into the unanchored header"
