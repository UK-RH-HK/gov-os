"""W2-116 S3 (widened, DEC-1087 (3)) and F1: ``gov launch`` points every worker session's retrieval at the
integration store, so a plain search from a worktree with no store answers from it; a designer's retrieval never
reads a ticket worktree's store (README). The store here is hand-built as the CTO's script builds it today
(``support.hand_built_store``), so these cases do not wait on S1's command."""

from __future__ import annotations

import pytest

import w2_116_support as support
from w2_116_support import ENGINEER_TICKET, ENGINEERS, ENGINEERS_WORD, KEPT, KEPT_WORD, PRODUCT_SPEC_TICKET

ROLES = {"engineer": ENGINEER_TICKET, "independent-test-designer": ENGINEER_TICKET,
         "independent-auditor": ENGINEER_TICKET, "product-spec": PRODUCT_SPEC_TICKET}


@pytest.mark.parametrize("role", sorted(ROLES))
def test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none(box, env, project, role):
    support.hand_built_store(box, project, env)
    worktree = support.worktree(project, box.base / "worktrees" / "W2-901", branch="w2/W2-901")
    assert not (worktree / support.STORE_REL).exists()
    session = support.launch_and_search(box, env, worktree, role, ROLES[role], KEPT_WORD)
    assert session.launch.returncode == 0, f"gov launch {role} did not run its session\n{session.describe()}"
    run = session.search
    assert run.error_code != "STORE_MISSING", (
        f"the {role} session's search answered STORE_MISSING: its retrieval is not pointed at the integration "
        f"store\n{session.describe()}")
    support.assert_answers(run, KEPT_WORD, KEPT, f"the {role} session's search from a worktree with no store")


def test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store(box, env, project):
    half = support.hand_built_store(box, project, env)
    worktree = support.worktree(project, box.base / "worktrees" / "W2-901", branch="w2/W2-901")
    support.write(worktree / ENGINEERS, support.note(ENGINEERS_WORD))   # the engineer's work, on the ticket branch
    support.git(worktree, "add", "-A")
    support.git(worktree, "commit", "-q", "-m", "the engineer's new note")
    built = support.rebuild(worktree, env)
    assert built.ok, f"the ticket worktree's own store was not built\n{built.describe()}"
    premise = support.search(worktree, env, ENGINEERS_WORD)
    assert ENGINEERS in support.evidence_paths(premise), (
        f"premise: the ticket worktree's own store does not hold the engineer's note\n{premise.describe()}")
    assert not (half / ENGINEERS).exists(), "premise: the integration store's half holds the engineer's note"

    session = support.launch_and_search(box, env, worktree, "independent-test-designer", ENGINEER_TICKET,
                                        ENGINEERS_WORD)
    assert session.launch.returncode == 0, f"gov launch did not run the designer's session\n{session.describe()}"
    run = session.search
    assert run.ok, f"the designer's search did not answer\n{session.describe()}"
    support.assert_not_answered_with(run, ENGINEERS, "the designer's search in the ticket worktree")
    paths = support.evidence_paths(run)
    assert paths and all((half / path).is_file() for path in paths), (
        f"the designer's search was not answered from the integration store: {paths}")
    support.assert_facets_available(run, "the designer's search in the ticket worktree")


def test_s3_guard_the_launched_session_keeps_its_role_and_ticket(box, env, project):
    support.hand_built_store(box, project, env)
    worktree = support.worktree(project, box.base / "worktrees" / "W2-901", branch="w2/W2-901")
    session = support.launch_and_search(box, env, worktree, "independent-test-designer", ENGINEER_TICKET, KEPT_WORD)
    assert session.launch.returncode == 0 and session.record is not None, session.describe()
    block = session.record["env_block"]
    assert block.get("GOV_ROLE") == "independent-test-designer" and block.get("GOV_TICKET") == ENGINEER_TICKET, block
    assert session.record["cwd"] == str(worktree.resolve()), session.record["cwd"]
