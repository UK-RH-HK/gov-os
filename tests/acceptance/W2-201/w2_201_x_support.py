"""Support code for W2-201's fix lines X1 to X3 (DEC-1219 (5)): ``gov launch <role> <ticket> --fix "<line>"`` and
``gov launch <role> --chore "<line>"`` (standard library and PyYAML only).

It stands on ``w2_201_support`` (imported as ``k``) and, through it, on W2-184's and W2-60a's support modules: the
sandbox HOME, the open resource gate, the fixture project (W2-184's: a role file with a fixture table per worker role,
a ``criticality.yaml`` with C3 ``src/critical``, C2 ``src/product``, C1 ``docs``), the stand-in CLI that records its
arguments, process environment and ``--settings``, and the launch record folder. Nothing of those modules is changed.

What is added here: a launch from any words (the ticket is optional now, and the new options are written before
``--``), with more in ``gov launch``'s own environment; a ticket of any status; the lead's plan (a ready list,
committed); ``gov pause`` and a shut gate; the readers of a usage error and of the run folders.
"""

from __future__ import annotations

import time
from pathlib import Path

import w2_201_support as k

s = k.s
b = s.b

ENGINEER, TEST_DESIGNER, PRODUCT_SPEC = k.ENGINEER, k.TEST_DESIGNER, k.PRODUCT_SPEC
OPUS, SONNET = k.OPUS, k.SONNET
LEAD_ROLES = ("orchestrator", "lead")
LEAD_GOV_ROLE = "orchestrator"
READY_REL = "governance/project/orchestration/ready.txt"
RUNS_NAME = "gov-os-runs"

FIX_LINE = "the count is off by one when the list is empty"
CHORE_LINE = "tidy the release notes' headings (tests unchanged and green)"
# A caller's own ticket in gov launch's environment (a lead launching a worker has one): it must not reach a chore.
CALLER_TICKET = "DAEO-cllr"

KIND_KEYS = ("kind", "kind_line")
LAUNCH_KIND, LAUNCH_LINE = "GOV_LAUNCH_KIND", "GOV_LAUNCH_LINE"

# W2-184's fixture role files: the default line of every worker role is (Sonnet, medium); the engineer's table gives
# C3 (Opus, high) and C2 (Sonnet, high). So a chore's effort (medium) is told from any class's (high).
ROLE_DEFAULT = s.DEFAULT
ENGINEER_TABLE = s.TABLES[ENGINEER]


def ticket(project, role, cls, status="closed", *, tk, profile="STANDARD"):
    """A ticket (not committed) of ``status`` whose allowed paths put it in ``cls`` by the fixture rubric; the
    engineer owns it unless ``role`` is one the launcher ties to its own ticket (W2-184's ``ticket``)."""
    s.ticket(project, role, cls, profile, tk=tk)
    path = Path(project) / ".tickets" / f"{tk}.md"
    text = path.read_text(encoding="utf-8")
    assert "status: in_progress\n" in text, f"fixture: the planted ticket {tk} has no status line to change"
    path.write_text(text.replace("status: in_progress\n", f"status: {status}\n", 1), encoding="utf-8")
    return tk


def commit(project, message):
    b.git(project, "add", "-A")
    b.git(project, "commit", "-q", "-m", message)


def launch(sandbox, cli, *words, extra_env=None, cwd=None):
    """``gov launch <words>`` through the console script, in the project (or ``cwd``), with ``extra_env`` added to
    the environment W2-60a builds. ``words`` are written as given: the role, the ticket when there is one, the
    options, then ``--`` and the CLI's arguments where the case has them. Returns W2-60a's ``Launch``."""
    root = Path(cwd) if cwd is not None else Path(sandbox.project)
    records = Path(sandbox.records)
    before_calls, before = len(b.calls(cli)), b._listing(records)
    started = time.time()
    run = b.run_gov(sandbox, root, "launch", *words, extra_env=extra_env)
    return b.Launch(run, tuple(b.calls(cli)[before_calls:]), records, before, b._listing(records), started,
                    time.time(), ())


def usage_error(result):
    """X1's usage error: exit 2, nothing started, no launch record; and it is the new options' rule that refused,
    not argparse finding an option ``gov launch`` does not know (``unrecognized arguments``)."""
    said = b.said(result)
    assert result.run.returncode == 2, f"gov launch did not end with the usage code 2\n{result.describe()}"
    assert not result.calls, f"a usage error started the CLI\n{result.describe()}"
    assert not result.new_records, f"a usage error left a launch record: {sorted(result.new_records)}"
    assert "unrecognized arguments" not in said, (
        f"gov launch does not know --fix or --chore (argparse's 'unrecognized arguments'), so this is not the "
        f"usage rule of X1\n{result.describe()}")


def launched(result):
    b.assert_launched(result)
    return result


def line_values(result):
    return {"--model": result.values("--model"), "--effort": result.values("--effort")}


def assert_line(result, model, effort):
    got = line_values(result)
    assert got == {"--model": [model], "--effort": [effort]}, (
        f"the stand-in did not receive --model {model} and --effort {effort} once each: {got}\n{result.args}")


def record_of(result, *keys):
    record = result.record()
    return {key: record.get(key, s.MISSING) for key in keys}


def env_pair(result):
    """The ``--settings`` env block and the CLI process's environment the stand-in recorded."""
    return result.env_block(), result.session()["env"]


def lead_env_pair(result):
    settings = result.settings()
    block = settings.get("env")
    assert isinstance(block, dict), f"the lead's --settings has no env block: {settings}"
    return block, result.session()["env"]


def runs_listing(sandbox):
    """The folders under ``<HOME>/gov-os-runs`` (a session's own run folder is made there)."""
    root = Path(sandbox.home) / RUNS_NAME
    return sorted(p.name for p in root.iterdir()) if root.is_dir() else []


# --------------------------------------------------------------------------
# What stops any launch: gov pause and the resource gate
# --------------------------------------------------------------------------

GIB = 1024 ** 3


def pause(sandbox):
    """``gov pause`` in the fixture project, as the owner (no ``GOV_ROLE``)."""
    done = b.run_gov(sandbox, sandbox.project, "pause")
    assert done.returncode == 0, f"fixture: gov pause did not pause the fixture project\n{done.describe()}"
    flag = Path(sandbox.project) / ".gov-runtime" / "freeze"
    assert flag.exists(), f"fixture: gov pause left no freeze flag at {flag}"
    return done


def shut_gate_env(sandbox):
    """The gate's memory reading at 1 GiB available, under the planted floor (3 GiB): the gate is shut."""
    path = Path(sandbox.elsewhere) / "shut-gate" / "meminfo"
    b.write(path, f"MemTotal: {80 * GIB // 1024} kB\nMemAvailable: {1 * GIB // 1024} kB\n")
    return {"GOV_RESOURCES_MEMINFO": str(path)}


def stop(sandbox, how):
    """Plant one stop (``"pause"`` or ``"gate"``); returns the extra environment and the words a refusal names."""
    if how == "pause":
        pause(sandbox)
        return None, ("paused",)
    return shut_gate_env(sandbox), ("memory",)


def stopped(result, words):
    """A refusal by the pause or the gate: non-zero, nothing started, no record, LAUNCH_REFUSED and its words."""
    b.assert_refused(result, "LAUNCH_REFUSED", *words)
