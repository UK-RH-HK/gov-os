"""W2-201 S3: ``gov launch`` picks the model and effort from the role file, the ticket's class and the table, and
states them in its launch record (RT-8).

Planted worker launches on the stand-in CLI, in W2-184's fixture project (its ``criticality.yaml``: C3 for
``src/critical``, C2 for ``src/product``, C1 for ``docs``), with this repository's own kernel role file planted for the
role launched (``plant_real_role``): the table is the product's, not a fixture's. Each case reads the ``--model`` and
``--effort`` the stand-in received and the launch record: the model and ``model_source`` (``by criticality``), the
effort and ``effort_source``, ``criticality`` and ``rubric`` (the criticality file); a successful launch writes nothing to
stdout or stderr. Without a criticality file the sources are ``role default`` and ``rubric`` is null.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s = k.s
KEYS = ("model", "model_source", "effort", "effort_source", "criticality")


def _launched(result, model, effort, cls, source="by criticality"):
    s.b.assert_launched(result)
    line = {"--model": result.values("--model"), "--effort": result.values("--effort")}
    assert line == {"--model": [model], "--effort": [effort]}, (
        f"the stand-in did not receive --model {model} and --effort {effort} once each: {line}\n{result.args}")
    record = result.record()
    got = {key: record.get(key, s.MISSING) for key in KEYS}
    want = {"model": model, "model_source": source, "effort": effort, "effort_source": source, "criticality": cls}
    assert got == want, f"the launch record states {got}, not {want}"
    rubric = record.get("rubric", s.MISSING)
    if source == "by criticality":
        assert isinstance(rubric, str) and rubric.endswith(k.CRITICALITY_REL), (
            f"the record's rubric is {rubric!r}, not the criticality file {k.CRITICALITY_REL}")
    else:
        assert rubric is None, f"the record's rubric is {rubric!r}, not null (no criticality file)"
    k.quiet(result)
    return record


@pytest.mark.parametrize("role", [k.ENGINEER, k.TEST_DESIGNER])
@pytest.mark.parametrize("cls, model", [("C3", k.OPUS), ("C2", k.SONNET)])
def test_s3_engineer_and_test_designer_run_opus_on_c3_and_sonnet_on_c2(project, launch, role, cls, model):
    """Guard on the base (the kernel lines already say so for these two roles); the record's keys are RT-8's."""
    k.plant_real_role(project, role)
    tk = s.ticket(project, role, cls)
    _launched(launch(role, tk), model, "high", cls)


@pytest.mark.parametrize("cls, model", [("C3", k.OPUS), ("C2", k.SONNET)])
def test_s3_independent_auditor_runs_sonnet_on_c2_and_opus_on_c3(project, launch, cls, model):
    """A STANDARD ticket (no review round). Red on the base: the auditor's kernel file has no table line and a default
    of Opus, so the source is ``role default`` and C2 runs Opus."""
    k.plant_real_role(project, k.AUDITOR)
    tk = s.ticket(project, k.AUDITOR, cls)
    _launched(launch(k.AUDITOR, tk), model, "high", cls)


def test_s3_qa_engineer_runs_sonnet_on_a_full_c2_ticket(project, launch):
    """Red on the base: the QA engineer's kernel C2 entry gives Opus on FULL."""
    k.plant_real_role(project, k.QA)
    tk = s.ticket(project, k.ENGINEER, "C2", "FULL", tk="DAEO-qac2")
    _launched(launch(k.QA, tk), k.SONNET, "high", "C2")


@pytest.mark.parametrize("role, model", [(k.ENGINEER, k.SONNET), (k.AUDITOR, k.SONNET)])
def test_s3_without_a_criticality_file_the_role_default_applies_and_rubric_is_null(project, launch, role, model):
    """A C3 ticket, no criticality file: the role's ``Launch default`` line, source ``role default``, rubric null. The
    engineer's case is a guard; the auditor's is red on the base (its default is Opus)."""
    k.plant_real_role(project, role)
    s.drop_criticality(project)
    tk = s.ticket(project, role, "C3")
    record = _launched(launch(role, tk), model, "high", None, source="role default")
    assert record.get("criticality", s.MISSING) is None
