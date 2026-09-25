"""BR-ARCH-RULING-1 (``GATES/BR-ARCH-RULING-1-MANDATORY-INPUTS-ALWAYS-IN-A.md``; run BR-AR-0013): section A
membership is decided by the resolver together with the class's admissibility in A -- never by lifecycle. A
mandatory item whose class is ladder-admissible in A (ranks 1-6) goes to A whatever its lifecycle, carrying a
lifecycle banner and a ``MANDATORY_LIFECYCLE_NOT_ACTIVE`` J notice when that lifecycle is not ACTIVE. Lifecycle
still gates D.1 and the non-ladder classes keep their fixed section regardless. Nothing here is Review-8/Phase-2
content (OC-BR-02): every id is CX-*, from the generic ``tests/fixtures/compile`` corpus.
"""
from govbridge.authority import classes as classesmod
from govbridge.compile import packet as packetmod
from govbridge.compile import validate as validatemod
from govbridge.route.router import RouteHit, RouteOccurrence, RouteSet


def _every_section_ids(manifest: dict) -> dict:
    out = {}
    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub, subsec in sec["subblocks"].items():
                out[sub] = [row["unit"]["id"] for row in subsec["items"]]
        else:
            out[letter] = [row["unit"]["id"] for row in sec["items"]]
    return out


def _probe_task_spec(view_path, task_spec_factory):
    return task_spec_factory(view_path, required_inputs=[
        {"state_ref": "state:bridge#mandatory_bridge_inputs.lifecycle_probe_items[*]", "reason": "BR-ARCH-RULING-1"},
    ])


def test_mandatory_unknown_lifecycle_lands_in_a_with_banner_and_notice(fixture_repo, view_path, registry_path,
                                                                          task_spec_factory):
    task_spec = _probe_task_spec(view_path, task_spec_factory)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    m = result["manifest"]
    by_section = _every_section_ids(m)

    # a mandatory CONTRACT item with lifecycle UNKNOWN lands in A -- never moved to H, never relabelled ACTIVE.
    assert "CX-CONTRACT-NO-STATUS" in by_section["A"]
    a_rows = {r["unit"]["id"]: r for r in m["sections"]["A"]["items"]}
    contract_row = a_rows["CX-CONTRACT-NO-STATUS"]
    assert contract_row["authority_class"] == "CONTRACT"
    assert contract_row["lifecycle"] == classesmod.LIFECYCLE_UNKNOWN
    assert contract_row["banner"] == packetmod.LIFECYCLE_BANNERS[classesmod.LIFECYCLE_UNKNOWN]

    # a mandatory ORCHESTRATION_RECORD item with lifecycle UNKNOWN also lands in A, same treatment.
    assert "CX-ORCH-RECORD-NO-STATUS" in by_section["A"]
    orch_row = a_rows["CX-ORCH-RECORD-NO-STATUS"]
    assert orch_row["authority_class"] == "ORCHESTRATION_RECORD"
    assert orch_row["lifecycle"] == classesmod.LIFECYCLE_UNKNOWN
    assert orch_row["banner"] == packetmod.LIFECYCLE_BANNERS[classesmod.LIFECYCLE_UNKNOWN]

    # neither UNKNOWN item ever reaches D.1 -- lifecycle still gates D.1 (ACTIVE only).
    assert "CX-CONTRACT-NO-STATUS" not in by_section["D.1"]
    assert "CX-ORCH-RECORD-NO-STATUS" not in by_section["D.1"]

    # a J notice names the gap for each, honestly, without erasing either item from A.
    notice_ids = {n["id"]: n for n in m["notices"] if n["type"] == "MANDATORY_LIFECYCLE_NOT_ACTIVE"}
    assert notice_ids["CX-CONTRACT-NO-STATUS"]["class"] == "CONTRACT"
    assert notice_ids["CX-CONTRACT-NO-STATUS"]["lifecycle"] == classesmod.LIFECYCLE_UNKNOWN
    assert notice_ids["CX-ORCH-RECORD-NO-STATUS"]["class"] == "ORCHESTRATION_RECORD"
    assert notice_ids["CX-ORCH-RECORD-NO-STATUS"]["lifecycle"] == classesmod.LIFECYCLE_UNKNOWN
    assert not any(n["type"] == "MANDATORY_ITEM_NOT_IN_A" for n in m["notices"]), \
        "MANDATORY_ITEM_NOT_IN_A must not fire for an A-admissible class -- it is unreachable now BR-ARCH-RULING-1 " \
        "applies; MANDATORY_LIFECYCLE_NOT_ACTIVE replaces it for this case"

    # a non-ladder mandatory item (OWNER_DIRECTION_TO_TEST) keeps its own fixed section, D.2, and never enters A --
    # BR-ARCH-RULING-1 rule 4 leaves the non-ladder classes unchanged.
    assert "CX-DIRECTION-NO-STATUS" in by_section["D.2"]
    for letter, ids in by_section.items():
        if letter != "D.2":
            assert "CX-DIRECTION-NO-STATUS" not in ids

    assert validatemod.verify_packet(m, task_spec, repo=str(fixture_repo.root), registry_path=registry_path) == []


