"""Builder tests for W2-88 S27-W (DEC-1156 (7), the 11-16 nightly): folder mode keeps S27's bound (DEC-1183 (2), run
9) of at least 10 texts per gitleaks process on average, both rule sets counted, whatever the worker width.

Each batch starts one ``gitleaks dir`` per rule set, so for N texts and R rule sets the batches number at most N / (10 R)
wherever N >= 10 R (one batch below that). The width still caps the batches the bound allows, and the caps
``_BATCH_TEXTS`` and ``_BATCH_BYTES`` still split a batch. Regression evidence only (DEC-136); no secret anywhere here.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from gov import secrets

REPO = Path(__file__).resolve().parents[3]
MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
FLOOR = 10  # texts per gitleaks process, on average (S27, DEC-1183 (2))


def _split(count: int, width: int, rule_sets: int, sizes: list[int] | None = None) -> list[list[int]]:
    items = list(range(count))
    return list(secrets._batches(items, sizes or [100] * count, width, rule_sets=rule_sets))


def _bound_holds(batches: list[list[int]], count: int, width: int, rule_sets: int) -> None:
    """Every text once, in order; the bound; no batch under the floor (the last aside where the split is uneven);
    no more batches than the width or the text cap asks."""
    assert [item for batch in batches for item in batch] == list(range(count))
    floor = FLOOR * rule_sets
    if count >= floor:
        assert len(batches) * rule_sets * FLOOR <= count, "more gitleaks processes than one per 10 texts"
    whole = batches if count % len(batches) == 0 else batches[:-1]
    assert all(len(batch) >= min(count, floor) for batch in whole)
    assert len(batches) <= max(width, -(-count // secrets._BATCH_TEXTS))


# The batch counts: (texts, rule sets) -> {width: batches}.
COUNTS = {
    (300, 1): {1: 1, 3: 3, 20: 20, 64: 30},
    (300, 2): {1: 1, 3: 3, 20: 15, 64: 15},
    (600, 1): {1: 1, 3: 3, 20: 20, 64: 60},
    (600, 2): {1: 1, 3: 3, 20: 20, 64: 30},
    (7, 1): {1: 1, 3: 1, 20: 1, 64: 1},  # under 10 R: one batch
    (15, 2): {1: 1, 3: 1, 20: 1, 64: 1},  # under 10 R: one batch
}


@pytest.mark.parametrize("count, rule_sets, width, expected",
                         [(count, rule_sets, width, expected) for (count, rule_sets), widths in COUNTS.items()
                          for width, expected in widths.items()],
                         ids=lambda value: str(value))
def test_the_batch_count_keeps_the_bound_for_every_width(count, rule_sets, width, expected):
    batches = _split(count, width, rule_sets)
    assert len(batches) == expected
    _bound_holds(batches, count, width, rule_sets)


def test_batches_are_spread_evenly_where_the_texts_do_not_divide():
    batches = _split(310, 20, 2)  # 15 batches allowed: 21 texts in ten of them, 20 in five
    assert len(batches) == 15 and {len(batch) for batch in batches} == {20, 21}
    _bound_holds(batches, 310, 20, 2)


@pytest.mark.parametrize("width, expected", [(1, 5), (3, 5), (20, 20), (64, 64)])
def test_the_width_still_caps_the_batches_on_a_large_list(width, expected):
    """5,000 texts, two rule sets: the bound allows 250 batches; the width caps them, and the text cap of 1,000
    makes at least 5 (so width 3 gives 5 batches of 1,000, never 3 of 1,667)."""
    batches = _split(5_000, width, 2)
    assert len(batches) == expected
    assert all(len(batch) <= secrets._BATCH_TEXTS for batch in batches)
    _bound_holds(batches, 5_000, width, 2)


def test_a_text_over_the_byte_cap_is_still_a_batch_of_its_own():
    sizes = [100] * 30
    sizes[5] = secrets._BATCH_BYTES + 1
    batches = _split(30, 3, 1, sizes)
    assert [item for batch in batches for item in batch] == list(range(30))
    assert [5] in batches
    assert all(sum(sizes[item] for item in batch) <= secrets._BATCH_BYTES for batch in batches if batch != [5])


@pytest.mark.parametrize("cpus, expected", [(20, {300: 15, 600: 20}), (64, {300: 15, 600: 30})])
def test_the_width_from_the_cpu_set_with_no_slot_budget(monkeypatch, cpus, expected):
    monkeypatch.delenv("GOV_HEAVY_THREAD_BUDGET", raising=False)
    monkeypatch.setattr(secrets.os, "sched_getaffinity", lambda pid: set(range(cpus)), raising=False)
    width = secrets._workers()
    assert width == cpus
    for count, batches in expected.items():
        split = _split(count, width, 2)
        assert len(split) == batches
        _bound_holds(split, count, width, 2)


def test_the_slot_budget_still_runs_batches_side_by_side(monkeypatch):
    """S27's parallel behaviour: 600 texts, two rule sets, budget 3 -> 3 batches, as many as the width."""
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "3")
    monkeypatch.setattr(secrets.os, "sched_getaffinity", lambda pid: set(range(20)), raising=False)
    assert len(_split(600, secrets._workers(), 2)) == 3


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
def test_indexable_on_20_cpus_starts_at_most_one_gitleaks_per_10_files(tmp_path, monkeypatch):
    """The nightly's shape, with a stand-in for each ``gitleaks dir`` (it answers clean): 300 files, the rule sets of
    the template's ``.gitleaks.toml``, 20 CPUs and no slot budget."""
    root = tmp_path / "project"
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/path-map.yaml").write_text(MAP, encoding="utf-8")
    (root / ".gitleaks.toml").write_text((REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"),
                                         encoding="utf-8")
    (root / "notes").mkdir()
    rels = []
    for number in range(300):
        (root / f"notes/n{number:03d}.md").write_text(f"Plain {number}.\n", encoding="utf-8")
        rels.append(f"notes/n{number:03d}.md")
    monkeypatch.delenv("GOV_HEAVY_THREAD_BUDGET", raising=False)
    monkeypatch.delenv("GOV_SECRETS_CACHE", raising=False)
    monkeypatch.setattr(secrets.os, "sched_getaffinity", lambda pid: set(range(20)), raising=False)
    real, runs = secrets.subprocess.run, []

    def run(command, **options):
        if command and command[0] == "gitleaks" and command[1] == "dir":
            runs.append(len(list(Path(options["cwd"]).iterdir())))
            return subprocess.CompletedProcess(command, 0, b"[]", b"")
        return real(command, **options)

    monkeypatch.setattr(secrets.subprocess, "run", run)
    rule_sets = len(secrets._rules(root))
    assert secrets.indexable(root, rels) == rels
    assert len(runs) * FLOOR <= 300
    assert len(runs) == 300 // (FLOOR * rule_sets) * rule_sets
