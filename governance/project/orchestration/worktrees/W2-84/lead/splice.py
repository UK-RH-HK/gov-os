"""Put the design note into a brief at its <<DESIGN NOTE>> marker: splice.py <brief>."""
import sys

LEAD = "/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/"
brief = sys.argv[1]
note = open(LEAD + "design.md", encoding="utf-8").read().strip()
text = open(brief, encoding="utf-8").read()
assert text.count("<<DESIGN NOTE>>") == 1, "the marker must appear once"
open(brief, "w", encoding="utf-8").write(text.replace("<<DESIGN NOTE>>", note))
print("spliced", brief)
