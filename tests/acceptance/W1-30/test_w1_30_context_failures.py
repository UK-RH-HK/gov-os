"""A ticket whose context cannot be built does not close (KPI S5 "packet hash", S6 "with whole-system context
from gov context"; DEC-454 "A context that cannot be built refuses the close"; DEC-455: it is one iteration).

``tests/acceptance/W1-24/README.md`` gives the errors ``gov context`` has for a ticket (its S5 line and its
command section):

- ``BLOCKED``: a mandatory input (an id the ticket declares in ``sources``, ``depends_on`` or ``deps``) is
  missing from the store;
- ``BLOCKED``: a declared record is superseded, by one record or by several; the error names it;
- ``CONTRADICTION``: two active records at the same precedence level, with no supersession between them.

One case each. Each first runs ``gov context`` in its project and holds that it gives that error, so the case
cannot pass on a project whose context builds. Then ``gov close`` on the ticket, which is otherwise green and
clean: refused with exit code 3, the answer says the context failed and names the record, no close record, the
ticket in progress, and the refusal counted as one iteration.

The decision checker (W1-11) being unable to run is the fifth reason. ``tests/acceptance/W1-11/README.md``: a
history the checker cannot read raises ``GovError`` (a shallow clone, DEC-387). The case holds first that the
checker raises in its project.

No record store is the sixth (DEC-470): ``gov context`` answers ``STORE_MISSING`` in a project whose store was
never loaded. The close is refused with that reason and counted, and it does not build the store itself:
after the refusal ``gov context`` still answers ``STORE_MISSING``. So every other project of this suite is
given its store by its fixture (``support.run_close`` loads it before the close, or the case does and passes
``store=False``); the cases here are the only ones that close without one.

Last, a failing close that is given a class (DEC-454: "with it, the context is built first and its hash is
recorded"): when that context cannot be built, the answer and the repair ticket say so and carry no hash.
"""

import re
import subprocess

import w1_30_support as support

TICKET = "PROJ-ctxf"
WBS = "W1-ctxf"
BASE = support.BASE_SOURCE
SHA256 = re.compile(r"\b[0-9a-f]{64}\b")


def _decisions(project, **records):
    """Write decision records ``id=(status, keys)`` and commit them as the owner."""
    for record_id, (status, keys) in records.items():
        project.add_decision(record_id.replace("_", "-"), status, **keys)
    project.commit("decision records", who=support.OWNER)


def _refused_for_the_context(project, sandbox, interface, code, *named):
    """The otherwise green ticket's context gives ``code``; the close is refused for it and counted."""
    error = support.context_error(project, sandbox, TICKET)
    assert error["code"] == code, f"the fixture is wrong: gov context gives {error}"

    run = support.run_close(project, sandbox, TICKET, store=False)
    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert "context" in text.lower(), f"the refusal does not say the context failed\n{run.describe()}"
    for record_id in named:
        assert record_id in text, f"the refusal does not name {record_id}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1, "the refusal is not counted as one iteration"


def test_a_missing_mandatory_input_refuses_the_close(project, sandbox, interface):
    """BLOCKED: the ticket names a source no record has."""
    support.build_ticket(project, TICKET, WBS, sources=["DEC-gone"])
    support.load_store(project, sandbox)
    _refused_for_the_context(project, sandbox, interface, "BLOCKED", "DEC-gone")


def test_a_missing_depends_on_id_refuses_the_close(project, sandbox, interface):
    """BLOCKED: an id under ``depends_on`` is a mandatory input too (W1-24 S4)."""
    support.build_ticket(project, TICKET, WBS, depends_on=["W1-gone"])
    support.load_store(project, sandbox)
    _refused_for_the_context(project, sandbox, interface, "BLOCKED", "W1-gone")


def test_a_superseded_source_refuses_the_close(project, sandbox, interface):
    """BLOCKED: the ticket's source is superseded; the error names it."""
    _decisions(project, DEC_old=("SUPERSEDED", {"superseded_by": "DEC-new"}),
               DEC_new=("ACTIVE", {"supersedes": ["DEC-old"]}))
    support.build_ticket(project, TICKET, WBS, sources=["DEC-old"])
    support.load_store(project, sandbox)
    _refused_for_the_context(project, sandbox, interface, "BLOCKED", "DEC-old")


def test_a_source_superseded_by_several_records_refuses_the_close(project, sandbox, interface):
    """BLOCKED: more than one record supersedes the ticket's source."""
    _decisions(project, DEC_old=("SUPERSEDED", {}),
               DEC_new1=("ACTIVE", {"supersedes": ["DEC-old"]}),
               DEC_new2=("ACTIVE", {"supersedes": ["DEC-old"]}))
    support.build_ticket(project, TICKET, WBS, sources=["DEC-old"])
    support.load_store(project, sandbox)
    _refused_for_the_context(project, sandbox, interface, "BLOCKED", "DEC-old")


def test_two_contradicting_sources_refuse_the_close(project, sandbox, interface):
    """CONTRADICTION: two active decisions among the ticket's sources, neither superseding the other."""
    _decisions(project, DEC_other=("ACTIVE", {}))
    support.build_ticket(project, TICKET, WBS, sources=[BASE, "DEC-other"])
    support.load_store(project, sandbox)
    _refused_for_the_context(project, sandbox, interface, "CONTRADICTION", BASE, "DEC-other")


