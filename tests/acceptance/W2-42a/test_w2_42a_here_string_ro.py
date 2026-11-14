"""W2-42a reopened, fourth round: read-only here-string forms with an expanded text (DEC-1164 (18), the narrow check's
R3 F1; DEC-1028, DEC-958).

The R3 round made a here-string whose text the shell expands (``"$v"``, ``"$(…)"``) fail closed for any reader not on a
short data list. That refuses everyday read-only idioms (``read -r a <<< "$v"``, ``while read …; done <<<
"$(git status --porcelain)"``, ``mapfile``, ``sed``, ``bc``). The CTO's decided rule (F1 (a)):

1. ``read``, ``mapfile`` and ``readarray`` take a here-string as data, whatever its text; their own writes (a redirect)
   are judged as usual.
2. A loop's here-string (``while read -r f; do …; done <<< "$(…)"``) is data for the loop; the loop body's commands are
   judged by their own words.
3. Data readers that never run their input (``sed``, ``awk`` without ``system(``/``>``/``|`` in its script, ``bc``,
   ``grep``, ``wc``, ``cut``, ``tr``, ``sort``) take an expanded text as data; a reader whose script writes is judged
   on that script.
4. ``bash``, ``sh``, ``zsh``, ``dash``, ``xargs``, ``source``, ``eval`` and any reader not named keep R3's fail-closed
   rule for an unknown text.
5. Nothing R3's cases refuse becomes allowed; a ``$(…)`` inside the text still runs, so its writes are still judged.

Every case asks the product guard, ``decide("Bash", {"command": …}, root, "engineer", "DAEO-03ub", cwd=root,
flag="open")``, in a project of its own (``proj``): an in-progress engineer ticket ``DAEO-03ub`` allowing ``src/**``.
``T`` = ``tests/acceptance/X/zz.py`` (no engineer may write it); ``A`` = ``src/ok.py`` (allowed). Each form was run
through real bash in a scratch folder: every write named here is one bash performs, and each read-only form writes
nothing.

- ``test_hsro_read_only_*``: group RO, here-strings that write nothing stay allowed (the expanded text is data).
- ``test_hsro_write_*``: group RW, the same forms with a write: ``T`` refused (the reason names ``T``), ``A`` allowed.
- ``test_hsro_fail_closed_*``: group FC, R3's fail-closed forms stay refused (no target is required in the reason).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402

T = "tests/acceptance/X/zz.py"
A = "src/ok.py"
TICKET = """---
id: DAEO-03ub
status: in_progress
type: task
role: engineer
wbs_id: W2-42a
allowed_paths:
- src/**
---
# A stand-in of the engineer's ticket for the read-only here-string cases
"""

# -- group RO: read-only forms with an expanded text; each writes no file -------------------------------------------------
RO_FORMS = [
    pytest.param('read -r a <<< "$v"', id="read"),
    pytest.param('IFS=: read -r a b <<< "$line"', id="read-with-ifs-prefix"),
    pytest.param('read -r a b <<< "$(git rev-parse HEAD HEAD)"', id="read-of-a-substitution"),
    pytest.param('v=$(git log -1); read -r a <<< "$v"', id="read-of-a-variable-set-by-substitution"),
    pytest.param('mapfile -t L <<< "$(ls)"', id="mapfile"),
    pytest.param('readarray -t L <<< "$v"', id="readarray"),
    pytest.param('while read -r f; do echo "$f"; done <<< "$(git status --porcelain)"', id="while-read-loop"),
    pytest.param('sed \'s/a/b/\' <<< "$v"', id="sed-substitution-script"),
    pytest.param('awk \'{print $1}\' <<< "$line"', id="awk-print-script"),
    pytest.param('bc <<< "$x + 1"', id="bc"),
    # variants of the same rule
    pytest.param('read -ra arr <<< "$v"', id="read-into-an-array"),
    pytest.param('until read -r l; do echo "$l"; done <<< "$v"', id="until-read-loop"),
    pytest.param('while IFS= read -r l; do printf \'%s\\n\' "$l"; done <<< "$v"', id="while-ifs-read-loop"),
]
# data readers the guard already lets through today: kept as guards
RO_GUARDS = [
    pytest.param('grep x <<< "$v"', id="grep"),
    pytest.param('wc -l <<< "$(ls)"', id="wc"),
    pytest.param('cut -d: -f1 <<< "$v"', id="cut"),
    pytest.param('tr a b <<< "$v"', id="tr"),
    pytest.param('sort <<< "$v"', id="sort"),
]

# -- group RW: the same forms with a write; {w} is the write's target (T or A) ---------------------------------------------
RW_FORMS = [
    pytest.param('read -r a <<< "$v" > {w}', id="read-redirect"),
    pytest.param('mapfile -t L <<< "$v"; touch {w}', id="mapfile-then-touch"),
    pytest.param('while read -r f; do touch {w}; done <<< "$(ls)"', id="loop-body-touch"),
    pytest.param('while read -r f; do cp "$f" {w}; done <<< "$v"', id="loop-body-cp"),
    pytest.param('sed \'s/a/b/\' <<< "$v" > {w}', id="sed-redirect"),
    pytest.param('sort -o {w} <<< "$v"', id="sort-o"),
    pytest.param('read -r a <<< "$(touch {w})"', id="read-text-substitution-writes"),
    pytest.param('while read -r f; do echo "$f"; done <<< "$(touch {w})"', id="loop-text-substitution-writes"),
    pytest.param('sed \'s/a/b/\' <<< "$(touch {w})"', id="sed-text-substitution-writes"),
]

# -- group FC: R3's fail-closed forms stay refused ---------------------------------------------------------------------------
FC_FORMS = [
    pytest.param('bash <<< "$v"', id="bash"),
    pytest.param('sh <<< "$(cat x.py)"', id="sh-substitution"),
    pytest.param('zsh <<< "$v"', id="zsh"),
    pytest.param('dash <<< "$v"', id="dash"),
    pytest.param('xargs touch <<< "$v"', id="xargs"),
    pytest.param('source /dev/stdin <<< "$v"', id="source"),
    pytest.param('. /dev/stdin <<< "$v"', id="dot"),
    pytest.param('eval "$v"', id="eval"),
    pytest.param('python3 <<< "$v"', id="python3-a-reader-not-named"),
    pytest.param('perl <<< "$v"', id="perl-a-reader-not-named"),
    pytest.param('awk \'{print}\' <<< "$(cat x)" | sh', id="awk-piped-to-sh"),
    pytest.param('while read -r f; do bash -c "$f"; done <<< "$v"', id="loop-body-bash-c"),
    pytest.param('while read -r f; do eval "$f"; done <<< "$v"', id="loop-body-eval"),
]
FC_T_FORMS = [
    pytest.param('awk \'{print > "tests/acceptance/X/zz.py"}\' <<< "$v"', id="awk-redirect-script-writes-t"),
    pytest.param('awk \'{system("touch tests/acceptance/X/zz.py")}\' <<< "$v"', id="awk-system-script-writes-t"),
    pytest.param('sed \'w tests/acceptance/X/zz.py\' <<< "$v"', id="sed-w-command-writes-t"),
    pytest.param('sed -i \'s/a/b/\' tests/acceptance/X/zz.py <<< "$v"', id="sed-i-writes-t"),
]


@pytest.fixture
def proj(tmp_path, monkeypatch):
    """The case's project (real path): an engineer's in-progress ticket DAEO-03ub allowing ``src/**``, the file the
    commands name (``x.py``) and an empty ``tests/acceptance/X/``; no session variable set."""
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
    return os.path.realpath(str(root))


def decide(command, root):
    """The product guard's decision on the call for an engineer on DAEO-03ub: ``(decision, why)``."""
    from gov.guard.decide import decide as product_decide
    return product_decide("Bash", {"command": command}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")


def assert_allowed(command, root):
    got, why = decide(command, root)
    assert got == "allow", f"want allow, got {got}: {why}\n--- the command ---\n{command}"


def assert_refused_naming_t(command, root):
    """Refused because it writes T: the reason names T."""
    got, why = decide(command, root)
    assert got == "deny", f"want deny (bash writes {T}), got {got}: {why}\n--- the command ---\n{command}"
    assert T in why, f"want the reason to name {T}, got: {why}\n--- the command ---\n{command}"


def assert_refused(command, root):
    """Refused, whatever the reason (the reason is in the message)."""
    got, why = decide(command, root)
    assert got == "deny", f"want deny, got {got}: {why}\n--- the command ---\n{command}"


# -- group RO --------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("command", RO_FORMS)
def test_hsro_read_only_a_reader_of_an_expanded_here_string_that_writes_nothing_is_allowed(proj, command):
    assert_allowed(command, proj)


@pytest.mark.parametrize("command", RO_GUARDS)
def test_hsro_read_only_a_data_reader_of_an_expanded_here_string_stays_allowed(proj, command):
    assert_allowed(command, proj)


# -- group RW --------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("template", RW_FORMS)
def test_hsro_write_a_read_only_form_that_writes_t_is_refused_naming_t(proj, template):
    assert_refused_naming_t(template.replace("{w}", T), proj)


@pytest.mark.parametrize("template", RW_FORMS)
def test_hsro_write_a_read_only_form_that_writes_an_allowed_path_is_allowed(proj, template):
    assert_allowed(template.replace("{w}", A), proj)


# -- group FC --------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("command", FC_FORMS)
def test_hsro_fail_closed_a_shell_or_unknown_reader_of_an_expanded_text_is_refused(proj, command):
    assert_refused(command, proj)


@pytest.mark.parametrize("command", FC_T_FORMS)
def test_hsro_fail_closed_a_writing_script_over_a_here_string_writing_t_is_refused(proj, command):
    # ``sed -i`` rewrites T only where it exists: make it exist, so the form is a real write of T
    with open(os.path.join(proj, T), "w", encoding="utf-8") as f:
        f.write("a\n")
    assert_refused(command, proj)
