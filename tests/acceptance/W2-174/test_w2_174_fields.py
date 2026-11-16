"""W2-174 S6, S7 and F4 (DEC-1188): the launch fields (role, allowed_paths, kpis, reads, needs, waits_on) by the checked pass.

The lead's interface L10 to L17 (README, "The launch fields"): the list names each lacking field (S6); the apply checks
every field before any write and refuses with a named code, leaving the whole tree byte-identical (S7); and it never
overwrites a field, writes one the answers do not name, or leaves a ticket that fails the ticket schema (F4).
"""

from __future__ import annotations

import difflib
import os
import re
import sys
from pathlib import Path

import pytest

import w2_174_support as s

FIELDS = list(s.FIELD_NAMES)
SIX = " ".join(FIELDS)
CLAUSE = s.CLAUSE
MARKER = re.compile(r"^verify_pass: \d{4}-\d{2}-\d{2} " + re.escape(s.SESSION) + "$")


# --- helpers --------------------------------------------------------------------------------------------------------

def _apply(repo, data: dict, how: str, name: str = "answers.yaml") -> list[str]:
    """The apply through the CLI (``how == "cli"``) or the function; the tickets it changed."""
    path = repo.answers(data, name)
    if how == "cli":
        return s.result_of(repo.verify_apply(path)).get("changed")
    return s.verify_pass().apply(repo.root, path, s.SESSION, s.TODAY)


def _listed(repo, how: str) -> tuple[list[dict], str | None]:
    """``(missing, text)``: from the CLI's envelope, or from the function (no text)."""
    if how == "cli":
        result = s.result_of(repo.verify_list())
        return result.get("missing"), result.get("text")
    return s.verify_pass().missing(repo.root), None


def _refused(repo, data: dict | None = None, text: str | None = None, name: str = "answers.yaml") -> str:
    """The apply through the CLI and through the function must refuse with the same code and leave the whole tree
    (repository and answers folder) byte-identical each time. Returns the code."""
    from gov.cli.errors import GovError

    path = repo.answers_text(text, name) if text is not None else repo.answers(data, name)
    before = s.snapshot(repo.tmp)
    code = s.refused_code(repo.verify_apply(path))
    assert s.snapshot(repo.tmp) == before, \
        f"a refusal ({code}) through the CLI changed the tree: {s.changed_entries(before, s.snapshot(repo.tmp))}"
    with pytest.raises(GovError) as raised:
        s.verify_pass().apply(repo.root, path, s.SESSION, s.TODAY)
    assert raised.value.code == code, f"the function refuses {raised.value.code}, the CLI {code}"
    assert s.snapshot(repo.tmp) == before, f"a refusal ({code}) through the function changed the tree"
    s.marker_invariant(repo.root)
    return code


def _plan(repo, drop: tuple[str, ...] = (), **override) -> dict:
    """Two bare tickets: ``exa-aa01`` (the one a case spoils) and ``exa-bb02`` (answered well, so a refusal shows the
    good entry is not written either). The answers give ``exa-aa01`` every field of an engineer, less ``drop``, with
    ``override`` replacing the named fields."""
    repo.bare("exa-aa01", "W2-31")
    repo.bare("exa-bb02", "W2-32")
    bad = s.good_fields("engineer")
    bad.update(override)
    for name in drop:
        del bad[name]
    return {"exa-aa01": bad, "exa-bb02": s.good_fields("engineer", "The other widget")}


def _inserted_block(old: str, new: str) -> list[str]:
    """The lines ``new`` holds between ``old``'s last front-matter line and its closing ``---``; every other line of
    ``old`` must be where it was (L14: every byte the ticket had stays)."""
    old_lines, new_lines = old.split("\n"), new.split("\n")
    end = old_lines.index("---", 1)
    tail = old_lines[end:]
    assert new_lines[:end] == old_lines[:end], \
        "the front matter's lines before the closing --- are not exactly the original's (a re-dump, or an edit)"
    assert new_lines[len(new_lines) - len(tail):] == tail, "the closing --- and the body are not the original's"
    return new_lines[end:len(new_lines) - len(tail)]


def _check_inserted(old: str, new: str, answered: dict) -> None:
    """The inserted lines are the answered fields as YAML text in L10 order, then the one marker line."""
    import yaml

    block = _inserted_block(old, new)
    assert block and MARKER.match(block[-1]), f"the last inserted line is not the one verify_pass marker: {block[-3:]}"
    inserted = yaml.safe_load("\n".join(block[:-1])) if block[:-1] else {}
    want = [name for name in FIELDS if name in answered]
    assert isinstance(inserted, dict) and list(inserted) == want, \
        f"the inserted fields are {list(inserted) if isinstance(inserted, dict) else inserted!r}, expected {want} in order"
    for name in want:
        assert inserted[name] == answered[name], f"{name} was written as {inserted[name]!r}, the answers gave {answered[name]!r}"
    assert len(s.marker_lines(new)) == 1


