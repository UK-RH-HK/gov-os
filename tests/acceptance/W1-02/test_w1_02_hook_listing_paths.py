"""W1-02 — the hook-listing helper redacts a deny rule's absolute path held bare in a hook command (DEC-548, DP-2).

The helper (``python3 -m gov.guard.hooks``, interface in the README and in
``test_w1_02_hook_listing.py``) replaces a whole value of ``permissions.deny``
inside a hook command by ``[redacted]``. That stands. DEC-548 adds: "and also an
absolute path that a deny rule carries wherever a hook command holds it bare".

**Which spelling of a deny rule carries an absolute path.** Settled from the
stand-in deny lines the suites use and from the guard's own writer of deny
lines: the argument starts with two slashes, ``Tool(//<absolute path>…)``, and
the path it carries is the argument without its first slash and without its
tail. The tail is ``/**``, ``/`` or nothing; a blank may follow the opening
parenthesis; the path may go below a folder (``//<path>/cases/**`` carries
``<path>/cases``); the tool may be any (``Read``, ``Edit``).

**What carries none**, and so redacts nothing but its own whole value: a command
pattern (``Bash(name:*)``), a glob relative to the working folder
(``Read(./folder/**)``, ``Read(**/*.ext)``). No side is taken on an argument
that starts with one slash (relative to the project in the harness) or with
``~/`` (relative to the home folder).

Every settings file here is a stand-in written by the case; the paths in its
deny lines are made up and are never created. The helper is run as a process.

Red before the change: the helper prints the bare path. The cases named
``…_is_not_blanked``, ``…_prints_unchanged`` and ``…_whole_value…`` are green
today and stay green.
"""

from __future__ import annotations

import json

import pytest

import w1_02_protected_support as protected

R = protected.REDACTED
BEFORE = "echo w1-02-stand-in-before "
AFTER = " w1-02-stand-in-after"


@pytest.fixture()
def held(tmp_path):
    """A made-up absolute path for a stand-in deny line. It is never created."""
    return tmp_path / "sandbox" / "elsewhere" / "w1-02-stand-in-held-out"


@pytest.fixture()
def second(tmp_path):
    return tmp_path / "sandbox" / "elsewhere" / "w1-02-second-stand-in"


@pytest.fixture()
def third(tmp_path):
    return tmp_path / "sandbox" / "another-place" / "w1-02-third-stand-in"


def _settings(deny, commands):
    """A stand-in settings file: the deny lines, and one hook entry per command."""
    return {
        "permissions": {"allow": [protected.STAND_IN_ALLOW], "deny": list(deny)},
        "hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": command}
                                                                 for command in commands]}]},
    }


def _commands(project, sandbox, deny, commands):
    """The commands the helper lists for a stand-in settings file with ``deny`` and ``commands``."""
    protected.write_settings(project, _settings(deny, commands))
    run = protected.run_helper(project, sandbox)
    assert run.returncode == 0, f"the helper exited with {run.returncode}"
    try:
        rows = json.loads(run.stdout)
    except ValueError:
        pytest.fail("the helper's standard output is not one JSON document", pytrace=False)
    assert [sorted(row) for row in rows] == [["command", "event", "matcher"]] * len(commands), (
        "the listing does not hold one row with event, matcher and command per hook command"
    )
    return [row["command"] for row in rows], run


def _assert_gone(run, paths, what):
    """Nothing of a redacted path is left: neither the path nor its last part, anywhere in what the helper wrote."""
    said = run.stdout + "\n" + run.stderr
    left = [index for index, path in enumerate(paths) for part in (str(path), path.name) if part in said]
    # The paths are not put in the message: a failure must not print what the helper must not print.
    assert not left, f"{what}: the helper's output still carries a deny rule's path (positions {sorted(set(left))})"


# name -> (the deny rule for the path ``p``, the absolute path that rule carries).
SPELLINGS = {
    "with-a-wildcard-tail": (lambda p: f"Read(/{p}/**)", lambda p: p),
    "with-no-tail": (lambda p: f"Read(/{p})", lambda p: p),
    "with-a-trailing-slash": (lambda p: f"Read(/{p}/)", lambda p: p),
    "with-a-blank-before-the-path": (lambda p: f"Read( /{p}/**)", lambda p: p),
    "below-the-folder": (lambda p: f"Read(/{p}/cases/**)", lambda p: p / "cases"),
    "of-another-tool": (lambda p: f"Edit(/{p}/**)", lambda p: p),
}


