"""Lead's pre-brief probe: do the record's counts-after and left equal gov links at counts-after.head?"""
import collections
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130")
import w2_130_support as s  # noqa: E402

AREAS = {"D-5": ("template/", "docs/contract/"), "D-6": ("src/", "tests/"), "D-9": (".tickets/",)}


def counts(findings, tree):
    by_code, by_role, unlinked = collections.Counter(), collections.defaultdict(collections.Counter), collections.Counter()
    for f in findings:
        by_code[f["code"]] += 1
        by_role[f["code"]][f["role"]] += 1
        if f["code"] == "UNLINKED_ID" and f["path"].startswith(".tickets/"):
            unlinked[s.ticket_status((tree / f["path"]).read_text(encoding="utf-8"))] += 1
    return dict(by_code), {c: dict(r) for c, r in by_role.items()}, dict(unlinked)


def left_of(findings):
    out = {}
    for area, prefixes in AREAS.items():
        mine = collections.defaultdict(dict)
        for f in findings:
            if f["path"].startswith(prefixes):
                mine[f["path"]][f["role"]] = mine[f["path"]].get(f["role"], 0) + 1
        out[area] = dict(mine)
    return out


rec = s.Record(s.ROOT / s.RECORD)
after, left = rec.data("counts-after"), rec.data("left")
want_code = {k: v for k, v in after["by_code"].items() if v}
want_role = {c: {r: n for r, n in rs.items() if n} for c, rs in after["by_code_role"].items() if sum(rs.values())}
want_unl = {k: v for k, v in after["unlinked_by_status"].items() if v}
want_left = {a: {p: dict(r) for p, r in left[a].items()} for a in AREAS}
base = Path(tempfile.mkdtemp(prefix="w2-130-probe-", dir="/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp"))
home = base / "home"
home.mkdir()
print("cleanup[-1] =", rec.commit_list("cleanup")[-1], " counts-after.head =", after["head"])
for rev in (after["head"], after.get("measured_at")):
    tree = s.make_clone(base / rev[:12], rev)
    fs = s.links_json(tree, home)
    c, r, u = counts(fs, tree)
    lf = left_of(fs)
    print(rev[:12], "by_code eq:", c == want_code, "by_role eq:", r == want_role, "unlinked eq:", u == want_unl,
          "left eq:", {a: lf[a] == want_left[a] for a in AREAS})
    if c != want_code:
        print("   diff by_code:", {k: (want_code.get(k), c.get(k)) for k in set(c) | set(want_code) if c.get(k) != want_code.get(k)})
    for a in AREAS:
        if lf[a] != want_left[a]:
            ks = set(lf[a]) | set(want_left[a])
            print("   diff", a, {k: (want_left[a].get(k), lf[a].get(k)) for k in ks if lf[a].get(k) != want_left[a].get(k)})
print("tmp:", base)
