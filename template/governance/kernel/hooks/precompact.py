#!/usr/bin/env python3
"""
PreCompact hook (W1-49 state block + W1-29 checkpoint record, CAP-37).

Never blocks a compaction (DEC-264). Two actions, in order:

1. W1-29 checkpoint record: calls gov.checkpoint.record.write with
   trigger "compaction" for any role that has a GOV_TICKET. If the
   write fails, the error is reported in a systemMessage.

2. W1-49 state block: appends one generated state block to the
   checkpoint file. Acts only when GOV_ROLE is exactly "orchestrator"
   (DEC-259). The written part is never changed; the modification
   time is set back so the file's time stays the time of its written
   part. A block is the hook's own only when its lines match the
   digest on its ``generated:`` line.

Always exits 0.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

BEGIN = b"<!-- GENERATED STATE BLOCK BEGIN -->"
END = b"<!-- GENERATED STATE BLOCK END -->"
STAMP = "%Y-%m-%dT%H:%M:%SZ"


def checkpoint_rel(project_root: str) -> str:
    """The lead's checkpoint in a linked worktree (.git is a file
    there), the orchestrator's in the main tree."""
    linked = os.path.isfile(os.path.join(project_root, ".git"))
    return f".gov-runtime/scratch/{'lead' if linked else 'orchestrator'}/CHECKPOINT.md"


def digest(stamp: bytes, rest: bytes) -> bytes:
    return hashlib.sha256(stamp + b"\n" + rest).hexdigest().encode()


def split(data: bytes) -> tuple[bytes, bytes]:
    """(written part, generated block). There is a block only when the
    last line that is not empty is exactly the end marker, the last
    line that is exactly the begin marker is followed by the
    ``generated:`` line, and the digest on that line is that of the
    lines after it. Anything else is written text."""
    lines = data.splitlines(keepends=True)
    end = len(lines)
    while end and not lines[end - 1].strip():
        end -= 1
    if end and lines[end - 1] == END + b"\n":
        for index in range(end - 2, -1, -1):
            if lines[index] == BEGIN + b"\n":
                stamp = re.fullmatch(rb"generated: (\S+) (\S+)\n", lines[index + 1])
                if stamp and digest(stamp.group(1), b"".join(lines[index + 2:end])) == stamp.group(2):
                    return b"".join(lines[:index]), b"".join(lines[index:])
                break
    return data, b""


def output(project_root: str, *command: str) -> str:
    """What follows a label: the command's lines, indented, or why
    there are none."""
    try:
        done = subprocess.run(command, cwd=project_root, capture_output=True, encoding="utf-8",
                              errors="replace", timeout=5, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return f" unavailable ({type(exc).__name__})"
    if done.returncode:
        return f" unavailable (exit code {done.returncode})"
    return "".join(f"\n  {line}" for line in done.stdout.splitlines())


def state_block(project_root: str) -> bytes:
    stamp = time.strftime(STAMP, time.gmtime()).encode()
    rest = (
        f"git head: {output(project_root, 'git', 'rev-parse', 'HEAD').strip()}\n"
        f"tickets in progress (`tk ls --status=in_progress`):{output(project_root, 'tk', 'ls', '--status=in_progress')}\n"
        f"worktrees (`git worktree list`):{output(project_root, 'git', 'worktree', 'list')}\n"
        "pending owner decisions: not known to the hook; see the written part of this checkpoint\n"
    ).encode("utf-8") + END + b"\n"
    return BEGIN + b"\ngenerated: " + stamp + b" " + digest(stamp, rest) + b"\n" + rest


def put(f, offset: int, data: bytes) -> None:
    """Writes data at offset and ends the file there."""
    f.seek(offset)
    if f.write(data) != len(data):
        raise OSError(28, "No space left on device")
    f.truncate()


def main() -> None:
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    ticket = os.environ.get("GOV_TICKET", "")
    messages: list[str] = []

    if ticket:
        try:
            src_dir = os.path.join(project_root, "src")
            if os.path.isdir(src_dir) and src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            from gov.checkpoint.record import write as _rec_write
            _rec_write(Path(project_root), ticket, "compaction", "Resume after compaction", [], dest="automatic")
        except Exception as exc:
            messages.append(f"checkpoint not written ({exc})")

    if os.environ.get("GOV_ROLE") != "orchestrator":
        if messages:
            sys.stdout.write(json.dumps({"systemMessage":
                f"PreCompact: {'; '.join(messages)}. The compaction proceeds."}))
        return

    rel = checkpoint_rel(project_root)
    block = state_block(project_root)  # before the file is read: a checkpoint saved meanwhile is not put back
    try:
        # fails when it is missing, a directory or read-only
        with open(os.path.join(project_root, rel), "r+b", buffering=0) as f:
            was = os.fstat(f.fileno())
            data = f.read()
            kept = len(split(data)[0])
            try:
                put(f, kept, block if data[:kept].endswith(b"\n") or not kept else b"\n" + block)
            except OSError:
                with contextlib.suppress(OSError):
                    put(f, kept, data[kept:])  # the checkpoint as it was
                raise
            finally:
                os.utime(f.fileno(), ns=(was.st_atime_ns, was.st_mtime_ns))
    except OSError as exc:
        messages.append(f"no state block was appended to {rel} ({exc.strerror})")

    if messages:
        sys.stdout.write(json.dumps({"systemMessage":
            f"PreCompact: {'; '.join(messages)}. The compaction proceeds."}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
