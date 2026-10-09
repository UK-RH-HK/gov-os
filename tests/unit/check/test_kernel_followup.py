"""Unit tests for the checks' pieces of the follow-up after W1-41 (DEC-565, DEC-542, DEC-521)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

SCHEMAS_REL = "template/governance/kernel/schemas"
COMMIT = "0123456789abcdef0123456789abcdef01234567"
RECORD = "docs/probes/PROJ-full/PR-PROJ-full.md"


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _probe(commit=COMMIT):
    return ("---\ntype: probe\ntask: PROJ-full\nreviewer_session: r-1\nimplementer_session: i-1\n"
            "reviewer_wrote_nothing: true\ncommissioned_by: orchestrator\njudged_by: orchestrator\n"
            f"judgement: pass\nprobed_commit: {commit}\n---\n# A probe record\n")


def _with_schemas(root, *names):
    for name in names:
        target = root / SCHEMAS_REL / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / SCHEMAS_REL / name, target)
    return root


def _skill(root, rel, text="---\nname: a-skill\nversion: \"1.0.0\"\ndescription: A skill.\n---\n\n# A skill\n"):
    return _write(root, f"{rel}/SKILL.md", text)


def _validator(capsys, monkeypatch, root, *args):
    from gov.check.skill_validator import main
    monkeypatch.chdir(root)
    code = main(list(args))
    return code, json.loads(capsys.readouterr().out)


# --------------------------------------------------------------------------
# schema check: the probe type (DEC-565)
# --------------------------------------------------------------------------

def test_a_well_formed_probe_record_owes_no_shared_field(tmp_path):
    from gov.check.schema import check
    root = _with_schemas(tmp_path / "project", "probe.schema.json", "common.schema.json")
    _write(root, RECORD, _probe())
    assert check(root) == []


def test_a_probe_record_s_field_of_a_wrong_value_is_one_finding(tmp_path):
    from gov.check.schema import check
    root = _with_schemas(tmp_path / "project", "probe.schema.json", "common.schema.json")
    _write(root, RECORD, _probe(commit="HEAD"))
    assert [(f["code"], f["path"], f["field"]) for f in check(root)] == [
        ("SCHEMA_INVALID_FIELD", RECORD, "probed_commit")]


def test_a_probe_record_is_never_silent_where_its_schema_cannot_be_read(tmp_path):
    from gov.check.schema import check
    root = tmp_path / "project"
    _write(root, RECORD, _probe())
    assert [f["code"] for f in check(root)] == ["SCHEMA_UNREADABLE"]
    # the shared definitions are gone: the shapes that refer to them cannot be measured
    _with_schemas(root, "probe.schema.json")
    assert {f["code"] for f in check(root)} == {"SCHEMA_INVALID_FIELD"}


def test_a_record_is_held_to_the_schemas_of_both_layouts_and_no_finding_is_doubled(tmp_path):
    """DEC-579: the installed kernel's schemas are read as the template's are."""
    from gov.check.schema import check
    root = _with_schemas(tmp_path / "project", "probe.schema.json", "common.schema.json")
    installed = root / "governance/kernel/schemas"
    shutil.copytree(root / SCHEMAS_REL, installed)
    _write(root, RECORD, _probe(commit="HEAD"))
    assert [(f["code"], f["field"]) for f in check(root)] == [("SCHEMA_INVALID_FIELD", "probed_commit")]
    schema = json.loads((installed / "probe.schema.json").read_text(encoding="utf-8"))
    schema["required"] = [*schema["required"], "review_note"]
    (installed / "probe.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    assert [(f["code"], f["field"]) for f in check(root)] == [
        ("SCHEMA_INVALID_FIELD", "probed_commit"), ("SCHEMA_MISSING_FIELD", "review_note")]
    shutil.rmtree(root / SCHEMAS_REL)   # the installed layout alone
    assert [f["field"] for f in check(root)] == ["review_note", "probed_commit"]


# --------------------------------------------------------------------------
# commands check: the recorded commands (DEC-542)
# --------------------------------------------------------------------------

def test_the_recorded_commands_are_held_and_lock_by_its_module_command(tmp_path):
    from gov.check.commands import GOV_COMMANDS, check
    root = tmp_path / "project"
    for command in GOV_COMMANDS:
        _write(root, f"src/gov/{command}/command.py", "")
    assert [f["command"] for f in check(root)] == ["lock"]
    _write(root, "src/gov/lock/__main__.py", "")
    assert check(root) == []
    (root / "src/gov/telemetry/command.py").unlink()
    assert [f["command"] for f in check(root)] == ["telemetry"]


# --------------------------------------------------------------------------
# skill validator: both layouts (DEC-521)
# --------------------------------------------------------------------------

def test_both_layouts_measures_the_installed_skills(tmp_path, capsys, monkeypatch):
    root = tmp_path / "project"
    _skill(root, "governance/kernel/skills/one", "# no frontmatter\n")
    code, output = _validator(capsys, monkeypatch, root, "--both-layouts", "template/governance/kernel/skills/one")
    assert code == 1 and [f["code"] for f in output["findings"]] == ["SKILL_NO_FRONTMATTER"]
    assert "governance/kernel/skills/one/SKILL.md" in output["findings"][0]["message"]
    assert "template/" not in output["findings"][0]["message"]


def test_both_layouts_a_skill_absent_from_a_layout_that_exists_is_unmeasured(tmp_path, capsys, monkeypatch):
    root = tmp_path / "project"
    _skill(root, "template/governance/kernel/skills/one")
    _skill(root, "governance/kernel/skills/another")
    code, output = _validator(capsys, monkeypatch, root, "--both-layouts", "template/governance/kernel/skills/one")
    assert code == 1 and output["unmeasured"] is True
    assert output["reason"] == "path does not exist: governance/kernel/skills/one"


def test_without_the_flag_a_template_path_is_only_itself(tmp_path, capsys, monkeypatch):
    root = tmp_path / "project"
    _skill(root, "governance/kernel/skills/one")
    code, output = _validator(capsys, monkeypatch, root, "template/governance/kernel/skills/one")
    assert code == 1 and output["unmeasured"] is True
