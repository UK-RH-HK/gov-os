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

BR-DAG-AMEND-R1-2 (node R1-RM): this file used to compile against LIVE refs of the shared repository with no
repo/view pin, and flaked under concurrent agent git activity -- ``config/canonical-view.yaml``'s ``records`` ref
(``refs/heads/bridge/p2-context-retrieval``, ``follow: tip``) is exactly the branch every parallel builder commits
to, in the SAME underlying object store this worktree shares with every other worktree of this repository (a git
worktree's branches are not private to it). A commit landing on that ref between this test's two ``compile_packet``
calls -- or even between two test RUNS sharing one pytest process -- could change section A's own item set (a new
mandatory owner record) or the resolved commits recorded in the manifest, which is precisely the "24 expected vs
20 items... became mandatory after run-1" failure BR-DAG-AMEND-R1-1 separately repairs in ``validate.py``.

The fix here is orthogonal to R1-1: PIN every named, tip-following ref to the exact commit it resolves to ONCE, at
module import time, and compile against THAT pinned view for both assertions in this file. This tests exactly what
BR-HO-0013/node B6 always meant to test -- "is the compiler itself deterministic and does it place every mandatory
item correctly" -- without the confound of a shared branch moving under it mid-test. ``product``/``evidence`` are
already ``follow: pinned`` in the real config; only ``records`` (and, generically, any other ``follow: tip`` named
ref a future edit to that config might add) needs pinning here. ``history`` (``ref_glob: refs/heads/phase2/*``,
the FROZEN phase2 product branches) is left as live tip -- those branches are frozen, and are not this test's own
mandatory-item content. ``repo=`` is passed explicitly to both compiles, never relying on ``gitobj.repo_root()``'s
process-global cwd cache (R1-INT's routed fix; a new test must pass ``repo=`` explicitly regardless -- template
amendment R1-T1).

BR-DAG-AMEND-R1-17 reopening (pass 3, coordinator finding): pinning the VIEW (above) closed the git-ref confound,
but ``compile_packet`` still reached ``govbridge.compile.packet.Compiler.code_conn``/``.code_seeds_for``, which
read the STORE by its ambient default (``GOVBRIDGE_STORE`` unset -> ``$HOME/.cache/gov-bridge/store/default``) --
a single, machine-wide store this test shared with every OTHER agent's own concurrent suite run in this session.
Two compiles in the SAME test could therefore see the code layer change (or be rebuilt) BETWEEN them by a
completely unrelated process, exactly the kind of external-state confound the view-pinning fix above already
eliminated for git refs, just not yet for the store.

The fix lives in ``tests/compile/conftest.py``'s own ``_no_env_leak`` fixture (see its docstring), not in this
file: an EARLIER version of this fix added a module-scoped ``GOVBRIDGE_STORE`` override here directly, using
``pytest.MonkeyPatch()`` since a module-scoped fixture cannot use the function-scoped ``monkeypatch`` fixture.
That override was silently undone every test by ``_no_env_leak`` itself, which back then only called
``monkeypatch.delenv("GOVBRIDGE_STORE")`` -- unconditionally, after this module's own fixture had already run
(pytest runs function-scoped fixtures' setup AFTER any wider-scoped ones for the same test), deleting the very
override this module had just set. The test still passed when that was tried, but only because nothing else
happened to touch the shared default store in that particular ~165s window -- not because the isolation took
effect. ``_no_env_leak`` now sets ``GOVBRIDGE_STORE`` to a fresh ``tmp_path`` directory itself (instead of
deleting it), which fixes this for every test in the package including both of this module's, so no local
override is needed or attempted here any more. The code layer is never built in that private store, so every
code-route touchpoint (``code_conn``/``code_seeds_for``, and section B/C's own graph BFS) degrades to its own,
pre-existing, documented "honest MISSING" empty/None result via ``packet.py``'s own out-of-scope exception
handling -- identically, deterministically, on every compile in this module, which is exactly what the
byte-identical assertion needs and never weakens it: the two renders are still compared for EXACT equality,
just no longer confounded by a store neither compile call ever asked to share."""
import os
import tempfile
from pathlib import Path

import yaml

from govbridge.compile import packet as packetmod
from govbridge.compile import validate as validatemod
from govbridge.core import gitobj
from govbridge.core.yamlutil import load_yaml_file
from govbridge.route.router import FAKE_ROUTES

DEMO_TASK_SPEC = Path(__file__).resolve().parents[2] / "ARCHITECTURE" / "demonstration-task.yaml"
REPO_ROOT = gitobj.repo_root(str(Path(__file__).resolve().parent))


def _pinned_view_path(tmp_dir: str) -> str:
    """Writes a copy of the real ``config/canonical-view.yaml`` with every ``follow: tip`` NAMED ref (``records``,
    concretely) rewritten to ``follow: pinned`` at the commit it resolves to right now -- resolved exactly ONCE,
    so every compile in this module sees the identical view regardless of what any other worktree commits to the
    shared ``records`` branch afterwards. ``ref_glob`` refs (``history``) are left untouched: see the module
    docstring."""
    real_task_spec = load_yaml_file(str(DEMO_TASK_SPEC))
    real_view_path = real_task_spec["view"]
    if not os.path.isabs(real_view_path):
        real_view_path = os.path.join(str(DEMO_TASK_SPEC.parents[1]), real_view_path) \
            if not os.path.exists(real_view_path) else real_view_path
    doc = load_yaml_file(real_view_path)
    for ref in doc.get("refs", []):
        if ref.get("follow") == "tip" and ref.get("ref"):
            commit = gitobj.resolve_commit(ref["ref"], repo=REPO_ROOT)
            assert commit, f"canonical-view ref {ref['name']!r} ({ref['ref']!r}) does not resolve at {REPO_ROOT}"
            ref["follow"] = "pinned"
            ref["pinned_commit"] = commit

    out_path = os.path.join(tmp_dir, "canonical-view.pinned.yaml")
    with open(out_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False)
    return out_path


_PIN_DIR = tempfile.mkdtemp(prefix="mf-recorded-view-")
_PINNED_VIEW_PATH = _pinned_view_path(_PIN_DIR)


def _pinned_task_spec() -> dict:
    task_spec = load_yaml_file(str(DEMO_TASK_SPEC))
    task_spec = dict(task_spec)
    task_spec["view"] = _PINNED_VIEW_PATH
    return task_spec

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
    task_spec = _pinned_task_spec()
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=REPO_ROOT)
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

    assert validatemod.verify_packet(m, task_spec, repo=REPO_ROOT, registry_path=result["registry_path"]) == []


def test_real_demonstration_task_compiles_byte_identical_twice():
    task_spec = _pinned_task_spec()
    r1 = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=REPO_ROOT)
    r2 = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=REPO_ROOT)
    assert r1["status"] == packetmod.STATUS_OK
    assert r2["status"] == packetmod.STATUS_OK
    assert r1["rendered"] == r2["rendered"]
    assert r1["packet_sha256"] == r2["packet_sha256"]
    assert r1["manifest_sha256"] == r2["manifest_sha256"]
    assert _per_item_section_map(r1["manifest"]) == _per_item_section_map(r2["manifest"])
