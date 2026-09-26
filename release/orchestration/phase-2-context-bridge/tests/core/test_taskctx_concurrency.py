"""BR-DAG-AMEND-R1-14 regression test.

``govbridge.core.taskctx.ExclusionCounter.bump`` used to do a plain ``self.count += n`` -- a read-modify-write, not
atomic across bytecode boundaries under the GIL, so several threads bumping the SAME counter concurrently
(``govbridge.gather.engine`` shares one ``ExclusionCounter`` across its ``--threads`` worker pool) could lose an
update. This module proves ``excluded_hits`` (``ExclusionCounter.count``) is EXACT under real concurrency, two
ways: (1) many threads hammering ``bump()`` directly, with the final count checked against the exact expected
total; (2) a real ``govbridge.gather.engine.gather()`` call against a fixture repo whose evidence spans several
excluded-path hits, run once at ``--threads 1`` and once at ``--threads 16`` over the SAME query/corpus, asserting
the reported ``excluded_hits`` is identical either way; (3) a DETERMINISTIC structural test
(``test_bump_serialises_through_a_lock``), because CPython 3.12's specializing adaptive interpreter makes the bare
pre-fix ``self.count += n`` appear atomic in ordinary busy-loop stress tests on this interpreter build -- (1) and
(2) below pass even against the UNFIXED implementation here, empirically confirmed while preparing this repair (a
lost update needs a genuine GIL-drop between the load and the store of ``count``, and this build's adaptive
bytecode specialisation for a tiny slots-attribute increment leaves too narrow a window to hit reliably in a
reasonable stress-test budget). (3) is the test that actually FAILS against the pre-fix module and PASSES against
the fixed one, deterministically, by asserting the structural fix itself (a lock ``bump`` genuinely blocks on).
"""
from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path

import pytest

from govbridge.core import freshness, store as storemod, taskctx as taskctxmod

FIXTURES_GATHER = Path(__file__).resolve().parents[1] / "fixtures" / "gather"
sys.path.insert(0, str(FIXTURES_GATHER))
import gather_repobuilder as repobuilder  # noqa: E402

TEST_FACETS_PATH = str(FIXTURES_GATHER / "test-facets.yaml")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


# --- (1) direct, high-contention hammering of one shared counter -------------------------------------------------

def test_many_threads_bumping_one_counter_produce_an_exact_count():
    counter = taskctxmod.ExclusionCounter()
    n_threads = 16
    bumps_per_thread = 2000
    expected = n_threads * bumps_per_thread

    barrier = threading.Barrier(n_threads)

    def worker():
        barrier.wait()  # maximise actual overlap, rather than threads starting staggered
        for _ in range(bumps_per_thread):
            counter.bump()

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
        assert not t.is_alive(), "a worker thread did not finish within the timeout"

    assert counter.count == expected, f"expected exactly {expected}, got {counter.count} (lost updates)"


def test_many_threads_bumping_with_varying_n_produce_an_exact_sum():
    counter = taskctxmod.ExclusionCounter()
    n_threads = 12
    per_thread_n = list(range(1, n_threads + 1))  # thread i bumps by (i+1), 50 times
    repeats = 50
    expected = sum(n * repeats for n in per_thread_n)

    barrier = threading.Barrier(n_threads)

    def worker(n: int):
        barrier.wait()
        for _ in range(repeats):
            counter.bump(n)

    threads = [threading.Thread(target=worker, args=(n,)) for n in per_thread_n]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert counter.count == expected


# --- (2) a real gather at --threads 16 vs --threads 1 discloses the SAME excluded_hits ----------------------------

