"""KPI 1 and 2, failure 1: the decisions validator's register checks (S1, S2).

Every entry has a domain from the closed list, a scope, a lands-in tag naming a file ``HEAD`` holds where its scope
says, and a status that names what superseded or changed it; ``gov.decisions.check_tags(root)`` and
``python3 -m gov.decisions.tags`` name each entry that has not. W2-03's ``gov.decisions.check(root)`` keeps its own
codes.
"""

from __future__ import annotations

import pytest

import w2_55_support as s

K, P = s.KERNEL_PLACE, s.PROJECT_PLACE

# The fully tagged register: every domain once, both scopes, an entry landing in two places, a marked supersession,
# a marked change, a superseded and a done entry landing nowhere.
GOOD = {}
for number, domain in enumerate(s.DOMAINS, start=101):
    scope = "kernel" if number % 2 else "repository"
    GOOD[f"DEC-{number}"] = dict(title=f"The {domain} rule", tags_line=s.tags(domain, scope, K if number % 2 else P))
GOOD.update({
    "DEC-112": dict(title="The two-place rule",
                    tags_line=s.tags("plan", "repository", f"{s.KERNEL_PLACE_2}, {s.PROMPT_PLACE}")),
    "DEC-113": dict(title="The old lamp rule", status="SUPERSEDED by DEC-114 · **Basis:** OWNER",
                    tags_line=s.tags("guard", "kernel", "none")),
    "DEC-114": dict(title="The lamp rule, restated", status="ACCEPTED · **Basis:** OWNER · **Supersedes:** DEC-113",
                    tags_line=s.tags("guard", "kernel", K)),
    "DEC-115": dict(title="The mast rule", status="ACCEPTED · **Basis:** OWNER · **Changed by:** DEC-116",
                    tags_line=s.tags("roles", "kernel", s.KERNEL_PLACE_2)),
    "DEC-116": dict(title="The mast rule's height", status="ACCEPTED · **Basis:** OWNER · **Changes:** DEC-115",
                    tags_line=s.tags("roles", "kernel", s.KERNEL_PLACE_2)),
    "DEC-117": dict(title="The one-off count of lanterns", tags_line=s.tags("records", "repository", "none", True)),
})


def register_text(**changes):
    """The good register with the named entries' fields replaced (``DEC_103={"tags_line": None}``)."""
    entries = []
    for entry_id, fields in GOOD.items():
        fields = {**fields, **changes.get(entry_id.replace("-", "_"), {})}
        entries.append(s.entry(entry_id, fields["title"], fields.get("status", "ACCEPTED · **Basis:** OWNER"),
                               fields.get("tags_line")))
    return s.register(*entries)


def check(api, tmp_path, text, files=None):
    project = s.build_project(tmp_path / "repo", text, files)
    return project, api.findings(project.root, "check_tags")


def only_about(found, entry_id):
    """Every finding names ``entry_id`` and the register: nothing else in the good register is found."""
    for finding in found:
        assert entry_id in finding["ids"], f"a finding names another entry than {entry_id}:\n{s.show(found)}"
        assert s.REGISTER in finding["paths"], f"a finding does not name the register:\n{s.show(found)}"


def assert_found(found, code, entry_id, word=None):
    hits = s.naming(found, code, entry_id)
    assert hits, f"no {code} finding names {entry_id}:\n{s.show(found)}"
    if word is not None:
        assert any(word in f["message"] for f in hits), f"no {code} finding of {entry_id} says {word!r}:\n{s.show(found)}"
    only_about(found, entry_id)


# --------------------------------------------------------------------------
# A fully tagged register passes
# --------------------------------------------------------------------------

def test_a_fully_tagged_register_passes(api, tmp_path):
    _, found = check(api, tmp_path, register_text())
    assert found == [], f"the fully tagged register gave findings:\n{s.show(found)}"


def test_the_tags_command_exits_0_on_a_fully_tagged_register(api, tmp_path):
    project = s.build_project(tmp_path / "repo", register_text())
    answer = api.module(project.root, "gov.decisions.tags")
    assert answer.returncode == 0, f"python3 -m gov.decisions.tags did not pass a fully tagged register\n" \
                                   f"{answer.describe()}"


def test_the_tags_command_exits_1_and_names_the_entry(api, tmp_path):
    project = s.build_project(tmp_path / "repo", register_text(DEC_104={"tags_line": None}))
    answer = api.module(project.root, "gov.decisions.tags")
    assert answer.returncode == 1, answer.describe()
    assert "DEC-104" in answer.stdout + answer.stderr and "TAG_MISSING" in answer.stdout + answer.stderr, \
        f"the command's output does not name the entry and its finding\n{answer.describe()}"


# --------------------------------------------------------------------------
# KPI 1, failure 1: domain, scope and status
# --------------------------------------------------------------------------

def test_an_entry_without_a_tags_line_is_named(api, tmp_path):
    _, found = check(api, tmp_path, register_text(DEC_103={"tags_line": None}))
    assert_found(found, "TAG_MISSING", "DEC-103")


@pytest.mark.parametrize("missing, line", [
    ("domain", f"- **Tags:** scope: kernel · lands in: {K}"),
    ("scope", f"- **Tags:** domain: retrieval · lands in: {K}"),
    ("lands in", "- **Tags:** domain: retrieval · scope: kernel"),
])
def test_a_tags_line_without_a_part_is_named_with_the_part(api, tmp_path, missing, line):
    _, found = check(api, tmp_path, register_text(DEC_103={"tags_line": line}))
    assert_found(found, "TAG_MISSING", "DEC-103", word=missing)


