"""``gov decisions page``, the part of it a batch needs (W2-211 PG-1; the renderer is slice b).

Takes the open packages that are page-ready (PG-1), names for every other open package the field at fault, and publishes
the batch as its manifest ``<batches>/<batch>.manifest.json``: the batch id, the day it was made, its hash (``batch_hash``)
and its cards in order, each with the card's fields and its package's content hash. It writes no page and makes no commit.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from gov.decisions import package, sheet

BATCHES_DEFAULT = "docs/decisions/batches"
PAGE_MAX = 12


class PageError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def manifest_path(root: Path, batches: str, batch: str) -> Path:
    return Path(root) / batches / f"{batch}.manifest.json"


def next_batch_id(root: Path, batches: str, now: datetime) -> str:
    day = now.strftime("%Y%m%d")
    folder = Path(root) / batches
    taken = {p.name.split(".")[0] for p in folder.glob(f"B-{day}-*.manifest.json")} if folder.is_dir() else set()
    n = 1
    while f"B-{day}-{n}" in taken:
        n += 1
    return f"B-{day}-{n}"


def withdrawn(packages: dict) -> dict[str, str]:
    """``{old id: newer id}``: a package some other package ``replaces`` is re-asked, so it is withdrawn."""
    out: dict[str, str] = {}
    for pid, pkg in packages.items():
        old = pkg["front"].get("replaces")
        if isinstance(old, str) and old in packages and old != pid:
            out[old] = pid
    return out


def build(root: Path, batches: str, register: str, limit: int, now: datetime | None = None) -> dict:
    """``{batch, taken, refused, manifest}``: the open page-ready packages in order, the others with their problems."""
    now = now or datetime.now(timezone.utc)
    packages = package.load_all(root)
    gone = withdrawn(packages)
    taken, refused = [], []
    for pid in sorted(packages):
        front = packages[pid]["front"]
        if front.get("status") != "PROPOSED" or pid in gone or front.get("file_only"):
            continue
        problems = package.page_ready(front, root, register)
        (refused if problems else taken).append((pid, problems) if problems else pid)
    taken = taken[:limit]
    if not taken:
        return {"batch": None, "taken": [], "refused": refused, "manifest": None}
    batch = next_batch_id(root, batches, now)
    cards = []
    for pid in taken:
        fields = package.card(packages[pid]["front"])
        cards.append({**fields, "content_hash": package.content_hash(packages[pid]["text"])})
    covered = [{k: v for k, v in c.items() if k != "content_hash"} for c in cards]
    manifest = {"batch": batch, "created": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "hash": sheet.batch_hash(batch, covered), "cards": cards}
    return {"batch": batch, "taken": taken, "refused": refused, "manifest": manifest}


def publish(root: Path, batches: str, manifest: dict) -> Path:
    path = manifest_path(root, batches, manifest["batch"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path
