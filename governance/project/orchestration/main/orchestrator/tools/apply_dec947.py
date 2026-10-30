"""Appends DEC-947, marks DEC-942's status line, and brings the prompt to v3.41 (the gate's memory rule; the weekly
re-measure). Safe to re-run."""
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REG = ROOT / "docs/DECISION_REGISTER.md"
PROMPT = ROOT / "governance/project/prompts/w2-orchestrator.md"
reg = REG.read_text(encoding="utf-8")
if "### DEC-947 " not in reg:
    m = re.search(r"### DEC-942 .*?\n- \*\*Status:\*\* [A-Z]+ \(", reg, re.S)
    if not m:
        sys.exit("DEC-942's status line not found")
    reg = reg[:m.end()] + "item 2's memory rule changed by DEC-947; " + reg[m.end():]
    reg = reg.rstrip("\n") + "\n" + (ROOT / ".gov-runtime/scratch/orchestrator/drafts/DEC-947.md").read_text(encoding="utf-8")
    REG.write_text(reg, encoding="utf-8")
    print("DEC-947 appended")
p = PROMPT.read_text(encoding="utf-8")
if "v3.41" not in p.split("\n", 1)[0]:
    old = ("and MemAvailable at least a floor (6,710,886 kB until the measurements support a lower one; if the floor is "
           "what holds launches while the CPU is idle, propose a lower one with the measurements) plus each running "
           "lead's measured reservation not yet in use (`tools/lead_mem.py`, sampled each minute);")
    new = ("and memory (owner, DEC-947): MemAvailable plus what the running leads hold at least the floor (6,710,886 kB), "
           "plus one verification run's measured peak (reserved once: one full test run at a time), plus a measured "
           "working size for each running lead and the new one (`tools/gate-config.json`; re-measured weekly from "
           "`tools/lead_mem.py`, sampled each minute); if memory alone holds launches while the CPU is idle, propose a "
           "lower floor with the measurements;")
    for a, b in (("v3.40: DEC-943 to DEC-946)", "v3.40: DEC-943 to DEC-946; v3.41: DEC-947)"), (old, new)):
        if p.count(a) != 1:
            sys.exit("prompt: not found once: " + a[:60])
        p = p.replace(a, b)
    PROMPT.write_text(p, encoding="utf-8")
    print("prompt v3.41")
