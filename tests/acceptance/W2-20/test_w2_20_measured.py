"""S16, measured (``local_only``: the CTO runs it outside the sandbox, on the real machine, through no other slot).

Measured, in the evidence: a planted test suite whose tests each start a program that uses every CPU, run in one slot,
keeps the machine's busy cores within the slot's share plus one, where without the budget and the CPU set it does
not; and its time with them against without (no more than 20 % slower on the planted suite)
[DEC-1038 (4), P-W2-20-THREAD-BUDGET (a)].

How: the planted suite is ``TESTS`` small pytest tests, each starting a program that forks one spinning process per CPU
it believes the machine has (``os.cpu_count()``, ignoring its CPU set) for ``SPIN_S`` seconds, run with ``-n WORKERS``
when pytest-xdist is there, else serially. It is run twice, once through ``gov resources --slot test`` and once
plainly, under the real gate configuration (``~/.gov-os/machine/gate.json``, read, never written). Busy cores are
sampled per CPU, from the ``cpuN`` lines of ``/proc/stat``, every 0.2 s during each run; the 95th percentile is
compared.

The share is the slot's real one, by S17's rule in the README's interface (round 6, the review's F3): the slots' CPUs
are this process's CPUs (``os.sched_getaffinity``, which ``gov resources`` inherits) less every CPU the file's
``embedding_servers`` section names, and the share is ``max(1, len(slots' CPUs) // heavy_slots)``. Each planted program
records the CPU set it ran on, and the case checks that inside the slot it was the share.

The measure is per CPU (round 8, DEC-1105, the review's R2-F2): the background is sampled once, before the plain run,
on a quiet machine (after a settle, for ``BACKGROUND_S`` seconds with nothing of the case running), per CPU.

- **Without the slot** (unchanged): the whole machine's busy cores, the run's p95 less the background's median, must
  exceed the share + 1 (else there is no measure).
- **With the slot:** the busy cores **on the slot's own CPUs** only (the CPU set the planted programs recorded), the
  run's p95, at most the share + 1. The rest of the machine does not enter this figure, so its background cannot
  push it over (run 2 of round 3's code failed by 0.003 on the whole machine's background tail).
- **No program escaped the set:** the CPUs outside the slot's set gained no more than the background during the
  slot's run: their median busy cores in the slot's run is at most their own median in the background (the same
  CPUs) plus one core. A program that escaped would put most of its ``os.cpu_count()`` spinning processes there.
- **The suite loaded its slot:** the slot's CPUs' p95 is at least half the share (else the slot ran nothing to
  measure).

The busy cores on a set of CPUs can never exceed the set's size, so the "with the slot" bar alone holds by
construction once the set is the share; the CPU-set check and the escape check carry the evidence that the whole load
stayed in the slot. The case prints every figure. Run:

    GOV_W2_20_MEASURE=1 PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-20/test_w2_20_measured.py \
        -m local_only -p no:cacheprovider -s

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

pytestmark = [
    pytest.mark.local_only,
    pytest.mark.skipif(os.environ.get("GOV_W2_20_MEASURE") != "1",
                       reason="S16 measures the real machine: the CTO runs it with GOV_W2_20_MEASURE=1 -m local_only"),
]

TESTS, WORKERS, SPIN_S = 8, 2, 3.0
BACKGROUND_S, SETTLE_S = 5.0, 2.0

# One forked process per CPU, not threads: the GIL holds a program's threads to about one core (round 5).
# Each program writes the CPU set it runs on to seen/<pid>.json beside it (round 6).
SPIN = r'''
import json, os, sys, time
from pathlib import Path
seen = Path(__file__).resolve().parent / "seen"
seen.mkdir(exist_ok=True)
(seen / f"{os.getpid()}.json").write_text(json.dumps(sorted(os.sched_getaffinity(0))))
end = time.monotonic() + float(sys.argv[1])
children = []
for _ in range(os.cpu_count() or 1):
    pid = os.fork()
    if pid == 0:
        while time.monotonic() < end:
            pass
        os._exit(0)
    children.append(pid)
print(f"spin: {len(children)} processes for {os.cpu_count()} CPUs", flush=True)
for pid in children:
    os.waitpid(pid, 0)
'''


def _cpu_times() -> dict[int, tuple[int, int]]:
    """``{cpu: (total, idle)}`` from the ``cpuN`` lines of ``/proc/stat`` (idle counts iowait), one entry per CPU."""
    times = {}
    for line in Path("/proc/stat").read_text().splitlines():
        name, *fields = line.split()
        if name.startswith("cpu") and name[3:].isdigit():
            values = [int(v) for v in fields]
            times[int(name[3:])] = (sum(values), values[3] + values[4])
    return times


def _cores(samples: list[dict[int, float]], cpus=None) -> list[float]:
    """Each sample's busy cores on ``cpus`` (every CPU when None): the sum of those CPUs' busy fractions."""
    return [sum(busy for cpu, busy in sample.items() if cpus is None or cpu in cpus) for sample in samples]


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    return ordered[int(0.95 * (len(ordered) - 1))] if ordered else 0.0


def _median(samples: list[float]) -> float:
    ordered = sorted(samples)
    return ordered[(len(ordered) - 1) // 2] if ordered else 0.0


def _cpus(value) -> set[int]:
    """A server's ``cpus`` as the file gives it: a list text ("0-3,8"), a list of ints, or one int."""
    if value is None or value == "":
        return set()
    if isinstance(value, int):
        return {value}
    if isinstance(value, (list, tuple)):
        return {int(c) for c in value}
    return support.parse_cpu_list(str(value))


