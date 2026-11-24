"""``brief``: a writer's or a checker's session folder, its brief filled from the repository's configuration (W2-204
I5; S9, F-2 of P-FRESH-80-1).

``gov memaudit brief --kind writer|checker --sets-root R --audit A --commit REV --repo D [--round 1|2] [--since REV]
--out DIR`` writes ``DIR/brief.md`` (never printed) and what the session reads: for the writer ``DIR/seed.txt`` and
``DIR/input/selection.json`` (the tracked paths changed since ``--since`` and a seeded sample of up to 300 others, less
the configuration's ``exclude``; a copy is the set's ``selection.json`` in the sets root, the record the pre-flight's
draw check reads); for round 2 and for the checker ``DIR/input/set/`` (the delivered questions, copied byte for byte and
never opened as text); for the writer's round 2 ``DIR/input/notes.md`` (the round-1 notes). The product starts no
session: the repository's CTO does, with this folder. One line is printed, ``BRIEF <kind> round <n> <12 hex>`` (the
brief's sha256), and a ``brief`` event is appended to the audit's ledger.
"""

from __future__ import annotations

import json
import os
import random
import secrets
import shlex
import shutil
import sys
from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import layout, ledger, preflight
from gov.memaudit.briefs import TEMPLATES
from gov.memaudit.common import (UsageError, git, read_json, resolve_commit, sha256_bytes, toplevel, z_list)

DESCRIPTION = ("Writes a writer's or a checker's session folder: brief.md filled from the repository's memory-audit "
               "configuration, and its input (the selection and the seed, the delivered set, the notes). Prints one "
               "line; the brief is never printed.")
KINDS = ("writer", "checker")
SAMPLE_N = 300
CHANGED_OF_40, KEYWORD_OF_40 = 24, 6  # the draw's and the keyword mark's share of a 40-question half, scaled
SEED_NAME = "seed.txt"


def add_arguments(sp) -> None:
    sp.add_argument("--kind", required=True, choices=KINDS, help="whose brief")
    sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sp.add_argument("--audit", required=True, metavar="NAME", help="the half's name, memory-audit-<8 digits>")
    sp.add_argument("--commit", required=True, metavar="REV", help="the pinned commit")
    sp.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    sp.add_argument("--round", type=int, choices=(1, 2), default=1, help="the round (default 1)")
    sp.add_argument("--since", metavar="REV", help="the last audit's commit: the paths changed since it are `changed`")
    sp.add_argument("--out", required=True, metavar="DIR", help="the session's folder (made when absent)")


# ---- the brief's text

def _tick(names) -> str:
    return ", ".join(f"`{n}`" for n in names)


def _subsystems(cfg) -> str:
    if not cfg.subsystems:
        return "(the configuration names no subsystem)."
    parts = []
    for s in cfg.subsystems:
        if s.record_key is not None:
            parts.append(f"`{s.name}` (a first source whose front matter has `{s.record_key}`: "
                         f"{' or '.join(s.values)})")
        else:
            parts.append(f"`{s.name}` ({', '.join(f'`{p}`' for p in s.paths)})")
    return "; ".join(parts) + ". A first source in none of them counts as `none`."