def _coordination_and_review(repo) -> dict:
    """The adopted repository's two tickets (L16): a coordination ticket and an A5 review ticket, each with the common
    keys and none of the six fields; the kernel templates, a filled facts file and a file the review waits on."""
    repo.kernel_templates()
    repo.filled_facts()
    repo.file("docs/notes/a5-scope.md", "The scope of the A5 review.\n")
    repo.bare("exa-dt1z", "W2-27")
    repo.bare("exa-a5rv", "W2-28")
    return {
        "exa-dt1z": {
            "role": "orchestrator",
            "allowed_paths": ["governance/adoption/**", "governance/project/**"],
            "kpis": {"success": [{"line": "The adoption runs its stages in turn, each resting on a record.",
                                  "verify": "gov adopt --lite --stage <each stage> --json exits 0 in turn"}],
                     "failure": [{"line": "A stage is skipped.", "verify": "gov adopt refuses the next stage"}]},
            "reads": ["governance/project/path-map.yaml"], "needs": [], "waits_on": [],
        },
        "exa-a5rv": {
            "role": "independent-auditor",
            "allowed_paths": ["governance/project/audits/adoption-A5/**"],
            "kpis": {"success": [{"line": "The verdict record names the auditor's session.",
                                  "verify": "the orchestrator's gov adopt --lite --stage A5 exits 0 on a pass verdict"},
                                 "Each kit check is mapped to a check family or to no equivalent. "
                                 "Verify: the verdict's body holds one table row per kit check"],
                     "failure": [{"line": "A pass verdict leaves a kit check unmapped.",
                                  "verify": "the table shows the gap while the front matter says pass"}]},
            "reads": ["CLAUDE.md", "AGENTS.md"], "needs": [],
            "waits_on": [{"ref": "exa-dt1z", "reason": "the coordination ticket runs the stages"},
                         "docs/notes/a5-scope.md"],
        },
    }


# --- S6: the list --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["cli", "function"])
def test_s6_the_list_names_the_six_fields_of_each_ticket_that_has_none(repo, how):
    _coordination_and_review(repo)
    before = s.snapshot(repo.root)
    listed, text = _listed(repo, how)
    expected = [{"ticket": "exa-a5rv", "labels": [], "fields": FIELDS},
                {"ticket": "exa-dt1z", "labels": [], "fields": FIELDS}]
    assert listed == expected, f"missing is not exactly the six fields of each bare ticket, in L10 order: {listed!r}"
    if how == "cli":
        assert text.splitlines() == [f"exa-a5rv {SIX}", f"exa-dt1z {SIX}"], \
            f"text is not one '<id> <fields>' line per ticket: {text!r}"
    assert s.snapshot(repo.root) == before, "the list changed the repository"


def test_s6_the_cli_text_without_json_is_gov_s_result_dict(repo):
    import json

    _coordination_and_review(repo)
    done = repo.adopt("--verify-list", json_out=False)
    assert done.returncode == 0, f"gov adopt --verify-list failed: {s.describe(done)}"
    printed = json.loads(done.stdout)
    assert printed.get("missing") == [{"ticket": "exa-a5rv", "labels": [], "fields": FIELDS},
                                      {"ticket": "exa-dt1z", "labels": [], "fields": FIELDS}], printed
    assert printed.get("text") == f"exa-a5rv {SIX}\nexa-dt1z {SIX}", printed


