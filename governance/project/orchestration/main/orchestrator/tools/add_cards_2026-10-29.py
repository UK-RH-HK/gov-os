"""Adds the cards of W2-60 (a, b), W2-76, W2-77, W2-78, W2-79, W2-80, W2-81 and W2-81's held-out companion to the
plan's draft copy, at the end of §2 (before "## 3. Order"), under a heading for the re-plan of 2026-10-29 (DEC-941)."""
import pathlib
import sys

D = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts")
WBS = D / "WAVE_2_WBS.next.md"
text = WBS.read_text(encoding="utf-8")
anchor = "## 3. Order, layers and critical path"
if text.count(anchor) != 1 or "#### W2-81 " in text:
    sys.exit("anchor not found once, or the cards are already in")
cards = "\n\n".join(p.read_text(encoding="utf-8").strip() for p in
                    (D / "tickets/W2-60-card.md", D / "tickets/cards-76-78.md", D / "tickets/cards.md"))
block = ("### The re-plan of 2026-10-29 (DEC-941): new cards\n\n"
         "W2-55, W2-56, W2-61 and W2-64 keep their cards above; their ticket files are filed on 2026-10-29.\n\n"
         + cards + "\n\n")
WBS.write_text(text.replace(anchor, block + anchor), encoding="utf-8")
print("cards added")
