"""W2-42a reopened, R4/R5 second batch (td-11): a revision-colon-path whose path the guard cannot place, an object
named by its blob id alone, and git's own ``--output`` write (DEC-1157 (12), DEC-1180 (4), DEC-1128, DEC-1133; the
ticket's S12 and F3).

S12: ``git diff REV:PATH REV:PATH`` and ``git show REV:PATH`` are judged as reads of those paths, under the read rules
the path names; a revision word that names no commit, tree or blob is refused, not passed. F3: a call that writes into
a walled path or reads a refused one is never let through (a fail-open).

The behaviour pinned here (the lead's probe of the head, each form checked through ``decide()``):

1. In ``<rev>:<path>`` the path starts at the top of the tree ``<rev>`` names. When ``<rev>`` names a tree that is not
   the commit's top (a subtree's id ``SUB``, the hidden folder's own tree id ``HTREE``), the path does not say where
   the blob lives, so it cannot be judged against the parts refused to the session: for a session with a refused part
   (research and engineer here, both measured by the planted evaluation set) it is refused by a ruled refusal (a deny
   whose reason is a rule's text: no exception, not the catch-all, not a ``PolicyError`` turned into a refusal).
2. An object named by its blob id alone that git shows as a file's text (``git cat-file blob BLOB``, ``git cat-file -p
   BLOB``) is refused to such a session, as ``git show BLOB`` already is; forms that show no file text (``-t``, ``-s``,
   ``-e``), a commit object, and blob refs of visible paths under ``HEAD`` stay allowed.
3. git's own ``--output=<file>`` / ``--output <file>`` (git diff, git show, git log) writes that file: for the engineer,
   whose ticket allows ``src/**`` only, each form writing ``tests/acceptance/X/zz.txt`` is refused by the Bash write
   refusal, which names that file; also after ``git -C <root>`` (from ``docs/``) and after ``cd tests &&`` with the
   relative path. ``--output`` into ``src/`` stays allowed.

Real git (2.43.0), run in a scratch repository of the same shape under ``$TMPDIR`` on 2026-11-14: every form of 1 and
2 above exits 0 and prints the hidden file's text (``git diff SUB:hidden/q01.txt HEAD:docs/a.md``, both sides swapped,
``git diff HTREE:q01.txt HEAD:docs/a.md``, ``git show SUB:hidden/q01.txt``, ``git show HTREE:q01.txt``, ``git cat-file
-p SUB:hidden/q01.txt``, ``git cat-file blob HTREE:q01.txt``, ``git cat-file blob BLOB``, ``git cat-file -p BLOB``);
the guards ``git cat-file -t/-s/-e BLOB``, ``git cat-file -p HEAD``, ``git show HEAD:docs/a.md``, ``git diff
HEAD:docs/a.md HEAD:docs/b.md`` and ``git cat-file -p HEAD:docs/a.md`` print no hidden text. Every ``--output`` form
of 3 exits 0 and creates ``tests/acceptance/X/zz.txt`` (the diff forms and the log forms write the patch; ``git show
--output=… HEAD:docs/a.md`` creates the file empty, the blob going to standard output; ``HEAD~0 HEAD`` creates it
empty): from the top, after ``git -C <root>`` and after ``cd tests`` with ``acceptance/X/zz.txt``.

The planted repository has two commits: the first adds every file, the second changes ``docs/a.md`` only. The brief
named one commit; the second is there because ``git log -p -1 --output=…`` (no path, no range) is refused in a planted
repository by the hidden-part read rule whatever its write (the judge takes the whole history's patch, which holds
the hidden file), so the log forms here are limited to ``HEAD~1..HEAD`` or ``-- docs/a.md`` (real git: each writes
the second commit's patch, no hidden text), where only the write can decide.

- ``test_r4_*`` (S12): group 1, a path under a tree that is not the commit's top, refused ruled; group 2, a blob id
  alone shown as text, refused ruled, and the guards that stay allowed; group 3's guard, ``--output`` into ``src/``.
- ``test_r45_failure_*`` (F3): group 1 through the five-rule hook; group 3, the ``--output`` writes into
  ``tests/acceptance/X/``, refused by the write refusal.
"""
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
HOOK = os.path.join(HERE, "fixtures", "hook", "pretooluse.py")
SESSION = ("TMPDIR", "GOV_ROLE", "GOV_TICKET", "CLAUDE_PROJECT_DIR", "GOV_HEAVY_SLOT")
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
ERROR_TAIL = ": the call is refused (fail closed, DEC-820)"  # a PolicyError turned into a refusal
CATCH = "the guard could not work out the reads this session is refused"  # the catch-all

