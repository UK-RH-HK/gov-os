"""S9: state per repository (Interface I1, I2, I9).

The runs folder is ``<runs>/indep/memaudit/<key>/`` with ``<key>`` the repository's directory name, a hyphen and the first 8
hex of the sha256 of its real path (``standing live`` prints ``KEY <key>``), so two repositories on one machine keep separate
``HISTORY.jsonl``, ``STARTS.log`` and ``AUDITS.log`` (the launch script's, at ``<key folder>/indep/AUDITS.log``). A change of
the gov pin (``declare.gov_pin`` of ``~/.local/bin/gov`` against the last HISTORY line's ``gov_pin``), of ``retrieval.yaml`` or
of the path map is a retrieval change that sends a monthly audit back to weekly; a HISTORY line with no ``gov_pin`` is no
trigger. ``pool-import --sets a b`` imports exactly those sets (once each); a standing set name is ``MS-STANDING``.

Not tested, by reading: whether a change under ``src/gov/retrieval/`` of an *adopted* repository that tracks such a file is a
trigger. KPI S9 says the six globs are Gov OS's own; Interface I9 says every repository keeps today's diff over the six globs
(an adopted repository tracks none of the four code paths). The suite takes the two files and the pin, which both readings share.
"""

from __future__ import annotations

import json
import os

import pytest

import w2_172_git as G
import w2_187_world as W
from w2_172_world import state_key
from w2_187_world import W171

PIN_A, PIN_B = "pin-aaaaaaaaaaaa", "pin-bbbbbbbbbbbb"


def standing_world(make_world, **kw):
    return make_world(standing=True, **kw)


def test_s9_standing_live_prints_the_key_and_the_live_set_and_writes_nothing(make_world):
    world = make_world()
    none = world.standing_live()
    assert none.code == 1 and none.lines == [f"KEY {state_key(world.repo)}", "LIVE none"], none
    world.plant_standing()
    before = W.tree_state(world.sets, world.runs_env)
    live = world.standing_live()
    assert live.code == 0 and live.lines == [f"KEY {state_key(world.repo)}", f"LIVE {W.STD}"], live
    assert W.tree_state(world.sets, world.runs_env) == before, "it writes nothing"
    world.plant_standing(world.standing_record(), {"event": "retired", "set": W.STD, "reason": "fitted", "at": "2026-11-09"})
    gone = world.standing_live()
    assert gone.code == 1 and gone.lines[-1] == "LIVE none", gone


def test_s9_the_key_is_the_directory_name_a_hyphen_and_8_hex_of_the_sha256_of_the_resolved_path(make_world):
    import hashlib
    world = make_world()
    real = os.path.realpath(world.repo)
    expected = os.path.basename(real) + "-" + hashlib.sha256(real.encode()).hexdigest()[:8]
    assert state_key(world.repo) == expected
    assert world.standing_live().lines[0] == f"KEY {expected}"
    link = world.base / "repo-link"
    os.symlink(world.repo, link)
    via = world.drive("standing", "live", "--sets-root", str(world.sets), "--repo", str(link))
    assert via.lines[0] == f"KEY {expected}", "the key is taken from the real path"


def two_repos(tmp_path):
    shared = tmp_path / "shared-runs"
    (shared / "indep").mkdir(parents=True)
    a = G.due_repo(tmp_path / "a")
    b = G.due_repo(tmp_path / "b")
    return shared, a, b, {"GOV_INDEP_RUNS_DIR": str(shared)}


def key_dir(shared, repo):
    return shared / "indep" / "memaudit" / state_key(repo.repo)


def test_s9_two_repositories_on_one_runs_folder_keep_separate_history_starts_and_audits(tmp_path):
    shared, a, b, env = two_repos(tmp_path)
    assert state_key(a.repo) != state_key(b.repo) and state_key(a.repo).startswith("repo-")
    folder = key_dir(shared, a)
    folder.mkdir(parents=True)
    (folder / "HISTORY.jsonl").write_text("".join(json.dumps(x) + "\n" for x in G.stable_history(a.l0)), encoding="utf-8")
    (folder / "STARTS.log").write_text(json.dumps(a.start_line("2026-10-10T21:00:00Z", commit=a.l0)) + "\n", encoding="utf-8")
    (folder / "indep").mkdir()
    (folder / "indep" / "AUDITS.log").write_text(json.dumps({"time": "2026-10-27T22:00:00Z", "commit": a.l0, "run": "x",
                                                              "audit": "memory-audit-20261027"}) + "\n", encoding="utf-8")
    mine = a.drive("due", *a.common_flags(), "--store-link", str(a.link), env=env)
    other = b.drive("due", *b.common_flags(), "--store-link", str(b.link), env=env)
    assert mine.lines[0] == "MODE monthly" and mine.lines[2] == "REASON stable", mine
    assert other.lines[0] == "MODE weekly" and other.lines[2] == "REASON start", "B reads none of A's history: " + repr(other)
    assert not key_dir(shared, b).exists() or not (key_dir(shared, b) / "HISTORY.jsonl").exists()


def test_s9_baseline_writes_the_repositorys_own_audits_log_and_no_shared_one(tmp_path):
    shared, a, b, env = two_repos(tmp_path)
    assert a.drive("baseline", "--sets-root", str(a.sets), "--repo", str(a.repo), "--commit", a.h, env=env).code == 0
    assert b.drive("baseline", "--sets-root", str(b.sets), "--repo", str(b.repo), "--commit", b.h, env=env).code == 0
    lines = {}
    for name, repo in (("a", a), ("b", b)):
        log = key_dir(shared, repo) / "indep" / "AUDITS.log"
        assert log.is_file(), f"{name}: {log}"
        lines[name] = [json.loads(x) for x in log.read_text().splitlines() if x.strip()]
    assert [x["commit"] for x in lines["a"]] == [a.h] and [x["commit"] for x in lines["b"]] == [b.h]
    assert not (shared / "indep" / "AUDITS.log").exists(), "no machine-wide log"