def fields(cfg, commit: str, rnd: int) -> dict:
    """What the templates' ``{{names}}`` stand for, all from the configuration."""
    half, names = cfg.half_size, [c.name for c in cfg.categories]
    changed_n = CHANGED_OF_40 * half // 40
    table = ["   | `category` | " + " | ".join(names) + " |", "   |" + "---|" * (len(names) + 1),
             "   | Count | " + " | ".join(str(c.count) for c in cfg.categories) + " |"]
    about = [f"   - `{c.name}` ({c.count}): {c.about.strip() or 'no note'}." for c in cfg.categories]
    off_list = [n for n in ("history", _config.APART) if n in names]
    no_list = (f"The {' and '.join(f'`{n}`' for n in off_list)} questions have no list path and count among the "
               f"{half - changed_n}.")
    areas = [*cfg.domain_names, _config.NONE]
    return {
        "repository": cfg.repository, "commit": commit, "round": str(rnd), "half": str(half),
        "half_less_one": str(half - 1), "min_kept": str(cfg.min_kept), "sample_size": str(SAMPLE_N),
        "category_count": str(len(names)), "category_table": "\n".join(table), "category_about": "\n".join(about),
        "category_counts": ", ".join(f"{c.name} {c.count}" for c in cfg.categories),
        "changed_n": str(changed_n), "sample_n": str(half - changed_n), "no_list": no_list,
        "domains": "; ".join(f"`{d.name}` ({', '.join(f'`{p}`' for p in d.paths)})" for d in cfg.domains),
        "domain_min": str(cfg.spread.domain_min), "subsystem_max": str(cfg.spread.subsystem_max),
        "subsystems": _subsystems(cfg), "keyword_max": str(KEYWORD_OF_40 * half // 40),
        "exclude": _tick(cfg.exclude) if cfg.exclude else "none",
        "by_area": _tick(areas),
        "notes_domains": ", ".join(f"{n} <n>" for n in areas),
        "notes_categories": ", ".join(f"{n} <n>" for n in names),
    }


def render(kind: str, cfg, commit: str, rnd: int = 1) -> str:
    text = TEMPLATES[kind]
    for name, value in fields(cfg, commit, rnd).items():
        text = text.replace("{{" + name + "}}", value)
    if "{{" in text:
        raise ValueError("template")
    return text


# ---- the selection

def select(repo, cfg, commit: str, since: str | None, seed: int) -> dict:
    """``changed`` (alphabetical) and ``sample`` (in the order drawn) of the paths tracked at ``commit``, less the
    configuration's ``exclude``."""
    tracked = z_list(git(repo, "ls-tree", "-r", "--name-only", "-z", commit))
    have, changed = set(tracked), []
    if since:
        diff = z_list(git(repo, "diff", "--name-only", "--no-renames", "-z", since, commit))
        changed = sorted({p for p in diff if p in have and not cfg.excluded(p)})
    chosen = set(changed)
    others = [p for p in tracked if not cfg.excluded(p) and p not in chosen]
    sample = random.Random(seed).sample(others, min(SAMPLE_N, len(others)))
    return {"commit": commit, "last_audit": since, "seed_sha256": sha256_bytes(f"{seed}\n".encode()),
            "changed": changed, "sample": sample}


def _write(path: Path, data: bytes) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _recorded_seed(p: dict, commit: str, since) -> tuple[int, bytes] | None:
    """The seed and the selection already recorded for this set at this commit and this last audit, so that a brief
    asked twice gives the writer the same lists."""
    doc = read_json(p["selection"])
    try:
        seed = int((p["set"] / SEED_NAME).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    if (isinstance(doc, dict) and doc.get("commit") == commit and doc.get("last_audit") == since
            and doc.get("seed_sha256") == sha256_bytes(f"{seed}\n".encode())):
        return seed, p["selection"].read_bytes()
    return None


def refusals_section(p: dict, kind: str) -> str:
    """``## Pre-flight 1 refusals`` from ``PREFLIGHT.json`` (FM-2): each refused id with its code, a set-level code on its
    own line; ids, codes and counts only. Empty when pre-flight 1 passed or left no record."""
    doc = read_json(p["preflight"])
    codes = doc.get("codes") if isinstance(doc, dict) and doc.get("ok") is False else None
    if not isinstance(codes, dict):
        return ""
    rows = []
    for code, c in codes.items():
        if not isinstance(c, dict) or c.get("ok", True):
            continue
        if code in preflight.SET_LEVEL:
            rows.append(f"- set {code} {'; '.join(c.get('detail') or []) or c.get('refused')}")
        else:
            rows += [f"- {qid} {code}" for qid in c.get("ids") or []]
    if not rows:
        return ""
    text = ["", "## Pre-flight 1 refusals", "", "The first pre-flight refused these (an id with its code; a line "
            "`set` is a code about the whole half):", "", *rows, ""]
    if kind == "writer":
        text += ["Repair or replace exactly those questions in this round: a refused id is rewritten or swapped for "
                 "a new question that passes the same checks, and a `set` line is met by what the half as a whole "
                 "lacks. Leave every other question as it is.", ""]
    return "\n".join(text)


def writer_permissions(out) -> dict:
    """What lets a writer's session write its set and nothing else (FM-5), in the wall template's own slash form."""
    o = "/" + os.path.abspath(os.path.expanduser(str(out))).lstrip("/")
    return {"allow": [f"Write({o}/out/**)", f"Edit({o}/out/**)"],
            "deny": [f"Edit({o}/.claude/**)", f"Edit({o}/input/**)", f"Edit({o}/brief.md)"]}


def stop_hook(p: dict, audit: str, repo, commit: str, out: Path) -> dict:
    """The writer's ``.claude/settings.json``: a ``Stop`` hook running ``writer-check`` on ``out/set`` (FM-1)."""
    src = Path(__file__).resolve().parents[2]
    argv = ["env", f"PYTHONPATH={src}", sys.executable, "-m", "gov.memaudit", "writer-check", "--sets-root", str(p["root"]),
            "--audit", audit, "--repo", str(Path(repo).resolve()), "--commit", commit, "--folder", str(out)]
    return {"permissions": writer_permissions(out),
            "hooks": {"Stop": [{"hooks": [{"type": "command", "command": shlex.join(argv)}]}]}}


WRITER_TOOLS = "Read,Grep,Glob,Write,Edit,TodoWrite"
WRITER_MODEL = "claude-sonnet-5-5"
LAUNCH_NAME = "LAUNCH.txt"


def launch_command(out: Path, repo) -> str:
    """The one real writer launch (FM-5): the session folder's own settings (the ``Stop`` hook) load through
    ``--setting-sources project --settings``; no ``--safe-mode`` and no ``--no-session-persistence``. Run with ``out`` as cwd."""
    prompt = "Read brief.md in this folder and do what it says."
    argv = ["claude", "-p", "--restricted", "--setting-sources", "project", "--settings",
            str(out / ".claude" / "settings.json"), "--add-dir", str(Path(repo).resolve()), "--tools", WRITER_TOOLS,
            "--strict-mcp-config", "--permission-prompts", "none", "--model", WRITER_MODEL, prompt]
    return shlex.join(argv)


def run(sets_root, audit, *, kind, commit, repo=None, rnd=1, since=None, out, emit) -> str:
    """The exit word: ``ok``, or ``refused`` with ``BR-NOSET`` (round 2 or a checker with nothing delivered) or
    ``BR-NONOTES`` (a writer's round 2 without the round-1 notes). Nothing is written before every refusal is past."""
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    if not out or not str(out).strip():
        raise UsageError("out")
    out = Path(os.path.abspath(os.path.expanduser(str(out))))
    for flag in (repo, out):
        if layout.inside(flag, p["root"]):
            raise UsageError("flag inside the sets root")
    commit = resolve_commit(repo, commit)
    cfg = _config.load(repo, commit)
    since = resolve_commit(repo, since) if since else None
    if kind == "checker" and since:
        raise UsageError("since")

    delivered, _ = layout.entries(p["hidden"])
    notes = p["set"] / "XCHECK-r1.md"
    if (kind == "checker" or rnd == 2) and not delivered:
        emit("BR-NOSET")
        return "refused"
    if kind == "writer" and rnd == 2 and not notes.is_file():
        emit("BR-NONOTES")
        return "refused"

    text = (render(kind, cfg, commit, rnd) + (refusals_section(p, kind) if rnd == 2 else "")).encode("utf-8")
    os.makedirs(out / "input", exist_ok=True)
    if kind == "writer" and rnd == 1:
        kept = _recorded_seed(p, commit, since)
        if kept is None:
            seed = secrets.randbits(63)
            selection = (json.dumps(select(repo, cfg, commit, since, seed), indent=1) + "\n").encode("utf-8")
            os.makedirs(p["set"], exist_ok=True)
            _write(p["set"] / SEED_NAME, f"{seed}\n".encode())
            _write(p["selection"], selection)
        else:
            seed, selection = kept
        _write(out / SEED_NAME, f"{seed}\n".encode())
        _write(out / "input" / "selection.json", selection)
    else:  # round 2 and the checker read the lists the writer drew from
        if p["selection"].is_file():
            shutil.copyfile(p["selection"], out / "input" / "selection.json")
        if kind == "writer" and (p["set"] / SEED_NAME).is_file():
            shutil.copyfile(p["set"] / SEED_NAME, out / SEED_NAME)
        target = out / "input" / "set"
        if target.exists():
            shutil.rmtree(target)
        os.makedirs(target)
        for f in delivered:
            shutil.copyfile(f, target / f.name)
        if kind == "writer":
            shutil.copyfile(notes, out / "input" / "notes.md")
    if kind == "writer":
        os.makedirs(out / ".claude", exist_ok=True)
        _write(out / ".claude" / "settings.json",
               (json.dumps(stop_hook(p, audit, repo, commit, out), indent=1) + "\n").encode("utf-8"))
    _write(out / "brief.md", text)
    digest = sha256_bytes(text)
    ledger.append(layout.make_run(p), "brief", kind=kind, round=rnd, commit=commit, brief_sha256=digest)
    emit(f"BRIEF {kind} round {rnd} {digest[:12]}")
    if kind == "writer":
        line = launch_command(out, repo)
        _write(out / LAUNCH_NAME, (line + "\n").encode("utf-8"))
        emit(f"LAUNCH writer {line}")
    return "ok"


def from_args(args, emit) -> str:
    return run(args.sets_root, args.audit, kind=args.kind, commit=args.commit, repo=args.repo, rnd=args.round,
               since=args.since, out=args.out, emit=emit)
