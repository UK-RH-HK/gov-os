"""Ticket files of ``.tickets/``: reading their frontmatter, and creating one (DEC-295)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from gov.util.frontmatter import of_file
from gov.util.gitenv import git_env

TICKETS_REL = ".tickets"
TK_REL = "governance/kernel/bin/tk"  # where an adopted project holds the vendored script (ADR-0002 section 5)


def frontmatter(path: Path) -> dict | None:
    """The frontmatter of the ticket file ``path``; None when it is no file or cannot be read."""
    return of_file(path)


def create(root: Path, title: str) -> str:
    """Run the project's vendored ``tk create`` and add ``state_class`` to the new ticket; its id."""
    tickets = Path(root) / TICKETS_REL
    done = subprocess.run([str(Path(root) / TK_REL), "create", title], cwd=root, capture_output=True, text=True,
                          check=True, env={**git_env(root), "TICKETS_DIR": str(tickets)})
    ticket = done.stdout.strip().split("\n")[-1]
    path = tickets / f"{ticket}.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    lines.insert(lines.index("---", 1), "state_class: AUTHORITATIVE")
    path.write_text("\n".join(lines), encoding="utf-8")
    return ticket
