"""Lead's probe (run 6): the pinned cases with the pinned tree's own gov links (PYTHONPATH=<clone>/src)."""
import collections
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130")
import w2_130_support as s  # noqa: E402
import test_w2_130_sources as t4  # noqa: E402
import test_w2_130_record as t8  # noqa: E402

rec = s.Record(s.ROOT / s.RECORD)
after = rec.data("counts-after")
before = rec.data("counts-before")
base = Path(tempfile.mkdtemp(prefix="w2-130-pin2-", dir="/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp"))
home = base / "home"
home.mkdir()
orig_src = s.src_dir


def run(tree, pinned):
    s.src_dir = (lambda: tree / "src") if pinned else orig_src
    try:
        return s.links_json(tree, home)
    finally:
        s.src_dir = orig_src


m = after["measured_at"]
tree = s.make_clone(base / "measured", m)
for pinned in (False, True):
    fs = run(tree, pinned)
    mine = t8._counts(fs, tree)
    ok_code = {k: v for k, v in after["by_code"].items() if v} == mine["by_code"]
    ok_role = {c: {r: n for r, n in rs.items() if n} for c, rs in after["by_code_role"].items() if sum(rs.values())} == mine["by_code_role"]
    ok_unl = {k: v for k, v in after["unlinked_by_status"].items() if v} == mine["unlinked_by_status"]
    left = rec.data("left")
    ok_left = {}
    for area, prefixes in t8.AREAS.items():
        mm = collections.defaultdict(dict)
        for f in fs:
            if f["path"].startswith(prefixes):
                mm[f["path"]][f["role"]] = mm[f["path"]].get(f["role"], 0) + 1
        ok_left[area] = {p: dict(r) for p, r in left[area].items()} == dict(mm)
    linked = t4._linked(rec)
    listed = {(k, i["id"]) for k, items in linked.items() for i in items}
    unl = s.unlinked_on_live(fs, tree)
    pairs = {(k, i) for k, ids in unl.items() for i in ids}
    bad = [(k, i["id"], p) for k, items in linked.items() for i in items
           if (p := s.linked_form_problem(tree, k, i, fs))]
    print(f"measured_at {m[:12]} pinned_tool={pinned}: by_code={ok_code} by_role={ok_role} unl_status={ok_unl} left={ok_left}"
          f" | S4 unlisted={sorted(pairs - listed)[:6]} extra={sorted(listed - pairs)[:6]} form_problems={bad[:4]}")
    if not ok_code:
        print("   record", {k: v for k, v in after["by_code"].items() if v}, "\n   tool  ", mine["by_code"])

st = s.make_clone(base / "start", s.START)
for pinned in (False, True):
    fs = run(st, pinned)
    mine = collections.Counter(f["code"] for f in fs)
    res = {c: (before["by_code"].get(c, 0), mine.get(c, 0)) for c in ("UNMARKED_CHANGE", "UNLINKED_ID", "STATUS_CONFLICT")}
    print(f"START {s.START[:12]} pinned_tool={pinned}: (record, tool) {res}")
