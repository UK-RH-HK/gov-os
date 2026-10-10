"""Round 15, piece 4 (DEC-612, DEC-620): the retrieval-regression check declares its own time limit.

Measured before the round: the check's program ends green in this repository in 108 seconds on a loaded machine;
the runner's limit for a declaration that states none is 60. DEC-620: "The time limit the retrieval-regression
declaration states is 600 seconds."

That the runner holds a check to its stated limit is held since DEC-595
(``tests/acceptance/W1-15/test_w1_15_check_time_limit.py``) and is not repeated here.
"""

from __future__ import annotations

import w1_30_r15_support as r15

CHECK = "retrieval-regression"
LIMIT_S = 600
# The declaration's other fields as they stand before the round: nothing else of it changes.
AS_IT_STANDS = {
    "id": "retrieval-regression",
    "family": "retrieval-regression",
    "tier": "G1",
    "severity": "hard-block",
    "command": "python3 -m gov.retrieval.retrieve_check",
}


def test_the_declaration_states_a_limit_of_600_seconds_and_nothing_else_of_it_changes():
    """Red before the round: the declaration states no ``timeout-seconds``."""
    document = r15.kernel_declaration(CHECK)
    assert {key: document.get(key) for key in AS_IT_STANDS} == AS_IT_STANDS, \
        f"a field of the {CHECK} declaration other than its time limit changed: {document}"
    limit = document.get(r15.TIMEOUT)
    assert type(limit) is int and limit == LIMIT_S, \
        f"the {CHECK} declaration states the time limit {limit!r} (key {r15.TIMEOUT!r}); {LIMIT_S} is decided"
    assert set(document) == set(AS_IT_STANDS) | {r15.TIMEOUT}, \
        f"the {CHECK} declaration holds keys beside its five fields and its time limit: {sorted(document)}"


def test_gov_check_list_shows_the_declaration_with_its_limit_and_without_a_declaration_error(scratch, sandbox):
    """The file as the kernel template holds it, in a project: listed, not refused as a declaration that is not
    valid. Red before the round: listed without a time limit."""
    project = scratch()
    project.declare_as_the_kernel_does(CHECK)
    entries, run = r15.listed(project, sandbox)
    assert sorted(entries) == [CHECK], f"the list is not the one declaration of the project\n{run.describe()}"
    assert entries[CHECK] == {**AS_IT_STANDS, r15.TIMEOUT: LIMIT_S}, \
        f"gov check --list does not show the declaration with its limit of {LIMIT_S} seconds\n{run.describe()}"
