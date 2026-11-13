"""W2-129 S2 to S8: each of the six finding codes is found where the planted repository puts it, and not where it
should not be. Every run is ``gov links --since <root>`` on repository A, so every record and commit is new."""

from __future__ import annotations

import sys

import pytest
import w2_129_support as support
from w2_129_support import ARCHIVE, CONTRACT, IN_FORCE, PATH_MAP, REGISTER

T001, T002, T003, T004 = (f".tickets/DAEO-t00{n}.md" for n in (1, 2, 3, 4))
SKILL = "template/governance/kernel/skills/demo/SKILL.md"
LESSON, PLAN = "docs/lessons/L-0001.md", "docs/plan/PLAN-A.md"


class Lazy:
    """The ``since_root`` output, read on first use, so a tree with no ``gov links`` fails in the test's body."""

    def __init__(self, done):
        self._done, self._out = done, None

    def __getattr__(self, name):
        if self._out is None:
            self._out = support.Output(self._done)
        return getattr(self._out, name)


@pytest.fixture()
def out(since_root):
    return Lazy(since_root[1])


@pytest.fixture()
def repo(since_root):
    return since_root[0]["repo"]


# ------------------------------------------------------------------------------------- S2 UNMARKED_CHANGE

UNMARKED = {  # changed, changer, the form's word, whole or part (None: not stated by the tests)
    "supersedes-ids-alone": ("DEC-101", "DEC-102", "Supersedes", "whole"),
    "changes-a-part": ("DEC-103", "DEC-104", "Changes", "part"),
    "supersedes-a-part": ("DEC-109", "DEC-110", "Supersedes", "part"),
    "free-text-amended-by": ("DEC-111", "DEC-112", "amended", None),
    "archive-section-a": ("DEC-130", "DEC-131", "ARCHIVE", None),
}


@pytest.mark.parametrize("case", UNMARKED, ids=list(UNMARKED))
def test_s2_unmarked_change_names_both_ids_and_the_form(out, repo, case):
    changed, changer, form, _ = UNMARKED[case]
    found = out.of("UNMARKED_CHANGE", changed, changer)
    assert len(found) == 1, f"one UNMARKED_CHANGE naming {changed} and {changer}: {found}"
    finding = found[0]
    assert form.lower() in finding.raw.lower() or (form == "ARCHIVE" and finding.path == ARCHIVE), finding
    if form == "ARCHIVE":
        lines = set(support.entry_lines(repo, changed)) | {support.line_of(repo, ARCHIVE, f"- {changed}:")}
        assert finding.path in (REGISTER, ARCHIVE) and finding.line in lines, finding
    else:
        lines = set(support.entry_lines(repo, changed)) | set(support.entry_lines(repo, changer))
        assert finding.path == REGISTER and finding.line in lines, finding


@pytest.mark.parametrize("case", [c for c in UNMARKED if UNMARKED[c][3]], ids=[c for c in UNMARKED if UNMARKED[c][3]])
def test_s2_unmarked_change_says_whether_the_change_is_whole_or_of_a_part(out, case):
    changed, changer, _, extent = UNMARKED[case]
    found = out.of("UNMARKED_CHANGE", changed, changer)
    assert found and any(f" {extent}" in f.raw.lower() or f"({extent}" in f.raw.lower() for f in found), found


@pytest.mark.parametrize("marked", [("DEC-105", "DEC-106"), ("DEC-107", "DEC-108")], ids=["changed-by", "superseded-by"])
def test_s2_guard_an_entry_that_names_its_changer_gives_no_unmarked_change(out, marked):
    assert out.findings, "gov links gave no finding at all on the planted repository"
    assert not out.of("UNMARKED_CHANGE", *marked)


# ------------------------------------------------------------------------------------------- S3 UNKNOWN_ID

UNKNOWN = {  # the id (or path) named, the place, the needle of its line (None: a commit's trailer)
    "ticket-sources": ("DEC-998", T001, "- DEC-998"),
    "ticket-links": ("DAEO-gone", T001, "links: [DAEO-gone]"),
    "ticket-acceptance-path": ("tests/acceptance/W2-901", T001, "path: tests/acceptance/W2-901/"),
    "register-label-under": ("DEC-999", REGISTER, "**Under:** DEC-999"),
    "commit-task": ("DAEO-zzzz", None, None),
    "commit-implements": ("DEC-997", None, None),
    "contract-provider": ("W9-999", CONTRACT, "- W9-999"),
    "lesson-constrains": ("DAEO-nope", LESSON, "constrains:"),
    "lesson-sources": ("DEC-992", LESSON, "sources:"),
    "plan-decisions": ("DEC-993", PLAN, "decisions:"),
    "checkpoint-task": ("DAEO-qqqq", "docs/checkpoints/DAEO-t001/CP-DAEO-t001-0002.md", "task: DAEO-qqqq"),
    "kernel-skill-line": ("DEC-991", SKILL, "(DEC-991)"),
    "test-file-id": ("DEC-995", "tests/unit/test_limits.py", "DEC-995"),
}


