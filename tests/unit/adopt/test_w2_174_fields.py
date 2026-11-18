"""W2-174 S6, S7 and F4: the Verify pass lists and writes a launchable ticket's six fields (DEC-1188).

A coordination ticket and a review ticket as the adoption's A0 and A5 leave them (the common keys, none of the six
fields) are listed, given the fields by one apply, and then validate against the kernel's ticket schema, pass
``ready_check`` and build ``gov brief independent-auditor``. Each refusal leaves the tree byte-identical.
"""
from __future__ import annotations

import datetime
import json
import shutil

import pytest

from .test_w2_174_support import REPO, answers_file, gov, gov_json, repo_with, snapshot

from gov.adopt import verify_pass
from gov.brief.build import Tickets, kpi_rows, ready_check
from gov.cli.errors import GovError
from gov.util.frontmatter import parse

TODAY = datetime.date(2026, 11, 15)
SIX = ("role", "allowed_paths", "kpis", "reads", "needs", "waits_on")
COORD, REVIEW = "exa-dt1z", "exa-qu2x"
VERDICT = "governance/project/audits/adoption-A5"


def bare(ticket_id, status="open", keys="", state_class="state_class: AUTHORITATIVE\n"):
    """A ticket as A0 leaves it: the common keys and a comment, none of the six fields (L16); ``keys`` adds raw YAML."""
    return (f"---\nid: {ticket_id}   # the tk id\ntitle: Ticket {ticket_id}\nstatus: {status}\n"
            "# kept: this comment and the key order\ntype: task\ncreated: 2026-11-15 09:00:00+00:00\n"
            f"{state_class}tags: [adoption]\n{keys}---\n\n# {ticket_id}\n\nBody text.\n")


KPIS = {"success": [{"line": "The verdict is committed", "verify": "gov adopt --lite --stage A5 exits 0"},
                    {"line": "Each rule is a finding", "verify": "the findings section lists each rule"}],
        "failure": [{"line": "A pass leaves a gap", "verify": "the table shows the gap"}]}
REVIEW_ANSWER = {"role": "independent-auditor", "allowed_paths": [f"{VERDICT}/**"], "kpis": KPIS,
                 "reads": ["governance/project/path-map.yaml", "CLAUDE.md"], "needs": [], "waits_on": [COORD]}
COORD_ANSWER = {"role": "orchestrator", "allowed_paths": ["governance/**"], "reads": [], "needs": [], "waits_on": [],
                "kpis": {"success": [{"line": "EXAMIN is adopted", "verify": "each stage exits 0 in turn"}],
                         "failure": []}}


def fixture(tmp_path, **tickets):
    return repo_with(tmp_path, tickets or {COORD: bare(COORD), REVIEW: bare(REVIEW)})


def adopted(tmp_path):
    """The two tickets, the kernel templates, the judging-work skill and a filled facts file: what ``gov brief`` reads
    (the auditor's brief carries the skill, W2-195: the kernel file and the session's preloaded copy of one version)."""
    root = fixture(tmp_path)
    shutil.copytree(REPO / "template/governance/kernel/templates", root / "template/governance/kernel/templates")
    for source, target in (("template/governance/kernel/skills/judging-work/SKILL.md",
                            "template/governance/kernel/skills/judging-work/SKILL.md"),
                           (".claude/skills/judging-work/SKILL.md", ".claude/skills/judging-work/SKILL.md")):
        (root / target).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / source, root / target)
    (root / "governance/project").mkdir(parents=True)
    shutil.copyfile(REPO / "governance/project/facts.yaml", root / "governance/project/facts.yaml")
    return root


def front(root, ticket_id):
    return parse((root / f".tickets/{ticket_id}.md").read_text(encoding="utf-8"), rstrip=True)