# --------------------------------------------------------------------------
# Redacted: the path bare, with the rule's wildcard part, as the start of a longer path
# --------------------------------------------------------------------------

@pytest.mark.parametrize("spelling", sorted(SPELLINGS))
def test_a_deny_rule_s_absolute_path_held_bare_in_a_hook_command_is_redacted(project, sandbox, held, spelling):
    """DP-2: the path without the rule around it, for each spelling of an absolute path in a deny rule."""
    rule, carried = SPELLINGS[spelling]
    path = carried(held)
    commands, run = _commands(project, sandbox, [rule(held)], [f"{BEFORE}{path}{AFTER}"])
    assert commands == [f"{BEFORE}{R}{AFTER}"], (
        f"a deny rule {spelling}: the bare path in a hook command was not replaced by {R}, or more than it was"
    )
    _assert_gone(run, [path], f"a deny rule {spelling}")


# name -> what the hook command holds for the path ``p`` of the rule ``Read(//p/**)``.
WITH_THE_WILDCARD_PART = {
    "the-path-and-the-wildcard-part": lambda p: f"{p}/**",
    "the-rule-s-argument-as-written": lambda p: f"/{p}/**",
    "the-path-and-a-slash": lambda p: f"{p}/",
    "the-path-in-double-quotes": lambda p: f'"{p}"',
    "the-path-after-an-equals-sign": lambda p: f"--exclude={p}",
}


@pytest.mark.parametrize("form", sorted(WITH_THE_WILDCARD_PART))
def test_the_path_with_the_rule_s_wildcard_part_or_inside_a_word_is_redacted(project, sandbox, held, form):
    """DP-2: with and without the rule's trailing wildcard part, and wherever in a word the command holds it."""
    text = WITH_THE_WILDCARD_PART[form](held)
    commands, run = _commands(project, sandbox, [f"Read(/{held}/**)"], [f"{BEFORE}{text}{AFTER}"])
    _assert_gone(run, [held], f"a hook command that holds {form}")
    assert R in commands[0], f"a hook command that holds {form}: nothing was replaced by {R}"
    assert commands[0].startswith(BEFORE) and commands[0].endswith(AFTER), (
        f"a hook command that holds {form}: the rest of the command did not stay"
    )


LONGER = {
    "a-file-below-the-folder": lambda p: f"cat {p}/answers/case-1.md",
    "a-script-below-the-folder-in-quotes": lambda p: f'python3 "{p}/tools/check.py" --all',
}


@pytest.mark.parametrize("spelling", ("with-a-wildcard-tail", "with-no-tail"))
@pytest.mark.parametrize("form", sorted(LONGER))
def test_the_path_as_the_start_of_a_longer_path_is_redacted(project, sandbox, held, form, spelling):
    """DP-2: what is below a held-out folder says where the folder is."""
    rule, _ = SPELLINGS[spelling]
    command = LONGER[form](held)
    commands, run = _commands(project, sandbox, [rule(held)], [command])
    _assert_gone(run, [held], f"a hook command that holds {form} (rule {spelling})")
    assert R in commands[0], f"a hook command that holds {form}: nothing was replaced by {R}"
    assert commands[0].split()[0] == command.split()[0], "the program of the hook command did not stay"


def test_every_place_a_command_holds_the_path_is_redacted(project, sandbox, held):
    """DP-2: "wherever a hook command holds it": twice in one command, and in every command."""
    deny = [f"Read(/{held}/**)"]
    commands, run = _commands(project, sandbox, deny, [f"diff {held} {held}", f"{BEFORE}{held}{AFTER}", "echo none"])
    assert commands == [f"diff {R} {R}", f"{BEFORE}{R}{AFTER}", "echo none"]
    _assert_gone(run, [held], "three hook commands")


# --------------------------------------------------------------------------
# Several deny rules
# --------------------------------------------------------------------------

