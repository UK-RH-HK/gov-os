"""``test_mandatory_bridge_inputs_classes`` (node B6 acceptance, fixture view -- OC-BR-02: this test uses only the
generic ``tests/fixtures/compile`` corpus, never a Review-8 id). Every ``mandatory_bridge_inputs`` item appears in
its expected section with its exact class and banner: the two OWNER_DECISION items are in A and D.1; the
OWNER_DIRECTION_TO_TEST item is only in D.2; the HYPOTHESIS_TO_TEST item only in D.3;
HYPOTHESIS_RELEVANT_OBSERVATION only in F, and never adjacent to D.3 as support; the EVIDENCE_WITHDRAWN item only in
F (its PINNED delivery), with lifecycle WITHDRAWN.
"""
from govbridge.compile import packet as packetmod
from govbridge.compile import validate as validatemod
from govbridge.route.router import RouteSet


def _every_section_ids(manifest: dict) -> dict:
    out = {}
    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub, subsec in sec["subblocks"].items():
                out[sub] = [row["unit"]["id"] for row in subsec["items"]]
        else:
            out[letter] = [row["unit"]["id"] for row in sec["items"]]
    return out


def test_mandatory_bridge_inputs_classes(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    m = result["manifest"]
    by_section = _every_section_ids(m)

    # the two OWNER_DECISION items: in A, and referenced in D.1.
    assert "CX-0010A" in by_section["A"]
    assert "CX-0010B" in by_section["A"]
    assert "CX-0010A" in by_section["D.1"]
    assert "CX-0010B" in by_section["D.1"]
    for letter in ("D.2", "D.3", "E", "F", "H"):
        assert "CX-0010A" not in by_section[letter]
        assert "CX-0010B" not in by_section[letter]

    a_rows = {r["unit"]["id"]: r for r in m["sections"]["A"]["items"]}
    assert a_rows["CX-0010A"]["authority_class"] == "OWNER_DECISION"
    assert a_rows["CX-0010A"]["lifecycle"] == "ACTIVE"

    # OWNER_DIRECTION_TO_TEST: only in D.2.
    assert "CX-DIRECTION" in by_section["D.2"]
    for letter, ids in by_section.items():
        if letter != "D.2":
            assert "CX-DIRECTION" not in ids
    d2_row = m["sections"]["D"]["subblocks"]["D.2"]["items"][0]
    assert d2_row["authority_class"] == "OWNER_DIRECTION_TO_TEST"
    assert d2_row["banner"] == "OWNER DIRECTION TO TEST: NOT YET AUTHORITY. The synthesis tests it and may reject it."

    # HYPOTHESIS_TO_TEST: only in D.3.
    assert "CX-HYPOTHESIS" in by_section["D.3"]
    for letter, ids in by_section.items():
        if letter != "D.3":
            assert "CX-HYPOTHESIS" not in ids
    d3_row = m["sections"]["D"]["subblocks"]["D.3"]["items"][0]
    assert d3_row["authority_class"] == "HYPOTHESIS_TO_TEST"
    assert d3_row["banner"] == \
        "HYPOTHESIS TO TEST: NO CLASSIFICATORY FORCE. The bridge makes it testable and does not answer it."

    # HYPOTHESIS_RELEVANT_OBSERVATION: only in F, never adjacent to D.3 as support (i.e. never IN D.3 at all).
    assert "CX-REASONING-OBSERVATION" in by_section["F"]
    assert "CX-REASONING-OBSERVATION" not in by_section["D.3"]
    for letter, ids in by_section.items():
        if letter != "F":
            assert "CX-REASONING-OBSERVATION" not in ids
    f_rows = {r["unit"]["id"]: r for r in m["sections"]["F"]["items"]}
    assert f_rows["CX-REASONING-OBSERVATION"]["authority_class"] == "HYPOTHESIS_RELEVANT_OBSERVATION"
    assert f_rows["CX-REASONING-OBSERVATION"]["banner"] == (
        "OBSERVATION ABOUT ORCHESTRATOR REASONING. It concerns reasoning, not implementation, and is not evidence "
        "for any hypothesis.")

    # EVIDENCE_WITHDRAWN (PINNED, from mandatory_bridge_inputs directly): only in F, lifecycle WITHDRAWN.
    assert "CX-WITHDRAWN-FINDING" in by_section["F"]
    for letter, ids in by_section.items():
        if letter != "F":
            assert "CX-WITHDRAWN-FINDING" not in ids
    assert f_rows["CX-WITHDRAWN-FINDING"]["authority_class"] == "EVIDENCE_WITHDRAWN"
    assert f_rows["CX-WITHDRAWN-FINDING"]["lifecycle"] == "WITHDRAWN"
    assert f_rows["CX-WITHDRAWN-FINDING"]["banner"] == \
        "WITHDRAWN: retained as evidence of a withdrawn claim; never cited as a finding."

    assert validatemod.verify_packet(m, task_spec, repo=str(fixture_repo.root), registry_path=registry_path) == []
