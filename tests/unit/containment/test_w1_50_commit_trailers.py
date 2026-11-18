"""Builder tests for W1-50: a forward HEAD move is judged commit by commit.

Regression evidence only; the acceptance suite is
``tests/acceptance/W1-50/``.  These cover what that suite leaves to the
builder: how a trailer block is read, how the close commit is found and
how a merge commit is read.  The cases that went through the retired
post-command check (``take_snapshot``, ``check_containment``) went with
it (EMERGENCY-2 6.1); ``judge_commits``' own are in test_judge_commits.py.

Each test creates a small git repository in a temporary directory.
"""

from __future__ import annotations

import subprocess

_GIT_IDENTITY = (
    "-c", "user.name=W1-50 test",
    "-c", "user.email=w1-50@test.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "core.hooksPath=/dev/null",
)

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


# ---------------------------------------------------------------
# Reading the commits of a move
# ---------------------------------------------------------------

def test_a_trailer_block_is_read_as_git_reads_one_with_default_settings():
    from gov.containment.commits import _role_and_task

    block = ("Implements: x\nrole : engineer\n  and more\nNot a trailer.\n"
             " Task: no\nTask:T-1\n\nRole=owner\n#Role: owner\nRole:\n")
    assert _role_and_task(block) == [
        ("role", "engineer and more"), ("task", "T-1"), ("role", "")]


# ---------------------------------------------------------------
# The close commit (DEC-358)
# ---------------------------------------------------------------

def test_close_commit_is_the_latest_commit_where_the_status_becomes_closed(tmp_path):
    from gov.containment.commits import _close_commit

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
    from gov.containment.commits import _close_commit

    project = _make_project(tmp_path, status="closed")
    assert _close_commit(str(project), "HEAD", TICKET_FILE) is None
    assert _close_commit(str(project), "HEAD", ".tickets/none.md") is None


# ---------------------------------------------------------------
# The ticket's file at HEAD and in the working tree disagree
# (DP-14, not decided): the commit passes only if both allow it
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# Cases the decisions leave unsaid: a finding
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# DEC-394, DEC-398: a merge read by the merge base; DP-16, DP-17,
# and what the check's git calls read
# ---------------------------------------------------------------

def _branch_commit(project, branch, path, start="main"):
    _git(project, "checkout", "-q", "-B", branch, start)
    sha = _commit(project, path)
    _git(project, "checkout", "-q", "main")
    return sha


def test_read_merge_tells_a_parent_s_change_from_the_merge_commit_s_own(tmp_path):
    from gov.containment.merge import read_merge

    project = _make_project(tmp_path)
    _branch_commit(project, "side", "src/side.py")
    _commit(project, "README.md")
    _git(project, "merge", "-q", "--no-ff", "--no-commit", "side")
    (project / "src" / "main.py").unlink()
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "merge")
    reading = read_merge(str(project), _git(project, "rev-parse", "HEAD").strip())
    # DEC-410, DP-22: what the first parent brought is in brought too.
    assert (reading.own, reading.brought) == (
        ["src/main.py"], ["README.md", "src/side.py"])


def test_read_merge_puts_a_parent_s_change_the_merge_commit_drops_in_own(tmp_path):
    from gov.containment.merge import read_merge

    project = _make_project(tmp_path)
    earlier = _git(project, "rev-parse", "HEAD").strip()
    later = _commit(project, "src/main.py")
    # The parents turned round (DEC-403): nothing differs from the first.
    merge = _git(project, "commit-tree", f"{earlier}^{{tree}}", "-p", earlier,
                 "-p", later, "-m", "drop").strip()
    assert read_merge(str(project), merge) == (["src/main.py"], [])
    # Each side's change of its own path is brought, whichever is first
    # (DEC-410, DP-22: brought is the complement of own).
    side = _branch_commit(project, "side", "src/side.py", start=earlier)
    _git(project, "merge", "-q", "--no-ff", "-m", "merge", "side")
    tree = _git(project, "rev-parse", "HEAD^{tree}").strip()
    both = ["src/main.py", "src/side.py"]
    assert read_merge(str(project), _git(
        project, "rev-parse", "HEAD").strip()) == ([], both)
    turned = _git(project, "commit-tree", tree, "-p", side, "-p", later,
                  "-m", "turned").strip()
    assert read_merge(str(project), turned) == ([], both)


