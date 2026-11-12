"""The GPU backstop (W2-157; DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030, DEC-1073): ``gov resources --backstop <pgid>...``.

It watches the named process groups of a GPU job and pauses every live one with SIGSTOP at once on a trip, then writes
its log line and one inbox item and ends. A pause only: no kill, no resume (the owner or the CTO does that), no server
touched. Each poll (every ``gpu_backstop_every_s``) checks, in this order, the first reason found tripping it:

1. GPU memory used above ``gpu_backstop_limit_mib`` (S1; L3);
2. GPU memory used within 64 MiB of the card's total, a spill into shared memory (S2; L3);
3. a model of a configured embedder whose ``size_vram`` is below its ``size``, from ``GET /api/ps`` (S3; L4);
4. a line ``offloaded N/M layers to GPU`` with N below M, in an embedder's log, written since the watch started (S3; L4).

The limit, the period and the embedders come from the gate's one file and nowhere else (``config.backstop_values``, F3):
no option and no environment variable sets them. Only the groups named are touched, by ``os.killpg`` with their id,
never a pid, a name or a pattern (S4, F1; L5). When the backstop's own group (``os.getpgrp()``) is named, it is paused
last, after the other groups, the TRIP line and the inbox item (L5b), so the SIGSTOP that freezes ``gov`` freezes it
only when everything else is done; ``kill -CONT`` to that group resumes it and the command ends. It reads only ``nvidia-smi``'s answer, the ``/api/ps`` answers and the
embedder logs, and writes only ``$HOME/.gov-os/machine/gpu-backstop.log`` and, on a trip, the one inbox item under
``<root>/.gov-runtime/dispatch/inbox/`` (S5; L6, L7, L9). The result is L8's.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from gov.cli.errors import GovError
from gov.resources import config

LOG = "gpu-backstop.log"
SPILL_MARGIN_MIB = 64
SMI_QUERY = ["--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"]
SMI_TIMEOUT_S = 20
PS_TIMEOUT_S = 3
READING = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*$")
OFFLOAD = re.compile(r"offloaded (\d+)/(\d+) layers to GPU")


def _stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _names(groups) -> str:
    return " ".join(str(g) for g in groups) or "none"


def _live(group: int) -> bool:
    """Signal 0 to the group: it exists (a group we may not signal exists too); a number beyond what a process group
    id can be (``os.killpg`` raises OverflowError) names no group, so it counts as ended (L5)."""
    try:
        os.killpg(group, 0)
    except (ProcessLookupError, OverflowError):
        return False
    except PermissionError:
        return True
    return True


def read_gpu(env: dict) -> tuple[tuple[int, int] | None, str | None]:
    """``((used, total), None)`` from the first line of nvidia-smi's answer, or ``(None, why)``."""
    program = shutil.which("nvidia-smi", path=env.get("PATH") or os.defpath)
    if not program:
        return None, "no nvidia-smi on PATH"
    try:
        done = subprocess.run([program, *SMI_QUERY], capture_output=True, text=True, timeout=SMI_TIMEOUT_S, env=env)
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"nvidia-smi cannot be run: {error}"
    if done.returncode != 0:
        said = " ".join((done.stderr + " " + done.stdout).split())[:120]
        return None, f"nvidia-smi exit {done.returncode}: {said}"
    first = (done.stdout.splitlines() or [""])[0]
    found = READING.match(first)
    if not found:
        return None, f"an answer not of the form '<used>, <total>': {first[:80]!r}"
    return (int(found.group(1)), int(found.group(2))), None


def _partial_models(port: int) -> str | None:
    """The reason when a model of the embedder at ``port`` is not wholly on the GPU; no answer is no trip."""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(f"http://127.0.0.1:{port}/api/ps", timeout=PS_TIMEOUT_S) as answer:
            models = json.loads(answer.read().decode("utf-8"))["models"]
        for model in models:
            size, vram = model["size"], model["size_vram"]
            if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (size, vram)) and vram < size:
                return f"embedder on :{port}: model {model['name']} not wholly on the GPU (size_vram/size {vram}/{size})"
    except Exception:  # noqa: BLE001 - an answer that is missing or malformed is no trip
        return None
    return None


def _log_start(file: str) -> int:
    try:
        return os.path.getsize(file)
    except OSError:
        return 0


def _partial_offload(file: str, offsets: dict) -> str | None:
    """Read what was appended to ``file`` since the last poll (whole lines only); a partial offload is the reason."""
    try:
        size = os.path.getsize(file)
        if size < offsets[file]:  # truncated or rotated: what is there now was written since the start
            offsets[file] = 0
        with open(file, "rb") as handle:
            handle.seek(offsets[file])
            chunk = handle.read(size - offsets[file])
    except OSError:
        return None
    whole = chunk[:chunk.rfind(b"\n") + 1]
    offsets[file] += len(whole)
    for found in OFFLOAD.finditer(whole.decode("utf-8", "replace")):
        if int(found.group(1)) < int(found.group(2)):
            return f"embedder log {file}: {found.group(0)}"
    return None


