"""W2-115 S11: READY computed from the reviewer's structured verdict block."""
from __future__ import annotations

import json

from gov.close import command

from .test_w2_115_support import TICKET, change, project

RECORD = f"docs/probes/{TICKET}/PR-1.md"
KPIS = {"success": ["one", "two"], "failure": ["three"]}


def _front(repo):
    from gov.tasks.tickets import frontmatter
    return frontmatter(repo.root / f".tickets/{TICKET}.md")


def _block(kpis):
    return "# probe\n\n```verdict\n" + json.dumps({"kpis": kpis}) + "\n```\n"


def _full(tmp_path):
    repo = project(tmp_path, profile="FULL", kpis=KPIS)
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)\n#\n"})
    return repo


def _review(repo, text, role="independent-auditor"):
    repo.commit("probe", f"Task: {TICKET}", f"Role: {role}", files={RECORD: text})


def _ok(kpi, *findings):
    return {"kpi": kpi, "verdict": "pass", "findings": list(findings)}


def _finding(scope="in", ordinary="yes", consequence="fails open"):
    return {"id": "F1", "scope": scope, "ordinary_work": ordinary, "consequence": consequence}


def test_s11_complete_verdict_with_only_harmless_findings_is_ready(tmp_path):
    repo = _full(tmp_path)
    _review(repo, _block([_ok("S1", _finding(scope="out")), _ok("S2", _finding(ordinary="no")),
                          _ok("F1", _finding(consequence="other"))]))
    got = command.review_verdict(repo.root, TICKET, _front(repo))
    assert got == {"verdict": "READY", "record": RECORD, "reasons": []}


def test_s11_an_in_scope_ordinary_fails_open_finding_blocks(tmp_path):
    for consequence in ("fails open", "loses work"):
        repo = _full(tmp_path / consequence.replace(" ", "-"))
        _review(repo, _block([_ok("S1", _finding(consequence=consequence)), _ok("S2"), _ok("F1")]))
        assert command.review_verdict(repo.root, TICKET, _front(repo))["verdict"] == command.FINDING_BLOCKS


def test_s11_a_kpi_line_marked_fail_blocks(tmp_path):
    repo = _full(tmp_path)
    _review(repo, _block([{"kpi": "S1", "verdict": "fail", "findings": []}, _ok("S2"), _ok("F1")]))
    assert command.review_verdict(repo.root, TICKET, _front(repo))["verdict"] == command.FINDING_BLOCKS


def test_s11_malformed_or_incomplete_refuses(tmp_path):
    cases = {
        "not json": "```verdict\n{kpis: [}\n```\n",
        "empty": _block([]),
        "missing line": _block([_ok("S1"), _ok("S2")]),
        "bad verdict": _block([{"kpi": "S1", "verdict": "ok"}, _ok("S2"), _ok("F1")]),
        "bad finding": _block([_ok("S1", {"id": "F1", "scope": "in"}), _ok("S2"), _ok("F1")]),
        "no block": "# probe without a verdict\n",
    }
    for name, text in cases.items():
        repo = _full(tmp_path / name.replace(" ", "-"))
        _review(repo, text)
        got = command.review_verdict(repo.root, TICKET, _front(repo))
        assert got["verdict"] == command.VERDICT_MALFORMED, (name, got)


def test_s11_a_lead_writing_over_the_reviewers_verdict_is_refused(tmp_path):
    repo = _full(tmp_path)
    _review(repo, _block([_ok("S1", _finding()), _ok("S2"), _ok("F1")]))
    _review(repo, _block([_ok("S1"), _ok("S2"), _ok("F1")]), role="orchestrator")
    got = command.review_verdict(repo.root, TICKET, _front(repo))
    assert got["verdict"] == command.VERDICT_NOT_REVIEWER


def test_s11_a_lead_editing_the_record_outside_the_block_is_not_refused(tmp_path):
    repo = _full(tmp_path)
    text = _block([_ok("S1"), _ok("S2"), _ok("F1")])
    _review(repo, text)
    _review(repo, "Moderated by the lead.\n\n" + text, role="orchestrator")
    assert command.review_verdict(repo.root, TICKET, _front(repo))["verdict"] == "READY"


def test_s11_a_verdict_never_written_by_a_reviewer_is_refused(tmp_path):
    repo = _full(tmp_path)
    _review(repo, _block([_ok("S1"), _ok("S2"), _ok("F1")]), role="engineer")
    assert command.review_verdict(repo.root, TICKET, _front(repo))["verdict"] == command.VERDICT_NOT_REVIEWER


def test_s11_a_standard_ticket_without_a_record_needs_no_review(tmp_path):
    repo = project(tmp_path)
    got = command.review_verdict(repo.root, TICKET, _front(repo))
    assert got["verdict"] == "READY" and got["record"] is None


def test_s11_a_full_ticket_without_a_record_refuses(tmp_path):
    repo = _full(tmp_path)
    assert command.review_verdict(repo.root, TICKET, _front(repo))["verdict"] == command.VERDICT_MALFORMED
