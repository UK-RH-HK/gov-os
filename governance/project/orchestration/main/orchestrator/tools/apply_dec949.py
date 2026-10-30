"""Appends DEC-949, marks DEC-938 and DEC-930, brings the prompt to v3.43, and copies the two packages into packages/.
Safe to re-run."""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
REG = ROOT / "docs/DECISION_REGISTER.md"
PROMPT = ROOT / "governance/project/prompts/w2-orchestrator.md"
reg = REG.read_text(encoding="utf-8")
if "### DEC-949 " not in reg:
    for dec, note in (("DEC-938", "the morning package's scope refined by DEC-949 (overnight only)"),
                      ("DEC-930", "item 2's weekly numbers gain the ticket total and its growth (DEC-949)")):
        m = re.search(r"### " + dec + r" .*?\n- \*\*Status:\*\* [A-Z]+ \(", reg, re.S)
        if not m:
            sys.exit(dec + "'s status line not found")
        reg = reg[:m.end()] + note + "; " + reg[m.end():]
    reg = reg.rstrip("\n") + "\n" + (D / "DEC-949.md").read_text(encoding="utf-8")
    REG.write_text(reg, encoding="utf-8")
    print("DEC-949 appended")
p = PROMPT.read_text(encoding="utf-8")
if "v3.43" not in p.split("\n", 1)[0]:
    edits = [
        ("v3.42: DEC-948)", "v3.42: DEC-948; v3.43: DEC-949)"),
        ("- **The morning package (owner, standing, DEC-938; it replaces separate night-time pings):** from the end of the "
         "owner's day to 07:30, nothing pings.",
         "- **The morning package (owner, standing, DEC-938, refined by DEC-949; it replaces separate night-time pings):** "
         "it carries only what happens overnight: the nightly's findings, night-time alerts, and anything that arose "
         "between the end of the owner's day and 07:30. From the end of the owner's day to 07:30, nothing pings."),
        ("Everything since the last package goes into one file,", "Everything that arose overnight goes into one file,"),
        ("- **Only P1s and ACTs ping the owner (owner, standing, DEC-936 item 2.5).**",
         "- **Decisions during the day (owner, standing, DEC-949):** a P1, or a decision only the owner can take, arising "
         "from a lead, a close, a review, a merge or your own findings, is sent at once as a package "
         "(`packages/<id>.md`, six parts) with a ping, between 07:30 and midnight; from midnight to 07:30 it waits for "
         "the morning package. P2s you decide as delegated stay listed in the daily document, for the owner to "
         "overturn.\n- **Only P1s and ACTs ping the owner (owner, standing, DEC-936 item 2.5).**"),
        ("and the owner's decisions per week.",
         "and the owner's decisions per week; plus (DEC-949) the ticket total and how much it grew that week, with the "
         "new tickets named, so scope growth is visible."),
    ]
    for a, b in edits:
        if p.count(a) != 1:
            sys.exit("prompt: not found once: " + a[:70])
        p = p.replace(a, b)
    PROMPT.write_text(p, encoding="utf-8")
    print("prompt v3.43")
for name in ("P-W2-H063-1.md", "P-W2-20-SCOPE.md"):
    shutil.copyfile(D / name, ROOT / "governance/project/orchestration/packages" / name)
print("packages copied")
