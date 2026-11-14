"""``due``, ``status`` and ``baseline``, and what they share with ``run``: the clock seam, the driver's own folder, the
store link, the churn of a commit and the active-and-stable rule (W2-172 Interface items 1, 4, 9, 10, 11).

Every figure here comes from git, ``HISTORY.jsonl``, ``STARTS.log`` and ``AUDITS.log``; none is read from a path under
the sets root (F1). Counts, codes and repository paths only.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from gov.memaudit.common import GitError, UsageError, blob_at, git, git_code, resolve_commit, toplevel, z_list

RETRIEVAL_GLOBS = ("src/gov/retrieval/**", "src/gov/retrieve/**", "src/gov/store/**", "src/gov/codeintel/**",
                   "governance/project/retrieval.yaml", "governance/project/path-map.yaml")
# the same six as git pathspecs (a directory names its whole tree), for ``git log`` and ``git diff``
RETRIEVAL_SPECS = ("src/gov/retrieval", "src/gov/retrieve", "src/gov/store", "src/gov/codeintel",
                   "governance/project/retrieval.yaml", "governance/project/path-map.yaml")
EXCLUDE_FILE = "governance/project/indep-walls/tree-exclude.txt"
REBUILD_YAML = "governance/project/rebuild.yaml"
WINDOW_DAYS = 28
WEEKLY_DAYS, MONTHLY_DAYS, RECENT_DAYS = 6, 28, 5
CALM, BUSY = 0.05, 0.10  # churn under 5 % is calm; 10 % or more sends a monthly audit back to weekly


def now() -> datetime:
    """``GOV_MEMAUDIT_NOW`` (ISO 8601 UTC) when set, else the real UTC time (the one clock of the driver)."""
    given = os.environ.get("GOV_MEMAUDIT_NOW")
    return parse_time(given) if given else datetime.now(timezone.utc)


def parse_time(text) -> datetime:
    try:
        when = datetime.fromisoformat(str(text).strip().replace("Z", "+00:00"))
    except ValueError:
        raise UsageError("time") from None
    return when if when.tzinfo else when.replace(tzinfo=timezone.utc)


def stamp(when: datetime) -> str:
    return when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def runs_dir() -> Path:
    """The runs folder: ``$GOV_INDEP_RUNS_DIR``, else ``~/gov-os-runs`` (never a flag)."""
    given = os.environ.get("GOV_INDEP_RUNS_DIR")
    return Path(os.path.abspath(os.path.expanduser(given or "~/gov-os-runs")))


def state_dir(runs, repo) -> Path:
    """The audit's state of one repository: ``<runs>/indep/memaudit/<key>/`` (W2-187 I2), ``<key>`` the repository's
    directory name, a hyphen and the first 8 hex of the sha256 of its real path, so two repositories on one machine
    keep separate ``HISTORY.jsonl``, ``STARTS.log``, ``STANDING.jsonl`` and (under ``indep/``) ``AUDITS.log``."""
    real = os.path.realpath(str(repo))
    return Path(runs) / "indep" / "memaudit" / f"{os.path.basename(real)}-{hashlib.sha256(real.encode()).hexdigest()[:8]}"


def state_of(repo) -> Path:
    """The state folder a child of the driver finds (the driver names it in ``GOV_MEMAUDIT_STATE``), else the one this
    repository's own key gives."""
    given = os.environ.get("GOV_MEMAUDIT_STATE")
    return Path(given) if given else state_dir(runs_dir(), repo_of(repo))


def repo_of(repo) -> Path:
    return Path(os.path.abspath(os.path.expanduser(repo))) if repo else toplevel()


def mainline(repo) -> str:
    """The main line, as the launch script reads it: ``w2/integrate`` when it exists, else ``main``."""
    for ref in ("refs/heads/w2/integrate", "refs/heads/main"):
        if git_code(repo, "show-ref", "--verify", "--quiet", ref) == 0:
            return ref
    raise UsageError("mainline")


def store_link(repo, given) -> str:
    """``--store-link``, else ``integration_store`` of ``rebuild.yaml`` at the main line."""
    if given:
        return str(given)
    import yaml
    data = blob_at(repo, mainline(repo), REBUILD_YAML)
    try:
        link = (yaml.safe_load(data) or {}).get("integration_store") if data else None
    except yaml.YAMLError:
        link = None
    if not isinstance(link, str) or not link:
        raise UsageError("store-link")
    return link


def head_of(link) -> str:
    try:
        return git(link, "rev-parse", "HEAD").decode().strip()
    except GitError:
        raise UsageError("store-link") from None


def due_head(repo, given) -> str:
    """The head the triggers are computed at: the store link's, else (``due`` and ``status`` need no link to answer)
    the main line's."""
    try:
        return head_of(store_link(repo, given))
    except UsageError:
        return git(repo, "rev-parse", mainline(repo)).decode().strip()


def committer_time(repo, commit) -> int:
    return int(git(repo, "show", "-s", "--format=%ct", commit).decode().strip())


def matches(path: str, globs) -> bool:
    return any(fnmatch.fnmatchcase(path, g) for g in globs)


