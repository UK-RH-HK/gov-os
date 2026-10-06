"""W1-50 — a move of very many large merge commits is judged, never passed over in silence.

Added after implementation; reason: review finding, DEC-410.

DEC-410 (DP-28) bounds one merge commit: the helper refuses a merge commit with more than 24 distinct parents,
so one merge commit cannot stop the post-command hook. A review found that nothing bounds the move as a whole.
The behaviour came to the test designer as a described behaviour, never as code. These cases are the twin of
the ninth batch's cases about one merge commit with very many parents
(``test_w1_50_review_of_the_symmetric_rule.py``).

**The move.** In an orchestrator session's own call a chain of 95 merge commits is made with
``git commit-tree`` and ``main`` is moved to its tip. Each merge commit has 24 parents, the most the helper
reads: the merge commit before it and 23 side commits on 23 different fork points, each with the orchestrator's
trailers and changing nothing. One merge commit of the chain holds the tree from before a test designer's
change under ``tests/acceptance/**``: by the words of DEC-403 that path is its own change. As reviewed, the
post-command hook does not end within the harness's time limit for that move, it is stopped, no finding is
recorded, and the test stays undone: the check fails open.

- *Through the check.* The hook ends by itself within the harness's limit, as the suite's support applies it
  (``HOOK_TIMEOUT_S`` of the W1-03 support module; it is not raised here), and this call adds a finding. Either
  form of finding is accepted: one that names the undone test's path, or one for the move as a whole, as the
  check records a move it cannot read. Nothing else in the move could be a finding: the side commits carry the
  orchestrator's trailers and change nothing, and every other merge commit holds, where it differs from a
  parent, what its first parent brought, or differs from none.
- *The other side.* A large ordinary integration is silent: 60 two-parent ``--no-ff`` merges in one call, each
  bringing one commit inside its own trailers' paths; and three ordinary octopus merges of eight branches
  each. A fix that flags a move for the number of its merge commits, or of its commits, fails these.

**Not pinned:** a number of merge commits or of git processes at which anything changes, how the work is
bounded or the time is kept, which form the finding has, its ``action``, and what the check does to the move
beyond recording it.
"""

from __future__ import annotations

import pytest

import w1_50_many_merges_support as many
import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS


# --------------------------------------------------------------------------
# Through the check: the chain of merge commits with 24 parents each
# --------------------------------------------------------------------------

# name: (the merge commits' trailers, the number of the dropping merge commit counted from the oldest).
# Neither the orchestrator's trailers nor the caller allow a path under tests/acceptance/**; with none the
# caller decides, and the caller is the orchestrator. The order in which the check reads a move is not known
# to the tests: one case has the dropping merge commit near the oldest end, the other near the newest.
CHAINS = {
    "orchestrator-trailers-dropped-near-the-newest": (AS_ORCHESTRATOR, many.VERY_MANY_MERGES - 2),
    "no-trailers-dropped-near-the-oldest": (NO_TRAILERS, 3),
}


@pytest.mark.parametrize("case", sorted(CHAINS), ids=sorted(CHAINS))
def test_a_move_of_very_many_merge_commits_with_24_parents_that_undoes_a_test_is_a_finding_within_the_hook_s_limit(
        project, sandbox, call, case):
    """Review finding, DEC-410. In the orchestrator's own call ``main`` is moved along a chain of merge commits
    with 24 parents each; one of them holds the tree from before a test designer's change of an acceptance
    test. The post-command hook ends by itself within the harness's limit and the call adds a finding: one that
    names the undone test, or one for the move as a whole. Which of the two is not pinned."""
    trailers, dropping = CHAINS[case]
    shape = many.chain_of_merge_commits_with_24_parents(project, sandbox, trailers, dropping)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, _ = call(project, shape.command, ORCHESTRATOR, TICKET)
    many.assert_chain(project, shape, before)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    assert result.returncode is not None, (
        f"{what}: the post-command hook did not end within the harness's limit of "
        f"{check_support.HOOK_TIMEOUT_S:g} s and was stopped; the findings it added until then: "
        f"{list(result.new_lines)}. A hook that is stopped judges nothing: the test stays undone, unseen"
    )
    findings = check_support.new_findings(result, what)
    assert findings, (
        f"{what}: the hook ended after {result.seconds:.1f} s and no finding was added to "
        f"{check_support.FINDINGS_REL}, neither one that names {shape.undone} nor one for the move as a whole: "
        f"{result.describe()}"
    )


# --------------------------------------------------------------------------
# The other side: large ordinary integrations stay silent
# --------------------------------------------------------------------------

def _assert_a_silent_integration(project, shape, before, result, left):
    many.assert_ordinary_merges(project, shape, before)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    assert result.returncode is not None, (
        f"{what}: the post-command hook did not end within the harness's limit of "
        f"{check_support.HOOK_TIMEOUT_S:g} s and was stopped"
    )
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_an_ordinary_move_of_sixty_two_parent_merges_of_commits_inside_their_own_paths_is_silent(project, sandbox,
                                                                                               call):
    """60 ``git merge --no-ff`` in the orchestrator's own call, one branch each. Every branch has one commit,
    a new file inside the allowed paths of its own trailers; twenty are a test designer's new acceptance
    tests, each another file. No merge commit has an own change: the check is silent, and nothing is moved."""
    shape = many.sixty_two_parent_merges(project, sandbox)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    tests = [brought.path for group in shape.groups for brought in group if brought.trailers == many.AS_DESIGNER]
    assert len(tests) == many.SIXTY // 3 and all(check_support.read(project, path) for path in tests), (
        f"the fixture is wrong: the merges did not bring in the test designer's {len(tests)} acceptance tests"
    )
    _assert_a_silent_integration(project, shape, before, result, left)


def test_an_ordinary_move_of_three_octopus_merges_of_eight_branches_each_is_silent(project, sandbox, call):
    """Three ``git merge`` of eight branches each in the orchestrator's own call: three merge commits with nine
    parents. Every branch has one commit inside the allowed paths of its own trailers; eight are a test
    designer's new acceptance tests. No merge commit has an own change: the check is silent."""
    shape = many.three_octopus_merges_of_eight(project, sandbox)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    assert [len(support.parents_of(project, revision)) for revision in ("HEAD", "HEAD~1", "HEAD~2")] == [
        many.BRANCHES_IN_AN_OCTOPUS + 1] * many.OCTOPUSES, "the fixture is wrong: not three merge commits of nine"
    _assert_a_silent_integration(project, shape, before, result, left)
