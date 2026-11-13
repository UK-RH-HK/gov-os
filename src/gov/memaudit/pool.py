"""``pool`` and ``pool-import``: the regression pool (Interface item 4; S7, F3).

After a measured audit the pool is re-run through the retrieval measure only (hit@5 and full evidence, no model tokens): the
whole pool while it holds 400 questions or fewer, else a seeded draw of 400, **the seed recorded first**. Its figures are
set beside the last audit's and a fall of 3 points or more in either is named a regression (printed, in ``POOL.json``,
exit 0). Then the audit's own kept questions join the pool, byte-equal. The pool is the flat folder
``<sets root>/fixtures/evaluation/memory-pool/hidden/<set>-<id>.yaml`` (hidden like a set); a draw is measured as the copied
set ``memory-pool-draw``. ``pool-import`` is the one-time import of the 79 of the fresh 80 and the 138 of the earlier sets,
run once by the CTO.
"""

from __future__ import annotations

import hashlib
import os
import random
import shutil
import tempfile
from fractions import Fraction
from pathlib import Path

import yaml

from gov.memaudit import declare, events, fault, layout, runner, scores, wrapper
from gov.memaudit.common import UsageError, read_json, set_digest, toplevel, write_whole

POOL_SET, DRAW_SET, DRAW_N = layout.POOL_SET, "memory-pool-draw", 400
FALL = Fraction(3, 100)  # a fall of 3 points or more is a regression
VERDICT_2, EARLIER = "memory-verdict-2", ("memory-retrieval", "memory-verdict")
IMPORT_PARTS = {VERDICT_2: ("hidden",), "memory-retrieval": ("visible", "hidden"), "memory-verdict": ("hidden",)}
WANT_VERDICT_2, WANT_EARLIER = 79, 138
LEFT_OUT_IDS = ("h24", "m60")  # the nonexistent-id questions of the earlier sets


def _names(folder: Path, audit: str | None) -> list[str]:
    """The pool's files (``*.yaml``, flat) in byte order of name, less the audit's own ``<audit>-*``."""
    if not folder.is_dir():
        return []
    return sorted((e.name for e in os.scandir(folder) if e.name.endswith(".yaml") and e.is_file()
                   and not (audit and e.name.startswith(f"{audit}-"))), key=lambda s: s.encode("utf-8"))


def _has_own(folder: Path, audit: str) -> bool:
    return folder.is_dir() and any(e.name.startswith(f"{audit}-") and e.name.endswith(".yaml") for e in os.scandir(folder))


def _digest(folder: Path, names: list[str]) -> str:
    """W2-170's rule over the named files only: ``set_digest`` of a folder holding links to them."""
    with tempfile.TemporaryDirectory(prefix="memaudit-pool-") as where:
        for name in names:
            os.symlink(folder / name, Path(where) / name)
        return set_digest(Path(where))


def _last_pool(p: dict) -> tuple[str | None, dict | None]:
    """The latest earlier audit's ``pool`` block of its ``FIGURES.json`` and its name."""
    runs = p["root"] / "runs"
    names = sorted((n for n in os.listdir(runs) if layout.AUDIT_RE.fullmatch(n) and n < p["run"].name), reverse=True) \
        if runs.is_dir() else []
    for name in names:
        doc = read_json(runs / name / "FIGURES.json")
        block = doc.get("pool") if isinstance(doc, dict) else None
        if isinstance(block, dict) and all(isinstance(block.get(k), int) for k in ("n", "hit5", "full")):
            return name, block
    return None, None


def _seed_of(audit: str, digest: str) -> int:
    return int(hashlib.sha256(f"{audit}\n{digest}".encode()).hexdigest()[:15], 16)


def choose(stems, seed: int) -> list[str]:
    """The draw: ``random.Random(seed).sample(sorted(stems), DRAW_N)``; the same seed gives the same draw."""
    return random.Random(seed).sample(sorted(stems), DRAW_N)


def _add_entries(p: dict, names: list[str]) -> None:
    """The sets root's own path map takes the entries (text insert, as W2-170's ``declare``); ``_plan_ok`` has said they fit."""
    for name in names:
        code, new = declare.plan_map(p, name)
        if code is None and new is not None:
            declare.write_map(p, new)