@pytest.mark.parametrize("how", ["cli", "function"])
def test_s6_the_list_mixes_labels_and_lacking_fields_and_skips_what_is_set(repo, how):
    """Lacking fields in L10 order beside the labels; a key present with any value, ``[]`` included, is set; a ticket that
    lacks ``kpis`` has no labels; ``state_class`` and the other keys are never listed; closed tickets are not listed."""
    kpis_lacking = {"success": ["The widget does a first thing [DEC-1].", "The widget does a second thing [DEC-1]."],
                    "failure": ["The widget never crashes [DEC-1]."]}
    kpis_ok = s.good_kpis()
    repo.bare("exa-aa01", "W2-41", state_class=False)                                    # lacks all six (no state_class)
    repo.bare("exa-bb02", "W2-42", **s.good_fields("engineer"))                          # all six set, `[]` declared none
    repo.bare("exa-cc03", "W2-43", role="engineer", allowed_paths=["src/**"],            # lacks reads, needs, waits_on
              kpis={"success": [kpis_lacking["success"][0], {"line": "A verified one.", "verify": "a test"}],
                    "failure": ["The widget never crashes [DEC-1]."]})
    repo.bare("exa-dd04", "W2-44", role="engineer", allowed_paths=["src/**"], kpis=kpis_ok, reads=[], waits_on=[])
    repo.bare("exa-ee05", "W2-45", role="engineer", allowed_paths=["src/**"], reads=[], needs=[], waits_on=[])  # no kpis
    repo.bare("exa-ff06", "W2-46", status="closed")                                      # closed: not listed
    repo.bare("exa-gg07", "W2-47", status="in_progress")                                 # lacks all six
    repo.bare("exa-hh08", "W2-48", **{**s.good_fields("engineer"), "kpis": kpis_lacking})  # fields set, lines lacking
    expected = [
        {"ticket": "exa-aa01", "labels": [], "fields": FIELDS},
        {"ticket": "exa-cc03", "labels": ["S1", "F1"], "fields": ["reads", "needs", "waits_on"]},
        {"ticket": "exa-dd04", "labels": [], "fields": ["needs"]},
        {"ticket": "exa-ee05", "labels": [], "fields": ["kpis"]},
        {"ticket": "exa-gg07", "labels": [], "fields": FIELDS},
        {"ticket": "exa-hh08", "labels": ["S1", "S2", "F1"], "fields": []},
    ]
    listed, text = _listed(repo, how)
    assert listed == expected, f"missing is not as L11 states:\n got {listed!r}\nwant {expected!r}"
    if how == "cli":
        assert text.splitlines() == [f"exa-aa01 {SIX}", "exa-cc03 S1 F1 reads needs waits_on", "exa-dd04 needs",
                                     "exa-ee05 kpis", f"exa-gg07 {SIX}", "exa-hh08 S1 S2 F1"], f"text is {text!r}"


# --- S6: the apply -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["cli", "function"])
def test_s6_after_the_apply_both_tickets_validate_are_ready_and_the_auditor_brief_builds(repo, how):
    answers = _coordination_and_review(repo)
    # the fixture is the cause of nothing: before the apply every check refuses them
    for ticket in answers:
        assert s.schema_errors(s.front_of(repo.ticket_text(ticket))), f"{ticket} validates before the apply"
        assert s.refusals_of(repo.root, ticket), f"ready_check passes {ticket} before the apply"
    refused = repo.gov("brief", "independent-auditor", "exa-a5rv", json_out=False)
    assert refused.returncode != 0 and "BRIEF_NOT_READY" in refused.stderr, \
        f"gov brief built a brief for a ticket with no launch fields: {s.describe(refused)}"

    changed = _apply(repo, answers, how)
    assert sorted(changed) == ["exa-a5rv", "exa-dt1z"], f"changed is {changed!r}"

    for ticket, given in answers.items():
        front = s.front_of(repo.ticket_text(ticket))
        assert s.schema_errors(front) == [], f"{ticket} does not validate against the ticket schema: {s.schema_errors(front)}"
        assert s.refusals_of(repo.root, ticket) == [], f"ready_check refuses {ticket}: {s.refusals_of(repo.root, ticket)}"
        for name in FIELDS:
            assert front.get(name) == given[name], f"{ticket}: {name} reads back {front.get(name)!r}, expected {given[name]!r}"
        assert s.lacking_labels(repo.ticket_text(ticket)) == []
    listed, text = _listed(repo, how)
    assert listed == [], f"the list still names {listed!r} after the apply"
    if how == "cli":
        assert text == "none"
    done = repo.gov("brief", "independent-auditor", "exa-a5rv", json_out=False)
    assert done.returncode == 0 and done.stdout.strip(), f"gov brief independent-auditor did not build: {s.describe(done)}"
    assert "governance/project/audits/adoption-A5/**" in done.stdout, "the brief does not carry the ticket's allowed path"


@pytest.mark.parametrize("how", ["cli", "function"])
def test_s6_the_applied_file_is_the_original_plus_only_the_inserted_field_lines_and_the_marker(repo, how):
    answers = _coordination_and_review(repo)
    original = {ticket: repo.ticket_text(ticket) for ticket in answers}
    _apply(repo, answers, how)
    for ticket, given in answers.items():
        new = repo.ticket_text(ticket)
        _check_inserted(original[ticket], new, given)
        assert "# a comment between keys that must stay" in new
        assert "state_class: AUTHORITATIVE  # a trailing comment that must stay" in new
        assert new.index("verify_pass:") > new.index("waits_on:"), "the marker is not after the fields"


