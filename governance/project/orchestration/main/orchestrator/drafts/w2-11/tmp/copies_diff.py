"""For each kernel skill: does the generated .claude copy carry the source's body and version? (read-only)

usage: python3 copies_diff.py <tree>
"""
import re
import sys
from pathlib import Path

tree = Path(sys.argv[1])
SKILLS = tree / "template/governance/kernel/skills"


def split(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def version(front):
    meta = re.search(r"^metadata:\n(?:[ ]+.*\n)*?[ ]+version:\s*\"?([\d.]+)\"?", front + "\n", re.M)
    top = re.search(r"^version:\s*\"?([\d.]+)\"?", front, re.M)
    return (top.group(1) if top else None, meta.group(1) if meta else None)


for folder in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
    name = folder.name
    src = folder / "SKILL.md"
    copy = tree / ".claude/skills" / name / "SKILL.md"
    if not src.is_file() or not copy.is_file():
        print(f"{name}: source {src.is_file()} copy {copy.is_file()}")
        continue
    sf, sb = split(src.read_text())
    cf, cb = split(copy.read_text())
    body = "same" if sb.strip() == cb.strip() else "DIFFERS"
    sv, cv = version(sf), version(cf)
    ok_ver = (sv[0] == cv[1]) or (sv[1] == cv[1])
    others = []
    for f in sorted(folder.iterdir()):
        if f.name == "SKILL.md" or not f.is_file():
            continue
        c = tree / ".claude/skills" / name / f.name
        if not c.is_file() or c.read_text() != f.read_text():
            others.append(f.name)
    print(f"{name}: body {body}; source version {sv[0]} (metadata {sv[1]}), copy metadata.version {cv[1]}"
          f"{'' if ok_ver else '  <-- version differs'}; other files differing: {others or 'none'}")
