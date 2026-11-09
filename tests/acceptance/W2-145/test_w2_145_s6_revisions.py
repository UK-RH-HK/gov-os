"""S6 and failure lines 4 and 5, from git: the tests that assumed a private fallback were revised by an independent
test designer with their Rewrite-Reason, never by the engineer; the engineer's commits stay in the ticket's paths
(DEC-1048 (5), DEC-1046 (1), DEC-1033 (3)).

The commits read are those after the one that filed W2-145 (``f916c5766f7f``) on the branch under test. S6's
"gov accept W2-145, W2-112, W2-32, W1-19 and W2-137 all green outside the sandbox" is the runner's, on those
tickets' own folders; the revised cases themselves are listed, with their old and new premises, in this folder's
README.

- S6: each acceptance file S6 names was changed after the filing by a commit whose message carries
  ``Role: independent-test-designer`` and ``Rewrite-Reason: DEC-1048 (5)``.
- Failure line 4: no commit of this ticket (``Task: DAEO-2tfd``) by ``Role: engineer`` changes anything under
  ``tests/acceptance/``; and every commit after the filing that changes an S6 file names a Rewrite-Reason.
- Failure line 5: every commit of this ticket by ``Role: engineer`` changes only files in the ticket's
  ``allowed_paths`` (read from ``.tickets/DAEO-2tfd.md``): so not ``gov-reranker-gpu-slot.pth`` or its module, not
  the reranker environment, not a CTO tool. Until the engineer commits, these two hold vacuously.
"""

from __future__ import annotations

import fnmatch
import re

import pytest
import yaml

import w2_145_support as support
from w2_145_support import commits_since_filed, trailer


def _allowed_paths() -> list[str]:
    text = support.TICKET.read_text(encoding="utf-8")
    front = text.split("---", 2)[1]
    return [str(path).split("#", 1)[0].strip() for path in yaml.safe_load(front)["allowed_paths"]]


def _ours_by(commit: dict, role: str) -> bool:
    return "DAEO-2tfd" in trailer(commit["message"], "Task") and role in trailer(commit["message"], "Role")


@pytest.mark.parametrize("path", support.S6_FILES, ids=[path.rsplit("/", 1)[-1] for path in support.S6_FILES])
def test_s6_each_acceptance_file_that_assumed_a_private_was_revised_by_a_designer_with_its_rewrite_reason(path):
    commits = commits_since_filed(path)
    revised = [commit["hash"][:12] for commit in commits
               if "independent-test-designer" in trailer(commit["message"], "Role")
               and support.REWRITE_REASON in commit["message"]]
    assert revised, (f"{path} has no commit since W2-145 was filed by Role: independent-test-designer with "
                     f"{support.REWRITE_REASON!r} (commits touching it: {[c['hash'][:12] for c in commits]})")
    unreasoned = [commit["hash"][:12] for commit in commits if not trailer(commit["message"], "Rewrite-Reason")]
    assert unreasoned == [], f"{path} was changed since the filing by commits with no Rewrite-Reason: {unreasoned}"


def test_failure_4_no_acceptance_test_is_changed_by_the_engineer():
    changed = [(commit["hash"][:12], [f for f in commit["files"] if f.startswith("tests/acceptance/")])
               for commit in commits_since_filed("tests/acceptance") if _ours_by(commit, "engineer")]
    assert changed == [], f"commits of W2-145 by Role: engineer changed acceptance tests: {changed}"


def test_failure_5_the_engineers_commits_touch_only_the_tickets_allowed_paths():
    allowed = _allowed_paths()
    assert any(re.search(r"rerank\.py$", path) for path in allowed), f"the ticket's allowed_paths: {allowed}"
    outside = []
    for commit in commits_since_filed():
        if not _ours_by(commit, "engineer"):
            continue
        for path in commit["files"]:
            if not any(fnmatch.fnmatch(path, pattern) or path == pattern for pattern in allowed):
                outside.append(f"{commit['hash'][:12]}: {path}")
    assert outside == [], f"commits of W2-145 by Role: engineer changed files outside its allowed_paths: {outside}"