def excluded_by(globs):
    """The walls' tree-exclude rule, as the launch script applies it: a path, or any folder above it, matches a glob."""
    def excluded(rel: str) -> bool:
        parts = rel.split("/")
        for i in range(1, len(parts) + 1):
            p = "/".join(parts[:i])
            forms = (p, p + "/") if i < len(parts) else (p,)
            if any(fnmatch.fnmatchcase(f, g) for f in forms for g in globs):
                return True
        return False
    return excluded


def churn_at(repo, commit) -> tuple[float, bool]:
    """``(churn, retrieval_28d)`` at ``commit``: the share of its tracked paths (less the walls' tree-exclude paths) that
    changed in the 28 days before its committer time, and whether any changed path is a retrieval path."""
    at = committer_time(repo, commit)
    raw = blob_at(repo, commit, EXCLUDE_FILE)
    globs = [x.strip() for x in raw.decode("utf-8", "replace").splitlines()
             if x.strip() and not x.lstrip().startswith("#")] if raw else []
    skip = excluded_by(globs)
    tracked = {p for p in z_list(git(repo, "ls-tree", "-r", "-z", "--name-only", commit)) if not skip(p)}
    changed = set(z_list(git(repo, "log", "-z", "--name-only", "--format=",
                             f"--since=@{at - WINDOW_DAYS * 86400}", f"--until=@{at}", commit)))
    share = len(tracked & changed) / len(tracked) if tracked else 0.0
    return round(share, 4), any(matches(p, RETRIEVAL_GLOBS) for p in changed)


def _changed(repo, since, until, gov, last_pin) -> list[str]:
    paths = []
    if since:
        try:
            names = z_list(git(repo, "diff", "-z", "--name-only", since, until))
        except GitError:  # a commit the repository does not hold: nothing to name
            names = []
        paths = [p for p in names if matches(p, RETRIEVAL_GLOBS)]
    if isinstance(last_pin, str):  # a line without the field (W2-172's planted lines) is no trigger
        from gov.memaudit import declare
        pin = declare.gov_pin(gov or "~/.local/bin/gov")
        if pin is not None and pin != last_pin:
            paths.append("gov-pin")
    return paths


def last_line(lines, key):
    """The value of ``key`` of the last of ``lines`` that has it."""
    return next((x[key] for x in reversed(lines) if key in x), None)


def retrieval_changed(repo, since, until, gov=None) -> list[str]:
    """The retrieval paths in ``git diff --name-only <since> <until>`` over the six globs, for every repository (none
    when there is no earlier audit), and ``gov-pin`` when the gov pin differs from the last ``HISTORY.jsonl`` line's
    (W2-187 I9)."""
    state = state_of(repo)
    return _changed(repo, since, until, gov, last_line(read_lines(state / "HISTORY.jsonl"), "gov_pin"))


