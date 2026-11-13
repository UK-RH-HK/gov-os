"""S7, S6, F3: the regression pool, its import path and the class counts, on planted sets and a fake ``gov``."""

from __future__ import annotations

import hashlib
import json
import random

import pytest
import yaml

from gov.memaudit import pool
from gov.memaudit.common import set_digest

from .conftest import AUDIT, SRC, question
from .fakes import measured
from .test_measure import events, snapshot

OLD = "memory-audit-20261001"


def pool_args(plant, *extra):
    return ["pool", "--sets-root", str(plant.root), "--audit", AUDIT, "--repo", str(plant.repo["path"]),
            "--gov", str(plant.gov), *extra]


def plant_pool(plant, fake, n: int, hits: int, prefix: str = "old") -> None:
    """``n`` questions in the pool, ``hits`` of them at rank 1 (the rest not found); ids ``p0001``..."""
    folder = plant.root / "fixtures/evaluation/memory-pool/hidden"
    for k in range(1, n + 1):
        q = question(1 + (k - 1) % 39, plant.repo["head"])
        q.update(id=f"p{k:04d}", question=f"Pool question number {k}?")
        (folder / f"{OLD}-{prefix}{k:04d}.yaml").write_text(yaml.safe_dump(q, sort_keys=False), encoding="utf-8")
        fake.rank(q, 1 if k <= hits else None)
    fake.save()


def with_figures(plant, **extra):
    """A measured audit, and the ``FIGURES.json`` ``judge`` would have written (the pool needs it only to exist)."""
    fake, ranks, claude = measured(plant)
    (plant.run_dir / "FIGURES.json").write_text(json.dumps({"audit": AUDIT, "pool": None, "classes": None, **extra}))
    return fake


def run_pool(plant, monkeypatch, **kw):
    monkeypatch.setenv("PYTHONPATH", SRC)
    lines = []
    word = pool.run(plant.root, AUDIT, repo=plant.repo["path"], gov=plant.gov, emit=lines.append, **kw)
    return word, lines


def earlier(plant, n, hit5, full, audit=OLD):
    (plant.root / "runs" / audit).mkdir(parents=True, exist_ok=True)
    (plant.root / "runs" / audit / "FIGURES.json").write_text(json.dumps({"pool": {"n": n, "hit5": hit5, "full": full}}))


# ---- the draw

def test_the_draw_is_400_of_the_sorted_ids_and_the_same_seed_gives_the_same_draw():
    stems = [f"set-q{i:04d}" for i in range(900)]
    a, b = pool.choose(stems, 12345), pool.choose(list(reversed(stems)), 12345)
    assert a == b and len(a) == 400 == len(set(a))
    assert a == random.Random(12345).sample(sorted(stems), 400)
    assert pool.choose(stems, 12346) != a


def test_the_default_seed_is_fifteen_hex_digits_of_the_audit_and_the_digest():
    assert pool._seed_of(AUDIT, "ab" * 32) == int(hashlib.sha256(f"{AUDIT}\n{'ab' * 32}".encode()).hexdigest()[:15], 16)


# ---- the whole pool, then a draw

def test_a_pool_of_300_is_measured_whole_and_the_audits_questions_join_it(plant):
    fake = with_figures(plant)
    plant_pool(plant, fake, 300, 270)
    digest_before = set_digest(plant.root / "fixtures/evaluation/memory-pool/hidden")
    done = plant.cli(*pool_args(plant, "--seed", "7"))
    assert done.returncode == 0, done.stdout
    p = json.loads((plant.run_dir / "POOL.json").read_text())
    assert p["size"] == 300 and p["drawn"] == 300 and p["seed"] == 7 and p["n"] == 300
    assert (p["hit5"], p["full"], p["regression"], p["last_audit"]) == (270, 270, False, None)
    assert p["digest"] == digest_before
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["pool"] == {k: p[k] for k in ("n", "hit5", "full", "last_audit", "last_hit5", "last_full", "regression")}
    out = done.stdout.splitlines()
    assert out[0].startswith("POOL 300 of 300: hit@5 270 (90.0 %); full evidence 270 (90.0 %); no earlier audit")
    ev = events(plant)
    names = [(e["event"], e.get("state")) for e in ev if e["event"] == "pool"]
    assert names == [("pool", "seed"), ("pool", "done")]
    first_pool_search = next(i for i, e in enumerate(ev) if e["event"] == "search" and e["phase"] == "pool")
    assert [e["event"] for e in ev].index("pool") < first_pool_search  # the seed is recorded before any search
    assert len([e for e in ev if e["event"] == "search" and e["phase"] == "pool"]) == 300
    assert "memory-pool:" in (plant.root / "governance/project/path-map.yaml").read_text()
    assert "memory-pool-draw" not in (plant.root / "governance/project/path-map.yaml").read_text()
    # the audit's kept questions (not the nonexistent-id one), byte-equal
    joined = sorted((plant.root / "fixtures/evaluation/memory-pool/hidden").glob(f"{AUDIT}-*.yaml"))
    assert len(joined) == 39 and f"{AUDIT}-q40.yaml" not in {x.name for x in joined}
    assert all(x.read_bytes() == (plant.hidden / x.name[len(AUDIT) + 1:]).read_bytes() for x in joined)
    assert (plant.run_dir / "pool/measure.txt").is_file() and len(list((plant.run_dir / "pool/kept").glob("*.json"))) == 300


