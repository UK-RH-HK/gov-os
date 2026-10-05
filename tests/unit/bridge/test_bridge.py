"""Builder tests for the proposal-to-ticket bridge (W1-14). Regression evidence only (DEC-136).

They cover what the acceptance tests leave to the builder: the ticket records its task number, a checkbox line
that is no well-formed task refuses the derivation, a ticket script that fails leaves no ticket behind, and how a
pattern is judged to cover the acceptance tests. Every project is a temporary directory (DEC-322).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.tasks import bridge, tickets  # noqa: E402

SPEC, CHANGE = "SPEC-zq14", "zq14-sample"
TEMPLATE = REPO / "template"
BLOCK = ("  ```yaml\n  role: engineer\n  class: implementation\n  profile: LITE\n  allowed_paths:\n  - src/part/**\n"
         "  kpis:\n    success:\n    - It works\n    failure: []\n  ```\n")


def _project(tmp_path, tasks):
    root = tmp_path / "project"  # the ticket script takes the id prefix from the folder name
    shutil.copytree(TEMPLATE / "openspec", root / "openspec")
    script = root / tickets.TK_REL
    script.parent.mkdir(parents=True)
    shutil.copyfile(TEMPLATE / "governance/kernel/bin/tk", script)
    script.chmod(0o755)
    (root / tickets.TICKETS_REL).mkdir()
    change = root / "openspec" / "changes" / CHANGE
    change.mkdir(parents=True)
    rows = yaml.safe_load((TEMPLATE / "openspec/schemas/feature-readiness/templates/readiness.yaml").read_text())
    rows = [{**row, "state": "PRESENT", "evidence": ["DEC-085"]} for row in rows["rows"]]
    (change / "readiness.yaml").write_text(yaml.safe_dump({"rows": rows}), encoding="utf-8")
    (change / "proposal.md").write_text(
        f"---\nid: {SPEC}\ntype: specification\nstatus: CLOSED\nstate_class: AUTHORITATIVE\nprofile: LITE\n"
        "spine: false\ncapability_types: []\n---\n# Proposal\n", encoding="utf-8")
    (change / "tasks.md").write_text("# Tasks\n\n## 1. Group\n\n" + tasks, encoding="utf-8")
    return root


def test_a_ticket_records_its_task_and_a_second_run_finds_it(tmp_path):
    root = _project(tmp_path, "- [ ] 1.1 Build the part\n" + BLOCK)
    first = bridge.derive(root, CHANGE)
    front = tickets.frontmatter(root / tickets.TICKETS_REL / f"{first['tickets'][0]['ticket']}.md")
    assert (front["task"], front["specification"], front["title"]) == ("1.1", SPEC, "Build the part")
    assert bridge.derive(root, CHANGE) == first


@pytest.mark.parametrize("line", ["- [ ] Build the part", "- [ ] 1.1", "- [ ] 1.1 Build it\n" + BLOCK + "- [ ] 1.1 Again"],
                         ids=["no-number", "no-description", "number-repeated"])
def test_a_checkbox_line_that_is_no_task_refuses_the_derivation(tmp_path, line):
    root = _project(tmp_path, line + "\n" + BLOCK)
    with pytest.raises(GovError) as caught:
        bridge.derive(root, CHANGE)
    assert caught.value.code == bridge.TASKS_INVALID
    assert list((root / tickets.TICKETS_REL).iterdir()) == []


def test_a_ticket_script_that_fails_leaves_no_ticket(tmp_path):
    root = _project(tmp_path, "- [ ] 1.1 Build the part\n" + BLOCK + "- [ ] 1.2 -x is no title for tk\n" + BLOCK)
    with pytest.raises(GovError) as caught:
        bridge.derive(root, CHANGE)
    assert caught.value.code == bridge.TICKET_FAILED
    assert list((root / tickets.TICKETS_REL).iterdir()) == []


@pytest.mark.parametrize("pattern, covers", [
    ("tests/acceptance/*/test_*.py", True), ("tests/*", True), ("tests/../tests/acceptance/**", True),
    ("tests/unit/**", False), ("tests/acceptance-data/**", False), ("src/**", False)])
def test_what_covers_the_acceptance_tests(pattern, covers):
    assert bridge._covers(pattern) is covers