@pytest.mark.parametrize("how", ["cli", "function"])
def test_s6_a_ticket_that_also_lacks_a_clause_gets_its_fields_and_its_clause_and_nothing_else(repo, how):
    repo.bare("exa-cc03", "W2-43", role="engineer", allowed_paths=["src/**"],
              kpis={"success": ["The widget does a first thing [DEC-1].", "The widget does a second thing [DEC-1]."],
                    "failure": ["The widget never crashes [DEC-1]."]})
    old = repo.ticket_text("exa-cc03")
    old_front = s.front_of(old)
    _apply(repo, {"exa-cc03": {"S2": CLAUSE, "F1": "a unit test crashes it on purpose and sees it stay up",
                               "S1": "a unit test runs it and reads what it prints", "reads": ["docs/**"],
                               "needs": [], "waits_on": []}}, how)
    new = repo.ticket_text("exa-cc03")
    front = s.front_of(new)
    assert s.lacking_labels(new) == [], "a line still lacks its verify"
    rows = {label: verify for label, _, verify in s.rows_of(new)}
    assert rows["S2"] == CLAUSE and rows["F1"].startswith("a unit test crashes it")
    assert {key: front[key] for key in old_front if key != "kpis"} == {key: old_front[key] for key in old_front if key != "kpis"}
    assert front["reads"] == ["docs/**"] and front["needs"] == [] and front["waits_on"] == []
    assert set(front) == set(old_front) | {"reads", "needs", "waits_on", "verify_pass"}, \
        f"keys after {sorted(front)}, before {sorted(old_front)}"
    # only the three KPI lines changed; everything else is a pure insertion before the closing ---
    old_lines, new_lines = old.split("\n"), new.split("\n")
    changed_old = []
    inserts = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
        if tag in ("replace", "delete"):
            changed_old += old_lines[i1:i2]
        if tag == "insert":
            inserts.append((i1, new_lines[j1:j2]))
    assert sorted(line.strip() for line in changed_old) == sorted(
        ["- The widget does a first thing [DEC-1].", "- The widget does a second thing [DEC-1].",
         "- The widget never crashes [DEC-1]."]), f"lines of the original other than the three KPI lines changed: {changed_old}"
    end = old_lines.index("---", 1)
    assert all(position == end for position, _ in inserts), f"a line was inserted somewhere but before the closing ---: {inserts}"
    closing = new_lines.index("---", 1)
    assert MARKER.match(new_lines[closing - 1]), f"the marker is not the last front-matter line: {new_lines[closing - 2:closing + 1]}"
    assert sum(1 for line in new_lines[:closing] if line.startswith("verify_pass:")) == 1


# --- S7: one case per refusal --------------------------------------------------------------------------------------

@pytest.mark.parametrize("role", ["wizard", "Engineer", "lead"])
def test_s7_an_unknown_role_is_refused(repo, role):
    assert _refused(repo, _plan(repo, role=role)) == "VERIFY_PASS_UNKNOWN_ROLE"


@pytest.mark.parametrize("role", list(s.ROLES))
def test_s7_each_role_a_ticket_is_launched_under_is_accepted(repo, role):
    assert _apply(repo, _plan(repo, role=role), "cli") == ["exa-aa01", "exa-bb02"]
    assert s.front_of(repo.ticket_text("exa-aa01"))["role"] == role


def test_s7_an_empty_allowed_paths_is_refused(repo):
    assert _refused(repo, _plan(repo, allowed_paths=[])) == "VERIFY_PASS_BAD_FIELD"


