"""W2-42a reopened, R4 (D1): a revision-colon-path naming a blob is judged as a read of that path; and the R4/R5
failure line (F3), the fail-open guards (DEC-1157 (12), DEC-1180 (4), DEC-1128 (3), DEC-1133 (2); DND row 122).

The ticket's S12: ``git diff REV:PATH REV:PATH`` (a revision-colon-path on one or both sides, each naming a blob that
exists) and ``git show REV:PATH`` are judged as reads of those paths, under the read rules the path names; a revision
word that names no commit, tree or blob is refused as today, not passed. F3: a call refused today stays refused when
it reads a refused path or writes a walled one.

Every case runs in a planted repository of its module (``git init`` under ``tmp_path``): two commits (``docs/a.md``
changes between them), a branch ``feature``, the visible files ``docs/a.md`` and ``docs/b.md``, a hidden-part file of
an evaluation set that measures ``research`` and ``engineer`` (so the judge has a hidden part the command might reach,
and asks git about revisions), a ``.env`` stand-in (no secret in it), the engineer's own acceptance file
``tests/acceptance/W2-42a/x.py`` (the counterpart's work for an engineer on DAEO-03ub), an in-progress engineer ticket
DAEO-03ub allowing ``src/**``, and a held-out list naming a second repository outside the project (``oracle``).

Each form was run through real git in a scratch repository of the same shape (2026-11-14, git 2.43):
``git diff HEAD:docs/a.md HEAD:docs/b.md``, ``git diff HEAD~1:docs/a.md HEAD:docs/a.md`` and the hash/branch forms
print the blobs' diff (exit 0); ``git diff HEAD:docs/a.md docs/b.md`` (and with ``--`` before the file) diffs the blob
against the working file, so a blob on one side is read too; ``git diff --no-index HEAD:docs/a.md docs/b.md`` fails
("Could not access"), so it is not used; from ``docs/``, ``HEAD:./a.md`` names ``docs/a.md`` (``HEAD:a.md`` does not);
``git show nosuchref:docs/a.md`` and ``git diff nosuch:docs/a.md HEAD:docs/b.md`` fail with "invalid object name"
(exit 128); ``git show HEAD:docs/missing.md`` and ``git diff HEAD:docs/missing.md HEAD:docs/a.md`` fail with "path
'docs/missing.md' does not exist in 'HEAD'" (exit 128).

Two views of the guard are asked (DEC-953 item 2, the brief's definition of rule ``error``):

- **the read judge as the live hook calls it**: ``reads._Judge(root, parts).tool("Bash", {"command": …}, cwd)``, the
  parts built as ``reads.policy_refusal`` builds them for a session whose acting role is its own
  (``reads.parts(root, role, ticket, {})``), with no ``may_write`` (the live hook passes none). Any exception it raises,
  ``PolicyError`` included, is what the live hook logs as rule ``error`` (exit 2);
- **the product's entry**: ``decide("Bash", {"command": …}, root, role, ticket, cwd=…, flag="open")``. Rule ``error``
  there: it raises, or returns the catch-all ("the guard could not work out the reads this session is refused"), or a
  ``PolicyError`` turned into a refusal (``"<fault>: the call is refused (fail closed, DEC-820)"``): no genuine fault is
  planted here, so that text means the judge raised.

- ``test_r4_*`` (S12): group 1, blob reads of visible paths, allowed; group 2, a blob read of a path the role may not
  read (the hidden part, a secret, the counterpart's tests), refused by that rule's own text; group 3, a revision word
  that names nothing, refused by a ruled refusal. Through the hook too for group 1's two-sided diff.
- ``test_r45_failure_*`` (F3): each refused today and must stay refused (any rule, but not an exception).
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
ERROR_TAIL = ": the call is refused (fail closed, DEC-820)"  # reads.policy_refusal's form of a PolicyError
CATCH = "the guard could not work out the reads this session is refused"  # its catch-all

HID = "fixtures/evaluation/w242a/hidden/q01.txt"
ENV = "." + "env"  # the planted stand-in's name (no secret in it)
OWN = "tests/acceptance/W2-42a/x.py"  # the engineer's own acceptance folder on DAEO-03ub (W2-42a)
T = "tests/acceptance/X/zz.txt"  # no engineer may write it
ENGINEER = ("engineer", "DAEO-03ub")
RESEARCH = ("research", None)
TICKET = """---
id: DAEO-03ub
status: in_progress
type: task
role: engineer
wbs_id: W2-42a
allowed_paths:
- src/**
---
# A stand-in of the engineer's ticket for the R4 cases
"""
PATH_MAP = ("evaluation_sets:\n  w242a:\n    visible: [\"docs/visible.md\"]\n"
            "    hidden: [\"fixtures/evaluation/w242a/hidden/**\"]\n"
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
    """``{"root", "oracle", "short", "held"}``: the planted project (real path), the held-out repository outside it,
    the abbreviated hash of HEAD, and the held-out path."""
    base = os.path.realpath(str(tmp_path_factory.mktemp("w242a-r4")))
    root = os.path.join(base, "proj")
    for rel, text in (("governance/project/path-map.yaml", PATH_MAP), (".tickets/DAEO-03ub.md", TICKET),
                      (HID, "hidden\n"), ("docs/a.md", "a1\n"), ("docs/b.md", "b1\n"), ("docs/visible.md", "v\n"),
                      (ENV, "W242A_STAND_IN=1\n"), (OWN, "x = 1\n"), ("src/ok.py", "ok = 1\n")):
        _write(root, rel, text)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "one")
    _write(root, "docs/a.md", "a2\n")
    _git(root, "commit", "-q", "-am", "two")
    _git(root, "branch", "feature")
    os.makedirs(os.path.join(root, "tests", "acceptance", "X"))
    oracle = os.path.join(base, "oracle")
    _write(oracle, "q.txt", "q\n")
    _git(oracle, "init", "-q", "-b", "main")
    _git(oracle, "add", "-A")
    _git(oracle, "commit", "-q", "-m", "o")
    _write(root, "governance/project/held-out.yaml", f"held_out_paths:\n  - {oracle}\n")
    return {"root": root, "oracle": oracle, "short": _git(root, "rev-parse", "--short", "HEAD"), "held": oracle}


@pytest.fixture(autouse=True)
def quiet_session(tmp_path, monkeypatch):
    """No session variable; the case's own HOME (no runs root, no key file of the machine)."""
    for name in SESSION:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "home").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))


def fill(template, planted):
    return template.format(short=planted["short"], root=planted["root"], oracle=planted["oracle"],
                           held=planted["held"], hid=HID, env=ENV, own=OWN, t=T)


# -- the two views of the guard -------------------------------------------------------------------------------------------

def judged(command, root, role, ticket=None, cwd=None):
    """``(exception, why)`` of the read judge as the live hook calls it. The parts are built as
    ``reads.policy_refusal`` builds them for a session whose acting role is its own: ``reads.parts(root, role,
    ticket, {})``; no ``may_write`` (the live hook passes none)."""
    from gov.guard import reads
    try:
        parts = reads.parts(root, role, ticket, {})
        return None, reads._Judge(root, parts).tool("Bash", {"command": command}, cwd or root)
    except Exception as exc:  # noqa: BLE001 - any exception is the live hook's rule ``error``
        return exc, None


def decided(command, root, role, ticket=None, cwd=None):
    """``(exception, (decision, why))`` of the product's entry."""
    from gov.guard.decide import decide
    try:
        return None, decide("Bash", {"command": command}, root, role, ticket, cwd=cwd or root, flag="open")
    except Exception as exc:  # noqa: BLE001
        return exc, None


def decide_error(exc, got):
    """Why the product's answer is rule ``error`` (an exception, raised or hidden), or ``""``."""
    if exc is not None:
        return f"decide() raised {type(exc).__name__}: {exc}"
    if CATCH in got[1]:
        return f"decide() hid an exception behind the catch-all: {got[1]}"
    if got[1].endswith(ERROR_TAIL):
        return f"the judge raised a PolicyError, turned into a refusal: {got[1]}"
    return ""


def show(command, cwd):
    return f"\n--- the command (cwd {cwd}) ---\n{command}"


def assert_allowed(command, root, who, cwd=None):
    role, ticket = who
    exc, why = judged(command, root, role, ticket, cwd)
    assert exc is None, f"the judge raised (rule error): {type(exc).__name__}: {exc}{show(command, cwd)}"
    assert why == "", f"want the judge to let the read through, got: {why}{show(command, cwd)}"
    exc, got = decided(command, root, role, ticket, cwd)
    err = decide_error(exc, got)
    assert not err, err + show(command, cwd)
    assert got == ("allow", ""), f"want allow, got {got}{show(command, cwd)}"


def assert_refused_by(command, root, who, rule, cwd=None):
    """Refused by the read rule ``rule`` (its own text), by the judge and by the product, with no exception."""
    role, ticket = who
    exc, why = judged(command, root, role, ticket, cwd)
    assert exc is None, f"the judge raised (rule error): {type(exc).__name__}: {exc}{show(command, cwd)}"
    assert why == rule, f"want the judge to refuse by the rule\n  {rule}\ngot\n  {why!r}{show(command, cwd)}"
    exc, got = decided(command, root, role, ticket, cwd)
    err = decide_error(exc, got)
    assert not err, err + show(command, cwd)
    assert got == ("deny", rule), f"want deny by the rule\n  {rule}\ngot\n  {got}{show(command, cwd)}"


def assert_refused_ruled(command, root, who, cwd=None):
    """Refused by a ruled refusal (any rule's own text), with no exception in the judge or the product."""
    role, ticket = who
    exc, why = judged(command, root, role, ticket, cwd)
    assert exc is None, f"the judge raised (rule error): {type(exc).__name__}: {exc}{show(command, cwd)}"
    exc, got = decided(command, root, role, ticket, cwd)
    err = decide_error(exc, got)
    assert not err, err + show(command, cwd)
    assert got[0] == "deny", f"want a ruled refusal, got {got}{show(command, cwd)}"


def hook(command, root, who, cwd=None):
    """The five-rule hook as Claude Code runs it (fixtures/hook/pretooluse.py, this tree's ``src`` on
    ``PYTHONPATH``): ``(decision, reason, exit code)``; exit 2 is a refusal by an error (rule ``error``)."""
    role, ticket = who
    env = {k: v for k, v in os.environ.items() if k not in SESSION and k != "PYTHONPATH"}
    env.update(PYTHONPATH=SRC, GOV_ROLE=role, CLAUDE_PROJECT_DIR=root, PYTHONDONTWRITEBYTECODE="1")
    if ticket:
        env["GOV_TICKET"] = ticket
    event = {"session_id": "w2-42a-r4", "hook_event_name": "PreToolUse", "tool_name": "Bash",
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


def reasons():
    from gov.guard import reads
    return {"hidden": reads.HIDDEN_REFUSAL, "secret": reads.SECRET_REFUSAL, "own": reads.TESTS_REFUSAL}


# -- S12 group 1: blob reads of visible paths are judged as reads, and allowed ----------------------------------------------

G1_TWO_SIDED = [
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md", None, id="diff-head-a-head-b"),
    pytest.param("git diff HEAD~1:docs/a.md HEAD:docs/a.md", None, id="diff-parent-a-head-a"),
    pytest.param("git diff {short}:docs/a.md feature:docs/b.md", None, id="diff-abbreviated-hash-and-branch"),
    pytest.param("git diff main~1:docs/a.md main:docs/a.md", None, id="diff-branch-parent-and-branch"),
    pytest.param("git diff HEAD:./a.md HEAD:./b.md", "docs", id="diff-dot-slash-paths-from-docs"),
    pytest.param("git -C {root} diff HEAD:docs/a.md HEAD:docs/b.md", "docs", id="diff-after-git-C-root"),
]
G1_GUARDS = [  # allowed on the base already; kept so the fix does not refuse them
    pytest.param("git diff --stat HEAD~1:docs/a.md HEAD:docs/a.md", None, id="diff-stat-two-blobs"),
    pytest.param("git diff HEAD:docs/a.md docs/b.md", None, id="diff-blob-against-working-file"),
    pytest.param("git diff HEAD:docs/a.md -- docs/b.md", None, id="diff-blob-against-working-file-after-dashes"),
    pytest.param("git show HEAD:docs/a.md", None, id="show-head"),
    pytest.param("git show {short}:docs/a.md", None, id="show-abbreviated-hash"),
    pytest.param("git show feature:docs/a.md", None, id="show-branch"),
    pytest.param("git show HEAD~1:docs/a.md HEAD:docs/b.md", None, id="show-two-blobs"),
    pytest.param("git -C docs show HEAD:./a.md", None, id="show-after-git-C-dot-slash"),
]


@pytest.mark.parametrize("template,sub", G1_TWO_SIDED)
def test_r4_a_diff_of_blob_refs_naming_visible_paths_is_judged_as_reads_and_allowed(planted, template, sub):
    """Red on the base: the judge resolves each revision word as a commit (reads.py ``_Judge.patched``, the
    ``rev-parse … <word>^{commit}`` question), git fails for a blob, and ``_Judge.ask`` raises
    ``PolicyError(_REV_FAULT)`` ("git cannot say whether a revision holds the hidden part")."""
    root = planted["root"]
    assert_allowed(fill(template, planted), root, RESEARCH, os.path.join(root, sub) if sub else None)


def test_r4_an_engineer_s_diff_of_two_visible_blobs_is_judged_by_those_paths_and_allowed(planted):
    """Red on the base: refused by the counterpart rule (``TESTS_REFUSAL``): a ``git diff`` whose words are taken for
    revisions is judged as a patch of the whole tree (reads.py ``_Judge.git``, ``others.spec(self.root, …)``), which
    takes in the engineer's own acceptance folder; read as two blobs it reads ``docs/a.md`` and ``docs/b.md`` only."""
    assert_allowed("git diff HEAD:docs/a.md HEAD:docs/b.md", planted["root"], ENGINEER)


@pytest.mark.parametrize("template,sub", G1_GUARDS)
def test_r4_a_show_or_one_sided_diff_of_a_visible_blob_stays_allowed(planted, template, sub):
    """Green on the base (a guard): ``git show REV:PATH`` of a visible path is judged by its path and allowed
    (reads.py ``_Judge.git``, the ``shown`` loop, and no patch is asked of git), a one-sided diff whose other side
    is a visible working file is narrowed to that file (``_Judge.covers`` is false), and ``--stat`` shows names only
    (no patch is asked of git)."""
    root = planted["root"]
    assert_allowed(fill(template, planted), root, RESEARCH, os.path.join(root, sub) if sub else None)


def test_r4_a_diff_of_two_visible_blobs_is_allowed_through_the_hook(planted):
    """Red on the base: the hook calls the judge, the judge raises the revision fault, and the hook exits 2
    ("guard (DEC-953): could not decide: git cannot say whether a revision holds the hidden part; refused")."""
    got = hook("git diff HEAD:docs/a.md HEAD:docs/b.md", planted["root"], RESEARCH)
    assert got == ("allow", "", 0), f"want the hook to allow the blob diff, got {got}"


# -- S12 group 2: a blob read of a path the role may not read is refused by that path's rule --------------------------------

G2 = [
    # the hidden part of the evaluation set that measures the session
    pytest.param("git show HEAD:{hid}", "hidden", RESEARCH, id="hidden-show"),
    pytest.param("git diff HEAD:{hid} HEAD:docs/a.md", "hidden", RESEARCH, id="hidden-diff-first-side"),
    pytest.param("git diff HEAD:docs/a.md HEAD:{hid}", "hidden", RESEARCH, id="hidden-diff-second-side"),
    pytest.param("git diff HEAD~1:{hid} HEAD:{hid}", "hidden", RESEARCH, id="hidden-diff-both-sides"),
    pytest.param("git diff HEAD:{hid} docs/a.md", "hidden", RESEARCH, id="hidden-diff-one-sided-against-a-file"),
    pytest.param("git diff HEAD:{hid} -- docs/a.md", "hidden", RESEARCH, id="hidden-diff-one-sided-after-dashes"),
    # a secret, refused to every role
    pytest.param("git show HEAD:{env}", "secret", RESEARCH, id="secret-show"),
    pytest.param("git diff HEAD:{env} HEAD:docs/a.md", "secret", RESEARCH, id="secret-diff-first-side"),
    pytest.param("git diff HEAD:docs/a.md HEAD:{env}", "secret", RESEARCH, id="secret-diff-second-side"),
    pytest.param("git diff HEAD:{env} docs/a.md", "secret", RESEARCH, id="secret-diff-one-sided-against-a-file"),
    # the counterpart's work: the engineer's own acceptance tests
    pytest.param("git show HEAD:{own}", "own", ENGINEER, id="own-tests-show"),
    pytest.param("git diff HEAD:{own} HEAD:docs/a.md", "own", ENGINEER, id="own-tests-diff"),
]


@pytest.mark.parametrize("template,rule,who", G2)
def test_r4_a_blob_ref_naming_a_path_the_role_may_not_read_is_refused_by_that_rule(planted, template, rule, who):
    """By form, on the base:

    - ``git show REV:<path>`` (hidden, secret, own tests): green, refused by the rule's text in reads.py
      ``_Judge.git``'s ``shown`` loop;
    - a two-sided ``git diff`` naming such a path: red, the judge raises ``PolicyError(_REV_FAULT)`` in
      ``_Judge.patched``/``_Judge.ask`` before any path rule is asked (the product shows "git cannot say …: the call is
      refused (fail closed, DEC-820)");
    - a one-sided ``git diff REV:<hidden or secret> docs/a.md`` (also after ``--``): red, **allowed** on the base (a
      fail-open: real git prints the blob against the file): the blob word is taken for a revision, and
      ``_Judge.covers`` judges only the working file's pathspec."""
    assert_refused_by(fill(template, planted), planted["root"], who, reasons()[rule])


# -- S12 group 3: a revision word that names no commit, tree or blob is refused, by a ruled refusal --------------------------

G3_DIFF = [
    pytest.param("git diff nosuch:docs/a.md HEAD:docs/b.md", id="diff-unknown-revision-first"),
    pytest.param("git diff HEAD:docs/a.md nosuch:docs/b.md", id="diff-unknown-revision-second"),
    pytest.param("git diff HEAD:docs/missing.md HEAD:docs/a.md", id="diff-missing-path-in-revision"),
    pytest.param("git diff HEAD:docs/a.md feature:docs/missing.md", id="diff-missing-path-in-branch"),
]
G3_SHOW = [
    pytest.param("git show nosuchref:docs/a.md", id="show-unknown-revision"),
    pytest.param("git show HEAD:docs/missing.md", id="show-missing-path-in-revision"),
]


@pytest.mark.parametrize("command", G3_DIFF)
def test_r4_a_diff_whose_revision_word_names_nothing_is_refused_by_a_ruled_refusal(planted, command):
    """Red on the base: refused, but by the error path: reads.py ``_Judge.ask`` raises ``PolicyError(_REV_FAULT)``
    when git's ``rev-parse … ^{commit}`` fails (the live hook logs rule ``error`` and exits 2)."""
    assert_refused_ruled(command, planted["root"], RESEARCH)


@pytest.mark.parametrize("command", G3_SHOW)
def test_r4_a_show_whose_revision_word_names_nothing_is_refused_by_a_ruled_refusal(planted, command):
    """Red on the base: **allowed** (the path is visible and ``git show`` of one blob asks git nothing); the KPI line
    says a revision word that names no commit, tree or blob is refused (git itself fails on it: exit 128)."""
    assert_refused_ruled(command, planted["root"], RESEARCH)


# -- F3: refused today, still refused (a fail-open guard) --------------------------------------------------------------------

F3_READS = [
    pytest.param("git -C {oracle} show HEAD:q.txt", RESEARCH, id="held-out-show-after-git-C"),
    pytest.param("git -C {oracle} diff HEAD:q.txt HEAD:q.txt", RESEARCH, id="held-out-diff-after-git-C"),
    pytest.param("git show HEAD:{held}/q.txt", RESEARCH, id="held-out-path-named-in-the-blob-ref"),
    pytest.param("git show HEAD:{env}", RESEARCH, id="secret-show"),
    pytest.param("git diff HEAD:{env} HEAD:docs/a.md", RESEARCH, id="secret-diff-first-side"),
    pytest.param("git diff HEAD:docs/a.md HEAD:{env}", ENGINEER, id="secret-diff-second-side-engineer"),
    pytest.param("git show HEAD:{hid}", RESEARCH, id="hidden-show"),
    pytest.param("git diff HEAD:{hid} HEAD:docs/a.md", RESEARCH, id="hidden-diff"),
    pytest.param("git diff HEAD~1:fixtures HEAD:fixtures", RESEARCH, id="hidden-tree-refs-holding-the-part"),
    pytest.param("git diff HEAD~1:fixtures/evaluation/w242a HEAD:fixtures/evaluation/w242a", RESEARCH,
                 id="hidden-tree-refs-of-the-set"),
]
F3_WRITES = [
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md > {t}", id="diff-redirected-into-acceptance"),
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md >> {t}", id="diff-appended-into-acceptance"),
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md | tee {t}", id="diff-piped-to-tee-into-acceptance"),
    pytest.param("git diff HEAD:docs/a.md HEAD:docs/b.md | tee -a {t}", id="diff-piped-to-tee-a-into-acceptance"),
    pytest.param("git show HEAD:docs/a.md > {t}", id="show-redirected-into-acceptance"),
]


def assert_still_refused(command, root, who):
    exc, got = decided(command, root, *who)
    assert exc is None, f"decide() raised {type(exc).__name__}: {exc}{show(command, root)}"
    assert CATCH not in got[1], f"refused only by the catch-all (an exception): {got[1]}{show(command, root)}"
    assert got[0] == "deny", f"a fail-open: want deny, got {got}{show(command, root)}"


@pytest.mark.parametrize("template,who", F3_READS)
def test_r45_failure_a_blob_or_tree_read_of_a_refused_path_stays_refused(planted, template, who):
    """Green on the base (each refused today): the held-out forms by ``names_held_out`` in decide.py ``decide``; the
    ``git show`` forms by the secret and hidden-part rules (reads.py ``_Judge.git``); the two-sided diffs and the tree
    refs by the revision fault (a ``PolicyError`` from ``_Judge.ask``, a refusal through the product). After the fix
    each must still be refused (any rule; never an exception, never allowed)."""
    assert_still_refused(fill(template, planted), planted["root"], who)


@pytest.mark.parametrize("template", F3_WRITES)
def test_r45_failure_a_blob_diff_whose_output_is_written_into_the_acceptance_folder_stays_refused(planted, template):
    """Green on the base (each refused today): the diffs by the revision fault before the write rule is reached, the
    ``git show`` by the write rule (``tests/acceptance/X/zz.txt`` is outside the engineer's ``src/**``). After the
    fix the read is allowed and the write must still refuse."""
    assert_still_refused(fill(template, planted), planted["root"], ENGINEER)


@pytest.mark.parametrize("template", F3_WRITES[:3])
def test_r45_failure_a_blob_diff_written_into_the_acceptance_folder_stays_refused_through_the_hook(planted, template):
    """Green on the base: the hook refuses each (exit 2, the revision fault, for the diffs; rule 1 for the others).
    After the fix the hook's rule 1 must refuse the write (a ``deny`` answer or exit 2, never an allow)."""
    got = hook(fill(template, planted), planted["root"], ENGINEER)
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"


@pytest.mark.parametrize("template", ["git -C {oracle} show HEAD:q.txt", "git show HEAD:{hid}",
                                      "git diff HEAD:{env} HEAD:docs/a.md"],
                         ids=["held-out", "hidden", "secret"])
def test_r45_failure_a_blob_read_of_a_refused_path_stays_refused_through_the_hook(planted, template):
    """Green on the base: the hook refuses each (rule 2 held-out, rule 2 hidden part, and exit 2 by the revision
    fault for the secret diff). After the fix each must still be refused by the hook."""
    got = hook(fill(template, planted), planted["root"], RESEARCH)
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
