"""DEC-944: files W2-82 and W2-83 (tk create gives id and created time; the drafts are written in place), adds their
cards and K9's two new entry criteria to the plan, writes the company mapping into packages/ with the ticket ids, and
starts the brief-gaps register (DEC-943). Writes log/tickets-2026-10-29b.json. Run only when no close queue runs."""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
MAP = ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-29b.json"
WBS = ROOT / "docs/plan/WAVE_2_WBS.md"
if MAP.exists():
    sys.exit("already filed: " + MAP.read_text())
ids = {}
for w2 in ("W2-82", "W2-83a", "W2-83b"):
    text = (D / "tickets" / (w2 + ".md")).read_text(encoding="utf-8")
    if "# proposed:" in text or text.count("ID-PLACEHOLDER") != 1 or text.count("CREATED-PLACEHOLDER") != 1:
        sys.exit(w2 + ": draft not as expected")
    title = re.search(r"^title: '(.*)'$", text, re.M).group(1).replace("''", "'")
    tid = subprocess.run(["tk", "create", title, "-p", "1", "--external-ref", w2], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    path.write_text(text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created), encoding="utf-8")
    ids[w2] = tid
    print(w2, tid)
MAP.write_text(json.dumps(ids, indent=1) + "\n", encoding="utf-8")

wbs = WBS.read_text(encoding="utf-8")
cards = (D / "tickets/cards-82-83.md").read_text(encoding="utf-8").strip()
for w2, tid in ids.items():
    head = "#### " + w2 + " "
    i = cards.index(head)
    end = cards.index("\n", i)
    cards = cards[:end] + "\n- **Ticket file:** `" + tid + "`." + cards[end:]
anchor = "## 3. Order, layers and critical path"
if wbs.count(anchor) != 1:
    sys.exit("plan: section 3 not found once")
wbs = wbs.replace(anchor, "### DEC-944: the Definition of Ready and the stream playbooks (EXAMIN minimum)\n\n" + cards + "\n\n" + anchor)
k9 = ("  - Wave 2-grade evidence (a clean close, the memory measure, or the proving ground) for every capability the copy "
      "relies on, not only Wave 1's record.\n")
if wbs.count(k9) != 1:
    sys.exit("plan: K9's last copy criterion not found once")
wbs = wbs.replace(k9, k9 + "  - a Definition of Ready checked at claim (W2-82, `" + ids["W2-82"] + "`) and a playbook per stream in "
                  "the kernel template (W2-83a, `" + ids["W2-83a"] + "`) (owner, DEC-944 items 2 and 3).\n")
WBS.write_text(wbs, encoding="utf-8")

m = (D / "COMPANY-MAP-2026-10-29.md").read_text(encoding="utf-8")
m = m.replace("W2-82 (being filed; no DAEO id yet)", "W2-82 (`" + ids["W2-82"] + "`)")
m = m.replace("W2-83 (being filed; no DAEO id yet)", "W2-83a (`" + ids["W2-83a"] + "`; EXAMIN minimum) and W2-83b (`"
              + ids["W2-83b"] + "`; spare capacity)")
if "being filed" in m:
    sys.exit("map: a ticket cell left unfilled")
(ROOT / "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md").write_text(m, encoding="utf-8")

gaps = ROOT / "governance/project/orchestration/brief-gaps.md"
if not gaps.exists():
    gaps.write_text(
        "# Brief gaps (DEC-943)\n\n"
        "What a lead or its workers had to discover, look up or ask that the brief, the ticket or the skills did not "
        "tell them, from each lead's `brief_gaps:` section. The orchestrator fixes the common brief, the brief builder "
        "or a kernel skill (through CIT-P, CAP-33) the same week; W2-79's tests keep each fix in place. The daily "
        "document reports the count found and fixed.\n\n"
        "| Date | Ticket | Gap | Where it belonged | Minutes | Fixed by |\n|---|---|---|---|---|---|\n",
        encoding="utf-8")
print("plan cards and K9, the mapping, the brief-gaps register")
