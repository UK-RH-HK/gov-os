"""Helpers of the fresh 80's writer loop fix (FM-1 to FM-4): a writer's ``out/`` folder planted from specs, the
planted faults (one per pre-flight code that can be planted with the World), the planted pairs ``fresh`` is run on,
and the readers of the printed lines. Everything is driven through the CLI; nothing of the product is imported."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

import w2_204_support as K
from w2_204_support import HIDDEN, VISIBLE

# -- the writer's out/ folder ------------------------------------------------------------------------------------------


def by_area(specs: list[dict]) -> dict:
    counts = {name: 0 for name in [*K.DOMAIN_NAMES, "none"]}
    for spec in specs:
        path = K.first_path(spec)
        counts[next((name for name, patterns in K.DOMAINS
                     if any(path == p or (p.endswith("/**") and path.startswith(p[:-2])) for p in patterns)), "none")] += 1
    return counts


def writer_out(world: K.World, folder: Path, specs: list[dict], *, salt=None) -> Path:
    """``out/`` with ``set/q*.yaml`` and a ``result.json`` that is well formed by names and counts."""
    out = Path(folder) / "out"
    world.write_half(HIDDEN, specs, folder=out / "set", salt=salt)
    n = len(specs)
    result = {"questions": n, "by_kind": {"fact": n - 12, "procedure": 4, "decision": 6, "location": 1, "negative": 1},
              "by_area": by_area(specs)}
    (out / "result.json").write_text(json.dumps(result), encoding="utf-8")
    return out


def landed(world: K.World) -> dict:
    hidden = world.hidden(HIDDEN)
    return {p.name: p.read_bytes() for p in hidden.iterdir()} if hidden.is_dir() else {}


def briefed(world: K.World, name: str = "writer-1") -> None:
    """The half's ``brief`` event and ``selection.json``, as a real run has them before the writer delivers."""
    run = world.brief("writer", HIDDEN, world.base / "briefs" / name)
    assert run.code == 0, ("the setup's writer brief failed", run)


# -- the planted faults: (mutator of the clean 40, the printed line that must be there) --------------------------------

def _spec(specs, qid):
    return next(s for s in specs if s["id"] == qid)


def f_form(world, specs):
    _spec(specs, "q07")["extra"] = {"bogus": 1}


def f_source(world, specs):
    _spec(specs, "q21")["sources"] = [{"path": "app/engine/nowhere.py"}]


def f_evalns(world, specs):
    _spec(specs, "q22")["sources"] = [{"path": "archive/old.md"}]


def f_drawn(world, specs):
    _spec(specs, "q08")["drawn"] = "changed"   # the brief had no --since: nothing is in ``changed``


def f_commit(world, specs):
    _spec(specs, "q09")["extra"] = {"commit": world.later_commit}


def f_quota(world, specs):
    _spec(specs, "q08")["category"] = "berth-spec"   # harbour-task 3, berth-spec 5 against 4 and 4


def f_idexists(world, specs):
    _spec(specs, "q40")["extra"] = {
        "question": f"What does decision DEC-101 decide for the {K.qword('h', 40)} mooring?"}   # DEC-101 exists


def f_count(world, specs):
    del specs[30:]


def f_duppool(world, specs):
    """The pool (a second set in the sets root) holds a question with q10's gold sources."""
    pool = world.sets / "fixtures" / "evaluation" / "memory-pool" / "hidden"
    pool.mkdir(parents=True, exist_ok=True)
    (pool / "p01.yaml").write_text(yaml.safe_dump({"id": "p01", "sources": _spec(specs, "q10")["sources"]}),
                                   encoding="utf-8")


def f_spread(world, specs):
    specs[:] = K.thin_specs()   # pilot-reports 3, under its minimum of 4


def unfault(world, fault):
    """Take back what a fault planted outside the set itself."""
    pool = world.sets / "fixtures" / "evaluation" / "memory-pool" / "hidden" / "p01.yaml"
    if fault == "duppool" and pool.exists():
        pool.unlink()