SET = "w242d"
SET_DIR = f"fixtures/evaluation/{SET}"
HID = f"{SET_DIR}/hidden/q01.txt"
T = "tests/acceptance/X/zz.txt"  # no engineer may write it
A = "src/out.txt"  # inside the engineer's allowed paths
ENGINEER = ("engineer", "DAEO-03ub")
RESEARCH = ("research", None)
WHO = [pytest.param(RESEARCH, id="research"), pytest.param(ENGINEER, id="engineer")]
TICKET = """---
id: DAEO-03ub
status: in_progress
type: task
role: engineer
wbs_id: W2-42a
allowed_paths:
- src/**
---
# A stand-in of the engineer's ticket for the R4/R5 second batch
"""
PATH_MAP = (f"evaluation_sets:\n  {SET}:\n    visible: [\"docs/a.md\", \"docs/b.md\"]\n"
            f"    hidden: [\"{SET_DIR}/hidden/**\"]\n"
            "    measures:\n      roles: [research, engineer]\n")


def _git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(GIT + list(args), cwd=cwd, capture_output=True, text=True, env=env, check=True,
                          timeout=60).stdout.strip()


def _write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


@pytest.fixture(scope="module")
def planted(tmp_path_factory):
    """``{"root", "SUB", "HTREE", "BLOB"}``: the planted project (real path) and the ids git gives for the set's
    subtree, the hidden folder's tree and the hidden file's blob."""
    root = os.path.join(os.path.realpath(str(tmp_path_factory.mktemp("w242a-r4b"))), "proj")
    for rel, text in (("governance/project/path-map.yaml", PATH_MAP), (".tickets/DAEO-03ub.md", TICKET),
                      (HID, "hidden q01\n"), ("docs/a.md", "a1\n"), ("docs/b.md", "b1\n"),
                      ("src/ok.py", "ok = 1\n")):
        _write(root, rel, text)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "one")
    _write(root, "docs/a.md", "a2\n")
    _git(root, "commit", "-q", "-am", "two")
    os.makedirs(os.path.join(root, "tests", "acceptance", "X"))
    ids = {"SUB": _git(root, "rev-parse", f"HEAD:{SET_DIR}"),
           "HTREE": _git(root, "rev-parse", f"HEAD:{SET_DIR}/hidden"),
           "BLOB": _git(root, "rev-parse", f"HEAD:{HID}")}
    assert [_git(root, "cat-file", "-t", ids[k]) for k in ("SUB", "HTREE", "BLOB")] == ["tree", "tree", "blob"]
    return dict(ids, root=root)


@pytest.fixture(autouse=True)
def quiet_session(tmp_path, monkeypatch):
    """No session variable; the case's own HOME (no runs root, no key file of the machine)."""
    for name in SESSION:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "home").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))


def fill(template, planted):
    return template.format(root=planted["root"], t=T, a=A, **{k: planted[k] for k in ("SUB", "HTREE", "BLOB")})


def decided(command, root, who, cwd=None):
    """``(exception, (decision, why))`` of the product's entry."""
    from gov.guard.decide import decide
    role, ticket = who
    try:
        return None, decide("Bash", {"command": command}, root, role, ticket, cwd=cwd or root, flag="open")
    except Exception as exc:  # noqa: BLE001 - an exception is rule ``error``
        return exc, None


def show(command, cwd):
    return f"\n--- the command (cwd {cwd}) ---\n{command}"


def assert_refused_ruled(command, root, who, cwd=None):
    """A deny whose reason is a rule's text: no exception, not the catch-all, not a PolicyError turned refusal."""
    exc, got = decided(command, root, who, cwd)
    assert exc is None, f"decide() raised {type(exc).__name__}: {exc}{show(command, cwd)}"
    assert CATCH not in got[1], f"refused only by the catch-all (an exception): {got[1]}{show(command, cwd)}"
    assert not got[1].endswith(ERROR_TAIL), f"the judge raised a PolicyError: {got[1]}{show(command, cwd)}"
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"


