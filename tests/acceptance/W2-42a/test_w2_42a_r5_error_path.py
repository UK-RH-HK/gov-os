"""W2-42a reopened, R5: the guard's judge never raises; its error path stays for a genuine fault (DEC-1157 (12),
DEC-1180 (4), DEC-1128 (3), DEC-1133 (2); DND row 123).

The ticket's S13: no Bash or tool input makes the guard's judge raise inside itself: the ``list index out of range``
crash and the revision it cannot classify each get a ruled decision (allow, or a refusal naming its rule), never rule
``error``; the error path stays and still fails closed for a genuine fault (a missing file, the 20-second deadline).

The crashing forms were looked for by reading the code at d9e7dc859 (reads.py ``_Judge``: ``tool``/``_tool``,
``command``, ``simple``, ``rewrites``, ``reads``, ``git``, ``patched``, ``stored``, ``ask``, ``runtime``, ``listing``,
``lists``; the module helpers ``_moved``, ``_tests_run``, ``_xargs``, ``_reads_files``, ``_simples``, ``_set_aside``,
the W2-141 block ``_x_*``/``x_search``; decide.py ``decide``, ``_expand_token``, ``_copy_args``,
``_extract_bash_write_targets``, ``lift_refusal``; heldout.py ``names_held_out``; install.py ``_head``,
``_download_target``; protected.py ``_options``), at every place that indexes a word list, a token list or a split
result, and by a seeded sweep of token sequences through ``decide`` and ``_Judge.tool``. What was found on the base:

- every index into a word or token list in those functions is guarded by a length check or a slice, so the forms the
  ticket names (empty words, a lone operator, a trailing pipe, ``&&`` or ``;``, an option with no value at the end, an
  unterminated ``$(``), also after a ``cd``, inside ``$(…)`` and after ``git -C <dir>``, are **ruled today** (green;
  kept as guards: the fix must not make them raise). The ``list index out of range`` crashes the ticket names are not
  reproduced by the product at d9e7dc859 (the guard's call log, their only record, is not read: SETUP-A-BAR S2);
- the judge **raises** ``PolicyError(_REV_FAULT)`` for a revision it cannot classify: reads.py ``_Judge.patched``
  (a word ``_expand_token`` cannot resolve, ``$X`` or ``$(…)``, or ``--stdin``) and ``_Judge.ask`` (git's
  ``rev-parse … ^{commit}`` fails: a blob or tree ref, a word that names nothing, an empty ref such as ``HEAD:``, ``:``,
  ``^``, ``:/``): the live hook logs rule ``error`` and exits 2;
- ``decide()`` **raises** for a Write or Edit whose ``file_path`` holds a NUL byte (``ValueError`` in
  ``os.path.realpath``) or is not a string (``TypeError`` in ``os.path.isabs``): decide.py ``decide``, the write-tool
  branch.

Rule ``error`` in these cases (the brief's definition): the read judge as the live hook calls it,
``reads._Judge(root, parts).tool(…)`` (parts built as ``reads.policy_refusal`` builds them: ``reads.parts(root, role,
ticket, {})``, no ``may_write``), raises anything; ``decide()`` raises, returns the catch-all, or returns a
``PolicyError`` turned into a refusal (``"…: the call is refused (fail closed, DEC-820)"``; no genuine fault is planted
in those cases); the hook exits 2. A ruled decision: allow, or a deny whose reason is a rule's own text.

- ``test_r5_*``: the named forms (ruled: guards), the revision forms (ruled: red), the tool inputs, the property case,
  and the genuine faults (git missing from ``PATH``, a path map that cannot be read), which must still refuse by the
  error path (green on the base). The 20-second deadline (the hook's ``signal.alarm(20)``) is not pinned: it lives in
  the hook template, not in ``src/gov/guard``, and a case for it would wait 20 s or change the hook.
"""
import json
import os
import random
import subprocess
import sys
import time

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
# A stand-in of the engineer's ticket for the R5 cases
"""
PATH_MAP = ("evaluation_sets:\n  w242a:\n    visible: [\"docs/visible.md\"]\n"
            "    hidden: [\"fixtures/evaluation/w242a/hidden/**\"]\n"
            "    measures:\n      roles: [research, engineer]\n")


def _git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(GIT + list(args), cwd=cwd, capture_output=True, text=True, env=env, check=True,
                          timeout=60).stdout.strip()


def make_project(base):
    """A planted project (real path): a git repository with two commits, an evaluation set measuring research and
    the engineer whose hidden part holds a file, an in-progress engineer ticket DAEO-03ub allowing ``src/**``."""
    root = os.path.join(os.path.realpath(str(base)), "proj")
    for rel, text in (("governance/project/path-map.yaml", PATH_MAP), (".tickets/DAEO-03ub.md", TICKET),
                      (HID, "hidden\n"), ("docs/a.md", "a1\n"), ("docs/b.md", "b1\n"), ("docs/visible.md", "v\n"),
                      ("src/ok.py", "ok = 1\n")):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "one")
    with open(os.path.join(root, "docs", "a.md"), "w", encoding="utf-8") as f:
        f.write("a2\n")
    _git(root, "commit", "-q", "-am", "two")
    return root


@pytest.fixture(scope="module")
def proj(tmp_path_factory):
    return make_project(tmp_path_factory.mktemp("w242a-r5"))


@pytest.fixture(autouse=True)
def quiet_session(tmp_path, monkeypatch):
    """No session variable; the case's own HOME; the variable the revision forms name is unset."""
    for name in SESSION + ("W242A_UNSET",):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "home").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))


# -- the views of the guard -----------------------------------------------------------------------------------------------

def judged(tool, tool_input, root, role, ticket=None, cwd=None):
    """``(exception, why)`` of the read judge as the live hook calls it; the parts built as ``reads.policy_refusal``
    builds them for a session whose acting role is its own (``reads.parts(root, role, ticket, {})``), no
    ``may_write`` (the live hook passes none)."""
    from gov.guard import reads
    try:
        parts = reads.parts(root, role, ticket, {})
        return None, reads._Judge(root, parts).tool(tool, tool_input, cwd or root)
    except Exception as exc:  # noqa: BLE001 - any exception is the live hook's rule ``error``
        return exc, None


def decided(tool, tool_input, root, role, ticket=None, cwd=None):
    from gov.guard.decide import decide
    try:
        return None, decide(tool, tool_input, root, role, ticket, cwd=cwd or root, flag="open")
    except Exception as exc:  # noqa: BLE001
        return exc, None


def decide_error(exc, got):
    if exc is not None:
        return f"decide() raised {type(exc).__name__}: {exc}"
    if CATCH in got[1]:
        return f"decide() hid an exception behind the catch-all: {got[1]}"
    if got[1].endswith(ERROR_TAIL):
        return f"the judge raised a PolicyError, turned into a refusal: {got[1]}"
    return ""


def error_of(tool, tool_input, root, who, judge=True):
    """Why the call is judged by rule ``error`` (the judge raised, or the product's answer hides an exception), or
    ``""`` for a ruled decision."""
    role, ticket = who
    if judge:
        exc, _ = judged(tool, tool_input, root, role, ticket)
        if exc is not None:
            return f"the judge raised (rule error): {type(exc).__name__}: {exc}"
    exc, got = decided(tool, tool_input, root, role, ticket)
    return decide_error(exc, got)


def assert_ruled(command, root, who=RESEARCH):
    why = error_of("Bash", {"command": command}, root, who)
    assert not why, f"{why}\n--- the command ({who[0]}) ---\n{command!r}"


def hook(tool, tool_input, root, who, path=None):
    """The five-rule hook as Claude Code runs it: ``(decision, reason, exit code)``; exit 2 is rule ``error``.
    ``path``: the hook's ``PATH`` (the interpreter is named by its absolute path)."""
    role, ticket = who
    env = {k: v for k, v in os.environ.items() if k not in SESSION and k != "PYTHONPATH"}
    env.update(PYTHONPATH=SRC, GOV_ROLE=role, CLAUDE_PROJECT_DIR=root, PYTHONDONTWRITEBYTECODE="1")
    if ticket:
        env["GOV_TICKET"] = ticket
    if path is not None:
        env["PATH"] = path
    event = {"session_id": "w2-42a-r5", "hook_event_name": "PreToolUse", "tool_name": tool,
             "tool_input": tool_input, "cwd": root, "agent_type": None}
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(event), capture_output=True, text=True, env=env,
                       cwd=root, timeout=120)
    if p.returncode == 2:
        return "deny", "ERROR: " + p.stderr[-800:], 2
    if p.returncode:
        return "crash", f"exit {p.returncode}: " + p.stderr[-800:], p.returncode
    if not p.stdout.strip():
        return "allow", "", 0
    out = json.loads(p.stdout)["hookSpecificOutput"]
    return out["permissionDecision"], out["permissionDecisionReason"], 0


# -- the forms the ticket names: ruled today, kept so (guards) ------------------------------------------------------------

NAMED = [
    ('""', "empty-double-quoted-word"), ("''", "empty-single-quoted-word"), ('"" ""', "two-empty-words"),
    ("", "empty-command"), (";", "lone-semicolon"), ("&&", "lone-and"), ("|", "lone-pipe"), ("&", "lone-ampersand"),
    ("||", "lone-or"), ("ls |", "trailing-pipe"), ("ls &&", "trailing-and"), ("ls ;", "trailing-semicolon"),
    ("ls ||", "trailing-or"), ("git -C", "git-C-no-value"), ("git diff -U", "git-diff-U-no-value"),
    ("git show --format", "git-show-format-no-value"), ("git log -n", "git-log-n-no-value"),
    ("git --git-dir", "git-dir-no-value"), ("cd -", "cd-dash"), ("find -name", "find-name-no-value"),
    ("grep -e", "grep-e-no-value"), ("sed -i", "sed-i-no-value"), ("xargs -I", "xargs-I-no-value"),
    ("cp -t", "cp-t-no-value"), ("echo $(ls", "unterminated-substitution"),
    ('cat "$(ls"', "unterminated-substitution-in-quotes"), ("echo `ls", "unterminated-backtick"),
]
CONTEXTS = [("{f}", "plain"), ("cd docs; {f}", "after-cd"), ("echo $({f})", "inside-substitution"),
            ("git -C docs {f}", "after-git-C")]
NAMED_CASES = [pytest.param(c.format(f=f), id=f"{fid}-{cid}") for c, cid in CONTEXTS for f, fid in NAMED]


@pytest.mark.parametrize("command", NAMED_CASES)
def test_r5_a_named_crashing_form_gets_a_ruled_decision(proj, command):
    """Green on the base (a guard): each index into a word or token list on these paths is guarded (reads.py
    ``_Judge.command`` reads ``tokens[i + 1]`` only with ``i + 1 < len(tokens)``, ``_Judge.simple`` returns for no
    words, ``_moved`` takes ``args[0]`` only when there are args, ``_Judge.git`` takes ``args[i]`` only while
    ``i < len(args)`` and ``-C`` only with a next word, ``_x_parse``/``_x_find`` check the length before
    ``args[i]``/``head[-2]``, ``_set_aside`` runs an unclosed substitution to the end; decide.py ``_copy_args``'s
    ``_next`` returns None at the end; install.py ``_download_target`` checks ``i + 1 < len(args)``). Ruled: the fix
    must keep it so, through the judge and the product."""
    assert_ruled(command, proj)


@pytest.mark.parametrize("command", [pytest.param(c.format(f=f), id=f"{fid}-{cid}")
                                     for c, cid in CONTEXTS[:1] for f, fid in NAMED])
def test_r5_a_named_crashing_form_gets_a_ruled_decision_for_an_engineer(proj, command):
    """Green on the base (a guard): the same forms for an engineer on DAEO-03ub, whose own acceptance folder brings in
    the W2-141 search block (reads.py ``x_search``, ``_x_parse``, ``_x_find``)."""
    assert_ruled(command, proj, ENGINEER)


@pytest.mark.parametrize("command", ['""', ";", "ls |", "ls &&", "git -C", "git diff -U", "cd -", "find -name",
                                     "echo $(ls", 'cat "$(ls"'],
                         ids=["empty-word", "lone-semicolon", "trailing-pipe", "trailing-and", "git-C-no-value",
                              "git-diff-U-no-value", "cd-dash", "find-name-no-value", "unterminated-substitution",
                              "unterminated-substitution-in-quotes"])
def test_r5_a_named_crashing_form_is_not_an_error_through_the_hook(proj, command):
    """Green on the base (a guard): the hook decides each (no exit 2)."""
    got = hook("Bash", {"command": command}, proj, RESEARCH)
    assert got[2] != 2 and got[0] in ("allow", "deny"), f"the hook could not decide (rule error): {got}"


# -- a revision the judge cannot classify: a ruled decision, never the error path ------------------------------------------

REV_FORMS = [
    pytest.param("git diff HEAD:", id="diff-empty-path-after-colon"),
    pytest.param("git diff :", id="diff-lone-colon"),
    pytest.param("git diff ^", id="diff-lone-caret"),
    pytest.param("git show :/", id="show-empty-message-search"),
    pytest.param("git diff HEAD HEAD:", id="diff-commit-and-empty-path"),
    pytest.param("git diff HEAD: HEAD:", id="diff-two-empty-paths"),
    pytest.param('git diff HEAD~1:"" HEAD:""', id="diff-two-empty-quoted-paths"),
    pytest.param("git diff $W242A_UNSET", id="diff-unset-variable"),
    pytest.param('git log -p "$(git rev-parse HEAD)"', id="log-p-substitution"),
    pytest.param("git log --stdin -p", id="log-stdin"),
    pytest.param("git log -p nosuchref", id="log-p-unknown-revision"),
    pytest.param("git diff nosuch", id="diff-unknown-revision"),
    pytest.param("git diff HEAD..nosuch", id="diff-range-to-unknown"),
    pytest.param("git show nosuch..HEAD", id="show-range-from-unknown"),
    pytest.param("git diff ls |", id="diff-word-then-trailing-pipe"),
    pytest.param("git diff find -name", id="diff-words-then-option-with-no-value"),
    pytest.param("cd docs && git diff HEAD:", id="diff-empty-path-after-cd"),
    pytest.param("echo $(git diff :)", id="diff-lone-colon-inside-substitution"),
]


@pytest.mark.parametrize("command", REV_FORMS)
def test_r5_a_revision_the_judge_cannot_classify_gets_a_ruled_decision(proj, command):
    """Red on the base: the judge raises ``PolicyError(_REV_FAULT)``: reads.py ``_Judge.patched`` for a word
    ``_expand_token`` cannot resolve (``$W242A_UNSET``, a ``$(…)``) or ``--stdin``, and ``_Judge.ask`` when git's
    ``rev-parse --end-of-options <word>^{commit}`` fails (an empty ref, ``:``, ``^``, ``:/``, a word naming nothing,
    a range to or from one); the product shows "git cannot say whether a revision holds the hidden part: the call is
    refused (fail closed, DEC-820)", the live hook exits 2. Ruled after the fix: allow, or a refusal naming its rule."""
    assert_ruled(command, proj)


@pytest.mark.parametrize("command", ["git diff HEAD:", "git diff nosuch", "git diff $W242A_UNSET"],
                         ids=["diff-empty-path-after-colon", "diff-unknown-revision", "diff-unset-variable"])
def test_r5_a_revision_the_judge_cannot_classify_is_not_an_error_through_the_hook(proj, command):
    """Red on the base: the hook exits 2 ("guard (DEC-953): could not decide: git cannot say whether a revision holds
    the hidden part; refused"), reads.py ``_Judge.patched``/``_Judge.ask``."""
    got = hook("Bash", {"command": command}, proj, RESEARCH)
    assert got[2] != 2 and got[0] in ("allow", "deny"), f"the hook could not decide (rule error): {got}"


# -- tool inputs ------------------------------------------------------------------------------------------------------------

WRITE_INPUTS = [
    pytest.param("Write", {"file_path": "src/a\x00b.py", "content": ""}, id="write-path-with-a-nul-byte"),
    pytest.param("Edit", {"file_path": "\x00", "old_string": "a", "new_string": "b"}, id="edit-path-a-nul-byte"),
    pytest.param("Write", {"file_path": 1, "content": ""}, id="write-path-a-number"),
    pytest.param("Edit", {"file_path": ["src/ok.py"], "old_string": "a", "new_string": "b"}, id="edit-path-a-list"),
]
READ_INPUTS = [
    pytest.param("Read", {"file_path": ""}, id="read-empty-path"),
    pytest.param("Read", {"file_path": None}, id="read-path-none"),
    pytest.param("Read", {"file_path": 1}, id="read-path-a-number"),
    pytest.param("Read", {"file_path": "a\x00b"}, id="read-path-with-a-nul-byte"),
    pytest.param("Grep", {"pattern": "x", "glob": "{,}"}, id="grep-empty-brace-glob"),
    pytest.param("Grep", {"pattern": "x", "path": "["}, id="grep-path-an-open-bracket"),
    pytest.param("Glob", {"pattern": ""}, id="glob-empty-pattern"),
    pytest.param("Glob", {"pattern": "**"}, id="glob-double-star"),
    pytest.param("Glob", {"pattern": "/"}, id="glob-root"),
    pytest.param("Glob", {"pattern": "[", "path": "["}, id="glob-open-brackets"),
    pytest.param("Bash", {}, id="bash-no-command"),
    pytest.param("Bash", {"command": None}, id="bash-command-none"),
    pytest.param("Bash", {"command": ["ls"]}, id="bash-command-a-list"),
]


@pytest.mark.parametrize("tool,tool_input", WRITE_INPUTS)
def test_r5_a_write_tool_input_whose_path_is_no_path_is_refused_by_a_ruled_refusal(proj, tool, tool_input):
    """Red on the base: decide.py ``decide`` raises out of itself in the write-tool branch: ``os.path.isabs`` raises
    ``TypeError`` for a path that is not a string, ``os.path.realpath`` ``ValueError`` ("embedded null byte") for a
    NUL byte. A write whose target is no path is not known to be allowed: refused, by a rule's text."""
    exc, got = decided(tool, tool_input, proj, *ENGINEER)
    why = decide_error(exc, got)
    assert not why, f"{why}\n--- the call --- {tool} {tool_input!r}"
    assert got[0] == "deny", f"want a ruled refusal, got {got}\n--- the call --- {tool} {tool_input!r}"


@pytest.mark.parametrize("tool,tool_input", READ_INPUTS)
def test_r5_an_odd_read_or_bash_tool_input_gets_a_ruled_decision(proj, tool, tool_input):
    """Green on the base (a guard): reads.py ``_Judge._tool`` takes a field that is not a string as ``""``; a glob is
    split only where it holds a wildcard (``glob_lead``/``glob_word``); ``spellings`` turns a NUL byte into no path."""
    for who in (RESEARCH, ENGINEER):
        why = error_of(tool, tool_input, proj, who)
        assert not why, f"{why}\n--- the call ({who[0]}) --- {tool} {tool_input!r}"


# -- the property case --------------------------------------------------------------------------------------------------------

SEED = 20261114
SEQUENCES = 1500
VOCAB = (["ls", "cat", "echo", "x", "docs/a.md", "docs", "cd", "grep", "find", "-name", "sed", "-i", "xargs", "tee"]
         + [";", "&&", "||", "|", "&", ">", "<<", "<<<", "$(", ")", "`", '"', "'"]
         + ["git", "diff", "show", "-C", "HEAD:", "HEAD:docs/a.md", "HEAD~1:docs/a.md", "--", "-U"]
         + ["", '""', "''"])


def sequences():
    """The generated token sequences, the same on every run: 1 to 8 tokens of ``VOCAB``; a third of them start with
    ``git diff`` or ``git show``, so the git words meet a git command."""
    rng = random.Random(SEED)
    out = []
    for _ in range(SEQUENCES):
        toks = [rng.choice(VOCAB) for _ in range(rng.randint(1, 8))]
        if rng.random() < 1 / 3:
            toks = ["git", rng.choice(["diff", "show"])] + toks
        out.append(toks)
    return out


def failure(root, toks, n):
    command = " ".join(toks)
    return error_of("Bash", {"command": command}, root, RESEARCH if n % 2 == 0 else ENGINEER) or (
        "" if n % 2 == 0 else error_of("Bash", {"command": command}, root, RESEARCH))


def shrink(root, toks, n):
    """The sequence with tokens dropped one at a time while it still fails."""
    i = 0
    while i < len(toks):
        cut = toks[:i] + toks[i + 1:]
        if cut and failure(root, cut, n):
            toks = cut
        else:
            i += 1
    return toks


def test_r5_property_no_generated_token_sequence_makes_the_judge_raise(proj):
    """Over 1500 seeded token sequences (``random.Random(20261114)``): shell words, operators, git words and empty
    strings joined by spaces, through ``_Judge.tool`` (research) and ``decide`` (research and engineer, by turns):
    never an exception in the judge, never one raised by or hidden in the product. On a failure the first failing
    sequence is shrunk (tokens dropped while it still fails) and printed with the count of failing sequences.
    Red on the base: sequences holding a git revision the judge cannot classify (``git diff … HEAD:docs/a.md …``,
    ``git diff HEAD:``) raise ``PolicyError(_REV_FAULT)`` in reads.py ``_Judge.ask``."""
    start = time.monotonic()
    failing = []
    for n, toks in enumerate(sequences()):
        why = failure(proj, toks, n)
        if why:
            failing.append((n, toks, why))
    spent = time.monotonic() - start
    if failing:
        n, toks, _ = failing[0]
        small = shrink(proj, toks, n)
        pytest.fail(f"{len(failing)} of {SEQUENCES} sequences give rule error ({spent:.1f} s); the first, shrunk:\n"
                    f"  {' '.join(small)!r}\n  {failure(proj, small, n)}\n  (from {' '.join(toks)!r})")


# -- the error path stays: a genuine fault still refuses by it ---------------------------------------------------------------

def assert_error_path(tool, tool_input, root, who):
    """Refused by the error path: a fault message turned into a refusal (``…: the call is refused (fail closed,
    DEC-820)``) or the catch-all; never allowed, never raised out of ``decide``."""
    exc, got = decided(tool, tool_input, root, *who)
    assert exc is None, f"decide() raised {type(exc).__name__}: {exc}"
    assert got[0] == "deny", f"a genuine fault must refuse (fail closed), got {got}"
    assert got[1].endswith(ERROR_TAIL) or CATCH in got[1], f"want the error path's refusal, got: {got[1]}"


@pytest.fixture
def no_git(tmp_path, monkeypatch):
    """``PATH`` holds no git (an empty folder only)."""
    empty = tmp_path / "no-git-bin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    return str(empty)


@pytest.mark.parametrize("command", ["git diff HEAD~1 HEAD", "git log -p"], ids=["diff-two-commits", "log-p"])
def test_r5_a_genuine_fault_git_missing_from_path_still_refuses_by_the_error_path(proj, no_git, command):
    """Green on the base: the judge must ask git whether the commits hold the hidden part; reads.py ``_git`` gets an
    ``OSError`` and raises ``PolicyError``, ``_Judge.ask`` re-raises ``_REV_FAULT``, the product refuses "…: the call is
    refused (fail closed, DEC-820)". Kept: a git that cannot be run is a genuine fault."""
    assert_error_path("Bash", {"command": command}, proj, RESEARCH)


def test_r5_a_genuine_fault_git_missing_from_path_refuses_a_blob_diff(proj, no_git):
    """Green on the base (refused by the revision fault): with no git the guard cannot tell whether ``HEAD:docs/a.md``
    names a blob, so a blob diff must not be allowed (any refusal)."""
    exc, got = decided("Bash", {"command": "git diff HEAD:docs/a.md HEAD:docs/b.md"}, proj, *RESEARCH)
    assert exc is None, f"decide() raised {type(exc).__name__}: {exc}"
    assert got[0] == "deny", f"with no git a blob diff is not known to be a read of visible paths, got {got}"


def test_r5_a_genuine_fault_git_missing_from_path_is_an_error_through_the_hook(proj, no_git):
    """Green on the base: the hook (its interpreter by absolute path, ``PATH`` with no git) exits 2 for a diff the
    judge must ask git about."""
    got = hook("Bash", {"command": "git diff HEAD~1 HEAD"}, proj, RESEARCH, path=no_git)
    assert got[0] == "deny" and got[2] == 2, f"want the error path (exit 2), got {got}"


@pytest.mark.parametrize("fault", ["folder", "bad-yaml"])
def test_r5_a_genuine_fault_an_unreadable_path_map_still_refuses_by_the_error_path(tmp_path, fault):
    """Green on the base: ``governance/project/path-map.yaml`` is a folder (an ``OSError`` on open) or holds YAML that
    does not parse: gov.util.parts ``evaluation_sets`` raises ``PolicyError`` from reads.py ``_hidden``, the product
    refuses by the error path, and the hook exits 2. Kept: the guard cannot know what the session is refused."""
    root = make_project(tmp_path)
    path_map = os.path.join(root, "governance", "project", "path-map.yaml")
    os.remove(path_map)
    if fault == "folder":
        os.mkdir(path_map)
    else:
        with open(path_map, "w", encoding="utf-8") as f:
            f.write("evaluation_sets:\n  w242a: [unclosed\n    hidden: {\n")
    assert_error_path("Bash", {"command": "cat docs/a.md"}, root, RESEARCH)
    assert_error_path("Read", {"file_path": "docs/a.md"}, root, RESEARCH)
    got = hook("Bash", {"command": "cat docs/a.md"}, root, RESEARCH)
    assert got[0] == "deny" and got[2] == 2, f"want the hook's error path (exit 2), got {got}"
