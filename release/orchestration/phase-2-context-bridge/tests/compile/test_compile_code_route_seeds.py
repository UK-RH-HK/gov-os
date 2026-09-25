"""BR-HO-0015 (G row, ARCHITECTURE.md section 7.2): a task SEED that names a RECORD (not a code symbol) must still
populate section G, by deriving seed symbols from the record's own citations -- ``path:N``, a backticked symbol --
resolved at the canonical product ref, then expanding callers/callees/TESTS/READS_KEY from there. A small,
self-contained fixture repo (never Review-8/Phase-2 content -- OC-BR-02): one finding-shaped record, one Rust
module with a target function, its caller and its test, and one evidence probe file the record also cites.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from govbridge.authority.classes import BRIDGE_STATE_PATH
from govbridge.compile import packet as packetmod
from govbridge.route import real_routes


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))


RECORD_PATH = "spec/reports/CX-FIND-0001.md"
NONCODE_PATH = "spec/reports/CX-NONCODE-0001.md"
CODE_PATH = "src/x.rs"
PROBE_PATH = "probes/CX-PROBE-0001.md"

RECORD_TEXT = """# CX-FIND-0001 -- a fixture finding record (BR-HO-0015 acceptance)

| Field | Value |
|---|---|
| Id | **CX-FIND-0001** |

## F1

