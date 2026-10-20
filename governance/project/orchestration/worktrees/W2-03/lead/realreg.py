import collections
import hashlib
from pathlib import Path

import gov
from gov import records

root = Path("/home/usain/gov-os-worktrees/W2-03")
print("gov:", gov.__file__)
reg = [r for r in records.records(root) if r["path"] == "docs/DECISION_REGISTER.md"]
print("decision records from the register:", len(reg))
print("types:", collections.Counter(r["type"] for r in reg))
print("statuses:", collections.Counter(r["status"] for r in reg))
hashes = collections.Counter(r.get("content_hash") for r in reg)
print("distinct hashes:", len(hashes), "shared:", [h for h, n in hashes.items() if n > 1])
bad = [r["id"] for r in reg if r.get("content_hash") != hashlib.sha256(r["span"].encode()).hexdigest()]
print("hash != sha256(span):", bad)
text = (root / "docs/DECISION_REGISTER.md").read_text()
print("span share of register (max):", max(len(r["span"]) for r in reg) / len(text))
print("spans not text of the register:", [r["id"] for r in reg if r["span"] not in text])
d = records.dangling(root)
print("dangling:", len(d), collections.Counter(e["type"] for e in d))
print("dangling DEC targets:", sorted({e["target"] for e in d if e["target"].startswith("DEC-")})[:30])
print("dangling sample by type:", {t: sorted({e["target"] for e in d if e["type"] == t})[:8] for t in {e["type"] for e in d}})
