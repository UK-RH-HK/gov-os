"""W2-130 (DEC-1097 (9), DEC-1074 (7) O2): the facts behind the owner's reconciliation list. Read-only.

    PYTHONPATH=src python3 sitting_data.py <repo> <out.json>

Per id of the list (the 110 decisions ARCHIVE-SUPERSEDED §B calls spent while the register lists them current, the
PROPOSED register entries, and every other STATUS_CONFLICT gov links finds): its title, status line, the archive's
words, the changers the register or archive states, whether DECISIONS-IN-FORCE lists it, which open tickets rest on it
(sources: or KPI brackets) and which later entries cite it. Reads HEAD through gov.links.check; writes only <out.json>.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
sys.path.insert(0, str(ROOT / "src"))
from gov.links import check  # noqa: E402
from gov.store import loader  # noqa: E402

repo = check._Repo(ROOT)
statements = check._statements(repo)
archive = repo.files[check.ARCHIVE_REL]
in_force = repo.files[check.IN_FORCE_REL]
DEC = re.compile(r"\bDEC-(\d{3,})\b")


def num(record_id):
    return int(record_id.split("-")[1])


# the spent set, as the drift script reads it (everything after "## B.", so §C's "DEC-038 to DEC-063 ... Spent"
# brings DEC-063) and as gov links reads it (§B only)
spent_line = {}
for line in archive.split("## B.", 1)[-1].split("\n"):
    if line.startswith("- DEC-") and re.search(r"\b[Ss]pent\b", line):
        for named in DEC.findall(line[2:].split(":")[0]):
            spent_line.setdefault("DEC-" + named, line[2:].strip())
a_line = {}
for line in archive.split("## B.", 1)[0].split("\n"):
    if line.startswith("- DEC-"):
        for named in DEC.findall(line[2:].split(":")[0]):
            a_line.setdefault("DEC-" + named, line[2:].strip())


def current(record_id):
    return repo.status.get(record_id) == "ACCEPTED"


in_force_lines = {}
lifted = False
for number, line in enumerate(in_force.split("\n"), 1):
    if line.startswith("## "):
        lifted = "lifted" in line.lower()
        continue
    for named in DEC.findall(line):
        in_force_lines.setdefault("DEC-" + named, []).append(("lifted" if lifted else "in force", number,
                                                               line.strip()[:200]))

open_rest = {}
for path, front in repo.tickets:
    if front.get("status") not in ("open", "in_progress"):
        continue
    named = set(str(v) for v in (front.get("sources") or []))
    for kpi in check._kpi_lines(front):
        named |= {"DEC-" + n for n in DEC.findall(kpi)}
    for record_id in named:
        open_rest.setdefault(record_id, []).append(f"{front.get('external-ref') or front.get('wbs_id')} ({front['id']})")

cited_by = {}
for entry in repo.entries:
    for named in set(DEC.findall(entry["span"])):
        record_id = "DEC-" + named
        if record_id != entry["id"]:
            cited_by.setdefault(record_id, []).append(entry["id"])

changers = {}
for statement in statements:
    if statement["cls"] in check.CHANGE_CLASSES and statement["source"] != statement["target"]:
        changers.setdefault(statement["target"], set()).add(
            (statement["source"], statement["where"], statement["form"]))

ids = sorted({i for i in spent_line if current(i)}, key=num)
proposed = [e["id"] for e in repo.entries if repo.status.get(e["id"]) == "PROPOSED"]
rows = []
for record_id in ids + proposed:
    entry = repo.entry[record_id]
    rows.append({
        "id": record_id, "group": "spent" if record_id in ids else "proposed", "title": entry["title"],
        "line": entry["line"], "status_line": entry["first"], "archive_B": spent_line.get(record_id),
        "archive_A": a_line.get(record_id),
        "changers": sorted(({"source": s, "where": w, "form": f} for s, w, f in changers.get(record_id, ())),
                           key=lambda c: num(c["source"])),
        "in_force_list": in_force_lines.get(record_id, []), "open_tickets": sorted(open_rest.get(record_id, [])),
        "cited_by_later": sorted((c for c in cited_by.get(record_id, []) if c.startswith("DEC-")), key=num)[-8:],
        "cited_by_count": len(cited_by.get(record_id, [])),
        "span_head": entry["span"][:900],
    })
OUT.write_text(json.dumps({"spent": len(ids), "proposed": len(proposed), "rows": rows}, indent=1))
print(f"spent {len(ids)}, proposed {len(proposed)} -> {OUT}")