This finding cites `src/x.rs:3` (the line inside the target function's body), the backticked symbol
`helper_fn`, and the supporting evidence probe `probes/CX-PROBE-0001.md:1`.
"""

CODE_TEXT = """// xyzzycode: fixture rust module for the BR-HO-0015 code-route-seed-derivation test
pub fn target_fn() -> bool {
    helper_fn()
}

pub fn helper_fn() -> bool {
    true
}

pub fn caller_of_target() -> bool {
    target_fn()
}

#[test]
fn test_target_fn() {
    let _ = target_fn();
}
"""

PROBE_TEXT = """# CX-PROBE-0001 -- fixture evidence probe

xyzzyprobe: this is the probe body the finding record cites.
"""

NONCODE_TEXT = """# CX-NONCODE-0001 -- a fixture non-code record

xyzzyrecord: this record has nothing to do with the code route.
"""


def _build_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")

    (root / RECORD_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / RECORD_PATH).write_text(RECORD_TEXT, encoding="utf-8")
    (root / NONCODE_PATH).write_text(NONCODE_TEXT, encoding="utf-8")
    (root / CODE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / CODE_PATH).write_text(CODE_TEXT, encoding="utf-8")
    (root / PROBE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / PROBE_PATH).write_text(PROBE_TEXT, encoding="utf-8")

    state_path = root / BRIDGE_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "schema: bridge-orchestrator-state/1\n"
        "mandatory_bridge_inputs:\n  authority_classes: {}\n  items: []\n",
        encoding="utf-8",
    )
    (root / "config" / "corpus-rules.yaml").parent.mkdir(parents=True, exist_ok=True)
    (root / "config" / "corpus-rules.yaml").write_text(
        "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n",
        encoding="utf-8",
    )

    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c1")
    _git(root, "branch", "-f", "product", "HEAD")
    return root


def _write_configs(tmp_path: Path) -> tuple:
    view_path = tmp_path / "canonical-view.yaml"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: cx-code-seeds-test-view\n"
        "refs:\n"
        "  - {name: records, ref: refs/heads/main, follow: tip, role: primary}\n"
        "  - {name: product, ref: refs/heads/product, follow: tip, role: product}\n"
        "partitions:\n"
        "  - {name: catchall, paths: ['**'], owner: records, fallback: [product]}\n",
        encoding="utf-8",
    )
    registry_path = tmp_path / "authority-registry.yaml"
    registry_path.write_text(
        "schema: govbridge-authority-registry/1\n"
        "class_rules:\n"
        f"  - {{glob: '{CODE_PATH}', class: EVIDENCE}}\n"
        "  - {glob: 'probes/**', class: EVIDENCE}\n"
        "  - {glob: 'spec/reports/**', class: EVIDENCE}\n"
        "  - {glob: '**', class: UNCLASSIFIED}\n",
        encoding="utf-8",
    )
    return str(view_path), str(registry_path)


def _task_spec(view_path: str) -> dict:
    return {
        "schema": "govbridge-task-spec/1", "task_id": "T-CODE-SEEDS-1", "role": "test",
        "objective": "compile a packet whose only seed is a record, to exercise BR-HO-0015's G derivation",
        "view": view_path,
        "required_inputs": [],
        "seeds": ["CX-FIND-0001#F1"],
        "queries": [
            {"id": "q-code", "text": "xyzzycode fixture module", "routes": ["lexical"]},
            {"id": "q-noncode", "text": "xyzzyrecord fixture", "routes": ["lexical"]},
        ],
        "mutation_scope": ["tests/compile/**"],
        "prohibitions": ["do not touch anything outside mutation_scope"],
        "required_checks": ["pytest tests/compile -q"],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": "synthesis",
    }


def _compile(tmp_path: Path) -> tuple:
    repo_root = _build_repo(tmp_path)
    view_path, registry_path = _write_configs(tmp_path)
    from govbridge.core import freshness
    freshness.run(view_path=view_path, rules_path=str(repo_root / "config" / "corpus-rules.yaml"),
                  repo=str(repo_root), from_clean=True)
    task_spec = _task_spec(view_path)
    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(repo_root), registry_path=registry_path)
    return result, task_spec, str(repo_root), registry_path


def test_record_seed_populates_g_with_enclosing_symbol_caller_tests_and_probe(tmp_path):
    result, _task_spec, _repo, _reg = _compile(tmp_path)
    assert result["status"] == packetmod.STATUS_OK

    g_items = result["sections"]["G"]
    assert g_items, "section G must not be empty for a record seed that cites code"

    by_path = {}
    for it in g_items:
        by_path.setdefault(it.path, []).append(it)

    # the enclosing symbol of src/x.rs:3 is target_fn -- an EXACT_PATH citation (the full relative path is cited
    # verbatim), so its resolution must be labelled exactly, never blurred as heuristic.
    target_defs = [it for it in g_items if it.unit_kind == "symbol" and "target_fn" in it.unit_id
                   or (it.unit_kind == "symbol" and it.text and "target_fn" in it.text)]
    assert target_defs, [it.unit_id for it in g_items]
    assert any("EXACT_PATH" in (it.text or "") for it in target_defs), [it.text for it in target_defs]

    # a caller of target_fn (caller_of_target) is present.
    assert any(it.route == "code" and it.unit_kind == "occurrence" and "CALLS" in it.unit_id
               and it.path == CODE_PATH for it in g_items), [it.unit_id for it in g_items]

    # a TESTS edge target (test_target_fn) is present.
    assert any("TESTS" in it.unit_id for it in g_items), [it.unit_id for it in g_items]

    # the backticked symbol (helper_fn) resolves too, labelled HEURISTIC_NAME (never promoted to exact).
    helper_defs = [it for it in g_items if it.unit_kind == "symbol" and it.text and "helper_fn" in it.text]
    assert helper_defs, [it.text for it in g_items if it.unit_kind == "symbol"]
    assert any("HEURISTIC_NAME" in (it.text or "") for it in helper_defs), [it.text for it in helper_defs]

    # the cited evidence probe (no enclosing symbol -- an occurrence-level G item) is present.
    assert any(it.path == PROBE_PATH for it in g_items), [it.path for it in g_items]

    # nothing retrieved/derived is in A or D.1.
    assert result["sections"]["A"] == []
    assert all(it.delivery not in ("RETRIEVED", "DERIVED") for it in result["sections"]["D.1"])


def test_lexical_code_hit_lands_in_g_not_h_and_noncode_hit_stays_in_h(tmp_path):
    result, _task_spec, _repo, _reg = _compile(tmp_path)
    assert result["status"] == packetmod.STATUS_OK

    g_paths = {it.path for it in result["sections"]["G"]}
    h_paths = {it.path for it in result["sections"]["H"]}

    assert CODE_PATH in g_paths, (g_paths, h_paths)
    assert CODE_PATH not in h_paths, (g_paths, h_paths)

    assert NONCODE_PATH in h_paths, (g_paths, h_paths)
    assert NONCODE_PATH not in g_paths, (g_paths, h_paths)


def test_hand_moved_g_item_fails_packet_verify(tmp_path):
    """ARCHITECTURE.md section 5.3 rule 4 (independent re-derivation), applied to a G item: hand-moving a G item
    into A -- or a RETRIEVED G item into D.1 -- must fail ``packet verify`` (BR-HO-0015 acceptance check 5)."""
    from govbridge.compile import validate as validatemod

    result, task_spec, repo_root, registry_path = _compile(tmp_path)
    manifest = result["manifest"]
    assert result["sections"]["G"], "need at least one G item to hand-move"
    assert validatemod.verify_packet(manifest, task_spec, repo=repo_root, registry_path=registry_path) == []

    # move a G item into A: packet verify must fail.
    into_a = dict(manifest)
    into_a["sections"] = dict(manifest["sections"])
    into_a["sections"]["A"] = dict(manifest["sections"]["A"])
    g_row = dict(manifest["sections"]["G"]["items"][0])
    into_a["sections"]["A"]["items"] = list(manifest["sections"]["A"]["items"]) + [g_row]
    problems = validatemod.verify_packet(into_a, task_spec, repo=repo_root, registry_path=registry_path)
    assert problems, "a hand-moved G item in A must fail packet verify"

    # move a RETRIEVED G item into D.1: packet verify must fail.
    retrieved_g_rows = [r for r in manifest["sections"]["G"]["items"] if r["delivery"] in ("RETRIEVED", "DERIVED")]
    assert retrieved_g_rows, [r["delivery"] for r in manifest["sections"]["G"]["items"]]
    into_d1 = dict(manifest)
    into_d1["sections"] = dict(manifest["sections"])
    into_d1["sections"]["D"] = dict(manifest["sections"]["D"])
    into_d1["sections"]["D"]["subblocks"] = dict(manifest["sections"]["D"]["subblocks"])
    into_d1["sections"]["D"]["subblocks"]["D.1"] = dict(manifest["sections"]["D"]["subblocks"]["D.1"])
    into_d1["sections"]["D"]["subblocks"]["D.1"]["items"] = (
        list(manifest["sections"]["D"]["subblocks"]["D.1"]["items"]) + [dict(retrieved_g_rows[0])]
    )
    problems2 = validatemod.verify_packet(into_d1, task_spec, repo=repo_root, registry_path=registry_path)
    assert problems2, "a hand-moved RETRIEVED G item in D.1 must fail packet verify"
