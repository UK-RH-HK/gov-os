"""Summarise select_tests.py's JSON; write the pytest options to a file; shorten full hashes in the log (DEC-911)."""
import json
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
d = json.loads(src.read_text(encoding="utf-8"))
print("scope:", d.get("scope"), "| core_changed:", d.get("core_changed"), "| unplaced:", d.get("unplaced"),
      "| why_full:", d.get("why_full"))
for s in d.get("selected", []):
    print("selected:", s.get("target"), [w.get("reason") + (":" + w["ticket"] if w.get("ticket") else "") for w in s.get("why", [])])
opts = d.get("pytest_options", [])
print("pytest_options count:", len(opts))
print("other keys:", [k for k in d if k not in ("selected", "changed", "pytest_options")])
Path(sys.argv[2]).write_text("\n".join(opts) + "\n", encoding="utf-8")
src.write_text(re.sub(r"\b([0-9a-f]{12})[0-9a-f]{28}\b", r"\1", src.read_text(encoding="utf-8")), encoding="utf-8")
