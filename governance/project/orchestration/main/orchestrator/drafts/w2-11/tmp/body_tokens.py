"""Body size of skill files the way the skill validator and W1-35 count it: ceil(characters / 4) of the text after the
front matter, at most 2,500 (so at most 10,000 characters); the description at most 60 tokens (240 characters).
Read-only. usage: python3 body_tokens.py <SKILL.md> [...]
"""
import math
import re
import sys
from pathlib import Path

for arg in sys.argv[1:]:
    text = Path(arg).read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        print(f"{arg}: no front matter")
        continue
    front, body = m.group(1), m.group(2)
    d = re.search(r"^description:\s*(.*)$", front, re.M)
    desc = d.group(1).strip().strip('"') if d else ""
    verdict = "OK" if math.ceil(len(body) / 4) <= 2500 and math.ceil(len(desc) / 4) <= 60 else "OVER THE CAP"
    print(f"{arg}: body {len(body)} chars = {math.ceil(len(body) / 4)} tokens (cap 2500); "
          f"description {math.ceil(len(desc) / 4)} tokens (cap 60); {verdict}")