def test_a_pool_of_900_is_a_seeded_draw_of_400_measured_as_the_copied_set(plant):
    fake = with_figures(plant)
    plant_pool(plant, fake, 900, 720)
    done = plant.cli(*pool_args(plant))
    assert done.returncode == 0, done.stdout
    p = json.loads((plant.run_dir / "POOL.json").read_text())
    seed = int(hashlib.sha256(f"{AUDIT}\n{p['digest']}".encode()).hexdigest()[:15], 16)
    assert p["size"] == 900 and p["drawn"] == 400 and p["n"] == 400 and p["seed"] == seed
    stems = [f"{OLD}-old{k:04d}" for k in range(1, 901)]
    want = {f"p{int(s[-4:]):04d}" for s in pool.choose(stems, seed)}
    got = {line.split(" ")[0] for line in (plant.run_dir / "pool/measure.txt").read_text().splitlines()
           if " (hidden): hit@5" in line}
    assert got == want and len(got) == 400
    hits = sum(1 for k in want if int(k[1:]) <= 720)
    assert p["hit5"] == hits and p["full"] == hits
    text = (plant.root / "governance/project/path-map.yaml").read_text()
    assert "memory-pool:" in text and "memory-pool-draw:" in text and "memory-pool-draw/hidden/**" in text
    assert not (plant.root / "fixtures/evaluation/memory-pool-draw").exists()  # made fresh, removed after
    assert len(list((plant.run_dir / "pool/kept").glob("*.json"))) == 400


def test_a_draw_of_a_smaller_size_follows_the_same_code(plant, monkeypatch):
    monkeypatch.setattr(pool, "DRAW_N", 30)
    fake = with_figures(plant)
    plant_pool(plant, fake, 90, 90)
    word, lines = run_pool(plant, monkeypatch, seed=99)
    assert word == "ok" and lines[0].startswith("POOL 30 of 90: hit@5 30 (100.0 %)")
    p = json.loads((plant.run_dir / "POOL.json").read_text())
    assert (p["size"], p["drawn"], p["seed"]) == (90, 30, 99)


# ---- the comparison and the regression

@pytest.mark.parametrize("now,named", [(38, True), (39, False)])
def test_a_fall_of_3_points_or_more_in_either_figure_is_named_a_regression(plant, monkeypatch, now, named):
    earlier(plant, 100, 80, 80)  # 80.0 %: 38 of 50 is 76.0 (a fall of 4), 39 of 50 is 78.0 (a fall of 2)
    fake = with_figures(plant)
    plant_pool(plant, fake, 50, now)
    word, lines = run_pool(plant, monkeypatch, seed=1)
    assert word == "ok"  # a regression is printed and recorded, never an exit code
    p = json.loads((plant.run_dir / "POOL.json").read_text())
    assert p["regression"] is named and p["last_audit"] == OLD and (p["last_hit5"], p["last_full"]) == (80, 80)
    assert (p["hit5"], p["full"]) == (now, now)
    assert any(line.startswith("POOL ") and f"last audit {OLD}: hit@5 80 of 100 (80.0 %)" in line for line in lines)
    assert ("POOL REGRESSION hit@5 80.0 -> 76.0 %" in lines) is named
    assert ("POOL REGRESSION full evidence 80.0 -> 76.0 %" in lines) is named
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["pool"]["regression"] is named


def test_a_fall_in_full_evidence_alone_is_named_with_its_own_word(plant, monkeypatch):
    earlier(plant, 50, 38, 50)
    fake = with_figures(plant)
    plant_pool(plant, fake, 50, 38)  # hit@5 unchanged; full evidence 76 % against 100 %
    fake.save()
    word, lines = run_pool(plant, monkeypatch, seed=1)
    assert [x for x in lines if "REGRESSION" in x] == ["POOL REGRESSION full evidence 100.0 -> 76.0 %"]


# ---- refusals