def read_lines(path: Path) -> list[dict]:
    """The JSON objects of a log, one a line; a line that is not an object is skipped."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def last_audit_commit(state: Path) -> str | None:
    """The commit "since the last audit" starts from: the last ``HISTORY.jsonl`` line's, else ``AUDITS.log``'s."""
    for source in (state / "HISTORY.jsonl", state / "indep" / "AUDITS.log"):
        lines = [x for x in read_lines(source) if isinstance(x.get("commit"), str)]
        if lines:
            return lines[-1]["commit"]
    return None


def kind_of(line: dict) -> str:
    """``standing`` or ``fresh``: a line without ``kind`` is a fresh audit's (W2-172's)."""
    return "standing" if line.get("kind") == "standing" else "fresh"


def decide(repo, state: Path, head: str, at: datetime, lines=None, *, standing: bool = False, gov=None) -> dict:
    """The active-and-stable rule, computed and never chosen (item 9): ``mode``, ``reason``, ``due``, ``next`` (a date),
    and the churn at ``head`` the rule used. ``lines`` are the ``HISTORY.jsonl`` lines it reads (default: the fresh
    audits' own, or with ``standing`` the standing lines); with ``standing`` it reads the standing ``STARTS.log`` lines."""
    history = read_lines(state / "HISTORY.jsonl")
    if lines is None:
        lines = [x for x in history if (kind_of(x) == "standing") == standing]
    measured = [x for x in lines if x.get("measured") is True]
    churn, _ = churn_at(repo, head)
    last = measured[-1] if measured else None
    if len(measured) < 3:
        mode, reason = "weekly", "start"
    else:
        trigger = None
        if churn >= BUSY:
            trigger = "churn"
        elif _changed(repo, last_audit_commit(state), head, gov, last_line(history, "gov_pin")):
            trigger = "retrieval"
        elif last.get("passes") is False:
            trigger = "verdict"
        elif last.get("pool_regression") is True:
            trigger = "pool"
        calm = all(isinstance(x.get("churn"), (int, float)) and x["churn"] < CALM and x.get("retrieval_28d") is False
                   and x.get("passes") is True and x.get("pool_regression") is False for x in measured[-3:])
        mode, reason = ("weekly", trigger) if trigger else (("monthly", "stable") if calm else ("weekly", "active"))
    days = MONTHLY_DAYS if mode == "monthly" else WEEKLY_DAYS
    starts = [x for x in read_lines(state / "STARTS.log") if (kind_of(x) == "standing") == standing]
    if not starts:
        return {"mode": mode, "reason": reason, "due": True, "next": at.strftime("%Y-%m-%d"), "churn": churn}
    try:
        last_start = parse_time(starts[-1].get("at"))
    except UsageError:
        last_start = at  # an unreadable stamp counts as a start just now: never due early
    due_at = last_start + timedelta(days=days)
    return {"mode": mode, "reason": reason, "due": at >= due_at, "next": max(due_at, at).strftime("%Y-%m-%d"),
            "churn": churn}


def monday_on_or_after(day: date) -> date:
    return day + timedelta(days=-day.weekday() % 7)


def fresh_due(starts: list[dict], standing_last: dict | None, at: datetime) -> dict:
    """The fresh set's cadence (W2-187 I8): ``first`` (no fresh start), ``miss`` (the live set's last standing
    measured line missed and no fresh start in the current ISO week), ``28d`` (today is on or after the first Monday on
    or after the last fresh start's date + 28 days) or ``wait``."""
    today = at.date()
    if not starts:
        return {"due": True, "reason": "first", "next": today.isoformat()}
    try:
        last = parse_time(starts[-1].get("at"))
    except UsageError:
        last = at
    week = at.isocalendar()[:2]
    started = False
    for x in starts:
        try:
            started = started or parse_time(x.get("at")).isocalendar()[:2] == week
        except UsageError:
            continue
    from gov.memaudit import standing
    missed = bool(standing_last) and standing.verdict_of(standing_last) == "miss"
    if missed and not started:
        return {"due": True, "reason": "miss", "next": today.isoformat()}
    ripe = monday_on_or_after((last + timedelta(days=WINDOW_DAYS)).date())
    if today >= ripe:
        return {"due": True, "reason": "28d", "next": today.isoformat()}
    nxt = today + timedelta(days=7 - today.weekday()) if missed else ripe
    return {"due": False, "reason": "wait", "next": nxt.isoformat()}


def due(sets_root, repo, link, emit, fresh: bool = False) -> str:
    from gov.memaudit import standing
    repo = repo_of(repo)
    state = state_of(repo)
    head = due_head(repo, link)
    live = standing.live(state)
    if fresh and live:
        history = read_lines(state / "HISTORY.jsonl")
        mine = [x for x in history if x.get("kind") == "standing" and x.get("set") == live["set"]
                and x.get("measured") is True]
        starts = [x for x in read_lines(state / "STARTS.log") if kind_of(x) == "fresh"]
        verdict = fresh_due(starts, mine[-1] if mine else None, now())
        emit("MODE fresh")
        emit(f"DUE {'yes' if verdict['due'] else 'no'} next {verdict['next']}")
        emit(f"REASON {verdict['reason']}")
        return "ok" if verdict["due"] else "refused"
    if live:
        verdict = decide(repo, state, head, now(), standing.lines_of(state, live["set"]), standing=True)
    else:
        verdict = decide(repo, state, head, now())
    emit(f"MODE {verdict['mode']}")
    emit(f"DUE {'yes' if verdict['due'] else 'no'} next {verdict['next']}")
    emit(f"REASON {verdict['reason']}")
    return "ok" if verdict["due"] else "refused"


def status(sets_root, repo, since, link, emit) -> str:
    from gov.memaudit import standing
    repo = repo_of(repo)
    since = resolve_commit(repo, since)
    last = git(repo, "log", "-1", "--format=%H", f"{since}..{mainline(repo)}", "--", *RETRIEVAL_SPECS).decode().strip()
    state = state_of(repo)
    if last:
        audited = any(git_code(repo, "merge-base", "--is-ancestor", last, x["commit"]) == 0
                      for x in read_lines(state / "HISTORY.jsonl")
                      if x.get("measured") is True and isinstance(x.get("commit"), str))
        if not audited:
            live = standing.live(state)
            if live:
                verdict = decide(repo, state, due_head(repo, link), now(), standing.lines_of(state, live["set"]),
                                 standing=True)
            else:
                verdict = decide(repo, state, due_head(repo, link), now())
            emit(f"not audited, next due {verdict['next']}")
            return "refused"
    emit("audited")
    return "ok"


def baseline(sets_root, repo, commit, emit) -> str:
    repo = repo_of(repo)
    try:
        full = resolve_commit(repo, commit)
    except UsageError:
        emit("BL-COMMIT")
        return "refused"
    log = state_dir(runs_dir(), repo) / "indep" / "AUDITS.log"
    try:
        held = any(x.strip() for x in log.read_text(encoding="utf-8").splitlines())
    except OSError:
        held = False
    if held:
        emit("BL-EXISTS")
        return "refused"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": stamp(now()), "commit": full, "run": "baseline", "audit": "baseline"}) + "\n")
    emit(f"BASELINE {full[:12]}")
    return "ok"
