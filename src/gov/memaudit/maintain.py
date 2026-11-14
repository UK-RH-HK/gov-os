"""``python3 -m gov.memaudit maintain``: the weekly maintenance pass (W2-187 I10; S10, F6; DEC-1179 (6), DEC-1178 (1)).

Six counts, before the standing run, and never a gate: each item is bounded by a timeout and a fault in one is named in
its word, never raised, so the pass exits 0 whatever it finds (4 for usage). It changes none of the standard's four
settings, applies no ACT, installs nothing and writes neither ``retrieval.yaml`` nor the path map; what it writes is
its own line in the state folder and, for each set the sets root's path map declares (a standing set left out), one
re-anchoring request that holds question ids and entry numbers only.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path

from gov.memaudit import layout, matcher, schedule
from gov.memaudit import standing as record
from gov.memaudit.common import UsageError, git, read_json, sha256_file

BUILD_S, OTHER_S = 1800, 300
MAINTAIN = "MAINTAIN.jsonl"
ENTRY = re.compile(r"entry ([0-9]+)(?:\.[0-9]+)?")
RETRIEVAL_YAML, PATH_MAP = "governance/project/retrieval.yaml", "governance/project/path-map.yaml"


def _timeout(build: bool) -> float:
    given = os.environ.get("GOV_MEMAUDIT_MAINTAIN_TIMEOUT_S")
    try:
        return float(given) if given else float(BUILD_S if build else OTHER_S)
    except ValueError:
        return float(BUILD_S if build else OTHER_S)


def _run(argv, cwd, *, build: bool = False) -> tuple[int, str]:
    """``(exit code, standard output)`` of a child; a timeout is 124 and a program not found 127."""
    try:
        done = subprocess.run(argv, cwd=str(cwd), capture_output=True, stdin=subprocess.DEVNULL,
                              timeout=_timeout(build))
    except subprocess.TimeoutExpired:
        return 124, ""
    except OSError:
        return 127, ""
    return done.returncode, done.stdout.decode("utf-8", "replace")


def _db(link) -> Path:
    return Path(link) / ".gov-runtime" / "store.db"


def _found(link) -> int | None:
    """``gov.store.layout.found_of`` on the store, opened read-only: ``None`` when current."""
    from gov.store import layout as store_layout
    conn = sqlite3.connect(f"file:{_db(link)}?mode=ro", uri=True)
    try:
        return store_layout.found_of(conn)
    finally:
        conn.close()


# ---- the six items

def store_item(repo, link, gov, branch) -> str:
    """1. The integration store at the main line's head, else one refresh by ``gov rebuild --integration``; a failed
    build leaves the last good store in service and names it."""
    want = git(repo, "rev-parse", f"refs/heads/{branch}").decode().strip()
    head = schedule.head_of(link)
    if head == want:
        return f"current {head[:12]}"
    code, _ = _run([gov, "rebuild", "--integration", branch], repo, build=True)
    now = schedule.head_of(link)
    return f"refreshed {now[:12]}" if code == 0 and now == want else f"kept {now[:12]} (refresh exit {code})"


def layout_item(repo, link, gov, branch) -> str:
    """2. The store's layout current, else one rebuild by the same command, else ``stale kept``."""
    if _found(link) is None:
        return "current"
    _run([gov, "rebuild", "--integration", branch], repo, build=True)
    try:
        return "rebuilt" if _found(link) is None else "stale kept"
    except (sqlite3.Error, OSError):
        return "stale kept"


def links_item(repo, gov, since) -> int | str:
    """3. ``gov links --since <the last pass's commit> --json``: the count of new findings; a first pass runs from the
    mark with no ``--since``; a refusal is ``none``."""
    code, out = _run([gov, "links", *(["--since", since] if since else []), "--json"], repo)
    if code not in (0, 1):
        return "none"
    try:
        new = json.loads(out)["result"]["new"]
    except (ValueError, KeyError, TypeError):
        return "none"
    return new if isinstance(new, int) and not isinstance(new, bool) else "none"


def unindexed_item(link) -> int:
    """4. The tracked paths of the link's worktree that the path map indexes (``lexical.kept_out`` keeps the rest out) and
    the store holds no chunk of."""
    from gov.retrieval import lexical
    names = [os.fsdecode(x) for x in git(link, "ls-files", "-z").split(b"\0") if x]
    files = [rel for rel in names if "\n" not in rel and (Path(link) / rel).is_file()]
    out = set(lexical.kept_out(Path(link), files))
    conn = sqlite3.connect(f"file:{_db(link)}?mode=ro", uri=True)
    try:
        try:
            held = {row[0] for row in conn.execute("SELECT DISTINCT path FROM lexical_chunk")}
        except sqlite3.OperationalError:  # a store with no chunk table holds no path: the count is a number all the same
            held = set()
    finally:
        conn.close()
    return sum(1 for rel in files if rel not in out and rel not in held)