# -- a retrieval change per repository ---------------------------------------------------------------------------------------
def plant_pin(repo, pin):
    target = repo.base / "pins" / pin / "gov"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("#!/bin/sh\n", encoding="utf-8")
    target.chmod(0o755)
    link = repo.home / ".local" / "bin" / "gov"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.unlink(missing_ok=True)
    os.symlink(target, link)


def pinned(tmp_path, *, line_pin, now_pin, **over):
    w = G.due_repo(tmp_path / "p", **over)
    G.plant_state(w, [{**x, **({"gov_pin": line_pin} if line_pin else {})} for x in G.stable_history(w.l0)],
                  last_start_days=30)
    plant_pin(w, now_pin)
    return w


def due_lines(w):
    run = w.due()
    return run.lines[0], run.lines[2]


def test_s9_an_unchanged_pin_leaves_a_stable_audit_monthly(tmp_path):
    assert due_lines(pinned(tmp_path, line_pin=PIN_A, now_pin=PIN_A)) == ("MODE monthly", "REASON stable")


def test_s9_a_change_of_the_gov_pin_is_a_retrieval_change_and_sends_it_back_to_weekly(tmp_path):
    assert due_lines(pinned(tmp_path, line_pin=PIN_A, now_pin=PIN_B)) == ("MODE weekly", "REASON retrieval")


def test_s9_a_history_line_with_no_gov_pin_is_no_trigger(tmp_path):
    assert due_lines(pinned(tmp_path, line_pin=None, now_pin=PIN_B)) == ("MODE monthly", "REASON stable")


@pytest.mark.parametrize("path", ["governance/project/retrieval.yaml", "governance/project/path-map.yaml"])
def test_s9_a_change_of_the_retrieval_settings_or_the_path_map_since_the_last_audit_is_a_retrieval_change(tmp_path, path):
    w = G.due_repo(tmp_path / "q", retr_after=(path,))
    G.plant_state(w, G.stable_history(w.l0), last_start_days=30)
    assert due_lines(w) == ("MODE weekly", "REASON retrieval")


# -- pool-import --sets --------------------------------------------------------------------------------------------------------
def plant_set(world, name, *, visible=False):
    import yaml
    folder = world.sets / "fixtures" / "evaluation" / name
    (folder / "hidden").mkdir(parents=True)
    for k in (1, 2, 3):
        doc = {"id": f"q0{k}", "question": f"A question {k} of set {name}?", "gold_answer": "an answer",
               "sources": [{"path": "docs/plan/p11.md"}], "category": "nonexistent-id" if k == 3 else "plan", "drawn": "none"}
        (folder / "hidden" / f"q0{k}.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")
    if visible:
        (folder / "visible").mkdir()
        (folder / "visible" / "v01.yaml").write_text(yaml.safe_dump(
            {"id": "v01", "question": f"A visible question of {name}?", "gold_answer": "a", "sources": [{"path": "docs/plan/p11.md"}],
             "category": "plan"}), encoding="utf-8")


def pool_names(world):
    return sorted(p.name for p in world.pool.glob("*.yaml")) if world.pool.is_dir() else []


def test_s9_pool_import_with_sets_imports_exactly_those_sets_once_each(make_world):
    world = make_world(standing=True)
    plant_set(world, "a", visible=True)
    plant_set(world, "b")
    plant_set(world, "c")
    before = pool_names(world)
    run = world.pool_import("--sets", "a", "b")
    assert run.code == 0, run
    added = sorted(set(pool_names(world)) - set(before))
    assert added == ["a-q01.yaml", "a-q02.yaml", "a-v01.yaml", "b-q01.yaml", "b-q02.yaml"], "the nonexistent-id questions stay out"
    for name in added:
        source = world.sets / "fixtures" / "evaluation" / name.split("-")[0] / ("visible" if "-v" in name else "hidden") / name.split("-", 1)[1]
        assert (world.pool / name).read_bytes() == source.read_bytes()
    assert (world.sets / "runs" / "memory-pool" / "IMPORTED-a.json").is_file()
    assert (world.sets / "runs" / "memory-pool" / "IMPORTED-b.json").is_file()
    assert not (world.sets / "runs" / "memory-pool" / "IMPORTED-c.json").exists()
    assert not (world.sets / "runs" / "memory-pool" / "IMPORTED.json").exists(), "today's one-time record is not this import's"
    again = world.pool_import("--sets", "a")
    assert again.code == 1 and "MS-IMPORTED" in again.lines, again
    assert pool_names(world) == sorted(set(before) | set(added))
    later = world.pool_import("--sets", "c")
    assert later.code == 0 and "c-q01.yaml" in pool_names(world), later


def test_s9_a_standing_set_name_is_ms_standing_and_imports_nothing(make_world):
    world = make_world(standing=True)
    before = pool_names(world)
    run = world.pool_import("--sets", W.STD)
    assert run.code == 1 and "MS-STANDING" in run.lines, run
    assert pool_names(world) == before


def test_s9_pool_import_with_no_sets_is_todays_and_refuses_a_world_without_the_79_and_the_138(make_world):
    world = make_world()
    run = world.pool_import()
    assert run.code == 1 and "MS-IMPORTCOUNT" in run.lines, run
