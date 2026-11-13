"""S18: the product's own parallel work sizes its pools to the CPUs the process may use (its CPU set,
``os.sched_getaffinity``), never to the machine's count: the secret scan's pool (``gov.secrets``) included, so a scan
inside a slot runs at most the slot's share at once [the owner 2026-11-02 ~18:20; incident 2026-11-02 16:20].

How: in a child process confined to two CPUs whose ``os.cpu_count()`` (and ``multiprocessing.cpu_count()``) says 64,
every thread or process pool created is recorded with its width while the pool's owner runs once:
``gov.secrets.indexable`` (its scan switched off and its configuration replaced: the pool is made either way) and
``gov.codeintel.index`` (its root check, filter, path judge, tool and home replaced). Each pool must be at most two
wide. The two modules are the ones in W2-20's paths; ``gov.check.schema``'s fixed pool of 8 is a discovery.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w2_20_support as support

PROBE = r'''
import concurrent.futures, json, multiprocessing, os, sys
from pathlib import Path
cpus = set(sorted(os.sched_getaffinity(0))[:2])
os.sched_setaffinity(0, cpus)
os.cpu_count = lambda: 64
multiprocessing.cpu_count = lambda: 64
widths = []
for cls in (concurrent.futures.ThreadPoolExecutor, concurrent.futures.ProcessPoolExecutor):
    original = cls.__init__
    def init(self, *args, __original=original, **kwargs):
        __original(self, *args, **kwargs)
        widths.append(self._max_workers)
    cls.__init__ = init
which, root = sys.argv[1], Path(sys.argv[2])
if which == "gov.secrets":
    from gov import secrets
    secrets.scan_on = lambda root: False
    secrets.load_config = lambda root: {"path-map.yaml": {"namespaces": {}}}
    secrets.indexable(root, ["a.txt", "b.txt", "c.txt"])
else:
    from gov import codeintel
    codeintel._checked = lambda r: Path(r)
    codeintel.indexable = lambda root, paths: ["a.txt", "b.txt", "c.txt"]
    codeintel.path_holds_secret = lambda root, rel: False
    codeintel._tool = lambda *args, **kwargs: {}
    codeintel.home = lambda root: root / "codeintel-home"
    codeintel.index(root)
print(json.dumps({"cpus": len(cpus), "widths": widths}))
'''


@pytest.mark.parametrize("module", ["gov.secrets", "gov.codeintel"])
def test_s18_a_pool_is_sized_to_the_cpu_set_never_to_the_machines_count(machine, module):
    if len(support.allowed_cpus()) < 2:
        pytest.skip("needs two CPUs to confine the probe to")
    root = machine.repo("pool-root")
    for name in ("a.txt", "b.txt", "c.txt"):
        (root / name).write_text(f"{name}\n")
    probe = machine.scripts / "pool_probe.py"
    probe.write_text(PROBE)
    done = subprocess.run([sys.executable, str(probe), module, str(root)], env=machine.env(), cwd=str(root),
                          capture_output=True, text=True, timeout=support.COMMAND_TIMEOUT_S)
    assert done.returncode == 0, f"the probe of {module} failed:\n{done.stdout}\n{done.stderr}"
    found = json.loads(done.stdout.strip().splitlines()[-1])
    assert found["widths"], f"{module} made no pool in the probe: {found}"
    assert all(width <= found["cpus"] for width in found["widths"]), (
        f"{module} made a pool wider than its CPU set of {found['cpus']} (os.cpu_count() said 64): {found['widths']}")
