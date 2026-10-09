"""W1-02 — the hook-listing helper redacts a deny path spelled from the home folder (DEC-553, DP-7).

The helper (``python3 -m gov.guard.hooks``, interface in the README) replaces a
whole value of ``permissions.deny`` inside a hook command by ``[redacted]``,
and an absolute path a deny rule carries wherever a hook command holds it bare
(DEC-548). Both stand. DEC-553 adds: "The helper also redacts a deny path that
is spelled from the home folder, as written and with the home folder in its
place. A project-relative spelling is not redacted (it would blank ordinary
relative paths) and stays a residual."

**A deny path spelled from the home folder** is the argument of a deny rule
that starts with the home-folder shorthand and a slash: ``Tool(~/<path>…)``.
The path it carries is the argument without its tail (``/**``, ``/`` or
nothing); a blank may follow the opening parenthesis; the path may go below a
folder; the tool may be any. A hook command may hold that path in two
spellings, and both are redacted:

- **as written**: ``~/<path>``;
- **with the home folder in its place**: ``<home>/<path>``, the home folder
  being the ``HOME`` of the helper's environment.

``HOME`` is a stand-in in every case (an empty temporary folder); the real
home folder is never named or read. Every settings file is a stand-in written
by the case; the paths in its deny lines are made up and are never created.

**When the helper cannot tell the home folder** (no ``HOME`` in its
environment) no side is taken on the resolved spelling: the case holds only
that the helper does not fail and that the as-written spelling is redacted.

Red before the change: the helper prints the path in both spellings. The cases
named ``…_is_not_blanked``, ``…_prints_unchanged`` and ``…_whole_value…`` are
green today and stay green.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w1_02_protected_support as protected
import w1_02_support as support

R = protected.REDACTED
BEFORE = "echo w1-02-stand-in-before "
AFTER = " w1-02-stand-in-after"
# Made-up paths below the home folder, for stand-in deny lines. Each name appears in no other text of a case.
HELD = "w1-02-home-held/w1-02-home-answers"
SECOND = "w1-02-home-second"
OTHER = "w1-02-home-other"            # below the home folder too, and in no deny rule
PROJECT_RELATIVE = "w1-02-rel/secrets"


@pytest.fixture(scope="module")
def sandbox(tmp_path_factory):
    """One set of stand-in folders for the module, the stand-in home among them."""
    return support.make_sandbox(tmp_path_factory.mktemp("home-paths") / "sandbox")


@pytest.fixture(scope="module")
def project(hook, tmp_path_factory):
    """One project for the module: each case writes its own stand-in settings file into it before it asks."""
    return support.make_project(tmp_path_factory.mktemp("home-paths-project") / "project")


@pytest.fixture()
def home(sandbox):
    """The stand-in home folder: the ``HOME`` of the helper's environment."""
    return sandbox.home


@pytest.fixture()
def absolute(tmp_path):
    """A made-up absolute path outside the home folder, for a deny line of the kind DEC-548 covers."""
    return tmp_path / "sandbox" / "elsewhere" / "w1-02-stand-in-held-out"


def _settings(deny, commands):
    """A stand-in settings file: the deny lines, and one hook entry per command."""
    return {
        "permissions": {"allow": [protected.STAND_IN_ALLOW], "deny": list(deny)},
        "hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": command}
                                                                 for command in commands]}]},
    }


def _run(project, sandbox, with_home=True):
    """The helper as an agent's shell would run it; ``with_home`` False leaves ``HOME`` out of its environment."""
    env = support.hook_environment(project, sandbox)
    if not with_home:
        del env["HOME"]
    proc = subprocess.run([sys.executable, "-m", protected.HELPER_MODULE], capture_output=True, text=True,
                          cwd=str(project), env=env, timeout=support.HOOK_TIMEOUT_S, check=False)
    return protected.HelperRun(proc.returncode, proc.stdout, proc.stderr)


def _commands(project, sandbox, deny, commands, with_home=True):
    """The commands the helper lists for a stand-in settings file with ``deny`` and ``commands``."""
    protected.write_settings(project, _settings(deny, commands))
    run = _run(project, sandbox, with_home)
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
    """Nothing of a redacted path is left: neither the path nor any folder name of it, in what the helper wrote."""
    said = run.stdout + "\n" + run.stderr
    left = [index for index, path in enumerate(paths) for part in [path, *path.split("/")] if part in said]
    # The paths are not put in the message: a failure must not print what the helper must not print.
    assert not left, f"{what}: the helper's output still carries a deny rule's path (positions {sorted(set(left))})"


