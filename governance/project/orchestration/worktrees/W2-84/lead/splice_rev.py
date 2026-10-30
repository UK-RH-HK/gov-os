"""Fill a reviewer brief: splice_rev.py <template> <out> <full head id>.

Puts in the design note, JUDGEMENT.md word for word, and the head."""
import sys

LEAD = "/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/"
src, out, head = sys.argv[1], sys.argv[2], sys.argv[3]
note = open(LEAD + "design.md", encoding="utf-8").read().strip()
judgement = open("/home/usain/gov-os-worktrees/W2-84/governance/project/briefs/JUDGEMENT.md",
                 encoding="utf-8").read().strip()
text = open(src, encoding="utf-8").read()
for marker in ("<<DESIGN NOTE>>", "<<JUDGEMENT>>"):
    assert text.count(marker) == 1, marker
assert len(head) == 40
text = text.replace("<<DESIGN NOTE>>", note).replace("<<JUDGEMENT>>", judgement).replace("<<HEAD>>", head)
open(out, "w", encoding="utf-8").write(text)
print("written", out)
