"""Insert the DEC-1127 draft into a CLONE's register after DEC-1126's entry (rehearsal only). Usage: insert_dec.py <clone> <draft>"""
import sys
from pathlib import Path
clone, draft = Path(sys.argv[1]), Path(sys.argv[2]).read_text().rstrip("\n").split("\n")
p = clone / "docs/DECISION_REGISTER.md"
lines = p.read_text().split("\n")
at = next(i for i, l in enumerate(lines) if l.startswith("### DEC-1126"))
table = next(i for i in range(at, len(lines)) if lines[i].startswith("| Version |"))
assert not any(l.startswith("### DEC-1127") for l in lines)
lines[table:table] = draft + [""]
p.write_text("\n".join(lines))
