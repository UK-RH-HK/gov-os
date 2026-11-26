"""One run of the check: the standard, the repository and the plan read, the checks, one result (SL-5, SL-13)."""

from __future__ import annotations

import os
from pathlib import Path

from gov.layout import CannotRun, checks, moved, rewrites, standard
from gov.layout.namespaces import compile_map
from gov.layout.plan import digest, read
from gov.layout.repo import Repo
from gov.layout.standard import ASK


def run(root: Path, plan: Path, *, after_moves: bool = False) -> dict:
    """The result of checking the plan file ``plan`` against the repository ``root``; ``CannotRun`` otherwise."""
    root = Path(root).resolve()
    std = standard.load(root)
    try:
        text = Path(plan).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise CannotRun(f"the plan {plan} cannot be read: {type(error).__name__}") from None
    inside = os.path.relpath(Path(plan).resolve(), root)
    outside = inside == ".." or inside.startswith(".." + os.sep)
    repo = Repo(root, std, None if outside else Path(inside).as_posix())
    lines, findings, canonical = read(text, std)
    if after_moves:
        moved_findings, held, kept = moved.check(repo, std, lines)
        findings += moved_findings
        covered = {path: [] for path in repo.items}
        for line in lines:
            for path in line.items:
                covered[path].append(line)
        listed: list = []
        namespaces, imports, _ = compile_map(repo, std, lines, {entry["path"] for entry in held})
    else:
        covered = checks.covering(lines, repo.items)
        findings += checks.coverage(repo, covered, lines)
        findings += checks.kinds(repo, lines)
        findings += checks.place(repo, std, lines)
        findings += checks.imports_whole(repo, std, lines, covered)
        findings += checks.targets(repo, lines)
        listed, held, kept = rewrites.judge(repo, std, lines, covered)
        namespaces, imports, overlaps = compile_map(repo, std, lines, {entry["path"] for entry in held})
        findings += overlaps
    stoppers, scan_off = checks.stoppers(repo, covered)
    counts: dict[str, int] = {}
    for over in covered.values():
        name = over[0].cls if over else ""
        if name == ASK or name in std.classes:
            counts[name] = counts.get(name, 0) + 1
    asks = [{"path": line.path, "question": line.data["ask"]["question"],
             "recommended": line.data["ask"].get("recommended")}
            for line in lines if line.cls == ASK and isinstance(line.data.get("ask"), dict)
            and isinstance(line.data["ask"].get("question"), str)]
    result = {
        "findings": _sorted(findings), "stoppers": _sorted(stoppers), "rewrites": listed, "held": held, "kept": kept,
        "asks": sorted(asks, key=lambda each: (each["path"], each["question"])), "counts": dict(sorted(counts.items())),
        "commit": repo.commit, "standard": std.version, "hash": digest(canonical, std.version, repo.commit),
        "namespaces": namespaces, "imports": imports,
    }
    if scan_off:
        result["secrets_scan"] = scan_off
    return result


def _sorted(findings: list[dict]) -> list[dict]:
    return sorted(findings, key=lambda each: (each["path"], each["code"], each.get("other") or "",
                                              each.get("field") or "", each["line"] or 0))