def _real_share(config: dict, slots: int) -> tuple[int, set[int], set[int]]:
    """S17's rule: (share, the slots' CPUs, the servers' CPUs)."""
    servers: set[int] = set()
    for name in ("shared", "query"):
        servers |= _cpus((config.get("embedding_servers") or {}).get(name, {}).get("cpus"))
    mine = set(os.sched_getaffinity(0))
    pool = (mine - servers) or mine
    return max(1, len(pool) // slots), pool, servers


def _background() -> list[dict[int, float]]:
    """The machine's busy fraction per CPU with nothing of the case running: taken once, before the plain run."""
    time.sleep(SETTLE_S)
    samples, _ = _busy(lambda: time.sleep(BACKGROUND_S))
    return samples


def _busy(run) -> tuple[list[dict[int, float]], float]:
    """Run ``run`` while sampling every 0.2 s each CPU's busy fraction over the interval: ``{cpu: 0.0 to 1.0}``."""
    samples, stop = [], threading.Event()

    def watch():
        last = _cpu_times()
        while not stop.is_set():
            time.sleep(0.2)
            now = _cpu_times()
            sample = {}
            for cpu, (total, idle) in now.items():
                if cpu in last:
                    d_total, d_idle = total - last[cpu][0], idle - last[cpu][1]
                    if d_total > 0:
                        sample[cpu] = (d_total - d_idle) / d_total
            if sample:
                samples.append(sample)
            last = now
    watcher = threading.Thread(target=watch)
    began = time.monotonic()
    watcher.start()
    try:
        run()
    finally:
        stop.set()
        watcher.join()
    return samples, time.monotonic() - began


def _seen(suite: Path) -> list[list[int]]:
    """The CPU sets the planted programs ran on since the last call; the records are then removed."""
    folder = suite / "seen"
    records = sorted(folder.glob("*.json")) if folder.is_dir() else []
    sets = [json.loads(path.read_text()) for path in records]
    for path in records:
        path.unlink()
    return sets


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

    share, pool, servers = _real_share(config, slots)
    mine = len(os.sched_getaffinity(0))

    background = _background()  # once, before the plain run, on a quiet machine (round 7)
    run_without, without_s = _busy(plain)
    _seen(suite)
    time.sleep(SETTLE_S)  # the plain run's tail is not sampled in the slot's run either
    run_with, with_s = _busy(in_slot)
    seen_in_slot = _seen(suite)

    sizes = sorted({len(cpus) for cpus in seen_in_slot})
    slot_set = set().union(*(set(cpus) for cpus in seen_in_slot)) if seen_in_slot else set()
    every_cpu = set().union(*(set(sample) for sample in background + run_without + run_with))
    outside = every_cpu - slot_set

    # Without the slot (unchanged): the whole machine, net of the background's median.
    base = _median(_cores(background))
    without_gross = _p95(_cores(run_without))
    without_net = without_gross - base
    # With the slot (round 8): the slot's own CPUs only; the rest of the machine does not enter it.
    with_slot = _p95(_cores(run_with, slot_set))
    # No program escaped: the CPUs outside the slot's set against their own background.
    outside_run = _median(_cores(run_with, outside))
    outside_base = _median(_cores(background, outside))
    outside_gain = outside_run - outside_base
    whole_with = _p95(_cores(run_with))
    slower = (with_s / without_s - 1) * 100

    print(f"\nS16 evidence: share {share} = {len(pool)} CPUs outside the servers' {len(servers)} of {mine} // "
          f"{slots} slots; the slot's programs ran on {sizes} CPUs ({len(seen_in_slot)} programs), the set "
          f"{support.cpu_list(slot_set) or '-'}; {len(outside)} of the machine's {len(every_cpu)} CPUs outside it")
    print(f"S16 evidence: background, sampled once before the plain run for {BACKGROUND_S:.0f} s per CPU "
          f"({len(background)} samples): whole machine median {base:.2f}, p95 {_p95(_cores(background)):.2f}; on the "
          f"CPUs outside the slot's set median {outside_base:.2f}, p95 {_p95(_cores(background, outside)):.2f}; on the "
          f"slot's set median {_median(_cores(background, slot_set)):.2f}")
    print(f"S16 evidence: without the slot, whole machine busy cores p95 {without_gross:.2f} gross, "
          f"{without_net:.2f} net of the background's median; must exceed share + 1 = {share + 1}")
    print(f"S16 evidence: with the slot, busy cores on the slot's own {len(slot_set)} CPUs p95 {with_slot:.2f} "
          f"(median {_median(_cores(run_with, slot_set)):.2f}); limit share + 1 = {share + 1}")
    print(f"S16 evidence: with the slot, the CPUs outside its set median {outside_run:.2f} "
          f"(p95 {_p95(_cores(run_with, outside)):.2f}) against their background median {outside_base:.2f}: gained "
          f"{outside_gain:+.2f}, limit +1; the whole machine p95 {whole_with:.2f} (for the record, not judged)")
    print(f"S16 evidence: time with {with_s:.1f} s, without {without_s:.1f} s ({slower:+.0f} %)")
    assert seen_in_slot, "no planted program recorded its CPU set inside the slot"
    assert sizes == [share], f"inside the slot the programs ran on {sizes} CPUs, not S17's share {share}"
    assert without_net > share + 1, (
        f"net of the background the planted suite reached {without_net:.2f} without the slot, not above the share "
        f"{share} + 1: no measure")
    assert with_slot >= share / 2, (
        f"the slot's own CPUs reached only {with_slot:.2f} busy cores (p95) of the share {share}: the suite did not "
        f"load its slot, no measure")
    assert with_slot <= share + 1, (
        f"in one slot the busy cores on the slot's own CPUs reached {with_slot:.2f}, above the share {share} + 1")
    assert outside_gain <= 1.0, (
        f"during the slot's run the CPUs outside its set reached a median of {outside_run:.2f} busy cores against "
        f"{outside_base:.2f} in the background ({outside_gain:+.2f}): a program escaped the slot's CPU set")
    assert with_s <= 1.2 * without_s, f"the slot made the suite {slower:.0f} % slower"
