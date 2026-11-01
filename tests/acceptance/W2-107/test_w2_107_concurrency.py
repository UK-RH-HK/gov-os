"""W2-107: several threads and several processes use one cache at once and get the right verdicts and no error.

The design's concurrency (several rebuilds and the filter's own threads use the cache at once); KPI success 4 and
failure 3 under load (a locked or busy cache that stops a rebuild or answers clean). The cache starts absent, so the
callers also race to make it. Then the cache is shown whole: a quiet pass (which writes again any verdict whose write
the race made fail, as the design allows) and after it a pass in which only the texts holding the secret are scanned.
"""

from __future__ import annotations

import threading

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

FILES = {f"docs/page-{number}.md": f"W2-107: page {number}, ordinary text.\n" for number in range(4)}
THREADS = 6


def scene(project):
    rels = support.put(project, FILES)
    secret = support.put(project, {"docs/planted.md": f"The value is {support.planted()} today.\n"})
    names = ["docs/an-ordinary-name.md", f"docs/{support.planted()}/page.md"]
    return rels, secret, names


def test_several_threads_judging_the_same_files_at_once_get_the_right_verdicts(project, engine, cache):
    rels, secret, names = scene(project)
    findings = support.uncached(engine, lambda: (secrets.indexable(project, secret),
                                                 secrets.path_holds_secret(project, names[1])))[1]
    gate, results, errors = threading.Barrier(THREADS), [], []

    def work():
        try:
            gate.wait(timeout=60)
            results.append((secrets.indexable(project, secret + rels),
                            [secrets.path_holds_secret(project, name) for name in names]))
        except Exception as error:  # noqa: BLE001 - every error is the finding
            errors.append(type(error).__name__)

    threads = [threading.Thread(target=work) for _ in range(THREADS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=support.CHILD_TIMEOUT_S)
    assert not any(thread.is_alive() for thread in threads), "every thread finished: none hangs on the cache"
    assert errors == [], f"no thread met an error: {errors}"
    assert results == [(rels, [False, True])] * THREADS, "every thread got the right verdicts"
    for label in ("the quiet pass", "the pass after it"):
        verdicts, calls = support.counted(engine, lambda: (secrets.indexable(project, secret + rels),
                                                           [secrets.path_holds_secret(project, name) for name in names]))
        assert verdicts == (rels, [False, True]), f"{label}: the verdicts are right"
    assert calls == findings, "after the race, the cache is whole: the clean texts are remembered"


def test_two_processes_judging_the_same_files_at_once_get_the_right_verdicts(project, engine, cache):
    rels, secret, names = scene(project)
    findings = support.counted(engine, lambda: support.run_child(project, secret, names[1:],
                                                                 support.child_env(engine, "")))[1]
    env = support.child_env(engine, cache)
    started = [support.start_child(project, secret + rels, names, env) for _ in range(2)]
    runs = [support.finish_child(each) for each in started]
    for number, run in enumerate(runs):
        assert run.error is None, f"process {number + 1} met {run.error}"
        assert run.indexable == rels and run.names == [False, True], f"process {number + 1}: the verdicts are right"
    for label in ("the quiet pass", "the pass after it"):
        run, calls = support.counted(engine, lambda: support.run_child(project, secret + rels, names, env))
        assert run.error is None and run.indexable == rels and run.names == [False, True], f"{label}: the verdicts"
    assert calls == findings, "after the race, the cache is whole: the clean texts are remembered"
