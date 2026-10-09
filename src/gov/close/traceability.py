"""Product-traceability check: every closed ticket's commits carry Implements: and Task: trailers that resolve.

Run as ``python3 -m gov.close.traceability`` (CAP-38.b).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

# DEC-482: an optional top-level key of the project's path map, a commit id, full or abbreviated. With it,
# only the commits after that commit are judged.
BASE_KEY = "trailers_base"
COMMIT_ID = re.compile(r"[0-9a-fA-F]{4,64}")


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


def _after_base(root: Path) -> tuple[str, set[str]] | None:
    """The trailers base the project's path map records, as the project holds it now, and the commits after
    it (DEC-482, DEC-479); None with no base: the whole history is judged. ``ValueError`` where the value is
    not the id, full or abbreviated, of one commit that ``HEAD`` descends from."""
    from gov.config.loader import load_config

    path_map = load_config(root).get("path-map.yaml", {})
    if BASE_KEY not in path_map:
        return None
    base = path_map[BASE_KEY]

    def asked(*args: str):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)

    if isinstance(base, str) and COMMIT_ID.fullmatch(base):
        commit = asked("rev-parse", "--verify", "--quiet", base + "^{commit}").stdout.strip()
        # The id of the commit, not a branch or a tag named in hex digits.
        if commit.startswith(base.lower()) and asked("merge-base", "--is-ancestor", commit, "HEAD").returncode == 0:
            listed = asked("rev-list", f"{commit}..HEAD")
            if listed.returncode != 0:
                raise RuntimeError(f"git rev-list failed after {commit[:12]}: {listed.stderr.strip()[:200]}")
            return commit, set(listed.stdout.split())
    raise ValueError(f"the base commit {base!r} recorded under '{BASE_KEY}' is not one commit of the project "
                     "that HEAD descends from: no commit is judged")


def main() -> int:
    from gov.cli.errors import GovError

    root = Path.cwd()
    findings = []

    closed = _closed_tickets(root)

    if not closed:
        print(json.dumps({"not_applicable": True, "reason": "no closed ticket"}))
        return 2

    try:
        after = _after_base(root)
    except ValueError as exc:
        print(json.dumps({"findings": [{"code": "TRAILERS_BASE_UNKNOWN", "message": str(exc)}]}))
        return 1
    except (GovError, RuntimeError) as exc:  # the base is not known: nothing is judged, and nothing passes
        print(json.dumps({"unmeasured": True, "reason": getattr(exc, "message", str(exc))}))
        return 1

    try:
        known_ids = _record_ids(root)
    except RuntimeError as exc:
        print(json.dumps({"findings": [{"code": "STORE_ERROR", "message": str(exc)}]}))
        return 1

    judged = 0
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
        if not commits:  # with a base too: the base takes commits out of the judgement, not tickets
            findings.append({
                "code": "NO_COMMITS",
                "message": f"closed ticket {ticket_id} has no commits with Task: trailer",
            })
            continue
        if after is not None:
            commits = [c for c in commits if c["sha"] in after[1]]
        judged += len(commits)

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
    if after is not None and not judged:  # nothing judged is not a clean history (DEC-479)
        print(json.dumps({"unmeasured": True, "reason": f"no commit of a closed ticket after the base commit "
                          f"{after[0][:12]} ('{BASE_KEY}'): nothing is judged"}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