BAD_FIELDS = {
    "allowed_paths-not-a-list": ("allowed_paths", "src/**"),
    "allowed_paths-an-empty-item": ("allowed_paths", ["src/**", ""]),
    "allowed_paths-a-number": ("allowed_paths", [5]),
    "allowed_paths-dotdot-first": ("allowed_paths", ["../elsewhere/**"]),
    "allowed_paths-dotdot-inside": ("allowed_paths", ["src/../docs/**"]),
    "allowed_paths-absolute": ("allowed_paths", ["/etc/**"]),
    "allowed_paths-absolute-acceptance": ("allowed_paths", ["/tests/acceptance/**"]),
    "reads-not-a-list": ("reads", "src/**"),
    "reads-an-empty-item": ("reads", [""]),
    "reads-a-number": ("reads", [5]),
    "needs-not-a-list": ("needs", "src/x.py"),
    "needs-an-empty-item": ("needs", [""]),
    "needs-a-number": ("needs", [5]),
    "waits_on-not-a-list": ("waits_on", "exa-qu2x"),
    "waits_on-a-number": ("waits_on", [5]),
    "waits_on-an-empty-string": ("waits_on", [""]),
    "waits_on-no-reason": ("waits_on", [{"ref": "exa-qu2x"}]),
    "waits_on-no-ref": ("waits_on", [{"reason": "it runs first"}]),
    "waits_on-an-empty-ref": ("waits_on", [{"ref": "", "reason": "it runs first"}]),
    "kpis-no-success": ("kpis", {"failure": []}),
    "kpis-an-empty-success": ("kpis", {"success": [], "failure": []}),
    "kpis-a-string": ("kpis", "The widget works. Verify: a test"),
    "kpis-success-not-a-list": ("kpis", {"success": "The widget works. Verify: a test", "failure": []}),
    "kpis-a-number-item": ("kpis", {"success": [5], "failure": []}),
}


@pytest.mark.parametrize("field,value", list(BAD_FIELDS.values()), ids=list(BAD_FIELDS))
def test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field(repo, field, value):
    assert _refused(repo, _plan(repo, **{field: value})) == "VERIFY_PASS_BAD_FIELD"


ACCEPTANCE = ["tests/acceptance/**", "tests/acceptance/W2-1/x.py", "**", "tests/**", "t*", "./tests/acceptance/**",
              "tests/acc*/x", "tests/accept?nce/**", "tests/acceptance/", "tests/acceptance", "[t]ests/**", "*",
              "tests/a*", "te?ts/**"]


@pytest.mark.parametrize("pattern", ACCEPTANCE)
def test_s7_an_acceptance_path_for_an_engineer_is_refused(repo, pattern):
    assert _refused(repo, _plan(repo, allowed_paths=["src/**", pattern])) == "VERIFY_PASS_ACCEPTANCE_PATH"


@pytest.mark.parametrize("role", ["orchestrator", "research", "independent-auditor", "product-spec"])
def test_s7_the_acceptance_rule_holds_for_every_role_but_the_test_designer(repo, role):
    assert _refused(repo, _plan(repo, role=role, allowed_paths=["**"])) == "VERIFY_PASS_ACCEPTANCE_PATH"


def test_s7_the_ticket_s_own_role_judges_the_acceptance_path_when_the_answers_give_no_role(repo):
    repo.bare("exa-aa01", "W2-31", role="engineer")
    given = {key: value for key, value in s.good_fields("engineer").items() if key != "role"}
    given["allowed_paths"] = ["tests/acceptance/W2-31/**"]
    assert _refused(repo, {"exa-aa01": given}) == "VERIFY_PASS_ACCEPTANCE_PATH"


@pytest.mark.parametrize("pattern", ["tests/acceptance/W2-9/**", "**", "tests/**", "tests/acceptance/W2-1/x.py"])
@pytest.mark.parametrize("how", ["cli", "function"])
def test_s7_an_independent_test_designer_may_hold_an_acceptance_path(repo, pattern, how):
    answers = _plan(repo, role="independent-test-designer", allowed_paths=[pattern])
    assert _apply(repo, answers, how) == ["exa-aa01", "exa-bb02"]
    front = s.front_of(repo.ticket_text("exa-aa01"))
    assert front["allowed_paths"] == [pattern] and s.schema_errors(front) == []


def test_s7_a_ticket_whose_own_role_is_the_test_designer_may_hold_an_acceptance_path(repo):
    repo.bare("exa-aa01", "W2-31", role="independent-test-designer")
    given = {key: value for key, value in s.good_fields("independent-test-designer").items() if key != "role"}
    given["allowed_paths"] = ["tests/acceptance/W2-31/**"]
    assert _apply(repo, {"exa-aa01": given}, "cli") == ["exa-aa01"]


SAFE = ["src/**", "tests/unit/**", "tests/acceptance_helpers/**", "tests/acceptancex/**", "docs/tests/acceptance/**",
        "tests/unit/test_*.py", "governance/project/audits/adoption-A5/**", "./src/widget/**"]


@pytest.mark.parametrize("pattern", SAFE)
def test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer(repo, pattern):
    answers = _plan(repo, allowed_paths=[pattern])
    assert _apply(repo, answers, "cli") == ["exa-aa01", "exa-bb02"], "a pattern that cannot reach tests/acceptance/ was refused"
    assert s.front_of(repo.ticket_text("exa-aa01"))["allowed_paths"] == [pattern]


