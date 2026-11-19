"""W2-201 S9: the rules of S4, S5 and S6 under the owner's temporary Fable substitution (DEC-1215), and unchanged
without it.

``governance/project/model-substitution.yaml`` is planted in the real file's form (``active``, ``from`` Opus, ``to``
``claude-fable-5-2``, ``effort`` high, ``until``, ``decided``) in three states: active with a fixed far-future
``until``, ``active: false``, and active with a past ``until``; a fourth, no file, where a case names it.

* **The hook** as S5 runs it (a subprocess on one PreToolUse event, the planted project of S5: the fixture tickets and
  rubric, the four roles' entries on ``opus`` with ``class: C3``). Active: ``fable`` and ``claude-fable-5-2`` are judged
  as Opus is in S5; Opus itself is refused with the Fable hint; a fork is refused as in S6. Not active: Fable is refused
  as any non-Sonnet model no entry names, and Opus is judged as S5 says.
* **The launcher** as S3 and S4 run it (W2-184's fixture project on the stand-in CLI; the engineer's fixture table: C3
  Opus, C2 Sonnet). Active: an Opus table entry runs Fable; a caller's ``--model claude-fable-5-2`` goes by S4 through
  an exceptions entry naming ``opus``; a caller's ``--model claude-opus-*`` is refused naming DEC-1215 and ``fable``,
  whatever the entry and the ticket. Not active: the caller's Fable is refused, C3 runs Opus, and a caller's Opus goes
  by S4.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s = k.s
ENG, TD = k.ENGINEER, k.TEST_DESIGNER
DECIDED = "the owner, 2026-11-18 (W2-201 S9 fixture entry)"
NO_CLASS = {"exceptions": [{"subagent_type": ENG, "model": "opus", "decided": k.DECIDED}]}
FORK_WORDS = ("a fresh helper from a written brief", "DEC-1212 (4)")
ASK_FABLE = ("--model", k.FABLE)
NOT_ACTIVE = ("inactive", "past-until")

fable_names = pytest.mark.parametrize("model", k.FABLE_NAMES, ids=["alias-fable", "fable-id"])


def _hook(hook_base, state, exceptions="fixture", **spawn):
    project = k.plant_substitution(k.hook_project(hook_base, exceptions=exceptions), state)
    return k.run_hook(project, k.spawn(**spawn))


# --------------------------------------------------------------------------
# The hook, the substitution active: Fable is judged as Opus
# --------------------------------------------------------------------------

@fable_names
def test_s9_hook_active_a_fable_spawn_for_a_c3_ticket_is_let_through(hook_base, model):
    """Guard on the base (the base lets Fable through on an Opus entry, whatever the ticket)."""
    k.let_through(_hook(hook_base, "active", model=model, tasks=(k.C3_TICKET,)))


@fable_names
def test_s9_hook_active_a_fable_spawn_for_a_c2_ticket_is_refused_as_opus_is(hook_base, model):
    """Red on the base: the hook reads no ticket."""
    k.refused(_hook(hook_base, "active", model=model, tasks=(k.C2_TICKET,)), k.C2_TICKET, "C2", "C3 work only")


@fable_names
def test_s9_hook_active_a_fable_spawn_with_no_task_line_is_refused_naming_the_task_line(hook_base, model):
    """Red on the base."""
    k.refused(_hook(hook_base, "active", model=model, tasks=()), "Task:")


@fable_names
def test_s9_hook_active_an_entry_without_a_class_lets_fable_through_with_no_task_line(hook_base, model):
    """An ``opus`` entry with no ``class`` covers Fable and asks for no ticket. Guard on the base."""
    k.let_through(_hook(hook_base, "active", exceptions=NO_CLASS, model=model, tasks=()))


@pytest.mark.parametrize("model", ["opus", k.OPUS], ids=["alias-opus", "opus-id"])
def test_s9_hook_active_an_opus_spawn_is_refused_with_the_fable_hint(hook_base, model):
    """A C3 ticket and the role's entry: Opus itself is still refused, naming DEC-1215 and ``fable``. Guard on the
    base."""
    k.refused(_hook(hook_base, "active", model=model, tasks=(k.C3_TICKET,)), "DEC-1215", "fable")


@pytest.mark.parametrize("model", [k.NO_MODEL, "fable", "opus"], ids=["no-model", "fable", "opus"])
def test_s9_hook_active_a_fork_is_refused_as_in_s6(hook_base, model):
    """Red on the base: no fork rule there."""
    k.refused(_hook(hook_base, "active", kind="fork", model=model, tasks=(k.C3_TICKET,)), *FORK_WORDS)


@pytest.mark.parametrize("model", ["sonnet", k.SONNET, k.NO_MODEL], ids=["sonnet", "sonnet-id", "no-model"])
@pytest.mark.parametrize("tasks", [(k.C2_TICKET,), ()], ids=["c2-ticket", "no-task-line"])
def test_s9_hook_active_a_sonnet_or_no_model_spawn_is_let_through(hook_base, model, tasks):
    """Guard on the base."""
    k.let_through(_hook(hook_base, "active", model=model, tasks=tasks))


# --------------------------------------------------------------------------
# The hook, no substitution in force: Fable is any other model, Opus is S5's
# --------------------------------------------------------------------------

@pytest.mark.parametrize("state", k.SUBSTITUTION_OFF)
@fable_names
def test_s9_hook_not_active_a_fable_spawn_is_refused(hook_base, state, model):
    """A C3 ticket and the role's ``opus`` entry: no entry names Fable, so it is refused. Guard on the base."""
    k.refused(_hook(hook_base, state, model=model, tasks=(k.C3_TICKET,)))