def test_the_paths_of_several_deny_rules_are_all_redacted(project, sandbox, held, second, third):
    """DP-2: several rules, of both kinds; a whole deny value and a bare path in one command."""
    whole = f"Read(/{held}/**)"
    deny = [protected.STAND_IN_DENY_BASH, whole, "Read(./w1-02-secrets/**)", f"Read(/{second})", f"Edit(/{third}/**)"]
    commands, run = _commands(project, sandbox, deny, [
        f"ls {held} {second} {third}",
        f"{BEFORE}{second}{AFTER}",
        f"echo {whole} then {third} end",
        protected.GUARD_COMMAND,
    ])
    assert commands == [f"ls {R} {R} {R}", f"{BEFORE}{R}{AFTER}", f"echo {R} then {R} end", protected.GUARD_COMMAND]
    _assert_gone(run, [held, second, third], "the listing for five deny rules")


def test_a_path_that_starts_like_another_rule_s_path_is_redacted_whole(project, sandbox, held):
    """DP-2: nothing of a redacted path is left: one rule's path is the first characters of another's."""
    longer = held.with_name(held.name + "-two")
    for deny in ([f"Read(/{held}/**)", f"Read(/{longer}/**)"], [f"Read(/{longer}/**)", f"Read(/{held}/**)"]):
        commands, run = _commands(project, sandbox, deny, [f"{BEFORE}{longer}{AFTER}", f"{BEFORE}{held}{AFTER}"])
        assert commands == [f"{BEFORE}{R}{AFTER}", f"{BEFORE}{R}{AFTER}"], (
            "a part of the longer of two deny paths is left beside the redaction, or the rest of a command changed"
        )
        _assert_gone(run, [longer, held], "the listing for two deny rules whose paths start alike")


# --------------------------------------------------------------------------
# Not blanked: green today, and they stay green
# --------------------------------------------------------------------------

# name -> (a deny rule whose argument is no absolute path, a hook command that holds the argument bare).
NOT_A_PATH = {
    "a-command-pattern": ("Bash(w1-02-stand-in-denied:*)",
                          "w1-02-stand-in-denied --check && echo w1-02-stand-in-denied:* w1-02-stand-in-denied"),
    "a-relative-glob-with-a-dot": ("Read(./w1-02-secrets/**)", "ls ./w1-02-secrets/** ./w1-02-secrets w1-02-secrets"),
    "a-relative-glob": ("Read(**/*.w1-02-key)", "find . -name '*.w1-02-key' -o -path '**/*.w1-02-key'"),
}


@pytest.mark.parametrize("kind", sorted(NOT_A_PATH))
def test_the_argument_of_a_deny_rule_that_is_no_absolute_path_is_not_blanked(project, sandbox, held, kind):
    """DP-2: such a rule redacts nothing but its own whole value; ordinary text of a command stays."""
    rule, command = NOT_A_PATH[kind]
    commands, _ = _commands(project, sandbox, [rule, f"Read(/{held}/**)"], [command, f"echo {rule} end"])
    assert commands[0] == command, f"a hook command was changed for {kind} in a deny rule"
    assert commands[1] == f"echo {R} end", f"the whole value of a deny rule ({kind}) inside a hook command is not redacted"


def test_a_hook_command_that_holds_no_deny_path_prints_unchanged(project, sandbox, held, second):
    """DP-2: other paths, the folder above a deny path and a sibling of it are no deny path."""
    plain = [
        protected.GUARD_COMMAND,
        protected.CHECK_COMMAND,
        "/usr/bin/env python3 /opt/w1-02-stand-in/tool.py --root /",
        f"ls {held.parent} {held.parent}/w1-02-another-folder",
    ]
    commands, _ = _commands(project, sandbox, [f"Read(/{held}/**)", f"Read(/{second})", protected.STAND_IN_DENY_BASH],
                            plain)
    assert commands == plain


def test_a_whole_deny_value_with_an_absolute_path_is_still_redacted_as_one(project, sandbox, held):
    """As built and held: the rule around the path goes with it, and the command's other words stay."""
    whole = f"Read(/{held}/**)"
    commands, run = _commands(project, sandbox, [whole], [f"{BEFORE}{whole}{AFTER}"])
    assert commands == [f"{BEFORE}{R}{AFTER}"]
    _assert_gone(run, [held], "a whole deny value")
