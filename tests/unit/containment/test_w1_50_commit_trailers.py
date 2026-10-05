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


def test_bytes_in_a_trailer_value_or_a_file_name_are_read_as_they_are(tmp_path):
    """Control characters, a trailing 0x1f, a newline in a name, and a name
    shaped like a trailer or a commit id: values and paths, never structure."""
    from gov.guard.containment import _move_commits

    project = _make_project(tmp_path)
    old = _git(project, "rev-parse", "HEAD").strip()
    role = "engineer\x02\x01" + "0" * 40 + "\x03orchestrator\x1f"
    names = ["Role: orchestrator", "0" * 40, "src/a\nb.py", "src/\x01:\x02 c"]
    for name in names:
        (project / name).write_text("x\n")
    sha = _commit(project, "src/main.py", f"Task: {TICKET}", f"Role: {role}",
                  "Role:", "role: second")
    assert _move_commits(str(project), old, sha) == [
        (sha, [old], sorted([role, "second"]), [TICKET],
         sorted(names + ["src/main.py"])),
    ]


def test_a_commit_with_an_unknown_role_made_of_chosen_bytes_names_its_paths(tmp_path):
    project = _make_project(tmp_path)
    report, findings = _check(project, lambda: _commit(
        project, "src/main.py", f"Task: {TICKET}", "Role: engineer\x1f"))
    assert report and len(findings) == 1
    assert findings[0]["paths"] == ["src/main.py"]
    assert "engineer\x1f" in findings[0]["reason"]


def test_a_commit_list_that_cannot_be_read_is_a_finding(tmp_path):
    """A file name that is not UTF-8: the move is flagged, not silent."""
    import os

    project = _make_project(tmp_path)

    def work():
        with open(os.fsencode(str(project)) + b"/src/\xff.py", "w") as f:
            f.write("x\n")
        _commit(project, "src/main.py", f"Task: {TICKET}", "Role: engineer")

    report, findings = _check(project, work)
    assert report and [f["action"] for f in findings] == ["flagged"]
    assert "not a forward move" in findings[0]["reason"]


def test_a_trailer_block_is_read_as_git_reads_one_with_default_settings():
    from gov.guard.containment import _role_and_task

    block = ("Implements: x\nrole : engineer\n  and more\nNot a trailer.\n"
             " Task: no\nTask:T-1\n\nRole=owner\n#Role: owner\nRole:\n")
    assert _role_and_task(block) == [
        ("role", "engineer and more"), ("task", "T-1"), ("role", "")]


def test_local_settings_and_replacement_refs_do_not_change_what_is_read(tmp_path):
    """The commits of a move, a ticket's file and its close commit are the
    real objects', whatever .git/config and refs/replace/ hold."""
    from gov.guard.containment import (
        _close_commit, _is_ancestor, _move_commits, _ticket_at)

    project = _make_project(tmp_path)
    root = str(project)
    old = _git(project, "rev-parse", "HEAD").strip()
    first = _commit(project, "src/main.py", f"Task: {TICKET}", "Role: engineer")
    _ticket(project, "closed")
    close = _commit(project, "README.md", "Role: owner")
    before = (_move_commits(root, old, close),
              _ticket_at(root, close, TICKET_FILE),
              _close_commit(root, close, TICKET_FILE))
    assert before[0][0][2:] == (["owner"], [], [TICKET_FILE, "README.md"])
    assert before[1]["status"] == "closed" and before[2] == close

    for key, value in (
            ("trailer.separators", "="), ("core.commentChar", "R"),
            ("trailer.roleplay.key", "Reviewed-by"), ("trailer.tasking.key", "X"),
            ("log.showRoot", "false"), ("diff.ignoreSubmodules", "all"),
            ("diff.renames", "true"), ("i18n.logOutputEncoding", "UTF-16")):
        _git(project, "config", "--local", key, value)
    twin = _git(project, "commit-tree", f"{old}^{{tree}}", "-p", old,
                "-m", "nothing").strip()
    _git(project, "replace", first, twin)
    _git(project, "replace", f"{close}:{TICKET_FILE}", f"{old}:{TICKET_FILE}")
    _git(project, "replace", f"{close}^{{tree}}", f"{old}^{{tree}}")
    assert "nothing" in _git(project, "cat-file", "commit", first)

    assert (_move_commits(root, old, close),
            _ticket_at(root, close, TICKET_FILE),
            _close_commit(root, close, TICKET_FILE)) == before
    assert _is_ancestor(root, first, close)


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
# The ticket's file at HEAD and in the working tree disagree
# (DP-14, not decided): the commit passes only if both allow it
# ---------------------------------------------------------------

def _engineer_commit_with_the_ticket_file_edited(project, status=None,
                                                 paths=None, path="src/main.py"):
    """An engineer's commit of *path*, then the ticket's file edited and
    not committed.  Returns the findings."""
    def work():
        _commit(project, path, f"Task: {TICKET}", "Role: engineer")
        text = (project / TICKET_FILE).read_text()
        if status:
            text = text.replace("status: " + text.split("status: ")[1]
                                .split("\n")[0], f"status: {status}")
        if paths:
            text = text.replace("- src/**", f"- {paths}")
        (project / TICKET_FILE).write_text(text)

    return _check(project, work)[1]


