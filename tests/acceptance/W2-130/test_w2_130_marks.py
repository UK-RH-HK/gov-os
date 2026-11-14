"""S1 and S2: the marks. The 87 first, then the rest; what gov links and the drift script still find at HEAD."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w2_130_support as s


def _head_lines(head_tree) -> dict:
    return {entry: line for entry, _, line in s.entries((head_tree / s.REGISTER).read_text(encoding="utf-8"))}


def _judged(record) -> set:
    data = record.data("judged-wrong")
    if not isinstance(data, list):
        pytest.fail("w2-130:judged-wrong is not a list")
    return {s.pair(item) for item in data}


# ---------------------------------------------------------------------------------------------------- S1 (history)


def test_s1_the_first_cleanup_commit_is_e12f8a30c_and_its_parent_is_the_starting_head():
    assert s.parent(s.FIRST) == s.full(s.START)


def test_s1_register_hunks_of_e12f8a30c_are_status_line_appends_only():
    delta = s.register_delta(s.START, s.FIRST)
    assert delta["same_ids"], "e12f8a30c adds or removes a register entry"
    assert delta["masked_equal"], "e12f8a30c changes a register line that is not an entry's status line"
    assert delta["changes"], "e12f8a30c changes no status line"
    bad = [c["id"] for c in delta["changes"] if c["kind"] != "append"]
    assert not bad, f"status lines of {bad} are not the old line kept whole with marks appended"


def test_s1_every_mark_e12f8a30c_appends_is_still_on_its_status_line_at_head(head_tree):
    lines = _head_lines(head_tree)
    marks = s.added_marks(s.FIRST)
    assert marks, "e12f8a30c appends no mark"
    missing = [(m["changed"], m["changer"]) for m in marks if not s.names_changer(lines[m["changed"]], m["changer"])]
    assert not missing, f"marks e12f8a30c appended and HEAD's status lines do not name: {missing[:5]}"


# ------------------------------------------------------------------------------------------------- S1 (the record)


def test_s1_the_record_names_e12f8a30c_as_the_first_commit_and_the_starting_head(record):
    commits = record.commits()
    assert s.need_hash(commits.get("first_commit"), "commits.first_commit") == s.full(s.FIRST)
    assert s.need_hash(commits.get("starting_head"), "commits.starting_head") == s.full(s.START)
    marks = s.marks_commits(record)
    assert s.full(s.FIRST) in marks and s.full(s.SECOND) in marks, "commits.marks lacks e12f8a30c or c4420040f"


def test_s1_ids_87_are_87_distinct_ids_each_a_key_of_the_census(record):
    ids = record.data("ids-87")
    census = record.data("census")
    assert isinstance(ids, list) and len(ids) == 87, f"ids-87 holds {len(ids) if isinstance(ids, list) else ids!r}"
    assert len(set(ids)) == 87, "ids-87 repeats an id"
    assert isinstance(census, dict) and not [i for i in ids if i not in census], "an id of ids-87 is no census key"


def test_s1_each_of_the_87_names_every_changer_the_census_states_on_its_own_status_line(record, head_tree):
    ids, census = record.data("ids-87"), record.data("census")
    judged, lines = _judged(record), _head_lines(head_tree)
    missing = []
    for entry in ids:
        changers = census[entry]
        assert isinstance(changers, list) and changers, f"census states no changer for {entry}"
        for changer in changers:
            if (entry, changer) not in judged and not s.names_changer(lines[entry], changer):
                missing.append((entry, changer))
    assert not missing, f"{len(missing)} census pairs of the 87 are not named on their status line: {missing[:6]}"


def test_s1_the_marks_e12f8a30c_adds_equal_patches_a0_a1_a2_after_the_audits_drops_and_rewrites(record):
    patched, touched = set(), set()
    for name in ("patch-a0", "patch-a1", "patch-a2"):
        patch = record.block(name, "diff")
        patched |= s.patch_register_pairs(patch, s.START)  # a0 (the archive's lines) holds no register hunk
        touched |= set(s.patch_sections(patch))
    assert touched <= set(s.changed_files(s.FIRST)), (
        f"patches a0-a2 change files e12f8a30c does not: {sorted(touched - set(s.changed_files(s.FIRST)))}")
    assert patched, "patches a0-a2 hold no mark of a register status line"
    items = s.audits_by_commit(record).get(s.full(s.FIRST))
    assert items is not None, "audits has no item for e12f8a30c"
    judged = s.audit_marks(items, "free_text") + s.audit_marks(items, "labelled")
    dropped = {(m["changed"], m["changer"]) for m in judged if m["fate"] == "dropped"}
    corrected = {(m["changed"], c) for m in judged if m["fate"] == "corrected"
                 for c in s.ids_in(str(m.get("committed_mark", "")))}
    expected = (patched - dropped) | corrected
    assert s.committed_pairs(s.FIRST) == expected, (
        f"e12f8a30c adds {len(s.committed_pairs(s.FIRST))} marks; patches a0-a2 after the drops give {len(expected)}")


def test_s1_a_mark_on_one_of_the_87_added_after_e12f8a30c_is_in_a_marks_commit_and_append_only(record):
    # The line is about the clean-up's marks, the census's pairs: one of them added after e12f8a30c is in c4420040f
    # or a follow-up marks commit, append-only. A later commit's own change of a status line of the 87 (DEC-866's
    # marking of a new decision's change, e.g. 518772b5c's DEC-989<-DEC-1141) adds no census pair; it may stay out of
    # a marks commit, but its line must keep the old line whole (an append), never an edit in the middle.
    ids = set(record.data("ids-87"))
    census = record.data("census")
    allowed = set(s.marks_commits(record))
    log = s.git("log", "--reverse", "--no-merges", "--format=%H", f"{s.full(s.FIRST)}..HEAD", "--", s.REGISTER)
    bad = []
    for commit in log.split():
        for change in s.register_delta(s.parent(commit), commit)["changes"]:
            if change["id"] not in ids:
                continue
            if commit in allowed:
                if change["kind"] not in ("append", "status"):
                    bad.append((commit[:12], change["id"], change["kind"]))
                continue
            tail = change["new"][len(change["old"]):]
            if not change["new"].startswith(change["old"]):
                bad.append((commit[:12], change["id"], "edited outside a marks commit, not an append"))
            elif set(s.ids_in(tail)) & set(census[change["id"]]):
                bad.append((commit[:12], change["id"], "a census pair marked outside a marks commit"))
    assert not bad, f"a register status line of the 87 changed outside a marks commit or not append-only: {bad[:5]}"


# ---------------------------------------------------------------------------------------------------------- S2


def test_s2_gov_links_reports_no_unmarked_change_but_the_eight_pairs_the_auditor_judged_wrong(head_findings):
    found = set(s.by_pair(head_findings))
    assert found == set(s.EIGHT), (f"extra: {sorted(found - set(s.EIGHT))}; missing: "
                                   f"{sorted(set(s.EIGHT) - found)}")


def test_s2_judged_wrong_holds_the_eight_gov_links_pairs_each_with_the_auditors_verdict(record):
    data = record.data("judged-wrong")
    assert isinstance(data, list), "w2-130:judged-wrong is not a list"
    by = {s.pair(item): item for item in data}
    for key in s.EIGHT:
        assert key in by, f"judged-wrong lacks {key}"
        item = by[key]
        assert item.get("in_gov_links") is True, f"{key} is reported by gov links: in_gov_links must be true"
    for key, item in by.items():
        assert str(item.get("verdict", "")).strip(), f"{key} has no verdict quoted"
        assert str(item.get("finding", "")).strip(), f"{key} names no finding id"
        assert isinstance(item.get("in_gov_links"), bool), f"{key}: in_gov_links is not true or false"
    in_gov = {key for key, item in by.items() if item["in_gov_links"]}
    assert in_gov == set(s.EIGHT), "in_gov_links: true must hold exactly the 8 gov links pairs"


@pytest.mark.parametrize("changed,changer", [("DEC-1115", "DEC-1122"), ("DEC-026", "DEC-086")],
                         ids=["dec-1115-dec-1122", "dec-026-dec-086"])
def test_s2_the_two_follow_up_marks_are_in_a_marks_commit_after_a_right_verdict(record, head_tree, changed, changer):
    # The pair is the line's; the mark's own wording (its part) is the auditor's to correct (S3), so the commit is
    # the one follow-up marks commit that makes the entry's status line name the changer, appended to the old line.
    assert s.names_changer(_head_lines(head_tree)[changed], changer), f"HEAD's {changed} does not name {changer}"
    audits, first, second = s.audits_by_commit(record), s.full(s.FIRST), s.full(s.SECOND)
    found = []
    for commit in s.marks_commits(record):
        if commit in (first, second) or not (s.is_ancestor(first, commit) and s.is_ancestor(second, commit)):
            continue
        for change in s.register_delta(s.parent(commit), commit)["changes"]:
            if (change["id"] == changed and change["kind"] == "append" and changer in s.ids_in(change["tail"])
                    and s.names_changer(change["new"], changer) and not s.names_changer(change["old"], changer)):
                found.append(commit)
    assert len(found) == 1, f"{changed}: {len(found)} follow-up marks commits append a mark naming {changer}"
    item = audits.get(found[0])
    assert item is not None, "no audits item for the follow-up marks commit"
    marks = [m for key in ("free_text", "labelled") for m in s.audit_marks(item, key)
             if (m["changed"], m["changer"]) == (changed, changer)]
    assert marks and all(m["verdict"] == "right" for m in marks), f"the audit does not judge {changed}<-{changer} right"
    assert s.is_ancestor(str(item["audit_head"]), found[0]), "the audit head is no ancestor of the commit"
    when = s.parse_when(item.get("audit_date"))
    assert when is not None and when < s.committer_date(found[0]), "the audit is not dated before the commit"


def test_s2_census_has_215_keys_and_archive_13_has_13_distinct_pairs(record):
    census, archive = record.data("census"), record.data("archive-13")
    assert isinstance(census, dict) and len(census) == 215, f"census holds {len(census) if census else census!r}"
    assert isinstance(archive, list) and len({s.pair(item) for item in archive}) == 13, "archive-13 is not 13 pairs"


def test_s2_each_census_id_names_every_stated_changer_unless_the_auditor_judged_the_pair_wrong(record, head_tree):
    # "Named on its own status line" is gov links' own test (check.py's UNMARKED_CHANGE: the changer's id is on the
    # entry's status line). The form (**Changed by:** / SUPERSEDED by) is the S1 line's, for the 87 (checked there);
    # the other census ids name some changers in the register's older forms (**Amended by:**, **Lifted by:**, prose).
    census, judged, lines = record.data("census"), _judged(record), _head_lines(head_tree)
    missing = []
    for entry, changers in census.items():
        assert isinstance(changers, list) and changers, f"census states no changer for {entry}"
        missing += [(entry, c) for c in changers if (entry, c) not in judged and c not in s.ids_in(lines[entry])]
    assert not missing, f"{len(missing)} census pairs are not on their status line: {missing[:6]}"


def test_s2_each_archive_only_pair_names_its_changer_unless_the_auditor_judged_it_wrong(record, head_tree):
    judged, lines = _judged(record), _head_lines(head_tree)
    pairs = [s.pair(item) for item in record.data("archive-13")]
    missing = [(a, b) for a, b in pairs if (a, b) not in judged and not s.names_changer(lines[a], b)]
    assert not missing, f"archive-only pairs not on their status line: {missing}"


def _drift(record, head_tree) -> dict:
    done = subprocess.run([sys.executable, "-"], input=record.block("drift", "python"), cwd=head_tree,
                          capture_output=True, text=True, check=False, timeout=300)
    assert done.returncode == 0, f"the drift script failed: {done.stderr.strip()[-300:]}"
    try:
        return json.loads(done.stdout)
    except ValueError:
        pytest.fail(f"the drift script printed no JSON object: {done.stdout[:200]!r}")


def test_s2_the_drift_script_on_head_leaves_no_pair_once_the_listed_pairs_are_set_aside(record, head_tree):
    out = _drift(record, head_tree)
    assert isinstance(out.get("drift"), list) and out.get("count") == len(out["drift"]), "drift output form"
    run = record.data("drift-run")
    aside = {s.pair(item) for item in run.get("set_aside", [])}
    allowed = _judged(record) | aside
    left = [pair for pair in (s.pair(item) for item in out["drift"]) if pair not in allowed]
    assert not left, f"{len(left)} drift pairs remain after the set-aside: {left[:6]}"


def test_s2_drift_run_keeps_the_command_the_output_and_the_pairs_set_aside_with_count_zero(record):
    run = record.data("drift-run")
    assert isinstance(run, dict) and {"head", "command", "output", "set_aside", "count_after_set_aside"} <= set(run)
    assert run["count_after_set_aside"] == 0
    assert isinstance(run["output"], dict) and "drift" in run["output"] and "count" in run["output"]
    listed = {s.pair(item) for item in run["output"]["drift"]}
    aside = {s.pair(item) for item in run["set_aside"]}
    assert aside <= _judged(record), "a pair is set aside that the record does not list as judged wrong"
    assert listed <= aside, "the recorded drift output holds a pair that was not set aside"
    s.need_hash(run["head"], "drift-run.head")
