"""Interface I2, the three defaults of Stage A0 (part of KPI success 1).

(i) a roster that already names an existing ticket: A0 keeps it and creates nothing;
(ii) a roster without the key: A0 adds the key and changes nothing else;
(iii) ``tk`` missing: A0 completes without creating the ticket or the key, and its record says so; the guard stays closed
      (every install refused, the refusal naming ``GOV_TICKET`` and how to set the key) (PKG-3 (b), the owner, DEC-1157
      (15); was: A0 refuses and writes nothing).

In (iii) A0 ends as W2-23's success does (exit 0, an ``ok: true`` envelope). "Its record says so" is judged on the
record's text, not on a field name (``w2_113_support.says_no_ticket_was_created_because_tk_is_missing``; README, "The
record says so"). "The guard stays closed" is the kernel hook's decision, as the rest of the suite reads it.
"""

from __future__ import annotations

import pytest
import yaml

import w2_113_support as support
from w2_113_support import w110

w23 = support.w23


# --- (i) a roster that already names an existing ticket -----------------------------------------------------------------

@pytest.mark.parametrize("name,named", [("names-by-id", support.OTHER.id), ("names-by-wbs", support.OTHER.wbs)])
def test_a_roster_that_names_an_existing_ticket_is_kept_and_no_ticket_is_created(adoption, name, named):
    adopted = adoption(name)
    support.assert_succeeded(adopted)
    assert adopted.created == set(), (
        f"the roster already names the existing ticket {named}: A0 creates no ticket; it added {sorted(adopted.created)}")
    assert adopted.key() == named, f"A0 changed the key {support.KEY}: it was {named!r}, it is {adopted.key()!r}"
    assert support.roster_data(adopted.project) == yaml.safe_load(adopted.before.roster.decode("utf-8")), \
        "A0 changed the roster's content although it already named an existing ticket"
    assert w23.porcelain(adopted.project) == "", "A0 left the tree dirty"


@pytest.mark.parametrize("name,named", [("names-by-id", support.OTHER.id), ("names-by-wbs", support.OTHER.wbs)])
def test_the_ticket_a_roster_names_stays_the_ctos(adoption, name, named, sandbox):
    """The kept key still decides: the orchestrator on the ticket the roster named is asked, a worker is refused."""
    adopted = adoption(name)
    support.assert_succeeded(adopted)
    settings = w110.wiring.load_settings(adopted.project)
    asked = w110.call(adopted.project, settings, sandbox, w110.cto(support.OTHER.id, "cto"), support.INSTALL)
    assert asked.decision == "ask", f"the orchestrator on {support.OTHER.id} (named by the roster) was {asked.decision}: {asked.describe()}"
    worker = w110.Session("engineer", w110.ENGINEER, support.ENGINEERING.id)
    refused = w110.call(adopted.project, settings, sandbox, worker, support.INSTALL)
    assert refused.decision == "deny", f"an engineer was {refused.decision}: {refused.describe()}"


# --- (ii) a roster with other content and no key -----------------------------------------------------------------------

def test_a_roster_without_the_key_gets_the_key_of_a_new_ticket(adoption):
    adopted = adoption("other-content")
    support.assert_succeeded(adopted)
    ticket = adopted.new_ticket()
    assert adopted.key() == ticket, f"the key must be the new ticket {ticket!r}; it is {adopted.key()!r}"


def test_a_roster_without_the_key_changes_nothing_else(adoption):
    """The roster, parsed, less the key, is what it was: every other key and value, nothing added, nothing dropped."""
    adopted = adoption("other-content")
    support.assert_succeeded(adopted)
    before = yaml.safe_load(adopted.before.roster.decode("utf-8"))
    after = support.roster_data(adopted.project)
    assert isinstance(after, dict), f"the roster does not parse as a mapping after A0: {after!r}"
    assert support.KEY not in before, "the planted roster already held the key"
    assert support.KEY in after, f"A0 did not add {support.KEY} to the roster"
    assert {k: v for k, v in after.items() if k != support.KEY} == before, (
        f"A0 changed more than the key: before {before!r}, after (less the key) "
        f"{ {k: v for k, v in after.items() if k != support.KEY} !r}")


