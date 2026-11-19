"""The standing hidden set (W2-187; DEC-1179 (1)-(5), DEC-1176 (1), DEC-1098 (1), DEC-1097 (1)): its record, the declaration,
the week rule, the check against fitting, the below-95 states and the repair.

The standing set is judged once a week by the one judged path of ``driver`` (``declare``, ``measure``, ``judge`` and
``figures`` with ``--week``), never by a second one. Everything this module writes lies in the repository's state
folder (``schedule.state_dir``): ``STANDING.jsonl`` holds a set's name, digests, counts and commits, never a question;
``HISTORY.jsonl`` takes its drift and repair lines. A standing set's questions, ids, answers and citations are written
nowhere outside ``<sets root>/runs/<set>/`` (F1).
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import layout, preflight, schedule, tables
from gov.memaudit.common import UsageError, read_json, set_digest

STANDING = "STANDING.jsonl"
HISTORY = "HISTORY.jsonl"
MIN_LIVE = 70  # fewer live questions asks for a replacement (STANDING_THIN)
MIN_FILES = 36
DRIFT_POINTS = 5
FIGURES_NEEDED = 4
DECISION_RE = re.compile(r"DEC-[0-9]+")


# ---- the record (STANDING.jsonl)

def records(state: Path) -> list[dict]:
    return schedule.read_lines(Path(state) / STANDING)


def append(state: Path, file: str, *rows: dict) -> None:
    """``rows`` appended to ``state/file`` in one write."""
    os.makedirs(state, exist_ok=True)
    with open(Path(state) / file, "a", encoding="utf-8") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows))


def live(state: Path) -> dict | None:
    """The live standing set's ``declared`` record: the last declared and not retired (one is live per repository)."""
    rows = records(state)
    retired = {r.get("set") for r in rows if r.get("event") == "retired"}
    found = [r for r in rows if r.get("event") == "declared" and r.get("set") not in retired]
    return found[-1] if found else None


def declared_sets(state: Path) -> list[str]:
    """Every standing set named in the record, live or retired."""
    return list(dict.fromkeys(r["set"] for r in records(state) if isinstance(r.get("set"), str)))


def retired_sets(state: Path) -> list[str]:
    return list(dict.fromkeys(r["set"] for r in records(state) if r.get("event") == "retired"
                              and isinstance(r.get("set"), str)))


def retire(state: Path, name: str, reason: str) -> None:
    append(state, STANDING, {"event": "retired", "set": name, "reason": reason, "at": schedule.stamp(schedule.now())})


def history(state: Path) -> list[dict]:
    return schedule.read_lines(Path(state) / HISTORY)


def lines_of(state: Path, name: str) -> list[dict]:
    """The standing set's own ``HISTORY.jsonl`` lines (a standing line that names no set is the live set's)."""
    return [x for x in history(state) if x.get("kind") == "standing" and x.get("set") in (name, None)]


def is_standing(sets_root, name: str, repo=None, *, by_name: bool = True) -> bool:
    """Whether ``name`` is a standing set: a ``STANDING.jsonl`` record of the repository, a week folder under
    ``runs/<name>/`` or (``by_name``) the name form ``memory-standing-<date>``."""
    if by_name and layout.STANDING_RE.fullmatch(str(name)):
        return True
    try:
        if any(r.get("set") == name for r in records(schedule.state_of(repo))):
            return True
    except Exception:  # noqa: BLE001: no repository to ask (outside git): the other repositories' records and the folder say
        pass
    for log in sorted(Path(schedule.runs_dir(), "indep", "memaudit").glob(f"*/{STANDING}")):
        if any(r.get("set") == name for r in schedule.read_lines(log)):
            return True
    try:
        folder = layout.root_of(sets_root) / "runs" / str(name)
        return any(layout.WEEK_RE.fullmatch(e.name.removesuffix(".stopped")) and e.is_dir() for e in os.scandir(folder))
    except (OSError, UsageError):
        return False


def latest_maintain(state: Path) -> str | None:
    """The latest ``MAINTAIN`` line of the maintenance pass (counts only), for the digest block."""
    rows = schedule.read_lines(Path(state) / "MAINTAIN.jsonl")
    return rows[-1].get("line") if rows and isinstance(rows[-1].get("line"), str) else None


