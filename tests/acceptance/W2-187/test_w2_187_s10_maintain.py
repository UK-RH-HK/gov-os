"""S10 and F6: the weekly maintenance pass, ``python3 -m gov.memaudit maintain --sets-root R [--repo D] [--store-link P] [--gov EXE]``
(Interface I10).

Six items and one printed line, ``MAINTAIN 1 store <word> 2 layout <word> 3 links <k> 4 unindexed <k> 5 not_found <a> second <b>
6 reanchor <k>``, exit 0 always (4 for usage): (1) the integration store at the main line's head, else one ``gov rebuild
--integration <main line>``, a failed build leaving the last good store in service and named ``kept <12 hex> (refresh exit <c>)``;
(2) the store's layout, one rebuild when stale, else ``stale kept``; (3) ``gov links --since <the last pass's commit> --json`` in
the repository, the new findings counted (``none`` when it refuses); (4) the tracked paths the path map indexes of which the store
holds no chunk; (5) the latest standing week's and the latest fresh run's reader rows that are ``not_found`` and that searched
again; (6) the gold questions whose cited lines changed at the audit commit (``unresolved`` of the measure's own loader: a block
moved unchanged is re-anchored in memory and not listed), for each set but the standing sets, written as question id and entry
number to ``runs/<set>/REANCHOR-<week>.json``. One ``MAINTAIN.jsonl`` line in the key folder holds the week, the commit, the
items and the digests of ``retrieval.yaml`` and the path map before and after (equal, F6).

The planted ``gov`` answers ``rebuild`` (moving the link and its store's head when asked) and ``links``; every call is logged
with its argv and cwd. Readings: the store word of a refresh holds the new head's first 12 hex; the entry number of a
re-anchoring request is read as the integer (``1``, ``"1"`` and ``"entry 1"`` all pass).
"""

from __future__ import annotations

import json
import os
import re
import stat
import time

import pytest

import w2_187_maintain as M
import w2_187_world as W
from w2_187_world import W171, parse_maintain

BUSY = {"GOV_MEMAUDIT_GATE_MAX_S": "0", "GOV_MEMAUDIT_GATE_POLL_S": "0"}


def world_of(make_world):
    return make_world(standing=True)


def test_s10_a_store_three_commits_behind_is_refreshed_once_and_the_new_head_printed(make_world):
    world = world_of(make_world)
    head = M.behind(world, 2)  # the template's own later commit is the third
    M.plan_rebuild(world, advance_to=head)
    run = world.maintain()
    assert run.code == 0, run
    calls = M.rebuild_calls(world)
    assert len(calls) == 1 and calls[0]["argv"][:2] == ["rebuild", "--integration"] and calls[0]["argv"][2] in ("main", "refs/heads/main")
    assert head[:12] in parse_maintain(M.maintain_line(run))["store"]
    assert world.link_head() == head
    again = world.maintain()
    assert again.code == 0 and len(M.rebuild_calls(world)) == 1, "a store at the head is not refreshed"


def test_s10_a_failing_rebuild_keeps_the_old_store_names_the_failure_and_the_pass_still_exits_0(make_world):
    world = world_of(make_world)
    M.behind(world, 2)
    M.plan_rebuild(world, exit=1)
    run = world.maintain()
    assert run.code == 0, run
    word = parse_maintain(M.maintain_line(run))["store"]
    assert re.fullmatch(r"kept ([0-9a-f]{12}) \(refresh exit 1\)", word), word
    assert word.split()[1] == world.audit_commit[:12] and world.link_head() == world.audit_commit
    assert len(M.rebuild_calls(world)) == 1, "one refresh, never a retry loop"


def test_s10_a_store_at_the_head_is_not_rebuilt(make_world):
    world = world_of(make_world)
    world.relink(world.repo_git("rev-parse", "main").strip())
    run = world.maintain()
    assert run.code == 0 and M.rebuild_calls(world) == [], run
    word = parse_maintain(M.maintain_line(run))
    assert "kept" not in word["store"] and "stale" not in word["layout"], word


