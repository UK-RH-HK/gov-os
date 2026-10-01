"""W1-02 — Bash writes follow the same allow-list as Edit and Write.

KPI success 1 ("Edit/Write/Bash writes are allowed only inside the active ticket
allowed_paths …") and KPI failure 1 ("Any write outside allowed_paths is allowed").

The guard judges the plain write forms: ``>``, ``>>``, ``| tee``, ``touch``,
``rm``, ``mv``, ``cp``, ``mkdir -p`` and ``sed -i``, with relative targets, after
``cd … &&``, and with absolute targets. Every other form stays with W1-03 and is
not tested here (owner answer to KD-5).

The session is the engineer on DAEO-zz90, whose paths include ``src/gov/guard/**``.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID

INSIDE = {
    "redirect": "echo changed > src/gov/guard/decide.py",
    "redirect-new-file": "echo changed > src/gov/guard/new_module.py",
    "append": "echo changed >> src/gov/guard/decide.py",
    "tee": "printf changed | tee src/gov/guard/decide.py",
    "touch": "touch src/gov/guard/new_module.py",
    "rm": "rm src/gov/guard/decide.py",
    "mv-within": "mv src/gov/guard/decide.py src/gov/guard/renamed.py",
    "cp-from-outside-into": "cp README.md src/gov/guard/copy.md",
    "mkdir": "mkdir -p src/gov/guard/new_package",
    "sed-in-place": "sed -i s/1/2/ src/gov/guard/decide.py",
    "cd-then-redirect": "cd src/gov/guard && echo changed > decide.py",
    "redirect-absolute-path": "echo changed > {root}/src/gov/guard/decide.py",
    "two-writes-both-inside": "echo one > src/gov/guard/one.py && echo two > tests/unit/guard/test_two.py",
}

OUTSIDE = {
    "redirect": "echo changed > README.md",
    "redirect-new-file": "echo changed > docs/new.md",
    "append": "echo changed >> docs/notes.md",
    "tee": "printf changed | tee docs/notes.md",
    "touch": "touch docs/new.md",
    "rm": "rm README.md",
    "rm-recursive-above-the-allowed-directory": "rm -r src",
    "mv-out": "mv src/gov/guard/decide.py docs/decide.py",
    "mv-in-removes-an-outside-file": "mv README.md src/gov/guard/README.md",
    "cp-out": "cp src/gov/guard/decide.py docs/copy.py",
    "mkdir": "mkdir -p docs/new_dir",
    "sed-in-place": "sed -i s/a/b/ README.md",
    "cd-then-redirect": "cd docs && echo changed > notes.md",
    "redirect-absolute-path": "echo changed > {root}/README.md",
    "redirect-through-dot-dot": "echo changed > src/gov/guard/../../../README.md",
    "inside-then-outside": "echo ok > src/gov/guard/decide.py && echo bad > README.md",
    "outside-then-inside": "echo bad > README.md; echo ok > src/gov/guard/decide.py",
    "ticket-file": "echo changed >> .tickets/" + TICKET + ".md",
    "freeze-flag": "rm " + support.FREEZE_FLAG_REL,
    "outside-the-repository": "echo changed > {elsewhere}/file.txt",
}

ACCEPTANCE = {
    "redirect": f"echo changed > tests/acceptance/{WBS}/test_fixture.py",
    "append": f"echo changed >> tests/acceptance/{WBS}/test_fixture.py",
    "tee": f"printf changed | tee tests/acceptance/{WBS}/test_fixture.py",
    "touch": f"touch tests/acceptance/{WBS}/test_added.py",
    "rm": f"rm tests/acceptance/{WBS}/test_fixture.py",
    "mv-out-of": f"mv tests/acceptance/{WBS}/test_fixture.py src/gov/guard/moved.py",
    "mv-into": f"mv src/gov/guard/decide.py tests/acceptance/{WBS}/test_moved.py",
    "cp-into": f"cp src/gov/guard/decide.py tests/acceptance/{WBS}/test_copy.py",
    "mkdir": "mkdir -p tests/acceptance/W1-77",
    "sed-in-place": f"sed -i s/1/2/ tests/acceptance/{WBS}/test_fixture.py",
    "cd-then-redirect": f"cd tests/acceptance/{WBS} && echo changed > test_fixture.py",
    "redirect-absolute-path": "echo changed > {root}/tests/acceptance/" + WBS + "/test_fixture.py",
}

READS = {
    "ls": "ls -la",
    "cat": "cat README.md",
    "cat-acceptance-test": f"cat tests/acceptance/{WBS}/test_fixture.py",
    "git-status": "git status --porcelain",
}


@pytest.mark.parametrize("form", sorted(INSIDE), ids=sorted(INSIDE))
def test_engineer_bash_write_inside_the_ticket_paths_is_allowed(project, bash, form):
    result = bash(project, INSIDE[form], ENGINEER, TICKET)
    support.assert_allowed(result, f"Bash `{INSIDE[form]}` by the engineer on {TICKET}")


@pytest.mark.parametrize("form", sorted(OUTSIDE), ids=sorted(OUTSIDE))
def test_engineer_bash_write_outside_the_ticket_paths_is_denied(project, bash, sandbox, form):
    result = bash(project, OUTSIDE[form], ENGINEER, TICKET, elsewhere=sandbox.elsewhere)
    support.assert_denied(result, f"Bash `{OUTSIDE[form]}` by the engineer on {TICKET}")


@pytest.mark.parametrize("form", sorted(ACCEPTANCE), ids=sorted(ACCEPTANCE))
def test_engineer_bash_write_under_acceptance_tests_is_denied(project, bash, form):
    result = bash(project, ACCEPTANCE[form], ENGINEER, TICKET)
    support.assert_denied(result, f"Bash `{ACCEPTANCE[form]}` by the engineer on {TICKET}")


@pytest.mark.parametrize("form", sorted(READS), ids=sorted(READS))
def test_engineer_bash_read_is_let_through(project, bash, form):
    result = bash(project, READS[form], ENGINEER, TICKET)
    support.assert_allowed(result, f"Bash `{READS[form]}` by the engineer on {TICKET}")


def test_bash_decisions_change_nothing_on_disk(project, bash):
    """The guard decides about the command; it does not run it."""
    for command in sorted(INSIDE.values()) + sorted(ACCEPTANCE.values()):
        bash(project, command, ENGINEER, TICKET)
    assert support.porcelain(project) == "", (
        "git status --porcelain changed after the guard's decisions:\n" + support.porcelain(project)
    )
