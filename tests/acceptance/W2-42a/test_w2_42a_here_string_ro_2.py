"""W2-42a reopened, fifth round: a here-string read as data must not hide a command it feeds (DEC-1164 (18), the R3 F1
second batch; DEC-1028, DEC-958).

The CTO's F1 (a) rule (pinned in ``test_w2_42a_here_string_ro.py``): ``read``, ``mapfile`` and ``readarray`` take a
here-string as data, whatever its text, and a loop's here-string is data for the loop. Taking the text as data is only
safe while the data is not run. Bash runs it in two ways the guard must still refuse (nothing refused before the rule
may become allowed when real bash writes ``T``):

1. A command word taken from a variable the here-string fed: ``read`` (alone or as a loop's condition) binds ``f``/``a``
   from the text, and a later word uses it as a command's name (``$f``, ``${l}``, ``"$f" x``, ``$a $b``, or after a
   prefix ``env``/``command``/``time``). The guard cannot know that command: the call is refused whatever the text.
2. ``mapfile``/``readarray`` with a callback (``-C cb``, joined ``-tC cb``): bash runs the callback as a command for each
   quantum of lines. A literal callback is judged as that command; a callback the guard cannot know is refused.

Every case asks the product guard, ``decide("Bash", {"command": …}, root, "engineer", "DAEO-03ub", cwd=root,
flag="open")``, in a project of its own (``proj``): an in-progress engineer ticket ``DAEO-03ub`` allowing ``src/**``.
``T`` = ``tests/acceptance/X/zz.py`` (no engineer may write it); ``A`` = ``src/ok.py`` (allowed). Each refused form with a
literal ``touch T`` text or callback was run through real bash in a scratch folder and wrote ``T`` (for the ``"$v"``
forms with ``v='touch T'``; ``"$f" x`` needs a one-word command, so there ``v`` was a script path that touches ``T``).

- ``test_hsro2_read_var_command_*``: group V, a command word from a variable a here-string fed is refused.
- ``test_hsro2_callback_*``: group CB, a ``mapfile``/``readarray`` callback is a command: judged, or refused if unknown.
- ``test_hsro2_guard_*``: group G, forms that only use the variable as data stay allowed (green at the base).
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
# A stand-in of the engineer's ticket for the here-string command-word and callback cases
"""

# -- group V: the variable's value is run; {w} is the write's target (T or A) -----------------------------------------------
V_LITERAL_FORMS = [
    pytest.param("while read -r f; do $f; done <<< 'touch {w}'", id="loop-read-then-run-f"),
    pytest.param("while read -r a b; do $a $b; done <<< 'touch {w}'", id="loop-read-two-then-run-a-b"),
    pytest.param("read -r a b <<< 'touch {w}'; $a $b", id="read-two-then-run-a-b"),
]
V_UNKNOWN_FORMS = [
    pytest.param('read -r a b <<< "$v"; $a $b', id="read-two-from-v-then-run-a-b"),
    pytest.param('read -r a <<< "$v"; $a', id="read-from-v-then-run-a"),
    pytest.param('while read -r l; do ${l}; done <<< "$v"', id="loop-run-braced-l"),
    pytest.param('while read -r f; do "$f" x; done <<< "$v"', id="loop-run-quoted-f-with-an-argument"),
    pytest.param('while read -r f; do env $f; done <<< "$v"', id="loop-env-f"),
    pytest.param('while read -r f; do command $f; done <<< "$v"', id="loop-command-f"),
    pytest.param('while read -r f; do time $f; done <<< "$v"', id="loop-time-f"),
]

# -- group CB: a mapfile/readarray callback is run as a command ------------------------------------------------------------
CB_LITERAL_FORMS = [
    pytest.param("mapfile -C 'touch {w}' -c 1 L <<< \"$v\"", id="mapfile-literal-callback"),
    pytest.param("readarray -tC 'touch {w}' -c1 L <<< \"$v\"", id="readarray-joined-tC-literal-callback"),
]
CB_UNKNOWN_FORMS = [
    pytest.param('mapfile -C cb L <<< "$v"', id="mapfile-callback-a-function-the-guard-cannot-read"),
    pytest.param('mapfile -t -C "$cb" L <<< "$v"', id="mapfile-callback-from-a-variable"),
]

# -- group G: the variable is data, not a command name: stays allowed ------------------------------------------------------
GUARDS = [
    pytest.param('while read -r f; do echo "$f"; done <<< "$v"', id="loop-echo-f"),
    pytest.param('read -r a b <<< "$v"; echo "$a" "$b"', id="read-then-echo"),
    pytest.param("while read -r f; do printf '%s\\n' \"$f\"; done <<< \"$(git status --porcelain)\"",
                 id="loop-printf-of-a-porcelain-listing"),
    pytest.param('mapfile -t L <<< "$(ls)"', id="mapfile-of-a-listing"),
    pytest.param('readarray -t L <<< "$v"; echo "${L[0]}"', id="readarray-then-echo-element"),
    pytest.param('while read -r f; do grep -c x "$f"; done <<< "$(ls)"', id="loop-grep-with-f-as-an-argument"),
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


def assert_refused(command, root):
    """Refused, whatever the reason (the reason is in the message)."""
    got, why = decide(command, root)
    assert got == "deny", f"want deny, got {got}: {why}\n--- the command ---\n{command}"


# -- group V ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("template", V_LITERAL_FORMS)
def test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused(proj, template):
    assert_refused(template.replace("{w}", T), proj)


@pytest.mark.parametrize("template", V_LITERAL_FORMS)
def test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path(proj, template):
    # the guard cannot know the command the variable names, so it refuses whatever the text says
    assert_refused(template.replace("{w}", A), proj)


@pytest.mark.parametrize("command", V_UNKNOWN_FORMS)
def test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused(proj, command):
    assert_refused(command, proj)


# -- group CB --------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("template", CB_LITERAL_FORMS)
def test_hsro2_callback_a_literal_callback_that_writes_t_is_refused(proj, template):
    assert_refused(template.replace("{w}", T), proj)


@pytest.mark.parametrize("command", CB_UNKNOWN_FORMS)
def test_hsro2_callback_a_callback_the_guard_cannot_know_is_refused(proj, command):
    assert_refused(command, proj)


# -- group G ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("command", GUARDS)
def test_hsro2_guard_a_variable_used_as_data_and_not_as_a_command_name_stays_allowed(proj, command):
    assert_allowed(command, proj)
