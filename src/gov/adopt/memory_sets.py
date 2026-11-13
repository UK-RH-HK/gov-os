"""The set tools of an adopted repository's memory audit (W2-88 S18 to S23; DEC-1101, DEC-1099 (2), DEC-1125 (2)).

One core, not two (S20): the pre-flight, the declaration with its use-once marker, the figures, the schedule and the
pool are ``gov.memaudit``'s (W2-170, W2-171, W2-172), imported here and carried in no copy. This module defines none
of them. It provides what adoption writes for the repository's owner and operator, and starts nothing:

- ``audit_record`` (S18): the repository's audit record, with its sets root, audit names, mode, the three briefs'
  variant ids and their sha256, and the first audit's earliest date; ``due`` says ``not due: no verdict set used``
  until the verdict set (S13) is used (``python3 -m gov.memaudit due|baseline`` is unchanged).
- ``variants`` (S19): the Gov OS briefs with two parts replaced by the repository's own, the domain table and the list
  of records the audit stays blind to; every other byte is the Gov OS brief's.
- ``walls_act`` (S22): one ACT package for the repository's owner's operator, never applied here.
- ``cost`` (S23): the audit's cost for the set's size, from MEMORY-AUDIT-1.md section 7.
- ``launch_check`` (S19): exit 10 for a variant whose sha256 is not on the approved list.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import timedelta
from pathlib import Path

from gov.memaudit import declare, figures, layout, pool, preflight, schedule

CORE = (preflight, declare, layout, figures, schedule, pool)  # the one core (S20): imported, never restated here
GOV_OS = Path(__file__).resolve().parents[3]
BRIEFS = "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs"
WALLS = "governance/project/indep-walls"
KINDS = ("writer", "checker", "auditor")
CATEGORIES = ("decision", "contract", "plan", "ticket", "exact-string", "callers", "code-paraphrase",
              "kernel-template", "multi-file", "failure-memory", "history", "nonexistent-id")
NOT_DUE = "not due: no verdict set used"
EXIT_UNAPPROVED = 10  # the exit code of a launch under a variant the owner has not approved
REFRESH = "gov rebuild --integration <branch>"  # S11: installed through the ACT, never by the tool
# The audit's cost for 40 questions (MEMORY-AUDIT-1.md section 7, basis E): about $30 with round 2, 35 GPU minutes
# (10 for the set and its control, 25 for the pool at first), the owner's 5 minutes a week. The tokens follow from the
# dollars at an assumed blended list price; the first audit measures them all and replaces these.
COST_BASIS_N = 40
USD_PER_AUDIT = 30.0
USD_PER_MILLION_TOKENS = 15.0
GPU_MINUTES_SET, GPU_MINUTES_POOL, OWNER_MINUTES = 10.0, 25.0, 5


def cost(n_questions: int) -> dict:
    """``{tokens, usd, gpu_minutes, owner_minutes, replace_after}`` for a set of ``n_questions`` (linear in the set)."""
    scale = n_questions / COST_BASIS_N
    usd = round(USD_PER_AUDIT * scale, 2)
    return {"tokens": int(usd / USD_PER_MILLION_TOKENS * 1_000_000), "usd": usd,
            "gpu_minutes": round(GPU_MINUTES_SET * n_questions / 80 + GPU_MINUTES_POOL, 1),
            "owner_minutes": OWNER_MINUTES, "n_questions": n_questions, "source": "MEMORY-AUDIT-1.md section 7 (E)",
            "replace_after": "the first audit's measured spend, GPU time and owner minutes (the spend log)"}


# ---- the variants

def _span(text: str, start: str, stop: str) -> tuple[int, int]:
    """The offsets of the part of ``text`` from the line starting ``start`` up to the line starting ``stop``."""
    begin = re.search(rf"(?m)^{re.escape(start)}", text)
    end = re.search(rf"(?m)^{re.escape(stop)}", text[begin.end():]) if begin else None
    if begin is None or end is None:
        raise ValueError(f"the brief has no part from {start!r} to {stop!r}")
    return begin.start(), begin.end() + end.start()


def _table(domains: dict[str, str], dropped: list[str]) -> str:
    rows = "\n".join(f"| `{category}` | {domains.get(category, 'dropped')} |" for category in CATEGORIES)
    left = ", ".join(dropped) or "none"
    return (f"| category | the repository's domain |\n|---|---|\n{rows}\n\nCategories dropped for want of a domain "
            f"(recorded): {left}.\n")


def _blind(blind: list[str]) -> str:
    listed = "\n".join(f"- `{path}`" for path in blind) or "- none declared"
    return f"The records this audit stays blind to (the repository's own list):\n\n{listed}\n"


def _replace(text: str, start: str, stop: str, new: str) -> str:
    begin, end = _span(text, start, stop)
    return text[:begin] + new + "\n" + text[end:]


def variants(briefs: Path, domains: dict[str, str], blind: list[str], dropped: list[str] | None = None) -> dict:
    """The three briefs as the repository's variants: kind -> ``{id, text, sha256}``. Only two parts differ from the
    Gov OS brief at ``briefs`` (a folder of ``writer.md``, ``checker.md`` and ``auditor.md``): the domain table (the
    writer's section 5 items 1 and 3, the checker's section 5a) and the blind list (a block added to section 4)."""
    dropped = sorted(dropped if dropped is not None else [c for c in CATEGORIES if c not in domains])
    out = {}
    for kind in KINDS:
        text = (Path(briefs) / f"{kind}.md").read_text(encoding="utf-8")
        if kind == "writer":
            text = _replace(text, "1. **Size and categories.**", "2. **Where they come from",
                            "1. **Size and categories.** (the repository's own domain table)\n\n" + _table(domains, dropped))
            text = _replace(text, "3. **The set's spread**", "4. **The rubric",
                            "3. **The set's spread** (the repository's own domains)\n\n" + _table(domains, dropped))
        elif kind == "checker":
            text = _replace(text, "### 5a.", "## 6.", "### 5a. The set (R5), counted from the questions as you judge them "
                            "(the repository's own domains)\n\n" + _table(domains, dropped))
        begin, end = _span(text, "## 4.", "## 5.")  # the blind list closes section 4 and nothing else of it moves
        text = text[:end] + _blind(blind) + "\n" + text[end:]
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        out[kind] = {"id": f"{kind}-v1-{digest[:12]}", "text": text, "sha256": digest}
    return out


# ---- the audit record (S18)

def audit_record(out: Path, *, sets_root: str, audits: list[str], made: dict, today=None) -> dict:
    """Write ``<out>/memory-audit/AUDIT-RECORD.json``: the repository's sets root, audit names, mode, the variant ids
    and sha256 and the first audit's earliest date. It starts no audit and writes no schedule line."""
    today = today or schedule.now()
    record = {"sets_root": sets_root, "audit_names": audits, "mode": "weekly",
              "mode_rule": f"weekly while active, monthly once stable (gov.memaudit.schedule: {schedule.WEEKLY_DAYS} "
                           f"days, then {schedule.MONTHLY_DAYS})",
              "variants": {kind: {"id": item["id"], "sha256": item["sha256"]} for kind, item in made.items()},
              "first_audit_earliest": (today + timedelta(days=schedule.WEEKLY_DAYS)).strftime("%Y-%m-%d"),
              "due": NOT_DUE,
              "first_audit_follows": "the verdict set (S13): its use-once marker and result record; then "
                                     "`python3 -m gov.memaudit baseline`"}
    folder = Path(out) / "memory-audit"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "AUDIT-RECORD.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


