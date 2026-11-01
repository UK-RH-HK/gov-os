"""Assemble the review-5 probe record: the lead's head, then the reviewer's record with its headings one level down."""
import sys

LEAD = "/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/probes/"
out_path = sys.argv[1]
head = open(LEAD + "rev5-head.md", encoding="utf-8").read()
body = []
for line in open(LEAD + "rev5-body.md", encoding="utf-8").read().splitlines():
    if line.startswith("#"):
        line = "#" + line
    body.append(line)
text = head + "\n".join(body).strip() + "\n"
open(out_path, "w", encoding="utf-8").write(text)
print(len(text.splitlines()), "lines")
