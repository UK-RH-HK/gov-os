"""KPI 5 (DEC-911 items 1 and 2): the rule's id and keywords are written only in parts in every tracked file this
ticket writes. Every file the branch adds or changes under ``src/gov/secrets/``, ``tests/unit/secrets_check/`` and
``tests/acceptance/W2-71/`` (against its merge base with ``w2/integrate``, the working tree included, untracked
files too) holds neither of row W2-L423's rule's keywords whole, in any case, in its content or its path. Without
``w2/integrate``, every file of the three folders is read.

A guard, green today: it must stay green, this suite's own files included.
"""

from __future__ import annotations

import subprocess

import w2_71_support as support

FOLDERS = ("src/gov/secrets", "tests/unit/secrets_check", "tests/acceptance/W2-71")


def _git(*args):
    done = subprocess.run(["git", "-C", str(support.REPO_ROOT), *args], capture_output=True, text=True, timeout=60)
    return done.returncode, done.stdout


def written_by_the_branch():
    code, base = _git("merge-base", "HEAD", "w2/integrate")
    if code == 0 and base.strip():
        _, tracked = _git("diff", "--name-only", "--diff-filter=d", base.strip(), "--", *FOLDERS)
    else:
        _, tracked = _git("ls-files", "--", *FOLDERS)
    _, untracked = _git("ls-files", "--others", "--exclude-standard", "--", *FOLDERS)
    return sorted(set(tracked.split()) | set(untracked.split()))


def test_premise_the_list_holds_this_suites_own_files():
    written = written_by_the_branch()
    own = "tests/acceptance/W2-71/test_w2_71_keywords_in_parts.py"
    assert own in written, "the files the branch writes do not include this suite's own: the list is not read right"


def test_no_file_the_branch_writes_holds_a_keyword_of_row_w2_l423s_rule_whole():
    offenders = []
    for rel in written_by_the_branch():
        path = support.REPO_ROOT / rel
        if path.is_symlink() or not path.is_file():
            continue
        text = path.read_bytes().decode("latin-1")
        if support.holds_keyword(text) or support.holds_keyword(rel):
            offenders.append(rel)
    clean = not offenders
    assert clean, support.say(f"files this ticket writes that hold a keyword whole: {offenders}")
