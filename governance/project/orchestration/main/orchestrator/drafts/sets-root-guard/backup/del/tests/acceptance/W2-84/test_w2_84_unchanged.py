"""W2-84 -- nothing else changes.

KPI success 5: "Nothing else changes: (a) secrets, (b) the held-out material and
(c) the counterpart's work are judged exactly as before; a set's visible part
stays readable; a session that no set measures sees no new refusal and runs no
new git call; ... [DEC-820, DEC-873, DEC-880, DEC-866]". (The hook's latency
case, W1-05, and the earlier tickets' suites are their own tests; the README
names them.)
KPI failure 4: "Any of (a) to (c) weakened, or a refusal added for a session that
no set measures."

These cases are green before the fix and must stay green after it.

- The unmeasured sessions: an orchestrator (a ticket lead on the engineer's
  ticket) and an independent auditor, which no set measures; and a research
  session on a ticket no set measures.
- (a) a stand-in ``.env`` in every tree; (b) W2-58's form of stand-in held-out
  material under the temporary HOME, named by the planted held-out list, never
  the real material; (c) the engineer's own acceptance tests,
  ``tests/acceptance/W2-81/``, in the tree it runs in.
- "No new git call" is shown by behaviour: a ``git`` first on ``PATH`` records
  every call it gets, then passes it to the real git.
"""

from __future__ import annotations

import pytest
import yaml

import w2_84_support as s

UNMEASURED = {"orchestrator": (s.ORCHESTRATOR, s.ENG), "auditor": (s.AUDITOR, s.ENG),
              "research-free-ticket": (s.RESEARCH, s.FREE_TK)}


def _unmeasured_reads(world, tree):
    return [
        s.read(tree / s.HIDDEN_FILE),
        s.bash(f"cat {s.q(tree / s.HIDDEN_EXTRA)}"),
        s.grep(tree / s.HIDDEN_FOLDER, pattern="q1"),
        s.bash(f"git -C {s.q(tree)} grep -n {s.HIDDEN_WORD}"),
    ]


@pytest.mark.parametrize("target", s.TREE_NAMES)
@pytest.mark.parametrize("who", sorted(UNMEASURED))
def test_a_session_no_set_measures_reads_every_tree_s_hidden_part(world, who, target):
    role, ticket = UNMEASURED[who]
    for session in (s.MAIN, s.WT_OWN):
        for call in _unmeasured_reads(world, world.tree(target)):
            result = world.ask(call, role, ticket, world.tree(session))
            s.assert_allowed(result, call, f"{who} rooted in the {session}: ")


@pytest.mark.parametrize("who", sorted(UNMEASURED))
def test_a_session_no_set_measures_searches_from_above_every_tree(world, who):
    role, ticket = UNMEASURED[who]
    for start in (world.sandbox.home, world.sandbox.runs, world.sandbox.worktrees_parent):
        call = s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(start)}")
        s.assert_allowed(world.ask(call, role, ticket, world.tree(s.WT_OWN)), call, f"{who}: ")


def test_a_session_no_set_measures_reads_the_store_s_hidden_revision(store):
    hidden = store.revs["hidden"]
    for call in (s.bash(f"git show {hidden}"), s.bash("git log -p --all"), s.bash(f"git grep -n {s.HIDDEN_WORD} {hidden}"),
                 s.bash(f"git cat-file -p {hidden}:{s.HIDDEN_FILE}")):
        for role in (s.ORCHESTRATOR, s.AUDITOR):
            s.assert_allowed(store.ask(call, role, s.ENG, store.tree(s.STORE_WT)), call, f"{role}: ")


# --------------------------------------------------------------------------
# The visible part stays readable to the measured session
# --------------------------------------------------------------------------

@pytest.mark.parametrize("target", s.TREE_NAMES)
@pytest.mark.parametrize("session", s.SESSION_ROOTS)
def test_the_visible_part_stays_readable_to_the_measured_session(world, session, target):
    tree = world.tree(target)
    for call in (s.read(tree / s.VISIBLE_FILE), s.bash(f"cat {s.q(tree / s.VISIBLE_FILE)}"),
                 s.bash(f"grep -rn {s.WORD} {s.q(tree / s.VISIBLE_FOLDER)}"), s.read(tree / "README.md")):
        result = world.ask(call, s.ENGINEER, s.ENG, world.tree(session))
        s.assert_allowed(result, call, f"engineer rooted in the {session}, the {target}: ")


# --------------------------------------------------------------------------
# (a), (b) and (c) as before
# --------------------------------------------------------------------------

ROLES = {"engineer": (s.ENGINEER, s.ENG), "orchestrator": (s.ORCHESTRATOR, s.ENG), "auditor": (s.AUDITOR, s.ENG)}