def _plan_ok(p: dict, names: list[str]) -> bool:
    """Whether the map can take every entry, nothing written (the entries are planned one after the other on a copy)."""
    with tempfile.TemporaryDirectory(prefix="memaudit-map-") as where:
        fake = {**p, "map": Path(where) / "path-map.yaml"}
        shutil.copyfile(p["map"], fake["map"])
        for name in names:
            code, new = declare.plan_map(fake, name)
            if code:
                return False
            if new is not None:
                fake["map"].write_text(new, encoding="utf-8")
    return True


def run(sets_root, audit, *, repo=None, gov=None, seed=None, emit) -> str:
    """The exit word: ``ok`` (a regression included), ``refused`` (``MS-``/``DC-MAP`` codes) or ``used``."""
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    gov = os.path.abspath(os.path.expanduser(str(gov) if gov is not None else "~/.local/bin/gov"))
    for flag in (repo, gov):
        if layout.inside(flag, p["root"]):
            raise UsageError("flag inside the sets root")
    run_dir = p["run"]
    figures = read_json(run_dir / "FIGURES.json")
    if not isinstance(figures, dict):
        emit("MS-NOFIGURES")
        return "refused"
    if os.path.lexists(run_dir / "POOL.json"):
        emit("USED")
        return "used"
    decl = read_json(p["declaration"])
    if not isinstance(decl, dict) or set_digest(p["hidden"]) != decl.get("set_digest"):
        emit("MS-DIGEST")
        return "refused"
    if declare.gov_pin(gov) != decl.get("gov_pin"):
        emit("MS-PIN")
        return "refused"

    folder = p["pool"]
    names = _names(folder, audit)
    size = len(names)
    digest = _digest(folder, names)
    seed = int(seed) if seed is not None else _seed_of(audit, digest)
    drawn = min(size, DRAW_N)
    # a draw is measured as a copied set; so is a pool that already holds files of this audit's own (they are not the
    # pool: measuring the folder would count them), which only a hand-removed POOL.json can leave
    copied = size > DRAW_N or _has_own(folder, audit)
    sets = [POOL_SET] + ([DRAW_SET] if copied else [])
    if not _plan_ok(p, sets):
        emit("DC-MAP")
        return "refused"
    _add_entries(p, sets)
    folder.mkdir(parents=True, exist_ok=True)
    # the seed is recorded first: before any search
    write_whole(run_dir, "POOL.json", {"size": size, "drawn": drawn, "seed": seed, "digest": digest})
    events.append(run_dir, "pool", state="seed", seed=seed, size=size, drawn=drawn, digest=digest)

    draw_dir = p["root"] / layout.EVALUATION / DRAW_SET
    set_name = POOL_SET
    try:
        if copied:
            stems = [n[:-len(".yaml")] for n in names]
            chosen = choose(stems, seed) if size > DRAW_N else stems
            if os.path.lexists(draw_dir):
                shutil.rmtree(draw_dir)
            os.makedirs(draw_dir / "hidden")
            for stem in chosen:
                shutil.copyfile(folder / f"{stem}.yaml", draw_dir / "hidden" / f"{stem}.yaml")
            set_name = DRAW_SET
        pool_run = run_dir / "pool"
        try:
            runner.start(pool_run)
        except FileExistsError:
            emit("MS-POOLFAULT")
            return "refused"
        shim = wrapper.install(run_dir, gov)
        rc = runner.measure(set_name, "hidden", repo=repo, root=p["root"], folder=pool_run, wrapper=shim, run=run_dir,
                            phase="pool", attempt=None)
    finally:
        if os.path.lexists(draw_dir):
            shutil.rmtree(draw_dir)
    counting = run_dir / (_text_of(run_dir / "COUNTS") or "attempt-1")
    families = fault.read_parsed(counting)["families"]
    cause = "exit" if rc != 0 else fault.not_whole(pool_run, drawn, families)
    if cause is not None:
        events.append(run_dir, "pool", state="fault", seed=seed, size=size, drawn=drawn, digest=digest)
        emit("MS-POOLFAULT")
        return "refused"
    parsed = fault.read_parsed(pool_run)
    n = len(parsed["questions"])
    hit5, full = (sum(1 for q in parsed["questions"] if q[k]) for k in ("hit5", "full"))
    last_audit, last = _last_pool(p)
    regress = []
    if last and n and last["n"]:
        for word, now, before in (("hit@5", hit5, last["hit5"]), ("full evidence", full, last["full"])):
            if Fraction(before, last["n"]) - Fraction(now, n) >= FALL:
                regress.append((word, 100 * before / last["n"], 100 * now / n))
    block = {"n": n, "hit5": hit5, "full": full, "last_audit": last_audit,
             "last_hit5": last["hit5"] if last else None, "last_full": last["full"] if last else None,
             "regression": bool(regress)}
    write_whole(run_dir, "POOL.json", {"size": size, "drawn": drawn, "seed": seed, "digest": digest, **block})
    figures["pool"] = block
    write_whole(run_dir, "FIGURES.json", figures)
    events.append(run_dir, "pool", state="done", seed=seed, size=size, drawn=drawn, digest=digest)
    beside = (f"last audit {last_audit}: hit@5 {last['hit5']} of {last['n']} ({scores.pct(last['hit5'], last['n'])}); "
              f"full evidence {last['full']} ({scores.pct(last['full'], last['n'])})") if last else "no earlier audit"
    emit(f"POOL {n} of {size}: hit@5 {hit5} ({scores.pct(hit5, n)}); full evidence {full} ({scores.pct(full, n)}); "
         f"{beside}")
    for word, before, now in regress:
        emit(f"POOL REGRESSION {word} {before:.1f} -> {now:.1f} %")
    # the audit's own kept questions join the pool, byte-equal; a present equal file is skipped
    folder.mkdir(parents=True, exist_ok=True)
    for src in sorted(p["hidden"].glob("*.yaml")):
        try:
            data = yaml.safe_load(src.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            data = None
        if isinstance(data, dict) and data.get("category") == scores.APART:
            continue
        dest = folder / f"{audit}-{src.stem}.yaml"
        if os.path.lexists(dest):
            if dest.read_bytes() != src.read_bytes():
                emit("MS-POOLDIFF")
                return "refused"
            continue
        shutil.copyfile(src, dest)
    return "ok"


def _text_of(path: Path) -> str | None:
    try:
        return Path(path).read_text().strip() or None
    except OSError:
        return None


def importing(sets_root, *, emit) -> str:
    """The one-time import: ``refused`` (``MS-IMPORTED``, ``MS-IMPORTCOUNT``, ``MS-POOLDIFF``) or ``ok``."""
    root = layout.root_of(sets_root)
    evaluation = root / layout.EVALUATION
    run_dir = root / "runs" / POOL_SET
    if os.path.lexists(run_dir / "IMPORTED.json"):
        emit("MS-IMPORTED")
        return "refused"
    plan, counts = {}, {VERDICT_2: 0, "earlier": 0}
    for name, parts in IMPORT_PARTS.items():
        for part in parts:
            folder = evaluation / name / part
            for src in sorted(folder.glob("*.yaml")) if folder.is_dir() else []:
                try:
                    data = yaml.safe_load(src.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, yaml.YAMLError):
                    data = None
                data = data if isinstance(data, dict) else {}
                if data.get("category") == scores.APART or str(data.get("id", src.stem)) in LEFT_OUT_IDS \
                        or src.stem in LEFT_OUT_IDS:
                    continue
                dest = f"{name}-{src.stem}.yaml"
                if dest in plan:  # two questions for one name: the count cannot be right
                    emit("MS-IMPORTCOUNT")
                    return "refused"
                plan[dest] = src
                counts[VERDICT_2 if name == VERDICT_2 else "earlier"] += 1
    if counts[VERDICT_2] != WANT_VERDICT_2 or counts["earlier"] != WANT_EARLIER:
        emit("MS-IMPORTCOUNT")
        return "refused"
    folder = evaluation / POOL_SET / "hidden"
    if any(os.path.lexists(folder / d) and (folder / d).read_bytes() != src.read_bytes() for d, src in plan.items()):
        emit("MS-POOLDIFF")
        return "refused"
    folder.mkdir(parents=True, exist_ok=True)
    for d, src in plan.items():
        if not os.path.lexists(folder / d):
            shutil.copyfile(src, folder / d)
    if not run_dir.is_dir():
        os.makedirs(run_dir.parent, exist_ok=True)
        os.mkdir(run_dir, 0o700)
        os.chmod(run_dir, 0o700)
    write_whole(run_dir, "IMPORTED.json", {"counts": counts, "total": len(plan), "digest": set_digest(folder)})
    emit(f"IMPORTED {len(plan)}: {counts[VERDICT_2]} of the fresh 80, {counts['earlier']} of the earlier sets")
    return "ok"