# ---- S1: standing declare

def _logs(state: Path, runs: Path) -> list[Path]:
    return list(dict.fromkeys([Path(state) / "indep" / "AUDITS.log", Path(runs) / "indep" / "AUDITS.log"]))


def _first_commit(logs) -> str | None:
    for log in logs:
        rows = schedule.read_lines(log)
        if rows:
            return rows[0].get("commit")
    return None


def _questions(hidden: Path) -> list[tuple[Path, dict | None]]:
    out = []
    for f in sorted(hidden.glob("*.yaml")) if hidden.is_dir() else []:
        out.append((f, preflight._load(f)))
    return out


def _spent(p: dict, name: str, hidden: Path, used: bool) -> int | None:
    """The count of this set's questions found in a ``misses.jsonl`` under ``runs/`` (the own run's record of a set with
    a ``USED`` mark not counted: I3 skips it whether or not the Wave 0 conditions then hold; the caller answers
    ``STANDING_SPENT 0`` when they do not), or ``None`` when no question matched and no other mark of use stands."""
    runs = p["root"] / "runs"
    own = runs / name
    seen = set()
    for f in runs.rglob("misses.jsonl") if runs.is_dir() else []:
        if used and f == own / "misses.jsonl":
            continue  # U1: the Wave 0 verdict set's own run does not spend it
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if isinstance(obj, dict) and isinstance(obj.get("question"), str):
                    seen.add(obj["question"])
        except OSError:
            continue
    matched = sum(1 for _, data in _questions(hidden)
                  if isinstance(data, dict) and isinstance(data.get("question"), str) and data["question"] in seen)
    classes = any(f != own / "miss-classes.json" if used else True
                  for f in own.rglob("miss-classes.json")) if own.is_dir() else False
    return matched if matched or classes else None


def _delivered(dirs, kind: str, name: str) -> dict | None:
    found = []
    for d in dirs:
        for f in Path(d).glob(f"indep/{kind}/*/counts.json"):
            data = read_json(f)
            if isinstance(data, dict) and data.get("status") == "delivered" and data.get("set") == name:
                found.append((f.parent.name, data))
    return sorted(found, key=lambda x: x[0])[-1][1] if found else None


def _thin(state: Path, name: str) -> bool:
    mine = [x for x in lines_of(state, name) if x.get("measured") is not False]
    return bool(mine) and "STANDING_THIN" in json.dumps(mine[-1])


def declare(sets_root, name, *, repo=None, runs_dir=None, replaces=None) -> tuple[str, dict]:
    """Record one standing set for the repository (S1). ``("ok", counts)`` or ``("refused", {"code": ...})``; the refusals
    are checked in this order and write nothing: ``STANDING_SPENT <k>``, ``STANDING_LIVE <set>``, ``STANDING_BRIEFS``,
    ``STANDING_FORM``."""
    p = layout.paths(sets_root, name)
    repo = schedule.repo_of(repo)
    runs = Path(os.path.abspath(os.path.expanduser(str(runs_dir)))) if runs_dir else schedule.runs_dir()
    for flag in (repo, runs):
        if layout.inside(flag, p["root"]):
            raise UsageError("flag inside the sets root")
    if replaces is not None and not layout.SET_RE.fullmatch(str(replaces)):
        raise UsageError("replaces")
    state = schedule.state_of(repo)
    hidden, own = p["hidden"], p["root"] / "runs" / name

    wave0, used = False, os.path.lexists(own / "USED")
    if used:  # the repository's Wave 0 verdict set: used once, its counts-only result record there (W2-88 S13, S16)
        decl, fig = read_json(own / "DECLARATION.json"), read_json(own / "FIGURES.json")
        base = _first_commit(_logs(state, runs))
        wave0 = isinstance(decl, dict) and isinstance(fig, dict) and base is not None and decl.get("audit_commit") == base
    k = _spent(p, name, hidden, used)
    if k is None and any(x.get("audit") == name for log in _logs(state, runs) for x in schedule.read_lines(log)):
        k = 0
    if k is None and name in retired_sets(state):
        k = 0
    if k is None and used and not wave0:
        k = 0
    if k is not None:
        return "refused", {"code": f"STANDING_SPENT {k}"}

    current = live(state)
    if current is not None and not (replaces == current["set"] and _thin(state, current["set"])):
        return "refused", {"code": f"STANDING_LIVE {current['set']}"}
    writer, checker = (_delivered([state, runs], kind, name) for kind in ("writer", "checker"))
    if writer is None or checker is None:
        return "refused", {"code": "STANDING_BRIEFS"}
    files, _ = layout.entries(hidden)
    loaded = [(f, preflight._load(f)) for f in files]
    categories = _config.load(repo).quotas  # the repository's own categories
    if len(files) < MIN_FILES or not all(preflight.form_ok(d, f.stem, categories) for f, d in loaded):
        return "refused", {"code": "STANDING_FORM"}

    row = {"event": "declared", "set": name, "set_digest": set_digest(hidden), "n": len(files),
           "n_apart": sum(1 for _, d in loaded if d["category"] == tables.APART),
           "writer_brief_sha256": writer.get("brief_sha256"), "checker_brief_sha256": checker.get("brief_sha256"),
           "written_commit": writer.get("commit"), "wave0": wave0, "at": schedule.stamp(schedule.now())}
    rows = [row]
    if current is not None:
        rows.insert(0, {"event": "retired", "set": current["set"], "reason": "thin", "at": row["at"]})
    append(state, STANDING, *rows)
    return "ok", row