@pytest.mark.parametrize("who", sorted(ROLES))
def test_a_secret_stays_refused_in_every_tree(world, who):
    role, ticket = ROLES[who]
    for target in (s.MAIN, s.WT_OTHER, s.CLONE):
        path = world.tree(target) / s.SECRET_REL
        for call in (s.read(path), s.bash(f"cat {s.q(path)}")):
            result = world.ask(call, role, ticket, world.tree(s.WT_OWN))
            s.assert_refused(result, call, f"{who}: ")


@pytest.mark.parametrize("who", sorted(ROLES))
def test_the_held_out_names_stay_readable_and_their_contents_refused(world, who):
    role, ticket = ROLES[who]
    root = world.tree(s.WT_OWN)
    held_rel, _ = s.held_out_list()
    s.assert_allowed(world.ask(s.read(root / held_rel), role, ticket, root), "Read of the held-out list", f"{who}: ")
    sample = world.sandbox.held_out / s.HELD_SAMPLE
    for call in (s.read(sample), s.bash(f"cat {s.q(sample)}"), s.bash(f"grep -rn {s.HELD_WORD} {s.q(world.sandbox.held_out)}")):
        s.assert_refused(world.ask(call, role, ticket, root), call, f"{who}: ")


@pytest.mark.parametrize("session", (s.MAIN, s.WT_OWN))
def test_the_engineer_s_own_acceptance_tests_stay_refused_and_runnable(world, session):
    root = world.tree(session)
    for call in (s.read(root / s.OWN_TEST_REL), s.bash(f"cat {s.OWN_TEST_REL}")):
        s.assert_refused(world.ask(call, s.ENGINEER, s.ENG, root), call, f"engineer rooted in the {session}: ")
    run = s.bash(f"python3 -m pytest {s.ENG.acceptance} -q")
    s.assert_allowed(world.ask(run, s.ENGINEER, s.ENG, root), run, f"engineer rooted in the {session}: ")


# --------------------------------------------------------------------------
# No new git call for a session no set measures; at most one listing for a measured one
# --------------------------------------------------------------------------

def _recorded(world, stand_in, role, ticket, calls):
    """The git calls the guard runs for each call, in order, through the recording stand-in."""
    out = []
    for call in calls:
        stand_in.clear()
        result = world.ask(call, role, ticket, world.tree(s.MAIN), path_first=stand_in.folder)
        s.assert_allowed(result, call, f"{role}: ")
        out.append(stand_in.calls())
    return out


@pytest.mark.parametrize("who", ("orchestrator", "auditor"))
def test_a_session_no_set_measures_runs_no_new_git_call(fresh_world, who):
    """No ``git worktree`` call, and no other git call than those the guard runs for the same calls when the path
    map declares no evaluation set at all (the baseline: the same project with the block taken out)."""
    world = fresh_world
    role, ticket = UNMEASURED[who]
    stand_in = s.install_git_stand_in(world.sandbox, "record", "recording-git")
    other = world.tree(s.WT_OTHER)
    calls = [s.read(other / s.HIDDEN_FILE), s.grep(other / s.HIDDEN_FOLDER, pattern="q1"),
             s.glob_call(f"{s.HIDDEN_FOLDER}/*", other), s.bash(f"cat {s.q(other / s.HIDDEN_FILE)}"),
             s.bash(f"grep -rn {s.HIDDEN_WORD} {s.q(world.sandbox.home)}")]
    with_set = _recorded(world, stand_in, role, ticket, calls)
    worktree = [c for calls_of_one in with_set for c in calls_of_one if "worktree" in c]
    assert not worktree, f"the guard listed the worktrees for a session no set measures: {worktree}"
    path_map = world.tree(s.MAIN) / s.PATH_MAP_REL
    document = yaml.safe_load(path_map.read_text(encoding="utf-8"))
    del document["evaluation_sets"]
    path_map.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    without_set = _recorded(world, stand_in, role, ticket, calls)
    for call, one, baseline in zip(calls, with_set, without_set):
        assert one == baseline, (f"{who}: {call} ran git calls it does not run without an evaluation set: "
                                 f"{one} against {baseline}")


@pytest.mark.parametrize("session", (s.MAIN, s.WT_OWN))
def test_a_measured_session_lists_the_worktrees_at_most_once_per_call(world, session):
    """The design note's item 6: one ``git worktree list`` per guard call at most, even when the session's role and
    its subagent's role are both measured."""
    stand_in = s.install_git_stand_in(world.sandbox, "record", f"recording-git-{session}")
    call = s.read(world.tree(s.WT_OTHER) / s.HIDDEN_FILE)
    for agent_type in (None, s.ENGINEER):
        stand_in.clear()
        world.ask(call, s.ENGINEER, s.ENG, world.tree(session), path_first=stand_in.folder, agent_type=agent_type)
        assert len(stand_in.worktree_calls()) <= 1, (
            f"one guard call listed the worktrees {len(stand_in.worktree_calls())} times: {stand_in.worktree_calls()}")