def test_read_merge_puts_an_acceptance_test_both_sides_changed_in_own(tmp_path):
    """DEC-410, DP-24: whichever side's content the merge commit holds,
    also when both sides made the same change; a source file is read as
    before."""
    from gov.containment.merge import read_merge

    project = _make_project(tmp_path)
    test, source = "tests/acceptance/T-01/test_a.py", "src/main.py"
    side = _branch_commit(project, "side", test)
    _git(project, "checkout", "-q", "side")
    _commit(project, source)
    _git(project, "checkout", "-q", "main")
    # The same change of the test on main, another of the source file.
    _git(project, "checkout", "-q", side, "--", test)
    _git(project, "commit", "-q", "-m", "the same change")
    (project / source).write_text("VALUE = 2\n")
    _git(project, "commit", "-q", "-a", "-m", "main's")
    _git(project, "merge", "-q", "--no-ff", "-X", "theirs", "-m", "merge", "side")
    head = _git(project, "rev-parse", "HEAD").strip()
    assert read_merge(str(project), head) == ([test], [source])
    # Another change of the test on main: the merge takes the side's.
    _git(project, "reset", "-q", "--hard", "HEAD^")
    _commit(project, test)
    _git(project, "merge", "-q", "--no-ff", "-X", "theirs", "-m", "merge", "side")
    head = _git(project, "rev-parse", "HEAD").strip()
    assert read_merge(str(project), head) == ([test], [source])


def test_read_merge_reads_the_other_parents_of_an_octopus_against_each_other(tmp_path):
    from gov.containment.merge import read_merge

    project = _make_project(tmp_path)
    head = _git(project, "rev-parse", "HEAD").strip()
    _branch_commit(project, "q", "src/q.py")
    one = _branch_commit(project, "one", "src/q.py", start="q")
    other = _branch_commit(project, "other", "src/other.py", start="q")
    # The tree is the third parent's: the second parent's later change
    # of src/q.py is dropped, although the third brought the path
    # against the first.
    octopus = _git(project, "commit-tree", f"{other}^{{tree}}", "-p", head,
                   "-p", one, "-p", other, "-m", "octopus").strip()
    assert read_merge(str(project), octopus) == (
        ["src/q.py"], ["src/other.py"])


def test_read_merge_starts_six_git_processes_for_two_parents(tmp_path, monkeypatch):
    from gov.containment import merge as containment_merge

    project = _make_project(tmp_path)
    _branch_commit(project, "side", "src/side.py")
    for n in range(20):
        _commit(project, f"src/more{n}.py")
    _git(project, "merge", "-q", "--no-ff", "-m", "merge", "side")
    calls = []
    real = containment_merge._git
    monkeypatch.setattr(containment_merge, "_git",
                        lambda *a, **k: calls.append(a) or real(*a, **k))
    containment_merge.read_merge(
        str(project), _git(project, "rev-parse", "HEAD").strip())
    assert len(calls) == 6


def test_read_merge_bounds_its_git_processes_by_the_number_of_parents(tmp_path, monkeypatch):
    import pytest
    from gov.containment import merge as containment_merge
    from gov.containment.merge import MAX_PARENTS, MergeReadError

    project = _make_project(tmp_path)
    head = _git(project, "rev-parse", "HEAD").strip()
    sides = [_branch_commit(project, f"s{n}", f"src/s{n}.py")
             for n in range(MAX_PARENTS)]
    calls = []
    real = containment_merge._git
    monkeypatch.setattr(containment_merge, "_git",
                        lambda *a, **k: calls.append(a) or real(*a, **k))

    def octopus(others, tree):
        parents = [a for p in (head, *others) for a in ("-p", p)]
        return _git(project, "commit-tree", tree, *parents, "-m",
                    "octopus").strip()

    # Nine parents, each side on top of the first: the commit, a diff
    # for each parent, a merge base for each of the 36 pairs and one
    # diff from the first parent to each side.
    _git(project, "merge", "-q", "--no-ff", "-m", "octopus",
         *(f"s{n}" for n in range(8)))
    merged = _git(project, "rev-parse", "HEAD").strip()
    assert containment_merge.read_merge(str(project), merged) == (
        [], [f"src/s{n}.py" for n in range(8)])
    assert len(calls) == 1 + 9 + 36 + 8
    # The most parents that are read; the tree drops every side's change.
    most = octopus(sides[:MAX_PARENTS - 1], f"{head}^{{tree}}")
    assert containment_merge.read_merge(str(project), most) == (
        sorted(f"src/s{n}.py" for n in range(MAX_PARENTS - 1)), [])
    # One parent more is refused after the one process that lists them.
    del calls[:]
    with pytest.raises(MergeReadError):
        containment_merge.read_merge(
            str(project), octopus(sides, f"{head}^{{tree}}"))
    assert len(calls) == 1


