"""W2-201 fix F19: no launch takes a model the rubric does not give.

DEC-1225 gives every worker role Sonnet at every class. A role file (or a fixture table in it) that names Opus or Haiku
must not make ``gov launch`` start that model: the launcher replaces it with the rubric's model, Sonnet. On W2-184's
fixture project (a role file per worker role with a table that names Opus and Haiku entries) and the stand-in CLI.

Read: the ``--model`` and ``--effort`` the stand-in received, the launch record's ``model`` and ``effort``. The effort
stays the table's (no other change); ``model_source`` is not pinned.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s, b = k.s, k.s.b
ENG, TD, AUD, PS = k.ENGINEER, k.TEST_DESIGNER, k.AUDITOR, k.PRODUCT_SPEC

# (role, class): the fixture table (W2-184) names Opus or Haiku there, with an effort that needs no --reason
NON_RUBRIC = [(ENG, "C3"), (AUD, "C2"), (AUD, "C3"), (PS, "C3"), (ENG, "C0"), (TD, "C1")]


def _started_on_sonnet(result, role, cls):
    b.assert_launched(result)
    effort = s.TABLES[role][cls][1]
    assert result.values("--model") == [k.SONNET], (
        f"the stand-in received --model {result.values('--model')}, not [{k.SONNET!r}]: the fixture table names "
        f"{s.TABLES[role][cls][0]} for {role} at {cls}\n{result.args}")
    assert result.values("--effort") == [effort], f"--effort is {result.values('--effort')}, not [{effort!r}]"
    assert k.record_values(result, "model", "effort") == {"model": k.SONNET, "effort": effort}
    k.quiet(result)  # a replaced model is not a message: a successful launch writes nothing


@pytest.mark.parametrize("role,cls", NON_RUBRIC)
def test_a_table_naming_a_model_the_rubric_does_not_give_launches_sonnet(project, launch, role, cls):
    """Red on the base: the launcher starts the table's Opus or Haiku."""
    tk = s.ticket(project, role, cls)
    _started_on_sonnet(launch(role, tk), role, cls)


@pytest.mark.parametrize("model", [k.OPUS, k.HAIKU], ids=["opus", "haiku"])
def test_a_role_default_line_naming_another_model_launches_sonnet(project, launch, model):
    """No table line, the role file's default line names Opus (or Haiku): the launch is Sonnet, at the line's effort.
    Red on the base."""
    s.write_role(project, ENG, table=None, default=(model, "high"))
    tk = s.ticket(project, ENG, "C2")
    result = launch(ENG, tk)
    b.assert_launched(result)
    assert result.values("--model") == [k.SONNET], f"--model is {result.values('--model')}\n{result.args}"
    assert k.record_values(result, "model", "effort") == {"model": k.SONNET, "effort": "high"}


def test_a_table_naming_sonnet_is_unchanged(project, launch):
    """Guard (green on the base): the engineer's C2 entry is Sonnet, high; nothing is replaced, nothing refused."""
    tk = s.ticket(project, ENG, "C2")
    _started_on_sonnet(launch(ENG, tk), ENG, "C2")