KPI_FAULTS = {
    "success-without-verify": ({"success": ["The widget does a thing [DEC-1]."], "failure": []}, "VERIFY_PASS_KPI_NO_VERIFY"),
    "failure-without-verify": ({"success": [{"line": "It works.", "verify": "a test"}], "failure": ["It never crashes."]},
                               "VERIFY_PASS_KPI_NO_VERIFY"),
    "second-line-without-verify": ({"success": ["First. Verify: a test", "Second, with none."], "failure": []},
                                   "VERIFY_PASS_KPI_NO_VERIFY"),
    "verify-label-and-nothing-after": ({"success": ["It does a thing. Verify:"], "failure": []},
                                       "VERIFY_PASS_KPI_NO_VERIFY"),
    "mapping-verify-tbd": ({"success": [{"line": "It works.", "verify": "TBD"}], "failure": []},
                           "VERIFY_PASS_EMPTY_CLAUSE"),
    "mapping-verify-na": ({"success": [{"line": "It works.", "verify": "n/a"}], "failure": []},
                          "VERIFY_PASS_EMPTY_CLAUSE"),
    "mapping-verify-none": ({"success": [{"line": "It works.", "verify": "none"}], "failure": []},
                            "VERIFY_PASS_EMPTY_CLAUSE"),
    "mapping-verify-todo-dot": ({"success": [{"line": "It works.", "verify": " TODO. "}], "failure": []},
                                "VERIFY_PASS_EMPTY_CLAUSE"),
    "string-verify-tbd": ({"success": ["It works. Verify: TBD"], "failure": []}, "VERIFY_PASS_EMPTY_CLAUSE"),
    "failure-mapping-verify-todo": ({"success": [{"line": "It works.", "verify": "a test"}],
                                     "failure": [{"line": "It fails.", "verify": "TODO"}]}, "VERIFY_PASS_EMPTY_CLAUSE"),
}


@pytest.mark.parametrize("kpis,code", list(KPI_FAULTS.values()), ids=list(KPI_FAULTS))
def test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused(repo, kpis, code):
    assert _refused(repo, _plan(repo, kpis=kpis)) == code


def test_s7_a_verify_that_starts_with_a_placeholder_word_is_text_of_its_own(repo):
    kpis = {"success": [{"line": "It works.", "verify": "none of the other files change: a hash shows it"}], "failure": []}
    assert _apply(repo, _plan(repo, kpis=kpis), "cli") == ["exa-aa01", "exa-bb02"]


VALUES = {"role": "research", "allowed_paths": ["docs/**"], "kpis": s.good_kpis("The old widget"),
          "reads": [], "needs": ["docs/a.md"], "waits_on": []}


@pytest.mark.parametrize("field", FIELDS)
def test_s7_a_field_the_ticket_already_has_is_refused_never_overwritten(repo, field):
    repo.bare("exa-aa01", "W2-31", **{field: VALUES[field]})
    answers = {"exa-aa01": s.good_fields("engineer")}
    assert _refused(repo, answers) == "VERIFY_PASS_FIELD_SET"
    assert s.front_of(repo.ticket_text("exa-aa01"))[field] == VALUES[field]


# --- S7: the rest of L13 -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("dropped", FIELDS)
def test_s7_a_lacking_field_the_answers_do_not_supply_is_refused_unanswered(repo, dropped):
    assert _refused(repo, _plan(repo, drop=(dropped,))) == "VERIFY_PASS_UNANSWERED"


def test_s7_a_named_ticket_with_nothing_answered_is_refused_unanswered(repo):
    answers = _plan(repo)
    answers["exa-aa01"] = {}
    assert _refused(repo, answers) == "VERIFY_PASS_UNANSWERED"


def test_s7_fields_answered_while_a_line_still_lacks_its_verify_is_refused_and_the_ticket_unmarked(repo):
    repo.bare("exa-cc03", "W2-43", role="engineer", allowed_paths=["src/**"],
              kpis={"success": ["The widget does a first thing [DEC-1]."], "failure": ["The widget never crashes [DEC-1]."]})
    answers = {"exa-cc03": {"S1": CLAUSE, "reads": ["docs/**"], "needs": [], "waits_on": []}}  # F1 not answered
    assert _refused(repo, answers) == "VERIFY_PASS_UNANSWERED"
    assert s.marker_lines(repo.ticket_text("exa-cc03")) == []


