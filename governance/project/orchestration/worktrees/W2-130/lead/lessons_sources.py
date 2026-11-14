"""Adds one front-matter line `sources: [...]` before the closing --- of each lesson; no other byte changes."""
from pathlib import Path

SOURCES = {
    "L-0074": ["DEC-041", "DEC-046"],
    "L-0075": ["OWNER-DECISION-P2-0008"],
    "L-0076": ["OWNER-DIRECTION-BR-0004"],
    "L-0077": ["OWNER-AMENDMENT-P2-0010"],
    "L-0078": ["DEC-044", "DEC-046", "OWNER-AMENDMENT-P2-0010"],
}
root = Path("/home/usain/gov-os-worktrees/W2-130/docs/lessons")
for name, ids in SOURCES.items():
    p = root / f"{name}.md"
    lines = p.read_text(encoding="utf-8").split("\n")
    assert lines[0] == "---"
    closing = lines.index("---", 1)
    assert not any(l.startswith("sources:") for l in lines[:closing]), name
    lines.insert(closing, "sources: [" + ", ".join(ids) + "]")
    p.write_text("\n".join(lines), encoding="utf-8")
    print(name, "ok")