def schema_errors(instance):
    """Validate against the kernel's ticket schema, with the common schema resolved beside it."""
    import jsonschema

    folder = REPO / "template/governance/kernel/schemas"
    schema = json.loads((folder / "ticket.schema.json").read_text(encoding="utf-8"))
    resolver = jsonschema.RefResolver(base_uri=(folder / "ticket.schema.json").as_uri(), referrer=schema)
    instance = json.loads(json.dumps(instance, default=lambda value: value.isoformat()))
    return [error.message for error in jsonschema.Draft202012Validator(schema, resolver=resolver).iter_errors(instance)]


def refused(root, answers, code, tmp_path, name="a.yaml"):
    before = snapshot(root)
    with pytest.raises(GovError) as raised:
        verify_pass.apply(root, answers_file(tmp_path, answers, name), "s", TODAY)
    assert raised.value.code == code, raised.value
    assert snapshot(root) == before  # nothing written, no marker, no temporary file


# ---------------------------------------------------------------- S6: the list


def test_list_names_the_six_fields_each_ticket_lacks_in_order(tmp_path):
    root = fixture(tmp_path)
    before = snapshot(root)
    code, envelope, _ = gov_json("adopt", "--verify-list", "--root", str(root))
    assert code == 0
    item = lambda ticket: {"ticket": ticket, "labels": [], "fields": list(SIX)}  # noqa: E731
    assert envelope["result"]["missing"] == [item(COORD), item(REVIEW)]
    assert envelope["result"]["text"] == f"{COORD} {' '.join(SIX)}\n{REVIEW} {' '.join(SIX)}"
    assert verify_pass.missing(root) == [item(COORD), item(REVIEW)]
    assert snapshot(root) == before


def test_list_names_only_the_absent_keys_and_a_declared_none_is_set(tmp_path):
    keys = ("role: engineer\nreads: []\nneeds: []\nwaits_on: []\nallowed_paths:\n- src/x.py\n"
            "kpis:\n  success:\n  - one line\n  - 'two Verify: its check'\n  failure: []\n")
    root = fixture(tmp_path, **{"abc-1111": bare("abc-1111", keys=keys),
                                "abc-2222": bare("abc-2222", keys="role: engineer\nreads: []\n"),
                                "abc-3333": bare("abc-3333", "in_progress"),
                                "abc-4444": bare("abc-4444", "closed"),
                                "abc-5555": bare("abc-5555", keys=keys.replace("one line", "'one Verify: c'"))})
    assert verify_pass.missing(root) == [
        {"ticket": "abc-1111", "labels": ["S1"], "fields": []},
        {"ticket": "abc-2222", "labels": [], "fields": ["allowed_paths", "kpis", "needs", "waits_on"]},
        {"ticket": "abc-3333", "labels": [], "fields": list(SIX)}]
    code, out, _ = gov("adopt", "--verify-list", "--root", str(root))
    assert code == 0 and ('"text": "abc-1111 S1\\nabc-2222 allowed_paths kpis needs waits_on\\n'
                          'abc-3333 role allowed_paths kpis reads needs waits_on"') in out


def test_labels_come_before_fields_in_the_text_and_other_keys_are_never_listed(tmp_path):
    keys = "kpis:\n  success: [one, two]\n  failure: []\nrole: engineer\n"
    root = fixture(tmp_path, **{"abc-1111": bare("abc-1111", keys=keys, state_class="")})
    assert verify_pass.missing(root) == [{"ticket": "abc-1111", "labels": ["S1", "S2"],
                                          "fields": ["allowed_paths", "reads", "needs", "waits_on"]}]
    assert gov_json("adopt", "--verify-list", "--root", str(root))[1]["result"]["text"] == \
        "abc-1111 S1 S2 allowed_paths reads needs waits_on"


def test_a_verified_ticket_with_all_six_fields_is_not_listed(tmp_path):
    root = fixture(tmp_path)
    verify_pass.apply(root, answers_file(tmp_path, {COORD: COORD_ANSWER, REVIEW: REVIEW_ANSWER}), "s", TODAY)
    assert verify_pass.missing(root) == []
    assert gov_json("adopt", "--verify-list", "--root", str(root))[1]["result"] == {"missing": [], "text": "none"}


