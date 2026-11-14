"""W2-42a reopened, third round: R3 and the fallback's here-string forms (DEC-1164 (18), the CTO's reopening of
2026-11-14; DEC-1028, DEC-958).

Bash takes a here-string ``<<< word`` anywhere in a simple command, like any redirect: the word after ``<<<`` is the
here-string's text (the command's standard input), and the words after it are still that command's arguments. The
rule the cases pin: the word after ``<<<`` is the text, never the command's end; the words after it stay the
command's arguments and their write targets are judged; the text given to ``bash <<<`` or ``sh <<<`` is a command
and is judged as one; what the guard still cannot read is refused (fail closed); read-only forms stay free.

Every case asks the product guard, ``decide("Bash", {"command": …}, root, "engineer", "DAEO-03ub", cwd=root,
flag="open")``, in a project of its own (``proj``): an in-progress engineer ticket ``DAEO-03ub`` allowing ``src/**``.
``T`` = ``tests/acceptance/X/zz.py`` (no engineer may write it); ``A`` = ``src/ok.py`` (allowed). Each form was run
through real bash in a scratch folder: every write named here is one bash performs, and each read-only form writes
nothing.

- ``test_r3_*``: a write argument after a here-string is seen (refused naming ``T``; ``A`` allowed).
- ``test_hstr_fallback_*``: ``bash <<<``/``sh <<<``/``xargs touch <<<`` with a write, a shell whose text cannot be
  known, and a body-less heredoc after a ``python3 -c`` write.
- ``test_hstr_read_only_*``: here-strings that write nothing stay allowed.
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
# A stand-in of the engineer's ticket for the here-string cases
"""

# -- R3: a write argument after a here-string; {w} is the write's target (T or A) --------------------------------------
R3_FORMS = [
    pytest.param("tee <<< \"x\" {w}", id="tee"),
    pytest.param("tee -a <<< \"x\" {w}", id="tee-append"),
    pytest.param("cp <<< x x.py {w}", id="cp"),
    pytest.param("tee <<< \"x\" {w}; echo done", id="tee-then-a-list"),
    pytest.param("echo a && tee <<< \"$v\" {w}", id="here-string-inside-a-list"),
]
R3_REDIRECT_AFTER = "cat <<< \"x\" > {w}"

# -- the fallback's here-string forms ---------------------------------------------------------------------------------
FALLBACK_FORMS = [
    pytest.param("bash <<< 'touch {w}'", id="bash-text-is-a-command"),
    pytest.param("sh <<< 'touch {w}'", id="sh-text-is-a-command"),
    pytest.param("xargs touch <<< {w}", id="xargs-passes-the-text-as-arguments"),
]
UNKNOWABLE_SHELL_TEXT = [
    pytest.param('bash <<< "$X"', id="bash-variable-text"),
    pytest.param('sh <<< "$(cat x.py)"', id="sh-substitution-text"),
]
BODYLESS_HEREDOC = [
    pytest.param("python3 -c \"open('{w}','w').write('x')\"; cat <<EOF", id="unquoted-delimiter"),
    pytest.param("python3 -c \"open('{w}','w').write('x')\"; cat <<'EOF'", id="quoted-delimiter"),
]

# -- the read-only forms stay free --------------------------------------------------------------------------------------
READ_ONLY = [
    pytest.param('grep -c b <<< "a"', id="grep-count"),
    pytest.param('wc -l <<< "$v"', id="wc-lines"),
    pytest.param('tr a b <<< "x"', id="tr"),
    pytest.param('cat <<< "x"', id="cat"),
    pytest.param('read -r a b <<< "x y"', id="read"),
    pytest.param("grep x <<< tests/acceptance/X/zz.py", id="grep-text-names-t"),
    pytest.param("cat <<< tests/acceptance/X/zz.py", id="cat-text-names-t"),
    pytest.param("bash <<< 'echo hi'", id="bash-text-writes-nothing"),
    pytest.param("sh <<< 'ls src'", id="sh-text-writes-nothing"),
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


# -- R3 ------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("template", R3_FORMS)
def test_r3_a_write_argument_after_a_here_string_is_seen_and_t_is_refused(proj, template):
    assert_refused_naming_t(template.replace("{w}", T), proj)


@pytest.mark.parametrize("template", R3_FORMS)
def test_r3_a_write_argument_after_a_here_string_to_an_allowed_path_is_allowed(proj, template):
    assert_allowed(template.replace("{w}", A), proj)


def test_r3_a_redirect_after_a_here_string_to_t_stays_refused(proj):
    assert_refused_naming_t(R3_REDIRECT_AFTER.replace("{w}", T), proj)


def test_r3_a_redirect_after_a_here_string_to_an_allowed_path_is_allowed(proj):
    assert_allowed(R3_REDIRECT_AFTER.replace("{w}", A), proj)


# -- the fallback's here-string forms ------------------------------------------------------------------------------------

@pytest.mark.parametrize("template", FALLBACK_FORMS)
def test_hstr_fallback_a_here_string_whose_text_writes_t_is_refused(proj, template):
    assert_refused(template.replace("{w}", T), proj)


@pytest.mark.parametrize("template", FALLBACK_FORMS)
def test_hstr_fallback_a_here_string_whose_text_writes_an_allowed_path_is_allowed(proj, template):
    assert_allowed(template.replace("{w}", A), proj)


@pytest.mark.parametrize("command", UNKNOWABLE_SHELL_TEXT)
def test_hstr_fallback_a_here_string_to_a_shell_whose_text_cannot_be_known_is_refused(proj, command):
    assert_refused(command, proj)


@pytest.mark.parametrize("template", BODYLESS_HEREDOC)
def test_hstr_fallback_a_bodyless_heredoc_after_a_python_write_of_t_is_refused(proj, template):
    assert_refused(template.replace("{w}", T), proj)


# -- the read-only forms stay free -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("command", READ_ONLY)
def test_hstr_read_only_a_here_string_that_writes_nothing_is_allowed(proj, command):
    assert_allowed(command, proj)