def test_s10_a_stale_layout_is_rebuilt_once_and_named_when_the_rebuild_fails(make_world):
    world = world_of(make_world)
    world.relink(world.repo_git("rev-parse", "main").strip())
    M.stamp_layout(world, 1)
    M.plan_rebuild(world, fix_layout=True)
    run = world.maintain()
    assert run.code == 0 and len(M.rebuild_calls(world)) == 1, run
    assert "stale" not in parse_maintain(M.maintain_line(run))["layout"]
    failing = world_of(make_world)
    failing.relink(failing.repo_git("rev-parse", "main").strip())
    M.stamp_layout(failing, 1)
    M.plan_rebuild(failing, exit=1)
    bad = failing.maintain()
    assert bad.code == 0 and "stale kept" in parse_maintain(M.maintain_line(bad))["layout"], bad
    assert len(M.rebuild_calls(failing)) == 1


def test_s10_the_new_link_findings_are_counted_first_from_the_mark_then_since_the_last_passs_commit(make_world):
    world = world_of(make_world)
    world.write_x_plan(links={"new": 3})
    first = world.maintain()
    assert first.code == 0 and parse_maintain(M.maintain_line(first))["links"] == "3", first
    (call,) = M.links_calls(world)
    assert "--since" not in call["argv"] and "--json" in call["argv"], "a first pass runs from the mark"
    assert call["cwd"] == M.real(world.repo), "in the repository"
    head = world.link_head()
    second = world.maintain()
    assert second.code == 0
    since = M.links_calls(world)[-1]["argv"]
    assert "--since" in since and "--json" in since
    assert head.startswith(since[since.index("--since") + 1]) and len(since[since.index("--since") + 1]) >= 12, since
    assert len(M.maintain_lines(world)) == 2


def test_s10_a_refused_links_check_is_none_and_never_fails_the_pass(make_world):
    world = world_of(make_world)
    world.write_x_plan(links={"refuse": True})
    run = world.maintain()
    assert run.code == 0 and parse_maintain(M.maintain_line(run))["links"] == "none", run


@pytest.mark.parametrize("skipped,expected", [(2, "2"), (0, "0")])
def test_s10_the_tracked_paths_the_store_holds_no_chunk_of_are_counted(make_world, skipped, expected):
    world = world_of(make_world)
    world.relink(world.repo_git("rev-parse", "main").strip())
    M.plant_chunks(world, M.candidates(world)[:skipped])
    run = world.maintain()
    assert run.code == 0 and parse_maintain(M.maintain_line(run))["unindexed"] == expected, run


def test_s10_the_not_found_answers_and_second_searches_of_the_latest_standing_week_and_fresh_run_are_counted(make_world):
    world = world_of(make_world)
    a, b = M.plant_reader_runs(world)
    run = world.maintain()
    got = parse_maintain(M.maintain_line(run))
    assert run.code == 0 and (int(got["nf"]), int(got["second"])) == (a, b), got


def reanchor_world(make_world):
    world = world_of(make_world)
    world.break_anchors(["q05"])  # a standing set's stale question drops by count (S6): it is never in a request
    world.plant_standing()
    d1, d2 = M.plant_reanchor_set(world)
    return world, d2


def test_s10_a_changed_cited_block_is_listed_by_id_and_entry_and_a_moved_unchanged_one_is_not(make_world):
    world, d2 = reanchor_world(make_world)
    run = world.maintain()
    assert run.code == 0 and parse_maintain(M.maintain_line(run))["reanchor"] == "1", run
    request = world.sets / "runs" / M.AUDIT_SET / f"REANCHOR-{world.week}.json"
    doc = json.loads(request.read_text(encoding="utf-8"))
    assert set(doc) == {"week", "audit_commit", "set", "changed", "count"}, doc
    assert (doc["week"], doc["set"], doc["count"]) == (world.week, M.AUDIT_SET, 1)
    assert doc["audit_commit"] in (d2, d2[:12])
    assert len(doc["changed"]) == 1 and doc["changed"][0]["id"] == "q02", doc
    assert str(doc["changed"][0]["entry"]).replace("entry ", "") == "1"
    assert stat.S_IMODE(os.stat(request).st_mode) == 0o600
    assert stat.S_IMODE(os.stat(request.parent).st_mode) == 0o700
    assert sorted(p.relative_to(world.sets).as_posix() for p in (world.sets / "runs").rglob("REANCHOR-*.json")) == \
        [request.relative_to(world.sets).as_posix()], "one request, for the one set; the standing set is left out"


