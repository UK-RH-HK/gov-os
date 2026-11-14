"""Run 4: gov links at HEAD (clone), live unlinked vs dec-1123-linked, closed-missing diff vs record."""
import collections, json, shutil, sys
from pathlib import Path
import yaml

W = Path("/home/usain/gov-os-worktrees/W2-130")
sys.path.insert(0, str(W / "tests/acceptance/W2-130"))
import w2_130_support as s  # noqa: E402

L = W / ".gov-runtime/scratch/lead"
TMP = W / ".gov-runtime/scratch/tmp/r4"
HOME = W / ".gov-runtime/scratch/empty-home"
head = s.full("HEAD")
d = TMP / head[:12]
shutil.rmtree(d, ignore_errors=True)
d.parent.mkdir(parents=True, exist_ok=True)
tree = s.make_clone(d, head)
f = s.links_json(tree, HOME)
(L / "links-all-r4-head.json").write_text(json.dumps(f))
print("head", head, "findings", len(f))
print("by_code", dict(collections.Counter(x["code"] for x in f)))
live = s.unlinked_on_live(f, tree)
linked = yaml.safe_load((L / "dec-1123-linked.yaml").read_text())
lk = {(t, e["id"]) for t, es in linked.items() for e in es}
livepairs = {(t, i) for t, ids in live.items() for i in ids}
print("live unlinked not in dec-1123-linked:", sorted(livepairs - lk))
print("dec-1123-linked no longer unlinked:", sorted(lk - livepairs))
rec = s.Record(W / s.RECORD) if hasattr(s, "Record") else None