# ---------------------------------------------------------------- S6: the apply


def test_after_the_apply_both_tickets_validate_pass_the_ready_check_and_the_brief_builds(tmp_path):
    root = adopted(tmp_path)
    answers = answers_file(tmp_path, {COORD: COORD_ANSWER, REVIEW: REVIEW_ANSWER})
    code, envelope, err = gov_json("adopt", "--verify-apply", str(answers), "--root", str(root), "--session", "S-1")
    assert code == 0, err
    assert envelope["result"] == {"changed": [COORD, REVIEW]}
    for ticket in (COORD, REVIEW):
        assert schema_errors(front(root, ticket)) == []
        assert ready_check(front(root, ticket), Tickets(root), root, "2026-11-10")[0] == []
        assert front(root, ticket)["verify_pass"].endswith(" S-1")
    code, _, err = gov("brief", "independent-auditor", REVIEW, "--root", str(root))
    assert code == 0, err


def test_the_edit_inserts_the_field_lines_before_the_marker_and_changes_nothing_else(tmp_path):
    root = fixture(tmp_path)
    path = root / f".tickets/{REVIEW}.md"
    old = path.read_text(encoding="utf-8")
    verify_pass.apply(root, answers_file(tmp_path, {REVIEW: REVIEW_ANSWER}), "S-1", TODAY)
    new = path.read_text(encoding="utf-8")
    head, closing = new.split("\n---\n", 1)
    assert closing == old.split("\n---\n", 1)[1]  # the body is untouched
    lines = head.split("\n")
    assert lines[-1] == "verify_pass: 2026-11-15 S-1"
    old_lines = old.split("\n---\n", 1)[0].split("\n")
    assert lines[:len(old_lines)] == old_lines  # every byte the ticket had stays, comments and key order included
    added = lines[len(old_lines):-1]
    keys = [line.split(":")[0] for line in added if line and not line[0] in " -"]
    assert keys == list(SIX)  # L10 order
    assert front(root, REVIEW)["waits_on"] == [COORD] and front(root, REVIEW)["needs"] == []
    assert [(label, verify) for label, _, verify in kpi_rows(front(root, REVIEW))] == [
        ("S1", "gov adopt --lite --stage A5 exits 0"), ("S2", "the findings section lists each rule"),
        ("F1", "the table shows the gap")]


def test_only_the_answered_fields_are_written_and_the_rest_of_the_ticket_is_kept(tmp_path):
    keys = "role: engineer\nallowed_paths:\n- src/x.py\nkpis:\n  success:\n  - 'one Verify: c'\n  failure: []\nreads: []\n"
    root = fixture(tmp_path, **{"abc-1111": bare("abc-1111", keys=keys), "abc-2222": bare("abc-2222")})
    old = (root / ".tickets/abc-1111.md").read_text(encoding="utf-8")
    answers = answers_file(tmp_path, {"abc-1111": {"needs": ["docs/a.md"], "waits_on": []}})
    assert verify_pass.apply(root, answers, "s", TODAY) == ["abc-1111"]
    new = (root / ".tickets/abc-1111.md").read_text(encoding="utf-8")
    assert new == old.replace("---\n\n#", "needs:\n- docs/a.md\nwaits_on: []\nverify_pass: 2026-11-15 s\n---\n\n#")
    assert (root / ".tickets/abc-2222.md").read_text(encoding="utf-8") == bare("abc-2222")


