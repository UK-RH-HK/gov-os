"""Appends DEC-935 (drafts/DEC-935.md) to the register and marks DEC-933's status line (DEC-866)."""
import pathlib
import sys

REG = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md")
DRAFT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/DEC-935.md")
text = REG.read_text(encoding="utf-8")
old = "item 2's application revised by DEC-934: committed scripts, logs, the morning check, the Windows wake task)"
new = ("item 2's application revised by DEC-934: committed scripts, logs, the morning check, the Windows wake task; "
       "item 1's re-pin 2 done, DEC-935)")
if text.count(old) != 1:
    sys.exit("DEC-933's status line not found once")
if "### DEC-935 " in text:
    sys.exit("DEC-935 is already in the register")
REG.write_text(text.replace(old, new).rstrip("\n") + "\n" + DRAFT.read_text(encoding="utf-8"), encoding="utf-8")
print("appended DEC-935; DEC-933 marked")
