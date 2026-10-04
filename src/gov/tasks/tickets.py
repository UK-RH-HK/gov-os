"""Ticket files of ``.tickets/``: reading their frontmatter, and creating one (DEC-295)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

TICKETS_REL = ".tickets"
TK_REL = "governance/kernel/bin/tk"  # where an adopted project holds the vendored script (ADR-0002 section 5)


def frontmatter(path: Path) -> dict | None:
    """The frontmatter of the ticket file ``path``; None when it is no file or cannot be read."""
    import yaml

    try:
        lines = [line.rstrip() for line in Path(path).read_text(encoding="utf-8").split("\n")]
        front = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)])) if lines[0] == "---" else None
    except (OSError, ValueError, yaml.YAMLError):
        return None
    return front if isinstance(front, dict) else None


def create(root: Path, title: str) -> str:
    """Run the project's vendored ``tk create`` and add ``state_class`` to the new ticket; its id."""
    tickets = Path(root) / TICKETS_REL
    done = subprocess.run([str(Path(root) / TK_REL), "create", title], cwd=root, capture_output=True, text=True,
                          check=True, env={**os.environ, "TICKETS_DIR": str(tickets)})
    ticket = done.stdout.strip().split("\n")[-1]
    path = tickets / f"{ticket}.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    lines.insert(lines.index("---", 1), "state_class: AUTHORITATIVE")
    path.write_text("\n".join(lines), encoding="utf-8")
    return ticket
