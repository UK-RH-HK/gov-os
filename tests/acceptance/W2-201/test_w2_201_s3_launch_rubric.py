"""W2-201 S3 (revised for DEC-1225, lines R2): ``gov launch`` picks a worker's model and effort from the role file and
states them in its launch record (RT-8).

Rewrite-Reason: DEC-1225: these cases pinned Opus for the engineer and the test designer on C3 and for the independent
auditor on C3 (the kernel files' table lines). DEC-1225 (1) gives every worker Sonnet, C3 work included, and the role
files no table line (R1), so every class and profile launches the role file's default: Sonnet, high.

Planted worker launches on the stand-in CLI, in W2-184's fixture project (its ``criticality.yaml``: C3 for
``src/critical``, C2 for ``src/product``, C1 for ``docs``), with this repository's own kernel role file planted for the
role launched (``plant_real_role``): the model is the product's, not a fixture's. Each case reads the ``--model`` and
``--effort`` the stand-in received (once each) and the launch record: ``model``, ``effort`` and ``criticality``. Which
word names the source of the model (``role default`` or ``by criticality``) is left open, as R2 does not state it, and
``rubric`` is not pinned. A successful launch writes nothing to stdout or stderr. Without a criticality file the
source is ``role default``, ``criticality`` and ``rubric`` are null.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s = k.s
KEYS = ("model", "effort", "criticality")
SOURCES = ("role default", "by criticality")


def _launched(result, model, effort, cls, source=None):
    s.b.assert_launched(result)
    line = {"--model": result.values("--model"), "--effort": result.values("--effort")}
    assert line == {"--model": [model], "--effort": [effort]}, (
        f"the stand-in did not receive --model {model} and --effort {effort} once each: {line}\n{result.args}")
    record = result.record()
    got = {key: record.get(key, s.MISSING) for key in KEYS}
    assert got == {"model": model, "effort": effort, "criticality": cls}, f"the launch record states {got}"
    for key in ("model_source", "effort_source"):
        found = record.get(key, s.MISSING)
        assert found in (SOURCES if source is None else (source,)), f"the record's {key} is {found!r}"
    if source == "role default":
        assert record.get("rubric", s.MISSING) is None, f"the record's rubric is {record.get('rubric')!r}, not null"
    k.quiet(result)
    return record


@pytest.mark.parametrize("role", [k.ENGINEER, k.TEST_DESIGNER, k.AUDITOR, k.QA, k.PRODUCT_SPEC, k.RESEARCH])
@pytest.mark.parametrize("cls", ["C3", "C2", "C1", "C0"])
def test_s3_every_worker_runs_sonnet_high_at_every_class(project, launch, role, cls):
    """Was: the engineer and test designer on Opus at C3 and the auditor on Opus at C3. Red on the base for C3 of the
    engineer, test designer, auditor and QA engineer (their table lines) and C0 of the same four (Haiku)."""
    k.plant_real_role(project, role)
    # the QA engineer has no ticket kind of its own: the engineer's ticket, as S7's case plants it
    tk = s.ticket(project, k.ENGINEER if role == k.QA else role, cls, tk=f"DAEO-qa{cls.lower()}x" if role == k.QA else None)
    _launched(launch(role, tk), k.SONNET, "high", cls)


def test_s3_qa_engineer_runs_sonnet_on_a_full_c2_ticket(project, launch):
    """Unchanged pin (Sonnet on a FULL C2 ticket), now by the role file's default and not by its table line."""
    k.plant_real_role(project, k.QA)
    tk = s.ticket(project, k.ENGINEER, "C2", "FULL", tk="DAEO-qac2")
    _launched(launch(k.QA, tk), k.SONNET, "high", "C2")


@pytest.mark.parametrize("role", [k.ENGINEER, k.AUDITOR, k.TEST_DESIGNER])
def test_s3_without_a_criticality_file_the_role_default_applies_and_rubric_is_null(project, launch, role):
    """A C3 ticket, no criticality file: the role's ``Launch default`` line, source ``role default``, rubric null."""
    k.plant_real_role(project, role)
    s.drop_criticality(project)
    tk = s.ticket(project, role, "C3")
    record = _launched(launch(role, tk), k.SONNET, "high", None, source="role default")
    assert record.get("criticality", s.MISSING) is None
