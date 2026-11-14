"""Lead's probe for the S4 package: the three HEAD-reading S4 cases' conditions at measured_at and at HEAD."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130")
import w2_130_support as s  # noqa: E402
import test_w2_130_sources as t  # noqa: E402

rec = s.Record(s.ROOT / s.RECORD)
linked = t._linked(rec)
listed = {(k, i["id"]) for k, items in linked.items() for i in items}
base = Path(tempfile.mkdtemp(prefix="w2-130-s4-", dir="/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp"))
home = base / "home"
home.mkdir()
for rev in (rec.data("counts-after")["measured_at"], s.head()):
    tree = s.make_clone(base / rev[:12], rev)
    fs = s.links_json(tree, home)
    unl = s.unlinked_on_live(fs, tree)
    pairs = {(k, i) for k, ids in unl.items() for i in ids}
    bad = [(k, i["id"], p) for k, items in linked.items() for i in items
           if (p := s.linked_form_problem(tree, k, i, fs))]
    print(rev[:12], "unlisted:", sorted(pairs - listed), "| extra listed:", sorted(listed - pairs), "| form problems:", bad[:4])
