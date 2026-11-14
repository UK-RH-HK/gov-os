"""W2-42a reopened, second round (DEC-1174 (1); the CTO's P-03ub-APOS-3 (1) and P-03ub-APOS-4 (a)).

The narrow check of the apostrophe fix found (F1) that the product guard takes a ``#`` after a blank inside a
parameter expansion ``${…}`` for the start of a comment and drops the rest of the line, and with it a write that bash
runs: the call is allowed and bash writes ``T`` (a fail-open). Bash never takes a ``#`` inside ``${…}`` for a
comment, at any depth, quoted or not. (F4) a here-string holding `` #`` (``grep -c b <<< "a # b"``) is refused as
"the command cannot be read" although it writes nothing. Departure 1, accepted by name: a ``python3 -c`` string's
writes are write targets.

Every case asks the product guard, ``decide("Bash", {"command": …}, root, "engineer", "DAEO-03ub", cwd=root,
flag="open")``, in a project of its own (``proj``, as in ``test_w2_42a_apostrophe.py``): an in-progress engineer ticket
``DAEO-03ub`` allowing ``src/**``. ``T`` = ``tests/acceptance/X/zz.py`` (no engineer may write it); ``A`` =
``src/ok.py`` (allowed). Each form below was run through real bash in a scratch folder: every write named here is
one bash performs (``echo hi # it's fine`` writes nothing).

- ``test_apos2_f1_*``: each ``${…}`` form holding `` #``, at the top level, as a ``bash <<'EOF'`` body and inside
  ``bash -c '…'``: refused naming ``T`` when it writes ``T``, allowed when it writes ``A``. The forms that never were
  comments (``${#v}``, ``${v#a}``, ``$#``) and a real comment (``echo hi # it's fine``) are kept as guards.
- ``test_apos2_f4_*``: a here-string holding `` #`` that writes nothing is allowed; one whose command writes is judged
  by its target (``T`` refused naming ``T``, not as unreadable; ``A`` allowed).
- ``test_apos2_dep1_*``: a standalone ``python3 -c`` write of ``T`` is refused, of ``A`` allowed; read-only one-liners
  are allowed.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402

T = "tests/acceptance/X/zz.py"
A = "src/ok.py"
UNREADABLE = "cannot be read"
TICKET = """---
id: DAEO-03ub
status: in_progress
type: task
role: engineer
wbs_id: W2-42a
allowed_paths:
- src/**
---
# A stand-in of the engineer's ticket for the apostrophe cases, second round
"""

# -- F1: a '#' inside ${…} never starts a comment ------------------------------------------------------------------------
# ``{w}`` is the write's target (T or A); ``{a}`` a first write that is always to an allowed path.
F1_FORMS = [
    ("strip-suffix-of-a-quoted-value", "v='a # b'; echo ${v%% #*} > {w}"),
    ("default-value-then-a-later-command", "echo ${x:- #a}; echo x > {w}"),
    ("pattern-substitution", "v='a #b'; echo ${v/ #/} > {w}"),
    ("while-read-loop-redirected", "while read -r l; do echo ${l%% #*}; done < f > {w}"),
    ("while-read-loop-appending-inside", "while read -r l; do k=${l%% #*}; echo $k >> {w}; done < f"),
    ("allowed-write-then-a-second-write", "echo ${X:- #} > {a}; cp x.py {w}"),
    ("double-quoted-expansion", 'echo "${v%% #*}" > {w}'),
    ("nested-expansion", "echo ${v:-${w%% #*}} > {w}"),
]
# The same in ``bash -c '…'`` (inner quotes made double where the form has single ones).
F1_BASH_C = [
    ("strip-suffix-of-a-quoted-value", "bash -c 'v=\"a # b\"; echo ${v%% #*} > {w}'"),
    ("default-value-then-a-later-command", "bash -c 'echo ${x:- #a}; echo x > {w}'"),
    ("pattern-substitution", "bash -c 'v=\"a #b\"; echo ${v/ #/} > {w}'"),
    ("while-read-loop-redirected", "bash -c 'while read -r l; do echo ${l%% #*}; done < f > {w}'"),
    ("while-read-loop-appending-inside", "bash -c 'while read -r l; do k=${l%% #*}; echo $k >> {w}; done < f'"),
    ("allowed-write-then-a-second-write", "bash -c 'echo ${X:- #} > {a}; cp x.py {w}'"),
    ("double-quoted-expansion", "bash -c 'echo \"${v%% #*}\" > {w}'"),
    ("nested-expansion", "bash -c 'echo ${v:-${w%% #*}} > {w}'"),
]
# The forms that never were comments: kept as guards (green on the base).
NEVER_COMMENTS = [
    ("length-expansion", "v=ab; echo ${#v} > {w}"),
    ("pattern-removal", "echo ${v#a} > {w}"),
    ("argument-count", "echo $# > {w}"),
]
NEVER_COMMENTS_BASH_C = [
    ("length-expansion", "bash -c 'v=ab; echo ${#v} > {w}'"),
    ("pattern-removal", "bash -c 'echo ${v#a} > {w}'"),
    ("argument-count", "bash -c 'echo $# > {w}'"),
]


def heredoc(line):
    """A ``bash <<'EOF'`` call whose body is the line."""
    return f"bash <<'EOF'\n{line}\nEOF"


def fill(template, target):
    """The command with ``{w}`` as the target and ``{a}`` as the allowed path."""
    return template.replace("{w}", target).replace("{a}", A)


WRAPPED = (
    [pytest.param(tpl, "top-level", id=f"top-level/{i}") for i, tpl in F1_FORMS]
    + [pytest.param(tpl, "heredoc", id=f"bash-heredoc-quoted/{i}") for i, tpl in F1_FORMS]
    + [pytest.param(tpl, "bash-c", id=f"bash-c/{i}") for i, tpl in F1_BASH_C]
)
NEVER_WRAPPED = (
    [pytest.param(tpl, "top-level", id=f"top-level/{i}") for i, tpl in NEVER_COMMENTS]
    + [pytest.param(tpl, "heredoc", id=f"bash-heredoc-quoted/{i}") for i, tpl in NEVER_COMMENTS]
    + [pytest.param(tpl, "bash-c", id=f"bash-c/{i}") for i, tpl in NEVER_COMMENTS_BASH_C]
)


def build(template, wrapper, target):
    command = fill(template, target)
    return heredoc(command) if wrapper == "heredoc" else command


# -- F4: a here-string holding ' #' ------------------------------------------------------------------------------------
F4_NO_WRITE = [
    pytest.param('grep -c b <<< "a # b"', id="grep-count"),
    pytest.param('wc -w <<< "one # two"', id="wc-words"),
    pytest.param("jq -r '.x' <<< '{\"x\": \"a # b\"}'", id="jq-raw"),
]
F4_WRITES = [
    ("grep-count-redirected", 'grep -c b <<< "a # b" > {w}'),
    ("tr-redirected", "tr a b <<< 'x # y' > {w}"),
]

# -- departure 1: python3 -c writes are write targets ----------------------------------------------------------------
DEP1_WRITE = "python3 -c \"open('{w}','w').write('x')\""
DEP1_READ_ONLY = [
    pytest.param("python3 -c \"import json; print(json.dumps({'a': 1}))\"", id="json-dumps"),
    pytest.param("python3 -c \"import os; print(os.listdir('.'))\"", id="os-listdir"),
    pytest.param("python3 -c \"import pathlib; print(pathlib.Path('README.md').read_text()[:10])\"",
                 id="pathlib-read-text"),
]


@pytest.fixture
def proj(tmp_path, monkeypatch):
    """The case's project (real path): an engineer's in-progress ticket DAEO-03ub allowing ``src/**``, the files the
    commands name (``x.py``, ``f``, ``README.md``, an empty ``tests/acceptance/X/``); no session variable set."""
    for name in s._SESSION:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "home").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    root = tmp_path / "proj"
    (root / "tests" / "acceptance" / "X").mkdir(parents=True)
    (root / "src").mkdir()
    (root / ".tickets").mkdir()
    (root / ".tickets" / "DAEO-03ub.md").write_text(TICKET, encoding="utf-8")
    (root / "x.py").write_text("x = 1\n", encoding="utf-8")
    (root / "f").write_text("a # b\nc #d\n", encoding="utf-8")
    (root / "README.md").write_text("# a project\n", encoding="utf-8")
    return os.path.realpath(str(root))


def decide(command, root):
    """The product guard's decision on the call for an engineer on DAEO-03ub: ``(decision, why)``."""
    from gov.guard.decide import decide as product_decide
    return product_decide("Bash", {"command": command}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")


def assert_allowed(command, root):
    got, why = decide(command, root)
    assert got == "allow", f"want allow, got {got}: {why}\n--- the command ---\n{command}"


def assert_refused_naming_t(command, root):
    """Refused because it writes T: the reason names T (not 'cannot be read', not another reason)."""
    got, why = decide(command, root)
    assert got == "deny", f"want deny (bash writes {T}), got {got}: {why}\n--- the command ---\n{command}"
    assert T in why, f"want the reason to name {T}, got: {why}\n--- the command ---\n{command}"


# -- F1: a '#' inside ${…} never starts a comment ----------------------------------------------------------------------

@pytest.mark.parametrize("template,wrapper", WRAPPED)
def test_apos2_f1_a_hash_inside_a_parameter_expansion_starts_no_comment_so_its_write_of_t_is_refused(
        proj, template, wrapper):
    assert_refused_naming_t(build(template, wrapper, T), proj)


@pytest.mark.parametrize("template,wrapper", WRAPPED)
def test_apos2_f1_a_hash_inside_a_parameter_expansion_with_a_write_of_an_allowed_path_is_allowed(
        proj, template, wrapper):
    assert_allowed(build(template, wrapper, A), proj)


@pytest.mark.parametrize("template,wrapper", NEVER_WRAPPED)
def test_apos2_f1_a_hash_that_never_was_a_comment_keeps_its_write_of_t_refused(proj, template, wrapper):
    assert_refused_naming_t(build(template, wrapper, T), proj)


@pytest.mark.parametrize("template,wrapper", NEVER_WRAPPED)
def test_apos2_f1_a_hash_that_never_was_a_comment_with_a_write_of_an_allowed_path_is_allowed(proj, template, wrapper):
    assert_allowed(build(template, wrapper, A), proj)


def test_apos2_f1_a_real_comment_with_an_apostrophe_and_no_write_is_allowed(proj):
    assert_allowed("echo hi # it's fine", proj)


def test_apos2_f1_a_write_of_t_before_a_real_comment_with_an_apostrophe_is_refused(proj):
    assert_refused_naming_t(f"echo hi > {T} # it's fine", proj)


# -- F4: a here-string holding ' #' is read, not refused as unreadable -------------------------------------------------

@pytest.mark.parametrize("command", F4_NO_WRITE)
def test_apos2_f4_a_here_string_holding_a_hash_that_writes_nothing_is_allowed(proj, command):
    assert_allowed(command, proj)


@pytest.mark.parametrize("template", [pytest.param(t, id=i) for i, t in F4_WRITES])
def test_apos2_f4_a_here_string_command_writing_t_is_refused_for_t_not_as_unreadable(proj, template):
    command = fill(template, T)
    got, why = decide(command, proj)
    assert got == "deny", f"want deny (bash writes {T}), got {got}: {why}\n--- the command ---\n{command}"
    assert T in why and UNREADABLE not in why, \
        f"want the reason to name {T}, not '{UNREADABLE}'; got: {why}\n--- the command ---\n{command}"


@pytest.mark.parametrize("template", [pytest.param(t, id=i) for i, t in F4_WRITES])
def test_apos2_f4_a_here_string_command_writing_an_allowed_path_is_allowed(proj, template):
    assert_allowed(fill(template, A), proj)


# -- departure 1: python3 -c writes are write targets ----------------------------------------------------------------

def test_apos2_dep1_a_python3_c_write_of_t_is_refused(proj):
    assert_refused_naming_t(fill(DEP1_WRITE, T), proj)


def test_apos2_dep1_a_python3_c_write_of_an_allowed_path_is_allowed(proj):
    assert_allowed(fill(DEP1_WRITE, A), proj)


@pytest.mark.parametrize("command", DEP1_READ_ONLY)
def test_apos2_dep1_a_read_only_python3_c_one_liner_is_allowed(proj, command):
    assert_allowed(command, proj)