def test_a_ticket_closed_only_in_the_working_tree_is_a_finding(tmp_path):
    project = _make_project(tmp_path)
    findings = _engineer_commit_with_the_ticket_file_edited(project, "closed")
    assert len(findings) == 1 and "closed ticket" in findings[0]["reason"]
    assert findings[0]["paths"] == ["src/main.py"]


def test_a_ticket_started_only_in_the_working_tree_is_a_finding(tmp_path):
    project = _make_project(tmp_path, status="open")
    findings = _engineer_commit_with_the_ticket_file_edited(
        project, "in_progress")
    assert len(findings) == 1 and findings[0]["paths"] == ["src/main.py"]


def test_a_path_only_one_of_the_two_files_allows_is_a_finding(tmp_path):
    # Only the working tree's file allows docs/**; only HEAD's allows src/**.
    for path in ("docs/a.md", "src/main.py"):
        project = _make_project(tmp_path / path.replace("/", "_"))
        findings = _engineer_commit_with_the_ticket_file_edited(
            project, paths="docs/**", path=path)
        assert len(findings) == 1 and findings[0]["paths"] == [path]


def test_a_ticket_file_that_is_not_committed_names_no_ticket(tmp_path):
    project = _make_project(tmp_path)

    def work():
        _commit(project, "src/main.py", "Task: DAEO-t02", "Role: engineer")
        (project / ".tickets/DAEO-t02.md").write_text(
            (project / TICKET_FILE).read_text().replace(TICKET, "DAEO-t02"))

    findings = _check(project, work)[1]
    assert "not committed at HEAD" in findings[0]["reason"]
    assert findings[0]["paths"] == ["src/main.py"]


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


def test_role_owner_with_characters_inside_the_word_that_do_not_show_is_a_finding(tmp_path):
    """The behaviour names characters around the word; inside it is not said."""
    project = _make_project(tmp_path)
    report, findings = _check(project, lambda: _commit(
        project, "README.md", "Role:  Ow​ner\x0c\x7f"))
    assert report and len(findings) == 1
    assert "Role: owner commit" in findings[0]["reason"]
    assert findings[0]["paths"] == ["README.md"]


def test_a_committed_path_behind_a_linked_directory_is_a_finding(tmp_path):
    """Inside the commit's own paths by its name, but a directory on the way
    to it is a symbolic link in the working tree: not judged by where the
    link leads, and not silent."""
    import shutil

    for role in ("orchestrator", "engineer"):
        project = _make_project(tmp_path / role)

        def work():
            _commit(project, "src/deep/a.py", f"Task: {TICKET}",
                    "Role: engineer")
            shutil.rmtree(project / "src" / "deep")
            (project / "src" / "deep").symlink_to(project / "src")

        report, findings = _check(project, work, role=role)
        assert report and "src/deep/a.py" in findings[0]["paths"]


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


# ---------------------------------------------------------------
# DEC-390: DP-15, DP-16, and what the check's git calls read
# ---------------------------------------------------------------

def test_a_merge_commit_with_an_earlier_other_parent_lists_its_change_against_its_first_parent(tmp_path):
    from gov.guard.containment import _move_commits

    project = _make_project(tmp_path)
    earlier = _git(project, "rev-parse", "HEAD").strip()
    old = _commit(project, "src/main.py")
    merge = _git(project, "commit-tree", f"{earlier}^{{tree}}", "-p", old,
                 "-p", earlier, "-m", "undo").strip()
    assert _move_commits(str(project), old, merge) == [
        (merge, [old, earlier], [], [], ["src/main.py"])]


def test_a_worker_s_commit_of_a_ticket_file_is_a_finding_and_an_orchestrator_s_is_not(tmp_path):
    for role, expected in (("engineer", [TICKET_FILE]), ("orchestrator", None)):
        project = _make_project(tmp_path / role)

        def work():
            (project / "src" / "main.py").write_text("VALUE = 2\n")
            _commit(project, TICKET_FILE, f"Task: {TICKET}", f"Role: {role}")

        report, findings = _check(project, work)
        if expected is None:
            assert report == "" and findings == []
        else:
            assert report and [f["paths"] for f in findings] == [expected]


def test_grafts_a_shallow_file_and_inherited_variables_do_not_change_what_is_read(tmp_path, monkeypatch):
    from gov.guard.containment import _is_ancestor, _move_commits

    project = _make_project(tmp_path)
    old = _git(project, "rev-parse", "HEAD").strip()
    first = _commit(project, "README.md", "Role: owner")
    second = _commit(project, "src/main.py")
    expected = [(second, [first], [], [], ["src/main.py"]),
                (first, [old], ["owner"], [], ["README.md"])]
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    for name in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY"):
        monkeypatch.setenv(name, str(other / ".git"))
    monkeypatch.setenv("GIT_GRAFT_FILE", str(project / ".git" / "info" / "grafts"))
    for hiding in ("info/grafts", "shallow"):
        target = project / ".git" / hiding
        target.write_text(f"{second} {old}\n" if hiding == "info/grafts"
                          else f"{second}\n")
        assert _move_commits(str(project), old, second) == expected
        assert _is_ancestor(str(project), first, second)
        target.unlink()
