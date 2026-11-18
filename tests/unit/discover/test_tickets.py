"""Builder tests for ``gov discover``'s tickets and its commands (W2-36), each in a temporary project (DEC-322)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.discover import command, tickets  # noqa: E402
from gov.util.frontmatter import of_file  # noqa: E402

WORDS = "add CSV export to the report page"
CHANGE = "add-csv-export-report-page"


@pytest.fixture()
def project(tmp_path):
    root = tmp_path / "proj"
    (root / "governance/kernel/bin").mkdir(parents=True)
    shutil.copy(REPO / "template/governance/kernel/bin/tk", root / "governance/kernel/bin/tk")
    shutil.copytree(REPO / "template/openspec", root / "openspec")
    (root / ".tickets").mkdir()
    (root / "docs").mkdir()
    (root / "docs/report.md").write_text("Report page: CSV export.\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return root


def _args(**given):
    base = dict(words=[], profile=None, type=[], check=None, generate=None, ticket=None, paths=[], json=False,
                root=None)
    return type("Args", (), {**base, **given})()


def _open(root, **given):
    return command.act(root, _args(words=WORDS.split(), **given))


def test_discovery_writes_the_change_and_one_ticket(project):
    result = _open(project)
    folder = project / "openspec/changes" / CHANGE
    assert sorted(path.name for path in folder.iterdir()) == ["proposal.md", "readiness.yaml", "spec.md"]
    assert result["change"] == CHANGE and result["specification"] == f"SPEC-{CHANGE}"
    ticket = of_file(project / ".tickets" / f"{result['ticket']}.md")
    assert ticket["class"] == "specification" and ticket["role"] == "product-spec"
    assert ticket["discovers"] == CHANGE and "specification" not in ticket
    assert ticket["allowed_paths"] == [f"openspec/changes/{CHANGE}/**"]
    assert ticket["kpis"]["success"][0]["verify"] == f"gov discover --check {CHANGE}"
    assert (ticket["reads"], ticket["needs"], ticket["waits_on"]) == ([], [], [])
    assert "docs/report.md" in (folder / "spec.md").read_text(encoding="utf-8")
    assert result["briefs"] == [f"gov brief product-spec {result['ticket']}"]


def test_a_second_discovery_is_refused_and_writes_nothing(project):
    _open(project)
    before = sorted(path.name for path in (project / ".tickets").iterdir())
    with pytest.raises(GovError) as raised:
        _open(project)
    assert raised.value.code == "DISCOVER_EXISTS" and CHANGE in raised.value.message
    assert sorted(path.name for path in (project / ".tickets").iterdir()) == before


def test_no_words_and_only_stop_words_are_refused(project):
    for words in ([], ["the", "of"]):
        with pytest.raises(GovError) as raised:
            command.act(project, _args(words=words))
        assert raised.value.code == "DISCOVER_NO_WORDS"
    assert not (project / "openspec/changes").exists()


def test_standard_needs_a_type(project):
    with pytest.raises(GovError) as raised:
        _open(project, profile="STANDARD")
    assert raised.value.code == "DISCOVER_NO_TYPE"


def test_an_unknown_change_is_refused_for_each_form(project):
    for form in ("check", "generate", "ticket"):
        with pytest.raises(GovError) as raised:
            command.act(project, _args(**{form: "no-such-change"}, paths=["src/**"]))
        assert raised.value.code == "DISCOVER_CHANGE_NOT_FOUND" and "no-such-change" in raised.value.message


def test_generate_links_rows_in_order_and_is_idempotent(project):
    _open(project)
    readiness = project / "openspec/changes" / CHANGE / "readiness.yaml"
    before = readiness.read_text(encoding="utf-8")
    made = command.act(project, _args(generate=CHANGE))
    assert len(made["tickets"]) == 10
    by_key = {item["key"]: item["ticket"] for item in made["tickets"]}
    front = {key: of_file(project / ".tickets" / f"{ticket}.md") for key, ticket in by_key.items()}
    assert front["acceptance_tests"]["class"] == "test-design"
    assert sorted(front["acceptance_tests"]["depends_on"]) == sorted(t for k, t in by_key.items() if k != "acceptance_tests")
    assert front["inputs"]["class"] == "data" and front["scenarios"]["readiness_row"] == {
        "specification": f"SPEC-{CHANGE}", "n": 4, "key": "scenarios"}
    rows = yaml.safe_load(readiness.read_text(encoding="utf-8"))["rows"]
    assert {row["key"]: row["gap_ticket"] for row in rows if row["gap_ticket"]} == by_key
    assert readiness.read_text(encoding="utf-8").count("gap_ticket: null") == 16
    assert before.replace("gap_ticket: null", "gap_ticket: X").count("X") == 26
    again = readiness.read_text(encoding="utf-8")
    assert command.act(project, _args(generate=CHANGE))["tickets"] == []
    assert readiness.read_text(encoding="utf-8") == again


def test_research_rows_name_their_evidence_record(project):
    command.act(project, _args(words=WORDS.split(), profile="STANDARD", type=["performance-capacity"]))
    made = command.act(project, _args(generate=CHANGE))
    nfr = of_file(project / ".tickets" / f"{next(t['ticket'] for t in made['tickets'] if t['key'] == 'nfr')}.md")
    assert nfr["class"] == "research" and nfr["role"] == "research"
    assert f"docs/research/{CHANGE}/**" in nfr["allowed_paths"]
    assert any(f"docs/research/{CHANGE}/nfr.md" in item["verify"] for item in nfr["kpis"]["success"])
