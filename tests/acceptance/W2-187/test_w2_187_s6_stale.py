"""S6: staleness by count (Interface I6).

Before each standing run the pre-flight checks each question's gold anchors at the audit commit: a question whose anchor no
longer resolves, or whose nonexistent id now exists, is dropped from that week's n and counted (``dropped k``); nothing in the
set is edited or moved; no id is printed (the dropped ids stay in the run folder's ``PREFLIGHT.json``). Fewer than 70 live
questions prints ``STANDING_THIN <live>``.

Three whole runs: 3 broken anchors (n 77), 11 (69 live: thin) and 10 (70 live: not thin). The pre-flight is also run alone, as
the driver runs it (``preflight --audit <set> --week <w> --repo <the store link's work tree> --commit <audit commit>``).
"""

from __future__ import annotations

import json
import re

import w2_187_world as W
from w2_187_world import W171

QUESTION_LINE = re.compile(r"^(\S+) \((\w+)\): hit@5 ")


def ids_in(text: str, ids) -> list[str]:
    return [i for i in ids if re.search(rf"(?<![A-Za-z0-9_]){i}(?![A-Za-z0-9_])", text)]


def key_folder_text(world) -> str:
    return "\n".join(p.read_bytes().decode("utf-8", "replace") for p in world.scan_targets(world.mem))


def test_s6_three_broken_anchors_make_n_77_and_print_dropped_3_with_no_id(ran_std):
    world, run = ran_std("drop3")
    assert run.code == 0, run
    broken = ["q05", "q17", "q42"]
    block = world.std_digest_lines()
    assert W.digest_line(block, "QUESTIONS") == "QUESTIONS live 77 of 80; dropped 3", block
    assert ids_in(run.out + run.err + key_folder_text(world), broken) == [], "no dropped id is printed or logged"
    pre = world.std_json("PREFLIGHT.json")
    assert (pre["mode"], pre["ok"], pre["n_set"], pre["n"], pre["dropped"], pre["n_apart"]) == ("standing", True, 80, 77, 3, 1)
    assert sorted(pre["dropped_ids"]) == broken, "the ids stay in the run folder"
    assert pre["set_digest"] == world.std_digest()
    assert pre["files_sha256"] == {p.stem: W171.sha_file(p) for p in sorted(world.std_hidden.glob("*.yaml"))}


def test_s6_nothing_in_the_set_is_edited_or_moved_and_the_run_measures_it_whole(ran_std):
    world, run = ran_std("drop3")
    assert run.code == 0, run
    assert world.std_digest() == world.standing_lines()[0]["set_digest"], "the set's digest is unchanged by the run"
    assert sorted(p.name for p in world.std_hidden.iterdir()) == [f"q{k:02d}.yaml" for k in range(1, 81)]
    assert not (world.std_hidden / "dropped").exists() and not (world.std_week / "DROPS.json").exists(), "void is never called"
    measured = [x for x in (world.std_week / "attempt-1" / "measure.txt").read_text().splitlines() if QUESTION_LINE.match(x)]
    assert len(measured) == 80, "the whole hidden part is measured (wholeness against n_set), the live ids scored"


def test_s6_n_is_the_live_count_in_the_declaration_the_figures_and_the_history_and_the_judge_asks_only_the_live(ran_std):
    world, run = ran_std("drop3")
    assert run.code == 0, run
    doc = world.std_json("DECLARATION.json")
    assert (doc["n"], doc["n_set"], doc["dropped"]) == (77, 80, 3)
    assert doc["bar"] == {"need_right": 74, "max_wrong": 3, "target_right": 74}
    fig = world.std_json("FIGURES.json")
    assert (fig["n"], fig["verdict"]["right"], fig["bar"]) == (77, 77, doc["bar"])
    readers = {c["qid"] for c in world.claude_calls() if c["kind"] == "reader"}
    assert None not in readers and len(readers) == 77 and not readers & {"q05", "q17", "q42"}, "a dropped question is never asked"
    (line,) = [x for x in world.history_kind("standing")]
    assert (line["n"], line["dropped"], line["right"], line["measured"]) == (77, 3, 77, True)
    assert run.lines[-1] == f"STANDING {world.week} right 77 of 77: passes"


def test_s6_fewer_than_70_live_questions_prints_standing_thin_with_the_live_count(ran_std):
    world, run = ran_std("thin69")
    assert run.code == 0, run
    block = world.std_digest_lines()
    assert W.digest_line(block, "QUESTIONS").startswith("QUESTIONS live 69 of 80; dropped 11"), block
    assert any("STANDING_THIN 69" in line for line in block), "in the digest"
    assert any("STANDING_THIN 69" in line for line in run.lines), "and on standard output with it"
    (line,) = world.history_kind("standing")
    assert "STANDING_THIN 69" in json.dumps(line["word"]), line


def test_s6_70_live_questions_is_not_thin(ran_std):
    world, run = ran_std("live70")
    assert run.code == 0, run
    block = world.std_digest_lines()
    assert W.digest_line(block, "QUESTIONS").startswith("QUESTIONS live 70 of 80; dropped 10"), block
    assert not any("STANDING_THIN" in line for line in block + run.lines)
    (line,) = world.history_kind("standing")
    assert "STANDING_THIN" not in json.dumps(line)


def preflight(world, repo=None, commit=None):
    return world.drive("preflight", "--sets-root", str(world.sets), "--audit", W.STD, "--week", world.week, "--repo",
                       str(repo or world.link), "--commit", commit or world.audit_commit)


def test_s6_the_preflight_alone_prints_one_line_and_writes_the_record_in_the_run_folder(make_world):
    world = make_world()
    world.break_anchors(["q05", "q17", "q42"])
    world.plant_standing()
    run = preflight(world)
    assert run.code == 0 and run.lines == ["PRE-FLIGHT standing: n 77 of 80; dropped 3"], run
    pre = world.std_json("PREFLIGHT.json")
    assert sorted(pre["dropped_ids"]) == ["q05", "q17", "q42"] and pre["ok"] is True
    assert set(pre) >= {"mode", "ok", "n_set", "n", "dropped", "dropped_ids", "n_apart", "set_digest", "files_sha256"}


def test_s6_a_nonexistent_id_that_now_exists_drops_its_question(make_world):
    world = make_world()
    world.plant_standing()
    commit = world.repo_commit("2026-11-10T06:00:00+00:00", {"docs/std/mention.md": f"{W.ASK_ID} is decided here.\n"},
                               "the id exists now")
    world.relink(commit)
    run = preflight(world, commit=commit)
    assert run.code == 0 and run.lines == ["PRE-FLIGHT standing: n 79 of 80; dropped 1"], run
    assert world.std_json("PREFLIGHT.json")["dropped_ids"] == ["q80"]


def test_s6_a_set_with_every_anchor_live_drops_nothing(make_world):
    world = make_world()
    world.plant_standing()
    run = preflight(world)
    assert run.code == 0 and run.lines == ["PRE-FLIGHT standing: n 80 of 80; dropped 0"], run
    assert world.std_json("PREFLIGHT.json")["dropped_ids"] == []
