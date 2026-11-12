"""Running the standing retrieval measure and the probe search through the wrapper (Interface items 5, 6 and 12; S1, S2,
S4, F3, F4).

The measure is a child process, ``python -m gov.retrieval.measure <set> --part <part> --root <repo> --sets-root <root>
--out <folder> --gov <wrapper>``, with the environment as the fresh 80 ran it (``GOV_ROLE=orchestrator``, ``GOV_STORE``
and ``GOV_TICKET`` unset, the batch 10, bundle 6,000 and stack 24,000 the measure defaults to) and the wrapper's own
variables (``GOV_KEEP``, ``GOV_MS``, ``GOV_AUDIT_*``). Its standard output is the folder's ``measure.txt`` and its standard
error ``measure.err``: nothing a child says is printed (F1). Every other variable, those that name the shared servers
included, goes on unchanged; this module reads none and starts, stops or signals nothing (F4).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from gov.memaudit import fault

PROBE = "what decides a close"


def environment(run=None, phase=None, attempt=None, folder=None) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in ("GOV_STORE", "GOV_TICKET", "GOV_KEEP", "GOV_MS")}
    env["GOV_ROLE"] = "orchestrator"
    if run is not None:
        env.update(GOV_AUDIT_RUN=str(run), GOV_AUDIT_PHASE=str(phase), GOV_AUDIT_ATTEMPT="" if attempt is None
                   else str(attempt))
    if folder is not None:
        env.update(GOV_KEEP=str(Path(folder) / "kept"), GOV_MS=str(Path(folder) / "ms"))
    return env


def start(folder) -> Path:
    """A new run folder with its ``kept/`` and ``ms``; one that exists is never reused (``FileExistsError``)."""
    folder = Path(folder)
    os.mkdir(folder, 0o700)
    os.mkdir(folder / "kept", 0o700)
    (folder / "kept" / ".n").write_text("0\n")
    (folder / "ms").write_text("")
    return folder


def measure(set_name: str, part: str, *, repo, root, folder, wrapper, run, phase: str, attempt) -> int:
    """The measure's exit code; its output is in ``folder`` (``measure.txt``, ``measure.err``, ``kept/``, ``ms``)."""
    folder = Path(folder)
    cmd = [sys.executable, "-m", "gov.retrieval.measure", set_name, "--part", part, "--root", str(repo),
           "--sets-root", str(root), "--out", str(folder), "--gov", str(wrapper)]
    with open(folder / ".measure.txt.tmp", "wb") as out, open(folder / ".measure.err.tmp", "wb") as err:
        rc = subprocess.run(cmd, stdout=out, stderr=err, stdin=subprocess.DEVNULL, cwd=folder,
                            env=environment(run, phase, attempt, folder), check=False).returncode
    for name in ("measure.txt", "measure.err"):  # whole or absent: a run that died leaves no half output
        os.replace(folder / f".{name}.tmp", folder / name)
    return rc


def rescore(set_name: str, part: str, *, repo, root, kept) -> tuple[int, str]:
    """``--kept``: the measure over a run's kept outputs, no retriever; nothing is written (its standard error is dropped)."""
    cmd = [sys.executable, "-m", "gov.retrieval.measure", set_name, "--part", part, "--root", str(repo),
           "--sets-root", str(root), "--kept", str(kept)]
    done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                          cwd=str(root), env=environment(), check=False)
    return done.returncode, done.stdout.decode("utf-8", "replace")


def probe(run, wrapper, repo) -> tuple[bool, str | None]:
    """The ready check: one search, ``gov retrieve "what decides a close" --json`` on ``repo`` through the wrapper,
    answered as declared. ``(ok, why)``; ``why`` is None, ``exit``, ``no bundle``, ``route``, ``reranker`` or ``pool``."""
    with open(Path(run) / "probe.err", "ab") as err:
        done = subprocess.run([str(wrapper), "retrieve", PROBE, "--json"], stdout=subprocess.PIPE, stderr=err,
                              stdin=subprocess.DEVNULL, cwd=str(repo),
                              env=environment(run, "ready", None, None), check=False)
    return fault.answered(done.returncode, done.stdout.decode("utf-8", "replace"))
