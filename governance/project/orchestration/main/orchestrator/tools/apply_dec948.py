"""Appends DEC-948 and brings the prompt to v3.42 (the report's closing block). Safe to re-run."""
import pathlib
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REG = ROOT / "docs/DECISION_REGISTER.md"
PROMPT = ROOT / "governance/project/prompts/w2-orchestrator.md"
reg = REG.read_text(encoding="utf-8")
if "### DEC-948 " not in reg:
    reg = reg.rstrip("\n") + "\n" + (ROOT / ".gov-runtime/scratch/orchestrator/drafts/DEC-948.md").read_text(encoding="utf-8")
    REG.write_text(reg, encoding="utf-8")
    print("DEC-948 appended")
p = PROMPT.read_text(encoding="utf-8")
if "v3.42" not in p.split("\n", 1)[0]:
    old = ("is readable on a phone, gives its evidence, and ends with exactly one line `OWNER_ACTION: <P1|P2|COMMIT|"
           "COMMIT-NEEDED|none> <ids> - <summary>`, naming every open owner item.")
    new = ("is readable on a phone, gives its evidence, and **ends with the same five-line block, every report however "
           "short (owner, standing, DEC-948)**, printed by `tools/status_block.py` (hand-kept facts in "
           "`log/report-state.json`, updated at each merge, hold and close; `--mark` after sending):\n"
           "  - Progress: closed / merged-not-closed / built-and-held / in flight / not started, of the total;\n"
           "  - Leads: running (which), queued next (which), and what the gate is waiting on;\n"
           "  - Closes: running or next, and any refused since the last report;\n"
           "  - Toward EXAMIN's copy: on track for 18 November, or at risk (one line, with why);\n"
           "  - OWNER_ACTION: none, or `<P1|P2|COMMIT|COMMIT-NEEDED> <ids> - <summary>`, naming every open owner item.\n"
           " ")
    for a, b in (("v3.41: DEC-947)", "v3.41: DEC-947; v3.42: DEC-948)"), (old, new)):
        if p.count(a) != 1:
            sys.exit("prompt: not found once: " + a[:60])
        p = p.replace(a, b)
    PROMPT.write_text(p, encoding="utf-8")
    print("prompt v3.42")
