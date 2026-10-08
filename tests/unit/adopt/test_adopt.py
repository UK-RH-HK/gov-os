"""Builder tests for ``gov adopt --lite`` (W1-41). Regression evidence only (DEC-136).

The tool runs only on a project built in ``tmp_path``, a git repository of its own. Two things are replaced here,
and named where they are: the reading of the code graph (``stages._importers``, which needs the code index daemon)
and the index refresh (``stages.rebuild``). The acceptance cases hold both as they are.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.adopt import command, legacy, project, stages  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402

FILES = {"lib/util.py": "def helper():\n    return 1\n", "lib/other.py": "VALUE = 2\n",
         "scripts/run.py": "from lib.util import helper\nhelper()\n", "docs/old.md": "old\n", "README.md": "# p\n",
         ".gitignore": ".gov-runtime/\n"}  # the record store of A3 lies there; a tree that shows it is not clean
VERDICT = "audit/a5-verdict.md"


PATHS = ("lib/**", "scripts/**", "docs/**", "audit/**", "pkg/**", "README.md", ".gitignore")


def config(code_intelligence=True, paths=PATHS):
    return {"path-map.yaml": {"namespaces": {"all": {"paths": list(paths)}},
                              "capabilities": {"code_intelligence": {"enabled": code_intelligence}}}}


def sh(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


def write(root, rel, text):
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def commit(root, message, *trailers):
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", message, *[part for trailer in trailers for part in ("--trailer", trailer)])
    return sh(root, "rev-parse", "HEAD")


@pytest.fixture()
def root(tmp_path, monkeypatch):
    root = tmp_path / "project"
    for rel, text in FILES.items():
        write(root, rel, text)
    sh(root, "init", "-q")
    sh(root, "config", "user.name", "t")
    sh(root, "config", "user.email", "t@example.invalid")
    commit(root, "fixture")
    # Replaced: the code graph (needs the code index daemon) and the index refresh (gov rebuild).
    monkeypatch.setattr(stages, "_importers", lambda root, paths: {
        rel: (["scripts/run.py"] if rel == "lib/util.py" else []) for rel in paths})
    monkeypatch.setattr(stages, "rebuild", lambda run, result: {**result, "rebuild": "replaced in this test"})
    return root.resolve()


def stage(root, name, session="adopter", conf=None, **more):
    args = SimpleNamespace(**{"lite": True, "stage": name, "map": None, "verdict": None, "session": session, **more})
    return stages.run(root, args, conf or config())


def refused(code, root, name, **more):
    with pytest.raises(GovError) as caught:
        stage(root, name, **more)
    assert caught.value.code == "ADOPT_" + code, caught.value.message
    return caught.value


def proposal(root, *entries):
    file = root.parent / "proposal.yaml"
    file.write_text(yaml.safe_dump({"artefacts": list(entries)}), encoding="utf-8")
    return str(file)


def verdict(root, session="auditor", role="independent-auditor", verdict="pass"):
    head = {"id": "AV-1", "type": "adoption-verdict", "status": "ACTIVE", "state_class": "EVIDENCE",
            "verdict": verdict, "auditor_session": session,
            "path_map_hash": project.sha256((root / project.record_path("A3")).read_bytes())}
    write(root, VERDICT, "---\n" + yaml.safe_dump(head) + "---\n\n# AV-1\n")
    return commit(root, "A5: review", *([f"Role: {role}"] if role else []))


MOVES = ({"path": "lib/util.py", "action": "MOVE", "target": "pkg/util.py", "batch": 1},
         {"path": "docs/old.md", "action": "DELETE_FROM_ACTIVE_TREE", "batch": 2})


def planned(root, *entries):
    for name in ("A0", "A1", "A2"):
        stage(root, name)
    stage(root, "A3", map=proposal(root, *(entries or MOVES)))
    stage(root, "A4")


def record(root, name):
    return project.frontmatter((root / project.record_path(name)).read_text(encoding="utf-8"))


def test_without_lite_the_command_stays_reserved_and_lite_needs_a_stage(tmp_path):
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    with pytest.raises(GovError) as caught:
        command.run(tmp_path, parser.parse_args([]), {})
    assert caught.value.code == "NOT_IMPLEMENTED"
    with pytest.raises(SystemExit) as usage:
        command.run(tmp_path, parser.parse_args(["--lite"]), {})
    assert usage.value.code == 2


def test_a_stage_refuses_without_the_stage_before_it_and_on_a_dirty_tree(root):
    assert refused("STAGE_MISSING", root, "A1").details["stage"] == "A0"
    write(root, "lib/new.py", "x = 1\n")
    assert refused("TREE_NOT_CLEAN", root, "A0").details["paths"] == ["lib/new.py"]


def test_a_record_changed_after_the_next_stage_stood_on_it_breaks_the_chain(root):
    stage(root, "A0")
    stage(root, "A1")
    rel = project.record_path("A0")
    write(root, rel, (root / rel).read_text(encoding="utf-8") + "\nedited\n")
    commit(root, "edit")
    assert refused("CHAIN_BROKEN", root, "A2").details["stage"] == "A1"


def test_an_unknown_artefact_gets_a_decision_package_and_is_only_kept(root):
    write(root, "vault/ledger.bin", "?")
    commit(root, "unknown")
    for name in ("A0", "A1"):
        stage(root, name)
    result = stage(root, "A2")
    assert result["unknown"] == ["vault/ledger.bin"] and (root / result["packages"][0]).is_file()
    error = refused("PROPOSAL_REFUSED", root, "A3", map=proposal(
        root, {"path": "vault/ledger.bin", "action": "DELETE_FROM_ACTIVE_TREE"}))
    assert "unknown material artefact" in error.message


def test_no_move_is_recorded_where_code_intelligence_is_off(root):
    for name in ("A0", "A1", "A2"):
        stage(root, name)
    head = sh(root, "rev-parse", "HEAD")
    refused("CODE_INTELLIGENCE_OFF", root, "A3", conf=config(False), map=proposal(root, MOVES[0]))
    assert sh(root, "rev-parse", "HEAD") == head and not (root / project.record_path("A3")).exists()


def test_the_plan_flags_the_importer_and_refuses_what_changes_content(root):
    planned(root)
    plan = record(root, "A4")
    assert [batch["rollback_point"] for batch in plan["batches"]] == [
        "refs/gov/adoption/rollback/batch-1", "refs/gov/adoption/rollback/batch-2"]
    assert plan["dependents"] == [{"artefact": "lib/util.py", "relation": "importer", "dependent": "scripts/run.py",
                                   "handling": "flag"}]
    stage(root, "A3", map=proposal(root, {"path": "lib/util.py", "action": "SPLIT", "targets": ["pkg/a.py"]}))
    assert refused("CONTENT_CHANGE", root, "A4").details["artefacts"] == ["lib/util.py"]


def test_the_migration_moves_what_the_audited_map_says_and_changes_no_content(root):
    planned(root)
    before = project.tree(root)
    verdict(root)
    stage(root, "A5", verdict=VERDICT)
    start = sh(root, "rev-parse", "HEAD")
    result = stage(root, "A6")
    after = project.tree(root)
    assert after["pkg/util.py"] == before["lib/util.py"] and "lib/util.py" not in after and "docs/old.md" not in after
    assert {rel: blob for rel, blob in after.items() if rel in before} == {
        rel: blob for rel, blob in before.items() if rel not in ("lib/util.py", "docs/old.md")}
    done = record(root, "A6")["batches"]
    assert sh(root, "rev-parse", done[0]["rollback_point"]) == start
    assert sh(root, "rev-parse", done[1]["rollback_point"]) == done[0]["commit"]
    assert result["rebuild"] == "replaced in this test" and project.dirty(root) == []


@pytest.mark.parametrize("how, code", [
    (lambda root: None, "STAGE_MISSING"),
    (lambda root: verdict(root, role=None), "VERDICT_NOT_INDEPENDENT"),
    (lambda root: verdict(root, role="engineer"), "VERDICT_NOT_INDEPENDENT"),
    (lambda root: verdict(root, session="adopter"), "VERDICT_NOT_INDEPENDENT"),
    (lambda root: verdict(root, verdict="pass_with_findings"), "VERDICT_NOT_PASS"),
    (lambda root: write(root, VERDICT, "---\nverdict: pass\n---\n"), "TREE_NOT_CLEAN"),
])
def test_nothing_moves_without_an_accepted_verdict(root, how, code):
    planned(root)
    how(root)
    tree = None if code == "TREE_NOT_CLEAN" else project.tree(root)
    if code != "STAGE_MISSING":
        refused(code, root, "A5", verdict=VERDICT)
    refused("TREE_NOT_CLEAN" if tree is None else "STAGE_MISSING", root, "A6")
    assert (root / "lib/util.py").is_file() and (tree is None or project.tree(root) == tree)


def test_a_verdict_does_not_hold_for_a_path_map_or_a_verdict_that_changed_after_it(root):
    planned(root)
    verdict(root)
    stage(root, "A5", verdict=VERDICT)
    write(root, VERDICT, (root / VERDICT).read_text(encoding="utf-8") + "\nedited\n")
    commit(root, "edit the verdict", "Role: independent-auditor")
    refused("VERDICT_CHANGED", root, "A6")
    stage(root, "A3", map=proposal(root, MOVES[0]))
    refused("CHAIN_BROKEN", root, "A6")
    stage(root, "A4")
    refused("VERDICT_OTHER_MAP", root, "A5", verdict=VERDICT)
    assert (root / "lib/util.py").is_file() and not (root / "pkg").exists()


def test_a_batch_that_fails_is_rolled_back_and_the_batches_after_it_do_not_run(root):
    planned(root, {"path": "lib/other.py", "action": "MOVE", "target": "pkg", "batch": 1},
            {"path": "lib/util.py", "action": "MOVE", "target": "pkg/util.py", "batch": 2},
            {"path": "docs/old.md", "action": "DELETE_FROM_ACTIVE_TREE", "batch": 3})
    verdict(root)
    stage(root, "A5", verdict=VERDICT)
    error = refused("BATCH_FAILED", root, "A6")
    assert error.details["batch"] == 2 and error.details["done"] == [1]
    assert sh(root, "log", "-1", "--format=%s") == "gov adopt --lite A6: batch 1"
    assert sh(root, "rev-parse", "refs/gov/adoption/rollback/batch-2") == sh(root, "rev-parse", "HEAD")
    assert project.dirty(root) == [] and (root / "lib/util.py").is_file() and (root / "docs/old.md").is_file()
    assert not (root / project.record_path("A6")).exists()


def test_a_backup_ref_that_no_longer_resolves_stops_the_migration(root):
    planned(root)
    verdict(root)
    stage(root, "A5", verdict=VERDICT)
    sh(root, "update-ref", "-d", record(root, "A0")["backup_ref"])
    refused("BACKUP_REF", root, "A6")
    assert (root / "lib/util.py").is_file()


def test_a_move_out_of_a_native_layout_needs_both_grounds():
    tracked = {"pyproject.toml": "1", "src/app/core.py": "2", "tools/x/package.json": "3", "tools/x/src/a.js": "4",
               "lib/util.py": "5"}
    assert stages._native("src/app/core.py", tracked) == "pyproject.toml"
    assert stages._native("tools/x/src/a.js", tracked) == "tools/x/package.json"
    assert stages._native("lib/util.py", tracked) is None


def test_agents_md_is_imported_one_section_at_a_time():
    found = legacy._sections("# Title\n\nintro\n\n## Roles\n\n### Engineer\n\nbuilds\n\n## Style\n\nshort\n")
    assert list(found) == ["00-preamble", "03-engineer", "04-style"]  # "## Roles" is a heading and nothing else
    assert found["03-engineer"] == "### Engineer\n\nbuilds\n\n"


def test_the_tools_own_import_of_an_mdc_keeps_its_body_and_globs_in_plain_yaml():
    text = legacy._mdc(".cursor/rules/a.mdc", "---\ndescription: d\nglobs: ['*.py', '*.md']\n---\nUse tabs.\n")
    head = project.frontmatter(text)
    assert head["globs"] == ["*.py", "*.md"] == head["cursor"]["globs"] and head["description"] == "d"
    assert "&id" not in text and text.endswith("---\nUse tabs.\n")
    with pytest.raises(ValueError):
        legacy._mdc(".cursor/rules/a.mdc", "---\nglobs: 3\n---\nUse tabs.\n")