def test_a_decision_checker_that_cannot_run_refuses_the_close(project, sandbox, interface, tmp_path):
    """The project is a shallow clone that holds the ticket's commits and their parents, and not the commit
    that set the ticket's source ACTIVE. W1-11's checker raises ``GovError`` there; W1-50's judgement of the
    ticket's commits still answers, with no finding."""
    support.build_ticket(project, TICKET, WBS)
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "4", "file://" + str(project.root), str(shallow)],
                   check=True, capture_output=True)
    project.root = shallow
    answer = support.decision_check(project, sandbox)
    assert "error" in answer, f"the fixture is wrong: W1-11's checker runs here and gives {answer}"
    assert support.judged_by_w1_50(project, sandbox, support.ticket_commits(project.root, TICKET)) == []

    run = support.run_close(project, sandbox, TICKET)
    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert "decision" in text.lower(), f"the refusal does not say the decisions could not be checked\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    assert support.iteration_count(project.root, TICKET) == 1, "the refusal is not counted as one iteration"


# --------------------------------------------------------------------------
# No record store (DEC-470)
# --------------------------------------------------------------------------

STORE_MISSING = "STORE_MISSING"


def _close_without_a_store(project, sandbox, interface):
    """An otherwise green ticket in a project whose record store was never loaded."""
    support.build_ticket(project, TICKET, WBS)
    error = support.context_error(project, sandbox, TICKET)
    assert error["code"] == STORE_MISSING, f"the fixture is wrong: gov context gives {error}"
    run = support.run_close(project, sandbox, TICKET, store=False)
    return run, support.refused(run, interface, support.EXIT_CHECK_FAILED), error


def test_a_project_without_a_record_store_refuses_the_close(project, sandbox, interface):
    """Refused with the context's reason: the answer says the context failed and carries the code
    ``gov context`` gives; no close record, the ticket in progress."""
    run, error, of_context = _close_without_a_store(project, sandbox, interface)
    text = support.error_text(error)
    assert "context" in text.lower(), f"the refusal does not say the context failed\n{run.describe()}"
    assert STORE_MISSING in text or of_context["message"] in text, \
        f"the refusal does not give the context's reason ({of_context})\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_refusal_for_no_record_store_is_counted(project, sandbox, interface):
    """DEC-455: the refusal is one iteration."""
    _close_without_a_store(project, sandbox, interface)
    assert support.iteration_count(project.root, TICKET) == 1, "the refusal is not counted as one iteration"


def test_a_refusal_for_no_record_store_carries_no_hash(project, sandbox, interface):
    """Nothing is recorded that was not measured: the answer carries no packet hash."""
    run, _, _ = _close_without_a_store(project, sandbox, interface)
    assert not SHA256.search(run.stdout), f"the answer carries a hash although no context was built\n{run.describe()}"


def test_the_close_does_not_build_the_record_store(project, sandbox, interface):
    """Building the store is ``gov rebuild``'s work: after the refused close the project still has none."""
    run, _, _ = _close_without_a_store(project, sandbox, interface)
    after = support.context_error(project, sandbox, TICKET)
    assert after["code"] == STORE_MISSING, \
        f"after the refused close gov context gives {after}: the close built the store\n{run.describe()}"


def test_the_same_project_closes_once_it_has_a_record_store(project, sandbox, interface):
    """The store is the only reason: the same ticket closes after the store is loaded."""
    support.build_ticket(project, TICKET, WBS)
    assert support.context_error(project, sandbox, TICKET)["code"] == STORE_MISSING
    support.load_store(project, sandbox)
    support.result_of(support.run_close(project, sandbox, TICKET, store=False), interface)


# --------------------------------------------------------------------------
# A failing close with a class, whose context cannot be built
# --------------------------------------------------------------------------

def _failing_close_with_a_class_and_no_context(project, sandbox, interface):
    _decisions(project, DEC_old=("SUPERSEDED", {"superseded_by": "DEC-new"}),
               DEC_new=("ACTIVE", {"supersedes": ["DEC-old"]}))
    support.build_ticket(project, TICKET, WBS, failing=True, sources=["DEC-old"])
    support.load_store(project, sandbox)
    assert support.context_error(project, sandbox, TICKET)["code"] == "BLOCKED"
    run = support.run_close(project, sandbox, TICKET, "--disposition", "repair", store=False)
    return run, support.refused(run, interface, support.EXIT_CHECK_FAILED)


def test_the_answer_of_a_failing_close_with_a_class_says_the_context_failed(project, sandbox, interface):
    """The answer names the failing test (the finding) and, beside it, that the context failed and why; it
    carries no hash."""
    run, error = _failing_close_with_a_class_and_no_context(project, sandbox, interface)
    text = support.error_text(error)
    assert "test_fail" in text, f"the answer does not name the failing test\n{run.describe()}"
    assert "context" in text.lower() and "DEC-old" in text, \
        f"the answer does not say the context failed for DEC-old\n{run.describe()}"
    assert not SHA256.search(run.stdout), f"the answer carries a hash although no context was built\n{run.describe()}"


def test_the_repair_ticket_of_a_failing_close_with_a_class_says_the_context_failed(project, sandbox, interface):
    """The repair ticket says the context failed and why, and carries no hash."""
    run, _ = _failing_close_with_a_class_and_no_context(project, sandbox, interface)
    repairs = support.other_tickets(project.root, TICKET)
    assert len(repairs) == 1, f"one repair ticket is expected, found {[p.name for p in repairs]}\n{run.describe()}"
    text = repairs[0].read_text(encoding="utf-8")
    assert "context" in text.lower() and "DEC-old" in text, \
        f"the repair ticket does not say the context failed for DEC-old:\n{text}"
    assert not SHA256.search(text), f"the repair ticket carries a hash although no context was built:\n{text}"
