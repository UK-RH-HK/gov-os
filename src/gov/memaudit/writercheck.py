"""``writer-check``: a writer's questions form-checked by code before its session ends (FM-1 of the fresh 80's writer loop).

``python3 -m gov.memaudit writer-check --sets-root R --audit A --repo D --commit REV --folder F [--runs-dir X]`` is the
command of the ``Stop`` hook ``brief --kind writer`` writes into the writer's session folder ``F``. It reads the hook's
JSON on standard input and ignores it, and runs ``preflight.evaluate`` (the pre-flight's own checks, no copy) on ``F/out/set``.
Clean: nothing is printed and the end is recorded as ``pass``. Refused, with fewer than 3 returns so far: one JSON line
``{"decision": "block", "reason": ...}`` whose reason is pre-flight's own refusal lines (codes, counts and ids only), one return
counted. The fourth stop is allowed (``ended`` is ``limit``). The record (``returns``, ``ended``, ``refused``: codes with
question ids only) is ``WRITER-CHECK.json`` in the audit's run folder, and a copy of it in ``F`` so that the writer's
session folder shows the check ran (ML-3); a copy that cannot be written changes nothing else.
Exit 0 always: a fault of the check itself lets the session end, and ``deliver`` runs the same checks again.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import layout, preflight
from gov.memaudit.common import read_json, resolve_commit, toplevel, write_whole

DESCRIPTION = ("The Stop hook of a writer's session: runs the pre-flight's per-question and set checks on out/set and "
               "blocks the stop with their codes and ids, up to 3 returns. Exit 0 always.")
MAX_RETURNS = 3
NAME = "WRITER-CHECK.json"


def add_arguments(sp) -> None:
    sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sp.add_argument("--audit", required=True, metavar="NAME", help="the half's name, memory-audit-<8 digits>")
    sp.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    sp.add_argument("--commit", required=True, metavar="REV", help="the pinned commit the half is written at")
    sp.add_argument("--folder", required=True, metavar="DIR", help="the writer's session folder (its out/set is checked)")
    sp.add_argument("--runs-dir", metavar="DIR", help="where indep/ is (default: $GOV_INDEP_RUNS_DIR, else ~/gov-os-runs)")


def default_runs_dir(runs_dir=None) -> Path:
    env = os.environ.get("GOV_INDEP_RUNS_DIR")
    return Path(os.path.expanduser(str(runs_dir) if runs_dir else (env if env else "~/gov-os-runs")))


def record(run_dir: Path, folder: Path, state: dict) -> None:
    """``state`` written to the run folder, then to the session folder (ML-3). The second write's failure is passed
    over: the run folder's record is the one ``writer-run`` reads, and the hook's answer must not depend on a copy."""
    write_whole(run_dir, NAME, state)
    try:
        write_whole(folder, NAME, state)
    except OSError:
        try:
            (folder / f".{NAME}.tmp").unlink()
        except OSError:
            pass


def check(sets_root, audit, *, repo=None, commit, folder, runs_dir=None) -> str | None:
    """The hook's line (JSON) or None. Raises on a fault of the check itself."""
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    commit = resolve_commit(repo, commit)
    cfg = _config.load(repo, commit)
    counts, _ = preflight.evaluate(p, Path(folder) / "out" / "set", repo, commit, cfg, default_runs_dir(runs_dir), audit)
    run_dir = layout.make_run(p)
    state = read_json(run_dir / NAME)
    returns = state.get("returns", 0) if isinstance(state, dict) and isinstance(state.get("returns"), int) else 0
    refused = {c: list(v["ids"]) for c, v in counts["codes"].items() if not v["ok"]}
    if any(ids for ids in refused.values()):  # a set-level count off beside refused questions is their consequence
        refused = {c: ids for c, ids in refused.items() if ids}
    if not refused:
        record(run_dir, Path(folder), {"returns": returns, "ended": "pass", "refused": {}})
        return None
    if returns >= MAX_RETURNS:
        record(run_dir, Path(folder), {"returns": returns, "ended": "limit", "refused": refused})
        return None
    record(run_dir, Path(folder), {"returns": returns + 1, "ended": None, "refused": refused})
    return json.dumps({"decision": "block", "reason": "\n".join(preflight.refused_lines(counts))})


def from_args(args, emit) -> str:
    try:
        sys.stdin.read()  # the hook's JSON: ignored
    except Exception:  # noqa: BLE001
        pass
    try:
        line = check(args.sets_root, args.audit, repo=args.repo, commit=args.commit, folder=args.folder,
                     runs_dir=args.runs_dir)
    except Exception:  # noqa: BLE001: a fault of the check lets the session end; deliver checks the files again
        return "ok"
    if line is not None:
        emit(line)
    return "ok"
