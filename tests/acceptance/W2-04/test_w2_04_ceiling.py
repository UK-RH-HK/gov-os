"""KPI 1 (S1; CAP-15, CAP-15.d): the packet holds its ceiling and never drops the ticket's own text.

The ceiling is ``--budget N`` or 6,000 tokens; every ``ok: true`` packet has ``tokens <= budget.limit`` and
``budget.used == tokens``, and ``tokens`` counts the ticket's own text, every mandatory input's text and every
supplementary item's text. The ticket's file text is in the packet whole and verbatim under ``ticket_text``; under
pressure the supplementary block goes first.

Red reason, today: the packet has no ``ticket_text`` and its ``tokens`` leaves the ticket's own text out.
"""

from __future__ import annotations

import pytest

import w2_04_support as s

PLAIN_TICKET = "TK-W204-PLAIN"
LARGE_TICKET = "TK-W204-LARGE"
CAP_ID, CAP_REL = "CAP-15", "docs/contract/capabilities/CAP-15.md"
CHARTER_REL = "docs/charter/charter.md"
# A body of about 4,000 tokens: large, yet the ticket and its one small source fit the default ceiling.
LARGE_BODY = "\n".join(f"Paragraph {n}: the harbour master reads every line of this ticket before the tide turns."
                       for n in range(190))


@pytest.fixture(scope="module")
def plain(api, tmp_path_factory):
    """No lexical index: the packet holds the ticket and its mandatory inputs, nothing supplementary."""
    files = {
        CHARTER_REL: s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT),
        CAP_REL: s.record(CAP_ID, "capability", "ACCEPTED", "The context packet is compiled and bounded."),
        f".tickets/{PLAIN_TICKET}.md": s.ticket(PLAIN_TICKET, "The plain ticket", [s.CHARTER_ID, CAP_ID]),
        f".tickets/{LARGE_TICKET}.md": s.ticket(LARGE_TICKET, "The large ticket", [s.CHARTER_ID], body=LARGE_BODY),
    }
    project = s.build_project(tmp_path_factory.mktemp("w2-04-plain") / "repo", files)
    api.build(project.root, index=False)
    return project


def test_the_packet_carries_the_tickets_own_text_whole_and_verbatim(api, plain):
    packet = api.gov(plain.root, PLAIN_TICKET).packet
    assert packet.get(s.K_TICKET_TEXT) == plain.text(f".tickets/{PLAIN_TICKET}.md"), \
        f"`{s.K_TICKET_TEXT}` is not the ticket's file text, front matter and body: {packet.get(s.K_TICKET_TEXT)!r}"


def test_tokens_count_the_tickets_text_and_every_mandatory_input(api, plain):
    """With nothing supplementary, ``tokens`` is the ticket's text and its two mandatory files, each counted as the
    packet counts (each text alone, or their sum: both roundings are taken)."""
    packet = api.gov(plain.root, PLAIN_TICKET).packet
    texts = [plain.text(f".tickets/{PLAIN_TICKET}.md"), plain.text(CHARTER_REL), plain.text(CAP_REL)]
    assert packet[s.K_SUPPLEMENTARY] == [], f"the fixture is wrong: no index, yet supplementary items: {packet}"
    low, high = s.tokens("".join(texts)), sum(s.tokens(text) for text in texts)
    assert low <= packet[s.K_TOKENS] <= high, (
        f"tokens is {packet[s.K_TOKENS]}; the ticket's text and its mandatory inputs are {low} to {high} "
        f"(the ticket's text alone is {s.tokens(texts[0])})")
    assert packet[s.K_BUDGET] == {"limit": s.DEFAULT_CEILING, "used": packet[s.K_TOKENS]}, packet[s.K_BUDGET]


def test_a_large_ticket_whose_total_fits_is_served_whole(api, plain):
    text = plain.text(f".tickets/{LARGE_TICKET}.md")
    assert 3500 < s.tokens(text) < s.DEFAULT_CEILING - 500, f"the fixture is wrong: {s.tokens(text)} tokens"
    packet = api.gov(plain.root, LARGE_TICKET).packet
    s.assert_holds_its_ceiling(packet, text)
    assert packet[s.K_BUDGET]["limit"] == s.DEFAULT_CEILING


@pytest.mark.parametrize("share", (None, 0.5, 0.0), ids=("default ceiling", "half the supplementary room",
                                                         "no supplementary room"))
