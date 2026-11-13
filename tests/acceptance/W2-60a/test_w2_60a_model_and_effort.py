"""W2-60a, KPI success 3 and 4 -- the role's default model and effort, and the subagent model.

KPI success 3 [DEC-839 items 1, 2 and 5, CAP-35.c lite, lens F R1]: "The
role's default model and effort, read from its role file's default line, are
applied on the launch line (--model, --effort) and recorded; a missing or
malformed default line refuses the launch; an effort given after -- is applied
and recorded as the launch's own".

KPI success 4 [DEC-839 items 1 and 3, lens E F14]: "A model given after --
that is not the role's is refused, naming both; the subagent model is set to
the session's model (CLAUDE_CODE_SUBAGENT_MODEL in the settings' env) and
recorded". KPI failure 1: "a model not the role's"; KPI failure 2: "A role file
without its default line that still launches".

The default line's form (Behaviour 3), exactly once, as a whole line:
``- **Launch default:** model <model>, effort <effort>``: ``<model>`` is
``claude-`` then groups of lower-case letters and digits joined by ``-`` (no
alias); ``<effort>`` one of low, medium, high, xhigh, max; one space after each
``:`` and ``,``; nothing before the ``-`` or after the effort; no third field.
``--model`` and ``--effort`` go on the line only when the arguments after
``--`` carry none, so either is passed once. The fixture research role's model
is ``claude-sonnet-5-5``, so the value is seen to come from the role file.
"""

from __future__ import annotations

import pytest

import w2_60a_support as s


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_the_role_s_default_model_and_effort_are_on_the_line_and_recorded(launch, role):
    model, effort = s.DEFAULTS[role]
    result = launch(role)
    s.assert_launched(result)
    assert result.one("--model") == model, f"--model on the line is not the role's {model}: {result.args}"
    assert result.one("--effort") == effort, f"--effort on the line is not the role's {effort}: {result.args}"
    record = result.record()
    got = {key: record.get(key) for key in ("model", "model_source", "effort", "effort_source")}
    assert got == {"model": model, "model_source": "role default", "effort": effort,
                   "effort_source": "role default"}, f"the record's model and effort: {got}"


@pytest.mark.parametrize("passed", (("--effort", "xhigh"), ("--effort=xhigh",)), ids=("spaced", "joined"))
def test_an_effort_after_the_double_dash_is_applied_and_recorded_as_the_launch_s_own(launch, passed):
    """DEC-839 item 2: a FULL ticket's test designer at xhigh, given after ``--``."""
    arguments = ("-p", "Write the tests.", *passed)
    result = launch(s.TEST_DESIGNER, None, *arguments)
    s.assert_launched(result)
    s.assert_passed_through(result, arguments)
    assert s.occurrences(result.args, "--effort") == 1, f"--effort is passed more than once: {result.args}"
    record = result.record()
    assert (record.get("effort"), record.get("effort_source")) == ("xhigh", "after --"), (
        f"the record does not hold the effort given after -- as the launch's own: {record.get('effort')!r}, "
        f"{record.get('effort_source')!r}")


@pytest.mark.parametrize("passed", (("--model", s.OPUS), (f"--model={s.OPUS}",)), ids=("spaced", "joined"))
def test_the_role_s_own_model_after_the_double_dash_is_passed_once(launch, passed):
    arguments = ("-p", "Do the ticket's work.", *passed)
    result = launch(s.ENGINEER, None, *arguments)
    s.assert_launched(result)
    s.assert_passed_through(result, arguments)
    assert s.occurrences(result.args, "--model") == 1, f"--model is passed more than once: {result.args}"
    record = result.record()
    assert (record.get("model"), record.get("model_source")) == (s.OPUS, "after --"), (
        f"the record's model: {record.get('model')!r}, {record.get('model_source')!r}")


# --------------------------------------------------------------------------
# The default line: missing or malformed
# --------------------------------------------------------------------------

def test_a_role_file_without_its_default_line_is_refused(project, launch):
    s.write_role(project, s.ENGINEER, default="")
    s.assert_refused(launch(s.ENGINEER), "engineer.md", "Launch default")