def test_a_domain_outside_the_closed_list_is_refused(api, tmp_path):
    _, found = check(api, tmp_path, register_text(DEC_105={"tags_line": s.tags("security", "kernel", K)}))
    assert_found(found, "TAG_DOMAIN_UNKNOWN", "DEC-105")


def test_a_scope_outside_the_two_is_refused(api, tmp_path):
    _, found = check(api, tmp_path, register_text(DEC_105={"tags_line": s.tags("guard", "global", K)}))
    assert_found(found, "TAG_SCOPE_UNKNOWN", "DEC-105")


def test_a_superseded_entry_naming_no_successor_is_named(api, tmp_path):
    _, found = check(api, tmp_path, register_text(DEC_113={"status": "SUPERSEDED · **Basis:** OWNER"}))
    assert_found(found, "STATUS_SUCCESSOR_UNNAMED", "DEC-113")


def test_a_superseded_entry_naming_a_successor_the_register_does_not_hold_is_named(api, tmp_path):
    text = register_text(DEC_113={"status": "SUPERSEDED by DEC-999 · **Basis:** OWNER"},
                         DEC_114={"status": "ACCEPTED · **Basis:** OWNER"})
    _, found = check(api, tmp_path, text)
    assert_found(found, "STATUS_SUCCESSOR_UNNAMED", "DEC-113")


def test_an_entry_another_supersedes_whose_status_does_not_name_it_is_named_old_first(api, tmp_path):
    text = register_text(DEC_113={"status": "ACCEPTED · **Basis:** OWNER", "tags_line": s.tags("guard", "kernel", K)})
    _, found = check(api, tmp_path, text)
    hits = s.naming(found, "STATUS_RELATION_UNMARKED", "DEC-113")
    assert hits and all(f["ids"][:2] == ["DEC-113", "DEC-114"] for f in hits), \
        f"no STATUS_RELATION_UNMARKED finding with ids [DEC-113, DEC-114]:\n{s.show(found)}"


@pytest.mark.parametrize("field", ["Changes", "Settles", "Corrects", "Reverses", "Withdraws"])
def test_an_entry_another_changes_whose_status_does_not_name_it_is_named_old_first(api, tmp_path, field):
    text = register_text(DEC_115={"status": "ACCEPTED · **Basis:** OWNER"},
                         DEC_116={"status": f"ACCEPTED · **Basis:** OWNER · **{field}:** DEC-115"})
    _, found = check(api, tmp_path, text)
    hits = s.naming(found, "STATUS_RELATION_UNMARKED", "DEC-115")
    assert hits and all(f["ids"][:2] == ["DEC-115", "DEC-116"] for f in hits), \
        f"no STATUS_RELATION_UNMARKED finding with ids [DEC-115, DEC-116] for **{field}:**:\n{s.show(found)}"


# --------------------------------------------------------------------------
# KPI 2: lands in
# --------------------------------------------------------------------------

def test_a_place_head_does_not_hold_is_named(api, tmp_path):
    missing = "template/governance/kernel/skills/nowhere/SKILL.md"
    _, found = check(api, tmp_path, register_text(DEC_107={"tags_line": s.tags("launch", "kernel", missing)}))
    assert_found(found, "TAG_LANDS_IN_UNKNOWN", "DEC-107")


def test_a_place_only_in_the_working_tree_is_not_held_by_head(api, tmp_path):
    loose = "template/governance/kernel/skills/loose/SKILL.md"
    project = s.build_project(tmp_path / "repo", register_text(DEC_107={"tags_line": s.tags("launch", "kernel", loose)}))
    project.write(loose, "# Written, never committed\n")
    found = api.findings(project.root, "check_tags")
    assert_found(found, "TAG_LANDS_IN_UNKNOWN", "DEC-107")


@pytest.mark.parametrize("scope, place", [("kernel", P), ("repository", K)])
def test_a_place_outside_where_its_scope_says_is_named(api, tmp_path, scope, place):
    _, found = check(api, tmp_path, register_text(DEC_107={"tags_line": s.tags("launch", scope, place)}))
    assert_found(found, "TAG_LANDS_IN_MISPLACED", "DEC-107")


def test_none_on_an_entry_in_force_is_named(api, tmp_path):
    _, found = check(api, tmp_path, register_text(DEC_107={"tags_line": s.tags("launch", "kernel", "none")}))
    hits = [f for f in s.naming(found, None, "DEC-107")
            if f["code"] in ("TAG_MISSING", "TAG_LANDS_IN_UNKNOWN", "TAG_LANDS_IN_MISPLACED")]
    assert hits, f"`lands in: none` on an entry in force gave no lands-in finding:\n{s.show(found)}"
    only_about(found, "DEC-107")


def test_none_on_a_done_or_superseded_entry_is_no_finding(api, tmp_path):
    # the good register holds both (DEC-113 superseded, DEC-117 done); a second done entry, scoped to the kernel
    text = register_text(DEC_111={"tags_line": s.tags("release", "kernel", "none", done=True)})
    _, found = check(api, tmp_path, text)
    assert found == [], f"`lands in: none` on done or superseded entries gave findings:\n{s.show(found)}"


# --------------------------------------------------------------------------
# W2-03's checker keeps its own list
# --------------------------------------------------------------------------

def test_w2_03s_check_keeps_its_own_codes(api, tmp_path):
    text = register_text(DEC_103={"tags_line": None}, DEC_105={"tags_line": s.tags("security", "global", "none")},
                         DEC_113={"status": "SUPERSEDED · **Basis:** OWNER"})
    project = s.build_project(tmp_path / "repo", text)
    found = api.findings(project.root, "check")
    added = [f for f in found if f["code"] in s.TAG_CODES]
    assert not added, f"gov.decisions.check(root) reports the register checks:\n{s.show(added)}"