def _assert_listed(commands, expected, what):
    """The listed commands are the expected ones; a failure tells which rows differ, never their text."""
    wrong = [index for index, (got, want) in enumerate(zip(commands, expected)) if got != want]
    assert len(commands) == len(expected) and not wrong, (
        f"{what}: the listed command(s) at position(s) {wrong} differ from what is expected "
        f"(a deny path not replaced by {R}, or more than the path replaced)"
    )


# name -> (the deny rule for the path ``p`` below the home folder, the path below the home folder it carries).
SPELLINGS = {
    "with-a-wildcard-tail": (lambda p: f"Read(~/{p}/**)", lambda p: p),
    "with-no-tail": (lambda p: f"Read(~/{p})", lambda p: p),
    "with-a-trailing-slash": (lambda p: f"Read(~/{p}/)", lambda p: p),
    "with-a-blank-before-the-path": (lambda p: f"Read( ~/{p}/**)", lambda p: p),
    "below-the-folder": (lambda p: f"Read(~/{p}/cases/**)", lambda p: f"{p}/cases"),
    "of-another-tool": (lambda p: f"Edit(~/{p}/**)", lambda p: p),
}


# --------------------------------------------------------------------------
# Redacted: as written, with the home folder in its place, both
# --------------------------------------------------------------------------

@pytest.mark.parametrize("spelling", sorted(SPELLINGS))
def test_a_deny_path_spelled_from_the_home_folder_is_redacted_as_written(project, sandbox, spelling):
    """DP-7: the shorthand spelling, bare in a hook command, for each spelling of such a deny rule."""
    rule, carried = SPELLINGS[spelling]
    commands, run = _commands(project, sandbox, [rule(HELD)], [f"{BEFORE}~/{carried(HELD)}{AFTER}"])
    _assert_listed(commands, [f"{BEFORE}{R}{AFTER}"], f"a deny rule {spelling}, the path as written")
    _assert_gone(run, [carried(HELD)], f"a deny rule {spelling}, the path as written")


@pytest.mark.parametrize("spelling", sorted(SPELLINGS))
def test_a_deny_path_spelled_from_the_home_folder_is_redacted_with_the_home_folder_in_its_place(project, sandbox, home,
                                                                                                spelling):
    """DP-7: the absolute path the shorthand stands for, ``HOME`` being the helper's (a stand-in)."""
    rule, carried = SPELLINGS[spelling]
    commands, run = _commands(project, sandbox, [rule(HELD)], [f"{BEFORE}{home}/{carried(HELD)}{AFTER}"])
    _assert_listed(commands, [f"{BEFORE}{R}{AFTER}"], f"a deny rule {spelling}, the path with the home folder")
    _assert_gone(run, [carried(HELD)], f"a deny rule {spelling}, the path with the home folder")


@pytest.mark.parametrize("spelling", ("with-a-wildcard-tail", "with-no-tail", "below-the-folder"))
def test_both_spellings_in_one_command_are_redacted(project, sandbox, home, spelling):
    """DP-7: "as written and with the home folder in its place": both in the same command, in either order."""
    rule, carried = SPELLINGS[spelling]
    path = carried(HELD)
    commands, run = _commands(project, sandbox, [rule(HELD)], [
        f"diff ~/{path} {home}/{path}",
        f"diff {home}/{path} ~/{path} --brief",
        "echo none",
    ])
    _assert_listed(commands, [f"diff {R} {R}", f"diff {R} {R} --brief", "echo none"],
                   f"a deny rule {spelling}, both spellings in one command")
    _assert_gone(run, [path], f"a deny rule {spelling}, both spellings in one command")


# name -> what the hook command holds for the path ``p`` of the rule ``Read(~/p/**)``, the home folder being ``h``.
WITH_THE_WILDCARD_PART = {
    "as-written-with-the-wildcard-part": lambda p, h: f"~/{p}/**",
    "as-written-with-a-slash": lambda p, h: f"~/{p}/",
    "as-written-in-double-quotes": lambda p, h: f'"~/{p}"',
    "as-written-after-an-equals-sign": lambda p, h: f"--exclude=~/{p}",
    "resolved-with-the-wildcard-part": lambda p, h: f"{h}/{p}/**",
    "resolved-with-a-slash": lambda p, h: f"{h}/{p}/",
    "resolved-in-double-quotes": lambda p, h: f'"{h}/{p}"',
    "resolved-after-an-equals-sign": lambda p, h: f"--exclude={h}/{p}",
}


