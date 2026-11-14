"""S8 and F4: the record ``docs/research/W2-130-link-cleanup.md`` holds what the interface names; the clean-up began
only after W2-129 landed and W2-92's links were adopted, on the owner's word."""

from __future__ import annotations

import collections

import pytest

import w2_130_support as s

LANG = {name: "yaml" for name in s.BLOCKS}
LANG.update({"patch-a0": "diff", "patch-a1": "diff", "patch-a2": "diff", "patch-b1": "diff",
             "patch-sources-2": "diff", "patch-marks-3": "diff", "recount": "python", "drift": "python"})
AREAS = {"D-5": ("template/", "docs/contract/"), "D-6": ("src/", "tests/"), "D-9": (".tickets/",)}


def test_s8_the_record_exists_and_holds_each_block_the_interface_names_once(record):
    record.need()
    assert len(record.opens) == len(set(record.opens)), "a block name appears twice"
    missing = [name for name in s.BLOCKS if name not in record.blocks]
    assert not missing, f"blocks missing: {missing}"
    wrong = [(name, record.blocks[name][0]) for name in s.BLOCKS if record.blocks[name][0] != LANG[name]]
    assert not wrong, f"blocks in the wrong language: {wrong}"


def test_s8_the_commits_block_names_the_fixed_facts_and_each_list(record):
    commits = record.commits()
    for key, short in (("starting_head", s.START), ("first_commit", s.FIRST), ("w2_129_landing", s.W2_129_LANDING),
                       ("w2_92_adoption", s.W2_92_ADOPTION), ("status_decision_commit", s.DEC1098_COMMIT),
                       ("sitting_commit", s.SITTING_COMMIT)):
        assert s.need_hash(commits.get(key), f"commits.{key}") == s.full(short), f"commits.{key} is not {short}"
    assert commits.get("start_decision") == "DEC-1097 (9)" and commits.get("status_decision") == "DEC-1098 (3)"
    cleanup = record.commit_list("cleanup")
    assert cleanup[:2] == [s.full(s.FIRST), s.full(s.SECOND)], "commits.cleanup must start e12f8a30c, c4420040f"
    assert all(s.is_ancestor(a, b) and a != b for a, b in zip(cleanup, cleanup[1:])), "cleanup is not in order"
    for key in ("marks", "sources", "status"):
        assert set(record.commit_list(key)) <= set(cleanup), f"commits.{key} names a commit not in cleanup"
    assert {record.commit_list("r12")[0], record.commit_list("lessons")[0]} <= set(cleanup)
    assert record.commit_list("marks")[:2] == [s.full(s.FIRST), s.full(s.SECOND)]
    assert s.full(s.FIRST) in record.commit_list("sources") and s.full(s.SECOND) in record.commit_list("status")


def _by(findings, key):
    return {k: dict(v) for k, v in key(findings).items()}


def _counts(findings, head_tree) -> dict:
    by_code, by_role = collections.Counter(), collections.defaultdict(collections.Counter)
    unlinked = collections.Counter()
    for f in findings:
        by_code[f["code"]] += 1
        by_role[f["code"]][f["role"]] += 1
        if f["code"] == "UNLINKED_ID" and f["path"].startswith(".tickets/"):
            unlinked[s.ticket_status((head_tree / f["path"]).read_text(encoding="utf-8"))] += 1
    return {"by_code": dict(by_code), "by_code_role": {c: dict(r) for c, r in by_role.items()},
            "unlinked_by_status": dict(unlinked)}


def _shape(block, name):
    assert isinstance(block, dict) and {"head", "command", "by_code", "by_code_role", "unlinked_by_status"} <= set(block), (
        f"{name} lacks head, command, by_code, by_code_role or unlinked_by_status")
    assert "gov links" in str(block["command"]) and "--all" in str(block["command"]), f"{name}.command is not a gov links --all run"


def test_s8_counts_before_are_at_the_starting_head_and_counts_after_at_the_last_cleanup_commit(record):
    before, after = record.data("counts-before"), record.data("counts-after")
    _shape(before, "counts-before")
    _shape(after, "counts-after")
    assert s.need_hash(before["head"], "counts-before.head") == s.full(s.START)
    assert s.need_hash(after["head"], "counts-after.head") == record.commit_list("cleanup")[-1]