FAULTS = {
    "duppool": (f_duppool, r"PF-DUPPOOL refused 1 q10"),
    "spread": (f_spread, r"PF-SPREAD refused [0-9]+( .*)?"),
    "form": (f_form, r"PF-FORM refused 1 q07"),
    "source": (f_source, r"PF-SOURCE refused 1 q21"),
    "evalns": (f_evalns, r"PF-EVALNS refused 1 q22"),
    "drawn": (f_drawn, r"PF-DRAWN refused 1 q08"),
    "commit": (f_commit, r"PF-COMMIT refused 1 q09"),
    "idexists": (f_idexists, r"PF-IDEXISTS refused 1 q40"),
    "quota": (f_quota, r"PF-QUOTA refused [0-9]+( .*)?"),
    "count": (f_count, r"PF-COUNT refused [0-9]+( .*)?"),
}
SET_LEVEL = ("PF-COUNT", "PF-QUOTA", "PF-SPREAD")
PF_LINE = re.compile(r"PF-[A-Z]+ refused [0-9]+(?: [A-Za-z0-9_.-]+)*")
PF_ID_LINE = re.compile(r"PF-[A-Z]+ refused [0-9]+(?: q[0-9]{2})*")
PF_SET_LINE = re.compile(r"PF-(?:COUNT|QUOTA|SPREAD) refused [0-9]+(?: [A-Za-z0-9_.-]+)*")


def faulty(world: K.World, fault: str) -> list[dict]:
    specs = K.clean_specs()
    FAULTS[fault][0](world, specs)
    return specs


# -- the writer's session folder and its Stop hook -----------------------------------------------------------------------
HOOK_STDIN = json.dumps({"stop_hook_active": False})


def session(world: K.World, name: str = "writer-1", *, kind: str = "writer", round_no: int = 1) -> Path:
    """The brief's folder, as the CTO starts the session in it."""
    out = world.base / "briefs" / name
    run = world.brief(kind, HIDDEN, out, round_no=round_no)
    assert run.code == 0, ("the setup's brief failed", run)
    return out


def hook_command(folder: Path) -> str:
    path = Path(folder) / ".claude" / "settings.json"
    assert path.is_file(), f"no {path}"
    doc = json.loads(path.read_text(encoding="utf-8"))
    stops = doc["hooks"]["Stop"]
    assert len(stops) == 1 and len(stops[0]["hooks"]) == 1, doc
    hook = stops[0]["hooks"][0]
    assert hook["type"] == "command" and isinstance(hook["command"], str) and hook["command"].strip(), doc
    assert "writer-check" in hook["command"], doc
    return hook["command"]


def run_hook(world: K.World, folder: Path) -> K.Call:
    """The hook's command, as Claude Code runs it: a shell, the session folder as cwd, the hook JSON on stdin."""
    shim = world.base / "shim"
    if not shim.exists():
        shim.mkdir()
        (shim / "gov").write_text(f'#!/bin/sh\nexec {sys.executable} -m gov.cli.main "$@"\n', encoding="utf-8")
        (shim / "gov").chmod(0o755)
    env = K.W171.child_env(world.home, {"W171_STATE": str(world.state)})
    env.pop("MEMAUDIT_CONFIG", None)
    env["PATH"] = f"{shim}{os.pathsep}{env.get('PATH', '')}"
    done = subprocess.run(hook_command(folder), shell=True, cwd=folder, input=HOOK_STDIN, capture_output=True,
                          text=True, timeout=600, env=env)
    return K.Call(done.returncode, done.stdout, done.stderr, [hook_command(folder)])


def put_set(world: K.World, folder: Path, specs: list[dict], *, salt=None) -> None:
    world.write_half(HIDDEN, specs, folder=Path(folder) / "out" / "set", salt=salt)


def record(world: K.World) -> dict:
    return json.loads((world.run_dir(HIDDEN) / "WRITER-CHECK.json").read_text(encoding="utf-8"))


def block_of(call: K.Call) -> dict:
    """The one JSON line a refusal prints: ``{"decision": "block", "reason": ...}``."""
    assert call.code == 0, call
    assert len(call.out.splitlines()) == 1, ("one line of JSON", call)
    doc = json.loads(call.out)
    assert set(doc) == {"decision", "reason"} and doc["decision"] == "block" and isinstance(doc["reason"], str), doc
    return doc


