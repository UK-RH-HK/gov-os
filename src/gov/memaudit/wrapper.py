"""The ``gov`` wrapper of a run (Interface items 3 and 6; S2, S4, F3, F4).

``install`` writes ``runs/<A>/gov`` (a Python file, mode 700, whole by a temporary name then a rename): it hands the real
``gov`` (``--gov``) every call. A ``retrieve`` call it runs, keeps its standard output as the next ``kept/<n>.json``
(``GOV_KEEP``), appends the time to ``GOV_MS`` and appends the ``search`` event to the run's ledger **before** it returns
the output (F3). The phase of the call comes in the environment (``GOV_AUDIT_RUN``, ``GOV_AUDIT_PHASE``,
``GOV_AUDIT_ATTEMPT``): the measure that calls the wrapper passes its environment on. Any other call is the real
``gov``'s own (``exec``), and the wrapper reads no server address and signals nothing (F4): the real ``gov`` reaches
its servers by its own variables, which the wrapper leaves as they were.
"""

from __future__ import annotations

import fcntl
import os
import subprocess
import sys
import time
from pathlib import Path

NAME = "gov"


def _source(real_gov: str) -> str:
    src = str(Path(__file__).resolve().parents[2])  # the folder holding the ``gov`` package
    return (f"#!{sys.executable}\n"
            f"import sys\nsys.path.insert(0, {src!r})\n"
            f"from gov.memaudit.wrapper import main\n"
            f"sys.exit(main({str(real_gov)!r}))\n")


def install(run, real_gov) -> Path:
    """The wrapper file for ``real_gov`` in the run folder; written whole, mode 700."""
    run = Path(run)
    final, tmp = run / NAME, run / f".{NAME}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(_source(os.path.expanduser(str(real_gov))))
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, 0o700)
    os.replace(tmp, final)
    return final


def _next_call(keep: Path) -> int:
    """The next kept number of the folder, taken under a lock (the counter is ``.n``)."""
    fd = os.open(keep / ".n.lock", os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            n = int((keep / ".n").read_text().strip() or 0)
        except (OSError, ValueError):
            n = 0
        n += 1
        (keep / ".n").write_text(f"{n}\n")
        return n
    finally:
        os.close(fd)


def main(real_gov: str, argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    run, keep = os.environ.get("GOV_AUDIT_RUN"), os.environ.get("GOV_KEEP")
    if not argv or argv[0] != "retrieve" or not run:
        os.execv(real_gov, [real_gov, *argv])
    from gov.memaudit import events, fault
    started = time.monotonic()
    with open(Path(run) / "gov.err", "ab") as err:  # the real gov's standard error: a file of the run folder (F1)
        done = subprocess.run([real_gov, *argv], stdout=subprocess.PIPE, stderr=err, stdin=subprocess.DEVNULL)
    ms = int((time.monotonic() - started) * 1000)
    out = done.stdout
    call = None
    if keep:
        folder = Path(keep)
        call = _next_call(folder)
        tmp = folder / f".{call:05d}.tmp"
        tmp.write_bytes(out)
        os.replace(tmp, folder / f"{call:05d}.json")
        ms_file = os.environ.get("GOV_MS")
        if ms_file:
            with open(ms_file, "a") as f:
                f.write(f"{ms}\n")
    ok, _ = fault.answered(done.returncode, out.decode("utf-8", "replace"))
    attempt = os.environ.get("GOV_AUDIT_ATTEMPT") or None
    events.search(run, os.environ.get("GOV_AUDIT_PHASE") or "attempt", int(attempt) if attempt else None, call, None,
                  done.returncode, ms, ok)
    sys.stdout.buffer.write(out)
    sys.stdout.buffer.flush()
    return done.returncode
