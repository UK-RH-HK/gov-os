"""W2-201 fix X2 (DEC-1219 (5)): a chore launches with no ticket.

``gov launch <role> --chore "<line>"`` on W2-184's fixture project and the stand-in CLI. ``gov launch`` itself is run
with a caller's ``GOV_TICKET`` in its environment (a lead launching a worker has one), so "absent" is shown against a
value that could leak: ``GOV_TICKET`` is in neither the ``--settings`` env block nor the CLI process's environment. The
record holds ``kind`` ``chore``, ``kind_line`` the line and ``ticket``, ``ticket_class``, ``criticality`` and ``rubric``
null; the model and effort are the role file's ``Launch default`` (W2-184's fixture: Sonnet, medium; every class of the
engineer's table says effort high), source ``role default``, though the project has a criticality file. No run folder
of its own is made. Another ticket's record in the folder is not read as the chore's. The refusal of another model
(S4) applies with no class to lift it; ``gov pause`` and the gate stop a chore.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_201_support as k
import w2_201_x_support as x

s, b = x.s, x.b
CALLER = {"GOV_TICKET": x.CALLER_TICKET}
NULL_KEYS = ("ticket", "ticket_class", "criticality", "rubric")


def _chore(sandbox, cli, role=x.ENGINEER, *more, extra_env=None):
    return x.launch(sandbox, cli, role, "--chore", x.CHORE_LINE, *more, extra_env={**CALLER, **(extra_env or {})})


@pytest.mark.parametrize("role", [x.ENGINEER, x.TEST_DESIGNER])
def test_x2_a_chore_starts_with_no_ticket_on_the_role_default(sandbox, project, cli, role):
    runs_before = x.runs_listing(sandbox)
    result = _chore(sandbox, cli, role)
    x.launched(result)
    model, effort = x.ROLE_DEFAULT
    x.assert_line(result, model, effort)
    got = x.record_of(result, "kind", "kind_line", *NULL_KEYS, "model", "model_source", "effort", "effort_source")
    want = {"kind": "chore", "kind_line": x.CHORE_LINE, **{key: None for key in NULL_KEYS}, "model": model,
            "model_source": "role default", "effort": effort, "effort_source": "role default"}
    assert got == want, f"the chore's launch record states {got}, not {want}"
    block, env = x.env_pair(result)
    assert "GOV_TICKET" not in block, f"the chore's --settings env block holds GOV_TICKET: {block.get('GOV_TICKET')!r}"
    assert "GOV_TICKET" not in env, f"the chore's CLI process environment holds GOV_TICKET: {env.get('GOV_TICKET')!r}"
    assert x.runs_listing(sandbox) == runs_before, (
        f"a chore made a run folder of its own: {x.runs_listing(sandbox)} (before: {runs_before})")
    k.quiet(result)


def test_x2_another_ticket_s_record_in_the_folder_is_not_read_as_the_chore_s(sandbox, project, cli):
    """An engineer's launch on a C3 ticket first (its record: Opus, by criticality); then the chore."""
    tk = s.ticket(project, x.ENGINEER, "C3")
    first = x.launch(sandbox, cli, x.ENGINEER, tk)
    x.launched(first)
    first_name = f"{first.session_id()}.json"
    first_text = first.after[first_name]
    result = _chore(sandbox, cli)
    x.launched(result)
    assert result.session_id() != first.session_id(), "the chore took the earlier launch's session id"
    model, effort = x.ROLE_DEFAULT
    got = x.record_of(result, "kind", "ticket", "criticality", "model", "model_source", "effort", "promotion",
                      "review_round")
    want = {"kind": "chore", "ticket": None, "criticality": None, "model": model, "model_source": "role default",
            "effort": effort, "promotion": None, "review_round": None}
    assert got == want, f"the chore's record states {got}, not {want} (the earlier record was {first_name})"
    assert result.after[first_name] == first_text, "the earlier ticket's record changed with the chore's launch"
    assert json.loads(first_text).get("ticket") == tk


def test_x2_an_exception_limited_to_c3_does_not_lift_a_chore_s_other_model(sandbox, project, cli):
    k.write_exceptions(project, {"exceptions": [{"subagent_type": x.ENGINEER, "model": "opus",
                                                 "decided": k.DECIDED, "class": "C3"}]})
    result = _chore(sandbox, cli, x.ENGINEER, "--", "--model", x.OPUS)
    s.refused(result, x.OPUS, k.EXCEPTIONS_REL)


