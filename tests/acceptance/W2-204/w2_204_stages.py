"""The planted runs several cases read: each is built once per session (a file lock in pytest's shared base folder, so
xdist's workers build it once between them), driven as an adopter drives the product, and then only read.

A build never asserts on the product: it records every call (exit code, standard output and error) under a label, and
the cases assert on the record. On a tree without the ticket's commands every call ends at once with a usage error, so
a build costs little there.

The adopter's order (the README's reading of S8): ``fresh`` first, with nothing delivered (it names the two halves and
waits for ``writer-1``); then ``brief`` for each half (the ``brief`` event opens the scan's window, S12); then the
halves are delivered into the sets root (planted as files, as a delivery leaves them); then ``fresh`` again.

- ``right``: both halves clean and accepted; every answer right; a transcript that names ``q07`` is allowed with
  ``--allow-session``. Three ``fresh`` calls: ``plan``, ``delivered`` (no notes yet), ``final``.
- ``misses``: the same, three hidden answers wrong; a transcript that names no id. Calls: ``plan``, ``final``.
- ``void``: the same as ``right``, the transcript that names ``q07`` not allowed. Calls: ``plan``, ``final``.
- ``round2``: the visible half clean and accepted; the hidden half's round 1 has a thin domain, its round 2 is
  repaired and its second notes reject ``q05``. Calls: ``plan``, ``r1``, ``notes1``, ``r2``, ``final``.
- ``stopped-thin`` / ``stopped-heavy``: both halves thin (a domain under its minimum) or heavy (a subsystem over its
  maximum) in round 1 and still so in round 2. Calls: ``plan``, ``r1``, ``r2``, ``again``.
- ``govos``: W2-171's world (Gov OS's shape) twice, one driven by ``python3 -m gov.memaudit`` (``module``), one by
  ``gov memaudit`` (``cli``), with ``GOV_MEMAUDIT_CONFIG`` naming Gov OS's own file (the trial form). Calls:
  ``<entry>:preflight|void|measure|declare|judge|figures|usage``.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import traceback
from pathlib import Path

import w2_204_support as K
from w2_204_support import HALVES, HIDDEN, S171, VISIBLE, W171

LEAK_SESSION, PLAIN_SESSION = "sess-leak", "sess-plain"
WRONG = ((HIDDEN, "q03"), (HIDDEN, "q12"), (HIDDEN, "q22"))
GOV_OS_STEPS = ("preflight", "void", "measure", "declare", "judge", "figures", "usage")


def _start(world: K.World) -> dict:
    calls = {"plan": world.fresh()}
    for audit, _ in HALVES:
        calls[f"brief:{audit}"] = world.brief("writer", audit, world.base / "briefs" / f"{audit}-writer-1")
    return calls


def _deliver(world: K.World, specs, *, notes: bool, audits=(VISIBLE, HIDDEN)) -> None:
    for audit in audits:
        world.write_half(audit, specs)
        if notes:
            world.write_notes(audit)


def _transcripts(world: K.World, *, leak: bool) -> None:
    world.plant_transcript(PLAIN_SESSION, "nothing of the set here: q070 and xq07 are other words")
    if leak:
        world.plant_transcript(LEAK_SESSION, "the session opened q07 and read it")


def _figures(world: K.World, calls: dict) -> None:
    for audit, _ in HALVES:
        calls[f"figures:{audit}"] = world.step("figures", audit)


def _right(folder: Path) -> dict:
    world = K.build(folder / "w")
    before = world.repo_state()
    calls = _start(world)
    _deliver(world, K.clean_specs(), notes=False)
    world.install_plans(control_hits=17)
    calls["delivered"] = world.fresh()
    for audit, _ in HALVES:
        world.write_notes(audit)
    _transcripts(world, leak=True)
    calls["final"] = world.fresh("--allow-session", LEAK_SESSION)
    _figures(world, calls)
    return {"calls": calls, "before": before, "after": world.repo_state()}


def _judged(folder: Path, *, wrong=(), leak: bool) -> dict:
    world = K.build(folder / "w")
    calls = _start(world)
    _deliver(world, K.clean_specs(), notes=True)
    world.install_plans(control_hits=17, wrong=wrong)
    _transcripts(world, leak=leak)
    calls["final"] = world.fresh()
    return {"calls": calls}


def _round2(folder: Path) -> dict:
    world = K.build(folder / "w")
    calls = _start(world)
    _deliver(world, K.clean_specs(), notes=True, audits=(VISIBLE,))
    world.write_half(HIDDEN, K.thin_specs())
    world.install_plans(control_hits=17)
    calls["r1"] = world.fresh()
    first = (world.run_dir(HIDDEN) / "PREFLIGHT.json")
    kept = {"preflight_1": json.loads(first.read_text(encoding="utf-8")) if first.is_file() else None}
    world.write_notes(HIDDEN, 1)
    calls["notes1"] = world.fresh()
    world.write_half(HIDDEN, K.clean_specs())
    world.install_plans(control_hits=17)
    calls["r2"] = world.fresh()
    world.write_notes(HIDDEN, 2, {"q05": ("reject", "R1-WRONG")})
    _transcripts(world, leak=False)
    calls["final"] = world.fresh()
    return {"calls": calls, **kept}


def _stopped(folder: Path, specs) -> dict:
    world = K.build(folder / "w")
    calls = _start(world)
    _deliver(world, specs, notes=True)
    world.install_plans(control_hits=17)
    calls["r1"] = world.fresh()
    for audit, _ in HALVES:
        world.write_half(audit, specs, salt="second round")
        world.write_notes(audit, 2)
    calls["r2"] = world.fresh()
    events = {audit: [e.get("event") for e in world.ledger(audit)] for audit, _ in HALVES}
    calls["again"] = world.fresh()
    return {"calls": calls, "events_at_stop": events}


def gov_os_call(world, entry: str, step: str, flags) -> K.Call:
    """One step on a W2-171 world (Gov OS's shape), with ``GOV_MEMAUDIT_CONFIG`` naming Gov OS's own file."""
    argv = [*K.ENTRIES[entry], step, *map(str, flags)]
    done = subprocess.run(argv, cwd=world.work, capture_output=True, text=True, timeout=900,
                          env=W171.child_env(world.home, world.env({"GOV_MEMAUDIT_CONFIG": str(K.GOV_OS_CONFIG)})))
    return K.Call(done.returncode, done.stdout, done.stderr, argv)


def gov_os_flags(world) -> dict:
    return {"preflight": world.pf_flags(), "void": [*world.common(), "--repo", str(world.repo)],
            "measure": world.measure_flags(), "declare": world.measure_flags(), "judge": world.judge_flags(),
            "figures": world.common(),
            "usage": ["--sets-root", str(world.sets), "--audit", "not-an-audit", "--repo", str(world.repo),
                      "--commit", world.audit_commit]}


def _gov_os(folder: Path) -> dict:
    W171.build(folder / "template")
    calls = {}
    for entry in ("module", "cli"):
        base = folder / entry
        shutil.copytree(folder / "template", base, symlinks=True)
        world = W171.World(base)
        world.write_set(W171.clean_specs())
        world.write_notes(1)
        S171.SCENARIOS["clean"].install(world)
        flags = gov_os_flags(world)
        for step in GOV_OS_STEPS:
            calls[f"{entry}:{step}"] = gov_os_call(world, entry, "preflight" if step == "usage" else step, flags[step])
    return {"calls": calls}


BUILDS = {
    "right": _right,
    "misses": lambda folder: _judged(folder, wrong=WRONG, leak=False),
    "void": lambda folder: _judged(folder, leak=True),
    "round2": _round2,
    "stopped-thin": lambda folder: _stopped(folder, K.thin_specs()),
    "stopped-heavy": lambda folder: _stopped(folder, K.heavy_specs()),
    "govos": _gov_os,
}


class Stage:
    """A built run: its world (read only), each call by its label, and what the build kept beside them."""

    def __init__(self, folder: Path, record: dict):
        self.folder, self.record = folder, record
        self.world = K.World(folder / "w") if (folder / "w" / "world.json").is_file() else None
        self.calls = {label: K.Call(c["code"], c["out"], c["err"], c["argv"]) for label, c in record["calls"].items()}

    def __getitem__(self, label: str) -> K.Call:
        return self.calls[label]

    @property
    def fresh_calls(self) -> list[K.Call]:
        return [call for call in self.calls.values() if "fresh" in call.argv]


def shared(factory, name: str) -> Stage:
    base = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        base = base.parent
    folder = base / f"w2-204-{name}"
    with open(base / f"w2-204-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "record.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"fixture: the planted run {name} could not be built:\n{broken.read_text()}")
        if not done.is_file():
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True)
            try:
                data = BUILDS[name](folder)
            except BaseException:
                broken.write_text(traceback.format_exc(), encoding="utf-8")
                raise
            data["calls"] = {label: call.record() for label, call in data["calls"].items()}
            done.write_text(json.dumps(data), encoding="utf-8")
        return Stage(folder, json.loads(done.read_text(encoding="utf-8")))
