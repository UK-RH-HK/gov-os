"""S7: the regression pool (Interface 4; S7's Verify: planted pools of 300 and 900 questions: whole, then a draw of 400
with the same seed twice giving the same draw; a planted fall of 4 points is named).

``pool`` runs after ``judge`` (``FIGURES.json`` exists; ``POOL.json`` absent), re-runs the pool through the retrieval
measure only (no model call): the whole pool while it holds 400 questions or fewer, else ``random.Random(seed)
.sample(sorted(stems), 400)`` with the seed recorded first; prints the pool's figures beside the last audit's and names a
fall of 3.0 points or more in hit@5 or in full evidence a regression (exit 0, ``POOL.json``, ``FIGURES.json``'s
``pool``); then the audit's kept questions (not ``nonexistent-id``) join the pool byte-equal. ``pool-import`` is the
one-time import of the 79 of the fresh 80 and the 138 of the earlier sets.

The draw is observed from the planted ``gov``'s own call log (which pool questions were asked), against the expected
draw of the Interface's formula; the draw's folder is removed after, so it cannot be read from the disk.
"""

from __future__ import annotations

import difflib
import json
import re

import pytest
import yaml

import w2_171_pool as P
import w2_171_scenario as S
import w2_171_world as W

POOL_KEYS = {"size", "drawn", "seed", "digest", "n", "hit5", "full", "last_audit", "last_hit5", "last_full",
             "regression"}
FIGURES_POOL_KEYS = {"n", "hit5", "full", "last_audit", "last_hit5", "last_full", "regression"}
ROLES = W.ROLES


def sets_of(world):
    from gov.util.parts import evaluation_sets
    return evaluation_sets(str(world.sets))


def earlier_pool(world, *, n, hit5, full, audit=W.EARLIER):
    world.plant_earlier(audit, pool={"n": n, "hit5": hit5, "full": full, "last_audit": None, "last_hit5": None,
                                     "last_full": None, "regression": False})


def pool_world(make_world, n, hit5, full, **kw):
    world = make_world("judged:five")
    stems = P.plant_pool(world, n, hit5, full, **kw)
    return world, stems


def test_s7_pool_needs_the_figures_and_refuses_a_second_run(make_world):
    world = make_world("measured:five")
    run = world.pool_run()
    assert run.code == 1 and "MS-NOFIGURES" in run.lines, run
    assert not (world.run_dir / "POOL.json").exists()
    world = make_world("judged:five")
    (world.run_dir / "POOL.json").write_text('{"planted": true}\n')
    snap = W.snapshot(world.sets)
    run = world.pool_run()
    assert run.code == 3 and "USED" in run.lines, run
    assert W.snapshot(world.sets) == snap


def test_s7_a_pool_of_300_is_measured_whole_with_the_seed_recorded_first(make_world):
    world, stems = pool_world(make_world, 300, 240, 270)
    earlier_pool(world, n=300, hit5=240, full=270)
    claude_before, offset = len(world.claude_calls()), len(world.gov_calls())
    digest = W.set_digest(world.pool)
    before_map = world.sets_map.read_text()
    run = world.pool_run()
    assert run.code == 0, run
    pool = world.json_of("POOL.json")
    assert set(pool) == POOL_KEYS, sorted(pool)
    assert (pool["size"], pool["n"], pool["hit5"], pool["full"], pool["regression"]) == (300, 300, 240, 270, False)
    assert pool["digest"] == digest and pool["seed"] == P.default_seed(W.AUDIT, digest), \
        "the default seed: int(sha256(f'{audit}\\n{digest}').hexdigest()[:15], 16)"
    assert pool["last_audit"] == W.EARLIER and (pool["last_hit5"], pool["last_full"]) == (240, 270)
    figures = world.json_of("FIGURES.json")
    assert figures["pool"] == {k: pool[k] for k in FIGURES_POOL_KEYS}, "FIGURES.json's pool is set to the same"
    assert sorted(P.pool_asked(world, stems, offset)) == sorted(stems), "the whole pool, each question once"
    assert len(world.claude_calls()) == claude_before, "no model token"
    ledger = world.ledger()
    seed_at = next(i for i, e in enumerate(ledger) if e["event"] == "pool" and e.get("state") == "seed")
    searches = [i for i, e in enumerate(ledger) if e["event"] == "search" and e.get("phase") == "pool"]
    assert len(searches) >= 300 and all(seed_at < i for i in searches), "the seed is recorded before any search"
    assert ledger[seed_at]["seed"] == pool["seed"] and ledger[seed_at]["size"] == 300
    assert all(ledger[i]["ok"] is True and ledger[i]["rc"] == 0 for i in searches)
    assert len(list((world.run_dir / "pool" / "kept").glob("*.json"))) == len(searches)
    assert (world.run_dir / "pool" / "measure.txt").is_file()
    assert not [x for x in run.lines if x.startswith("POOL REGRESSION")]
    entries = sets_of(world)
    assert entries["memory-pool"]["hidden"] == ["fixtures/evaluation/memory-pool/hidden/**"]
    assert entries["memory-pool"]["measures"]["roles"] == ROLES == entries["memory-verdict-2"]["measures"]["roles"]
    assert "memory-pool-draw" not in entries, "a whole pool needs no draw's entry"
    after = world.sets_map.read_text()
    assert [x for x in difflib.ndiff(before_map.splitlines(), after.splitlines()) if x.startswith("- ")] \
        == [], "the path map gained text and lost none"