MALFORMED = {
    "alias-model": "- **Launch default:** model opus, effort high",
    "not-a-claude-model": "- **Launch default:** model gpt-5, effort high",
    "upper-case-model": "- **Launch default:** model Claude-Opus-5-5, effort high",
    "unknown-effort": "- **Launch default:** model claude-opus-5-5, effort extreme",
    "third-field-threshold": "- **Launch default:** model claude-opus-5-5, effort high, autocompact 300000",
    "no-space-after-comma": "- **Launch default:** model claude-opus-5-5,effort high",
    "text-after-effort": "- **Launch default:** model claude-opus-5-5, effort high (for now)",
    "indented": "  - **Launch default:** model claude-opus-5-5, effort high",
    "two-default-lines": ("- **Launch default:** model claude-opus-5-5, effort high\n"
                          "- **Launch default:** model claude-opus-5-5, effort high"),
}


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_a_malformed_default_line_is_refused(project, launch, case):
    s.write_role(project, s.ENGINEER, default=MALFORMED[case])
    s.assert_refused(launch(s.ENGINEER), "engineer.md", "Launch default")


# --------------------------------------------------------------------------
# After --: a model not the role's, a wrong effort
# --------------------------------------------------------------------------

NOT_THE_ROLES = {
    "alias-spaced": (s.ENGINEER, ("--model", "haiku"), "haiku"),
    "alias-of-the-same-model": (s.ENGINEER, ("--model", "opus"), "opus"),
    "another-model-spaced": (s.ENGINEER, ("--model", s.SONNET), s.SONNET),
    "another-model-joined": (s.ENGINEER, (f"--model={s.HAIKU}",), s.HAIKU),
    "research-given-opus": (s.RESEARCH, ("--model", s.OPUS), s.OPUS),
}


@pytest.mark.parametrize("case", sorted(NOT_THE_ROLES))
def test_a_model_that_is_not_the_role_s_is_refused_naming_both(launch, case):
    role, passed, given = NOT_THE_ROLES[case]
    result = launch(role, None, "-p", "Do the work.", *passed)
    s.assert_refused(result, "LAUNCH_REFUSED", "the CLI arguments carry", given, s.DEFAULTS[role][0])


ARGUMENT_FAULTS = {
    "model-without-value": (("-p", "x", "--model"), "--model"),
    "model-empty-joined": (("--model=",), "--model"),
    "model-twice": (("--model", s.OPUS, "--model", s.OPUS), "--model"),
    "effort-without-value": (("-p", "x", "--effort"), "--effort"),
    "effort-empty-joined": (("--effort=",), "--effort"),
    "effort-twice": (("--effort", "high", "--effort", "low"), "--effort"),
    "effort-unknown-spaced": (("--effort", "extreme"), "--effort"),
    "effort-unknown-joined": (("--effort=extreme",), "--effort"),
}


@pytest.mark.parametrize("case", sorted(ARGUMENT_FAULTS))
def test_a_model_or_effort_without_a_value_twice_or_unknown_is_refused(launch, case):
    passed, name = ARGUMENT_FAULTS[case]
    s.assert_refused(launch(s.ENGINEER, None, *passed), "LAUNCH_REFUSED", "the CLI arguments carry", name)


# --------------------------------------------------------------------------
# The subagent model
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", (s.ENGINEER, s.RESEARCH))
def test_the_subagent_model_is_the_session_s_model_and_recorded(launch, role):
    model = s.DEFAULTS[role][0]
    result = launch(role)
    s.assert_launched(result)
    assert result.env_block().get("CLAUDE_CODE_SUBAGENT_MODEL") == model, (
        f"the settings' env does not set CLAUDE_CODE_SUBAGENT_MODEL to the session's model {model}: "
        f"{result.env_block()}")
    assert result.record().get("subagent_model") == model, (
        f"the record's subagent_model is not {model}: {result.record().get('subagent_model')!r}")


def test_a_subagent_model_in_the_caller_s_environment_does_not_reach_the_settings(launch):
    result = launch(s.ENGINEER, extra_env={"CLAUDE_CODE_SUBAGENT_MODEL": s.HAIKU})
    s.assert_launched(result)
    assert result.env_block().get("CLAUDE_CODE_SUBAGENT_MODEL") == s.OPUS, (
        f"the settings' subagent model is not the session's: {result.env_block().get('CLAUDE_CODE_SUBAGENT_MODEL')!r}")
