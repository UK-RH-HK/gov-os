"""``gov queue`` lands a fix under a closed ticket (W2-201 fix X6, DEC-1219 (5)): the signal is a commit of the
branch with the ticket's ``Task:`` and a ``Fix:`` trailer; the fix lands with no second close and appends a ``fixes``
entry and a body line to the ticket's close record. Builder tests, regression evidence only."""
from __future__ import annotations

import pytest
import yaml

from gov.cli.errors import GovError
from gov.queue import checks, command

from queue_support import OTHER, TICKET, ticket_text

GREEN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}
GREEN2 = {"src/pkg/feature.py": "def twice(x):\n    return x * 2\n"}
RECORD = f"docs/close/{TICKET}/CL-{TICKET}.md"
PLANTED = ("---\n" + yaml.safe_dump({"id": f"CL-{TICKET}", "type": "close", "status": "ACTIVE", "task": TICKET,
                                     "created": "2026-11-01T00:00:00Z", "close": "queue", "commit": "abc"},
                                    sort_keys=False)
           + f"---\n\n# CL-{TICKET} — Close record for {TICKET}\nThe first close.\n")


def _close(project, record: bool = True):
    files = {f".tickets/{TICKET}.md": ticket_text(status="closed")}
    if record:
        files[RECORD] = PLANTED
    project.commit("close by hand", files=files)


def _record(project, rev="main"):
    text = project.git("show", f"{rev}:{RECORD}")
    _, front, body = text.split("---\n", 2)
    return yaml.safe_load(front), body


# -- the signal -----------------------------------------------------------------------------------------------

def test_fix_line_is_the_first_commit_with_the_ticket_s_task_and_a_fix(project):
    base = project.sha("main")
    project.git("checkout", "-q", "-b", "topic/f")
    project.commit("plain", f"Task: {TICKET}")
    project.commit("other", f"Task: {OTHER}", "Fix: not ours")
    project.commit("first", f"Task: {TICKET}", "Fix: the first line")
    project.commit("second", f"Task: {TICKET}", "Fix: the second line")
    tip = project.sha()
    project.git("checkout", "-q", "main")
    assert checks.fix_line(project.root, base, tip, TICKET) == "the first line"


@pytest.mark.parametrize("trailers", ((f"Task: {TICKET}",), (f"Task: {OTHER}", "Fix: a line"), ("Fix: a line",),
                                      (f"Task: {TICKET}", "Fix:   ")))
def test_no_fix_line_without_both_trailers_on_one_commit(project, trailers):
    base = project.sha("main")
    tip = project.branch("topic/p", GREEN, *trailers)
    assert checks.fix_line(project.root, base, tip, TICKET) is None


# -- the landing ----------------------------------------------------------------------------------------------

def test_a_fix_lands_on_a_closed_ticket_and_appends_to_its_close_record(project):
    _close(project)
    front_before, body_before = _record(project)
    tip = project.branch("topic/fix", GREEN, f"Task: {TICKET}", "Fix: twice doubles", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/fix"])
    assert code == 0 and result["landed"] == [TICKET]
    head = project.sha("main")
    assert result["closes"] == [{"ticket": TICKET, "close_record": RECORD, "commit": head, "fix": True,
                                 "fix_line": "twice doubles"}]
    message = project.git("log", "-1", "--format=%B", head)
    assert message.startswith(f"fix: {TICKET} (gov queue landed at {result['tested'][:12]})")
    assert f"Task: {TICKET}" in message
    assert project.status_of(TICKET, "main") == "closed"
    front, body = _record(project)
    [entry] = front.pop("fixes")
    assert front == front_before
    assert set(entry) == {"line", "branch", "tip", "tested", "landed"}
    assert (entry["line"], entry["branch"], entry["tip"], entry["tested"]) == (
        "twice doubles", "topic/fix", tip, result["tested"])
    assert str(entry["landed"]).endswith(("Z", "+00:00"))
    assert body.startswith(body_before.rstrip("\n"))
    assert body.rstrip("\n").splitlines()[-1] == f"- fix landed: twice doubles (topic/fix @ {tip[:12]})"
    assert project.git("status", "--porcelain") == ""

    tip2 = project.branch("topic/fix2", GREEN2, f"Task: {TICKET}", "Fix: again", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/fix2"])
    assert code == 0
    front, body = _record(project)
    assert [e["line"] for e in front["fixes"]] == ["twice doubles", "again"]
    lines = [line for line in body.splitlines() if line.startswith("- fix landed:")]
    assert lines == [f"- fix landed: twice doubles (topic/fix @ {tip[:12]})",
                     f"- fix landed: again (topic/fix2 @ {tip2[:12]})"]


def test_a_closed_ticket_with_no_record_gets_one_with_fixes(project):
    _close(project, record=False)
    tip = project.branch("topic/fix", GREEN, f"Task: {TICKET}", "Fix: a line", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/fix"])
    assert code == 0
    front, body = _record(project)
    assert [e["line"] for e in front["fixes"]] == ["a line"]
    assert f"- fix landed: a line (topic/fix @ {tip[:12]})" in body
    assert project.status_of(TICKET, "main") == "closed"


@pytest.mark.parametrize("trailers", ((f"Task: {TICKET}",), (f"Task: {OTHER}", "Fix: a line")))
def test_a_closed_ticket_s_plain_branch_is_refused(project, trailers):
    _close(project)
    base = project.sha("main")
    project.branch("topic/p", GREEN, *trailers, "Role: engineer")
    with pytest.raises(GovError) as refused:
        command.land(project.root, [f"{TICKET}=topic/p"])
    assert refused.value.code == "TICKET_CLOSED" and refused.value.exit_code == 1
    assert project.sha("main") == base


def test_a_closed_ticket_whose_branch_names_no_commit_is_refused_closed(project):
    _close(project)
    with pytest.raises(GovError) as refused:
        command.land(project.root, [f"{TICKET}=topic/none"])
    assert refused.value.code == "TICKET_CLOSED"


def test_a_fix_trailer_on_an_open_ticket_is_an_ordinary_landing(project):
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Fix: a line", "Role: engineer")
    result, code = command.land(project.root, [f"{TICKET}=topic/a"])
    assert code == 0 and project.status_of(TICKET, "main") == "closed"
    [entry] = result["closes"]
    assert "fix" not in entry and "fix_line" not in entry
    assert "fixes" not in _record(project)[0]


def test_the_dry_run_of_a_fix_names_it_and_changes_nothing(project, tmp_path):
    _close(project)
    project.branch("topic/fix", GREEN, f"Task: {TICKET}", "Fix: a line", "Role: engineer")
    project.branch("topic/b", {"src/pkg/gadget.py": "def gadget():\n    return 1  # b\n"}, f"Task: {OTHER}",
                   "Role: engineer")
    refs = project.git("for-each-ref")
    result, code = command.dry_run(project.root, [f"{TICKET}=topic/fix", f"{OTHER}=topic/b"],
                                   out=str(tmp_path / "out"))
    assert code == 0 and result["landed"] == [TICKET, OTHER]
    assert result["closes"] == [{"ticket": TICKET, "close_record": None, "commit": None, "fix": True,
                                 "fix_line": "a line"}]
    assert project.git("for-each-ref") == refs and project.git("status", "--porcelain") == ""
    assert "fixes" not in _record(project)[0]
