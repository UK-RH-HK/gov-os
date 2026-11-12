"""F4: the ticket's branch changes nothing outside the ticket's ``allowed_paths``.

Verify (the ticket's line): ``git diff --name-only`` of the ticket's branch against its base lists only paths matched by the
ticket's ``allowed_paths``. The base is the merge base of ``HEAD`` and ``w2/integrate``; this folder (``tests/acceptance/W2-159/``)
is the test designer's path, not a change outside the ticket. Read-only: git is asked only ``merge-base`` and ``diff``.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess

import w2_159_support as support

TICKET = support.TREE / ".tickets" / "DAEO-6lid.md"
ACCEPTANCE = "tests/acceptance/W2-159/"
SAFE_PATH = "/usr/local/bin:/usr/bin:/bin"


def allowed_paths() -> list[str]:
    """The ticket's ``allowed_paths`` (the list in its front matter), without the comment after a path.

    Raises ``AssertionError`` naming the gap where the ticket cannot be read or has no such list."""
    assert TICKET.is_file(), f"the ticket {TICKET} cannot be read"
    lines = TICKET.read_text().splitlines()
    assert "allowed_paths:" in lines, f"{TICKET} has no `allowed_paths:` list"
    found = []
    for line in lines[lines.index("allowed_paths:") + 1:]:
        match = re.match(r"^- (\S+)", line)
        if not match:
            break
        found.append(match.group(1))
    return found


def test_f4_the_branch_changes_only_the_tickets_allowed_paths(tmp_path):
    """``git diff --name-only <merge-base of HEAD and w2/integrate>...HEAD`` lists only paths matched by the ticket's
    ``allowed_paths`` or under ``tests/acceptance/W2-159/``. It is green only when the branch is clean: a change to any
    other path (a ticket file, another module, another ticket's test) fails it, naming the path; a missing
    ``w2/integrate``, a failing git call or an empty ``allowed_paths`` fails it, naming the gap (never a pass or a skip)."""
    env = {"PATH": SAFE_PATH, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C",
           "HOME": str(tmp_path)}

    def git(*args):
        return subprocess.run(["git", "-C", str(support.TREE), *args], env=env, capture_output=True, text=True,
                              timeout=60)

    base = git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0 and base.stdout.strip(), f"w2/integrate does not resolve: {base.stderr}"
    diff = git("diff", "--name-only", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, f"git diff failed: {diff.stderr}"
    patterns = allowed_paths()
    assert patterns, f"no allowed_paths read from {TICKET}"
    outside = [path for path in diff.stdout.splitlines()
               if not path.startswith(ACCEPTANCE) and not any(fnmatch.fnmatch(path, pattern) for pattern in patterns)]
    assert not outside, f"changed paths not matched by the ticket's allowed_paths {patterns}: {outside}"