def entry_of(item: dict) -> int:
    return int(str(item["entry"]).replace("entry ", "").split(".")[0])


def test_s10_a_heading_cited_section_whose_text_changed_is_listed_though_its_heading_is_found_one_that_did_not_is_not(make_world):
    """DEC-1180 (1), N2 (b), ``Rewrite-Reason: DEC-1180 (1)``. Eight heading-cited questions, every heading still found at the
    head (``plant_section_set``): a section rewritten (q01), one changed in its ``###`` sub-section (q04), the last section of
    its file with a line appended (q07) and the second entry of q08 are listed, by question id and entry number; a section that
    only moved (q02), one untouched (q03) and one whose *following* section changed (q05) are not; q06's entry, whose two
    alternatives both changed (a section that moved and was rewritten, and a rewritten line-cited block), is listed once.
    The entry number of an alternative is read as its entry's integer. Red until the engineer builds N2 (b)."""
    world = world_of(make_world)
    world.break_anchors(["q05"])
    world.plant_standing()
    d1, d2, expected = M.plant_section_set(world)
    run = world.maintain()
    assert run.code == 0 and parse_maintain(M.maintain_line(run))["reanchor"] == str(len(expected)), run
    request = world.sets / "runs" / M.AUDIT_SET / f"REANCHOR-{world.week}.json"
    doc = json.loads(request.read_text(encoding="utf-8"))
    assert set(doc) == {"week", "audit_commit", "set", "changed", "count"}, doc
    assert (doc["week"], doc["set"], doc["count"]) == (world.week, M.AUDIT_SET, len(expected)), doc
    assert doc["audit_commit"] in (d2, d2[:12])
    assert all(set(item) == {"id", "entry"} for item in doc["changed"]), "id and entry only"
    assert sorted((item["id"], entry_of(item)) for item in doc["changed"]) == expected, doc["changed"]
    assert stat.S_IMODE(os.stat(request).st_mode) == 0o600


def test_s10_a_set_of_heading_cited_sections_none_of_which_changed_has_no_request(make_world):
    """N2 (b)'s other side: sections that moved unchanged, or whose neighbours changed, are not listed, and a set with no entry
    gets no request file (S10 (6): one request per set with at least one entry)."""
    world = world_of(make_world)
    world.plant_standing()
    M.plant_section_set(world)
    hidden = world.sets / "fixtures" / "evaluation" / M.AUDIT_SET / "hidden"
    for q in ("q01", "q04", "q06", "q07", "q08"):
        (hidden / f"{q}.yaml").unlink()
    run = world.maintain()
    assert run.code == 0 and parse_maintain(M.maintain_line(run))["reanchor"] == "0", run
    assert list((world.sets / "runs").rglob("REANCHOR-*.json")) == []


def test_s10_the_section_request_the_line_the_log_and_the_digest_hold_no_question_answer_or_path_text(make_world):
    world = world_of(make_world)
    world.plant_standing()
    M.plant_section_set(world)
    run = world.maintain()
    assert run.code == 0, run
    request = world.sets / "runs" / M.AUDIT_SET / f"REANCHOR-{world.week}.json"
    assert request.is_file(), "the request exists, so there is something to leak"
    for path in (world.base, world.sets, world.repo, world.link, world.runs_env):
        assert not W.hits(str(path) + "/", M.SECTION_WORDS), f"{path} holds a planted word"
    texts = [run.out, run.err, request.read_text(),
             *(p.read_bytes().decode("utf-8", "replace") for p in world.scan_targets(world.runs_env))]
    for text in texts:
        assert W.hits(text, M.SECTION_WORDS) == [], "a planted question, answer, path or heading word is outside the set"