def _measured_at(record) -> str:
    """``counts-after.measured_at``: the tree the record says it counted. Pinned, not HEAD: a ticket closed or reopened
    after the land moves what ``gov links`` finds at HEAD (122 -> 124 CLOSED_TICKET_EDITED in five hours), and the
    record's counts must not turn red for it (DEC-1156 (7), DEC-1164 (18)). The tree is one this branch really holds:
    ``counts-after.head`` (the last clean-up commit) or a descendant of it, and an ancestor of HEAD."""
    after = record.data("counts-after")
    _shape(after, "counts-after")
    if "measured_at" not in after:
        pytest.fail("counts-after lacks measured_at, the tree the counts were taken at")
    measured = s.need_hash(after["measured_at"], "counts-after.measured_at")
    last_cleanup = s.need_hash(after["head"], "counts-after.head")
    assert s.is_ancestor(last_cleanup, measured), "counts-after.measured_at is not counts-after.head or a descendant of it"
    assert s.is_ancestor(measured, s.head()), "counts-after.measured_at is not an ancestor of HEAD"
    return measured


def test_s8_gov_links_at_head_gives_the_after_counts(record, clone_at, home):
    """Runs ``gov links`` on a clone at ``counts-after.measured_at`` (the tree the record says it counted), not at HEAD, and
    compares the record's after counts with it. The name is kept because the README map names it (DEC-1156 (7) pin run)."""
    after = record.data("counts-after")
    tree = clone_at(_measured_at(record))
    mine = _counts(s.links_json(tree, home), tree)
    assert {k: v for k, v in after["by_code"].items() if v} == mine["by_code"], "by_code differs from gov links at measured_at"
    assert {c: {r: n for r, n in rs.items() if n} for c, rs in after["by_code_role"].items() if sum(rs.values())} == mine["by_code_role"], (
        "by_code_role differs from gov links at measured_at")
    assert {k: v for k, v in after["unlinked_by_status"].items() if v} == mine["unlinked_by_status"], (
        "unlinked_by_status differs from gov links at measured_at")


def test_s8_the_before_counts_of_the_codes_the_clean_up_works_on_equal_gov_links_at_the_starting_head(record, start_findings):
    """Tool-version sensitive: HEAD's gov links run on the starting head, for the three codes the ticket names."""
    before = record.data("counts-before")
    _shape(before, "counts-before")
    mine = collections.Counter(f["code"] for f in start_findings)
    for code in ("UNMARKED_CHANGE", "UNLINKED_ID", "STATUS_CONFLICT"):
        assert before["by_code"].get(code, 0) == mine.get(code, 0), f"{code}: record {before['by_code'].get(code, 0)}, gov links {mine.get(code, 0)}"


def test_s8_left_holds_d_5_d_6_and_d_9_by_path_and_role_as_gov_links_finds_them_at_head(record, clone_at, home):
    """Compares ``left`` (D-5, D-6, D-9 by path and role) with what ``gov links`` finds on a clone at
    ``counts-after.measured_at``, not at HEAD. The name is kept because the README map names it (DEC-1156 (7) pin run)."""
    left = record.data("left")
    assert isinstance(left, dict) and {"D-5", "D-6", "D-9"} <= set(left), "left lacks D-5, D-6 or D-9"
    findings = s.links_json(clone_at(_measured_at(record)), home)
    for area, prefixes in AREAS.items():
        mine = collections.defaultdict(dict)
        for f in findings:
            if f["path"].startswith(prefixes):
                mine[f["path"]][f["role"]] = mine[f["path"]].get(f["role"], 0) + 1
        assert isinstance(left[area], dict), f"left.{area} is not a mapping path -> role -> n"
        assert {p: dict(r) for p, r in left[area].items()} == dict(mine), f"left.{area} differs from the findings at measured_at"


def test_f4_e12f8a30c_has_w2_129_s_landing_and_w2_92_s_stated_links_as_ancestors():
    assert s.is_ancestor(s.W2_129_LANDING, s.FIRST)
    assert s.is_ancestor(s.W2_92_ADOPTION, s.FIRST)


def test_f4_the_record_cites_dec_1097_9_the_owner_s_decision_that_allowed_the_start(record):
    record.need()
    assert "DEC-1097 (9)" in record.text
    assert record.commits().get("start_decision") == "DEC-1097 (9)"
