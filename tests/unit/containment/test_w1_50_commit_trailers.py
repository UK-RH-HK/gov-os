"""Builder tests for W1-50: a forward HEAD move is judged commit by commit.

Regression evidence only; the acceptance suite is
``tests/acceptance/W1-50/``.  These cover what that suite leaves to the
builder: how the commits of a move are read, how the close commit is
found, and that what cannot be read or is not decided is a finding.

Each test creates a small git repository in a temporary directory and
exercises ``take_snapshot`` and ``check_containment`` directly, without
running the kernel hooks.
"""

from __future__ import annotations

import json
import subprocess

_GIT_IDENTITY = (
    "-c", "user.name=W1-50 test",
    "-c", "user.email=w1-50@test.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "core.hooksPath=/dev/null",
)

FINDINGS_REL = ".gov-runtime/findings.jsonl"
TICKET = "DAEO-t01"
TICKET_FILE = f".tickets/{TICKET}.md"


def _git(project, *args):
    proc = subprocess.run(
        ["git", "-C", str(project), *_GIT_IDENTITY, *args],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, (
        f"git {' '.join(args)} failed: {proc.stderr.strip()}"
    )
    return proc.stdout


def _ticket(project, status):
    (project / TICKET_FILE).write_text(
        f"---\nid: {TICKET}\nstatus: {status}\nwbs_id: T-01\n"
        "role: engineer\nallowed_paths:\n- src/**\n---\n# T-01 Test\n")


def _make_project(tmp_path, status="in_progress"):
    """A minimal committed project with one engineer ticket."""
    project = tmp_path / "project"
    (project / ".tickets").mkdir(parents=True)
    (project / "src").mkdir()
    (project / ".gitignore").write_text(".gov-runtime/\n")
    (project / "README.md").write_text("# Test\n")
    (project / "src" / "main.py").write_text("VALUE = 1\n")
    _ticket(project, status)
    _git(project, "init", "-q", "-b", "main")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "initial")
    return project


def _commit(project, path, *trailers, message=("-m", "work")):
    target = project / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a") as f:
        f.write("changed\n")
    args = []
    for line in trailers:
        args += ["--trailer", line]
    _git(project, "add", "-A")
    _git(project, "commit", "-q", *message, *args)
    return _git(project, "rev-parse", "HEAD").strip()


def _findings(project):
    path = project / FINDINGS_REL
    if not path.is_file():
        return []
    lines = path.read_text("utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _check(project, work, role="orchestrator", subagent=None):
    """One call: the snapshot, *work*, the check.  Returns (report, findings)."""
    from gov.guard.containment import take_snapshot, check_containment

    take_snapshot(str(project), "toolu_w1_50")
    work()
    report = check_containment(
        project_root=str(project), role=role, ticket_id=TICKET,
        subagent_type=subagent, session_id="test-session",
        agent_type=subagent, command="work", tool_use_id="toolu_w1_50",
    )
    return report, _findings(project)


# ---------------------------------------------------------------
# Reading the commits of a move
# ---------------------------------------------------------------

def test_move_commits_reads_the_final_trailer_block_and_the_paths(tmp_path):
    from gov.guard.containment import _move_commits

    project = _make_project(tmp_path)
    old = _git(project, "rev-parse", "HEAD").strip()
    first = _commit(project, "src/a b.py", f"Task: {TICKET}",
                    "Role: engineer", "Implements: CAP-58.h")
    second = _commit(project, "README.md", message=(
        "-m", "body only", "-m", "Role: engineer", "-m", "Not a trailer."))
    commits = _move_commits(str(project), old, second)
    assert commits == [
        (second, [first], [], [], ["README.md"]),
        (first, [old], ["engineer"], [TICKET], ["src/a b.py"]),
    ]


def test_a_merge_commit_lists_only_what_it_changes_beyond_its_parents(tmp_path):
    from gov.guard.containment import _move_commits

    project = _make_project(tmp_path)
    old = _git(project, "rev-parse", "HEAD").strip()
    _git(project, "checkout", "-q", "-b", "side")
    _commit(project, "src/side.py")
    _git(project, "checkout", "-q", "main")
    _git(project, "merge", "-q", "--no-ff", "--no-commit", "side")
    (project / "README.md").write_text("# By the merge\n")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "merge")
    merge = _move_commits(str(project), old, "HEAD")[0]
    assert len(merge[1]) == 2 and merge[4] == ["README.md"]


