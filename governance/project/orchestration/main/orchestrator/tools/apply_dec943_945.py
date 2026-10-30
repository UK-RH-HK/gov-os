"""Applies DEC-943, DEC-944 and DEC-945 (drafts) to the register, the prompt (v3.40) and the lead brief, with the
ticket ids of W2-82 and W2-83 from log/tickets-2026-10-29b.json. Marks DEC-939 (item 7 reversed), DEC-941 (K9 gains
DEC-944's items), DEC-930 (a fifth weekly number) and DEC-742 (changed by DEC-942). Safe to re-run: each part checks
whether it is already done."""
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
REG = ROOT / "docs/DECISION_REGISTER.md"
PROMPT = ROOT / "governance/project/prompts/w2-orchestrator.md"
ids = json.loads((ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-29b.json").read_text())

reg = REG.read_text(encoding="utf-8")
if "### DEC-943 " not in reg:
    for dec, note in (
        ("DEC-939", "item 7 (Pushover) reversed by DEC-945"),
        ("DEC-941", "K9's entry criteria gain a Definition of Ready and stream playbooks (DEC-944)"),
        ("DEC-930", "a fifth weekly number, the orchestrator's drift (DEC-943 item 2)"),
        ("DEC-742", "the gate's values changed by DEC-942"),
    ):
        m = re.search(r"### " + dec + r" .*?\n- \*\*Status:\*\* [A-Z]+ \(", reg, re.S)
        if not m:
            sys.exit(dec + "'s status line not found")
        reg = reg[:m.end()] + note + "; " + reg[m.end():]
    add = (D / "DEC-943-944.md").read_text(encoding="utf-8")
    for w2 in ("W2-82", "W2-83a", "W2-83b"):
        add = add.replace("@@" + w2 + "@@", "`" + ids[w2] + "`")
    if "@@" in add:
        sys.exit("a placeholder left in DEC-943-944")
    for dec, note in (
        ("DEC-942", "item 1's launch order within DEC-946's priorities"),
        ("DEC-936", "item 2's priority line replaced by DEC-946"),
    ):
        m = re.search(r"### " + dec + r" .*?\n- \*\*Status:\*\* [A-Z]+ \(", reg, re.S)
        if not m:
            sys.exit(dec + "'s status line not found")
        reg = reg[:m.end()] + note + "; " + reg[m.end():]
    reg = (reg.rstrip("\n") + "\n" + add.rstrip("\n") + "\n" + (D / "DEC-945.md").read_text(encoding="utf-8").rstrip("\n")
           + "\n" + (D / "DEC-946.md").read_text(encoding="utf-8"))
    REG.write_text(reg, encoding="utf-8")
    print("register: DEC-943, DEC-944, DEC-945 appended; DEC-939, DEC-941, DEC-930, DEC-742 marked")

p = PROMPT.read_text(encoding="utf-8")
if "v3.40" not in p.split("\n", 1)[0]:
    EDITS = [
        ("v3.39: DEC-942)", "v3.39: DEC-942; v3.40: DEC-943 to DEC-946)"),
        ("- **The re-plan in force (owner, DEC-941, 2026-10-29; replaces DEC-831's slot order):**",
         "- **Standing priorities until EXAMIN's copy starts (owner, DEC-946; they order everything below):**\n"
         "  1. finish before you start: closing merged or built work comes before starting a new ticket (W2-57, W2-67, "
         "W2-71, the held merge-backs);\n"
         "  2. speed: W2-77, then the batch switched on and measured; W2-78; W2-76;\n"
         "  3. memory, the critical path: W2-61's baseline, then W2-03, W2-55, W2-64, W2-04, W2-05 and W2-06, W2-13, "
         "W2-15a, with the measure repeated after each;\n"
         "  4. K3 and K6 in parallel: W2-60a and W2-60b, W2-56, W2-21, W2-20;\n"
         "  5. the rest of EXAMIN's minimum: W2-81, W2-82 (light), W2-83a.\n"
         "  **Nothing else starts.** Every new idea goes to `docs/plan/WAVE_3_PARKING.md` unless it blocks EXAMIN's "
         "minimum, and the daily document says so; no ticket or package is drafted for it. The tools review's auditor, "
         "the STATE spot-check and W2-83b run in spare capacity only. If 18 November is at risk, bring what to cut, not "
         "a later date. Stagger lead launches by a minute or two (`tools/lead_chain2.sh`). The nightly is frozen: no "
         "more features or packages unless it breaks.\n"
         "- **The re-plan in force (owner, DEC-941, 2026-10-29; replaces DEC-831's slot order; ordered by DEC-946):**"),
        ("a stop, a compaction), and commit it (section 15, DEC-819, DEC-837).\n",
         "a stop, a compaction), and commit it (section 15, DEC-819, DEC-837).\n"
         "5. **Once W2-61's baseline and W2-55's and W2-04's closes are in (owner, DEC-943 item 2):** run `gov context` "
         "at every resume and before every decision that touches a standing rule, and act on what it returns. Every "
         "act against a standing decision is counted weekly (the fifth weekly number); until then, count them by hand "
         "from the owner's corrections and the slips list.\n"),
        ("there is no separate digest. **It reports (DEC-942 item 6):**",
         "there is no separate digest. **Brief gaps (DEC-943 item 1):** the leads' `brief_gaps:` sections go into "
         "`governance/project/orchestration/brief-gaps.md`; the common brief, the builder or a kernel skill (through "
         "CIT-P) is fixed the same week; the package says how many were found and how many fixed. **It reports (DEC-942 item 6):**"),
    ]
    for old, new in EDITS:
        if p.count(old) != 1:
            sys.exit("prompt: not found once: " + old[:60])
        p = p.replace(old, new)
    m = re.search(r"  - \*\*Emergencies \(DEC-938 item 6, DEC-939 item 7\):\*\*[^\n]*\n", p)
    if not m:
        sys.exit("prompt: the emergencies line not found")
    p = (p[:m.start()] + "  - **Emergencies (DEC-938 item 6, DEC-945):** first in the 07:30 morning package, from your own "
         "session; no push service. If a notifier is ever needed, bring the owner the free options as a package first, "
         "with any cost or install as a yes-or-no question.\n" + p[m.end():])
    anchor = "  **A known close-breaking row is fixed before the full closes it would hit"
    if p.count(anchor) != 1:
        sys.exit("prompt: the close-breaking-row anchor not found once")
    p = p.replace(anchor, "  **A Definition of Ready at every claim (owner, DEC-944 item 2):** until W2-82 (`" + ids["W2-82"] +
                  "`) checks it, check by hand before every claim that the ticket's sources resolve, its allowed paths, "
                  "KPIs, profile and acceptance-test path are set, and its dependencies are met; say so in the claim "
                  "commit.\n\n" + anchor)
    PROMPT.write_text(p, encoding="utf-8")
    print("prompt v3.40")
shutil.copyfile(D / "LEAD-w2-common.next.md", ROOT / "governance/project/briefs/LEAD-w2-common.md")
print("lead brief: brief_gaps section")
