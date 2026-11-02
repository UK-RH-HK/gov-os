"""assemble.py <head.md> <base brief> <from line> <to line> <middle.md> <return from line> <out>: a brief made of a new
head, the base brief's lines [from, to] (step 0 and the standing rules, word for word), a new middle, and the base
brief's lines from <return from line> to the end (the Return section, word for word)."""
import sys
from pathlib import Path

head, base, start, end, middle, ret, out = sys.argv[1:8]
lines = Path(base).read_text().splitlines(keepends=True)
text = (Path(head).read_text() + "\n" + "".join(lines[int(start) - 1:int(end)]) + Path(middle).read_text() + "\n"
        + "".join(lines[int(ret) - 1:]))
Path(out).write_text(text)
print(f"wrote {out}: {len(text.splitlines())} lines")