def test_a_marker_that_is_already_there_stays_last_or_in_place(tmp_path):
    root = fixture(tmp_path, **{COORD: bare(COORD, keys="verify_pass: 2026-11-01 old\n")})
    verify_pass.apply(root, answers_file(tmp_path, {COORD: COORD_ANSWER}), "new", TODAY)
    text = (root / f".tickets/{COORD}.md").read_text(encoding="utf-8")
    assert text.count("verify_pass:") == 1 and "waits_on: []\nverify_pass: 2026-11-15 new\n---\n" in text
    assert schema_errors(front(root, COORD)) == []
    root = fixture(tmp_path / "mid", **{COORD: bare(COORD, keys="verify_pass: 2026-11-01 old\nowner: me\n")})
    verify_pass.apply(root, answers_file(tmp_path, {COORD: COORD_ANSWER}), "new", TODAY)
    text = (root / f".tickets/{COORD}.md").read_text(encoding="utf-8")
    assert "verify_pass: 2026-11-15 new\nowner: me\nrole: orchestrator\n" in text and text.count("verify_pass:") == 1


def test_labels_and_fields_are_answered_together_in_one_edit(tmp_path):
    keys = "role: engineer\nallowed_paths:\n- src/x.py\nkpis:\n  success:\n  - plain line\n  failure: []\n"
    root = fixture(tmp_path, **{"abc-1111": bare("abc-1111", keys=keys)})
    answers = {"abc-1111": {"S1": "its check", "reads": [], "needs": [], "waits_on": []}}
    verify_pass.apply(root, answers_file(tmp_path, answers), "s", TODAY)
    found = front(root, "abc-1111")
    assert [row[2] for row in kpi_rows(found)] == ["its check"]
    assert all(found[key] == [] for key in ("reads", "needs", "waits_on"))
    assert verify_pass.missing(root) == []


def test_crlf_tickets_get_crlf_field_lines(tmp_path):
    text = bare(COORD).replace("\n", "\r\n")
    root = fixture(tmp_path, **{COORD: text})
    verify_pass.apply(root, answers_file(tmp_path, {COORD: COORD_ANSWER}), "s", TODAY)
    new = (root / f".tickets/{COORD}.md").read_bytes().decode("utf-8")
    assert new.count("\n") == new.count("\r\n") and schema_errors(front(root, COORD)) == []


def test_fields_a_value_of_yaml_special_text_reads_back_as_the_answer(tmp_path):
    answers = {COORD: {**COORD_ANSWER, "reads": ["on", "yes", "2026-11-15", "a: b", "# not a comment", "x\ny"],
                       "waits_on": [{"ref": "exa-qu2x", "reason": "its verdict: needed"}]}}
    root = fixture(tmp_path)
    verify_pass.apply(root, answers_file(tmp_path, answers), "s", TODAY)
    found = front(root, COORD)
    assert found["reads"] == ["on", "yes", "2026-11-15", "a: b", "# not a comment", "x y"]
    assert found["waits_on"] == [{"ref": "exa-qu2x", "reason": "its verdict: needed"}]


# ---------------------------------------------------------------- S7 and F4: the refusals


def test_unknown_role(tmp_path):
    for role in ("owner", "lead", "Engineer", "", "ticket lead"):
        refused(fixture(tmp_path / role.replace(" ", "_") / "x"), {REVIEW: {**REVIEW_ANSWER, "role": role}},
                "VERIFY_PASS_UNKNOWN_ROLE", tmp_path)


@pytest.mark.parametrize("role", ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                                  "independent-auditor", "research"])
def test_each_launch_role_is_known(tmp_path, role):
    verify_pass.apply(fixture(tmp_path), answers_file(tmp_path, {REVIEW: {**REVIEW_ANSWER, "role": role,
                      "allowed_paths": ["src/**"]}}), "s", TODAY)


@pytest.mark.parametrize("value", [[], "src/x.py", None, 5, {"a": "b"}, [""], ["src/x.py", ""], [5], [["a"]],
                                   ["../x"], ["src/../x"], ["/etc/x"], ["src/.."], [".."]])
