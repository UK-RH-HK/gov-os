"""Round 15 (DEC-614, DEC-620): a ticket's ``depends_on`` in either form of the id.

DEC-620: after the round's merge the tickets' ``depends_on`` are rewritten from work-breakdown ids to record ids,
and "the round's test designer brings the acceptance cases that read a real ticket file's ``depends_on`` to hold
under both forms."

Two existing cases read a real ticket's ``depends_on``:

- ``test_no_install_is_recorded_before_w1_05`` of W1-01's suite compared the list with a work-breakdown id. It is
  rewritten there to take either id of the same ticket.
- ``test_the_committed_tickets_validate_against_the_ticket_schema`` of W1-08's suite validates every committed
  ticket against the kernel template's ticket schema. Its words need no change, but the schema it reads allows
  only work-breakdown ids under ``depends_on``, so it would turn red with the rewrite of the tickets. The case
  below holds the schema to both forms now, so that it does not. It is the one thing of this file that asks the
  round for a change, and the README returns it as a package (the alternative is to leave the schema and change
  it with the rewrite).

The case needs ``check-jsonschema`` as W1-08's cases do, and is skipped where it is not installed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_W1_08 = str(Path(__file__).resolve().parent.parent / "W1-08")
if _W1_08 not in sys.path:
    sys.path.insert(0, _W1_08)

import w1_08_support as schema_support  # noqa: E402

A_WBS_ID, A_TICKET_ID = "W1-05", "DAEO-2lwj"
NOT_AN_ID = "not an id of a ticket!"


def test_the_ticket_schema_accepts_a_dependency_in_either_form_of_the_id(tmp_path):
    """Red before the round: a ticket id under ``depends_on`` is refused."""
    if schema_support.validator_path() is None:
        pytest.skip(f"{schema_support.VALIDATOR} is not installed on this machine")
    check = schema_support.Checker(tmp_path)
    schema = schema_support.schema_path("ticket")
    _, good = schema_support.template("ticket")
    check.accepts(schema, schema_support.replaced(good, "depends_on", [A_WBS_ID]),
                  f"a ticket that depends on {A_WBS_ID}")
    check.refuses(schema, schema_support.replaced(good, "depends_on", [NOT_AN_ID]),
                  f"a ticket that depends on {NOT_AN_ID!r}")
    check.accepts(schema, schema_support.replaced(good, "depends_on", [A_TICKET_ID, A_WBS_ID]),
                  f"a ticket that depends on {A_TICKET_ID} and on {A_WBS_ID}")
