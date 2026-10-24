"""KPI 7: the probe gate's named-finding acceptance [W2-M371, DEC-790 item 2].

KPI 7: "The probe gate accepts a failed probe record whose every finding is named, with its row, in an ACCEPTED owner
decision that names the record and its probed commit; any finding not so named still refuses." W2-M371 adds: "and
the close names that decision".

The forms (README, assumptions A3 and A4): a probe record lists its findings in its frontmatter under ``findings``,
a list of finding ids. The owner's decision is an entry of the project's register (the path map's
``decision_register``, DEC-479) whose status is ``ACCEPTED (owner, …)``, committed with ``Role: owner``, and whose
text names the record (its id and its path), its probed commit (the full id) and each finding id with the list row
that accepts it.
"""

import yaml

import w2_07_support as support

TICKET, WBS = "PROJ-pfnd", "W9-pfnd"
RECORD_ID = f"PR-{TICKET}"
RECORD_REL = f"docs/probes/{TICKET}/{RECORD_ID}.md"
FINDINGS = {"F1": "W2-M901", "F2": "W2-M902"}


def _failed_probe(project):
    """A FULL ticket whose work is done and checkpointed, and its committed probe record of the final code:
    judgement ``fail``, two findings. Returns the probed commit."""
    support.create_ticket(project, TICKET, WBS, profile="FULL")
    support.work(project, TICKET, {"src/example/feature.py": "# feature\n"})
    probed = support.checkpointed(project, TICKET)
    front = {"id": RECORD_ID, "type": "probe", "status": "ACTIVE", "state_class": "NARRATIVE", "task": TICKET,
             "reviewer_session": "reviewer-001", "implementer_session": "impl-001", "reviewer_wrote_nothing": True,
             "commissioned_by": "orchestrator", "judged_by": "orchestrator", "judgement": "fail",
             "probed_commit": probed, support.PROBE_FINDINGS_KEY: list(FINDINGS)}
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# Probe record\n\n" + "".join(
        f"{n}. **{finding}.** A finding of the review.\n" for n, finding in enumerate(FINDINGS, 1))
    project.write(RECORD_REL, text)
    project.commit("probe record", who=support.ORCHESTRATOR, trailers=("Role: orchestrator",), exact=True)
    return probed


def _owner_decision(project, decision, probed, named, status=support.OWNER_ACCEPTED):
    rows = "; ".join(f"finding {finding} is row {FINDINGS[finding]}" for finding in named)
    text = (f"The probe record {RECORD_ID} (`{RECORD_REL}`) of probed commit `{probed}` failed; its findings are "
            f"accepted as rows: {rows}.")
    return project.record_decision(decision, status, text)


def test_a_failed_probe_whose_every_finding_an_accepted_owner_decision_names_lets_the_ticket_close(project, sandbox,
                                                                                                interface):
    probed = _failed_probe(project)
    _owner_decision(project, "DEC-701", probed, list(FINDINGS))

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    record = support.base.the_close_record(project, TICKET)
    assert support.names(result, "DEC-701") or support.names(record, "DEC-701"), \
        f"the close does not name the decision that accepted the probe's findings\n{run.describe()}"


def test_a_finding_the_decision_does_not_name_still_refuses(project, sandbox, interface):
    probed = _failed_probe(project)
    _owner_decision(project, "DEC-702", probed, ["F1"])

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert support.names(error, "probe") and support.names(error, "F2"), \
        f"the refusal does not name the probe finding no decision accepts\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


def test_a_decision_that_is_not_accepted_does_not_accept_the_findings(project, sandbox, interface):
    probed = _failed_probe(project)
    _owner_decision(project, "DEC-703", probed, list(FINDINGS), status=support.PROPOSED)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert support.names(error, "probe"), f"the refusal is not the probe gate's\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)