def _rows(folder: Path) -> list[dict]:
    rows = []
    for f in sorted((folder / "reader").glob("*.json")) if (folder / "reader").is_dir() else []:
        row = read_json(f) if f.name != "plan.json" else None
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _latest(folder: Path, rx) -> Path | None:
    names = sorted((e.name for e in os.scandir(folder) if rx.fullmatch(e.name) and (Path(e.path) / "reader").is_dir()),
                   reverse=True) if folder.is_dir() else []
    return folder / names[0] if names else None


def answers_item(root: Path, state: Path) -> tuple[int, int]:
    """5. The ``not found`` answers and the second searches in the latest standing week's and the latest fresh run's
    reader rows: two counts."""
    standing_names = set(record.declared_sets(state))
    folders = []
    declared = record.records(state)
    if declared:
        folders.append(_latest(root / "runs" / declared[-1]["set"], layout.WEEK_RE))
    fresh = [e.name for e in os.scandir(root / "runs") if layout.AUDIT_RE.fullmatch(e.name)
             and e.name not in standing_names and (Path(e.path) / "reader").is_dir()] if (root / "runs").is_dir() else []
    if fresh:
        folders.append(root / "runs" / sorted(fresh)[-1])
    rows = [r for f in folders if f is not None for r in _rows(f)]
    return (sum(1 for r in rows if r.get("final_verdict") == "not_found"),
            sum(1 for r in rows if r.get("searches")))


def reanchor_item(root: Path, state: Path, link, week: str, commit: str) -> int:
    """6. The gold questions whose cited lines changed at the audit commit (the measure's own list of unresolved
    blocks: a block moved unchanged is found again and not listed), for every set the sets root's path map declares but
    the standing sets: one request per set with an entry, question id and entry number only, mode 0600."""
    standing_names = set(record.declared_sets(state))
    total = 0
    for name in sorted(matcher.M.evaluation_sets(str(root))):
        if name in standing_names or layout.STANDING_RE.fullmatch(name):
            continue
        changed = {}
        for part in ("visible", "hidden"):
            try:
                found = matcher.questions(root, name, part, link)
            except Exception:  # noqa: BLE001: a set that cannot be loaded as the measure loads it lists nothing
                continue
            for q in found:
                for text in q.get("unresolved") or []:
                    m = ENTRY.fullmatch(text)
                    if m:
                        changed[(q["id"], int(m[1]))] = None
        if not changed:
            continue
        rows = [{"id": i, "entry": n} for i, n in sorted(changed)]
        run = layout.make_run({"run": root / "runs" / name})
        tmp = run / f".REANCHOR-{week}.json.tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps({"week": week, "audit_commit": commit, "set": name, "changed": rows,
                                "count": len(rows)}, indent=1, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, run / f"REANCHOR-{week}.json")
        total += len(rows)
    return total


def _sha(repo, rel: str) -> str | None:
    try:
        return sha256_file(Path(repo) / rel)
    except OSError:
        return None


# ---- the pass

def run(sets_root, *, repo=None, link=None, gov=None, emit) -> str:
    """The exit word: ``ok`` always; a usage fault raises ``UsageError`` (exit 4)."""
    root = layout.root_of(sets_root)
    repo = schedule.repo_of(repo)
    gov = os.path.abspath(os.path.expanduser(str(gov) if gov is not None else "~/.local/bin/gov"))
    for flag in (repo, gov):
        if layout.inside(flag, root):
            raise UsageError("flag inside the sets root")
    state = schedule.state_of(repo)
    link = schedule.store_link(repo, link)
    branch = schedule.mainline(repo).removeprefix("refs/heads/")
    before = {"retrieval_yaml": _sha(repo, RETRIEVAL_YAML), "path_map": _sha(repo, PATH_MAP)}
    rows = schedule.read_lines(state / MAINTAIN)
    since = next((x["commit"] for x in reversed(rows) if isinstance(x.get("commit"), str)), None)
    week = record.week_of(schedule.now())

    def guarded(item, fallback):
        try:
            return item()
        except Exception:  # noqa: BLE001: the pass never fails the audit; the item says it could not be read
            return fallback

    one = guarded(lambda: store_item(repo, link, gov, branch), "unknown")
    two = guarded(lambda: layout_item(repo, link, gov, branch), "unknown")
    head = guarded(lambda: schedule.head_of(link), "")
    three = guarded(lambda: links_item(repo, gov, since), "none")
    four = guarded(lambda: unindexed_item(link), 0)
    five = guarded(lambda: answers_item(root, state), (0, 0))
    six = guarded(lambda: reanchor_item(root, state, link, week, head), 0)
    line = (f"MAINTAIN 1 store {one} 2 layout {two} 3 links {three} 4 unindexed {four} 5 not_found {five[0]} "
            f"second {five[1]} 6 reanchor {six}")
    after = {"retrieval_yaml": _sha(repo, RETRIEVAL_YAML), "path_map": _sha(repo, PATH_MAP)}
    record.append(state, MAINTAIN, {
        "week": week, "commit": head, "at": schedule.stamp(schedule.now()), "store": one, "layout": two, "links": three,
        "unindexed": four, "not_found": five[0], "second": five[1], "reanchor": six, "line": line,
        "sha256": {k: {"before": before[k], "after": after[k]} for k in before}})
    emit(line)
    return "ok"