def assert_allowed(command, root, who, cwd=None):
    exc, got = decided(command, root, who, cwd)
    assert exc is None, f"decide() raised {type(exc).__name__}: {exc}{show(command, cwd)}"
    assert got == ("allow", ""), f"want allow, got {got}{show(command, cwd)}"


def assert_write_refused(command, root, cwd=None):
    """The engineer's call is refused because it writes T: a deny whose reason names T (resolved from the top, never
    from ``docs/``)."""
    exc, got = decided(command, root, ENGINEER, cwd)
    assert exc is None, f"decide() raised {type(exc).__name__}: {exc}{show(command, cwd)}"
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
    assert T in got[1], f"want the write refusal naming {T}, got: {got[1]}{show(command, cwd)}"
    assert os.path.join("docs", T) not in got[1], f"the write is resolved from docs/: {got[1]}{show(command, cwd)}"


def hook(command, root, who, cwd=None):
    """The five-rule hook as Claude Code runs it (fixtures/hook/pretooluse.py, this tree's ``src`` on
    ``PYTHONPATH``): ``(decision, reason, exit code)``; exit 2 is a refusal by an error (rule ``error``)."""
    role, ticket = who
    env = {k: v for k, v in os.environ.items() if k not in SESSION and k != "PYTHONPATH"}
    env.update(PYTHONPATH=SRC, GOV_ROLE=role, CLAUDE_PROJECT_DIR=root, PYTHONDONTWRITEBYTECODE="1")
    if ticket:
        env["GOV_TICKET"] = ticket
    event = {"session_id": "w2-42a-r4b", "hook_event_name": "PreToolUse", "tool_name": "Bash",
             "tool_input": {"command": command}, "cwd": cwd or root, "agent_type": None}
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(event), capture_output=True, text=True, env=env,
                       cwd=cwd or root, timeout=120)
    if p.returncode == 2:
        return "deny", "ERROR: " + p.stderr[-800:], 2
    if p.returncode:
        return "crash", f"exit {p.returncode}: " + p.stderr[-800:], p.returncode
    if not p.stdout.strip():
        return "allow", "", 0
    out = json.loads(p.stdout)["hookSpecificOutput"]
    return out["permissionDecision"], out["permissionDecisionReason"], 0


# -- group 1: a revision-colon-path under a tree that is not the commit's top ----------------------------------------------

G1 = [
    pytest.param("git diff {SUB}:hidden/q01.txt HEAD:docs/a.md", id="diff-subtree-path-first"),
    pytest.param("git diff HEAD:docs/a.md {SUB}:hidden/q01.txt", id="diff-subtree-path-second"),
    pytest.param("git diff {HTREE}:q01.txt HEAD:docs/a.md", id="diff-hidden-tree-path-first"),
    pytest.param("git show {SUB}:hidden/q01.txt", id="show-subtree-path"),
    pytest.param("git show {HTREE}:q01.txt", id="show-hidden-tree-path"),
    pytest.param("git cat-file -p {SUB}:hidden/q01.txt", id="cat-file-p-subtree-path"),
    pytest.param("git cat-file blob {HTREE}:q01.txt", id="cat-file-blob-hidden-tree-path"),
]


@pytest.mark.parametrize("who", WHO)
@pytest.mark.parametrize("template", G1)
def test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal(planted, template, who):
    """Red at eca7a70176de: each allowed (real git prints the hidden file's text). The diff forms were refused on the
    base d9e7dc859 by the revision fault (a PolicyError); the show and cat-file forms were allowed there too."""
    assert_refused_ruled(fill(template, planted), planted["root"], who)


@pytest.mark.parametrize("template", G1)
def test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook(planted, template):
    """Red at eca7a70176de: the hook lets each through (exit 0, no answer). The hook's read rule asks the product's
    judge; it must refuse (a ``deny`` answer, never an allow)."""
    got = hook(fill(template, planted), planted["root"], RESEARCH)
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"


# -- group 2: an object named by its blob id alone ---------------------------------------------------------------------

G2 = [
    pytest.param("git cat-file blob {BLOB}", id="cat-file-blob-id"),
    pytest.param("git cat-file -p {BLOB}", id="cat-file-p-blob-id"),
]
G2_GUARDS = [
    pytest.param("git cat-file -t {BLOB}", id="cat-file-t-blob-id"),
    pytest.param("git cat-file -s {BLOB}", id="cat-file-s-blob-id"),
    pytest.param("git cat-file -e {BLOB}", id="cat-file-e-blob-id"),
    pytest.param("git cat-file -p HEAD", id="cat-file-p-commit"),
    pytest.param("git show HEAD:docs/a.md", id="show-visible-blob"),
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md", id="diff-two-visible-blobs"),
    pytest.param("git cat-file -p HEAD:docs/a.md", id="cat-file-p-visible-blob"),
]


