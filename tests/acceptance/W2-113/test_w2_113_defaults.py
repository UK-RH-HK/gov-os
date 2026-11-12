"""Interface I2, the three defaults of Stage A0 (part of KPI success 1).

(i) a roster that already names an existing ticket: A0 keeps it and creates nothing;
(ii) a roster without the key: A0 adds the key and changes nothing else;
(iii) ``tk`` missing: A0 refuses and writes nothing.

The wording of the refusal in (iii) is not judged beyond I2: a refusal is the tool's own (exit code not 0, no Python
traceback, an ``ok: false`` envelope; W2-23's ``refusal``).
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


# --- (iii) tk missing: A0 refuses and writes nothing ---------------------------------------------------------------------

def test_a0_refuses_when_tk_is_missing(adoption):
    adopted = adoption("no-tk")
    assert not (adopted.project / support.TK_REL).exists(), "the planted repository still holds the vendored tk"
    error = w23.refusal(adopted.done)
    assert isinstance(error, dict) and error, f"the refusal carries no error object\n{adopted.done.describe()}"


def test_a0_writes_nothing_when_tk_is_missing(adoption):
    adopted = adoption("no-tk")
    project, before = adopted.project, adopted.before
    assert adopted.done.returncode != 0, f"A0 must refuse (a non-zero exit)\n{adopted.done.describe()}"
    assert adopted.created == set(), f"A0 created a ticket although tk is missing: {sorted(adopted.created)}"
    assert support.roster_bytes(project) == before.roster, f"A0 changed {support.ROSTER_REL} (it had {before.roster!r})"
    assert w23.head(project) == before.head and support.commit_count(project) == before.commits, "A0 made a commit"
    assert not (project / support.A0_RECORD).exists(), f"A0 left its record {support.A0_RECORD}"
    assert w23.at_head(project, support.A0_RECORD) is None, f"{support.A0_RECORD} is committed"
    assert tuple(support.refs(project)) == before.refs, f"A0 left a ref: {support.refs(project)}"
    assert w23.porcelain(project) == "", f"A0 left the tree dirty:\n{w23.porcelain(project)}"
