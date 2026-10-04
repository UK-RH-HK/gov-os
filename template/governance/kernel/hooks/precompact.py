#!/usr/bin/env python3
"""
PreCompact hook (W1-49, light form of CAP-37; W1-29 replaces it).

Never blocks a compaction (DEC-264). Appends one generated state block
to the checkpoint, after the part the session wrote: the orchestrator's
in the main tree, the lead's in a linked worktree. A second compaction
replaces the block. Acts only when GOV_ROLE is exactly "orchestrator"
(DEC-259).

The written part is never changed: the new file is built beside the
checkpoint and put in its place in one step, with the modification
time the checkpoint had, so the file's time stays the time of its
written part. What the hook could not do it says in a systemMessage.
Always exits 0.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import time

BEGIN = b"<!-- GENERATED STATE BLOCK BEGIN -->"
END = b"<!-- GENERATED STATE BLOCK END -->"
STAMP = "%Y-%m-%dT%H:%M:%SZ"


def checkpoint_rel(project_root: str) -> str:
    """The lead's checkpoint in a linked worktree (.git is a file
    there), the orchestrator's in the main tree."""
    linked = os.path.isfile(os.path.join(project_root, ".git"))
    return f".gov-runtime/scratch/{'lead' if linked else 'orchestrator'}/CHECKPOINT.md"


def split(data: bytes) -> tuple[bytes, bytes]:
    """(written part, generated block). There is a block only when the
    last line that is not empty is the end marker; it starts at the
    last line that is the begin marker and nothing else."""
    lines = data.splitlines(keepends=True)
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and lines[-1].strip() == END:
        for index in range(len(lines) - 1, -1, -1):
            if lines[index].strip() == BEGIN:
                return b"".join(lines[:index]), b"".join(lines[index:])
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
    return (
        f"{BEGIN.decode()}\n"
        f"generated: {time.strftime(STAMP, time.gmtime())}\n"
        f"git head: {output(project_root, 'git', 'rev-parse', 'HEAD').strip()}\n"
        f"tickets in progress (`tk ls --status=in_progress`):{output(project_root, 'tk', 'ls', '--status=in_progress')}\n"
        f"worktrees (`git worktree list`):{output(project_root, 'git', 'worktree', 'list')}\n"
        "pending owner decisions: not known to the hook; see the written part of this checkpoint\n"
        f"{END.decode()}\n"
    ).encode("utf-8")


def main() -> None:
    if os.environ.get("GOV_ROLE") != "orchestrator":
        return
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    rel = checkpoint_rel(project_root)
    path = os.path.join(project_root, rel)
    beside = path + ".precompact"
    try:
        with open(path, "r+b") as f:  # fails when it is missing, a directory or read-only
            written = split(f.read())[0]
            was = os.fstat(f.fileno())
        if written and not written.endswith(b"\n"):
            written += b"\n"
        with open(beside, "wb") as f:
            f.write(written + state_block(project_root))
        os.chmod(beside, was.st_mode & 0o7777)
        os.utime(beside, ns=(was.st_atime_ns, was.st_mtime_ns))
        os.replace(beside, path)
    except OSError as exc:
        sys.stdout.write(json.dumps({"systemMessage": f"PreCompact: no state block was appended to {rel} "
                                                      f"({exc.strerror}). The compaction proceeds."}))
    finally:
        with contextlib.suppress(OSError):
            os.remove(beside)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
