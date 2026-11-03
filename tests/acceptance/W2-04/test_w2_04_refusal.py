"""KPI 2 and the failure line's first half (S2; AR-1, F-M5): over the ceiling, a refusal by name, never ok.

When the ticket's own text plus its mandatory inputs alone exceed the ceiling, ``gov context`` refuses: ``ok: false``,
``CONTEXT_OVER_CEILING``, a non-zero exit, a message naming the ticket, the ceiling and the mandatory size, details
with ``ticket``, ``limit`` and ``mandatory_tokens``; with ``--brief`` no packet file is written. DAEO-03pw's shape
(seven sources, a register as large as this repository's, 814,821 tokens at the audit because each decision was
counted as the whole register) fits or refuses.

Red reason, today: ``gov context`` returns ``ok: true`` with ``tokens`` above ``budget.limit``; it has no
``CONTEXT_OVER_CEILING``; DAEO-03pw's shape counts each decision as the whole register.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_04_support as s

BIG_TICKET = "TK-W204-BIG"
SMALL_TICKET = "TK-W204-SMALL"
BIG_ID, BIG_REL = "CHARTER-W204-BIG", "docs/charter/big.md"
BIG_TEXT = " ".join(f"Clause {n}: every agent sees one packet under its ceiling." for n in range(2400))  # ~35k tokens


@pytest.fixture(scope="module")
def over(api, tmp_path_factory):
    files = {
        BIG_REL: s.record(BIG_ID, "charter", "ACTIVE", BIG_TEXT),
        "docs/charter/charter.md": s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT),
        f".tickets/{BIG_TICKET}.md": s.ticket(BIG_TICKET, "The big ticket", [BIG_ID]),
        f".tickets/{SMALL_TICKET}.md": s.ticket(SMALL_TICKET, "The small ticket", [s.CHARTER_ID]),
    }
    project = s.build_project(tmp_path_factory.mktemp("w2-04-over") / "repo", files)
    api.build(project.root, index=False)
    return project


def test_mandatory_inputs_over_the_default_ceiling_refuse_by_name(api, over):
    answer = api.gov(over.root, BIG_TICKET)
    details = s.assert_refused_over_ceiling(answer, BIG_TICKET, s.DEFAULT_CEILING)
    assert isinstance(details["mandatory_tokens"], int) and details["mandatory_tokens"] > s.DEFAULT_CEILING, details


def test_mandatory_inputs_over_a_given_budget_refuse_by_name(api, over):
    answer = api.gov(over.root, SMALL_TICKET, "--budget", 40)
    s.assert_refused_over_ceiling(answer, SMALL_TICKET, 40)


def test_the_function_refuses_with_the_named_error(api, over):
    (out,) = api.context_calls(over.root, BIG_TICKET)
    assert "error" in out, f"gov.context.context returned a packet over its ceiling: tokens " \
                           f"{(out.get('value') or {}).get(s.K_TOKENS)}"
    assert out["error"]["code"] == s.OVER_CEILING, out["error"]


def test_at_the_line_it_fits_and_one_token_over_it_refuses(api, over):
    """The packet's own count of the ticket and its mandatory input (nothing supplementary without an index) is the
    line: a ceiling one token above it or at it fits; one token below it refuses (never ok: true over the budget)."""
    line = api.gov(over.root, SMALL_TICKET).packet[s.K_TOKENS]
    text = over.text(f".tickets/{SMALL_TICKET}.md")

    for budget in (line + 1, line):
        packet = api.gov(over.root, SMALL_TICKET, "--budget", budget).packet
        s.assert_holds_its_ceiling(packet, text)
        assert packet[s.K_TOKENS] == line
    s.assert_refused_over_ceiling(api.gov(over.root, SMALL_TICKET, "--budget", line - 1), SMALL_TICKET, line - 1)


@pytest.mark.parametrize("dry_run", (False, True), ids=("brief", "brief dry run"))
def test_brief_over_the_ceiling_refuses_and_writes_no_packet_file(api, over, dry_run):
    scratch = over.root / s.SCRATCH_REL

    def files():
        return {p for p in over.root.rglob("*") if p.is_file() and ".git" not in p.relative_to(over.root).parts}

    before = files()
    answer = api.gov(over.root, BIG_TICKET, "--brief", *(["--dry-run"] if dry_run else []))
    written = sorted(str(p.relative_to(over.root)) for p in files() - before
                     if scratch in p.parents or BIG_TICKET in p.name)
    s.assert_refused_over_ceiling(answer, BIG_TICKET, s.DEFAULT_CEILING)
    assert written == [], f"a refused --brief wrote a packet file: {written}"


# --------------------------------------------------------------------------
# The failure line: DAEO-03pw's shape
# --------------------------------------------------------------------------

AUDIT_TICKET, AUDIT_DEP = "DAEO-03pw", "DAEO-gjjf"
AUDIT_DECISIONS = ("DEC-070", "DEC-088", "DEC-092", "DEC-096")
AUDIT_SOURCES = (*AUDIT_DECISIONS, "MR-4", "CAP-47", "CAP-59")
OWN_REGISTER = s.REPO_ROOT / s.REGISTER_REL


def _audit_files():
    kpis = ("A fresh read-only auditor compares the Wave 1 output with every Contract v4 W1 item and issues a verdict.",
            "The audit and repair loop runs to convergence or to three non-converging iterations [CAP-59.a].",
            "The auditor's brief states the owner's reading of MR-3.")
    front = {"deps": [AUDIT_DEP], "depends_on": [AUDIT_DEP], "class": "audit", "profile": "FULL"}
    return {
        "docs/contract/master-rules/MR-4.md": s.record("MR-4", "specification", "PROPOSED",
                                                       "Audit, discovery and impact are distinct functions."),
        "docs/contract/capabilities/CAP-47.md": s.record("CAP-47", "capability", "ACCEPTED",
                                                         "Independent adoption and audit roles."),
        "docs/contract/capabilities/CAP-59.md": s.record("CAP-59", "capability", "ACCEPTED",
                                                         "The audit and repair loop and its escalation."),
        f".tickets/{AUDIT_DEP}.md": s.ticket(AUDIT_DEP, "The work the audit reads", ["CAP-47"]),
        f".tickets/{AUDIT_TICKET}.md": s.ticket(AUDIT_TICKET, "Wave 1 exit audit", AUDIT_SOURCES, kpis=kpis,
                                                failure=("The auditor authored any audited file.",
                                                         "A W1 contract item has no finding row."), **front),
    }


def _audit_register():
    """A register at least as large as this repository's: its four cited decisions short, among fillers."""
    size = OWN_REGISTER.stat().st_size if OWN_REGISTER.is_file() else 1_600_000
    cited = [s.entry(dec, f"The audit's decision {dec}", f"The text of {dec}: the auditor is a fresh session.")
             for dec in AUDIT_DECISIONS]
    fillers = s.filler_entries(200, size // 2000 + 1, 2000)
    return s.register(*cited[:2], *fillers[:len(fillers) // 2], *cited[2:], *fillers[len(fillers) // 2:])


@pytest.fixture(scope="module")
def audit(retrieval_api, tmp_path_factory):
    project = s.build_project(tmp_path_factory.mktemp("w2-04-audit") / "repo", _audit_files(), _audit_register())
    retrieval_api.build(project.root)
    return project


def test_daeo_03pw_shape_fits_or_refuses(retrieval_api, audit):
    register_bytes = (audit.root / s.REGISTER_REL).stat().st_size
    assert register_bytes >= min(OWN_REGISTER.stat().st_size if OWN_REGISTER.is_file() else 0, 1_500_000), \
        f"the fixture is wrong: the planted register is {register_bytes} bytes"
    answer = retrieval_api.gov(audit.root, AUDIT_TICKET)
    envelope = answer.envelope
    if envelope["ok"] is False:
        s.assert_refused_over_ceiling(answer, AUDIT_TICKET, s.DEFAULT_CEILING)
        return
    packet = answer.packet
    assert packet[s.K_TOKENS] <= packet[s.K_BUDGET]["limit"] == s.DEFAULT_CEILING, (
        f"DAEO-03pw's shape: ok: true with tokens {packet[s.K_TOKENS]} over the ceiling of "
        f"{packet[s.K_BUDGET]['limit']} (each decision counted as the whole register?)")
    s.assert_holds_its_ceiling(packet, audit.text(f".tickets/{AUDIT_TICKET}.md"))
    assert {item["id"] for item in packet[s.K_MANDATORY]} >= set(AUDIT_SOURCES), packet[s.K_MANDATORY]


@pytest.mark.local_only
def test_this_repositorys_daeo_03pw_fits_or_refuses(api):
    """This tree's own DAEO-03pw on this tree's own store, read and never rebuilt (README: it needs the store the
    lead rebuilds before verification). Skips where the tree has no store."""
    store = s.REPO_ROOT / s.STORE_REL
    ticket_file = s.REPO_ROOT / ".tickets" / f"{AUDIT_TICKET}.md"
    if not store.is_file() or not ticket_file.is_file():
        pytest.skip(f"this tree has no store ({s.STORE_REL}) or no {AUDIT_TICKET}; the lead's rebuild makes one")
    answer = api.gov(s.REPO_ROOT, AUDIT_TICKET)
    if answer.envelope["ok"] is False:
        s.assert_refused_over_ceiling(answer, AUDIT_TICKET, s.DEFAULT_CEILING)
        return
    packet = answer.packet
    assert packet[s.K_TOKENS] <= packet[s.K_BUDGET]["limit"], \
        f"{AUDIT_TICKET}: ok: true with tokens {packet[s.K_TOKENS]} over {packet[s.K_BUDGET]['limit']}"
    s.assert_holds_its_ceiling(packet, Path(ticket_file).read_text(encoding="utf-8"))
