import re
from pathlib import Path

d = Path("/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/lead/briefs")
shared = (d / "shared-interface.md").read_text()
for name in ("td-1.md", "eng-1.md"):
    p = d / name
    t = p.read_text()
    assert t.count("INTERFACE_PLACEHOLDER") == 1, name
    t = t.replace("INTERFACE_PLACEHOLDER", shared.rstrip("\n"))
    p.write_text(t)
    slots = re.findall(r"\{[A-Z_]{3,}\}", t)
    print(name, len(t.splitlines()), "lines", "slots:", slots)
