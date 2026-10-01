"""W1-02 — the guard resolves a Bash write target before judging it.

DEC-115 (refines DEC-111): "Before judging a Bash write target, the guard
expands ``~``, ``~user`` and environment variables from the hook's own
environment. Any target it still can't resolve (command substitution, an unset
or unknown variable, a glob it can't expand) is denied."

KPI success 1 and KPI failure 1 ("Any write outside allowed_paths is allowed").

The session is the engineer on DAEO-zz90 (``src/gov/guard/**``,
``tests/unit/guard/**``, …) unless a test says otherwise. The hook's environment
holds ``HOME`` (an empty directory outside the project and outside the scratch
set), ``TMPDIR`` (the scratch directory), ``CLAUDE_PROJECT_DIR`` (the project)
and the ``W1_02_*`` variables below. ``W1_02_NOT_SET`` is never set.

Every command is a ``str.format`` template: ``${{NAME}}`` reaches the guard as
``${NAME}``.

Each case differs from the unexpanded spelling: a guard that reads ``~`` or
``$NAME`` as an ordinary file name decides the other way.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
DESIGNER = support.TEST_DESIGNER
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID


def _variables(project, sandbox):
    """Variables the hook process holds, next to HOME, TMPDIR and CLAUDE_PROJECT_DIR."""
    return {
        "W1_02_GUARD_DIR": "src/gov/guard",
        "W1_02_UP": "../../..",
        "W1_02_ELSEWHERE": str(sandbox.elsewhere),
        "W1_02_ACCEPTANCE_DIR": str(project / "tests" / "acceptance" / WBS),
    }


# The target, once expanded, is inside the engineer's paths or the scratch set.
RESOLVES_INSIDE = {
    "project-variable": "echo changed > $CLAUDE_PROJECT_DIR/src/gov/guard/decide.py",
    "project-variable-in-braces": "echo changed > ${{CLAUDE_PROJECT_DIR}}/src/gov/guard/decide.py",
    "project-variable-in-double-quotes": 'echo changed > "$CLAUDE_PROJECT_DIR/src/gov/guard/decide.py"',
    "project-variable-append": "echo changed >> $CLAUDE_PROJECT_DIR/src/gov/guard/decide.py",
    "project-variable-tee": "printf changed | tee $CLAUDE_PROJECT_DIR/src/gov/guard/decide.py",
    "project-variable-sed-in-place": "sed -i s/1/2/ $CLAUDE_PROJECT_DIR/src/gov/guard/decide.py",
    "project-variable-rm": "rm $CLAUDE_PROJECT_DIR/src/gov/guard/decide.py",
    "project-variable-mkdir": "mkdir -p $CLAUDE_PROJECT_DIR/src/gov/guard/new_package",
    "directory-variable-touch": "touch $W1_02_GUARD_DIR/new_module.py",
    "directory-variable-mv": "mv $W1_02_GUARD_DIR/decide.py $W1_02_GUARD_DIR/renamed.py",
    "directory-variable-cp": "cp README.md $W1_02_GUARD_DIR/copy.md",
    "cd-to-a-variable": "cd $CLAUDE_PROJECT_DIR/src/gov/guard && echo changed > decide.py",
    "scratch-variable": "echo changed >> $TMPDIR/w1-02.log",
    "scratch-variable-in-braces": "echo changed > ${{TMPDIR}}/w1-02.log",
}

# The target, once expanded, is outside the engineer's paths. Spelled so that
# the unexpanded text looks like a path inside ``src/gov/guard``.
RESOLVES_OUTSIDE = {
    "tilde": "cd src/gov/guard && echo changed > ~/notes.py",
    "tilde-alone": "cd src/gov/guard && cp decide.py ~",
    "tilde-tee": "cd src/gov/guard && printf changed | tee ~/notes.py",
    "tilde-mkdir": "cd src/gov/guard && mkdir -p ~/new_package",
    "tilde-mv": "cd src/gov/guard && mv decide.py ~/decide.py",
    "tilde-user": "cd src/gov/guard && touch ~root/notes.py",
    "home-variable": "cd src/gov/guard && echo changed > $HOME/notes.py",
    "home-variable-in-braces": "cd src/gov/guard && echo changed > ${{HOME}}/notes.py",
    "home-variable-in-double-quotes": 'cd src/gov/guard && echo changed > "$HOME/notes.py"',
    "home-variable-cp": "cd src/gov/guard && cp decide.py $HOME/copy.py",
    "home-variable-sed-in-place": "cd src/gov/guard && sed -i s/1/2/ $HOME/notes.py",
    "variable-holds-an-outside-directory": "cd src/gov/guard && echo changed > $W1_02_ELSEWHERE/file.txt",
    "variable-holds-dot-dot": "echo changed > src/gov/guard/$W1_02_UP/README.md",
    "variable-holds-the-acceptance-tests": "cd src/gov/guard && echo changed > $W1_02_ACCEPTANCE_DIR/test_fixture.py",
    "cd-to-tilde": "cd src/gov/guard && cd ~ && echo changed > notes.py",
    "cd-to-the-home-variable": "cd src/gov/guard && cd $HOME && touch notes.py",
}

# The guard cannot know where the write lands.
UNRESOLVABLE = {
    "command-substitution": "cd src/gov/guard && echo changed > $(echo decide.py)",
    "command-substitution-in-a-name": "touch src/gov/guard/$(date +%s).py",
    "command-substitution-in-double-quotes": 'cd src/gov/guard && echo changed > "$(echo decide.py)"',
    "backticks": "cd src/gov/guard && echo changed > `echo decide.py`",
    "unset-variable": "echo changed > src/gov/guard/$W1_02_NOT_SET",
    "unset-variable-in-braces": "echo changed > src/gov/guard/${{W1_02_NOT_SET}}",
    "unset-variable-as-the-directory": "cd src/gov/guard && echo changed > $W1_02_NOT_SET/notes.py",
    "unset-variable-rm": "rm -r src/gov/guard/$W1_02_NOT_SET",
    "variable-set-inside-the-command": "cd src/gov/guard && D=../../.. && echo changed > $D/README.md",
    "variable-exported-inside-the-command": "export D=../../..; echo changed > src/gov/guard/$D/README.md",
    "glob-that-matches-nothing": "rm src/gov/guard/*.nomatch",
    "glob-that-matches-nothing-touch": "touch src/gov/guard/new_?.py",
}


def _run(bash, project, sandbox, command, role=ENGINEER, env=None):
    variables = _variables(project, sandbox)
    variables.update(env or {})
    return bash(project, command, role, TICKET, env=variables)


@pytest.mark.parametrize("form", sorted(RESOLVES_INSIDE), ids=sorted(RESOLVES_INSIDE))
def test_a_target_that_expands_into_the_engineer_s_paths_is_allowed(project, bash, sandbox, form):
    result = _run(bash, project, sandbox, RESOLVES_INSIDE[form])
    support.assert_allowed(result, f"Bash `{RESOLVES_INSIDE[form]}` by the engineer on {TICKET}")


@pytest.mark.parametrize("form", sorted(RESOLVES_OUTSIDE), ids=sorted(RESOLVES_OUTSIDE))
def test_a_target_that_expands_out_of_the_engineer_s_paths_is_denied(project, bash, sandbox, form):
    result = _run(bash, project, sandbox, RESOLVES_OUTSIDE[form])
    support.assert_denied(result, f"Bash `{RESOLVES_OUTSIDE[form]}` by the engineer on {TICKET}")


@pytest.mark.parametrize("form", sorted(UNRESOLVABLE), ids=sorted(UNRESOLVABLE))
def test_a_target_the_guard_cannot_resolve_is_denied(project, bash, sandbox, form):
    result = _run(bash, project, sandbox, UNRESOLVABLE[form])
    support.assert_denied(result, f"Bash `{UNRESOLVABLE[form]}` by the engineer on {TICKET}")


def test_tilde_follows_the_hook_s_own_home(project, bash, sandbox):
    """``~`` is ``HOME`` of the hook process, wherever that is."""
    command = "echo changed > ~/src/gov/guard/decide.py"
    result = _run(bash, project, sandbox, command, env={"HOME": str(project)})
    support.assert_allowed(result, f"Bash `{command}` with HOME set to the project")

    scratch_home = sandbox.tmpdir / "home"
    scratch_home.mkdir()
    command = "echo changed > ~/note.txt"
    result = _run(bash, project, sandbox, command, env={"HOME": str(scratch_home)})
    support.assert_allowed(result, f"Bash `{command}` with HOME inside the scratch directory")

    command = "cd src/gov/guard && echo changed > ~/README.md"
    result = _run(bash, project, sandbox, command, env={"HOME": str(project)})
    support.assert_denied(result, f"Bash `{command}` with HOME set to the project")


def test_a_glob_is_judged_by_what_it_expands_to(project, bash, sandbox):
    """A glob the guard can expand is judged by its matches; one it cannot expand is denied."""
    command = "rm src/gov/guard/*.py"
    result = _run(bash, project, sandbox, command)
    support.assert_allowed(result, f"Bash `{command}` (matches only src/gov/guard/decide.py)")

    # docs_link and acceptance_link are committed links out of the engineer's directory.
    command = "rm src/gov/guard/*/notes.md"
    result = _run(bash, project, sandbox, command)
    support.assert_denied(result, f"Bash `{command}` (matches docs/notes.md through docs_link)")

    command = f"sed -i s/1/2/ src/gov/guard/*/{WBS}/test_fixture.py"
    result = _run(bash, project, sandbox, command)
    support.assert_denied(result, f"Bash `{command}` (matches an acceptance test through acceptance_link)")

    command = "rm src/gov/guard/*.nomatch"
    result = _run(bash, project, sandbox, command)
    support.assert_denied(result, f"Bash `{command}` (matches nothing)")


def test_the_test_designer_s_targets_are_resolved_too(project, bash, sandbox):
    command = f"echo changed > $CLAUDE_PROJECT_DIR/tests/acceptance/{WBS}/test_added.py"
    result = _run(bash, project, sandbox, command, role=DESIGNER)
    support.assert_allowed(result, f"Bash `{command}` by the test designer")

    command = f"cd tests/acceptance/{WBS} && echo changed > ~/test_added.py"
    result = _run(bash, project, sandbox, command, role=DESIGNER)
    support.assert_denied(result, f"Bash `{command}` by the test designer")

    command = f"cd tests/acceptance/{WBS} && echo changed > $W1_02_NOT_SET/test_added.py"
    result = _run(bash, project, sandbox, command, role=DESIGNER)
    support.assert_denied(result, f"Bash `{command}` by the test designer")


def test_resolving_a_target_runs_nothing(project, bash, sandbox):
    """The guard resolves a target by reading the command, never by running part of it."""
    marker = project / "src" / "gov" / "guard" / "ran_by_the_guard.py"
    command = "cd src/gov/guard && echo changed > $(touch ran_by_the_guard.py; echo decide.py)"
    result = _run(bash, project, sandbox, command)
    support.assert_denied(result, f"Bash `{command}` by the engineer on {TICKET}")
    assert not marker.exists(), "the guard ran the command substitution: ran_by_the_guard.py was created"

    for command in (list(RESOLVES_INSIDE.values()) + list(RESOLVES_OUTSIDE.values())
                    + list(UNRESOLVABLE.values())):
        _run(bash, project, sandbox, command)
    assert support.porcelain(project) == "", (
        "git status --porcelain changed after the guard's decisions:\n" + support.porcelain(project)
    )
    assert list(sandbox.home.iterdir()) == [], "the guard wrote into HOME while deciding"
    assert list(sandbox.elsewhere.iterdir()) == [], "the guard wrote outside the project while deciding"
