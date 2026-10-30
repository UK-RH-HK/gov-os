"""Four ticket edits for after the close queue (2026-10-29): W2-79 gains DEC-943's KPI; W2-64's schema glob narrowed
to close.schema.json (split by file, DEC-942); W2-52 names the third copy of the adopt skill it changes, as the
first allowed path (a three-way merge with its branch stays clean); W2-26 names its evidence record for the close's
EVIDENCE gate. Prints each file changed; stops at the first anchor not found once."""
import pathlib
import sys

T = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.tickets")


def edit(tid, old, new):
    p = T / (tid + ".md")
    t = p.read_text(encoding="utf-8")
    if new in t:
        print(tid, "already done"); return
    if t.count(old) != 1:
        sys.exit(tid + ": not found once: " + old[:60])
    p.write_text(t.replace(old, new), encoding="utf-8")
    print(tid, "edited")


edit("DAEO-av72", "  failure:\n",
     "  - 'Each gap the orchestrator fixed in the common brief or the brief builder (governance/project/orchestration/"
     "brief-gaps.md, its \"Fixed by\" column) has a case that builds a brief today and shows the fix is still in it [DEC-943 item 1]'\n"
     "  failure:\n")
edit("DAEO-av72", "sources:\n", "sources:\n- DEC-943\n")
edit("DAEO-0uhh", "- template/governance/kernel/schemas/**\n", "- template/governance/kernel/schemas/close.schema.json\n")
edit("DAEO-siiz", "allowed_paths:\n- src/gov/adopt/lite_gates.py\n",
     "allowed_paths:\n- .claude/skills/adopt/SKILL.md\n- src/gov/adopt/lite_gates.py\n")
edit("DAEO-2ds6", "acceptance_tests:\n  judged_by:",
     "acceptance_tests:\n  evidence:\n  - docs/research/EXP-003/examin/README.md\n  judged_by:")