def test_a_commit_list_that_cannot_be_read_is_a_finding(tmp_path):
    """A trailer value holding the list's own separator: flagged, not silent."""
    project = _make_project(tmp_path)
    report, findings = _check(project, lambda: _commit(
        project, "src/main.py", f"Task: {TICKET}", "Role: engi\x02neer"))
    assert report and [f["action"] for f in findings] == ["flagged"]
    assert "not a forward move" in findings[0]["reason"]


# ---------------------------------------------------------------
# The close commit (DEC-358)
# ---------------------------------------------------------------

def test_close_commit_is_the_latest_commit_where_the_status_becomes_closed(tmp_path):
    from gov.guard.containment import _close_commit

    project = _make_project(tmp_path)
    closes = []
    for status in ("closed", "in_progress", "closed"):
        _ticket(project, status)
        _git(project, "commit", "-q", "-am", status)
        closes.append(_git(project, "rev-parse", "HEAD").strip())
    # A later change of the file that leaves the status closed is no close.
    with open(project / TICKET_FILE, "a") as f:
        f.write("A note after the close.\n")
    _git(project, "commit", "-q", "-am", "note")
    assert _close_commit(str(project), "HEAD", TICKET_FILE) == closes[2]


def test_a_first_version_that_is_already_closed_is_no_close_commit(tmp_path):
    from gov.guard.containment import _close_commit

    project = _make_project(tmp_path, status="closed")
    assert _close_commit(str(project), "HEAD", TICKET_FILE) is None
    assert _close_commit(str(project), "HEAD", ".tickets/none.md") is None


def test_the_close_commit_itself_with_a_worker_s_trailers_is_a_finding(tmp_path):
    """Not decided (DP-13): the close commit is not before itself."""
    project = _make_project(tmp_path)

    def work():
        _ticket(project, "closed")
        _commit(project, "src/main.py", f"Task: {TICKET}", "Role: engineer")

    report, findings = _check(project, work)
    assert report and len(findings) == 1
    assert "closed ticket" in findings[0]["reason"]
    assert sorted(findings[0]["paths"]) == [TICKET_FILE, "src/main.py"]


# ---------------------------------------------------------------
# Cases the decisions leave unsaid: a finding
# ---------------------------------------------------------------

def test_a_role_owner_commit_brought_by_a_merge_is_a_finding(tmp_path):
    """Not decided (DP-11): the commit is new to HEAD's history in the call."""
    project = _make_project(tmp_path)
    _git(project, "checkout", "-q", "-b", "side")
    owner = _commit(project, "README.md", "Role: owner")
    _git(project, "checkout", "-q", "main")
    report, findings = _check(project, lambda: _git(
        project, "merge", "-q", "--no-ff", "-m", "merge", "side"))
    assert report and len(findings) == 1
    assert owner[:12] in findings[0]["reason"]
    assert findings[0]["paths"] == ["README.md"]


def test_in_a_worker_s_call_another_role_s_trailer_alone_is_a_finding(tmp_path):
    """DEC-319 names the Role trailer; no Task trailer stands next to it."""
    project = _make_project(tmp_path)
    report, findings = _check(
        project, lambda: _commit(project, "src/main.py", "Role: orchestrator"),
        role="engineer")
    assert report and len(findings) == 1
    assert findings[0]["paths"] == ["src/main.py"]
    assert findings[0]["role"] == "engineer"


def test_a_commit_inside_the_caller_s_paths_stays_silent(tmp_path):
    project = _make_project(tmp_path)
    report, findings = _check(
        project, lambda: _commit(project, "src/main.py", f"Task: {TICKET}",
                                 "Role: engineer"),
        role="engineer")
    assert report == "" and findings == []
