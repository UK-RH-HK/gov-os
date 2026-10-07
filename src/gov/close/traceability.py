"""Product-traceability check: every closed ticket's commits carry Implements: and Task: trailers that resolve.

Run as ``python3 -m gov.close.traceability`` (CAP-38.b).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


def _frontmatter(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end < 0:
        return None
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return None
    return front if isinstance(front, dict) else None


def _closed_tickets(root: Path) -> list[dict]:
    tickets_dir = root / ".tickets"
    if not tickets_dir.is_dir():
        return []
    closed = []
    for path in sorted(tickets_dir.glob("*.md")):
        front = _frontmatter(path)
        if front and front.get("status") == "closed":
            closed.append(front)
    return closed


def _read_trailers(root: Path, sha: str) -> dict[str, list[str]]:
    result = subprocess.run(
        ["git", "-C", str(root), "log", "-1", "--format=%(trailers)", sha],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git log (trailers) failed for {sha[:12]}: {result.stderr.strip()[:200]}")
    trailers: dict[str, list[str]] = {}
    for line in result.stdout.split("\n"):
        line = line.strip()
        if ": " in line:
            key, _, value = line.partition(": ")
            key = key.strip()
            value = value.strip()
            if key and value:
                trailers.setdefault(key, []).append(value)
        elif ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if key and value:
                trailers.setdefault(key, []).append(value)
    return trailers


def _commits_for_ticket(root: Path, ticket_id: str) -> list[dict]:
    result = subprocess.run(
        ["git", "-C", str(root), "log", "HEAD", "--format=%H",
         f"--grep=Task: {ticket_id}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git log failed for ticket {ticket_id}: {result.stderr.strip()[:200]}")

    shas = [s.strip() for s in result.stdout.strip().split("\n") if s.strip()]
    commits = []
    for sha in shas:
        trailers = _read_trailers(root, sha)
        task_values = trailers.get("Task", [])
        if any(v.strip() == ticket_id for v in task_values):
            commits.append({"sha": sha, "trailers": trailers})
    return commits


def _record_ids(root: Path) -> set[str]:
    ids = set()
    store_path = root / ".gov-runtime" / "store.db"
    if store_path.is_file():
        try:
            from gov.store import connect
            conn = connect(root)
            try:
                for row in conn.execute("SELECT id FROM records").fetchall():
                    ids.add(row[0])
            finally:
                conn.close()
        except Exception as exc:
            raise RuntimeError(f"cannot read the record store: {exc}") from exc

    tickets_dir = root / ".tickets"
    if tickets_dir.is_dir():
        for path in tickets_dir.glob("*.md"):
            front = _frontmatter(path)
            if front and "id" in front:
                ids.add(front["id"])

    for md_dir in (root / "docs").rglob("*.md") if (root / "docs").is_dir() else []:
        front = _frontmatter(md_dir)
        if front and "id" in front:
            ids.add(front["id"])

    return ids


def main() -> int:
    root = Path.cwd()
    findings = []

    closed = _closed_tickets(root)

    if not closed:
        print(json.dumps({"not_applicable": True, "reason": "no closed ticket"}))
        return 2

    try:
        known_ids = _record_ids(root)
    except RuntimeError as exc:
        print(json.dumps({"findings": [{"code": "STORE_ERROR", "message": str(exc)}]}))
        return 1

    for ticket in closed:
        ticket_id = ticket.get("id", "")
        if not ticket_id:
            continue
        try:
            commits = _commits_for_ticket(root, ticket_id)
        except RuntimeError as exc:
            findings.append({
                "code": "GIT_FAILURE",
                "message": str(exc),
            })
            continue
        if not commits:
            findings.append({
                "code": "NO_COMMITS",
                "message": f"closed ticket {ticket_id} has no commits with Task: trailer",
            })
            continue

        for c in commits:
            task_vals = c["trailers"].get("Task", [])
            impl_vals = c["trailers"].get("Implements", [])

            if not any(v.strip() == ticket_id for v in task_vals):
                findings.append({
                    "code": "MISSING_TASK_TRAILER",
                    "message": f"commit {c['sha'][:12]} of {ticket_id} lacks Task: trailer",
                })

            if not impl_vals:
                findings.append({
                    "code": "MISSING_IMPLEMENTS_TRAILER",
                    "message": f"commit {c['sha'][:12]} of {ticket_id} lacks Implements: trailer",
                })
            else:
                for val in impl_vals:
                    for item in val.replace(",", " ").split():
                        item = item.strip()
                        if item and item not in known_ids:
                            findings.append({
                                "code": "IMPLEMENTS_UNRESOLVED",
                                "message": f"commit {c['sha'][:12]} of {ticket_id}: Implements: {item} does not resolve",
                            })

    if findings:
        print(json.dumps({"findings": findings}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