def test_s7_the_good_answers_apply_to_prove_the_fixture_is_not_the_cause(repo):
    assert _apply(repo, _plan(repo), "cli") == ["exa-aa01", "exa-bb02"]
    for ticket in ("exa-aa01", "exa-bb02"):
        assert s.schema_errors(s.front_of(repo.ticket_text(ticket))) == []
        assert s.refusals_of(repo.root, ticket) == []
        assert len(s.marker_lines(repo.ticket_text(ticket))) == 1


# --- F4: the planted cases -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ["different", "same"])
def test_f4_overwriting_a_set_field_is_refused_and_the_tree_is_byte_identical(repo, kind):
    repo.bare("exa-aa01", "W2-31", role="engineer", reads=["docs/**"])
    repo.bare("exa-bb02", "W2-32")
    given = s.good_fields("engineer" if kind == "same" else "orchestrator")
    given["reads"] = ["docs/**"] if kind == "same" else ["src/**"]
    answers = {"exa-aa01": given, "exa-bb02": s.good_fields()}
    assert _refused(repo, answers) == "VERIFY_PASS_FIELD_SET"
    front = s.front_of(repo.ticket_text("exa-aa01"))
    assert front["role"] == "engineer" and front["reads"] == ["docs/**"]


@pytest.mark.parametrize("kind", ["no-state-class", "id-not-a-ticket-id"])
def test_f4_a_ticket_that_would_fail_the_ticket_schema_is_refused_and_nothing_is_written(repo, kind):
    if kind == "no-state-class":
        repo.bare("exa-aa01", "W2-31", state_class=False)
    else:  # tk writes ids as a prefix and four lower-case characters; the schema holds the grammar
        repo.raw_ticket("exa-AB12", s.bare_text("exa-AB12", "W2-31"))
    repo.bare("exa-bb02", "W2-32")
    answers = {("exa-aa01" if kind == "no-state-class" else "exa-AB12"): s.good_fields(), "exa-bb02": s.good_fields()}
    assert _refused(repo, answers) == "VERIFY_PASS_SCHEMA"


def _decoy_schemas(repo, body: str) -> None:
    for name in ("ticket.schema.json", "common.schema.json"):
        repo.file(f"template/governance/kernel/schemas/{name}", body)


def test_f4_the_schema_judged_is_the_one_shipped_with_gov_never_a_copy_inside_the_repository(repo):
    _decoy_schemas(repo, "{}\n")  # a schema that accepts anything
    repo.bare("exa-aa01", "W2-31", state_class=False)
    assert _refused(repo, {"exa-aa01": s.good_fields()}) == "VERIFY_PASS_SCHEMA"


def test_f4_a_stricter_copy_inside_the_repository_does_not_refuse_a_ticket_the_kernel_schema_accepts(repo):
    _decoy_schemas(repo, '{"type": "object", "required": ["zzz-never-present"]}\n')
    repo.bare("exa-aa01", "W2-31")
    before = s.snapshot(repo.root / "template")
    assert _apply(repo, {"exa-aa01": s.good_fields()}, "cli") == ["exa-aa01"]
    assert s.snapshot(repo.root / "template") == before, "the apply touched the decoy schemas inside the repository"


@pytest.mark.parametrize("name", ["state_class", "non_goals", "class", "type", "profile", "title", "status", "ROLE",
                                  "deps", "verify_pass", "sources"])
def test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written(repo, name):
    answers = _plan(repo)
    answers["exa-aa01"][name] = "AUTHORITATIVE" if name == "state_class" else ["x"]
    assert _refused(repo, answers) == "VERIFY_PASS_UNKNOWN_LABEL"
    del answers["exa-aa01"][name]  # the same answers without that key are good: it was the only fault
    before = s.front_of(repo.ticket_text("exa-aa01"))
    assert _apply(repo, answers, "cli") == ["exa-aa01", "exa-bb02"]
    after = s.front_of(repo.ticket_text("exa-aa01"))
    assert name == "verify_pass" or after.get(name) == before.get(name), f"{name} was written: {after.get(name)!r}"


def test_f4_a_closed_ticket_and_an_unknown_one_are_refused_with_fields_too(repo):
    answers = _plan(repo)
    repo.bare("exa-cl09", "W2-39", status="closed")
    assert _refused(repo, {**answers, "exa-cl09": s.good_fields()}, name="closed.yaml") == "VERIFY_PASS_CLOSED"
    assert _refused(repo, {**answers, "exa-zz99": s.good_fields()}, name="unknown.yaml") == "VERIFY_PASS_UNKNOWN_TICKET"


