"""W1-25 -- the mandatory triggers: ticket transition, compaction, stop.

- KPI success 1 [CAP-37.b]: "... is written at every ticket transition,
  compaction and stop".
- KPI failure 1: "A ticket transition leaves no checkpoint".

Recommended option of DP-4. The hooks that call the command at a compaction and
a stop (W1-29, W1-49) and ``gov close`` (W1-30) do not exist on this branch, so
this ticket shows two things: the command writes a checkpoint for each trigger
and records which one, and the watchdog reports a ticket whose transition left
no checkpoint. Another answer to DP-4 changes this file only.
"""

from __future__ import annotations

import pytest

import w1_25_support as support

cli_support = support.cli_support


def _watch(gov, ticket=support.TICKET):
    return gov("checkpoint", "--watch", "--ticket", ticket, *support.LOOSE, "--json")


@pytest.mark.parametrize("trigger", support.TRIGGERS)
def test_each_mandatory_trigger_writes_a_checkpoint_that_records_it(checkpoint, trigger):
    document = support.frontmatter(checkpoint(trigger=trigger))
    assert document.get(support.KEY_TRIGGER) == trigger, document


def test_a_trigger_outside_the_list_is_refused(project, gov, interface):
    before = support.state(project)
    run = gov(*support.write_args(trigger="whenever"))
    support.refused(run, interface, exit_codes=(1, 2))
    assert support.state(project) == before, run.describe()


def test_a_ticket_in_progress_with_no_checkpoint_is_reported(gov, interface):
    """KPI failure 1: the transition to in_progress left no checkpoint."""
    error = support.refused(_watch(gov), interface, exit_codes=(support.EXIT_UNHEALTHY,))
    assert error["code"] == support.MISSING, error


def test_a_transition_after_the_latest_checkpoint_marks_it_stale(project, gov, interface, checkpoint):
    """KPI failure 1: the ticket moved on (its status changed) and no checkpoint followed."""
    checkpoint(trigger="stop")
    support.succeeded(_watch(gov), interface)
    support.set_ticket_status(project, "closed")
    error = support.refused(_watch(gov), interface, exit_codes=(support.EXIT_UNHEALTHY,))
    assert error["code"] == support.STALE, error
    assert support.REASON_TRANSITION in support.reasons(error), error


def test_a_checkpoint_at_the_transition_clears_it(project, gov, interface, checkpoint):
    checkpoint(trigger="stop")
    support.set_ticket_status(project, "closed")
    checkpoint(trigger="ticket-transition")
    result = support.succeeded(_watch(gov), interface)
    assert result.get("stale") is False, result


def test_another_tickets_checkpoint_does_not_cover_the_transition(gov, interface, checkpoint):
    """Per ticket: a checkpoint of one ticket says nothing about another."""
    checkpoint(ticket=support.OTHER_TICKET)
    error = support.refused(_watch(gov, support.TICKET), interface, exit_codes=(support.EXIT_UNHEALTHY,))
    assert error["code"] == support.MISSING, error
