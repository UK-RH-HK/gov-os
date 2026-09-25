"""BR-ARCH-RULING-1 real-view acceptance (BR-HO-0013): compiling the real ``ARCHITECTURE/demonstration-task.yaml``
with ``--fake-routes`` (lexical/semantic/code are the all-empty RouteSet in this branch; graph routes are real)
must place every A-admissible ``mandatory_bridge_inputs``/``owner_records``/``contract_v3`` item in section A,
whatever its lifecycle, and the non-ladder mandatory items in their own fixed sections -- never A. Two independent
compiles of the same task spec must be byte-identical (ARCHITECTURE.md section 5.3 rule 6/W10-style determinism;
node B6 acceptance, real view).

This is the ONLY place in ``tests/compile/**`` that reads real Review-8/Phase-2 ids, and only as DATA named
verbatim in the real ``ARCHITECTURE/demonstration-task.yaml`` and the bridge's own ``ORCHESTRATOR_STATE.yaml`` --
nothing here special-cases them: every assertion is the same generic placement rule the fixture tests exercise on
synthetic CX-* ids (OC-BR-02).
"""
from pathlib import Path

from govbridge.compile import packet as packetmod
from govbridge.compile import validate as validatemod
from govbridge.core.yamlutil import load_yaml_file
from govbridge.route.router import FAKE_ROUTES

DEMO_TASK_SPEC = Path(__file__).resolve().parents[2] / "ARCHITECTURE" / "demonstration-task.yaml"

# the mandatory items the ruling's own trigger names, resolved through the three required_inputs of the real task
# spec (mandatory_bridge_inputs.items[*], owner_records[*], contract_v3) -- BR-ARCH-RULING-1's governing record.
EXPECTED_IN_A = (
    "state:bridge#contract_v3",       # CONTRACT (owner source contract)
    "PHASE-2-FROZEN-GATE-CONTRACT",   # FROZEN_GATE_CONTRACT
    "OWNER-LAUNCHER-BR-0001",         # OWNER_DECISION (owner_records)
    "OD-P2-10A", "OD-P2-10B",         # OWNER_DECISION (mandatory_bridge_inputs.items, already ACTIVE)
    "REVIEW-8-RETURN",                # EVIDENCE
    "REVIEW-8-CONTEXT-PACK",          # ORCHESTRATION_RECORD
    "AR96-BUILDER-CHECKPOINT",        # EVIDENCE
    "PHASE-2-LEDGER-P2-L-0033-0047",  # ORCHESTRATION_RECORD
    "PHASE-2-STATE",                  # ORCHESTRATION_RECORD
    "DESIGN-P2-PROBE-OPTION-C",       # ORCHESTRATION_RECORD
    "DESIGN-P2-HISTORICAL-RULE-SOURCE",  # ORCHESTRATION_RECORD
)


def _every_section_ids(manifest: dict) -> dict:
    out = {}
    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub, subsec in sec["subblocks"].items():
                out[sub] = [row["unit"]["id"] for row in subsec["items"]]
        else:
            out[letter] = [row["unit"]["id"] for row in sec["items"]]
    return out


def _per_item_section_map(manifest: dict) -> dict:
    """``{unit_id: section_label}`` across the whole packet -- the map BR-HO-0013 asks to be saved as a checkpoint
    output; a test helper here so the CLI check that saves it (AGENT_RUNS/BR-AR-0013.*) and this test agree
    byte-for-byte on what it means."""
    out = {}
    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub, subsec in sec["subblocks"].items():
                for row in subsec["items"]:
                    out[row["unit"]["id"]] = sub
        else:
            for row in sec["items"]:
                out[row["unit"]["id"]] = letter
    return out


def test_real_demonstration_task_puts_every_a_admissible_mandatory_item_in_a():
    task_spec = load_yaml_file(str(DEMO_TASK_SPEC))
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES)
    assert result["status"] == packetmod.STATUS_OK
    m = result["manifest"]
    by_section = _every_section_ids(m)

    for item_id in EXPECTED_IN_A:
        assert item_id in by_section["A"], f"{item_id} must be in A (BR-ARCH-RULING-1)"

    # no MANDATORY_ITEM_NOT_IN_A notice survives for an A-admissible class -- that notice is only for a class not
    # admissible in A at all (none of the real task's mandatory items are DERIVED).
    assert not any(n["type"] == "MANDATORY_ITEM_NOT_IN_A" for n in m["notices"])
    # the ten items the ruling's trigger names are exactly the ones whose lifecycle is not ACTIVE -- each gets the
    # honest J notice instead, and none of them lost its place in A.
    lifecycle_notices = {n["id"] for n in m["notices"] if n["type"] == "MANDATORY_LIFECYCLE_NOT_ACTIVE"}
    assert lifecycle_notices, "the real records carry no machine-readable status; some notice must fire"
    assert lifecycle_notices <= set(EXPECTED_IN_A)
    a_rows = {r["unit"]["id"]: r for r in m["sections"]["A"]["items"]}
    for item_id in lifecycle_notices:
        assert a_rows[item_id]["lifecycle"] != "ACTIVE"
        assert a_rows[item_id]["banner"], f"{item_id}: a non-ACTIVE A item must carry its lifecycle banner"

    # the non-ladder mandatory items keep their fixed section and never reach A.
    d2_ids = by_section["D.2"]
    d3_ids = by_section["D.3"]
    f_ids = by_section["F"]
    assert "F1-DIRECTION" in d2_ids
    assert "F2-F3-COMMON-CLASS" in d3_ids
    assert "ORCHESTRATOR-REASONING-ERRORS" in f_ids
    for letter, ids in by_section.items():
        if letter != "D.2":
            assert "F1-DIRECTION" not in ids
        if letter != "D.3":
            assert "F2-F3-COMMON-CLASS" not in ids
        if letter != "F":
            assert "ORCHESTRATOR-REASONING-ERRORS" not in ids

    assert validatemod.verify_packet(m, task_spec, registry_path=result["registry_path"]) == []


def test_real_demonstration_task_compiles_byte_identical_twice():
    task_spec = load_yaml_file(str(DEMO_TASK_SPEC))
    r1 = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES)
    r2 = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES)
    assert r1["status"] == packetmod.STATUS_OK
    assert r2["status"] == packetmod.STATUS_OK
    assert r1["rendered"] == r2["rendered"]
    assert r1["packet_sha256"] == r2["packet_sha256"]
    assert r1["manifest_sha256"] == r2["manifest_sha256"]
    assert _per_item_section_map(r1["manifest"]) == _per_item_section_map(r2["manifest"])
