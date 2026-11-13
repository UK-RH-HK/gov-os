"""S5: the interim guards, stated, none changed by this ticket: ``docs/changes/W2-145-evidence.md`` records (a), (b)
and (c) (DEC-1048 (1), DEC-1048 (5), DEC-1043 (2), DEC-1046 (1)).

Read loosely, as a document test: the words may vary. A *passage* is one paragraph, one list item (with its
continuation lines) or one table row. "The git diff of the ticket's commits touches no file outside allowed_paths,
nothing under the reranker environment, and no CTO tool" is the reviewer's (S5's own Verify); failure line 5's
check on the engineer's commits is ``test_w2_145_s6_revisions.py``.

- (a) ``gov-reranker-gpu-slot.pth`` (ACT-RERANK-GPU-SLOTS-1) stays as the machine-wide guard, and is retired only
  when old code fails closed by construction (DEC-1048 (1)).
- (b) ``tools/rerank_service_slot_hold.py --watch`` is needed only while a service started by code older than this
  ticket can run (``pin-bcea09060ebc``, window 4's ``c00d525f``, any worktree before this ticket's merge), and is
  retired by the CTO when the lift's re-pin and every live worktree carry this ticket; the steps: the watcher stopped
  by its pid through ``tools/proc.sh``, its ``RESTART-CLASSES`` entry and the dispatcher's slot-holder note removed,
  the lock folder's slots seen held by the service alone.
- (c) the cases revised under S6, each with its commit: every S6 file is named in a passage with a commit's hash
  (7 to 40 hex digits), the hash is a commit of this repository, its message carries ``Rewrite-Reason: DEC-1048
  (5)``, and it changed that file.
"""

from __future__ import annotations

import re
from functools import lru_cache

import pytest

import w2_145_support as support

EVIDENCE = support.REPO_ROOT / "docs" / "changes" / "W2-145-evidence.md"
HASH = re.compile(r"\b[0-9a-f]{7,40}\b")


@lru_cache(maxsize=1)
def _passages() -> tuple[str, ...]:
    if not EVIDENCE.is_file():
        pytest.fail(f"there is no {EVIDENCE.relative_to(support.REPO_ROOT)} (S5)", pytrace=False)
    out, current = [], []
    for line in EVIDENCE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        starts = stripped.startswith(("- ", "* ", "|", "#")) or re.match(r"^\(?[a-z0-9]{1,2}[.)]\s", stripped)
        if not stripped or starts:
            if current:
                out.append(" ".join(current))
            current = [stripped] if stripped else []
            if stripped.startswith(("|", "#")):
                out.append(stripped)
                current = []
            continue
        current.append(stripped)
    if current:
        out.append(" ".join(current))
    return tuple(passage for passage in out if passage)


def _any(*patterns: str) -> list[str]:
    """The passages holding every pattern (case aside)."""
    return [passage for passage in _passages() if all(re.search(p, passage, re.IGNORECASE) for p in patterns)]


def test_s5_a_the_interim_pth_stays_as_the_machine_wide_guard_until_old_code_fails_closed():
    assert _any(r"gov-reranker-gpu-slot\.pth"), "(a): gov-reranker-gpu-slot.pth is not named"
    assert _any(r"ACT-RERANK-GPU-SLOTS-1"), "(a): ACT-RERANK-GPU-SLOTS-1 is not named"
    assert _any(r"gpu-slot\.pth|gov_reranker_gpu_slot|ACT-RERANK-GPU-SLOTS-1|interim",
                r"machine-wide|whole machine|every reranker|machine wide",
                r"stays|remains|kept|keeps|unchanged|not (retired|removed|changed)"), \
        "(a): no passage says the .pth stays as the machine-wide guard"
    assert _any(r"retir", r"fails? closed|by construction"), \
        "(a): no passage ties the .pth's retirement to old code failing closed by construction"
    assert _any(r"DEC-1048 \(1\)"), "(a): DEC-1048 (1) is not cited"


def test_s5_b_the_ctos_watcher_is_needed_only_while_older_code_can_start_a_service_and_its_retirement_steps():
    assert _any(r"rerank_service_slot_hold\.py", r"--watch"), "(b): tools/rerank_service_slot_hold.py --watch"
    assert _any(r"rerank_service_slot_hold|watcher", r"older|before this ticket|old code|earlier",
                r"only|until|while"), "(b): no passage says the watcher is needed only while older code can run"
    for older in (r"pin-bcea09060ebc", r"c00d525f", r"worktree"):
        assert _any(older), f"(b): the older code {older!r} is not named"
    assert _any(r"retir", r"CTO", r"re-?pin", r"worktree"), \
        "(b): no passage says the CTO retires it when the lift's re-pin and every live worktree carry this ticket"
    assert _any(r"pid", r"proc\.sh"), "(b): the step 'stopped by its pid through tools/proc.sh' is missing"
    assert _any(r"RESTART-CLASSES"), "(b): the step removing its RESTART-CLASSES entry is missing"
    assert _any(r"dispatcher", r"slot"), "(b): the step removing the dispatcher's slot-holder note is missing"
    assert _any(r"lock", r"slot", r"service alone|only the service|service only|by the service alone|"
                r"held by the service"), \
        "(b): the step seeing the lock folder's slots held by the service alone is missing"


@pytest.mark.parametrize("path", support.S6_FILES, ids=[path.rsplit("/", 1)[-1] for path in support.S6_FILES])
def test_s5_c_each_case_revised_under_s6_is_recorded_with_its_commit(path):
    name = path.rsplit("/", 1)[-1]
    passages = [passage for passage in _passages() if name in passage and HASH.search(passage)]
    assert passages, f"(c): {name} is not named beside a commit's hash"
    problems = []
    for passage in passages:
        for found in HASH.findall(passage):
            try:
                commit = support.run_git("rev-parse", "--verify", "--quiet", f"{found}^{{commit}}").strip()
            except AssertionError:
                continue  # a word of hex digits that is no commit
            message = support.run_git("show", "-s", "--format=%B", commit)
            files = support.run_git("show", "--format=", "--name-only", commit).split()
            if support.REWRITE_REASON in message and path in files:
                return
            problems.append(f"{found}: Rewrite-Reason {'present' if support.REWRITE_REASON in message else 'absent'},"
                            f" {path} {'changed' if path in files else 'not changed'}")
    pytest.fail(f"(c): no commit named beside {name} carries {support.REWRITE_REASON!r} and changed it: {problems}",
                pytrace=False)