@pytest.mark.parametrize("form", sorted(WITH_THE_WILDCARD_PART))
def test_the_path_with_the_rule_s_wildcard_part_or_inside_a_word_is_redacted(project, sandbox, home, form):
    """DP-7: with and without the rule's trailing wildcard part, and wherever in a word the command holds it."""
    text = WITH_THE_WILDCARD_PART[form](HELD, home)
    commands, run = _commands(project, sandbox, [f"Read(~/{HELD}/**)"], [f"{BEFORE}{text}{AFTER}"])
    _assert_gone(run, [HELD], f"a hook command that holds the path {form}")
    assert R in commands[0], f"a hook command that holds the path {form}: nothing was replaced by {R}"
    assert commands[0].startswith(BEFORE) and commands[0].endswith(AFTER), (
        f"a hook command that holds the path {form}: the rest of the command did not stay"
    )


LONGER = {
    "a-file-below-the-folder-as-written": lambda p, h: f"cat ~/{p}/answers/case-1.md",
    "a-script-below-the-folder-resolved-in-quotes": lambda p, h: f'python3 "{h}/{p}/tools/check.py" --all',
}


@pytest.mark.parametrize("spelling", ("with-a-wildcard-tail", "with-no-tail"))
@pytest.mark.parametrize("form", sorted(LONGER))
def test_the_path_as_the_start_of_a_longer_path_is_redacted(project, sandbox, home, form, spelling):
    """DP-7: what is below a held-out folder says where the folder is. Only "the deny path is gone" is held."""
    rule, _ = SPELLINGS[spelling]
    command = LONGER[form](HELD, home)
    commands, run = _commands(project, sandbox, [rule(HELD)], [command])
    _assert_gone(run, [HELD], f"a hook command that holds {form} (rule {spelling})")
    assert R in commands[0], f"a hook command that holds {form}: nothing was replaced by {R}"
    assert commands[0].split()[0] == command.split()[0], "the program of the hook command did not stay"


# --------------------------------------------------------------------------
# Several deny rules, of both kinds together
# --------------------------------------------------------------------------

def test_the_paths_of_several_deny_rules_of_both_kinds_are_all_redacted(project, sandbox, home, absolute):
    """DP-7: an absolute deny path (DEC-548) and two spelled from the home folder, beside rules that carry none."""
    whole_absolute = f"Read(/{absolute}/**)"
    whole_home = f"Read(~/{HELD}/**)"
    deny = [protected.STAND_IN_DENY_BASH, whole_absolute, "Read(./w1-02-secrets/**)", whole_home, f"Edit(~/{SECOND})"]
    commands, run = _commands(project, sandbox, deny, [
        f"ls {absolute} ~/{HELD} {home}/{SECOND}",
        f"{BEFORE}{home}/{HELD}{AFTER}",
        f"echo {whole_home} then ~/{SECOND} and {whole_absolute} end",
        protected.GUARD_COMMAND,
    ])
    _assert_listed(commands, [f"ls {R} {R} {R}", f"{BEFORE}{R}{AFTER}", f"echo {R} then {R} and {R} end",
                              protected.GUARD_COMMAND], "the listing for five deny rules of both kinds")
    _assert_gone(run, [HELD, SECOND, absolute.name], "the listing for five deny rules of both kinds")


def test_a_home_path_that_starts_like_another_rule_s_path_is_redacted_whole(project, sandbox, home):
    """DP-7: nothing of a redacted path is left: one rule's path is the first characters of another's."""
    longer = SECOND + "-two"
    for deny in ([f"Read(~/{SECOND}/**)", f"Read(~/{longer}/**)"], [f"Read(~/{longer}/**)", f"Read(~/{SECOND}/**)"]):
        commands, run = _commands(project, sandbox, deny, [f"{BEFORE}~/{longer}{AFTER}", f"{BEFORE}{home}/{longer}{AFTER}",
                                                           f"{BEFORE}~/{SECOND}{AFTER}"])
        _assert_listed(commands, [f"{BEFORE}{R}{AFTER}"] * 3, "two deny rules whose paths start alike")
        _assert_gone(run, [longer, SECOND], "two deny rules whose paths start alike")


# --------------------------------------------------------------------------
# No HOME in the helper's environment
# --------------------------------------------------------------------------

