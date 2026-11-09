"""Unit tests of gov brief's builder and command on a planted repository (W2-152, DAEO-o5x1; stand-ins only)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gov.brief.build import build
from gov.cli.errors import GovError
from gov.cli.main import main

T0 = """---
name: brief
version: 1.0.0
role: any
---
# Your assignment
You are a fresh {ROLE} session (template `{ROLE_TEMPLATE}`). Ticket {ID} ({W2}). {TICKET_SUMMARY: one paragraph}
Tree: {WRITE_TREE} on {BRANCH}. Commit with {SUBJECT}.
{KPI_TABLE: | id | line | verify |}
Lead note: {LEAD_NOTE}
{REPAIR: the failing output}
Run {CMD:accept}.
{STEP:keep}
{STEP:gone}
End.
"""
ROLE_ENGINEER = "---\nname: role-engineer\nversion: 1.2.0\nrole: engineer\n---\n# You are the engineer\nRun {CMD:accept}.\n"
ROLE_LEAD = """---
name: role-lead
version: 1.0.0
role: orchestrator
---
# Lead
Common head line.
## Your run: {RUN_KIND} (only this section)
**tests**: the tests only.
1. Make the tests.

**build**: implement.
1. Build it with {CMD:accept}.

{STEP:keep}
## Return
Return line.
"""
FACTS = """paths:
  tree: '/w/{W2}'
  tests_tree: '/w/{W2}-tests'
commands:
  accept: {run: 'gov accept {W2} --root {WRITE_TREE}', check: 'gov accept --help'}
steps:
  keep: {"on": true, line: 'Keep line {CMD:accept}.', match: 'x'}
  gone: {"on": false, line: 'Gone line.', match: 'y'}