def test_bad_allowed_paths(tmp_path, value):
    refused(fixture(tmp_path), {REVIEW: {**REVIEW_ANSWER, "allowed_paths": value}}, "VERIFY_PASS_BAD_FIELD", tmp_path)


@pytest.mark.parametrize("pattern", ["**", "tests/**", "t*", "tests/acceptance/**", "tests/acceptance/W2-1/x.py",
                                     "tests/acceptance", "tests/acceptance/", "./tests/acceptance/x", "tests//acceptance/x",
                                     "tests/./acceptance/x", "", "*", "?", "[a-z]*/x", "tests/acc*", "te?ts/a/b", "tests/acceptance/[a]*"])
def test_an_acceptance_path_for_an_engineer(tmp_path, pattern):
    if pattern == "":
        pattern = "./**"
    for role in ("engineer", "orchestrator", "product-spec", "research", "independent-auditor"):
        refused(fixture(tmp_path / role), {REVIEW: {**REVIEW_ANSWER, "role": role, "allowed_paths": ["src/**", pattern]}},
                "VERIFY_PASS_ACCEPTANCE_PATH", tmp_path)


def test_the_role_of_the_ticket_itself_judges_when_the_answers_name_none(tmp_path):
    keys = "role: engineer\n"
    answers = {"abc-1111": {key: value for key, value in REVIEW_ANSWER.items() if key != "role"}}
    refused(fixture(tmp_path, **{"abc-1111": bare("abc-1111", keys=keys)}),
            {"abc-1111": {**answers["abc-1111"], "allowed_paths": ["tests/**"]}}, "VERIFY_PASS_ACCEPTANCE_PATH", tmp_path)
    ok = fixture(tmp_path / "ok", **{"abc-1111": bare("abc-1111", keys="role: independent-test-designer\n")})
    verify_pass.apply(ok, answers_file(tmp_path, {"abc-1111": {**answers["abc-1111"],
                                                              "allowed_paths": ["tests/acceptance/W2-1/**"]}}), "s", TODAY)


def test_the_test_designer_may_have_acceptance_paths_and_an_engineer_may_have_src_and_lookalikes(tmp_path):
    designer = {**REVIEW_ANSWER, "role": "independent-test-designer", "allowed_paths": ["tests/acceptance/W2-1/**"]}
    verify_pass.apply(fixture(tmp_path / "d"), answers_file(tmp_path, {REVIEW: designer}), "s", TODAY)
    engineer = {**REVIEW_ANSWER, "role": "engineer",
                "allowed_paths": ["src/**", "tests/unit/**", "tests/acceptance-notes/x.md", "docs/tests/acceptance/x"]}
    verify_pass.apply(fixture(tmp_path / "e"), answers_file(tmp_path, {REVIEW: engineer}), "s", TODAY)


@pytest.mark.parametrize("kpis", [
    {"success": ["a line with no verify"], "failure": []},
    {"success": [{"line": "a line"}], "failure": []},
    {"success": [{"line": "a line", "verify": 5}], "failure": []},
    {"success": [{"line": "ok", "verify": "fine"}], "failure": ["a failure line with no verify"]},
])
def test_a_kpi_line_without_a_verify(tmp_path, kpis):
    refused(fixture(tmp_path), {REVIEW: {**REVIEW_ANSWER, "kpis": kpis}}, "VERIFY_PASS_KPI_NO_VERIFY", tmp_path)


@pytest.mark.parametrize("verify", ["", "  ", "TBD", "todo.", " N/A ", "none"])
def test_a_kpi_verify_that_is_no_text_of_its_own(tmp_path, verify):
    items = [{"line": "a line", "verify": verify}] + ([f"a line Verify: {verify}"] if verify.strip() else [])
    for item in items:  # a string with nothing after ``Verify:`` carries no verify at all (kpi_rows)
        refused(fixture(tmp_path / str(len(str(item)))), {REVIEW: {**REVIEW_ANSWER, "kpis": {"success": [item],
                "failure": []}}}, "VERIFY_PASS_EMPTY_CLAUSE", tmp_path)