def _built_repo_with_excluded_content(tmp_path, monkeypatch):
    """tests/fixtures/gather's own fixture repo (GA1's), plus one path per area added under an `excluded/` prefix
    so a task's retrieval_exclusions has real work to do across every one of the concurrently-run facets/routes."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    br = repobuilder.build(tmp_path)
    for area in repobuilder.AREAS:
        (br.root / "excluded" / area).mkdir(parents=True, exist_ok=True)
        (br.root / "excluded" / area / "note.md").write_text(
            f"# excluded {area} note\n\n{repobuilder.TERM} evidence item excluded-{area}: an excluded-path "
            f"duplicate of this area's own {repobuilder.TERM} evidence, present so a task's retrieval_exclusions "
            f"has real hits to drop.\n",
            encoding="utf-8",
        )
    _git(br.root, "add", "-A")
    _git(br.root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "c2: excluded dupes")
    r = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return br


def _gather_excluded_hits(br, threads: int) -> int:
    from govbridge.gather import engine as enginemod
    from govbridge.route import real_routes

    task = taskctxmod.TaskContext(source="test", retrieval_exclusions=("excluded/**",))
    routes = real_routes.build_real_routes(view_path=br.view_path, repo=str(br.root), registry_path=br.registry_path)
    # TWO active facets (test-facets.yaml's own "purpose"/"requirement", both lexical): gather.engine only ever
    # opens a ThreadPoolExecutor when more than one facet is active in a round, so a single-facet query would take
    # the identical sequential code path at every --threads value and never actually exercise concurrent bump()
    # calls at all. batch_size is deliberately >= the whole fixture's chunk count (15 lexical chunks: 10 original +
    # 5 excluded/** duplicates) so every route's own overfetch-then-exclude-filter (govbridge.lexical.query, out of
    # this node's scope) resolves the WHOLE corpus in a single round -- avoiding this route's own multi-round
    # pagination-under-exclusion behaviour (a separate, pre-existing concern, not this test's subject) so the
    # concurrent and sequential runs both do EXACTLY the same amount of work, deterministically.
    query = {"id": "Q1", "text": repobuilder.TERM, "class": None, "subject": None,
             "facets": ["purpose", "requirement"]}
    result = enginemod.gather(query, routes, task=task, batch_size=20, max_rounds=5, threads=threads,
                               facets_path=TEST_FACETS_PATH)
    assert result["stop_reason"] in enginemod.STOP_REASONS
    return result["excluded_hits"]


def test_gather_reports_identical_excluded_hits_at_threads_16_and_threads_1(monkeypatch, tmp_path):
    br = _built_repo_with_excluded_content(tmp_path, monkeypatch)

    # independent second measurement (R1-T2 rule 3): one excluded/**/note.md per area, never CONTRACT-classified,
    # so "requirement" (scoped to CONTRACT/FROZEN_GATE_CONTRACT) never even candidates them -- only "purpose"
    # (unscoped) does.
    expected_excluded = len(repobuilder.AREAS)

    excluded_1 = _gather_excluded_hits(br, threads=1)
    excluded_16 = _gather_excluded_hits(br, threads=16)

    assert excluded_1 == expected_excluded, (excluded_1, expected_excluded)
    assert excluded_16 == excluded_1, (
        f"--threads 16 reported excluded_hits={excluded_16}, --threads 1 reported {excluded_1} -- "
        "ExclusionCounter lost updates under concurrency"
    )


# --- (3) the deterministic structural regression: bump() genuinely serialises through a lock ----------------------

def test_bump_serialises_through_a_lock():
    """Deterministic regression test. Asserts the STRUCTURAL fix itself rather than relying on a busy-loop race
    actually manifesting (this module's docstring explains why (1)/(2) above cannot be trusted to fail against the
    pre-fix module on this interpreter): ``ExclusionCounter`` must expose a lock-like object, and ``bump()`` must
    actually acquire it -- proven by holding the counter's own lock from the main thread and confirming a
    concurrently-launched ``bump()`` call BLOCKS until the lock is released, applying exactly once only then.
    Against the pre-fix class (no lock attribute at all) this fails immediately and unambiguously."""
    counter = taskctxmod.ExclusionCounter()
    lock = getattr(counter, "_lock", None)
    assert lock is not None and hasattr(lock, "acquire") and hasattr(lock, "release"), (
        "ExclusionCounter has no lock-like attribute for bump() to serialise through"
    )

    assert lock.acquire(timeout=1), "could not acquire the counter's own lock from the main thread"
    bumped = threading.Event()

    def worker():
        counter.bump()
        bumped.set()

    t = threading.Thread(target=worker)
    t.start()
    try:
        # the worker's bump() must be BLOCKED on the lock this test still holds -- it must not have applied yet.
        completed_too_early = bumped.wait(timeout=0.3)
        assert not completed_too_early, "bump() completed while this test held the counter's own lock"
        assert counter.count == 0
    finally:
        lock.release()
    t.join(timeout=5)
    assert not t.is_alive()
    assert counter.count == 1
