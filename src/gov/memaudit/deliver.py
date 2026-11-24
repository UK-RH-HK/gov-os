"""``deliver``: a session's ``out/`` folder taken into the sets root (W2-204 I5; S10, F-2 of P-FRESH-80-1).

``gov memaudit deliver --kind writer|checker --sets-root R --audit A --repo D --from DIR [--round 1|2]``; ``DIR`` is
the session's ``out/`` folder itself.

- **A writer's:** ``result.json`` must hold ``questions``, ``by_kind`` and ``by_area``, each object's counts summing to
  ``questions`` and ``by_area`` keyed by the configuration's domains and ``none`` (``DL-RESULT``); ``set/`` must hold
  plain files named ``q<nn>.yaml`` and nothing else, as many as ``questions`` (``DL-SET``). They are copied byte for
  byte into the set's ``hidden/``. Round 1 refuses a ``hidden/`` that holds anything (``DL-EXISTS``); round 2 first
  moves what round 1 left to the set's ``r1/``, so no stray reaches the pre-flight.
- **A checker's:** ``notes.md`` in the checker brief's form (``# Cross-check notes``, then ``## Questions``, then
  ``## The set``; ``DL-NOTES``) becomes the set's ``XCHECK-r<n>.md`` (``DL-EXISTS`` when that round's notes are there).

A refusal copies nothing. No file's text is printed: ``DELIVER <kind> round <n> files|lines <count>``.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import drops, layout, ledger, preflight, writercheck
from gov.memaudit.common import UsageError, read_json, resolve_commit, toplevel

DESCRIPTION = ("Takes a session's out/ folder into the sets root: a writer's result.json and set/q*.yaml into the "
               "half's own folder (round 2 moves round 1 aside first), a checker's notes.md into XCHECK-r<n>.md. A "
               "delivery that fails its form is refused and nothing is copied. Counts only.")
HEAD, SET_SECTION = "# Cross-check notes", "## The set"


def add_arguments(sp) -> None:
    sp.add_argument("--kind", required=True, choices=("writer", "checker"), help="whose delivery")
    sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sp.add_argument("--audit", required=True, metavar="NAME", help="the half's name, memory-audit-<8 digits>")
    sp.add_argument("--repo", metavar="DIR", help="the repository whose configuration names the domains "
                                                  "(default: the top level)")
    sp.add_argument("--from", required=True, dest="source", metavar="DIR", help="the session's out/ folder")
    sp.add_argument("--round", type=int, choices=(1, 2), default=1, help="the round (default 1)")


def _count(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _sums(obj, total: int, keys=None) -> bool:
    return (isinstance(obj, dict) and all(isinstance(k, str) and _count(v) for k, v in obj.items())
            and (keys is None or set(obj) <= set(keys)) and sum(obj.values()) == total)


def result_ok(doc, cfg) -> bool:
    """The writer's result: ``questions``, and ``by_kind`` and ``by_area`` each summing to it; ``by_area`` in the
    configuration's domain names and ``none`` only."""
    if not isinstance(doc, dict) or not _count(doc.get("questions")):
        return False
    return (_sums(doc.get("by_kind"), doc["questions"])
            and _sums(doc.get("by_area"), doc["questions"], [*cfg.domain_names, _config.NONE]))


def set_files(folder: Path) -> list[Path] | None:
    """The question files of ``folder`` in name order, or None when it holds anything but plain ``q<nn>.yaml`` files
    (a link, a folder, another name) or none at all."""
    if folder.is_symlink() or not folder.is_dir():
        return None
    found = []
    for e in sorted(os.scandir(folder), key=lambda e: e.name):
        if not layout.QFILE_RE.fullmatch(e.name) or e.is_symlink() or not e.is_file(follow_symlinks=False):
            return None
        found.append(folder / e.name)
    return found or None