@pytest.mark.parametrize("state", NOT_ACTIVE)
def test_s9_hook_not_active_an_opus_spawn_for_a_c3_ticket_is_let_through(hook_base, state):
    """Guard on the base."""
    k.let_through(_hook(hook_base, state, model="opus", tasks=(k.C3_TICKET,)))


@pytest.mark.parametrize("state", NOT_ACTIVE)
def test_s9_hook_not_active_an_opus_spawn_for_a_c2_ticket_is_refused_as_s5_says(hook_base, state):
    """Red on the base: the hook reads no ticket."""
    k.refused(_hook(hook_base, state, model="opus", tasks=(k.C2_TICKET,)), k.C2_TICKET, "C2", "C3 work only")


# --------------------------------------------------------------------------
# The launcher
# --------------------------------------------------------------------------

def _entry(role=ENG, cls=None):
    entry = {"subagent_type": role, "model": "opus", "decided": DECIDED}
    if cls is not None:
        entry["class"] = cls
    return {"exceptions": [entry]}


def _ran(result, model):
    s.b.assert_launched(result)
    assert result.values("--model") == [model], f"the stand-in did not receive --model {model} once: {result.args}"
    got = k.record_values(result, "model")
    assert got == {"model": model}, f"the launch record states {got}, not model {model}"


def _on_exception(result, model=k.FABLE):
    s.b.assert_launched(result)
    assert result.values("--model") == [model], f"the stand-in did not receive --model {model} once: {result.args}"
    got = k.record_values(result, "model", "model_source", "exception")
    want = {"model": model, "model_source": "exception", "exception": DECIDED}
    assert got == want, f"the launch record states {got}, not {want}"


def test_s9_launch_active_an_engineer_on_a_c3_ticket_runs_fable(project, launch):
    """The table's C3 entry is Opus: the substituted model runs. Guard on the base."""
    k.plant_substitution(project, "active")
    _ran(launch(ENG, s.ticket(project, ENG, "C3")), k.FABLE)


def test_s9_launch_active_an_engineer_on_a_c2_ticket_still_runs_sonnet(project, launch):
    """Guard on the base."""
    k.plant_substitution(project, "active")
    _ran(launch(ENG, s.ticket(project, ENG, "C2")), k.SONNET)


def test_s9_launch_active_a_caller_s_fable_with_an_opus_entry_starts_on_the_exception(project, launch):
    """Red on the base: no exceptions route."""
    k.plant_substitution(project, "active")
    k.write_exceptions(project, _entry())
    _on_exception(launch(ENG, s.ticket(project, ENG, "C2"), *ASK_FABLE))


