"""W2-174 S5: ``gov adopt --facts`` writes the facts file ``gov brief`` needs, with product defaults and named placeholders."""
from __future__ import annotations

import datetime
import json
import re
import shutil

import pytest
import yaml

from .test_w2_174_support import DONE, REPO, gov, gov_json, repo_with, snapshot, ticket

from gov.adopt import facts

SCHEMA = REPO / "template/governance/kernel/schemas/facts.schema.json"
TEMPLATES = REPO / "template/governance/kernel/templates"
DATE = datetime.date(2026, 11, 13)


def fixture(tmp_path, name="adopted-project-x"):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=[DONE], failure=[DONE])}, name=name)
    shutil.copytree(TEMPLATES, root / "template/governance/kernel/templates")
    return root


def written(tmp_path):
    root = fixture(tmp_path)
    assert facts.write_default(root, DATE) == {"path": str(root / "governance/project/facts.yaml"), "written": True}
    path = root / "governance/project/facts.yaml"
    return root, path, yaml.safe_load(path.read_text(encoding="utf-8"))


def test_the_file_validates_against_the_kernel_schema_and_new_since_is_the_steps_date_as_a_quoted_string(tmp_path):
    import jsonschema

    _, path, data = written(tmp_path)
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")),
                                    format_checker=jsonschema.FormatChecker()).validate(data)
    assert data["ready"] == {"new_since": "2026-11-13"}
    assert "new_since: '2026-11-13'" in path.read_text(encoding="utf-8")


def test_the_command_writes_it_with_the_runs_utc_date_and_a_second_run_writes_nothing(tmp_path):
    root = fixture(tmp_path)
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    code, envelope, _ = gov_json("adopt", "--facts", "--root", str(root))
    assert code == 0 and envelope["result"] == {"path": str(root / "governance/project/facts.yaml"), "written": True}
    assert yaml.safe_load((root / "governance/project/facts.yaml").read_text())["ready"]["new_since"] == today
    before = snapshot(root)
    code, envelope, _ = gov_json("adopt", "--facts", "--root", str(root))
    assert code == 0 and envelope["result"]["written"] is False and snapshot(root) == before


def test_every_other_value_is_a_product_default_of_this_repositorys_nothing(tmp_path):
    root, path, _ = written(tmp_path)
    text = path.read_text(encoding="utf-8")
    for token in (str(tmp_path), root.name, "/home/", "gov-os", "Dynamic-Agentic", "DEC-", "W2-", "usain", ".sh"):
        assert token not in text, token


def test_each_command_is_a_gov_form_or_a_named_placeholder(tmp_path):
    _, _, data = written(tmp_path)
    for name, command in data["commands"].items():
        for part in ("run", "check"):
            form = command[part]
            assert form.startswith("gov ") or form == "{UNSET_%s}" % name.upper(), (name, part, form)
    assert data["commands"]["lead_verify"] == {"run": "{UNSET_LEAD_VERIFY}", "check": "{UNSET_LEAD_VERIFY}"}
    assert data["commands"]["wait_for"]["run"].startswith("gov wait")


def test_the_defaults_cover_every_command_and_step_the_kernel_templates_name(tmp_path):
    _, _, data = written(tmp_path)
    named = {"CMD": set(), "STEP": set()}
    for path in TEMPLATES.glob("*.md"):
        for kind, name in re.findall(r"\{(CMD|STEP):([a-z_]+)\}", path.read_text(encoding="utf-8")):
            named[kind].add(name)
    for key in data["dod"]:
        named["CMD"] |= set(re.findall(r"\{CMD:([a-z_]+)\}", key["line"]))
    for step in data["steps"].values():
        named["CMD"] |= set(re.findall(r"\{CMD:([a-z_]+)\}", step["line"]))
    named["CMD"].discard("name")
    named["STEP"].discard("name")
    assert not named["CMD"] - set(data["commands"]) and not named["STEP"] - set(data["steps"])


def test_gov_brief_no_longer_answers_facts_missing_and_names_the_placeholder_commands(tmp_path):
    root = fixture(tmp_path)
    code, _, err = gov("brief", "engineer", "DAEO-a1", "--root", str(root))
    assert code == 1 and "BRIEF_FACTS_MISSING" in err
    gov("adopt", "--facts", "--root", str(root))
    code, _, err = gov("brief", "engineer", "DAEO-a1", "--root", str(root))
    assert code == 1 and "BRIEF_FACTS_MISSING" not in err and "BRIEF_NOT_READY" in err
    assert re.search(r"PLACEHOLDER_LEFT UNSET_[A-Z_]+", err)
    code, _, err = gov("brief", "lead", "DAEO-a1", "--run", "build", "--root", str(root))
    assert code == 1 and "PLACEHOLDER_LEFT UNSET_LEAD_VERIFY" in err and "BRIEF_FACTS_MISSING" not in err


def test_the_ready_check_has_nothing_to_say_of_the_defaults_themselves(tmp_path):
    root = fixture(tmp_path)
    gov("adopt", "--facts", "--root", str(root))
    _, _, err = gov("brief", "engineer", "DAEO-a1", "--root", str(root))
    assert "READY_NEW_SINCE" not in err and "KPI_NO_VERIFY" not in err and "FACTS_UNREADABLE" not in err


@pytest.mark.parametrize("content", ["paths: {}\n", "not yaml: [", "", "x: 1\n"])
def test_an_existing_facts_file_is_left_byte_for_byte(tmp_path, content):
    root = fixture(tmp_path)
    path = root / "governance/project/facts.yaml"
    path.parent.mkdir(parents=True)
    path.write_bytes(content.encode("utf-8"))
    before = snapshot(root)
    assert facts.write_default(root, DATE) == {"path": str(path), "written": False}
    assert snapshot(root) == before
