"""Files the re-plan's tickets of 2026-10-29 (DEC-941): `tk create` gives each its id and created time, then the
draft is written in its place with those filled in, the drafting notes (lines starting "# proposed:") left out,
W2-60b's depends_on given W2-60a's id, and the plan's cards given their ticket ids. Writes the W2 -> id map to
log/tickets-2026-10-29.json. Stops before any write if a draft still holds a placeholder it cannot fill."""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
MAP = ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-29.json"
WBS = ROOT / "docs/plan/WAVE_2_WBS.md"
# W2 id -> (draft, header for drafts without one: assignee, tags)
ORDER = [
    ("W2-77", D / "ticket-W2-77.md", ("engineer", "[wave-2, implementation, full, nightly, close]")),
    ("W2-61", D / "tickets/W2-61.md", None),
    ("W2-61h", D / "tickets/W2-61h.md", None),
    ("W2-60a", D / "tickets/W2-60a.md", None),
    ("W2-56", D / "tickets/W2-56.md", None),
    ("W2-76", D / "ticket-W2-76.md", ("engineer", "[wave-2, implementation, standard, rebuild]")),
    ("W2-78", D / "tickets/W2-78.md", None),
    ("W2-55", D / "tickets/W2-55.md", None),
    ("W2-64", D / "tickets/W2-64.md", None),
    ("W2-60b", D / "tickets/W2-60b.md", None),
    ("W2-79", D / "tickets/W2-79.md", None),
    ("W2-80", D / "tickets/W2-80.md", None),
    ("W2-81", D / "tickets/W2-81.md", None),
]
if MAP.exists():
    sys.exit("already filed: " + MAP.read_text())


def body(w2, draft, header):
    text = draft.read_text(encoding="utf-8")
    text = "\n".join(l for l in text.splitlines() if not l.startswith("# proposed:")).rstrip("\n") + "\n"
    if header:
        assignee, tags = header
        text = ("---\nid: ID-PLACEHOLDER\nstatus: open\ndeps: []\nlinks: []\ncreated: CREATED-PLACEHOLDER\n"
                "type: task\npriority: 1\nassignee: " + assignee + "\nexternal-ref: " + w2 + "\ntags: " + tags + "\n"
                + text.lstrip("\n"))
    return text


texts = {w2: body(w2, d, h) for w2, d, h in ORDER}
for w2, t in texts.items():
    if not t.startswith("---\nid: ID-PLACEHOLDER\n") or "CREATED-PLACEHOLDER" not in t:
        sys.exit(w2 + ": header not as expected")
    rest = t.replace("id: ID-PLACEHOLDER", "", 1).replace("ID-PLACEHOLDER-W2-60a", "")
    if "PLACEHOLDER" in rest.replace("CREATED-PLACEHOLDER", "", 1):
        sys.exit(w2 + ": a placeholder the script cannot fill")
ids = {}
for w2, draft, _ in ORDER:
    title = re.search(r"^title: '(.*)'$", texts[w2], re.M).group(1).replace("''", "'")
    out = subprocess.run(["tk", "create", title, "-p", "1", "--external-ref", w2], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (out + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    ids[w2] = out
    t = texts[w2].replace("id: ID-PLACEHOLDER", "id: " + out, 1).replace("CREATED-PLACEHOLDER", created, 1)
    if w2 == "W2-60b":
        t = t.replace("ID-PLACEHOLDER-W2-60a", ids["W2-60a"])
    path.write_text(t, encoding="utf-8")
    print(w2, out)
MAP.write_text(json.dumps(ids, indent=1) + "\n", encoding="utf-8")
# The plan's new cards name their ticket files.
wbs = WBS.read_text(encoding="utf-8")
for w2 in ("W2-79", "W2-80", "W2-81"):
    head = "#### " + w2 + " "
    i = wbs.index(head)
    j = wbs.index("Ticket file `ID-PLACEHOLDER`", i)
    if wbs.find("#### ", i + 5) < j:
        sys.exit(w2 + ": its card's placeholder not found inside the card")
    wbs = wbs[:j] + "Ticket file `" + ids[w2] + "`" + wbs[j + len("Ticket file `ID-PLACEHOLDER`"):]
for w2 in ("W2-60a", "W2-60b", "W2-61h", "W2-76", "W2-77", "W2-78"):
    head = "#### " + w2 + " "
    if head in wbs:
        end = wbs.index("\n", wbs.index(head))
        wbs = wbs[:end] + "\n- **Ticket file:** `" + ids[w2] + "`." + wbs[end:]
if "PLACEHOLDER" in wbs:
    sys.exit("the plan still holds a placeholder")
WBS.write_text(wbs, encoding="utf-8")
print("cards updated")
