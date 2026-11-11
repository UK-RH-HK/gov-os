"""S3, S4, F2, F3: the declaration, the use-once marker and the set's entry in the sets root's own map."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from gov.memaudit import declare, ledger
from gov.memaudit.common import set_digest

from .conftest import AUDIT, SETS_MAP


def ready(plant, drop=None):
    """Pre-flight and void run clean, as the runner would before declare."""
    assert plant.cli(*plant.preflight_args()).returncode == 0
    plant.notes(drop or {})
    assert plant.cli(*plant.void_args()).returncode == 0


def test_declare_writes_the_map_entry_then_declaration_then_used_in_order(plant):
    ready(plant, {"q01": "reject"})
    done = plant.cli(*plant.declare_args())
    assert done.returncode == 0, done.stdout
    decl = json.loads((plant.run_dir / "DECLARATION.json").read_text())
    out = done.stdout.splitlines()
    assert out == [f"DECLARED: audit commit {plant.repo['head'][:12]}, n 39, set digest {decl['set_digest'][:12]}",
                   "USED written"]
    d_ns = (plant.run_dir / "DECLARATION.json").stat().st_mtime_ns
    u_ns = (plant.run_dir / "USED").stat().st_mtime_ns
    assert u_ns > d_ns
    events = [e["event"] for e in ledger.read(plant.run_dir)]
    assert events == ["preflight", "drop", "declaration", "used"]
    used = (plant.run_dir / "USED").read_text().split()
    assert used[1] == AUDIT and used[2] == declare.sha256_file(plant.run_dir / "DECLARATION.json")


def test_the_declaration_holds_every_key_and_the_bar_scaled_to_n(plant):
    ready(plant, {"q01": "reject"})
    assert plant.cli(*plant.declare_args()).returncode == 0
    decl = json.loads((plant.run_dir / "DECLARATION.json").read_text())
    assert set(decl) == {"audit", "audit_commit", "store_commit", "store_sha256", "gov_pin", "retrieval_yaml_sha256",
                         "set_digest", "n", "settings", "nonstandard", "decision", "ok", "bar", "rounding",
                         "declared_at"}
    assert decl["audit_commit"] == decl["store_commit"] == plant.repo["head"]
    assert decl["gov_pin"] == "pin-0123456789ab"
    assert decl["settings"] == {"reranker": "shared", "pool": True, "bundle_tokens": 6000, "search_again_once": True}
    assert decl["n"] == 39 and decl["bar"] == {"need_right": 34, "max_wrong": 1, "target_right": 38}
    assert decl["ok"] is True and decl["nonstandard"] == [] and decl["decision"] is None
    assert decl["set_digest"] == set_digest(plant.hidden)
    assert decl["store_sha256"] == declare.sha256_file(plant.store)


def test_a_second_declare_exits_3_and_writes_nothing(plant):
    ready(plant)
    assert plant.cli(*plant.declare_args()).returncode == 0
    before = {p.name: p.stat().st_mtime_ns for p in plant.run_dir.iterdir()}
    map_before = (plant.root / "governance/project/path-map.yaml").read_bytes()
    done = plant.cli(*plant.declare_args())
    assert done.returncode == 3 and done.stdout == "USED\n"
    assert {p.name: p.stat().st_mtime_ns for p in plant.run_dir.iterdir()} == before
    assert (plant.root / "governance/project/path-map.yaml").read_bytes() == map_before
    assert plant.cli(*plant.void_args()).returncode == 3


def test_a_pool_off_retrieval_yaml_is_named_and_not_ok_without_a_decision(plant):
    head = plant.repo["off_head"]
    for i in range(1, 41):
        plant.put({**plant.questions[f"q{i:02d}"], "commit": head})
    plant.make_store(head)
    args = plant.preflight_args(head)
    args[args.index("--repo") + 1] = str(plant.repo["off"])
    assert plant.cli(*args).returncode == 0
    plant.notes()
    assert plant.cli(*plant.void_args()).returncode == 0
    map_before = (plant.root / "governance/project/path-map.yaml").read_bytes()
    done = plant.cli(*plant.declare_args(plant.repo["off"], head))
    assert done.returncode == 1 and done.stdout == "DC-DECISION pool\n"
    decl = json.loads((plant.run_dir / "DECLARATION.json").read_text())
    assert decl["ok"] is False and decl["nonstandard"] == ["pool"] and decl["settings"]["pool"] is False
    assert not (plant.run_dir / "USED").exists()
    assert (plant.root / "governance/project/path-map.yaml").read_bytes() == map_before
    done = plant.cli(*plant.declare_args(plant.repo["off"], head, "--decision", "DEC-1234"))
    assert done.returncode == 0
    decl = json.loads((plant.run_dir / "DECLARATION.json").read_text())
    assert decl["ok"] is True and decl["decision"] == "DEC-1234"
    assert (plant.run_dir / "USED").exists()


def test_each_refusal_code_writes_nothing(plant):
    done = plant.cli(*plant.declare_args())
    assert done.returncode == 1
    assert done.stdout.splitlines() == ["DC-PREFLIGHT", "DC-DROPS"]
    ready(plant)
    plant.make_store(plant.repo["earlier"])
    (plant.tmp / "plain-gov").write_text("x")
    done = plant.cli(*plant.declare_args(None, None, "--gov", str(plant.tmp / "plain-gov")))
    assert done.stdout.splitlines() == ["DC-STORE", "DC-PIN"]
    assert not (plant.run_dir / "DECLARATION.json").exists() and not (plant.run_dir / "USED").exists()


def test_a_set_changed_after_void_is_dc_drops(plant):
    ready(plant)
    (plant.hidden / "q05.yaml").write_text((plant.hidden / "q05.yaml").read_text() + "\n")
    assert plant.cli(*plant.declare_args()).stdout == "DC-DROPS\n"


def test_the_sets_root_map_gains_exactly_one_entry_and_the_repository_is_untouched(plant):
    ready(plant)
    repo = plant.repo["path"]
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True,
                            env=plant.repo["env"]).stdout
    assert plant.cli(*plant.declare_args()).returncode == 0
    text = (plant.root / "governance/project/path-map.yaml").read_text()
    assert text.count(f"{AUDIT}:") == 1
    assert text.replace(declare._entry_text(AUDIT, 2), "") == SETS_MAP  # every other byte kept
    assert subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True,
                          env=plant.repo["env"]).stdout == status == ""
    # the measure's own acceptance: declared, well formed, hidden part covered, the orchestrator not measured
    from gov.util.parts import _Part, evaluation_sets, set_fault
    entry = evaluation_sets(str(plant.root))[AUDIT]
    assert set_fault(entry) is None and "orchestrator" not in entry["measures"]["roles"]
    assert entry["measures"]["roles"] == declare.ROLES and len(declare.ROLES) == 5
    assert _Part(str(plant.root), entry["hidden"], "").inside(str(plant.hidden))
    assert "memory-verdict-2" in evaluation_sets(str(plant.root))


def test_an_equal_entry_is_left_and_a_different_one_is_dc_map(plant):
    ready(plant)
    p = plant.root / "governance/project/path-map.yaml"
    p.write_text(SETS_MAP.replace("  # a comment after", declare._entry_text(AUDIT, 2) + "  # a comment after"))
    before = p.read_bytes()
    assert plant.cli(*plant.declare_args()).returncode == 0
    assert p.read_bytes() == before


def test_a_different_entry_or_no_block_is_dc_map(plant):
    ready(plant)
    p = plant.root / "governance/project/path-map.yaml"
    p.write_text(SETS_MAP.replace("  # a comment after", f"  {AUDIT}:\n    visible: []\n    hidden: [\"x/**\"]\n"
                                  "    measures:\n      roles: [engineer]\n  # a comment after"))
    assert plant.cli(*plant.declare_args()).stdout == "DC-MAP\n"
    p.write_text("version: 1\n")
    assert plant.cli(*plant.declare_args()).stdout == "DC-MAP\n"
    assert not (plant.run_dir / "USED").exists()


def test_an_empty_block_takes_the_entry(tmp_path):
    root = Path(tmp_path)
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/path-map.yaml").write_text("evaluation_sets:\n# end\nnext: 1\n")
    code, new = declare.plan_map({"map": root / "governance/project/path-map.yaml"}, AUDIT)
    assert code is None and new.startswith("evaluation_sets:\n  memory-audit-") and new.endswith("# end\nnext: 1\n")


def test_used_waits_for_a_file_time_past_the_declaration(plant, monkeypatch):
    plant.run_dir.mkdir(parents=True)
    (plant.run_dir / "DECLARATION.json").write_text("{}")
    future = os.stat(plant.run_dir / "DECLARATION.json").st_mtime_ns + 3_600 * 10**9
    os.utime(plant.run_dir / "DECLARATION.json", ns=(future, future))
    monkeypatch.setattr(declare, "WAIT_S", 0.05)
    p = {"declaration": plant.run_dir / "DECLARATION.json", "run": plant.run_dir, "used": plant.run_dir / "USED"}
    try:
        declare._write_used(p, AUDIT, "0" * 64)
    except TimeoutError:
        pass
    else:
        raise AssertionError("USED written before the declaration's time")
    assert not (plant.run_dir / "USED").exists()
    assert sorted(x.name for x in plant.run_dir.iterdir()) == ["DECLARATION.json"]