@pytest.mark.parametrize("case", UNKNOWN, ids=list(UNKNOWN))
def test_s3_unknown_id_in_each_typed_place(out, repo, case):
    named, path, needle = UNKNOWN[case]
    found = [f for f in out.findings if f.code == "UNKNOWN_ID" and named in f.head and (path is None or f.path == path)]
    assert found, f"no UNKNOWN_ID naming {named} at {path}"
    if needle:
        lines = {support.line_of(repo, path, needle)}
        if case == "ticket-acceptance-path":
            lines.add(support.line_of(repo, path, "acceptance_tests:"))
        assert any(f.line in lines for f in found), (lines, found)


@pytest.mark.parametrize("named", ["decision-record", "W2-L001", "DAEO-t002", "W2-901", "W2-902", "DEC-100",
                                   "DEC-113"])
def test_s3_guard_what_exists_is_no_unknown_id(out, named):
    assert out.findings, "gov links gave no finding at all on the planted repository"
    assert not [f for f in out.findings if f.code == "UNKNOWN_ID" and f.names(named)]


@pytest.mark.parametrize("path", [T002, T004], ids=["closed-ticket-paths-exist", "open-ticket-not-judged"])
def test_s3_guard_no_unknown_id_in_a_ticket_whose_typed_places_resolve_or_are_not_judged(out, path):
    """DAEO-t002's acceptance path exists and its W2-L001 is a row of the list file; DAEO-t004 is open, so its
    missing acceptance path is not judged (the KPI's typed places are in-progress and closed tickets')."""
    assert out.findings, "gov links gave no finding at all on the planted repository"
    assert not [f for f in out.findings if f.code == "UNKNOWN_ID" and f.path == path]


# ------------------------------------------------------------------------------------------ S4 UNLINKED_ID

def test_s4_unlinked_id_from_a_kpi_bracket(out, repo):
    for rid, needle in (("DEC-104", "[DEC-100, DEC-104]"), ("DEC-121", "[DEC-121]")):
        found = [f for f in out.of("UNLINKED_ID", rid) if f.path == T001]
        assert found, f"no UNLINKED_ID for {rid} at {T001}"
        lines = {support.line_of(repo, T001, needle), support.line_of(repo, T001, "sources:")}
        assert any(f.line in lines for f in found), (lines, found)


def test_s4_unlinked_id_from_a_worker_commit_s_implements(out):
    found = [f for f in out.of("UNLINKED_ID", "DEC-105") if f.path == T001 or "DAEO-t001" in f.raw]
    assert found, "no UNLINKED_ID for DEC-105 (Implements: of an engineer's commit for DAEO-t001)"


@pytest.mark.parametrize("rid", ["DEC-100", "DEC-113", "DEC-120"],
                         ids=["linked-in-sources", "landing-commit-implements", "worker-implements-in-sources"])
def test_s4_guard_no_unlinked_id_for_a_linked_id_or_a_landing_commit(out, rid):
    assert out.findings, "gov links gave no finding at all on the planted repository"
    assert not out.of("UNLINKED_ID", rid)


# -------------------------------------------------------------------------------------- S5 STATUS_CONFLICT

CONFLICTS = {
    "register-current-archive-spent": ("DEC-132", (REGISTER, ARCHIVE)),
    "in-force-list-register-superseded": ("DEC-107", (IN_FORCE, REGISTER)),
    "ticket-against-its-close-record": ("DAEO-t003", (T003, "docs/close/DAEO-t003/CL-DAEO-t003.md")),
    "mr-record-against-contract-yaml": ("MR-1", ("docs/contract/master-rules/MR-1.md", CONTRACT)),
}


@pytest.mark.parametrize("case", CONFLICTS, ids=list(CONFLICTS))
def test_s5_status_conflict_between_two_records(out, case):
    rid, paths = CONFLICTS[case]
    found = [f for f in out.findings if f.code == "STATUS_CONFLICT" and f.path in paths
             and (f.names(rid) or f.names("CL-" + rid))]
    assert found, f"no STATUS_CONFLICT for {rid} at {paths}"


@pytest.mark.parametrize("rid", ["DEC-133", "DEC-100", "DAEO-t002", "MR-2"],
                         ids=["done-and-spent", "in-force-and-current", "closed-with-close-record", "mr-accepted"])
def test_s5_guard_records_that_agree_give_no_status_conflict(out, rid):
    assert out.findings, "gov links gave no finding at all on the planted repository"
    assert not out.of("STATUS_CONFLICT", rid)