budgets: {brief: 4000}
ready: {new_since: "2026-11-10"}
"""
KEYS = "keys: [ID, W2, ROLE, ROLE_TEMPLATE, TICKET_SUMMARY, WRITE_TREE, BRANCH, SUBJECT, KPI_TABLE, LEAD_NOTE, REPAIR, RUN_KIND, TREE, TESTS_TREE]\n"
GOOD = {"id": "DAEO-aaaa", "external-ref": "W2-900", "status": "open", "created": "2026-11-01T10:00:00Z",
        "role": "engineer", "allowed_paths": ["src/x/**"], "non_goals": ["nothing else"], "est_loc": 100,
        "kpis": {"success": ["S1 it works. Verify: a test"], "failure": [{"line": "never breaks", "verify": "a case"}]}}


def ticket_text(front: dict, body: str = "# W2-900 Title\n\nThe summary paragraph.\n") -> str:
    return "---\n" + json.dumps(front) + "\n---\n" + body


def plant(tmp_path: Path, front: dict | None = None, t0: str = T0, facts: str = FACTS, extra: dict | None = None) -> Path:
    root = tmp_path / "repo"
    templates = root / "template/governance/kernel/templates"
    templates.mkdir(parents=True)
    (root / ".tickets").mkdir()
    (root / "governance/project").mkdir(parents=True)
    for name, text in (("brief.md", t0), ("role-engineer.md", ROLE_ENGINEER), ("role-lead.md", ROLE_LEAD),
                       ("keys.yaml", KEYS)):
        (templates / name).write_text(text, encoding="utf-8")
    (root / "governance/project/facts.yaml").write_text(facts, encoding="utf-8")
    for ident, other in {"DAEO-aaaa": front or GOOD, **(extra or {})}.items():
        (root / ".tickets" / f"{ident}.md").write_text(ticket_text(other), encoding="utf-8")
    return root


def codes(out: dict) -> list[tuple[str, str]]:
    return [(f["code"], f["detail"]) for f in out["findings"]]


def test_fills_the_brief_deterministically(tmp_path):
    root = plant(tmp_path)
    first, second = build(root, "engineer", "W2-900"), build(root, "engineer", "DAEO-aaaa")
    assert first == second and first["findings"] == []
    brief = first["brief"]
    assert brief.startswith("# Your assignment\n") and "name: brief" not in brief
    assert "Ticket DAEO-aaaa (W2-900). The summary paragraph." in brief
    assert "Tree: /w/W2-900 on w2/W2-900. Commit with {SUBJECT}." in brief  # a form key is left as written
    assert "Run gov accept W2-900 --root /w/W2-900." in brief
    assert "| S1 | S1 it works. | a test |" in brief and "| F1 | never breaks | a case |" in brief
    assert "Lead note: none\nnone\n" in brief and "Keep line gov accept" in brief
    assert "Gone line" not in brief and "{STEP:" not in brief  # TPL-2 S3: the switched-off line is dropped
    assert first["budget"] == 4000 and 0 < first["size"] < len(brief)


def test_designer_writes_in_its_tests_tree(tmp_path):
    root = plant(tmp_path)
    (root / "template/governance/kernel/templates/role-test-designer.md").write_text(ROLE_ENGINEER, encoding="utf-8")
    assert "Tree: /w/W2-900-tests on w2/W2-900-tests." in build(root, "independent-test-designer", "W2-900")["brief"]


def test_step_switch_changes_only_its_line(tmp_path):
    on = build(plant(tmp_path), "engineer", "W2-900")["brief"]
    off = build(plant(tmp_path / "b", facts=FACTS.replace('"on": true', '"on": false')), "engineer", "W2-900")["brief"]
    assert [line for line in on.split("\n") if not line.startswith("Keep line")] == off.split("\n")


def test_part_and_repair_fill_their_keys(tmp_path):
    root = plant(tmp_path)
    (tmp_path / "part.md").write_text("the lead knows X\n", encoding="utf-8")
    (tmp_path / "repair.txt").write_text("FAILED test_y\n", encoding="utf-8")
    brief = build(root, "engineer", "W2-900", part=str(tmp_path / "part.md"), repair=str(tmp_path / "repair.txt"))
    assert "Lead note: the lead knows X\nFAILED test_y\n" in brief["brief"]


@pytest.mark.parametrize("kind, wanted, unwanted", [("tests", "1. Make the tests.", "implement"),
                                                    ("build", "1. Build it with gov accept W2-900", "Make the tests")])
def test_lead_carries_only_its_run_block(tmp_path, kind, wanted, unwanted):
    brief = build(plant(tmp_path), "lead", "W2-900", run=kind)["brief"]
    tail = brief.split("End.\n", 1)[1]
    assert tail.startswith(f"\n## Your run: {kind} (only this section)\n**{kind}**:") and wanted in tail
    assert unwanted not in tail and "Common head line" not in brief and "Return line" not in brief
    assert "Keep line" not in tail  # the block ends at the section's first {STEP:} line


def test_run_goes_with_the_lead_only(tmp_path):
    root = plant(tmp_path)
    for role, run in (("lead", None), ("engineer", "build")):
        with pytest.raises(GovError) as raised:
            build(root, role, "W2-900", run=run)
        assert raised.value.code == "BRIEF_RUN_MISSING"


def test_refusals_name_each_finding(tmp_path):
    front = dict(GOOD, allowed_paths=[], depends_on=["DAEO-open", "W2-901"],
                 kpis={"success": ["no verify here", {"line": "x", "verify": " "}], "failure": ["F. Verify: ok"]})
    closed = dict(GOOD, id="DAEO-done", **{"external-ref": "W2-901"}, status="closed")
    t0 = T0.replace("End.", "Keep this until W2-901 lands. {NOT_A_KEY} {CMD:nope} {STEP:nope}")
    out = build(plant(tmp_path, front, t0=t0, extra={"DAEO-done": closed}), "engineer", "DAEO-aaaa")
    assert codes(out) == [("ALLOWED_PATHS_EMPTY", "DAEO-aaaa"), ("KPI_NO_VERIFY", "S1"), ("KPI_NO_VERIFY", "S2"),
                          ("DEPENDS_NOT_CLOSED", "DAEO-open"), ("UNTIL_CLOSED", "W2-901"),
                          ("PLACEHOLDER_LEFT", "NOT_A_KEY"), ("PLACEHOLDER_LEFT", "CMD:nope"),
                          ("PLACEHOLDER_LEFT", "STEP:nope")]


def test_advisory_items_only_warn(tmp_path):
    out = build(plant(tmp_path, dict(GOOD, non_goals=[], est_loc=401)), "engineer", "W2-900")
    assert out["findings"] == []
    assert out["warnings"] == [{"code": "NON_GOALS_MISSING", "detail": "DAEO-aaaa"},
                               {"code": "EST_LOC_OVER", "detail": "401"}]


def test_dependency_fields_from_the_date_on(tmp_path):
    new = dict(GOOD, created="2026-11-10T00:00:00Z")
    assert [c for c, _ in codes(build(plant(tmp_path), "engineer", "W2-900"))] == []  # created before the date
    out = build(plant(tmp_path / "b", new), "engineer", "W2-900")
    assert [c for c, _ in codes(out)] == ["READS_MISSING", "NEEDS_MISSING", "WAITS_ON_MISSING"]
    declared = dict(new, reads=[], needs=[], waits_on=["DAEO-aaaa — itself", {"ref": "docs/r.md", "reason": "r"},
                                                      {"ref": "DAEO-gone", "reason": "g"}])
    assert codes(build(plant(tmp_path / "c", declared), "engineer", "W2-900")) == [
        ("WAITS_ON_UNKNOWN", "docs/r.md"), ("WAITS_ON_UNKNOWN", "DAEO-gone")]


def test_command_output_and_refusal(tmp_path, capsys):
    root = plant(tmp_path)
    before = sorted((p, p.stat().st_mtime_ns) for p in tmp_path.rglob("*"))
    assert main(["brief", "engineer", "W2-900", "--root", str(root)]) == 0
    out, err = capsys.readouterr()
    assert out == build(root, "engineer", "W2-900")["brief"]
    assert "gov brief: SIZE " in err and "of 4000" in err
    assert main(["brief", "engineer", "W2-900", "--root", str(root), "--json"]) == 0
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["ok"] and set(envelope["result"]) == {"brief", "warnings", "size", "budget"}
    assert sorted((p, p.stat().st_mtime_ns) for p in tmp_path.rglob("*")) == before  # it writes nothing
    (root / ".tickets/DAEO-aaaa.md").write_text(ticket_text(dict(GOOD, allowed_paths=[])), encoding="utf-8")
    assert main(["brief", "engineer", "W2-900", "--root", str(root), "--json"]) == 1
    error = json.loads(capsys.readouterr().out)["error"]
    assert error["code"] == "BRIEF_NOT_READY"
    assert error["details"]["findings"] == [{"code": "ALLOWED_PATHS_EMPTY", "detail": "DAEO-aaaa"}]


def test_facts_schema_requires_a_date(tmp_path):
    import jsonschema
    import yaml

    repo = Path(__file__).resolve().parents[3]
    schema = json.loads((repo / "template/governance/kernel/schemas/facts.schema.json").read_text(encoding="utf-8"))
    facts = yaml.safe_load((repo / "governance/project/facts.yaml").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    assert isinstance(facts["ready"]["new_since"], str) and not list(validator.iter_errors(facts))
    assert list(validator.iter_errors(dict(facts, ready={"new_since": "soon"})))