@pytest.mark.parametrize("how", ["cli", "function"])
def test_f4_a_good_apply_of_several_tickets_adds_no_key_the_answers_did_not_name(repo, how):
    kpis = {"success": [{"line": "A verified one.", "verify": "a test"}], "failure": []}
    repo.bare("exa-aa01", "W2-31")                                                         # all six answered
    repo.bare("exa-bb02", "W2-32", role="engineer", allowed_paths=["src/**"], kpis=kpis)  # reads, needs, waits_on
    repo.bare("exa-cc03", "W2-33")                                                         # not named
    repo.bare("exa-dd04", "W2-34", status="closed")                                        # closed, not named
    repo.bare("exa-ee05", "W2-35", **s.good_fields("engineer"))                            # complete, not named
    repo.bare("exa-ff06", "W2-36", state_class=False)                                      # would fail the schema, not named
    answers = {"exa-aa01": s.good_fields("independent-auditor"),
               "exa-bb02": {"reads": ["docs/**"], "needs": ["docs/a.md"], "waits_on": ["exa-aa01"]}}
    untouched = {t: repo.ticket_bytes(t) for t in ("exa-cc03", "exa-dd04", "exa-ee05", "exa-ff06")}
    before_text = {t: repo.ticket_text(t) for t in answers}
    before = s.snapshot(repo.tmp)
    assert _apply(repo, answers, how) == ["exa-aa01", "exa-bb02"]
    for ticket, content in untouched.items():
        assert repo.ticket_bytes(ticket) == content, f"{ticket} is not named in the answers but was edited"
    for ticket, given in answers.items():
        old, new = s.front_of(before_text[ticket]), s.front_of(repo.ticket_text(ticket))
        assert set(new) == set(old) | set(given) | {"verify_pass"}, \
            f"{ticket}: keys after {sorted(new)} are not the old keys, the named fields and the marker ({sorted(given)})"
        assert {key: new[key] for key in old} == old, f"{ticket}: a value the ticket had changed"
        assert {key: new[key] for key in given} == given
        _check_inserted(before_text[ticket], repo.ticket_text(ticket), given)
    after = s.snapshot(repo.tmp)
    changed = [entry for entry in s.changed_entries(before, after) if not entry.endswith("answers.yaml")]
    assert changed == [f"{s.REPO_NAME}/.tickets/exa-aa01.md", f"{s.REPO_NAME}/.tickets/exa-bb02.md"], \
        f"the apply changed or added something else: {changed}"


# --- L15 (F3 stands): the field apply reads nothing of the repository outside .tickets/ --------------------------------

class _Spy:
    on = False
    events: list = []
    installed = False

    @classmethod
    def hook(cls, event, args):
        if cls.on and event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            cls.events.append((str(args[1]), args[0]))
        if cls.on and event in ("socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system"):
            cls.events.append((event, args[0] if args else ""))

    @classmethod
    def watch(cls):
        if not cls.installed:
            sys.addaudithook(cls.hook)
            cls.installed = True
        cls.events, cls.on = [], True

    @classmethod
    def stop(cls) -> list:
        cls.on = False
        return cls.events


def test_l15_the_field_pass_opens_nothing_of_the_repository_but_tickets_starts_no_process_and_no_connection(repo):
    answers = _coordination_and_review(repo)
    repo.file("README.md", "# the product\n")
    _decoy_schemas(repo, "{}\n")
    path = repo.answers(answers)
    module = s.verify_pass()
    import gov.brief.build  # noqa: F401  (loaded before the watch)
    import jsonschema  # noqa: F401
    import yaml  # noqa: F401

    tickets = (repo.root / ".tickets").resolve()
    root = repo.root.resolve()
    for run in (lambda: module.missing(repo.root), lambda: module.apply(repo.root, path, s.SESSION, s.TODAY)):
        _Spy.watch()
        try:
            run()
        finally:
            events = _Spy.stop()
        stray, inside = [], []
        for mode, raw in events:
            if mode in ("socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system"):
                stray.append((mode, raw))
                continue
            target = Path(os.fsdecode(raw))
            target = (target if target.is_absolute() else Path.cwd() / target).resolve()
            if root in target.parents and tickets not in target.parents:
                stray.append((mode, str(target)))
            elif tickets in target.parents:
                inside.append(target)
        assert not stray, f"the field pass opened {stray}: only {tickets}, the answers file and gov's own files are allowed"
        assert inside, "the spy saw no ticket opened: it does not watch the opens the tool makes"
