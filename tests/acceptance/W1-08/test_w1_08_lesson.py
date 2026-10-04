"""The lesson schema.

Success 3, third part: a lifecycle state, candidate -> corroborated -> scoped -> proposed -> validated -> approved
[CAP-41.a]. Success 7: a scope of PROJECT, PRODUCT or FRAMEWORK [CAP-41.c]. Success 8: both a scope and a severity
(low, medium, high or critical) are required (DEC-168) [CAP-41.f].

The good lesson is the committed lesson template; each bad lesson is that template with one change. Scope and
severity are stored in lower case, and the schema refuses the upper-case forms (DEC-226).
"""

from __future__ import annotations

import pytest

import w1_08_support as support

LIFECYCLE = ("candidate", "corroborated", "scoped", "proposed", "validated", "approved")
SCOPES = ("project", "product", "framework")
SEVERITIES = ("low", "medium", "high", "critical")


@pytest.fixture
def lesson():
    schema = support.schema_path("lesson")
    _, good = support.template("lesson")
    return schema, good


def _lifecycle_keys(good):
    return [key for key, value in good.items() if key not in ("scope", "severity") and value in LIFECYCLE]


# --- scope [CAP-41.c, CAP-41.f] ---------------------------------------------------------------------------------

def test_the_lesson_template_carries_a_scope_and_a_severity_in_lower_case():
    path, good = support.template("lesson")
    assert good.get("scope") in SCOPES, f"{path.name}: `scope` is {good.get('scope')!r}, not one of {SCOPES}"
    assert good.get("severity") in SEVERITIES, (
        f"{path.name}: `severity` is {good.get('severity')!r}, not one of {SEVERITIES}")


@pytest.mark.local_only
@pytest.mark.parametrize("scope", SCOPES)
def test_each_scope_is_accepted(scope, lesson, check):
    schema, good = lesson
    check.accepts(schema, support.replaced(good, "scope", scope), f"a lesson with scope {scope}")


@pytest.mark.local_only
@pytest.mark.parametrize("scope", ("PROJECT", "galaxy", None, ["project", "product"]))
def test_a_scope_outside_the_three_is_refused(scope, lesson, check):
    """`PROJECT` is CAP-41.c's spelling of a value that is stored as `project` (DEC-226)."""
    schema, good = lesson
    check.good(schema, good, "the lesson template")
    check.refuses(schema, support.replaced(good, "scope", scope), f"a lesson with scope {scope!r}")


# --- severity [CAP-41.f, DEC-168] -------------------------------------------------------------------------------

@pytest.mark.local_only
@pytest.mark.parametrize("severity", SEVERITIES)
def test_each_severity_is_accepted(severity, lesson, check):
    schema, good = lesson
    check.accepts(schema, support.replaced(good, "severity", severity), f"a lesson with severity {severity}")


@pytest.mark.local_only
@pytest.mark.parametrize("severity", ("HIGH", "catastrophic", 3, None))
def test_a_severity_outside_the_four_is_refused(severity, lesson, check):
    schema, good = lesson
    check.good(schema, good, "the lesson template")
    check.refuses(schema, support.replaced(good, "severity", severity), f"a lesson with severity {severity!r}")


# --- both are required [CAP-41.f] -------------------------------------------------------------------------------

@pytest.mark.local_only
@pytest.mark.parametrize("field", ("scope", "severity"))
def test_a_lesson_without_the_field_is_refused(field, lesson, check):
    """Both are required: one does not stand in for the other."""
    schema, good = lesson
    assert field in good, f"the lesson template has no `{field}`"
    check.good(schema, good, "the lesson template")
    check.refuses(schema, support.without(good, field), f"a lesson without `{field}`")


# --- lifecycle state [CAP-41.a] ---------------------------------------------------------------------------------

def test_the_lesson_template_carries_a_lifecycle_state():
    path, good = support.template("lesson")
    assert _lifecycle_keys(good), (
        f"{path.name}: no field of the frontmatter holds a lifecycle state (one of {', '.join(LIFECYCLE)})")


@pytest.mark.local_only
def test_the_six_lifecycle_states_are_accepted_and_no_other(lesson, check):
    """One field of the lesson holds the lifecycle state: it takes each of the six states, refuses another word,
    and cannot be left out. The field is found by its value in the template, because no source says whether it is
    `lifecycle` or `status`."""
    schema, good = lesson
    keys = _lifecycle_keys(good)
    assert keys, f"the lesson template has no field that holds a lifecycle state (one of {', '.join(LIFECYCLE)})"
    check.good(schema, good, "the lesson template")
    problems = []
    for key in keys:
        try:
            for state in LIFECYCLE:
                check.accepts(schema, support.replaced(good, key, state), f"a lesson whose `{key}` is {state}")
            check.refuses(schema, support.replaced(good, key, "not-a-lifecycle-state"),
                          f"a lesson whose `{key}` is not a lifecycle state")
            check.refuses(schema, support.without(good, key), f"a lesson without `{key}`")
            return
        except AssertionError as exc:
            problems.append(str(exc))
    raise AssertionError("no field of the lesson record behaves as the lifecycle state:\n" + "\n".join(problems))
