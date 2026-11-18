"""F2: gov discover never overwrites or half-writes; each refusal names its code and leaves git status as before."""

from __future__ import annotations

import json

import pytest

import w2_36_support as support

MISSING = "no-such-change"


def refused(run, code):
    """The run exited non-zero with ``code`` in its ``--json`` envelope: the error, as text."""
    assert run.returncode != 0, run.describe()
    envelope = run.envelope()
    assert envelope is not None and envelope.get("ok") is False, f"no refusal envelope:\n{run.describe()}"
    error = envelope.get("error") or {}
    assert error.get("code") == code, f"expected {code}:\n{run.describe()}"
    return json.dumps(error)


def test_discovering_an_existing_change_again_is_refused_and_overwrites_nothing(own_c, home):
    before, tickets, status = support.snapshot(own_c), support.tickets(own_c), support.porcelain(own_c)
    run = support.discover(own_c, support.WORDS, "--json", home=home)
    error = refused(run, "DISCOVER_EXISTS")
    assert support.CHANGE in error, error
    assert support.tickets(own_c) == tickets
    assert support.porcelain(own_c) == status
    assert support.snapshot(own_c) == before


def test_discover_with_no_words_is_refused_and_writes_nothing(own_p, home):
    before, status = support.snapshot(own_p), support.porcelain(own_p)
    run = support.discover(own_p, "--json", home=home)
    assert run.returncode != 0, run.describe()
    envelope = run.envelope() or {}
    own_usage = run.returncode == 2 and "usage: gov discover" in run.stderr and "invalid choice" not in run.stderr
    assert (envelope.get("error") or {}).get("code") == "DISCOVER_NO_WORDS" or own_usage, \
        f"neither DISCOVER_NO_WORDS nor gov discover's own usage error:\n{run.describe()}"
    assert support.porcelain(own_p) == status
    assert support.snapshot(own_p) == before


@pytest.mark.parametrize("form", [("--check", MISSING), ("--generate", MISSING),
                                  ("--ticket", MISSING, "--paths", "src/report/**")],
                         ids=["check", "generate", "ticket"])
def test_a_change_that_does_not_exist_is_refused_by_name(form, own_c, home):
    status = support.porcelain(own_c)
    run = support.discover(own_c, *form, "--json", home=home)
    error = refused(run, "DISCOVER_CHANGE_NOT_FOUND")
    assert MISSING in error, error
    assert support.porcelain(own_c) == status


def test_ticket_on_a_spec_the_check_refuses_is_refused_listing_the_lines_and_writes_no_ticket(own_c, home):
    text, line = support.VARIANTS["k2-has-no-verify"]
    (own_c / support.SPEC_REL).write_text(text, encoding="utf-8")
    tickets, status = support.tickets(own_c), support.porcelain(own_c)
    run = support.discover(own_c, "--ticket", support.CHANGE, "--paths", "src/report/**", "--json", home=home)
    error = refused(run, "DISCOVER_SPEC_NOT_READY")
    assert line in error, error
    assert support.tickets(own_c) == tickets
    assert support.porcelain(own_c) == status
