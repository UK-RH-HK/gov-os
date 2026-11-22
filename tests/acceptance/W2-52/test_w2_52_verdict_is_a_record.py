"""A verdict that the A5, A7 or A10 gate accepts is a record the store reads [fix under W2-52; CAP-44.f, CAP-06].

Evidence (release 0.1.4, W2-81's proving run): an adopter's A5 and A7 verdicts had the front matter ``id``, ``type``,
``stage``, ``verdict: pass`` and the auditor's keys, but no ``status``. The gates accepted them (exit 0); the final
``gov rebuild`` then listed each file as an invalid record ("required key missing or not a string: status"), because
the store reads every Markdown file whose front matter states an ``id`` and requires non-empty string ``id``, ``type``
and ``status``. A file with front matter and no ``id`` is no record and is never listed.

KPI line: a verdict whose front matter states an ``id`` but lacks a non-empty string ``type`` or ``status`` is
refused with ``VERDICT_NOT_A_RECORD``, the message naming the missing keys and the file; a verdict that states
``id``, ``type`` and ``status`` is accepted and ``gov rebuild`` then lists no invalid record for it; a verdict with
no ``id`` (the adopt skill's form) is still accepted and still listed invalid by nothing. Failure: a gate that
accepts a verdict that rebuild then calls invalid.

Every case drives ``gov adopt --lite --stage A5|A7|A10 --verdict <path> --json`` and ``gov rebuild --json`` in a
temporary project. The new refusal comes after the existing checks (README, "Fix: a verdict is a record").
"""

from __future__ import annotations

import pytest

import w2_52_support as gates

support = gates.support
CODE = "VERDICT_NOT_A_RECORD"


def _code(error):
    """The refusal's code as the stages name it; the envelope may carry the ``ADOPT_`` prefix every adopt refusal has
    (``ADOPT_VERDICT_NOT_PASS`` is what ``gov adopt`` answers for ``VERDICT_NOT_PASS``)."""
    code = str(error.get("code"))
    return code[len("ADOPT_"):] if code.startswith("ADOPT_") else code


@pytest.fixture(scope="module")
def after_a4(tmp_path_factory, interface, stand_in, vector_site):
    """The harbour project through A4 (the A5 gate's own ground), kept for the cases to copy."""
    folder = tmp_path_factory.mktemp("after-a4")
    project = gates.build_harbour(folder / "harbour")
    adoption = gates.GateAdoption(project, support.make_sandbox(folder / "sandbox"), interface,
                                  endpoint=stand_in.host, site=vector_site)
    adoption.through("A4", gates.proposal())
    return gates.snapshot(adoption)


@pytest.fixture()
def a4_copy(after_a4, tmp_path, interface, stand_in, vector_site):
    return gates.copy_adoption(after_a4, tmp_path, interface, endpoint=stand_in.host, site=vector_site)


# --------------------------------------------------------------------------
# One door for the three stages: write the auditor's record with a change to its keys, run the gate
# --------------------------------------------------------------------------

def _a5(adoption, role=support.AUDITOR_ROLE, **keys):
    support.write_verdict(adoption.project, adoption.stages["A3"].record, role=role, **keys)
    return support.VERDICT_REL, ("A5", "--verdict", support.VERDICT_REL)


def _gate(stage):
    def write(adoption, role=support.AUDITOR_ROLE, **keys):
        rel = gates.write_gate_verdict(adoption, stage, role=role, **keys)
        return rel, (stage, "--verdict", rel)
    return write


DOORS = {"A5": _a5, "A7": _gate("A7"), "A10": _gate("A10")}
FIXTURE = {"A5": "a4_copy", "A7": "a6_copy", "A10": "a8_copy"}


def _copy(request, stage):
    return request.getfixturevalue(FIXTURE[stage])


def _run(adoption, gate, **keys):
    """Write the record (``keys`` change its front matter; None leaves a key out), run the gate once."""
    rel, args = DOORS[gate](adoption, **keys)
    before = support.tree(adoption.project)
    run = adoption.run(*args)
    return rel, run, before


def _assert_no_stage_record(adoption, stage, before):
    assert support.tree(adoption.project) == before, f"the refused {stage} gate wrote something"
    assert support.porcelain(adoption.project) == "", f"the refused {stage} gate left the tree dirty"


def _assert_refused_not_a_record(adoption, stage, rel, run, before, *keys):
    """The gate refused with VERDICT_NOT_A_RECORD; the message names the file and each missing key; nothing written."""
    error = support.assert_refused(run, adoption.interface, rel)
    assert _code(error) == CODE, f"the refusal is {error.get('code')!r}, not {CODE}\n{run.describe()}"
    for key in keys:
        assert key in str(error.get("message")), f"the message does not name the missing key {key!r}\n{run.describe()}"
    _assert_no_stage_record(adoption, stage, before)


def _invalid_paths(adoption):
    """The paths ``gov rebuild --json`` lists as invalid records (any depth of its result, under ``invalid``)."""
    run = adoption.gov("rebuild", "--json")
    envelope = run.envelope()
    assert envelope and envelope.get("ok") is True, f"the rebuild failed\n{run.describe()}"
    found = []

    def walk(value, under=False):
        if isinstance(value, dict):
            for key, item in value.items():
                walk(item, under or key == "invalid")
            if under and isinstance(value.get("path"), str):
                found.append(value["path"])
        elif isinstance(value, list):
            for item in value:
                walk(item, under)
        elif under and isinstance(value, str):
            found.append(value)

    walk(envelope.get("result"))
    return found


