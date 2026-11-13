"""W2-88 S18 to S23: the set tools call ``gov.memaudit`` and define no copy of it; the variants, the walls' ACT, the
cost and the launch check."""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from gov.adopt import memory_sets

GOV_OS = Path(memory_sets.__file__).resolve().parents[3]
BRIEFS = GOV_OS / memory_sets.BRIEFS


def test_the_module_imports_the_audit_core_and_defines_none_of_it():
    tree = ast.parse(Path(memory_sets.__file__).read_text())
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module == "gov.memaudit"
                for alias in node.names}
    assert {"preflight", "declare", "layout", "figures", "schedule", "pool"} <= imported
    defined = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    forbidden = ("preflight", "used", "mark", "declare", "figures", "verdict", "bar")
    assert not [name for name in defined if any(word in name.lower() for word in forbidden)], defined
    constants = {target.id for node in ast.walk(tree) if isinstance(node, ast.Assign) for target in node.targets
                 if isinstance(target, ast.Name)}
    assert not [name for name in constants if "USED" in name.upper() or "PREFLIGHT" in name.upper()]


def test_the_variants_differ_from_the_gov_os_briefs_only_in_the_two_parts():
    made = memory_sets.variants(BRIEFS, {"decision": "adr", "callers": "src", "code-paraphrase": "src"},
                                ["records/private/**"])
    assert set(made) == {"writer", "checker", "auditor"}
    for kind, item in made.items():
        original = (BRIEFS / f"{kind}.md").read_text()
        assert item["sha256"] == hashlib.sha256(item["text"].encode()).hexdigest()
        assert "records/private/**" in item["text"] and original != item["text"]
        gone = set(original.splitlines()) - set(item["text"].splitlines())
        added = set(item["text"].splitlines()) - set(original.splitlines())
        everything = "\n".join(sorted(gone))
        if kind == "auditor":
            assert not gone  # the auditor's brief only gains the repository's blind list
        else:
            assert "| Count |" in everything or "Each of the five domains" in everything or "category" in everything
        assert any("dropped" in line.lower() or "blind" in line.lower() for line in added)


def test_a_launch_under_an_unapproved_variant_exits_10(tmp_path):
    variant, approved = tmp_path / "variant.md", tmp_path / "approved.txt"
    variant.write_text("a brief\n")
    approved.write_text(hashlib.sha256(b"another brief\n").hexdigest() + "  writer-v1\n")
    assert memory_sets.launch_check(variant, approved) == 10
    approved.write_text(hashlib.sha256(b"a brief\n").hexdigest() + "  writer-v1\n")
    assert memory_sets.launch_check(variant, approved) == 0
    done = subprocess.run([sys.executable, "-m", "gov.adopt.memory_sets", "launch-check", "--variant", str(variant),
                           "--approved", str(tmp_path / "missing.txt")], capture_output=True, env={
                               "PYTHONPATH": str(GOV_OS / "src"), "PATH": "/usr/bin:/bin"})
    assert done.returncode == 10


def test_the_cost_gives_the_four_figures_and_names_what_replaces_them():
    price = memory_sets.cost(40)
    assert {"tokens", "usd", "gpu_minutes", "owner_minutes", "replace_after"} <= set(price)
    assert price["usd"] == 30.0 and memory_sets.cost(80)["usd"] == 60.0
    assert "first audit" in price["replace_after"]


def test_the_audit_record_and_the_walls_act_start_nothing_and_apply_nothing(tmp_path):
    made = memory_sets.variants(BRIEFS, {}, [])
    sets = tmp_path / "sets"  # never made by the tool
    record = memory_sets.audit_record(tmp_path, sets_root=str(sets), audits=["memory-audit-20261113"], made=made)
    act = memory_sets.walls_act(tmp_path, sets_root=str(sets), audit="memory-audit-20261113", made=made, blind=["x/**"])
    assert record["due"] == memory_sets.NOT_DUE and set(record["variants"]) == {"writer", "checker", "auditor"}
    assert json.loads((tmp_path / "memory-audit/AUDIT-RECORD.json").read_text())["sets_root"] == str(sets)
    assert not sets.exists()  # the sets root is the operator's to make
    assert (act / "walls/wall_hook.py").is_file() and json.loads((act / "sets-root.json").read_text())["mode"] == "0700"
    assert len((act / "approved.txt").read_text().splitlines()) == 3
    assert "gov rebuild --integration" in (act / "ACT.md").read_text()