def lines(word: str, counts: dict) -> list[str]:
    if word == "refused":
        return [counts["code"]]
    commit = str(counts.get("written_commit") or "")[:12]
    return [f"STANDING DECLARED {counts['set']}: n {counts['n']} apart {counts['n_apart']} "
            f"digest {counts['set_digest'][:12]} written at {commit}"]


# ---- S2: the week rule

def week_of(at: datetime) -> str:
    year, week, _ = at.isocalendar()
    return f"{year}-W{week:02d}"


def week_state(p: dict) -> str:
    """``go`` (no ``USED`` yet in the week folder, absent or not), ``restart`` (stopped before its reader run began, and
    not restarted yet) or ``used`` (a verdict stands, a reader run began or the one restart has been made)."""
    run = p["run"]
    if not os.path.lexists(p["used"]):
        return "go"
    if os.path.lexists(run / "reader") or os.path.lexists(run / "FIGURES.json") or not os.path.lexists(run / "STOPPED"):
        return "used"
    return "used" if os.path.lexists(run.parent / f"{run.name}.stopped") else "restart"


def restart(p: dict) -> None:
    run = p["run"]
    os.rename(run, run.parent / f"{run.name}.stopped")


# ---- verdicts of HISTORY lines

def verdict_of(line: dict) -> str | None:
    """``pass`` or ``miss`` for a standing line (its ``word``, a string or a list, else ``passes``), else ``None``."""
    word = line.get("word")
    words = word if isinstance(word, list) else [word]
    if "miss" in words:
        return "miss"
    if "pass" in words:
        return "pass"
    return {True: "pass", False: "miss"}.get(line.get("passes"))


def pct_of(line: dict) -> float | None:
    pct = line.get("pct")
    if isinstance(pct, (int, float)) and not isinstance(pct, bool):
        return float(pct)
    right, n = line.get("right"), line.get("n")
    if isinstance(right, int) and isinstance(n, int) and n > 0:
        return 100 * right / n
    return None


def measured_lines(lines_: list[dict]) -> list[dict]:
    return [x for x in lines_ if x.get("kind") == "standing" and x.get("measured") is not False
            and verdict_of(x) is not None]


# ---- S7: the check against fitting