def _inbox_item(root: Path, reason: str, paused: list, skipped: list, own: int | None = None) -> str:
    folder = Path(root) / ".gov-runtime" / "dispatch" / "inbox"
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"gpu-backstop-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    target, number = folder / f"{stem}.txt", 1
    while target.exists():  # an item is never overwritten
        number += 1
        target = folder / f"{stem}-{number}.txt"
    lines = ["log: gpu-backstop.log", "W2: none", f"status: GPU backstop tripped: {reason}", f"paused: {_names(paused)}",
             f"skipped (already ended): {_names(skipped)}"]
    lines += [f"resume: kill -CONT -- -{g}" for g in paused]
    lines += [f"stop: kill -TERM -- -{g} && kill -CONT -- -{g}" for g in paused]
    if own is not None:
        lines.append(f"note: the backstop's own group {own} is paused last; resuming it resumes the backstop, "
                     "which then ends")
    temporary = folder / f".{target.name}.tmp"
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    return str(target)


def watch(groups: list[int], root: Path, env: dict | None = None) -> dict:
    """Watch the named process groups until a trip or until every one has ended; the result of L8."""
    env = dict(os.environ if env is None else env)
    values, faults = config.backstop_values(env)
    if faults:
        raise GovError("RESOURCE_CONFIG_INVALID", "the GPU backstop's configuration is invalid: "
                       + "; ".join(f["why"] for f in faults), {"faults": faults})
    named = list(dict.fromkeys(groups))
    if not named or any(isinstance(g, bool) or not isinstance(g, int) or g <= 1 for g in named):
        raise GovError("RESOURCE_ARGUMENTS_INVALID", f"not process group ids above 1: {groups!r}")
    limit, every, embedders = values["limit_mib"], values["every_s"], values["embedders"]
    log = config.machine_dir(env) / LOG
    log.parent.mkdir(parents=True, exist_ok=True)

    def note(text: str) -> None:
        with log.open("a", encoding="utf-8") as handle:
            handle.write(f"{_stamp()} {text}\n")

    skipped = [g for g in named if not _live(g)]
    offsets = {e["log"]: _log_start(e["log"]) for e in embedders}
    own = os.getpgrp()
    tail = f"; own group {own} named: paused last" if own in named else ""
    note(f"start: limit {limit} MiB; every {every} s; groups {_names(named)}; skipped (ended) {_names(skipped)}; "
         f"embedders {_names(e['port'] for e in embedders)}{tail}")
    result = {"tripped": False, "reason": None, "reading": None, "paused": [], "skipped": skipped, "log": str(log),
              "inbox_item": None}
    while True:
        if not any(_live(g) for g in named):
            note(f"end: every watched group has ended ({_names(named)})")
            return result
        reading, why = read_gpu(env)
        if why:
            note(f"no GPU reading: {why}")
        reason = None
        if reading:
            used, total = reading
            if used > limit:
                reason = f"GPU memory {used} MiB > limit {limit} MiB"
            elif used >= total - SPILL_MARGIN_MIB:
                reason = f"GPU memory {used} of {total} MiB: at the card's total (a spill into shared memory)"
        for embedder in embedders if reason is None else ():
            reason = _partial_models(embedder["port"])
            if reason:
                break
        for embedder in embedders if reason is None else ():
            reason = _partial_offload(embedder["log"], offsets)
            if reason:
                break
        if reason:
            paused = []
            for g in named:
                if g == own or not _live(g):  # the own group is paused last (L5b)
                    continue
                try:
                    os.killpg(g, signal.SIGSTOP)
                except (ProcessLookupError, PermissionError, OverflowError):
                    continue
                paused.append(g)
            if own in named:
                paused.append(own)  # it is paused after the line and the item are written, below
            seen = f"{reading[0]}/{reading[1]} MiB" if reading else "none"
            note(f"TRIP: {reason}; reading {seen}; paused groups {_names(paused)}")
            result.update(tripped=True, reason=reason, paused=paused,
                          reading={"used_mib": reading[0], "total_mib": reading[1]} if reading else None,
                          inbox_item=_inbox_item(root, reason, paused, skipped, own if own in named else None))
            if own in named:  # stops gov too: the owner's `kill -CONT -- -<own>` resumes it, and it returns the result
                try:
                    os.killpg(own, signal.SIGSTOP)
                except (ProcessLookupError, PermissionError, OverflowError):
                    paused.remove(own)
            return result
        time.sleep(every)
