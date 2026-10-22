"""KPI success line 1, the adoption verdict [AR-9, W2-M317], as DEC-741 I (ii) types it: the three CAP-44.h
values and a required list of named conditions, each with its name, its source item and its state (``met``,
``not met`` or ``accepted``); an ``accepted`` condition names the owner entry (a DEC id) that accepts it (DEC-741
answer F). The schema states the shape only: whether the verdict agrees with its conditions is W2-52's and W2-28's,
and is not held here.

The keys are found in the verdict type's schema by content (``support.the_condition_keys``; see the README). A
well-formed verdict with its conditions passes in ``test_w2_02_record_types.py``. Each case here writes that
well-formed record beside the one it breaks, in the same project, and holds both: the twin has no finding, the
broken record has a finding that names the conditions field, and the check is not green.
"""

from __future__ import annotations

import pytest

import w2_02_support as support

GOOD_REL = "docs/adoption/AV-0001.md"
BAD_REL = "docs/adoption/AV-0002.md"


@pytest.fixture
def project(tmp_path):
    made = support.Project(tmp_path)
    made.kernel_schemas()
    return made


def _the_verdict():
    """``(record type, verdict field, condition keys)`` of the kernel's adoption verdict; fails the case (not its
    setup) when the schema states none."""
    record_type, field = support.the_verdict_type()
    return record_type, field, support.the_condition_keys()


def _record(record_id, verdict, value, conditions):
    record_type, field, keys = verdict
    front = support.shared(record_id, record_type, status="ACCEPTED", state_class="EVIDENCE", **{field: value})
    if conditions is not ...:
        front[keys["conditions"]] = conditions
    return support.markdown(front, "# The adoption verdict\n\nThe conditions behind it.\n")


def _refused(project, verdict, value, conditions):
    """Write the well-formed twin and the broken record; hold the twin clean, the broken one refused on the
    conditions field, and the check not green."""
    _, _, keys = verdict
    project.write(GOOD_REL, _record("AV-0001", verdict, value, support.conditions_for(keys, value)))
    project.write(BAD_REL, _record("AV-0002", verdict, value, conditions))
    code, findings = project.core_schema()
    good = support.about(findings, GOOD_REL)
    assert not good, f"the well-formed twin is a finding, so the case says nothing: {good}"
    found = [finding for finding in support.about(findings, BAD_REL)
             if support.names_field_or_part(finding, keys["conditions"])]
    assert found, (f"the verdict record is not refused on {keys['conditions']!r}: "
                   f"{support.about(findings, BAD_REL)}")
    assert code != 0, f"core-schema exits {code} on a verdict record whose conditions are not well formed"


# --------------------------------------------------------------------------
# The list is required and is a list of named conditions
# --------------------------------------------------------------------------

def test_the_verdict_schema_types_its_list_of_named_conditions():
    """The one adoption-verdict schema has a list property whose items have a state of exactly ``met``,
    ``not met`` and ``accepted``, a name, a source item and an owner entry with a decision id's grammar, and it
    requires that list. Red today: ``conditions`` is optional and unconstrained."""
    keys = support.the_condition_keys()
    schema = next(iter(support.verdict_schemas().values()))[0]
    assert keys["conditions"] in support.required_of(schema), \
        f"the adoption-verdict schema does not require {keys['conditions']!r}"


@pytest.mark.parametrize("conditions", (..., "all met"), ids=("missing", "a-text-not-a-list"))
def test_a_verdict_record_without_its_list_of_conditions_is_refused(project, conditions):
    """No conditions at all, or a text where the list goes. Red today: the verdict schema types no list of
    conditions (the case fails at finding its keys)."""
    _refused(project, _the_verdict(), "ADOPTED_HEALTHY", conditions)


# --------------------------------------------------------------------------
# Each condition has its name, its source item and its state
# --------------------------------------------------------------------------

@pytest.mark.parametrize("part", ("name", "source", "state"), ids=("name", "source-item", "state"))
def test_a_condition_missing_its_name_source_item_or_state_is_refused(project, part):
    """One ``met`` condition of a not-adopted verdict without that part. Red today: the verdict schema types no
    list of conditions."""
    verdict = _the_verdict()
    _, _, keys = verdict
    conditions = support.conditions_for(keys, "NOT_ADOPTED_HEALTHY")
    del conditions[0][keys[part]]
    _refused(project, verdict, "NOT_ADOPTED_HEALTHY", conditions)


@pytest.mark.parametrize("state", ("waived", "not_met", "Met"))
def test_a_condition_whose_state_is_not_one_of_the_three_words_is_refused(project, state):
    """A state outside ``met``, ``not met`` and ``accepted``: another word, the words joined by ``_``, another
    case. Red today: the verdict schema types no list of conditions."""
    verdict = _the_verdict()
    _, _, keys = verdict
    conditions = support.conditions_for(keys, "NOT_ADOPTED_HEALTHY")
    conditions[1][keys["state"]] = state
    _refused(project, verdict, "NOT_ADOPTED_HEALTHY", conditions)


# --------------------------------------------------------------------------
# An accepted condition names the owner entry that accepts it (DEC-741 answer F)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("owner_entry", (None, "the owner said so"), ids=("missing", "not-a-decision-id"))
def test_an_accepted_condition_without_its_owner_entry_is_refused(project, owner_entry):
    """The ``accepted`` condition of a verdict with accepted exceptions, without an owner entry or with one that
    is no DEC id. Its twin, the same condition with ``DEC-741``, passes. Red today: the verdict schema types no
    list of conditions."""
    verdict = _the_verdict()
    _, _, keys = verdict
    conditions = support.conditions_for(keys, "ADOPTED_WITH_ACCEPTED_EXCEPTIONS")
    accepted = conditions[1]
    assert accepted[keys["state"]] == "accepted"
    del accepted[keys["owner_entry"]]
    if owner_entry is not None:
        accepted[keys["owner_entry"]] = owner_entry
    _refused(project, verdict, "ADOPTED_WITH_ACCEPTED_EXCEPTIONS", conditions)