@pytest.mark.parametrize("who", WHO)
@pytest.mark.parametrize("template", G2)
def test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal(planted, template, who):
    """Red at eca7a70176de: each allowed (real git prints the hidden file's text), while ``git show BLOB`` is refused;
    allowed on the base too (an older fail-open)."""
    assert_refused_ruled(fill(template, planted), planted["root"], who)


@pytest.mark.parametrize("who", WHO)
@pytest.mark.parametrize("template", G2_GUARDS)
def test_r4_a_cat_file_or_blob_ref_that_shows_no_refused_text_stays_allowed(planted, template, who):
    """Green at eca7a70176de (a guard): no file text (``-t``, ``-s``, ``-e``), a commit object, or a visible path
    under ``HEAD``."""
    assert_allowed(fill(template, planted), planted["root"], who)


# -- group 3: git's own --output writes its file -----------------------------------------------------------------------

G3 = [
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md --output={t}", None, id="diff-blobs-output-eq-last"),
    pytest.param("git diff --output={t} HEAD:docs/a.md HEAD:docs/b.md", None, id="diff-output-eq-first-blobs"),
    pytest.param("git diff --output {t} HEAD~0 HEAD", None, id="diff-output-space-commits"),
    pytest.param("git diff --output={t} HEAD~0 HEAD", None, id="diff-output-eq-commits"),
    pytest.param("git show --output={t} HEAD:docs/a.md", None, id="show-output-eq-blob"),
    pytest.param("git log -p --output={t} HEAD~1..HEAD", None, id="log-p-output-eq-range"),
    pytest.param("git log -p -1 --output={t} -- docs/a.md", None, id="log-p-1-output-eq-path"),
    pytest.param("git -C {root} diff --output={t} HEAD:docs/a.md HEAD:docs/b.md", "docs", id="git-C-diff-output-eq"),
    pytest.param("git -C {root} diff --output {t} HEAD~0 HEAD", "docs", id="git-C-diff-output-space"),
    pytest.param("git -C {root} show --output={t} HEAD:docs/a.md", "docs", id="git-C-show-output-eq"),
    pytest.param("git -C {root} log -p --output={t} HEAD~1..HEAD", "docs", id="git-C-log-output-eq"),
    pytest.param("cd tests && git diff --output=acceptance/X/zz.txt HEAD:docs/a.md HEAD:docs/b.md", None,
                 id="cd-diff-output-eq-relative"),
    pytest.param("cd tests && git diff --output acceptance/X/zz.txt HEAD~0 HEAD", None,
                 id="cd-diff-output-space-relative"),
    pytest.param("cd tests && git show --output=acceptance/X/zz.txt HEAD:docs/a.md", None,
                 id="cd-show-output-eq-relative"),
    pytest.param("cd tests && git log -p --output=acceptance/X/zz.txt HEAD~1..HEAD", None,
                 id="cd-log-output-eq-relative"),
]
G3_GUARDS = [
    pytest.param("git diff --output={a} HEAD~0 HEAD", id="diff-output-eq-commits-into-src"),
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md --output={a}", id="diff-blobs-output-eq-into-src"),
    pytest.param("git log -p --output={a} HEAD~1..HEAD", id="log-p-output-eq-into-src"),
]


@pytest.mark.parametrize("template,sub", G3)
def test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule(
        planted, template, sub):
    """Red at eca7a70176de: the ``--output=`` forms are allowed (real git creates ``tests/acceptance/X/zz.txt``); the
    ``--output <file>`` forms are refused, but by the revision rule (the file's name taken for a revision word), not
    by the write refusal naming the file. On the base d9e7dc859 the two blob-diff forms were refused by the revision
    fault and the others allowed."""
    root = planted["root"]
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)


@pytest.mark.parametrize("template", G3_GUARDS)
def test_r4_git_s_output_option_into_a_path_the_engineer_may_write_stays_allowed(planted, template):
    """Green at eca7a70176de (a guard): ``src/out.txt`` is inside the engineer's ``src/**``."""
    assert_allowed(fill(template, planted), planted["root"], ENGINEER)