def test_without_a_home_folder_the_helper_does_not_fail_and_redacts_the_path_as_written(project, sandbox):
    """No side on the resolved spelling when the helper cannot tell the home folder: the command holds none."""
    commands, run = _commands(project, sandbox, [f"Read(~/{HELD}/**)"],
                              [f"{BEFORE}~/{HELD}{AFTER}", protected.GUARD_COMMAND], with_home=False)
    _assert_listed(commands, [f"{BEFORE}{R}{AFTER}", protected.GUARD_COMMAND],
                   "a deny rule spelled from the home folder, with no HOME in the environment")
    _assert_gone(run, [HELD], "a deny rule spelled from the home folder, with no HOME in the environment")


# --------------------------------------------------------------------------
# Not blanked: green today, and they stay green
# --------------------------------------------------------------------------

# name -> (a deny rule in a spelling that is neither absolute nor from the home folder, a hook command that holds
# its argument bare, in the rule's own spelling and without the rule's first characters).
PROJECT_RELATIVE_RULES = {
    "one-leading-slash": (f"Read(/{PROJECT_RELATIVE}/**)",
                          f"ls /{PROJECT_RELATIVE}/** /{PROJECT_RELATIVE} {PROJECT_RELATIVE}"),
    "a-dot-and-a-slash": (f"Read(./{PROJECT_RELATIVE}/**)",
                          f"ls ./{PROJECT_RELATIVE}/** ./{PROJECT_RELATIVE} {PROJECT_RELATIVE}"),
    "a-bare-relative-glob": ("Read(**/*.w1-02-key)", "find . -name '*.w1-02-key' -o -path '**/*.w1-02-key'"),
}


@pytest.mark.parametrize("kind", sorted(PROJECT_RELATIVE_RULES))
def test_a_project_relative_deny_path_held_bare_is_not_blanked(project, sandbox, kind):
    """DP-7: "A project-relative spelling is not redacted": ordinary relative paths of a command stay.

    A deny rule spelled from the home folder stands beside it, so the new redaction is at work in the same listing.
    The whole value of the rule inside a hook command is still redacted, as built.
    """
    rule, command = PROJECT_RELATIVE_RULES[kind]
    commands, _ = _commands(project, sandbox, [rule, f"Read(~/{HELD}/**)"], [command, f"echo {rule} end"])
    assert commands[0] == command, f"a hook command was changed for a deny rule spelled with {kind}"
    assert commands[1] == f"echo {R} end", (
        f"the whole value of a deny rule spelled with {kind} inside a hook command is not redacted")


def test_the_home_folder_alone_and_another_path_below_it_print_unchanged(project, sandbox, home):
    """DP-7: the home folder is no deny path, and neither is a path below it that no deny rule carries."""
    plain = [
        "ls ~",
        f"ls {home}",
        "cd ~ && pwd",
        f"cat ~/{OTHER}/notes.md {home}/{OTHER}/notes.md",
        f"ls ~/{OTHER} {home}/{OTHER}",
        'echo "$HOME" ~/',
    ]
    commands, _ = _commands(project, sandbox, [f"Read(~/{HELD}/**)", f"Edit(~/{SECOND})"], plain)
    assert commands == plain, "a hook command that holds the home folder or another path below it was changed"


def test_a_hook_command_that_holds_no_deny_path_prints_unchanged(project, sandbox, absolute):
    """DP-7: with deny rules of both kinds in the file, the commands that hold none of their paths stay."""
    plain = [
        protected.GUARD_COMMAND,
        protected.CHECK_COMMAND,
        "/usr/bin/env python3 /opt/w1-02-stand-in/tool.py --root /",
        protected.STOP_COMMAND,
    ]
    deny = [f"Read(~/{HELD}/**)", f"Read(/{absolute}/**)", f"Edit(~/{SECOND}/)", protected.STAND_IN_DENY_BASH]
    commands, _ = _commands(project, sandbox, deny, plain)
    assert commands == plain


def test_a_whole_deny_value_spelled_from_the_home_folder_is_still_redacted_as_one(project, sandbox):
    """As built and held: the rule around the path goes with it, and the command's other words stay."""
    whole = f"Read(~/{HELD}/**)"
    commands, run = _commands(project, sandbox, [whole], [f"{BEFORE}{whole}{AFTER}"])
    _assert_listed(commands, [f"{BEFORE}{R}{AFTER}"], "a whole deny value spelled from the home folder")
    _assert_gone(run, [HELD], "a whole deny value spelled from the home folder")
