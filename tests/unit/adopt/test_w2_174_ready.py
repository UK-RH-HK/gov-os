"""W2-174 S3: after an apply, the ticket is READY by W2-152's own code and ``gov brief engineer`` builds its brief."""
from __future__ import annotations

import datetime
import shutil

from .test_w2_174_support import DONE, REPO, answers_file, gov, repo_with, ticket

from gov.adopt import verify_pass
from gov.brief.build import Tickets, ready_check
from gov.util.frontmatter import parse

TODAY = datetime.date(2026, 11, 13)


def adopted_fixture(tmp_path):
    """A repository with an old ticket (two lines, one verified), the kernel templates and its own filled facts file."""
    root = repo_with(tmp_path, {"DAEO-aa11": ticket("DAEO-aa11", success=["first line", DONE], failure=["second line"])})
    shutil.copytree(REPO / "template/governance/kernel/templates", root / "template/governance/kernel/templates")
    (root / "governance/project").mkdir(parents=True)
    # the shape of a filled facts file (every command filled, as an adopted project's CTO fills it after the defaults)
    shutil.copyfile(REPO / "governance/project/facts.yaml", root / "governance/project/facts.yaml")
    return root


def refusals(root):
    front = parse((root / ".tickets/DAEO-aa11.md").read_text(encoding="utf-8"), rstrip=True)
    return ready_check(front, Tickets(root), root, "2026-11-10")[0]


def test_ready_check_finds_no_kpi_no_verify_after_the_apply(tmp_path):
    root = adopted_fixture(tmp_path)
    assert [f["detail"] for f in refusals(root) if f["code"] == "KPI_NO_VERIFY"] == ["S1", "F1"]
    verify_pass.apply(root, answers_file(tmp_path, {"DAEO-aa11": {"S1": "a case", "F1": "another case"}}), "s", TODAY)
    assert [f for f in refusals(root) if f["code"] == "KPI_NO_VERIFY"] == []


def test_gov_brief_engineer_builds_the_brief_on_the_fixture_after_the_apply(tmp_path):
    root = adopted_fixture(tmp_path)
    code, _, err = gov("brief", "engineer", "DAEO-aa11", "--root", str(root))
    assert code == 1 and "KPI_NO_VERIFY" in err  # before the pass: refused by name
    gov("adopt", "--verify-apply", str(answers_file(tmp_path, {"DAEO-aa11": {"S1": "a case", "F1": "b case"}})),
        "--root", str(root), "--session", "s")
    code, out, err = gov("brief", "engineer", "DAEO-aa11", "--root", str(root))
    assert code == 0, err
    assert "a case" in out and "b case" in out  # the KPI table carries the appended clauses