def test_a_kpi_line_as_a_string_with_its_verify_is_accepted(tmp_path):
    root = fixture(tmp_path)
    kpis = {"success": ["a line Verify: the check"], "failure": []}
    verify_pass.apply(root, answers_file(tmp_path, {REVIEW: {**REVIEW_ANSWER, "kpis": kpis}}), "s", TODAY)
    assert [row[2] for row in kpi_rows(front(root, REVIEW))] == ["the check"]


@pytest.mark.parametrize("field, value", [
    ("kpis", {"failure": []}), ("kpis", {"success": [], "failure": []}), ("kpis", []), ("kpis", "text"),
    ("kpis", {"success": [{"line": "a", "verify": "b"}]}), ("kpis", {"success": [{"line": "", "verify": "b"}], "failure": []}),
    ("kpis", {"success": [{"line": "a", "verify": "b", "extra": 1}], "failure": []}),
    ("kpis", {"success": [5], "failure": []}), ("kpis", {"success": [""], "failure": []}),
    ("reads", "a.md"), ("reads", [""]), ("reads", [5]), ("reads", None),
    ("needs", {"a": "b"}), ("needs", ["a", ""]),
    ("waits_on", "exa-dt1z"), ("waits_on", [5]), ("waits_on", [{"ref": "a"}]), ("waits_on", [{"reason": "a"}]),
    ("waits_on", [{"ref": "a", "reason": ""}]), ("waits_on", [{"ref": "a", "reason": "b", "on": "c"}]), ("waits_on", [""]),
    ("role", 5), ("role", ["engineer"]), ("role", None),
])
def test_a_field_value_that_is_not_the_form(tmp_path, field, value):
    refused(fixture(tmp_path), {REVIEW: {**REVIEW_ANSWER, field: value}}, "VERIFY_PASS_BAD_FIELD", tmp_path)


def test_a_field_the_ticket_already_has_is_never_overwritten(tmp_path):
    for field in SIX:
        had = {"role": "role: engineer\n", "allowed_paths": "allowed_paths: [src/x.py]\n",
               "kpis": "kpis:\n  success: [x]\n  failure: []\n", "reads": "reads: []\n", "needs": "needs: []\n",
               "waits_on": "waits_on: []\n"}[field]
        root = fixture(tmp_path / field, **{REVIEW: bare(REVIEW, keys=had)})
        refused(root, {REVIEW: REVIEW_ANSWER}, "VERIFY_PASS_FIELD_SET", tmp_path / field)


def test_an_answer_for_a_field_that_holds_none_is_a_set_field_too(tmp_path):
    root = fixture(tmp_path, **{REVIEW: bare(REVIEW, keys="reads: []\nneeds:\nwaits_on: []\n")})
    refused(root, {REVIEW: {**REVIEW_ANSWER, "needs": []}}, "VERIFY_PASS_FIELD_SET", tmp_path)


def test_a_lacking_field_the_answers_do_not_supply_is_unanswered_and_the_ticket_stays_unmarked(tmp_path):
    root = fixture(tmp_path)
    for missing in SIX:
        entry = {key: value for key, value in REVIEW_ANSWER.items() if key != missing}
        refused(root, {REVIEW: entry}, "VERIFY_PASS_UNANSWERED", tmp_path)
    refused(root, {REVIEW: {}}, "VERIFY_PASS_UNANSWERED", tmp_path)
    assert "verify_pass" not in (root / f".tickets/{REVIEW}.md").read_text(encoding="utf-8")


def test_a_label_answer_alone_on_a_ticket_that_also_lacks_fields_is_unanswered(tmp_path):
    keys = "kpis:\n  success: [plain line]\n  failure: []\n"
    refused(fixture(tmp_path, **{"abc-1111": bare("abc-1111", keys=keys)}), {"abc-1111": {"S1": "c"}},
            "VERIFY_PASS_UNANSWERED", tmp_path)


