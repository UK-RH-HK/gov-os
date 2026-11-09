"""S16, measured (``local_only``: the CTO runs it outside the sandbox, on the real machine, through no other slot).

Measured, in the evidence: a planted test suite whose tests each start a program that uses every CPU, run in one slot,
keeps the machine's busy cores within the slot's share plus one, where without the budget and the CPU set it does
not; and its time with them against without (no more than 20 % slower on the planted suite)
[DEC-1038 (4), P-W2-20-THREAD-BUDGET (a)].

How: the planted suite is ``TESTS`` small pytest tests, each starting a program that spins one thread per CPU it
believes the machine has (``os.cpu_count()``, ignoring its CPU set) for ``SPIN_S`` seconds, run with ``-n WORKERS``
when pytest-xdist is there, else serially. It is run twice, once through ``gov resources --slot test`` and once
plainly, under the real gate configuration (``~/.gov-os/machine/gate.json``, read, never written). Busy cores are
sampled from ``/proc/stat`` every 0.2 s during each run; the 95th percentile is compared. Run:

    PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-20/test_w2_20_measured.py -m local_only -p no:cacheprovider

The case prints both figures and both times for the evidence record.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

import w2_20_support as support

pytestmark = pytest.mark.local_only

TESTS, WORKERS, SPIN_S = 8, 2, 3.0

SPIN = r'''
import os, sys, threading, time
end = time.monotonic() + float(sys.argv[1])
def spin():
    while time.monotonic() < end:
        pass
threads = [threading.Thread(target=spin) for _ in range(os.cpu_count() or 1)]
[t.start() for t in threads]
[t.join() for t in threads]
'''


def _cpu_times():
    fields = Path("/proc/stat").read_text().splitlines()[0].split()[1:]
    values = [int(v) for v in fields]
    idle = values[3] + values[4]
    return sum(values), idle


def _busy_p95(run) -> tuple[float, float]:
    samples, stop = [], threading.Event()

    def watch():
        last = _cpu_times()
        while not stop.is_set():
            time.sleep(0.2)
            now = _cpu_times()
            total, idle = now[0] - last[0], now[1] - last[1]
            if total:
                samples.append((total - idle) / total * os.cpu_count())
            last = now
    watcher = threading.Thread(target=watch)
    began = time.monotonic()
    watcher.start()
    try:
        run()
    finally:
        stop.set()
        watcher.join()
    samples.sort()
    return samples[int(0.95 * (len(samples) - 1))] if samples else 0.0, time.monotonic() - began


def test_s16_one_slot_holds_a_cpu_hungry_suite_to_its_share_plus_one_within_20_percent_of_the_time(tmp_path):
    real_home = Path.home()
    config = json.loads((real_home / ".gov-os/machine/gate.json").read_text())
    slots = config["heavy_slots"]["value"]
    suite = tmp_path / "suite"
    suite.mkdir()
    (suite / "spin.py").write_text(SPIN)
    (suite / "test_spin.py").write_text(
        "import subprocess, sys, pytest\n"
        f"@pytest.mark.parametrize('n', range({TESTS}))\n"
        "def test_spin(n):\n"
        f"    subprocess.run([sys.executable, {str(suite / 'spin.py')!r}, '{SPIN_S}'], check=True)\n")
    try:
        import xdist  # noqa: F401
        parallel = ["-n", str(WORKERS)]
    except ImportError:
        parallel = []
    pytest_argv = [sys.executable, "-m", "pytest", str(suite), "-q", "-p", "no:cacheprovider", *parallel]
    env = {**os.environ, "PYTHONPATH": str(support.SRC)}

    def plain():
        subprocess.run(pytest_argv, env=env, check=True, capture_output=True, timeout=600)

    def in_slot():
        subprocess.run([sys.executable, "-m", "gov.cli.main", "resources", "--slot", "test",
                        "--workers", str(WORKERS if parallel else 1), "--", *pytest_argv], env=env, check=True,
                       capture_output=True, timeout=600)

    without_busy, without_s = _busy_p95(plain)
    with_busy, with_s = _busy_p95(in_slot)
    share = max(1, len(os.sched_getaffinity(0)) // slots)
    print(f"\nS16 evidence: share {share} of {len(os.sched_getaffinity(0))} CPUs ({slots} slots); busy cores p95 "
          f"with the slot {with_busy:.2f}, without {without_busy:.2f}; time with {with_s:.1f} s, without "
          f"{without_s:.1f} s ({(with_s / without_s - 1) * 100:+.0f} %)")
    assert without_busy > share + 1, "the planted suite does not exceed the share without the slot: no measure"
    assert with_busy <= share + 1, f"in one slot the busy cores reached {with_busy:.2f}, above the share {share} + 1"
    assert with_s <= 1.2 * without_s, f"the slot made the suite {(with_s / without_s - 1) * 100:.0f} % slower"