def reason_lines(call: K.Call) -> list[str]:
    return [x.strip() for x in block_of(call)["reason"].splitlines() if x.strip()]


def preflight_refused_lines(world: K.World) -> list[str]:
    """Pre-flight's own refusal lines for what is now in ``hidden/``."""
    run = world.step("preflight", HIDDEN)
    return [x for x in run.lines if " refused " in x]


# -- the brief's section ------------------------------------------------------------------------------------------------
SECTION = "## Pre-flight 1 refusals"


def section_of(text: str) -> str | None:
    """The text of the refusals section (heading to the next ``## `` heading), or None."""
    at = text.find(SECTION)
    if at < 0:
        return None
    rest = text[at + len(SECTION):]
    end = rest.find("\n## ")
    return rest if end < 0 else rest[:end]


def section_lines(section: str) -> list[str]:
    """Each non-empty line with its bullet and backticks removed."""
    out = []
    for line in section.splitlines():
        line = re.sub(r"^[\s>*+-]+", "", line).replace("`", "").strip()
        if line:
            out.append(line)
    return out


# -- the pairs ``fresh`` is run on ---------------------------------------------------------------------------------------
REJECTS = {qid: ("reject", "R1-WRONG") for qid in ("q07", "q12", "q20", "q30", "q35")}


def void_pair(base: Path, kind: str) -> SimpleNamespace:
    """The visible half clean and ready, the hidden half's last notes void it (``count``: 5 of 40 rejected in round 2;
    ``domain``: a domain thin in both rounds). The visible half is delivered only for the last call, so that no
    implementation can have measured it before the hidden half's notes are there."""
    world = K.build(base / "w")
    calls = {"plan": world.fresh()}
    if kind == "count":
        world.write_half(HIDDEN, K.clean_specs())
        world.write_notes(HIDDEN, 1, REJECTS)
        specs2, verdicts2 = K.clean_specs(), REJECTS
    else:
        world.write_half(HIDDEN, K.thin_specs())
        world.write_notes(HIDDEN, 1)
        specs2, verdicts2 = K.thin_specs(), None
    calls["r1"] = world.fresh()
    world.write_half(HIDDEN, specs2, salt="second round")
    world.write_notes(HIDDEN, 2, verdicts2)
    world.write_half(VISIBLE, K.clean_specs())
    world.write_notes(VISIBLE, 1)
    world.install_plans(control_hits=17)
    calls["final"] = world.fresh()
    return SimpleNamespace(world=world, calls=calls)


def prepared_pair(base: Path, *, used: bool, env=None, extra=()) -> SimpleNamespace:
    """Both halves delivered, pre-flighted, noted and voided by the step commands, then ``fresh``: it goes on to the
    visible half's measure, where a ``USED`` marker (``used``) or a busy gate (``extra``) stops it."""
    world = K.build(base / "w")
    calls = {"plan": world.fresh()}
    world.prepare(VISIBLE)
    world.prepare(HIDDEN)
    world.install_plans(control_hits=17)
    if used:
        (world.run_dir(VISIBLE) / "USED").write_text("used\n", encoding="utf-8")
    calls["final"] = world.fresh(*extra, env=env)
    return SimpleNamespace(world=world, calls=calls)


# -- the printed lines ---------------------------------------------------------------------------------------------------
STOPPED = re.compile(r"STOPPED (\S+) (\S+)(?: .*)?")
CAUSE = re.compile(r"CAUSE (\S+) (\S+) ([^:\s]+(?: [^:\s]+)*): (\S.*)")


def stops(call: K.Call) -> list[tuple[int, str, str]]:
    return [(i, m[1], m[2]) for i, m in ((i, STOPPED.fullmatch(x)) for i, x in enumerate(call.lines)) if m]


def cause_before(call: K.Call, at: int):
    """The ``CAUSE`` match of the line just before line ``at``, or None."""
    return CAUSE.fullmatch(call.lines[at - 1]) if at > 0 else None
