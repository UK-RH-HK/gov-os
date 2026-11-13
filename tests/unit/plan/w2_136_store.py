"""A planted ticket store for W2-136's unit tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from gov.cli.main import main


def ticket(tid: str, *, status: str = "open", priority: int = 1, wbs: str | None = None, writes=(), needs=(),
           **fields) -> dict:
    front = {"id": tid, "status": status, "priority": priority, "wbs_id": wbs or f"W9-{tid.split('-')[-1]}",
             "role": "engineer", "allowed_paths": list(writes), "depends_on": [], "deps": []}
    if needs is not None:
        front["needs"] = list(needs)
    front.update(fields)
    if "depends_on" in fields and "deps" not in fields:
        front["deps"] = list(fields["depends_on"])
    return front


def plant(root: Path, *tickets: dict, order=None) -> Path:
    folder = root / ".tickets"
    folder.mkdir(parents=True, exist_ok=True)
    for front in (tickets if order is None else [tickets[n] for n in order]):
        text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n# " + front["id"] + "\n"
        (folder / f"{front['id']}.md").write_text(text, encoding="utf-8")
    return root


def run(root: Path, capsys, *args: str) -> tuple[int, str]:
    capsys.readouterr()
    code = main(["plan", "--root", str(root), *args])
    return code, capsys.readouterr().out


def run_json(root: Path, capsys, *args: str) -> tuple[int, dict]:
    code, out = run(root, capsys, "--json", *args)
    return code, json.loads(out)


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(str(path.relative_to(root)).encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()