def test_pool_needs_figures_and_runs_once(plant, monkeypatch):
    fake, _, _ = measured(plant)
    plant_pool(plant, fake, 20, 20)
    assert plant.cli(*pool_args(plant)).stdout == "MS-NOFIGURES\n"
    (plant.run_dir / "FIGURES.json").write_text(json.dumps({"audit": AUDIT, "pool": None, "classes": None}))
    assert plant.cli(*pool_args(plant)).returncode == 0
    before = snapshot(plant.run_dir)
    again = plant.cli(*pool_args(plant))
    assert again.returncode == 3 and again.stdout == "USED\n" and snapshot(plant.run_dir) == before


def test_a_gov_of_another_pin_or_a_changed_set_is_refused_before_anything_is_written(plant, tmp_path):
    fake = with_figures(plant)
    other = tmp_path / "other/pin-ffffffffffff/bin"
    other.mkdir(parents=True)
    (other / "gov").write_text("#!/bin/sh\n")
    args = pool_args(plant)
    args[args.index("--gov") + 1] = str(other / "gov")
    done = plant.cli(*args)
    assert done.returncode == 1 and done.stdout == "MS-PIN\n" and not (plant.run_dir / "POOL.json").exists()
    (plant.hidden / "q01.yaml").write_text((plant.hidden / "q01.yaml").read_text() + "# edited\n")
    done = plant.cli(*pool_args(plant))
    assert done.returncode == 1 and done.stdout == "MS-DIGEST\n"


def test_a_different_file_in_the_pool_under_the_audits_name_is_ms_pooldiff_and_an_equal_one_is_skipped(plant):
    fake = with_figures(plant)
    plant_pool(plant, fake, 10, 10)
    folder = plant.root / "fixtures/evaluation/memory-pool/hidden"
    (folder / f"{AUDIT}-q02.yaml").write_bytes((plant.hidden / "q02.yaml").read_bytes())  # equal: skipped
    (folder / f"{AUDIT}-q03.yaml").write_text("different: 1\n")
    done = plant.cli(*pool_args(plant))
    assert done.returncode == 1 and done.stdout.splitlines()[-1] == "MS-POOLDIFF"
    assert (folder / f"{AUDIT}-q03.yaml").read_text() == "different: 1\n"  # never overwritten
    assert (folder / f"{AUDIT}-q01.yaml").read_bytes() == (plant.hidden / "q01.yaml").read_bytes()


def test_a_map_that_cannot_take_the_entry_is_dc_map_and_nothing_is_written(plant):
    map_path = plant.root / "governance/project/path-map.yaml"
    text = map_path.read_text().replace("evaluation_sets:\n", (
        "evaluation_sets:\n  memory-pool:\n    visible: []\n    hidden: [\"fixtures/evaluation/memory-pool/hidden/**\"]\n"
        "    measures:\n      roles: [engineer]\n"), 1)
    map_path.write_text(text)
    fake = with_figures(plant)
    before = map_path.read_bytes()
    done = plant.cli(*pool_args(plant))
    assert done.returncode == 1 and done.stdout == "DC-MAP\n"
    assert map_path.read_bytes() == before and not (plant.run_dir / "POOL.json").exists()


def test_a_pool_run_that_is_not_whole_is_ms_poolfault(plant):
    fake = with_figures(plant)
    plant_pool(plant, fake, 12, 12)
    q = list((plant.root / "fixtures/evaluation/memory-pool/hidden").glob("*.yaml"))[0]
    text = yaml.safe_load(q.read_text())["question"]
    fake.override(text, 1, rerank_by="private")
    fake.save()
    done = plant.cli(*pool_args(plant))
    assert done.returncode == 1 and done.stdout.splitlines()[-1] == "MS-POOLFAULT"
    assert not (plant.root / "fixtures/evaluation/memory-pool-draw").exists()


# ---- pool-import

def plant_import_sets(plant, verdict2=80, visible=40, hidden=40, verdict=60):
    ev = plant.root / "fixtures/evaluation"

    def put(set_name, part, ids, apart):
        folder = ev / set_name / part
        folder.mkdir(parents=True, exist_ok=True)
        for i in ids:
            q = question(1, plant.repo["head"])
            q.update(id=i, category="nonexistent-id" if i == apart else "decision")
            (folder / f"{i}.yaml").write_text(yaml.safe_dump(q, sort_keys=False), encoding="utf-8")
    put("memory-verdict-2", "hidden", [f"q{i:02d}" for i in range(1, verdict2 + 1)], f"q{verdict2:02d}")
    put("memory-retrieval", "visible", [f"v{i:02d}" for i in range(1, visible + 1)], None)
    put("memory-retrieval", "hidden", [f"h{i:02d}" for i in range(1, hidden + 1)], "h24")
    put("memory-verdict", "hidden", [f"m{i:02d}" for i in range(1, verdict + 1)], f"m{verdict:02d}")