def drift(state: Path, fresh_fig: dict) -> dict:
    """At each fresh run: F is the fresh run's right end to end per cent, S the mean of the live standing set's last
    four weekly figures. ``S - F`` of 5 or more writes ``STANDING_FITTED`` (a HISTORY line) and retires the set;
    ``F - S`` of 5 or more writes ``STANDING_STALE``. Returns ``{"set", "word", "S", "F", "k"}``; ``word`` is ``None``
    with fewer than four figures (``k`` of 4), else ``none``, ``STANDING_FITTED`` or ``STANDING_STALE``."""
    state = Path(state)
    now = live(state)
    if now is None:
        return {"set": None, "word": None, "S": None, "F": None, "k": 0}
    v = (fresh_fig or {}).get("verdict") if isinstance((fresh_fig or {}).get("verdict"), dict) else {}
    n, right = (fresh_fig or {}).get("n"), v.get("right")
    mine = [pct_of(x) for x in measured_lines(lines_of(state, now["set"])) if pct_of(x) is not None]
    out = {"set": now["set"], "word": None, "S": None, "F": None, "k": min(len(mine), FIGURES_NEEDED)}
    if not (isinstance(n, int) and n > 0 and isinstance(right, int)):
        return out
    out["F"] = round(100 * right / n, 2)
    if len(mine) < FIGURES_NEEDED:
        return out
    out["S"] = round(sum(mine[-FIGURES_NEEDED:]) / FIGURES_NEEDED, 2)
    gap = out["S"] - out["F"]
    word = "STANDING_FITTED" if gap >= DRIFT_POINTS - 1e-9 else "STANDING_STALE" if -gap >= DRIFT_POINTS - 1e-9 else "none"
    out["word"] = word
    if word != "none":
        append(state, HISTORY, {"kind": "drift", "word": word, "S": out["S"], "F": out["F"], "set": now["set"]})
    if word == "STANDING_FITTED":
        retire(state, now["set"], "fitted")
    return out


# ---- S8: the repair

def repair_state(rows: list[dict]) -> tuple[bool, str]:
    """``(open, week it opened)``, read from the lines in order: ``MEMORY_REPAIR open`` opens it; ``closed``, a
    ``residual`` line or a later standing line that passes closes it."""
    is_open, week = False, ""
    for x in rows:
        if x.get("kind") == "repair":
            word = x.get("word")
            if word == "MEMORY_REPAIR open":
                is_open, week = True, str(x.get("week") or "")
            elif word in ("MEMORY_REPAIR closed", "MEMORY_REPAIR residual"):
                is_open = False
        elif is_open and x.get("kind") == "standing" and x.get("measured") is not False and verdict_of(x) == "pass":
            is_open = False
    return is_open, week


def repair_after(state: Path, name: str, week: str) -> None:
    """After a standing measured line: write ``MEMORY_REPAIR open`` when none is open and this line and the one before
    are both misses, or this line is a miss 5 points or more below the last passing figure; ``MEMORY_REPAIR closed`` when
    this line passes and one was open (W2-187 I8)."""
    rows = history(state)
    at = max((i for i, x in enumerate(rows) if x.get("kind") == "standing" and x.get("set") == name), default=None)
    if at is None:
        return
    was_open, _ = repair_state(rows[:at])
    mine = [x for x in measured_lines(rows[:at + 1]) if x.get("set") == name]
    this, before = mine[-1], mine[:-1]
    if verdict_of(this) == "pass":
        if was_open:
            append(state, HISTORY, {"kind": "repair", "word": "MEMORY_REPAIR closed", "set": name, "week": week})
        return
    if was_open:
        return
    passing = [pct_of(x) for x in before if verdict_of(x) == "pass" and pct_of(x) is not None]
    now = pct_of(this)
    two = bool(before) and verdict_of(before[-1]) == "miss"
    far = bool(passing) and now is not None and passing[-1] - now >= DRIFT_POINTS - 1e-9
    if two or far:
        append(state, HISTORY, {"kind": "repair", "word": "MEMORY_REPAIR open", "set": name, "week": week})


def repair_status(sets_root, repo, residual, emit) -> str:
    """``status --repair``: ``REPAIR open since <week>`` (refused, exit 1) or ``REPAIR none``; with ``--residual DEC-<n>``
    the owner's decision is recorded and the answer is ``REPAIR residual DEC-<n>`` (exit 0)."""
    state = schedule.state_of(repo)
    if residual is not None:
        if not DECISION_RE.fullmatch(str(residual)):
            raise UsageError("residual")
        append(state, HISTORY, {"kind": "repair", "word": "MEMORY_REPAIR residual", "decision": residual})
        emit(f"REPAIR residual {residual}")
        return "ok"
    is_open, week = repair_state(history(state))
    if is_open:
        emit(f"REPAIR open since {week}")
        return "refused"
    emit("REPAIR none")
    return "ok"