def test_s9_launch_active_an_entry_with_class_c3_does_not_lift_the_refusal_on_a_c2_ticket(project, launch):
    """As S4's case: the test designer with no table line and a Sonnet default. Red on the base: the refusal does not
    name the exceptions file."""
    k.plant_substitution(project, "active")
    s.write_role(project, TD, table=None, default=(k.SONNET, "high"))
    k.write_exceptions(project, _entry(role=TD, cls="C3"))
    s.refused(launch(TD, s.ticket(project, TD, "C2"), *ASK_FABLE), "C2", k.EXCEPTIONS_REL)


def test_s9_launch_active_an_entry_with_class_c3_lifts_the_refusal_on_a_c3_ticket(project, launch):
    """Red on the base: no exceptions route."""
    k.plant_substitution(project, "active")
    s.write_role(project, TD, table=None, default=(k.SONNET, "high"))
    k.write_exceptions(project, _entry(role=TD, cls="C3"))
    _on_exception(launch(TD, s.ticket(project, TD, "C3"), *ASK_FABLE))


@pytest.mark.parametrize("state", k.SUBSTITUTION_OFF)
def test_s9_launch_not_active_a_caller_s_fable_is_refused_even_with_the_opus_entry(project, launch, state):
    """Red on the base: the refusal does not name the exceptions file."""
    k.plant_substitution(project, state)
    k.write_exceptions(project, _entry())
    s.refused(launch(ENG, s.ticket(project, ENG, "C2"), *ASK_FABLE), k.EXCEPTIONS_REL)


@pytest.mark.parametrize("state", k.SUBSTITUTION_OFF)
def test_s9_launch_not_active_an_engineer_on_a_c3_ticket_runs_opus(project, launch, state):
    """Guard on the base."""
    k.plant_substitution(project, state)
    _ran(launch(ENG, s.ticket(project, ENG, "C3")), k.OPUS)


# --------------------------------------------------------------------------
# The launcher, a caller's Opus: refused while the substitution is active, S4's without it
# --------------------------------------------------------------------------

# id -> (role, the ticket's class, the exceptions entry's class or "none" for no exceptions file, the model asked for)
OPUS_CALLERS = {
    "c2-entry-without-class": (ENG, "C2", None, k.OPUS),
    "c3-entry-without-class": (ENG, "C3", None, k.OPUS),
    "c3-entry-with-class-c3": (TD, "C3", "C3", k.OPUS),
    "c2-no-exceptions-file": (ENG, "C2", "none", k.OPUS),
    "another-opus-id": (ENG, "C2", None, "claude-opus-4-7"),
}


@pytest.mark.parametrize("case", sorted(OPUS_CALLERS))
def test_s9_launch_active_a_caller_s_opus_is_refused_naming_dec_1215_and_fable(project, launch, case):
    """Even with an entry naming ``opus`` for the role and even on a C3 ticket. The test designer is S4's (no table
    line, a Sonnet default)."""
    role, cls, entry_class, model = OPUS_CALLERS[case]
    k.plant_substitution(project, "active")
    if role == TD:
        s.write_role(project, TD, table=None, default=(k.SONNET, "high"))
    if entry_class != "none":
        k.write_exceptions(project, _entry(role=role, cls=entry_class))
    s.refused(launch(role, s.ticket(project, role, cls), "--model", model), "DEC-1215", "fable")


@pytest.mark.parametrize("state", k.SUBSTITUTION_OFF)
def test_s9_launch_not_active_a_caller_s_opus_without_an_entry_is_refused_as_s4_says(project, launch, state):
    k.plant_substitution(project, state)
    s.refused(launch(ENG, s.ticket(project, ENG, "C2"), "--model", k.OPUS), k.OPUS, "C2", k.EXCEPTIONS_REL)


@pytest.mark.parametrize("state", k.SUBSTITUTION_OFF)
def test_s9_launch_not_active_a_caller_s_opus_with_an_entry_starts_on_the_exception(project, launch, state):
    k.plant_substitution(project, state)
    k.write_exceptions(project, _entry())
    _on_exception(launch(ENG, s.ticket(project, ENG, "C2"), "--model", k.OPUS), k.OPUS)