def test_s10_the_request_the_line_the_log_and_the_digest_hold_no_question_answer_or_path_text(make_world):
    world, _ = reanchor_world(make_world)
    run = world.maintain()
    assert run.code == 0, run
    for path in (world.base, world.sets, world.repo, world.link, world.runs_env):
        assert not W.hits(str(path) + "/", M.WORDS), f"{path} holds a planted word"
    texts = [run.out, run.err, *(p.read_bytes().decode("utf-8", "replace") for p in world.scan_targets(world.runs_env)),
             (world.sets / "runs" / M.AUDIT_SET / f"REANCHOR-{world.week}.json").read_text()]
    for text in texts:
        assert W.hits(text, M.WORDS) == [], "a planted question, answer or path word is outside the set"
    assert any(W.hits(p.read_text(), M.WORDS) for p in (world.sets / "fixtures" / "evaluation" / M.AUDIT_SET / "hidden").glob("*.yaml"))


def test_s10_the_pass_prints_one_line_with_the_six_counts_and_writes_one_line_in_the_key_folder(make_world):
    world, d2 = reanchor_world(make_world)
    world.write_x_plan(links={"new": 3})
    M.plant_chunks(world, M.candidates(world)[:2])
    M.plant_reader_runs(world)
    run = world.maintain()
    assert run.code == 0 and len(run.lines) == 1, run
    got = parse_maintain(run.lines[0])
    assert (got["links"], got["unindexed"], got["nf"], got["second"], got["reanchor"]) == ("3", "2", "3", "5", "1"), got
    (line,) = M.maintain_lines(world)
    assert line["week"] == world.week and (line["commit"] == d2 or d2.startswith(line["commit"])), line
    text = json.dumps(line)
    digests = M.digests(world)
    for name in ("retrieval.yaml", "path-map"):
        assert text.count(digests[name]) >= 2, f"the {name} digest before and after"


def test_s10_a_pass_that_cannot_finish_in_time_still_exits_0_quickly_and_keeps_the_store(make_world):
    world = world_of(make_world)
    M.behind(world, 2)
    M.plan_rebuild(world, sleep=30, advance_to=world.repo_git("rev-parse", "main").strip())
    began = time.monotonic()
    run = world.maintain(env={"GOV_MEMAUDIT_MAINTAIN_TIMEOUT_S": "2"}, timeout=60)
    assert run.code == 0 and time.monotonic() - began < 25, run
    assert parse_maintain(M.maintain_line(run))["store"].startswith("kept "), run
    assert world.link_head() == world.audit_commit


def test_s10_the_audit_runs_whatever_the_pass_finds(make_world):
    world = world_of(make_world)
    M.behind(world, 2)
    M.plan_rebuild(world, exit=1)
    world.write_x_plan(links={"refuse": True})
    M.stamp_layout(world, 1)
    assert world.maintain().code == 0
    world.plan_gate(1)
    run = world.standing_run(gate=world.gate_stub, env=BUSY)
    assert run.code == 2 and "STOPPED measure gate busy" in run.lines, "the standing run starts: a failed pass is no gate"


def test_f6_a_pass_changes_no_setting_applies_no_act_and_calls_no_crontab(make_world):
    world, _ = reanchor_world(make_world)
    before = M.digests(world)
    status = M.repo_status(world)
    assert world.maintain().code == 0
    assert M.digests(world) == before, "retrieval.yaml, the path map and the sets root's path map are unchanged"
    assert M.repo_status(world) == status, "nothing is written in the repository"
    assert world.crontab_calls() == ""


def test_f6_the_maintenance_module_imports_no_crontab_writer_and_names_none():
    source = W.SRC / "gov" / "memaudit" / "maintain.py"
    assert source.is_file(), "src/gov/memaudit/maintain.py"
    assert "crontab" not in source.read_text(encoding="utf-8").lower()


def test_s10_the_digest_of_a_standing_run_carries_the_latest_maintain_line(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    line = M.maintain_line(world.maintain_run)
    assert line in world.std_digest_lines() and line in run.lines