@pytest.mark.parametrize("seed", [None, 777])
def test_s7_a_pool_of_900_is_a_draw_of_400_by_the_recorded_seed(make_world, seed):
    world, stems = pool_world(make_world, 900, 600, 700)
    offset = len(world.gov_calls())
    digest = W.set_digest(world.pool)
    run = world.pool_run(*(["--seed", str(seed)] if seed is not None else []))
    assert run.code == 0, run
    pool = world.json_of("POOL.json")
    want_seed = seed if seed is not None else P.default_seed(W.AUDIT, digest)
    assert (pool["size"], pool["drawn"], pool["n"], pool["seed"], pool["digest"]) == (900, 400, 400, want_seed, digest)
    drawn = P.expected_draw(W.AUDIT, stems, want_seed)
    asked = P.pool_asked(world, stems, offset)
    assert sorted(asked) == sorted(drawn) and len(set(asked)) == 400, "the draw is the Interface's formula"
    assert (pool["hit5"], pool["full"]) == (sum(1 for s in drawn if P.rank_of(s, 600, 700) == 1),
                                          sum(1 for s in drawn if P.rank_of(s, 600, 700) is not None))
    entries = sets_of(world)
    assert entries["memory-pool-draw"]["hidden"] == ["fixtures/evaluation/memory-pool-draw/hidden/**"]
    assert entries["memory-pool-draw"]["measures"]["roles"] == ROLES
    assert not list((world.sets / "fixtures" / "evaluation" / "memory-pool-draw").rglob("*.yaml")), \
        "the drawn copy is removed after"
    seed_event = next(e for e in world.ledger() if e["event"] == "pool" and e.get("state") == "seed")
    assert (seed_event["seed"], seed_event["size"]) == (want_seed, 900)


def test_s7_the_same_seed_gives_the_same_draw(make_world):
    runs = []
    for _ in range(2):
        world, stems = pool_world(make_world, 900, 600, 700)
        offset = len(world.gov_calls())
        assert world.pool_run("--seed", "31337").code == 0
        runs.append(P.pool_asked(world, stems, offset))
    assert runs[0] == runs[1] and len(runs[0]) == 400
    assert sorted(runs[0]) == sorted(P.expected_draw(W.AUDIT, stems, 31337))


@pytest.mark.parametrize("now,last,named", [
    ((70, 90), (80, 90), "hit@5"),         # 80 -> 70 of 100: a fall of 10
    ((76, 90), (80, 90), "hit@5"),         # a fall of 4 points
    ((77, 90), (80, 90), "hit@5"),         # exactly 3.0 points: a regression
    ((78, 90), (80, 90), None),            # 2.0 points: none
    ((80, 86), (80, 90), "full evidence"),  # full evidence falls 4 points, hit@5 holds
    ((85, 95), (80, 90), None),            # a rise
])
def test_s7_a_fall_of_3_points_or_more_in_hit5_or_full_evidence_is_named_a_regression(make_world, now, last, named):
    world, stems = pool_world(make_world, 100, now[0], now[1])
    earlier_pool(world, n=100, hit5=last[0], full=last[1])
    run = world.pool_run()
    assert run.code == 0, "a regression is printed and recorded, never a refusal"
    regression = [x for x in run.lines if x.startswith("POOL REGRESSION")]
    pool = world.json_of("POOL.json")
    assert pool["regression"] is (named is not None) and (pool["hit5"], pool["full"]) == now, pool
    assert world.json_of("FIGURES.json")["pool"]["regression"] is (named is not None)
    if named is None:
        assert regression == [], regression
    else:
        shown = {"hit@5": last[0], "full evidence": last[1]}[named], {"hit@5": now[0], "full evidence": now[1]}[named]
        mine = [x for x in regression if f"POOL REGRESSION {named} " in x]
        assert len(mine) == 1, regression
        m = re.fullmatch(rf"POOL REGRESSION {re.escape(named)} ([0-9.]+) -> ([0-9.]+) %", mine[0])
        assert m and (float(m[1]), float(m[2])) == pytest.approx((shown[0], shown[1]), abs=0.05), mine