def test_a_roster_without_the_key_keeps_its_text_and_its_comments(adoption):
    """The stricter reading of "changes nothing else": every line of the roster's text, comments and blank lines
    included, is still there, in its order; the key's line is the only addition. (README, "Readings stated".)"""
    adopted = adoption("other-content")
    support.assert_succeeded(adopted)
    original = adopted.before.roster.decode("utf-8").split("\n")
    now = (adopted.project / support.ROSTER_REL).read_text(encoding="utf-8").split("\n")
    remaining = iter(now)
    missing = [line for line in original if line.strip() and line not in remaining]
    assert not missing, (
        f"A0 rewrote the roster instead of adding the key: these original lines are gone or moved: {missing}\n"
        f"the roster now:\n" + "\n".join(now))
    extra = [line for line in now if line.strip() and line not in original]
    assert len(extra) == 1 and extra[0].lstrip().startswith(f"{support.KEY}:"), (
        f"the key's line must be the only line A0 adds; it added {extra}")


# --- (iii) tk missing: A0 completes without the ticket or the key, says so, and the guard stays closed -----------------

def test_a0_completes_without_a_ticket_or_a_key_and_its_record_says_so_when_tk_is_missing(adoption):
    adopted = adoption("no-tk")
    project, before = adopted.project, adopted.before
    assert not (project / support.TK_REL).exists(), "the planted repository still holds the vendored tk"
    support.assert_succeeded(adopted)                     # PKG-3 (b): A0 completes, it does not refuse
    assert adopted.created == set(), f"A0 created a ticket although tk is missing: {sorted(adopted.created)}"
    assert support.roster_bytes(project) == before.roster, (
        f"A0 changed {support.ROSTER_REL} (it had {before.roster!r}): with tk missing no {support.KEY} key is added")
    record = project / support.A0_RECORD
    assert record.is_file(), f"A0 completed but left no record at {support.A0_RECORD}"
    text = record.read_text(encoding="utf-8")
    assert support.says_no_ticket_was_created_because_tk_is_missing(text), (
        f"A0's record {support.A0_RECORD} must say that no coordination ticket was created because tk is missing "
        f"(it must name tk and say a ticket was not made); the record reads:\n{text}")


def test_the_guard_stays_closed_when_tk_is_missing(adoption, sandbox):
    """No key was written, so the install rule cannot run: every session's install is refused (fail closed), and the
    refusal names ``GOV_TICKET`` and says how to set the key, as KPI success 2 asks of every such refusal."""
    adopted = adoption("no-tk")
    support.assert_succeeded(adopted)
    project = adopted.project
    settings = w110.wiring.load_settings(project)
    sessions = [w110.cto(support.OTHER.id, "orchestrator on an existing ticket"),
                w110.cto(w110.COORDINATION.id, "orchestrator on a would-be coordination ticket"),
                w110.Session("orchestrator with no ticket", w110.ORCHESTRATOR, None),
                w110.Session("engineer", w110.ENGINEER, support.ENGINEERING.id)]
    problems = []
    for session in sessions:
        for command in support.INSTALLS:
            answer = w110.call(project, settings, sandbox, session, command)
            if answer.decision != "deny":
                problems.append(f"{session}: `{command}` was {answer.decision}, not refused: {answer.describe()}")
                continue
            if not support.names_the_variable(answer.reason):
                problems.append(f"{session}: the refusal of `{command}` does not name {support.NAMES_THE_VARIABLE}: "
                                f"{answer.reason!r}")
            if not support.says_how_to_set_the_key(answer.reason):
                problems.append(f"{session}: the refusal of `{command}` does not say how to set the key (name "
                                f"{support.ROSTER_REL} and {support.KEY}): {answer.reason!r}")
    assert not problems, "with tk missing the guard must stay closed:\n" + "\n".join(problems)
    assert w23.porcelain(project) == "", f"A0 left the tree dirty:\n{w23.porcelain(project)}"
