"""Appends DEC-934 (drafts/DEC-934.md) to the register and marks DEC-933's status line (DEC-866)."""
import pathlib
import sys

REG = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md")
DRAFT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/DEC-934.md")
text = REG.read_text(encoding="utf-8")
old = "`Decided-by: owner (chat, 2026-10-28)`; standing) · **Under:** DEC-932 item 3, DEC-852 item 3"
new = ("`Decided-by: owner (chat, 2026-10-28)`; standing; item 2's application revised by DEC-934: committed scripts, "
       "logs, the morning check, the Windows wake task) · **Under:** DEC-932 item 3, DEC-852 item 3")
if text.count(old) != 1:
    sys.exit("DEC-933's status line not found once")
if "### DEC-934 " in text:
    sys.exit("DEC-934 is already in the register")
REG.write_text(text.replace(old, new).rstrip("\n") + "\n" + DRAFT.read_text(encoding="utf-8"), encoding="utf-8")
print("appended DEC-934; DEC-933 marked")