@pytest.mark.parametrize("earlier", ["none", "earlier audit without a pool block"])
def test_s7_without_an_earlier_pool_figure_there_is_no_comparison(make_world, earlier):
    world, stems = pool_world(make_world, 60, 50, 55)
    if earlier != "none":
        world.plant_earlier(W.EARLIER, pool=None)
    run = world.pool_run()
    assert run.code == 0, run
    pool = world.json_of("POOL.json")
    assert pool["regression"] is False and not pool["last_audit"] and pool["last_hit5"] is None, pool
    assert (pool["n"], pool["hit5"], pool["full"]) == (60, 50, 55)
    assert not [x for x in run.lines if x.startswith("POOL REGRESSION")]


def test_s7_the_audits_kept_questions_join_the_pool_byte_equal_less_the_nonexistent_id_one(make_world):
    world, stems = pool_world(make_world, 20, 15, 18)
    run = world.pool_run()
    assert run.code == 0, run
    joined = sorted(p.name for p in world.pool.glob(f"{W.AUDIT}-*.yaml"))
    assert joined == [f"{W.AUDIT}-q{i:02d}.yaml" for i in range(1, 40)], "39 files: q40's category is nonexistent-id"
    for path in world.pool.glob(f"{W.AUDIT}-*.yaml"):
        assert path.read_bytes() == (world.hidden / path.name[len(W.AUDIT) + 1:]).read_bytes(), path.name
    assert len(list(world.pool.glob(f"{W.EARLIER}-*.yaml"))) == 20, "the earlier questions stay as they were"


def test_s7_an_equal_file_already_in_the_pool_is_skipped_a_different_one_is_ms_pooldiff(make_world):
    world, _ = pool_world(make_world, 20, 15, 18)
    equal = world.pool / f"{W.AUDIT}-q05.yaml"
    equal.write_bytes((world.hidden / "q05.yaml").read_bytes())
    mtime = equal.stat().st_mtime_ns
    run = world.pool_run()
    assert run.code == 0, run
    assert equal.stat().st_mtime_ns == mtime, "a present equal file is skipped, not rewritten"
    assert len(list(world.pool.glob(f"{W.AUDIT}-*.yaml"))) == 39

    world, _ = pool_world(make_world, 20, 15, 18)
    different = world.pool / f"{W.AUDIT}-q05.yaml"
    doc = yaml.safe_load((world.hidden / "q05.yaml").read_text())
    doc["gold_answer"] = "Another answer, as a well-formed question that differs."
    different.write_text(yaml.safe_dump(doc, sort_keys=False))
    kept = different.read_bytes()
    run = world.pool_run()
    assert run.code == 1 and "MS-POOLDIFF" in run.lines, run
    assert different.read_bytes() == kept, "a different file is never overwritten"


def test_s7_a_pool_search_not_answered_as_declared_is_ms_poolfault(make_world):
    world, stems = pool_world(make_world, 20, 15, 18)
    plan = json.loads((world.state / "gov_plan.json").read_text())
    plan["questions"][stems[f"{W.EARLIER}-p0007"]]["fault"] = "rerank"
    (world.state / "gov_plan.json").write_text(json.dumps(plan))
    run = world.pool_run()
    assert run.code == 1 and "MS-POOLFAULT" in run.lines, run
    assert world.json_of("FIGURES.json")["pool"] is None
    assert not list(world.pool.glob(f"{W.AUDIT}-*.yaml")), "the audit's questions join only after a whole pool run"


def test_s7_pool_refuses_a_gov_whose_pin_is_not_the_declared_one(make_world):
    world, _ = pool_world(make_world, 20, 15, 18)
    snap = W.snapshot(world.sets)
    run = world.pool_run(gov=world.gov_other)
    assert run.code == 1 and "MS-PIN" in run.lines, run
    assert W.snapshot(world.sets) == snap