def test_a_key_that_is_neither_a_label_nor_one_of_the_six_fields_is_an_unknown_label(tmp_path):
    for key in ("state_class", "non_goals", "type", "class", "profile", "S1", "F1", "s1", "Role"):
        refused(fixture(tmp_path / key), {REVIEW: {**REVIEW_ANSWER, key: "x"}}, "VERIFY_PASS_UNKNOWN_LABEL", tmp_path)


def test_a_ticket_that_would_fail_the_ticket_schema_is_refused_and_nothing_is_written(tmp_path):
    # tk's own output has no state_class (L16); a tk id of another shape fails the id pattern
    root = fixture(tmp_path / "a", **{COORD: bare(COORD, state_class="")})
    refused(root, {COORD: COORD_ANSWER}, "VERIFY_PASS_SCHEMA", tmp_path)
    root = fixture(tmp_path / "b", **{"DAEO-a1": bare("DAEO-a1")})
    refused(root, {"DAEO-a1": COORD_ANSWER}, "VERIFY_PASS_SCHEMA", tmp_path)
    root = fixture(tmp_path / "c", **{COORD: bare(COORD, state_class="state_class: MADE_UP\n")})
    refused(root, {COORD: COORD_ANSWER}, "VERIFY_PASS_SCHEMA", tmp_path)


def test_a_schema_copy_inside_the_repository_is_never_the_one_that_judges(tmp_path):
    root = fixture(tmp_path, **{COORD: bare(COORD, state_class="")})
    for rel in ("template/governance/kernel/schemas", "governance/kernel/schemas"):
        (root / rel).mkdir(parents=True)
        (root / rel / "ticket.schema.json").write_text("{}", encoding="utf-8")
        (root / rel / "common.schema.json").write_text("{}", encoding="utf-8")
    refused(root, {COORD: COORD_ANSWER}, "VERIFY_PASS_SCHEMA", tmp_path)


def test_one_planted_refusal_in_one_ticket_writes_nothing_to_the_other(tmp_path):
    root = fixture(tmp_path)
    refused(root, {COORD: COORD_ANSWER, REVIEW: {**REVIEW_ANSWER, "allowed_paths": ["tests/**"]}},
            "VERIFY_PASS_ACCEPTANCE_PATH", tmp_path)
    refused(root, {REVIEW: REVIEW_ANSWER, COORD: {**COORD_ANSWER, "role": "owner"}}, "VERIFY_PASS_UNKNOWN_ROLE", tmp_path)
    refused(root, {COORD: COORD_ANSWER, "exa-zzzz": REVIEW_ANSWER}, "VERIFY_PASS_UNKNOWN_TICKET", tmp_path)


def test_a_closed_ticket_is_not_given_fields(tmp_path):
    refused(fixture(tmp_path, **{COORD: bare(COORD, "closed")}), {COORD: COORD_ANSWER}, "VERIFY_PASS_CLOSED", tmp_path)


def test_the_answers_file_form_of_the_fields_is_the_yaml_a_hand_writes(tmp_path):
    root = fixture(tmp_path)
    path = tmp_path / "answers.yaml"
    path.write_text(f"""{REVIEW}:
  role: independent-auditor
  allowed_paths: ['{VERDICT}/**']
  reads: [CLAUDE.md]
  needs: []
  waits_on:
  - {COORD}
  - ref: {REVIEW}
    reason: itself   # a ref may name any ticket
  kpis:
    success:
    - line: the verdict is committed
      verify: the command exits 0
    failure: []
""", encoding="utf-8")
    assert verify_pass.apply(root, path, "s", TODAY) == [REVIEW]
    assert front(root, REVIEW)["waits_on"] == [COORD, {"ref": REVIEW, "reason": "itself"}]
