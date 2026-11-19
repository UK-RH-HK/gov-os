"""W2-201 S4: ``gov launch`` refuses a caller's other model; an exception comes only from the exceptions file.

W2-184's fixture project (fixture role tables: the engineer's C2 entry is Sonnet, high) on the stand-in CLI.
``governance/project/model-exceptions.yaml`` is planted per case: ``exceptions: [{subagent_type, model, decided,
class?}]``; ``model: opus`` matches every ``claude-opus-*`` id. A refusal is ``LAUNCH_REFUSED`` (exit 1, no session, no
record) naming the session model asked for, the ticket's class and the exceptions file. A launch on an exception runs
the model asked for and records ``model_source`` ``exception`` and the entry's ``decided`` text in ``exception``, which
is null in every other record. An exceptions file that cannot be read, or is not a map with an ``exceptions`` list,
refuses a launch that asks for another model and leaves a launch that asks for none as it was.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s = k.s
ENG, TD = k.ENGINEER, k.TEST_DESIGNER
DECIDED = "the owner, 2026-11-18 (W2-201 fixture entry)"
ASK_OPUS = ("--model", k.OPUS)


def _entry(role=ENG, model="opus", cls=None, decided=DECIDED):
    entry = {"subagent_type": role, "model": model, "decided": decided}
    if cls is not None:
        entry["class"] = cls
    return entry


def _on_exception(result, decided=DECIDED):
    s.b.assert_launched(result)
    assert result.values("--model") == [k.OPUS], (
        f"the stand-in did not receive --model {k.OPUS} once: {result.args}")
    got = k.record_values(result, "model", "model_source", "exception")
    want = {"model": k.OPUS, "model_source": "exception", "exception": decided}
    assert got == want, f"the launch record states {got}, not {want}"


def _refused(result, cls):
    s.refused(result, k.OPUS, cls, k.EXCEPTIONS_REL)


# --------------------------------------------------------------------------
# The refusal, and the exception that lifts it
# --------------------------------------------------------------------------

def test_s4_an_engineer_asking_opus_on_a_c2_ticket_is_refused_naming_model_class_and_exceptions_file(project, launch):
    """No exceptions file. Red on the base: W2-184 refuses, but names neither the class nor the exceptions file."""
    tk = s.ticket(project, ENG, "C2")
    _refused(launch(ENG, tk, *ASK_OPUS), "C2")


def test_s4_an_exceptions_file_with_no_entry_for_the_role_still_refuses(project, launch):
    k.write_exceptions(project, {"exceptions": [_entry(role=k.RESEARCH)]})
    tk = s.ticket(project, ENG, "C2")
    _refused(launch(ENG, tk, *ASK_OPUS), "C2")


@pytest.mark.parametrize("model", ["opus", k.OPUS], ids=["alias-opus", "model-id"])
def test_s4_an_entry_for_the_engineer_and_opus_starts_it_on_opus_and_records_the_exception(project, launch, model):
    k.write_exceptions(project, {"exceptions": [_entry(model=model)]})
    tk = s.ticket(project, ENG, "C2")
    _on_exception(launch(ENG, tk, *ASK_OPUS))


def test_s4_an_entry_with_class_c3_lifts_the_refusal_on_a_c3_ticket(project, launch):
    """The test designer with no table line and a Sonnet default, so Opus is another model in every class."""
    s.write_role(project, TD, table=None, default=(k.SONNET, "high"))
    k.write_exceptions(project, {"exceptions": [_entry(role=TD, cls="C3")]})
    tk = s.ticket(project, TD, "C3")
    _on_exception(launch(TD, tk, *ASK_OPUS))


def test_s4_an_entry_with_class_c3_does_not_lift_the_refusal_on_a_c2_ticket(project, launch):
    s.write_role(project, TD, table=None, default=(k.SONNET, "high"))
    k.write_exceptions(project, {"exceptions": [_entry(role=TD, cls="C3")]})
    tk = s.ticket(project, TD, "C2")
    _refused(launch(TD, tk, *ASK_OPUS), "C2")


def test_s4_the_exception_key_is_null_in_a_launch_that_takes_no_exception(project, launch):
    """An exceptions file that lists the engineer, and a launch that asks for no model: the table applies (C2 Sonnet,
    ``by criticality``) and ``exception`` is null. Red on the base: the record has no ``exception`` key."""
    k.write_exceptions(project, {"exceptions": [_entry()]})
    tk = s.ticket(project, ENG, "C2")
    result = launch(ENG, tk)
    s.b.assert_launched(result)
    got = k.record_values(result, "model", "model_source", "exception")
    assert got == {"model": k.SONNET, "model_source": "by criticality", "exception": None}, got


# --------------------------------------------------------------------------
# An exceptions file that cannot be used: fail closed for another model, no effect on a launch that asks none
# --------------------------------------------------------------------------

ENTRY_YAML = "{subagent_type: engineer, model: opus, decided: \"the owner\"}"
BAD_FILES = {
    "does-not-parse": f"exceptions: [ {ENTRY_YAML}\n",
    "a-list-not-a-map": f"- {ENTRY_YAML}\n",
    "no-exceptions-key": f"entries:\n  - {ENTRY_YAML}\n",
    "exceptions-not-a-list": f"exceptions: {ENTRY_YAML}\n",
    "cannot-be-read": None,  # a folder where the file should be
}


def _plant_bad(project, form):
    text = BAD_FILES[form]
    path = project / k.EXCEPTIONS_REL
    if text is None:
        path.mkdir(parents=True, exist_ok=True)
        (path / "entry.yaml").write_text(ENTRY_YAML + "\n", encoding="utf-8")
    else:
        k.write_exceptions(project, text)


@pytest.mark.parametrize("form", sorted(BAD_FILES))
def test_s4_an_unusable_exceptions_file_refuses_a_launch_asking_another_model(project, launch, form):
    _plant_bad(project, form)
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk, *ASK_OPUS), k.EXCEPTIONS_REL)


@pytest.mark.parametrize("form", sorted(BAD_FILES))
def test_s4_an_unusable_exceptions_file_does_not_touch_a_launch_asking_no_model(project, launch, form):
    _plant_bad(project, form)
    tk = s.ticket(project, ENG, "C2")
    result = launch(ENG, tk)
    s.b.assert_launched(result)
    got = k.record_values(result, "model", "effort", "model_source", "exception")
    assert got == {"model": k.SONNET, "effort": "high", "model_source": "by criticality", "exception": None}, got