def test_x2_a_chore_asking_another_model_with_no_exceptions_file_is_refused(sandbox, project, cli):
    s.refused(_chore(sandbox, cli, x.ENGINEER, "--", "--model", x.OPUS), x.OPUS, k.EXCEPTIONS_REL)


def test_x2_an_opus_exception_with_no_limiter_does_not_lift_a_chore_s_other_model(sandbox, project, cli):
    """Rewrite-Reason: DEC-1225: this case pinned "an entry without ``class`` is not limited by class (S4), so a chore
    may take it" and expected Opus with ``model_source`` ``exception``. R3: an entry that names Opus and carries no
    limiter (``class``, ``task``, ``decision``) lifts nothing, for a chore too."""
    k.write_exceptions(project, {"exceptions": [{"subagent_type": x.ENGINEER, "model": "opus",
                                                 "decided": k.DECIDED}]})
    result = _chore(sandbox, cli, x.ENGINEER, "--", "--model", x.OPUS)
    s.refused(result, x.OPUS, k.EXCEPTIONS_REL)


def test_x2_an_opus_exception_limited_by_decision_lifts_a_chore_s_other_model_when_the_launch_names_it(
        sandbox, project, cli):
    """Rewrite-Reason: DEC-1225: as above, the chore's exception is now one whose ``decision`` limiter the launch meets
    with ``--owner-named`` (a chore has no ticket and no class, so no other limiter can be met)."""
    k.write_exceptions(project, {"exceptions": [{"subagent_type": x.ENGINEER, "model": "opus",
                                                 "decision": ["DEC-1230"], "decided": k.DECIDED}]})
    result = _chore(sandbox, cli, x.ENGINEER, "--owner-named", "DEC-1230", "--", "--model", x.OPUS)
    x.launched(result)
    got = x.record_of(result, "kind", "model", "model_source", "exception", "ticket")
    want = {"kind": "chore", "model": x.OPUS, "model_source": "exception", "exception": k.DECIDED, "ticket": None}
    assert got == want, f"the chore's record states {got}, not {want}"


@pytest.mark.parametrize("how", ["pause", "gate"])
def test_x2_gov_pause_and_the_gate_stop_a_chore(sandbox, project, cli, how):
    env, words = x.stop(sandbox, how)
    x.stopped(_chore(sandbox, cli, extra_env=env), words)


@pytest.mark.parametrize("how", ["pause", "gate"])
def test_x2_the_planted_pause_and_gate_stop_an_ordinary_launch(sandbox, project, cli, how):
    """Guard on the base, the plants' own check: what stops a chore above stops an ordinary launch today."""
    tk = s.ticket(project, x.ENGINEER, "C2")
    env, words = x.stop(sandbox, how)
    x.stopped(x.launch(sandbox, cli, x.ENGINEER, tk, extra_env=env), words)


def test_x2_plan_with_chore_prints_the_role_s_default_line(sandbox, project, cli):
    result = x.launch(sandbox, cli, x.ENGINEER, "--plan", "--chore", x.CHORE_LINE)
    model, effort = x.ROLE_DEFAULT
    assert result.run.returncode == 0, f"--plan --chore did not end 0\n{result.describe()}"
    assert result.run.stdout.strip() == f"model {model}, effort {effort}", (
        f"--plan --chore did not print the role's default line\n{result.describe()}")
    assert not result.calls and not result.new_records, f"--plan started or recorded something\n{result.describe()}"


def test_x2_tests_worktree_does_not_take_chore(sandbox, project, cli):
    """``--tests-worktree`` makes a ticket's tests worktree, and a chore has no ticket: refused, nothing made. Not a
    refusal of an unknown option (``unrecognized arguments``): ``--chore`` is one of gov launch's."""
    tree = Path(f"{Path(sandbox.project).resolve()}-tests")
    result = x.launch(sandbox, cli, x.TEST_DESIGNER, "--tests-worktree", "--chore", x.CHORE_LINE)
    assert result.run.returncode != 0, f"--tests-worktree --chore was not refused\n{result.describe()}"
    assert "unrecognized arguments" not in b.said(result), (
        f"gov launch does not know --chore (argparse's 'unrecognized arguments')\n{result.describe()}")
    assert not tree.exists(), f"--tests-worktree --chore made {tree}"
    assert not result.calls and not result.new_records, f"it started or recorded something\n{result.describe()}"