# ---- the walls' ACT (S22)

def walls_act(out: Path, *, sets_root: str, audit: str, made: dict, blind: list[str]) -> Path:
    """Write ``<out>/memory-audit/ACT-WALLS/``: the walls' template copy, the sets root's spec (mode 0700), the
    approved list with the three variant briefs, the path map's hidden globs and the refresh the operator installs.
    Nothing is applied: no folder is made at the sets root, no path map and no crontab is changed."""
    act = Path(out) / "memory-audit" / "ACT-WALLS"
    (act / "walls").mkdir(parents=True, exist_ok=True)
    for source in sorted((GOV_OS / WALLS).glob("*")):
        if source.is_file():
            (act / "walls" / source.name).write_bytes(source.read_bytes())
    (act / "sets-root.json").write_text(json.dumps({"path": sets_root, "mode": "0700", "create": True}, indent=2) + "\n",
                                        encoding="utf-8")
    (act / "approved.txt").write_text("".join(f"{item['sha256']}  {item['id']}\n" for item in made.values()),
                                      encoding="utf-8")
    (act / "briefs").mkdir(exist_ok=True)
    for kind, item in made.items():
        (act / "briefs" / f"{kind}.md").write_text(item["text"], encoding="utf-8")
    entry = declare.entry_of(audit)
    (act / "hidden-globs.txt").write_text("".join(f"{glob}\n" for glob in entry["hidden"]), encoding="utf-8")
    (act / "blind-list.txt").write_text("".join(f"{path}\n" for path in blind), encoding="utf-8")
    (act / "ACT.md").write_text(
        "# ACT: the walls for this repository's memory audit (for the owner's operator; not applied by adoption)\n\n"
        f"1. Copy `walls/` to the repository's `{WALLS}/`.\n"
        f"2. Make the sets root `{sets_root}` with mode 0700 (`sets-root.json`).\n"
        "3. Put `approved.txt` beside the briefs the owner approves (`briefs/`): a launch under a variant not on it exits "
        f"{EXIT_UNAPPROVED}.\n"
        f"4. Add `hidden-globs.txt`'s globs to the path map's `evaluation_sets` (`{audit}`), every role but the "
        "orchestrator refused.\n"
        f"5. Install the refresh the operator runs after each update of the integration branch: `{REFRESH}` "
        "(W2-116), with the daily backstop.\n", encoding="utf-8")
    return act


# ---- the launch check (S19)

def launch_check(variant: Path, approved: Path) -> int:
    """0 when the sha256 of ``variant`` is on the ``approved`` list (a hex digest at the start of a line), else 10."""
    try:
        digest = hashlib.sha256(Path(variant).read_bytes()).hexdigest()
        listed = {row.split()[0] for row in Path(approved).read_text(encoding="utf-8").splitlines() if row.strip()}
    except (OSError, UnicodeDecodeError):
        return EXIT_UNAPPROVED
    return 0 if digest in listed else EXIT_UNAPPROVED


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 5 and args[0] == "launch-check" and args[1] == "--variant" and args[3] == "--approved":
        return launch_check(Path(args[2]), Path(args[4]))
    if len(args) == 3 and args[0] == "launch-check":
        return launch_check(Path(args[1]), Path(args[2]))
    print("usage: python3 -m gov.adopt.memory_sets launch-check --variant <file> --approved <file>", file=sys.stderr)
    return 4


if __name__ == "__main__":
    sys.exit(main())
