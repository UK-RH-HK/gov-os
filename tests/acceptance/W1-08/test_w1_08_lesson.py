"""The lesson schema.

Success 3, third part: a lifecycle state, candidate -> corroborated -> scoped -> proposed -> validated -> approved
[CAP-41.a]. Success 7: a scope of PROJECT, PRODUCT or FRAMEWORK [CAP-41.c]. Success 8: both a scope and a severity
(low, medium, high or critical) are required (DEC-168) [CAP-41.f].

The good lesson is the committed lesson template; each bad lesson is that template with one change. CAP-41.c
writes the scope values in upper case and CAP-41.f in lower case: the tests use the case the template uses.
"""

from __future__ import annotations

import pytest

import w1_08_support as support

LIFECYCLE = ("candidate", "corroborated", "scoped", "proposed", "validated", "approved")
SCOPES = ("project", "product", "framework")
SEVERITIES = ("low", "medium", "high", "critical")


def _in_case_of(sample, word):
    """``word`` in the letter case of ``sample``."""
    if sample.isupper():
        return word.upper()
    if sample.istitle():
        return word.title()
    return word.lower()


def _is_one_of(value, words):
    return isinstance(value, str) and value.lower() in words


@pytest.fixture
def lesson():
    schema = support.schema_path("lesson")
    _, good = support.template("lesson")
    return schema, good


def _lifecycle_keys(good):
    return [key for key, value in good.items() if key not in ("scope", "severity") and _is_one_of(value, LIFECYCLE)]


# --- scope [CAP-41.c, CAP-41.f] ---------------------------------------------------------------------------------

def test_the_lesson_template_carries_a_scope():
    path, good = support.template("lesson")
    assert _is_one_of(good.get("scope"), SCOPES), (
        f"{path.name}: `scope` is {good.get('scope')!r}, not project, product or framework")


@pytest.mark.local_only
@pytest.mark.parametrize("scope", SCOPES)
def test_each_scope_is_accepted(scope, lesson, check):
    schema, good = lesson
    assert _is_one_of(good.get("scope"), SCOPES), "the lesson template has no valid `scope`"
    value = _in_case_of(good["scope"], scope)
    check.accepts(schema, support.replaced(good, "scope", value), f"a lesson with scope {value}")


@pytest.mark.local_only
@pytest.mark.parametrize("scope", ("galaxy", "", 42, None, ["project", "product"]))
def test_a_scope_outside_the_three_is_refused(scope, lesson, check):
    schema, good = lesson
    check.accepts(schema, good, "the lesson template")
    check.refuses(schema, support.replaced(good, "scope", scope), f"a lesson with scope {scope!r}")


@pytest.mark.local_only
def test_a_lesson_without_a_scope_is_refused(lesson, check):
    schema, good = lesson
    assert "scope" in good, "the lesson template has no `scope`"
    check.accepts(schema, good, "the lesson template")
    check.refuses(schema, support.without(good, "scope"), "a lesson without `scope`")


# --- severity [CAP-41.f, DEC-168] -------------------------------------------------------------------------------

def test_the_lesson_template_carries_a_severity():
    path, good = support.template("lesson")
    assert _is_one_of(good.get("severity"), SEVERITIES), (
        f"{path.name}: `severity` is {good.get('severity')!r}, not low, medium, high or critical")


@pytest.mark.local_only
@pytest.mark.parametrize("severity", SEVERITIES)
def test_each_severity_is_accepted(severity, lesson, check):
    schema, good = lesson
    assert _is_one_of(good.get("severity"), SEVERITIES), "the lesson template has no valid `severity`"
    value = _in_case_of(good["severity"], severity)
    check.accepts(schema, support.replaced(good, "severity", value), f"a lesson with severity {value}")


@pytest.mark.local_only
@pytest.mark.parametrize("severity", ("catastrophic", "", 3, None))
def test_a_severity_outside_the_four_is_refused(severity, lesson, check):
    schema, good = lesson
    check.accepts(schema, good, "the lesson template")
    check.refuses(schema, support.replaced(good, "severity", severity), f"a lesson with severity {severity!r}")


@pytest.mark.local_only
def test_a_lesson_without_a_severity_is_refused(lesson, check):
    schema, good = lesson
    assert "severity" in good, "the lesson template has no `severity`"
    check.accepts(schema, good, "the lesson template")
    check.refuses(schema, support.without(good, "severity"), "a lesson without `severity`")


@pytest.mark.local_only
def test_a_lesson_with_a_scope_and_no_severity_or_a_severity_and_no_scope_is_refused(lesson, check):
    """Both are required: one does not stand in for the other."""
    schema, good = lesson
    check.accepts(schema, good, "the lesson template")
    check.refuses(schema, support.without(support.without(good, "scope"), "severity"),
                  "a lesson without `scope` and without `severity`")


# --- lifecycle state [CAP-41.a] ---------------------------------------------------------------------------------

def test_the_lesson_template_carries_a_lifecycle_state():
    path, good = support.template("lesson")
    assert _lifecycle_keys(good), (
        f"{path.name}: no field of the frontmatter holds a lifecycle state (one of {', '.join(LIFECYCLE)})")


@pytest.mark.local_only
def test_the_six_lifecycle_states_are_accepted_and_no_other(lesson, check):
    """One field of the lesson holds the lifecycle state: it takes each of the six states, refuses another word,
    and cannot be left out. The field is found by its value in the template, because no source names it."""
    schema, good = lesson
    keys = _lifecycle_keys(good)
    assert keys, f"the lesson template has no field that holds a lifecycle state (one of {', '.join(LIFECYCLE)})"
    check.accepts(schema, good, "the lesson template")
    problems = []
    for key in keys:
        try:
            for state in LIFECYCLE:
                value = _in_case_of(good[key], state)
                check.accepts(schema, support.replaced(good, key, value), f"a lesson whose `{key}` is {value}")
            check.refuses(schema, support.replaced(good, key, "not-a-lifecycle-state"),
                          f"a lesson whose `{key}` is not a lifecycle state")
            check.refuses(schema, support.without(good, key), f"a lesson without `{key}`")
            return
        except AssertionError as exc:
            problems.append(str(exc))
    raise AssertionError("no field of the lesson record behaves as the lifecycle state:\n" + "\n".join(problems))