def test_retrieved_item_never_lands_in_a_whatever_its_class_or_lifecycle():
    """``place_item`` is the ONE function that decides section membership (packet.py's module docstring); this
    exercises it directly for every A-admissible ladder class, at both ACTIVE and UNKNOWN lifecycle, for a
    RETRIEVED delivery (what every route hit carries -- ``govbridge.route.router.RouteHit.delivery`` is always
    ``RETRIEVED``/``DERIVED``, never ``MANDATORY``). BR-ARCH-RULING-1 loosens the MANDATORY branch only; a
    retrieved item must still never reach A."""
    a_admissible_ladder = [c.name for c in classesmod.LADDER if c.admissible_in_a]
    assert a_admissible_ladder, "the ladder must have at least one A-admissible class for this test to be meaningful"
    for cls in a_admissible_ladder:
        for lifecycle in (classesmod.LIFECYCLE_ACTIVE, classesmod.LIFECYCLE_UNKNOWN, classesmod.LIFECYCLE_SUPERSEDED):
            for delivery in ("RETRIEVED", "DERIVED"):
                section, also_d1 = packetmod.place_item(cls, lifecycle, delivery, "PROBE-UNIT", None)
                assert section != "A", f"{cls}/{lifecycle}/{delivery} reached A"
                assert also_d1 is False


def test_retrieved_hit_never_lands_in_a_through_a_full_compile(fixture_repo, view_path, registry_path,
                                                                  task_spec_factory):
    """The same invariant, end to end: a fused lexical hit claiming an A-admissible class and ACTIVE lifecycle is
    still never placed in A by a real compile."""
    occ = RouteOccurrence(ref="records", commit=fixture_repo.c2, path="spec/decisions/CX-0002.yaml",
                           version_status="CANONICAL")

    def fake_lexical(text=None, k=8, exclude=None, **kw):
        return [RouteHit(unit_id="CX-0002", unit_kind="record", route="lexical", rank=1, occurrences=(occ,),
                          text="a route hit, never authority", authority_class="ARCHITECTURE_DECISION",
                          lifecycle="ACTIVE")]

    routes = RouteSet(lexical=fake_lexical)
    task_spec = task_spec_factory(view_path, queries=[{"id": "q1", "text": "what governs the fixture rule exactly"}])
    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    a_ids = [it["unit"]["id"] for it in result["manifest"]["sections"]["A"]["items"]]
    assert "CX-0002" not in a_ids


def test_hand_moved_a_admissible_item_out_of_a_fails_verify(fixture_repo, view_path, registry_path,
                                                               task_spec_factory):
    """Validator negative control (BR-HO-0013): take a valid packet and, by hand, move a resolver A-admissible
    item OUT of A into H. ``packet verify`` (``validate.verify_packet``) must refuse it -- the re-derivation in
    ``verify_section_a`` recomputes A fresh via the (now fixed) ``place_item`` and finds the moved item missing."""
    task_spec = _probe_task_spec(view_path, task_spec_factory)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = result["manifest"]
    assert validatemod.verify_packet(manifest, task_spec, repo=str(fixture_repo.root),
                                      registry_path=registry_path) == []

    a_items = list(manifest["sections"]["A"]["items"])
    moved = next(r for r in a_items if r["unit"]["id"] == "CX-CONTRACT-NO-STATUS")
    remaining = [r for r in a_items if r is not moved]

    tampered = dict(manifest)
    tampered["sections"] = dict(manifest["sections"])
    tampered["sections"]["A"] = {**manifest["sections"]["A"], "items": remaining}
    tampered["sections"]["H"] = {**manifest["sections"]["H"],
                                  "items": list(manifest["sections"]["H"]["items"]) + [moved]}

    problems = validatemod.verify_packet(tampered, task_spec, repo=str(fixture_repo.root),
                                          registry_path=registry_path)
    assert problems, "moving an A-admissible mandatory item from A to H by hand must fail packet verify"
    assert any("section A does not equal" in p for p in problems)