# --------------------------------------------------------------------------------- S6 NOT_IN_FORCE_AS_RULE

RULES = {  # the decision, its status, the place, the needle of its line
    "proposed-in-ticket-sources": ("DEC-120", "PROPOSED", T001, "- DEC-120"),
    "rejected-in-kpi-bracket": ("DEC-121", "REJECTED", T001, "[DEC-121]"),
    "superseded-in-open-ticket-sources": ("DEC-107", "SUPERSEDED", T004, "- DEC-107"),
    "proposed-in-register-under": ("DEC-120", "PROPOSED", REGISTER, "**Under:** DEC-120"),
    "proposed-in-kernel-skill-line": ("DEC-120", "PROPOSED", SKILL, "(DEC-120)"),
    "rejected-in-prompt-line": ("DEC-121", "REJECTED", "governance/project/prompts/w2.md", "(DEC-121)"),
    "withdrawn-in-brief-line": ("DEC-124", "WITHDRAWN", "governance/project/briefs/b1.md", "(DEC-124)"),
    "proposed-in-path-map-comment": ("DEC-120", "PROPOSED", PATH_MAP, "(DEC-120)"),
}


@pytest.mark.parametrize("case", RULES, ids=list(RULES))
def test_s6_not_in_force_as_rule_in_each_rule_bearing_place(out, repo, case):
    rid, _, path, needle = RULES[case]
    found = out.of("NOT_IN_FORCE_AS_RULE", rid, path=path)
    assert found, f"no NOT_IN_FORCE_AS_RULE for {rid} at {path}"
    assert any(f.line == support.line_of(repo, path, needle) for f in found), found


@pytest.mark.parametrize("case", RULES, ids=list(RULES))
def test_s6_the_finding_names_the_decision_s_status(out, case):
    rid, status, path, _ = RULES[case]
    found = out.of("NOT_IN_FORCE_AS_RULE", rid, path=path)
    assert found and any(status in f.raw for f in found), found


def test_s6_not_in_force_as_rule_in_a_judged_commit_s_implements(out, since_root):
    """The test designer's commit names the PROPOSED DEC-120 in Implements:."""
    c3 = since_root[0]["c3"]
    placed = {T001, REGISTER, SKILL, PATH_MAP}
    found = [f for f in out.of("NOT_IN_FORCE_AS_RULE", "DEC-120") if f.path not in placed
             and (c3[:7] in f.raw or "Implements" in f.raw)]
    assert found, "no NOT_IN_FORCE_AS_RULE for the commit whose Implements: names DEC-120"


def test_s6_guard_a_closed_ticket_and_a_decision_in_force_give_none(out):
    assert out.findings, "gov links gave no finding at all on the planted repository"
    assert not [f for f in out.findings if f.code == "NOT_IN_FORCE_AS_RULE" and (f.path == T002 or f.names("DEC-100"))]


# ---------------------------------------------------------------------------------- S7 ENFORCES_SUPERSEDED

def propagation(repo):
    sys.path.insert(0, str(support.src_dir()))
    from gov.decisions.propagation import check_propagation
    return check_propagation(repo)


def test_s7_premise_propagation_finds_the_two_planted_places(repo):
    found = propagation(repo)
    assert sorted(f["paths"][0] for f in found) == [T004, "src/app/limits.py"], found


def test_s7_every_propagation_finding_is_carried_with_its_path_and_line(out, repo):
    found = propagation(repo)
    assert found
    for finding in found:
        path = finding["paths"][0]
        line = int(finding["message"].split(" ", 1)[0].rsplit(":", 1)[1])
        carried = out.of("ENFORCES_SUPERSEDED", *finding["ids"], path=path)
        assert any(f.line == line for f in carried), (finding, carried)
    assert len(out.of("ENFORCES_SUPERSEDED")) == len(found)


# ------------------------------------------------------------------------------- S8 one source of patterns

def test_s8_premise_the_loader_s_patterns_give_the_planted_unmarked_pairs(repo):
    assert support.statement_pairs(repo) == {("DEC-101", "DEC-102"), ("DEC-103", "DEC-104"), ("DEC-109", "DEC-110"),
                                             ("DEC-111", "DEC-112"), ("DEC-130", "DEC-131")}


def test_s8_unmarked_change_is_exactly_what_register_statements_and_archive_section_a_state(out, repo):
    pairs = support.statement_pairs(repo)
    found = out.of("UNMARKED_CHANGE")
    for changed, changer in pairs:
        assert out.of("UNMARKED_CHANGE", changed, changer), f"{changed} <- {changer} missing"
    for finding in found:
        assert any(finding.names(changed, changer) for changed, changer in pairs), finding
