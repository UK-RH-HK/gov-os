"""Every path of one audit under the sets root, derived from ``--sets-root`` and ``--audit`` only (Interface section 2).

No flag names a folder under the sets root: the set, its dropped questions, the checker's notes, the selection, the
pool and the run folder are all derived here and checked to stay inside the root.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from gov.memaudit.common import UsageError

AUDIT_RE = re.compile(r"memory-audit-[0-9]{8}")
SET_RE = re.compile(r"memory-(audit|standing)-[0-9]{8}")  # a fresh audit's set, a Wave 0 verdict set or a standing set
STANDING_RE = re.compile(r"memory-standing-[0-9]{8}")
WEEK_RE = re.compile(r"[0-9]{4}-W[0-9]{2}")  # the ISO year and week of a standing run (W2-187 I1)
QFILE_RE = re.compile(r"q[0-9]{2}\.yaml")
NOTES_RE = re.compile(r"XCHECK-r([0-9]+)\.md")
EVALUATION = "fixtures/evaluation"
POOL_SET = "memory-pool"
WALLS = "indep-walls"


def root_of(sets_root) -> Path:
    """The sets root's real path; one that is not a directory, or lies inside the walls' folder, is refused."""
    if sets_root is None or not str(sets_root).strip():
        raise UsageError("sets-root")
    given = os.path.abspath(os.path.expanduser(str(sets_root)))
    real = os.path.realpath(given)
    if not os.path.isdir(real) or WALLS in Path(real).parts or WALLS in Path(given).parts:
        raise UsageError("sets-root")
    return Path(real)


def check_audit(audit) -> str:
    if not isinstance(audit, str) or not SET_RE.fullmatch(audit):
        raise UsageError("audit")
    return audit


def check_week(week) -> str | None:
    """``week`` as given (``YYYY-Www``), ``None`` for none; anything else is a usage error."""
    if week is None:
        return None
    if not isinstance(week, str) or not WEEK_RE.fullmatch(week):
        raise UsageError("week")
    return week


def inside(path, root) -> bool:
    """Whether ``path`` (as given, and as its real path) lies at or under ``root``."""
    root = os.path.realpath(str(root))
    for form in {os.path.abspath(os.path.expanduser(str(path))),
                 os.path.realpath(os.path.expanduser(str(path)))}:
        if form == root or form.startswith(root.rstrip("/") + "/"):
            return True
    return False


def paths(sets_root, audit, week=None) -> dict:
    """Every path of section 2 for ``audit``, each checked to resolve inside the sets root. With ``week`` (a standing
    run, W2-187 I2) ``run`` is ``<sets root>/runs/<set>/<week>/``; ``preflight``, ``declaration``, ``used`` and ``ledger``
    lie in it; ``set``, ``hidden`` and ``map`` are as without it."""
    root = root_of(sets_root)
    audit = check_audit(audit)
    week = check_week(week)
    set_dir = root / EVALUATION / audit
    run = root / "runs" / audit / week if week else root / "runs" / audit
    p = {
        "root": root,
        "map": root / "governance/project/path-map.yaml",
        "set": set_dir,
        "hidden": set_dir / "hidden",
        "dropped": set_dir / "hidden" / "dropped",
        "selection": set_dir / "selection.json",
        "pool": root / EVALUATION / POOL_SET / "hidden",
        "run": run,
        "preflight": run / "PREFLIGHT.json",
        "drops": run / "DROPS.json",
        "declaration": run / "DECLARATION.json",
        "used": run / "USED",
        "ledger": run / "ledger.jsonl",
    }
    for key, value in p.items():
        if key != "root" and not os.path.realpath(value).startswith(str(root) + "/"):
            raise UsageError("layout")
    p["week"] = week
    return p


def is_used(sets_root, audit, week=None) -> bool:
    """Whether the audit's ``USED`` marker exists (a set is measured once; a standing set once a week)."""
    return os.path.lexists(paths(sets_root, audit, week)["used"])


def notes(p: dict) -> tuple[Path | None, int | None]:
    """The checker's notes with the highest round, ``XCHECK-r<n>.md`` beside ``hidden/``, and its round."""
    best = None
    try:
        names = os.listdir(p["set"])
    except OSError:
        return None, None
    for name in names:
        m = NOTES_RE.fullmatch(name)
        if m and (best is None or int(m[1]) > best[1]) and os.path.isfile(p["set"] / name):
            best = (p["set"] / name, int(m[1]))
    return best if best else (None, None)


def entries(hidden: Path) -> tuple[list[Path], int]:
    """The question files ``q<nn>.yaml`` in ``hidden/`` (flat, in name order) and the count of other entries (any file
    not of that name, any folder but ``dropped/``)."""
    files, strays = [], 0
    if not hidden.is_dir():
        return files, strays
    for e in sorted(os.scandir(hidden), key=lambda e: e.name):
        if e.is_dir(follow_symlinks=False) and e.name == "dropped":
            continue
        if QFILE_RE.fullmatch(e.name) and e.is_file(follow_symlinks=False):
            files.append(hidden / e.name)
        else:
            strays += 1
    return files, strays


def make_run(p: dict) -> Path:
    """The run folder, made with mode 700 when absent. A week folder's parent, ``runs/<set>/``, is the standing set's
    own run folder and is made with mode 700 too."""
    run = p["run"]
    if not run.is_dir():
        os.makedirs(run.parent.parent if p.get("week") else run.parent, exist_ok=True)
        if p.get("week") and not run.parent.is_dir():
            os.mkdir(run.parent, 0o700)
            os.chmod(run.parent, 0o700)
        os.mkdir(run, 0o700)
        os.chmod(run, 0o700)
    return run
