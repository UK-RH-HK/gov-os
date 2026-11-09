"""W2-130 after the owner's sitting (DEC-1098 (3)): the final patches, against <repo>'s HEAD. Read-only on <repo>.

    python3 final_build.py <repo>

Reads the rulings from the sitting list the owner accepted, as HEAD holds it
(`governance/project/orchestration/packages/W2-130-SITTING.md`, groups A to G as proposed). Writes, in final/:

- f1-statuses.patch   the register: each decided status in its entry's own status line. The new status word goes
                      right after `**Status:** ` and the old text follows it whole ("…; it was ACCEPTED (owner, …)"),
                      as the register's own form already has it (DEC-798: "SUPERSEDED by DEC-1033 (…; it was
                      ACCEPTED …)"). Nothing is removed. The marks the rulings name ("mark Changed by …") are appended
                      at the line's end (DEC-866). The loader reads a status from its first word, so a status
                      appended at the end would change nothing it reads.
- f2-archive.patch    ARCHIVE-SUPERSEDED.md: §A's lines whose wording gives a wrong mark rewritten one statement a
                      line (H2: DEC-038, DEC-045, DEC-501/502); §B's lines for group F no longer call them spent
                      (DEC-729, DEC-786, DEC-924, DEC-927, DEC-928 in force; DEC-912, DEC-918 product record)
- f3-ticket-kpi4.patch  .tickets/DAEO-q8cl.md: KPI 4 to open and in-progress tickets (H1 (b)), marked
                      "[changed, DEC-1098 (3); DEC-1088 (6)]"
- f4-in-force.patch   DECISIONS-IN-FORCE.md: written only if f1 makes a listed id done or superseded
- f5-marks.patch      the marks gov links still proposes once f1 to f4 stand (a3 regenerated): the same rules as
                      build_patches.py (the audit's drops, the certainly-wrong drops), one diff on top of f1
- final-summary.json  the rulings, the counts, the head

f5 is made in a scratch clone (work/final-clone, `git clone --shared`): f1 to f4 are applied and committed there,
then build_patches.py runs on the clone and its batches are applied, and f5 is the clone's diff.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
OUT = HERE / "final"
CLONE = HERE / "work" / "final-clone"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
from gov.links import patch  # noqa: E402

REGISTER = "docs/DECISION_REGISTER.md"
ARCHIVE = "governance/project/orchestration/ARCHIVE-SUPERSEDED.md"
IN_FORCE = "governance/project/orchestration/DECISIONS-IN-FORCE.md"
TICKET = ".tickets/DAEO-q8cl.md"
SITTING = "governance/project/orchestration/packages/W2-130-SITTING.md"


def git(*args, cwd=ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


HEAD = git("rev-parse", "HEAD").strip()
at_head = {p: git("show", f"HEAD:{p}") for p in (REGISTER, ARCHIVE, IN_FORCE, TICKET, SITTING)}
for p in (REGISTER, ARCHIVE, IN_FORCE, TICKET):
    if (ROOT / p).read_text() != at_head[p]:
        sys.exit(f"{p} in the working tree differs from HEAD: commit or stash first")

# ---------------------------------------------------------------- the rulings, from the accepted sitting list
ROW = re.compile(r"^\| (DEC-\d+) \| [^|]* \| [^|]* \| \*\*(.+?)\*\* \| ([^|]+) \|", re.M)
rulings = {i: prop.strip() for i, prop, _ in ROW.findall(at_head[SITTING])}
if len(rulings) != 150:
    sys.exit(f"the sitting list gives {len(rulings)} rulings, not 150")

STAMP = "recorded by DEC-1098 (3)"


def insertion(i: str, prop: str) -> str | None:
    """The status word and its source, put before the old status text; None for no status change (group F)."""
    if prop == "DONE":
        return "DONE (owner, 2026-11-09, DEC-1098 (3)); it was "
    if prop.startswith("ACCEPTED (by DEC-083)"):
        return f"ACCEPTED (owner, 2026-09-30, DEC-083; {STAMP}); it was "
    if prop.startswith("ACCEPTED as realised"):
        return f"ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; {STAMP}); it was "
    if prop.startswith("SUPERSEDED by "):
        ids = prop.removeprefix("SUPERSEDED by ").strip()
        source = "DEC-074's tool choice" if i == "DEC-013" else "owner, 2026-09-30, DEC-083"
        return f"SUPERSEDED by {ids} ({source}; {STAMP}); it was "
    if prop.startswith("WITHDRAWN by DEC-842"):
        return f"WITHDRAWN by DEC-842 (owner, 2026-10-19; {STAMP}); it was "
    if prop.startswith("DEFERRED to Wave 3 (model routing)"):
        return f"DEFERRED to Wave 3, model routing (owner, 2026-09-30, DEC-083; {STAMP}); it was "
    if prop.startswith("DEFERRED to Wave 3"):
        return "DEFERRED to Wave 3 (owner, 2026-11-09, DEC-1098 (3)); it was "
    if prop.startswith(("In force", "Stays ACCEPTED")):
        return None
    sys.exit(f"{i}: no rule for the ruling {prop!r}")


def marks_named(prop: str) -> list[str]:
    """The changers a ruling names ("mark Changed by X, Y; …"), each with its part."""
    found = re.search(r"mark Changed by (.+?)(?:;|$)", prop)
    if not found:
        return []
    parts, depth, cur = [], 0, ""
    for ch in found.group(1):
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return [p for p in parts + [cur.strip()] if p]


from gov.store.loader import register_entries  # noqa: E402

entries = {e["id"]: e for e in register_entries(at_head[REGISTER])[0]}
lines = at_head[REGISTER].split("\n")
applied = {"status": {}, "marks": {}, "no_change": []}
for i, prop in rulings.items():
    e = entries[i]
    number = e["line"] + next(n for n, line in enumerate(e["span"].split("\n")[1:], 1) if line.strip())
    line = lines[number - 1]
    assert line == e["first"], i
    word = insertion(i, prop)
    if word:
        cut = line.index("**Status:**") + len("**Status:**")
        rest = line[cut:].lstrip(" ")
        line = line[:cut] + " " + word + rest
        applied["status"][i] = word.split(" ")[0]
    else:
        applied["no_change"].append(i)
    new_marks = [m for m in marks_named(prop) if not re.search(rf"\b{m.split(' ')[0]}(?![0-9])", e["first"])]
    if new_marks:
        line = line.rstrip() + " · **Changed by:** " + ", ".join(new_marks)
        applied["marks"][i] = new_marks
    lines[number - 1] = line
register_after = "\n".join(lines)
(OUT / "f1-statuses.patch").write_text(patch._diff(REGISTER, at_head[REGISTER], register_after))

# ---------------------------------------------------------------- f2: the archive (H2 and group F)
ARCHIVE_EDITS = {
    "- DEC-038: SUPERSEDED by DEC-048, itself superseded by DEC-051.":
        ["- DEC-038: SUPERSEDED by DEC-048; DEC-048's own successor is on its line."],
    "- DEC-045: amended by DEC-049, itself superseded by DEC-053 Q5.":
        ["- DEC-045: amended by DEC-049 (location of the originals); DEC-049's own fate is on its line."],
    "- DEC-501: corrected by DEC-502. DEC-502: corrected by DEC-512.":
        ["- DEC-501: corrected by DEC-502.", "- DEC-502: corrected by DEC-512."],
    "- DEC-729: the Wave 2 plan approved; W2-00. Spent.":
        ["- DEC-729: the Wave 2 plan approved; W2-00. In force until W2-00 closes (its item 3; DEC-1098 (3))."],
    "- DEC-786: stacked starts by rule. Spent, within DEC-942.":
        ["- DEC-786: stacked starts by rule. In force (item 1); its cap is DEC-942's (DEC-1098 (3))."],
    "- DEC-871, DEC-912, DEC-918, DEC-921: accepted history, merge rules, containment. Spent; feature lifted. "
    "DEC-912 and DEC-918 stay product record.":
        ["- DEC-871, DEC-921: accepted history, containment. Spent; feature lifted.",
         "- DEC-912, DEC-918: the merge rules. Product record (DEC-1098 (3))."],
    "- DEC-891, DEC-895, DEC-896, DEC-900, DEC-923, DEC-924, DEC-926, DEC-927, DEC-928: history entries, readers, "
    "work without a task, `Implements:`. Lifted or spent.":
        ["- DEC-891, DEC-895, DEC-896, DEC-900, DEC-923, DEC-926: history entries, readers, work without a task, "
         "`Implements:`. Lifted or spent.",
         "- DEC-924, DEC-927, DEC-928: their standing items stay in force: DEC-924 item 2, DEC-927 item 2 "
         "(LINK-INTEGRITY §5, DEC-1074 (7)), DEC-928 items 1 and 3 (DEC-1098 (3)). Their other items are finished."],
}
arch = at_head[ARCHIVE].split("\n")
for old, new in ARCHIVE_EDITS.items():
    if arch.count(old) != 1:
        sys.exit(f"ARCHIVE line not found once: {old[:60]}")
    at = arch.index(old)
    arch[at:at + 1] = new
archive_after = "\n".join(arch)
(OUT / "f2-archive.patch").write_text(patch._diff(ARCHIVE, at_head[ARCHIVE], archive_after))

# ---------------------------------------------------------------- f3: W2-130's KPI 4 (H1 (b))
KPI4_OLD = ("  - 'Tickets linked: every id a ticket''s KPI brackets name and every Implements: id of its worker commits is "
            "in its sources:, from gov links --propose-sources, in one commit that changes no other field; gov links "
            "--all then reports no UNLINKED_ID. Ids that name no record are listed per ticket in the record, for D-9 "
            "[DEC-1073 (5)(a)]'")
KPI4_NEW = ("  - 'Tickets linked, open and in-progress tickets only: every id an open or in-progress ticket''s KPI "
            "brackets name and every Implements: id of its worker commits is in its sources:, from gov links "
            "--propose-sources, in one commit that changes no other field; gov links --all then reports no UNLINKED_ID "
            "on an open or in-progress ticket. A closed ticket is not edited: its missing ids are listed per ticket in "
            "the record. Ids that name no record are listed per ticket in the record, for D-9 [DEC-1073 (5)(a)] "
            "[changed, DEC-1098 (3); DEC-1088 (6)]'")
if at_head[TICKET].count(KPI4_OLD + "\n") != 1:
    sys.exit("W2-130's KPI 4 is not as expected")
ticket_after = at_head[TICKET].replace(KPI4_OLD, KPI4_NEW)
# the new bracket names DEC-1098 and DEC-1088: they go in its sources: too, or the KPI cites ids it does not link
front_sources = re.search(r"^sources:\n((?:- .*\n)+)", ticket_after, re.M)
have = set(re.findall(r"DEC-\d+", front_sources.group(1))) if front_sources else set()
ticket_after = patch._with_sources(ticket_after, [i for i in ("DEC-1098", "DEC-1088") if i not in have])
(OUT / "f3-ticket-kpi4.patch").write_text(patch._diff(TICKET, at_head[TICKET], ticket_after))

# ---------------------------------------------------------------- f4: DECISIONS-IN-FORCE, only where f1 contradicts it
not_in_force = {i for i, w in applied["status"].items() if w in ("DONE", "SUPERSEDED", "WITHDRAWN", "DEFERRED")}
inf = at_head[IN_FORCE].split("\n")
lifted, clashes = False, []
for n, line in enumerate(inf):
    if line.startswith("## "):
        lifted = "lifted" in line.lower()
        continue
    if not lifted and line.startswith("- "):
        named = {"DEC-" + x for x in re.findall(r"\bDEC-(\d{3,})\b", line[2:].split(":")[0])}
        if named & not_in_force:
            clashes.append((n + 1, sorted(named & not_in_force), line))
(OUT / "f4-in-force.patch").write_text("")  # nothing to change unless clashes are found (reported, not guessed)

# ---------------------------------------------------------------- f5: the marks still proposed (a3 regenerated)
if CLONE.exists():
    shutil.rmtree(CLONE)
git("clone", "-q", "--shared", "--no-checkout", str(ROOT), str(CLONE))
git("checkout", "-q", "--detach", HEAD, cwd=CLONE)
for name in ("f1-statuses.patch", "f2-archive.patch", "f3-ticket-kpi4.patch"):
    git("apply", str(OUT / name), cwd=CLONE)
git("add", "-A", cwd=CLONE)
git("-c", "user.name=W2-130 final", "-c", "user.email=final@localhost", "commit", "-q", "-m",
    "W2-130 final: f1 to f3", "--trailer", "Task: DAEO-q8cl", "--trailer", "Role: orchestrator", "--trailer",
    "Implements: DEC-1098", cwd=CLONE)
built = HERE / "work" / "final-marks"
if built.exists():
    shutil.rmtree(built)
subprocess.run([sys.executable, str(HERE / "build_patches.py"), str(CLONE), str(built)], check=True,
               stdout=subprocess.DEVNULL, env={**os.environ, "W2130_AFTER_APPLY": "1"})
for name in ("a1-marks-no-hint.patch", "a2-marks-rest.patch", "a3-marks-after-sitting.patch"):
    if (built / name).read_text():
        git("apply", str(built / name), cwd=CLONE)
f5 = git("diff", "HEAD", "--", REGISTER, cwd=CLONE)
(OUT / "f5-marks.patch").write_text(f5)
marks = json.loads((built / "build-summary.json").read_text())
shutil.copy(built / "marks-audit.md", OUT / "f5-marks-audit.md")

summary = {"head": HEAD, "rulings": len(rulings), "status_changes_by_id": applied["status"],
           "status_changes": {w: sum(1 for x in applied["status"].values() if x == w)
                              for w in sorted(set(applied["status"].values()))},
           "no_status_change": applied["no_change"], "marks_named_by_rulings": applied["marks"],
           "archive_lines_rewritten": len(ARCHIVE_EDITS), "in_force_clashes": clashes,
           "f5": {"pairs": marks["marked_pairs"], "entries": len({l for l in f5.split("\n") if l.startswith("+-")}),
                  "dropped": marks["dropped_certainly_wrong"], "pre_check_flags": marks["audit"]["pre_check_flags"],
                  "free_text": marks["audit"]["free_text_marks"]}}
(OUT / "final-summary.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
