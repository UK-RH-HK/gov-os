"""Survey the evidence blocks of docs/close/*: key sets and value types (lead's scratch)."""
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])
for path in sorted(root.glob("docs/close/*/CL-*.md")):
    text = path.read_text(encoding="utf-8").split("\n")
    end = text.index("---", 1)
    front = yaml.safe_load("\n".join(text[1:end]))
    ev = front.get("evidence", "<absent>")
    if not isinstance(ev, dict):
        print(path.parent.name, "evidence:", repr(ev)[:60])
        continue
    shape = {k: type(v).__name__ for k, v in ev.items()}
    print(path.parent.name, front.get("created"), shape)
    for key in ("selected", "left_out", "why_full"):
        val = ev.get(key)
        if isinstance(val, list) and val:
            print("   ", key, "item:", val[0])
    print("    scope:", ev.get("scope"), "failures n:", len(ev.get("failures") or []), "skip_count:", ev.get("skip_count"), "skips n:", len(ev.get("skips") or []))