def _assert_accepted_and_read(adoption, stage, rel, run):
    """The gate accepted the verdict (exit 0, ok), and the store lists no invalid record naming it."""
    envelope = run.envelope()
    assert envelope and envelope.get("ok") is True and run.returncode == 0, \
        f"the {stage} gate did not accept the verdict {rel}\n{run.describe()}"
    invalid = [path for path in _invalid_paths(adoption) if path == rel]
    assert not invalid, f"the gate accepted {rel} and gov rebuild lists it as an invalid record"


# --------------------------------------------------------------------------
# (a), (b), (e): an id with no usable type or status is refused, on every stage
# --------------------------------------------------------------------------

@pytest.mark.parametrize("stage", ["A5", "A7", "A10"])
def test_a_verdict_with_an_id_and_no_status_is_refused_as_not_a_record(request, stage):
    """(a): ``id`` and ``type`` but no ``status``: VERDICT_NOT_A_RECORD naming ``status`` and the file; no stage record."""
    adoption = _copy(request, stage)
    rel, run, before = _run(adoption, stage, status=None)
    _assert_refused_not_a_record(adoption, stage, rel, run, before, "status")


@pytest.mark.parametrize("stage", ["A5", "A7", "A10"])
def test_a_verdict_with_an_id_and_no_type_is_refused_as_not_a_record(request, stage):
    """(b): ``id`` and ``status`` but no ``type``: the message names ``type``."""
    adoption = _copy(request, stage)
    rel, run, before = _run(adoption, stage, type=None)
    _assert_refused_not_a_record(adoption, stage, rel, run, before, "type")


@pytest.mark.parametrize("stage", ["A5", "A7"])
def test_a_verdict_with_neither_type_nor_status_names_both(request, stage):
    adoption = _copy(request, stage)
    rel, run, before = _run(adoption, stage, type=None, status=None)
    _assert_refused_not_a_record(adoption, stage, rel, run, before, "type", "status")


@pytest.mark.parametrize("value", ["", 5, ["ACTIVE"]], ids=["empty", "number", "list"])
@pytest.mark.parametrize("stage", ["A5", "A7"])
def test_a_status_that_is_not_a_non_empty_string_is_refused(request, stage, value):
    """(e): ``status`` present but empty or not a string is no ``status`` the store reads."""
    adoption = _copy(request, stage)
    rel, run, before = _run(adoption, stage, status=value)
    _assert_refused_not_a_record(adoption, stage, rel, run, before, "status")


@pytest.mark.parametrize("value", ["", 7], ids=["empty", "number"])
def test_a_type_that_is_not_a_non_empty_string_is_refused(a6_copy, value):
    """(e): the same for ``type``."""
    rel, run, before = _run(a6_copy, "A7", type=value)
    _assert_refused_not_a_record(a6_copy, "A7", rel, run, before, "type")


# --------------------------------------------------------------------------
# (c), (d): a verdict the store reads, and one with no id, are accepted and never listed invalid
# --------------------------------------------------------------------------

@pytest.mark.parametrize("stage", ["A5", "A7", "A10"])
def test_a_verdict_with_id_type_and_status_is_accepted_and_the_store_reads_it(request, stage, needs_vectors):
    """(c): the adopt skill's keys (``id``, ``type``, ``status``): accepted; then ``gov rebuild`` lists no invalid
    record for the verdict (green on the base: the success side already holds; it guards the fix)."""
    adoption = _copy(request, stage)
    rel, run, _ = _run(adoption, stage)
    _assert_accepted_and_read(adoption, stage, rel, run)


@pytest.mark.parametrize("stage", ["A5", "A7"])
def test_a_verdict_with_no_id_is_still_accepted_and_listed_invalid_by_nothing(request, stage, needs_vectors):
    """(d): the skill's form has no ``id``: it is no record; the gate accepts it and rebuild lists none invalid
    (green on the base; it guards the fix against a gate that demands an ``id``)."""
    adoption = _copy(request, stage)
    rel, run, _ = _run(adoption, stage, id=None, status=None, type=None)
    _assert_accepted_and_read(adoption, stage, rel, run)


# --------------------------------------------------------------------------
# The order: the new refusal comes after every existing check (green on the base; they guard the order)
# --------------------------------------------------------------------------

def test_a_verdict_that_is_not_a_pass_keeps_its_own_refusal_whatever_its_keys(a4_copy):
    rel, run, _ = _run(a4_copy, "A5", verdict="fail", status=None)
    error = support.assert_refused(run, a4_copy.interface, rel)
    assert _code(error) == "VERDICT_NOT_PASS", f"{error.get('code')!r}\n{run.describe()}"


def test_a_verdict_of_another_stage_keeps_its_own_refusal_whatever_its_keys(a6_copy):
    rel, run, _ = _run(a6_copy, "A7", stage="A5", status=None)
    error = support.assert_refused(run, a6_copy.interface, rel)
    assert _code(error) == "VERDICT_OTHER_STAGE", f"{error.get('code')!r}\n{run.describe()}"


def test_a_verdict_not_committed_by_the_auditor_keeps_its_own_refusal_whatever_its_keys(a4_copy):
    rel, run, _ = _run(a4_copy, "A5", role=None, status=None)
    error = support.assert_refused(run, a4_copy.interface, rel)
    assert _code(error) == "VERDICT_NOT_INDEPENDENT", f"{error.get('code')!r}\n{run.describe()}"