def notes_ok(text: str) -> bool:
    lines = [x.strip() for x in text.splitlines()]
    body = [x for x in lines if x]
    if not body or body[0] != HEAD or drops.SECTION not in lines or SET_SECTION not in lines:
        return False
    return lines.index(drops.SECTION) < lines.index(SET_SECTION) and drops.read_notes(text) is not None


def _commit_of(p: dict, repo):
    """The commit the half's briefs were made at (the ledger's last ``brief`` event), when the repository holds it."""
    for e in reversed(ledger.read(p["ledger"])):
        if e.get("event") == "brief":
            return _config.recorded(repo, e.get("commit"))
    return None


def _writer(p: dict, cfg, source: Path, rnd: int, emit, repo=None, audit=None) -> str:
    if not result_ok(read_json(source / "result.json"), cfg):
        emit("DL-RESULT")
        return "refused"
    files = set_files(source / "set")
    if files is None:
        emit("DL-SET")
        return "refused"
    if len(files) != read_json(source / "result.json")["questions"]:
        emit("DL-RESULT")
        return "refused"
    commit = _commit_of(p, repo)
    if commit is not None:  # the pre-flight's own checks on the delivered files, codes only (FM-1)
        counts, _ = preflight.evaluate(p, source / "set", repo, resolve_commit(repo, commit), cfg,
                                       writercheck.default_runs_dir(), audit)
        if not counts["ok"]:
            emit("DL-PREFLIGHT")
            for line in preflight.refused_lines(counts):
                emit(line)
            return "refused"
    hidden, aside = p["hidden"], p["set"] / "r1"
    held = sorted(os.listdir(hidden)) if hidden.is_dir() else []
    if rnd == 1 and held:
        emit("DL-EXISTS")
        return "refused"
    if rnd == 2 and (not held or (os.path.lexists(aside) and os.listdir(aside))):
        emit("DL-EXISTS" if held else "DL-SET")  # a second round-2 delivery; or no round 1 to revise
        return "refused"
    os.makedirs(hidden, mode=0o700, exist_ok=True)
    if rnd == 2:
        os.makedirs(aside, mode=0o700, exist_ok=True)
        for name in held:
            os.rename(hidden / name, aside / name)
    for f in files:
        shutil.copyfile(f, hidden / f.name)
    emit(f"DELIVER writer round {rnd} files {len(files)}")
    return "ok"


def _checker(p: dict, source: Path, rnd: int, emit) -> str:
    notes = source / "notes.md"
    try:
        if notes.is_symlink() or not notes.is_file():
            raise OSError
        raw = notes.read_bytes()
    except OSError:
        emit("DL-NOTES")
        return "refused"
    text = raw.decode("utf-8", "replace")
    if not notes_ok(text):
        emit("DL-NOTES")
        return "refused"
    target = p["set"] / f"XCHECK-r{rnd}.md"
    if os.path.lexists(target):
        emit("DL-EXISTS")
        return "refused"
    if not p["set"].is_dir():
        emit("DL-SET")  # notes for a half nothing was delivered to
        return "refused"
    tmp = target.with_name(f".{target.name}.tmp")
    with open(tmp, "wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, target)
    emit(f"DELIVER checker round {rnd} lines {len(drops.read_notes(text))}")
    return "ok"


def run(sets_root, audit, *, kind, repo=None, source, rnd=1, emit) -> str:
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    if not source or not str(source).strip():
        raise UsageError("from")
    source = Path(os.path.abspath(os.path.expanduser(str(source))))
    for flag in (repo, source):
        if layout.inside(flag, p["root"]):
            raise UsageError("flag inside the sets root")
    cfg = _config.load(repo, _commit_of(p, repo))
    if kind == "writer":
        return _writer(p, cfg, source, rnd, emit, repo, audit)
    return _checker(p, source, rnd, emit)


def from_args(args, emit) -> str:
    return run(args.sets_root, args.audit, kind=args.kind, repo=args.repo, source=args.source, rnd=args.round,
               emit=emit)