def test_read_merge_refuses_a_commit_argument_that_is_not_the_commit_s_own_id(tmp_path):
    import pytest
    from gov.containment.merge import MergeReadError, read_merge

    project = _make_project(tmp_path)
    _branch_commit(project, "side", "src/side.py")
    _git(project, "merge", "-q", "--no-ff", "-m", "merge", "side")
    merge = _git(project, "rev-parse", "HEAD").strip()
    _git(project, "tag", "-a", "-m", "tag", "merged", merge)
    _git(project, "branch", "0123456789abcdef" * 4, merge)
    for commit in (_git(project, "rev-parse", "refs/tags/merged").strip(),
                   "0123456789abcdef" * 4):
        with pytest.raises(MergeReadError):
            read_merge(str(project), commit)
    assert read_merge(str(project), merge) == ([], ["src/side.py"])


def test_read_merge_of_an_octopus_fails_closed_when_one_parent_has_no_merge_base(tmp_path):
    from gov.containment.merge import read_merge

    project = _make_project(tmp_path)
    side = _branch_commit(project, "side", "src/side.py")
    head = _git(project, "rev-parse", "HEAD").strip()
    tree = _git(project, "rev-parse", "side^{tree}").strip()
    ordinary = _git(project, "commit-tree", tree, "-p", head, "-p", side,
                    "-m", "merge").strip()
    assert read_merge(str(project), ordinary) == ([], ["src/side.py"])
    island = _git(project, "commit-tree", tree, "-m", "island").strip()
    for parents in ((side, island), (island, side)):
        octopus = _git(project, "commit-tree", tree, "-p", head, "-p",
                       parents[0], "-p", parents[1], "-m", "octopus").strip()
        assert read_merge(str(project), octopus) == (["src/side.py"], [])


def test_read_merge_fails_closed_with_several_merge_bases(tmp_path):
    from gov.containment.merge import read_merge

    project = _make_project(tmp_path)
    a = _branch_commit(project, "a", "src/a.py")
    b = _branch_commit(project, "b", "src/b.py")
    _git(project, "checkout", "-q", "a")
    _git(project, "merge", "-q", "--no-ff", "-m", "a takes b", b)
    _git(project, "checkout", "-q", "b")
    _git(project, "merge", "-q", "--no-ff", "-m", "b takes a", a)
    _commit(project, "src/later.py")
    _git(project, "checkout", "-q", "a")
    _git(project, "merge", "-q", "--no-ff", "-m", "criss-cross", "b")
    assert len(_git(project, "merge-base", "--all", "HEAD^1", "HEAD^2").split()) == 2
    head = _git(project, "rev-parse", "HEAD").strip()
    assert read_merge(str(project), head) == (["src/later.py"], [])
    # Fail closed for every parent (DEC-403): with the parents turned
    # round and the first parent's tree, what differs from the other
    # parent is the merge commit's own.
    turned = _git(project, "commit-tree", f"{head}^1^{{tree}}", "-p",
                  f"{head}^1", "-p", "b", "-m", "turned").strip()
    assert read_merge(str(project), turned) == (["src/later.py"], [])


def test_read_merge_raises_for_a_commit_that_is_no_merge_and_for_one_it_cannot_read(tmp_path, monkeypatch):
    import pytest
    from gov.containment import merge as containment_merge
    from gov.containment.merge import MergeReadError, read_merge

    project = _make_project(tmp_path)
    assert issubclass(MergeReadError, ValueError)  # the check's finding
    with pytest.raises(MergeReadError):
        # a commit without a parent
        read_merge(str(project), _git(project, "rev-parse", "HEAD").strip())
    with pytest.raises(MergeReadError):
        read_merge(str(project), _commit(project, "README.md"))
    with pytest.raises(MergeReadError):
        read_merge(str(project), "0" * 40)
    with pytest.raises(MergeReadError):
        read_merge(str(tmp_path), "0" * 40)  # no repository
    # What is not a full commit id never reaches git (DEC-403, F3).
    monkeypatch.setattr(containment_merge, "_git", None)
    for commit in ("", "HEAD", "--all", "-1", "0" * 39, "A" * 40,
                   "0" * 40 + "\n", None):
        with pytest.raises(MergeReadError):
            read_merge(str(project), commit)


# ---------------------------------------------------------------
# A move whose merge commits need too many git processes
# ---------------------------------------------------------------

def test_the_bound_of_a_move_leaves_room_for_ordinary_integrations():
    from gov.containment.merge import (
        MAX_MOVE_PROCESSES, MAX_PARENTS, processes)

    assert (processes(2), processes(9), processes(MAX_PARENTS)) == (6, 118, 853)
    assert 500 * processes(2) <= MAX_MOVE_PROCESSES < 4 * processes(MAX_PARENTS)

