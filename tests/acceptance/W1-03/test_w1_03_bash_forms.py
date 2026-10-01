"""W1-03 — the check catches the Bash writes the guard cannot see.

KPI success 1 and KPI failure 1. CAP-58 acceptance: "a Bash form the guard
cannot parse is caught by the post-command containment check". DEC-099 leaves
shell aliases and functions to this check; DEC-111 and DEC-115 leave every form
the guard does not judge, and DEC-110 leaves the case of a guard that timed out.

The check does not read the command. It looks at what the call left behind, so
each form is run for real and must then be reported. None of these commands
holds a plain ``> file``, ``touch``, ``rm``, ``mv``, ``cp``, ``mkdir`` or
``sed -i`` aimed at the path it changes.

This is the test designer's own list. KPI success 3 names "nine Bash write forms
from S0b2 I-06"; that list is not in the repository and is with the owner
(decision package of 2026-10-01, KD-2).

Every command is a ``str.format`` template: a literal brace is doubled.
"""

from __future__ import annotations

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE

# name: (command, path git status shows afterwards)
FORMS = {
    "interpreter-one-liner": (
        "python3 -c \"open('README.md', 'a').write('changed')\"", "README.md"),
    "interpreter-here-document": (
        "python3 - <<'PY'\nfrom pathlib import Path\nPath('docs/new.md').write_text('new')\nPY", "docs/new.md"),
    "nested-shell": ("bash -c 'echo changed >> README.md'", "README.md"),
    "nested-sh": ("sh -c \"echo changed >> README.md\"", "README.md"),
    "eval": ("eval \"echo changed >> README.md\"", "README.md"),
    "target-in-a-shell-variable": ("f=README.md; echo changed >> \"$f\"", "README.md"),
    "target-from-command-substitution": ("echo changed >> \"$(printf README.md)\"", "README.md"),
    "shell-function": ("w() {{ echo changed >> README.md; }}; w", "README.md"),
    "shell-alias": ("shopt -s expand_aliases\nalias w='tee -a README.md'\nprintf changed | w > /dev/null", "README.md"),
    "here-document-through-cat": ("cat > docs/new.md <<'EOF'\nnew\nEOF", "docs/new.md"),
    "dd": ("printf changed | dd of=README.md status=none", "README.md"),
    "truncate": ("truncate -s 0 README.md", "README.md"),
    "install": ("install -m 644 README.md docs/installed.md", "docs/installed.md"),
    "symbolic-link": ("ln -s ../README.md docs/link.md", "docs/link.md"),
    "find-delete": ("find docs -name notes.md -delete", "docs/notes.md"),
    "xargs": ("printf '%s\\n' docs/notes.md | xargs rm", "docs/notes.md"),
    "awk": ("awk 'BEGIN {{ print \"changed\" > \"README.md\" }}'", "README.md"),
    "sed-write-command": ("sed -n 'w docs/sed.md' README.md", "docs/sed.md"),
    "tar-extract": ("tar -cf - src/gov/guard/decide.py | tar -xf - -C docs", "docs/src/gov/guard/decide.py"),
    "git-mv": ("git mv README.md README.txt", "README.txt"),
    "git-rm": ("git rm -q docs/notes.md", "docs/notes.md"),
    "git-apply": (
        "git apply <<'EOF'\n--- a/README.md\n+++ b/README.md\n@@ -1 +1,2 @@\n # Fixture project\n+changed\nEOF",
        "README.md"),
    "interpreter-copy": (
        "python3 -c \"import shutil; shutil.copy('README.md', 'docs/copied.md')\"", "docs/copied.md"),
    "interpreter-rename": (
        "python3 -c \"import os; os.rename('docs/notes.md', 'docs/renamed.md')\"", "docs/renamed.md"),
}


@pytest.mark.parametrize("form", sorted(FORMS), ids=sorted(FORMS))
def test_a_write_the_guard_cannot_see_is_reported(project, after_bash, form):
    command, changed = FORMS[form]
    result = after_bash(project, command, ENGINEER, TICKET, changed=[changed])
    name = changed if not changed.startswith("docs/src/") else "docs/src"
    support.assert_reported(result, name, what=f"`{command}` by the engineer on {TICKET}")


# The same routes into the acceptance tests. name: command
INTO_ACCEPTANCE = {
    "interpreter-one-liner": f"python3 -c \"open('{ACCEPTANCE_FILE}', 'a').write('changed')\"",
    "nested-shell": f"bash -c 'echo changed >> {ACCEPTANCE_FILE}'",
    "target-in-a-shell-variable": f"f={ACCEPTANCE_FILE}; echo changed >> \"$f\"",
    "shell-function": f"w() {{{{ echo changed >> {ACCEPTANCE_FILE}; }}}}; w",
    "dd": f"printf changed | dd of={ACCEPTANCE_FILE} status=none",
    "truncate": f"truncate -s 0 {ACCEPTANCE_FILE}",
    "find-delete": "find tests/acceptance -name test_fixture.py -delete",
    "git-rm": f"git rm -q {ACCEPTANCE_FILE}",
    "git-mv": f"git mv {ACCEPTANCE_FILE} src/gov/guard/moved.py",
    "through-a-committed-link": (
        f"python3 -c \"open('src/gov/guard/acceptance_link/{support.TICKET_WBS_ID}/test_fixture.py', 'a')"
        ".write('changed')\""),
}


@pytest.mark.parametrize("form", sorted(INTO_ACCEPTANCE), ids=sorted(INTO_ACCEPTANCE))
def test_an_unseen_write_to_an_acceptance_test_is_reported_and_restored(project, after_bash, form):
    """KPI success 2, through the forms the guard cannot see."""
    command = INTO_ACCEPTANCE[form]
    result = after_bash(project, command, ENGINEER, TICKET, changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_reported(result, ACCEPTANCE_FILE, what=what)
    path = project / ACCEPTANCE_FILE
    assert path.is_file() and path.read_text(encoding="utf-8") == support.head_text(project, ACCEPTANCE_FILE), (
        f"{what}: {ACCEPTANCE_FILE} was not restored from HEAD"
    )
    assert support.porcelain(project, support.ACCEPTANCE_REL) == "", (
        f"{what}: tests/acceptance still differs from HEAD:\n" + support.porcelain(project, support.ACCEPTANCE_REL)
    )