# -- the one-time import ------------------------------------------------------------------------------------------
def _plant_source_sets(world):
    """memory-verdict-2: 80 files (``f80`` the nonexistent-id one); memory-retrieval: the control's 40 visible
    (``c01`` to ``c40``) and 40 hidden (``h01`` to ``h40``, ``h24`` the nonexistent-id one); memory-verdict: 60
    hidden (``m01`` to ``m60``, ``m60`` the nonexistent-id one): 79 and 138 after the exclusions."""
    base = world.sets / "fixtures" / "evaluation"

    def put(folder, qid, category="plan"):
        (base / folder).mkdir(parents=True, exist_ok=True)
        (base / folder / f"{qid}.yaml").write_text(yaml.safe_dump({
            "id": qid, "question": f"A {folder} question {qid}.", "gold_answer": "An answer.",
            "sources": [{"path": "docs/plan/p11.md"}], "category": category}, sort_keys=False), encoding="utf-8")
    for k in range(1, 81):
        put("memory-verdict-2/hidden", f"f{k:02d}", "nonexistent-id" if k == 80 else "plan")
    for k in range(1, 41):
        put("memory-retrieval/hidden", f"h{k:02d}", "nonexistent-id" if k == 24 else "plan")
    for k in range(1, 61):
        put("memory-verdict/hidden", f"m{k:02d}", "nonexistent-id" if k == 60 else "plan")


def _imported_names():
    names = [f"memory-verdict-2-f{k:02d}.yaml" for k in range(1, 80)]
    names += [f"memory-retrieval-c{k:02d}.yaml" for k in range(1, 41)]
    names += [f"memory-retrieval-h{k:02d}.yaml" for k in range(1, 41) if k != 24]
    names += [f"memory-verdict-m{k:02d}.yaml" for k in range(1, 60)]
    assert len(names) == 79 + 138
    return sorted(names)


def test_s7_pool_import_copies_the_79_and_the_138_and_records_the_import_last(world):
    _plant_source_sets(world)
    before = {p.name for p in world.pool.glob("*.yaml")}
    run = world.pool_import()
    assert run.code == 0, run
    added = sorted({p.name for p in world.pool.glob("*.yaml")} - before)
    assert added == _imported_names(), "<set>-<qid>.yaml, less each set's nonexistent-id question"
    base = world.sets / "fixtures" / "evaluation"
    for name in added:
        sets, qid = name.rsplit("-", 1)
        folder = {"memory-verdict-2": "memory-verdict-2/hidden", "memory-verdict": "memory-verdict/hidden"}.get(
            sets, f"{sets}/{'visible' if qid.startswith('c') else 'hidden'}")
        assert (world.pool / name).read_bytes() == (base / folder / qid).read_bytes(), name
    record = json.loads((world.sets / "runs" / "memory-pool" / "IMPORTED.json").read_text())
    flat = json.dumps(record)
    assert re.search(r"\b79\b", flat) and re.search(r"\b138\b", flat) and re.search(r"[0-9a-f]{64}", flat), record
    assert "A memory" not in flat, "counts and a digest, no question text"
    assert (world.sets / "runs" / "memory-pool" / "IMPORTED.json").stat().st_mtime_ns >= max(
        (world.pool / n).stat().st_mtime_ns for n in added), "IMPORTED.json is written last"


def test_s7_pool_import_refuses_a_count_other_than_79_and_138_writing_nothing(world):
    _plant_source_sets(world)
    (world.sets / "fixtures" / "evaluation" / "memory-verdict-2" / "hidden" / "f05.yaml").unlink()
    snap = W.snapshot(world.sets)
    run = world.pool_import()
    assert run.code == 1 and "MS-IMPORTCOUNT" in run.lines, run
    assert W.snapshot(world.sets) == snap and not (world.sets / "runs" / "memory-pool").exists()


def test_s7_pool_import_runs_once(world):
    _plant_source_sets(world)
    assert world.pool_import().code == 0
    snap = W.snapshot(world.sets)
    run = world.pool_import()
    assert run.code == 1 and "MS-IMPORTED" in run.lines, run
    assert W.snapshot(world.sets) == snap


def test_s7_pool_import_takes_the_sets_root_only(world):
    _plant_source_sets(world)
    run = world.pool_import("--audit", W.AUDIT)
    assert run.code == 4, run
    assert not (world.sets / "runs" / "memory-pool").exists()
    assert world.pool_import().code == 0, "with the sets root only it runs"