def test_under_pressure_supplementary_goes_first_and_the_ticket_text_stays_whole(retrieval_api, ledger, share):
    """The ledger ticket at the default ceiling (everything fits), then with ``--budget`` leaving room for half of
    its supplementary items, then for none: each packet holds its ceiling, its mandatory input and the ticket's whole
    text; only the supplementary block shrinks."""
    text = ledger.text(f".tickets/{s.LEDGER_TICKET}.md")
    full = retrieval_api.gov(ledger.root, s.LEDGER_TICKET).packet
    s.assert_holds_its_ceiling(full, text)
    assert full[s.K_SUPPLEMENTARY], f"the fixture is wrong: nothing supplementary at the default ceiling: {full}"
    if share is None:
        return
    mandatory = full[s.K_TOKENS] - s.supplementary_tokens(full)
    budget = mandatory + int(s.supplementary_tokens(full) * share)

    packet = retrieval_api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget).packet

    s.assert_holds_its_ceiling(packet, text)
    assert packet[s.K_BUDGET]["limit"] == budget
    assert [item["id"] for item in packet[s.K_MANDATORY]] == [item["id"] for item in full[s.K_MANDATORY]], \
        "a mandatory input was dropped under pressure; supplementary context goes first (CAP-15.d)"
    assert len(packet[s.K_SUPPLEMENTARY]) < len(full[s.K_SUPPLEMENTARY]), \
        f"with a budget of {budget} the supplementary block did not shrink"
    if share == 0.0:
        assert packet[s.K_SUPPLEMENTARY] == [] and packet[s.K_TOKENS] == mandatory, packet[s.K_TOKENS]


DEP_TICKET, WITH_DEP = "TK-W204-DEP", "TK-W204-WITHDEP"
DEP_KPI = "The dependency's own work is done."
# A body of about 40,000 tokens: alone far over the default ceiling, counted whole.
DEP_BODY = "\n".join(f"Paragraph {n}: the dependency's long history, kept in its body and read by no one here."
                     for n in range(1800))


def _dep(body=DEP_BODY, kpi=DEP_KPI):
    return s.ticket(DEP_TICKET, "The dependency ticket", [s.CHARTER_ID], kpis=(kpi,), body=body)


def test_a_dependency_ticket_is_counted_by_its_front_matter_so_a_large_body_still_fits(api, tmp_path):
    """The addendum's S1 (DEC-1005, P-W2-04-3 (b); CAP-15.b). A ticket that names a dependency in its ``deps``: the
    dependency counts by its front matter only (its id, status, title and KPI lines), never its whole file, and keeps
    its file's sha256 (S3). A dependency whose body is about 40,000 tokens still fits the default ceiling; a change to
    its body alone leaves the packet's ``tokens`` unchanged and changes its sha256 to its new file's; a change to its
    KPI lines is counted. The ticket's own text is still whole and counted whole."""
    files = {CHARTER_REL: s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT),
             f".tickets/{DEP_TICKET}.md": _dep(),
             f".tickets/{WITH_DEP}.md": s.ticket(WITH_DEP, "The ticket with a dependency", [s.CHARTER_ID],
                                                 deps=[DEP_TICKET])}
    project = s.build_project(tmp_path / "repo", files)
    api.build(project.root, index=False)
    dep_rel, text = f".tickets/{DEP_TICKET}.md", project.text(f".tickets/{WITH_DEP}.md")
    assert s.tokens(project.text(dep_rel)) > 6 * s.DEFAULT_CEILING, "the fixture is wrong: a small dependency"

    answer = api.gov(project.root, WITH_DEP)
    assert answer.envelope["ok"] is True, f"a dependency with a large body does not fit\n{answer.describe()[:1500]}"
    before = answer.packet
    s.assert_holds_its_ceiling(before, text)
    assert s.item_of(before, DEP_TICKET)["sha256"] == s.sha256_file(project.root / dep_rel), \
        f"{DEP_TICKET} is not named by its file's sha256"

    project.write(dep_rel, _dep(body=DEP_BODY.replace("long history", "longer history, told again,")))
    project.commit("the dependency's body changes")
    api.load(project.root)
    after = api.gov(project.root, WITH_DEP).packet
    assert after[s.K_TOKENS] == before[s.K_TOKENS], \
        f"a change to the dependency's body alone changed tokens: {before[s.K_TOKENS]} -> {after[s.K_TOKENS]}"
    assert s.item_of(after, DEP_TICKET)["sha256"] == s.sha256_file(project.root / dep_rel) != \
        s.item_of(before, DEP_TICKET)["sha256"], f"{DEP_TICKET}'s sha256 is not its new file's"

    project.write(dep_rel, _dep(kpi=DEP_KPI + " " + "Every line of its work is checked twice. " * 20))
    project.commit("the dependency's KPI line grows")
    api.load(project.root)
    grown = api.gov(project.root, WITH_DEP).packet
    s.assert_holds_its_ceiling(grown, text)
    assert grown[s.K_TOKENS] > after[s.K_TOKENS], \
        f"the dependency's KPI lines grew by about 200 tokens and tokens did not: {after[s.K_TOKENS]}"


def test_the_function_holds_the_ceiling_as_the_command_does(api, plain):
    """``gov.context.context`` in a process of its own gives the packet the command gives."""
    (out,) = api.context_calls(plain.root, PLAIN_TICKET)
    assert "value" in out, f"gov.context.context refused: {out}"
    s.assert_holds_its_ceiling(out["value"], plain.text(f".tickets/{PLAIN_TICKET}.md"))
    assert out["value"][s.K_HASH] == api.gov(plain.root, PLAIN_TICKET).packet[s.K_HASH]
