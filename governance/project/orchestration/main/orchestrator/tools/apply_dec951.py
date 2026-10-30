"""DEC-951: appends it, marks DEC-938, brings the prompt to v3.44 (items A and B), widens W2-05 and W2-60a, adds W2-11's
test-proportion KPI, files W2-85 with its card. Writes log/tickets-2026-10-30.json. Parses every edited ticket."""
import json
import pathlib
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
T = ROOT / ".tickets"


def edit(p, pairs):
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in t:
            continue
        if t.count(old) != 1:
            sys.exit(p.name + ": not found once: " + old[:70])
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")


reg = ROOT / "docs/DECISION_REGISTER.md"
r = reg.read_text(encoding="utf-8")
if "### DEC-951 " not in r:
    m = re.search(r"### DEC-938 .*?\n- \*\*Status:\*\* [A-Z]+ \(", r, re.S)
    r = r[:m.end()] + "the hold after a red nightly and the schedule refined by DEC-951 items A and B; " + r[m.end():]
    r = r.rstrip("\n") + "\n" + (D / "DEC-951.md").read_text(encoding="utf-8")
    reg.write_text(r, encoding="utf-8")
    print("DEC-951 appended")
edit(ROOT / "governance/project/prompts/w2-orchestrator.md", [
    ("v3.43: DEC-949)", "v3.43: DEC-949; v3.44: DEC-951)"),
    ("  - **Hold only what an item blocks:** a red nightly holds all closes until the owner answers;",
     "  - **Hold only what an item blocks:** a red nightly holds all closes until the owner answers, unless (owner, "
     "standing, DEC-951 A) its cause is found, repaired, merged and verified in the main tree (the repaired tests pass, "
     "nothing else red): then release the closes yourself and report it in the package as a delegated decision; hold "
     "for the owner only a red that is unexplained, unrepaired, or in the judge's own core;"),
    ("  - **The schedule:** background waits in your session",
     "  - **The ping on time (owner, standing, DEC-951 B):** if the package is ready before 07:30, start no long "
     "foreground work between 07:15 and 07:35, so the 07:30 ping goes on time; a late package is logged with its cause.\n"
     "  - **The schedule:** background waits in your session"),
])
edit(T / "DAEO-0z8c.md", [("- tests/unit/gitenv/**\n", "- tests/unit/gitenv/**\n- tests/acceptance/W1-02/**\n")])
edit(T / "DAEO-cv58.md", [("- tests/unit/launch/test_launch_record*\n",
                           "- tests/unit/launch/test_launch_record*\n- tests/unit/launch/test_runs.py\n"
                           "- tests/unit/launch/test_w1_28.py\n- tests/unit/launch/test_w1_32.py\n"
                           "- tests/acceptance/serial-only.txt\n")])
edit(T / "DAEO-k7hz.md", [("kpis:\n  success:\n",
                           "kpis:\n  success:\n  - 'The test-design skill says how much is enough: acceptance tests in "
                           "proportion to the change (the minimum that shows each KPI line and each failure line), with "
                           "W2-60a''s 2,980 test lines for 713 code lines named as out of proportion [DEC-951 item 5]'\n")])
for tid in ("DAEO-0z8c", "DAEO-cv58", "DAEO-k7hz"):
    yaml.safe_load((T / (tid + ".md")).read_text(encoding="utf-8").split("\n---", 1)[0].lstrip("-\n"))
MAP = ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-30.json"
if MAP.exists():
    tid = json.loads(MAP.read_text())["W2-85"]
else:
    text = (D / "tickets/W2-85.md").read_text(encoding="utf-8")
    text = text.replace("and the context-reproducibility case test_gov_check_gives_context_reproducibility_green_here",
                        "and test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here")
    title = re.search(r"^title: '(.*)'$", text, re.M).group(1).replace("''", "'")
    tid = subprocess.run(["tk", "create", title, "-p", "1", "--external-ref", "W2-85"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip().split()[-1]
    path = T / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    text = text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created)
    yaml.safe_load(text.split("\n---", 1)[0].lstrip("-\n"))
    path.write_text(text, encoding="utf-8")
    MAP.write_text(json.dumps({"W2-85": tid}) + "\n", encoding="utf-8")
print("W2-85", tid)
card = ("#### W2-85 W2-54's two time-limit cases routed to the nightly (LITE, independent-test-designer; DEC-951 item 3)\n"
        "- **Ticket file:** `" + tid + "`.\n"
        "- **Why:** both passed at low load and failed in closes and verifications at loads of 30 to 100; closes run "
        "beside leads (DEC-942). Not onto `load_sensitive`, which only shrinks.\n"
        "- **Allowed paths:** `tests/acceptance/W2-54/**`, `tests/acceptance/serial-only.txt`.\n"
        "- **KPIs:** both routed with a `# nightly:` reason and `Rewrite-Reason: DEC-951 item 3`; expectations unchanged; "
        "the close leaves them out, the nightly runs them.\n")
edit(ROOT / "docs/plan/WAVE_2_WBS.md", [("## 3. Order, layers and critical path",
                                         "### DEC-951: W2-54's time limits to the nightly\n\n" + card +
                                         "\n## 3. Order, layers and critical path")])
print("prompt v3.44, tickets widened, W2-11 KPI, W2-85 card")