def import_args(plant):
    return ["pool-import", "--sets-root", str(plant.root)]


def test_pool_import_copies_the_79_and_the_138_each_less_its_nonexistent_id_question(plant):
    plant_import_sets(plant)
    done = plant.cli(*import_args(plant))
    assert done.returncode == 0, done.stdout
    folder = plant.root / "fixtures/evaluation/memory-pool/hidden"
    names = sorted(x.name for x in folder.glob("*.yaml"))
    assert len(names) == 217
    assert sum(n.startswith("memory-verdict-2-") for n in names) == 79 and "memory-verdict-2-q80.yaml" not in names
    assert sum(n.startswith(("memory-retrieval-", "memory-verdict-q")) or n.startswith("memory-verdict-m") for n in names) == 138
    assert "memory-retrieval-h24.yaml" not in names and "memory-verdict-m60.yaml" not in names
    src = plant.root / "fixtures/evaluation/memory-retrieval/visible/v01.yaml"
    assert (folder / "memory-retrieval-v01.yaml").read_bytes() == src.read_bytes()
    imported = json.loads((plant.root / "runs/memory-pool/IMPORTED.json").read_text())
    assert imported["counts"] == {"memory-verdict-2": 79, "earlier": 138} and imported["total"] == 217
    assert imported["digest"] == set_digest(folder)
    again = plant.cli(*import_args(plant))
    assert again.returncode == 1 and again.stdout == "MS-IMPORTED\n"


@pytest.mark.parametrize("kw", [{"verdict2": 79}, {"visible": 39}, {"verdict": 59}])
def test_pool_import_with_another_count_is_ms_importcount_and_writes_nothing(plant, kw):
    plant_import_sets(plant, **kw)
    done = plant.cli(*import_args(plant))
    assert done.returncode == 1 and done.stdout == "MS-IMPORTCOUNT\n"
    assert not list((plant.root / "fixtures/evaluation/memory-pool/hidden").glob("*.yaml"))
    assert not (plant.root / "runs/memory-pool").exists()


# ---- classes

def plant_misses(plant, ids):
    plant.run_dir.mkdir(parents=True, exist_ok=True)
    (plant.run_dir / "misses.jsonl").write_text("".join(json.dumps({"id": i}) + "\n" for i in ids))
    (plant.run_dir / "FIGURES.json").write_text(json.dumps({"audit": AUDIT, "classes": None, "pool": None}))


def classes_args(plant):
    return ["classes", "--sets-root", str(plant.root), "--audit", AUDIT]


def test_classes_adds_the_five_counts_to_figures_json_summing_to_the_misses(plant):
    plant_misses(plant, ["q01", "q02", "q03", "q04", "q05"])
    doc = {"q01": "gold_wrong", "q02": "retrieval_miss", "q03": "answer_wrong", "q04": "retrieval_miss",
           "q05": "out_of_scope"}
    (plant.run_dir / "miss-classes.json").write_text(json.dumps({k: {"class": v, "reason": "a reason"} for k, v in doc.items()}))
    done = plant.cli(*classes_args(plant))
    assert done.returncode == 0, done.stdout
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["classes"] == {"gold_wrong": 1, "question_ambiguous": 0, "out_of_scope": 1, "retrieval_miss": 2,
                            "answer_wrong": 1}
    assert "a reason" not in (plant.run_dir / "FIGURES.json").read_text() and "a reason" not in done.stdout


@pytest.mark.parametrize("ids,klass", [(["q01", "q02"], "gold_wrong"), (["q01", "q02", "q03", "q09"], "gold_wrong"),
                                       (["q01", "q02", "q03"], "not_a_class")])
def test_classes_for_other_ids_or_another_class_is_ms_classes_and_changes_nothing(plant, ids, klass):
    plant_misses(plant, ["q01", "q02", "q03"])
    (plant.run_dir / "miss-classes.json").write_text(json.dumps({i: {"class": klass, "reason": "r"} for i in ids}))
    before = (plant.run_dir / "FIGURES.json").read_bytes()
    done = plant.cli(*classes_args(plant))
    assert done.returncode == 1 and done.stdout == "MS-CLASSES\n"
    assert (plant.run_dir / "FIGURES.json").read_bytes() == before


def test_classes_without_figures_is_ms_nofigures(plant):
    plant.run_dir.mkdir(parents=True)
    done = plant.cli(*classes_args(plant))
    assert done.returncode == 1 and done.stdout == "MS-NOFIGURES\n"
