"""Shared assertions of the W2-172 cases."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

import w2_172_world as W
from w2_172_digest import by_word


def assert_ok(run) -> None:
    assert run.code == 0, run


def driver_events(world: W.World) -> list[dict]:
    """The spy's lines of the driver's own process (``python -m gov.memaudit run``), in order."""
    return [e for e in world.spy() if e["argv"][1:4] == ["-m", "gov.memaudit", "run"]]


def classify(args: list[str]) -> str | None:
    """The step a spawned command is: a launch (``writer-1`` ...) or a ``gov.memaudit`` subcommand; else None."""
    if len(args) > 2 and Path(args[1]).name == "launch_stub.py":
        flags = W.flag_map(args[2:])
        return "auditor" if flags.get("--kind") == "auditor" else f"{flags['--kind']}-{flags['--round']}"
    if args[1:3] == ["-m", "gov.memaudit"]:
        return args[3]
    return None


def spawned_steps(world: W.World) -> list[str]:
    """The steps the driver really started, by the file-access spy's ``subprocess.Popen`` lines (not by what it printed)."""
    steps = [classify(e["arg"]) for e in driver_events(world) if e["kind"] == "popen"]
    return [s for s in steps if s]


def brief_hash_at(world: W.World, commit: str, name: str) -> str:
    out = subprocess.run(["git", "-C", str(world.repo), "show", f"{commit}:{W.BRIEF_DIR}/{name}.md"],
                         capture_output=True, check=True).stdout
    return W.sha(out)


def launch_flags(line: str) -> tuple[list[str], dict]:
    tokens = shlex.split(line)
    return tokens, W.flag_map(tokens[2:])


def stop_digest(world: W.World, strict: bool = False) -> dict:
    return by_word(world.digest(), strict)


def refused_without_a_start(world: W.World, run, code: str, *, had_folder: bool = False, starts_before=None) -> None:
    """A refusal (item 3): ``REFUSED <code>`` printed, exit 1, no child, no step, no new start; ``COUNTS.json`` with
    ``refused`` where the audit's folder did not exist."""
    assert run.code == 1, run
    assert f"REFUSED {code}" in run.lines, run
    assert world.stub_calls() == [] and W.step_names(run) == [], (world.stub_calls(), run.out)
    assert world.starts() == (starts_before if starts_before is not None else []), world.starts()
    assert world.gov_calls() == [] and world.claude_calls() == []
    if not had_folder:
        assert world.counts()["refused"] == code, world.counts()


def counts_steps(counts: dict) -> list[dict]:
    return counts["steps"]


def as_json_lines(text: str) -> list[dict]:
    return [json.loads(x) for x in text.splitlines() if x.strip()]
