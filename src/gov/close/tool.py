"""The ticket tool of a close (B2, B3; DEC-492): where it is found, and the repair ticket opened through it.

One lookup serves closing and repair tickets: the installed kernel's tool, and where the kernel's place holds
nothing, the one on ``PATH``. Whatever lies at the kernel's place is the tool: one that fails there is not
replaced by another.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from gov.cli.errors import GovError
from gov.close import state as _state

TOOL_NAME = "tk"
NOT_OPENED = "not opened"  # how the answer begins where the tool opened no repair ticket
# What a repair ticket holds of the findings: under what one argument of a command carries (128 KiB on Linux).
FINDINGS_BYTES = 96 * 1024


def find(root: Path) -> Path:
    """The ticket tool: the kernel's where its place holds anything, else the one on ``PATH``;
    ``TICKET_TOOL_ABSENT`` with neither."""
    from gov.tasks.tickets import TK_REL

    kernel = Path(root) / TK_REL
    if os.path.lexists(kernel):
        return kernel
    on_path = shutil.which(TOOL_NAME)
    if on_path:
        return Path(os.path.abspath(on_path))  # the tool runs in the project's folder, not the caller's
    raise GovError("TICKET_TOOL_ABSENT",
                    f"the ticket tool ({TOOL_NAME}) is not available at {TK_REL} or on PATH",
                    {"looked_at": [TK_REL, "PATH"]})


def tk(root: Path, *args: str) -> str:
    """The output of the ticket tool; ``TICKET_TOOL_ABSENT`` or ``TICKET_TOOL_FAILED``."""
    from gov.tasks.tickets import TICKETS_REL

    try:
        tool = find(root)
    except GovError as e:
        e.details["command"] = args[0]
        raise
    try:
        done = subprocess.run(
            [str(tool), *args], capture_output=True, text=True, cwd=str(root),
            env={**os.environ, "TICKETS_DIR": str(Path(root) / TICKETS_REL)})
    except OSError as e:
        raise GovError("TICKET_TOOL_FAILED", f"tk {args[0]} cannot run: {e}",
                        {"command": args[0], "tool": str(tool)})
    if done.returncode != 0:
        raise GovError("TICKET_TOOL_FAILED",
                        f"tk {args[0]} failed with exit code {done.returncode}: "
                        f"{done.stderr.strip()[:200]}",
                        {"command": args[0], "tool": str(tool)})
    return done.stdout


def close(root: Path, ticket: str) -> None:
    """Close ``ticket`` through the tool. ``TICKET_TOOL_FAILED`` too when the tool answers that it did and the
    ticket's file does not say closed: the tool on ``PATH`` is whatever carries its name (DEC-492)."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    tk(root, "close", ticket)
    status = (frontmatter(Path(root) / TICKETS_REL / f"{ticket}.md") or {}).get("status")
    if str(status) != "closed":
        raise GovError("TICKET_TOOL_FAILED",
                        f"tk close answered without an error and the status of {ticket} is {status!r}, not closed",
                        {"command": "close", "tool": str(find(root))})


def findings_held(findings: list[str]) -> int:
    """How many of ``findings``, from the first on, a repair ticket holds: the findings go to the tool as one
    argument, and those that would take it beyond ``FINDINGS_BYTES`` are left out, whole."""
    room = FINDINGS_BYTES
    for held, finding in enumerate(findings):
        room -= len(finding.encode("utf-8")) + len("- \n")
        if room < 0:
            return held
    return len(findings)


def open_repair_ticket(root: Path, ticket: str, findings: list[str],
                       disposition: str | None = None,
                       context_hash: str | None = None,
                       context_reason: str | None = None,
                       not_measured: list[str] | None = None) -> str:
    """Open the repair ticket of a refused close through the ticket tool: its
    parent and its findings with ``tk create``, its dependency on ``ticket``
    with ``tk dep``. Returns what the answer says of it: its id, or that none
    was opened and why. No ticket file is written by any other means.
    """
    from gov.tasks.tickets import TICKETS_REL

    held = findings_held(findings)
    description = [f"Findings of the refused close of {ticket} "
                   f"(disposition: {disposition or 'unclassed'}):"]
    description += [f"- {finding}" for finding in findings[:held]]
    if held < len(findings):
        description.append(f"Cut: {len(findings) - held} of the {len(findings)} findings are not in this ticket, "
                           "which holds the first of them; the answer of the refused close names every one.")
    if not_measured:
        description.append("Not measured by that close:")
        description += [f"- {part}" for part in not_measured]
    if context_reason:
        description.append(f"The class was given without whole-system context: {context_reason}")
    try:
        created = tk(root, "create", f"Repair {ticket}: {findings[0][:60]}",
                     "--parent", ticket, "-d", "\n".join(description))
    except GovError as e:
        return f"{NOT_OPENED}: {e.message}"
    repair_id = created.strip().split("\n")[-1]
    path = Path(root) / TICKETS_REL / f"{repair_id}.md"

    # What tk has no option for, as lines of the frontmatter tk wrote (as
    # gov.tasks.tickets.create adds state_class): the class and the context hash.
    fields = ["state_class: AUTHORITATIVE", f"disposition: {disposition or 'unclassed'}"]
    if context_hash:
        fields.append(f"context_hash: {context_hash}")
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
        end = lines.index("---", 1)
        _state.write_whole(path, "\n".join(lines[:end] + fields + lines[end:]))
    except (OSError, ValueError) as e:
        return f"{repair_id} opened by tk; its class could not be recorded: {e}"
    try:
        tk(root, "dep", repair_id, ticket)
    except GovError as e:
        return f"{repair_id} opened; its dependency on {ticket} was not recorded: {e.message}"
    return repair_id
