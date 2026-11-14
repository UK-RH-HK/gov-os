import re
from pathlib import Path

d = Path("/home/usain/gov-os-worktrees/W2-174/.gov-runtime/scratch/lead/briefs")
block = (d / "interface.md").read_text(encoding="utf-8").rstrip("\n")
for name in ("td-1.md", "en-1.md"):
    p = d / name
    text = p.read_text(encoding="utf-8")
    if "INTERFACE_BLOCK" in text:
        text = text.replace("INTERFACE_BLOCK", block)
        p.write_text(text, encoding="utf-8")
    left = sorted(set(re.findall(r"(?<!\$)\{([A-Z][A-Z0-9_]*)\}", text)))
    print(name, len(text), "slots:", left)
