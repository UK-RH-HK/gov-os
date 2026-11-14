"""Lead's probe (run 7, pin run 3): closed_missing and no_record at counts-after.measured_at with the pinned tool;
variant_findings' free-text sets under the branch's tool vs each commit's own tree's tool."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130")
import w2_130_support as s  # noqa: E402

rec = s.Record(s.ROOT / s.RECORD)
after = rec.data("counts-after")
base = Path(tempfile.mkdtemp(prefix="w2-130-pin3-", dir="/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp"))
home = base / "home"
home.mkdir()

m = after["measured_at"]
tree = s.make_clone(base / "measured", m)
fs = s.links_json(tree, home, src=s.pinned_src(tree))


def tk(t):
    p = tree / ".tickets" / f"{t}.md"
    return p.read_text(encoding="utf-8") if p.is_file() else None


# closed_missing
data = rec.data("closed-missing")
expected = {}
for f in fs:
    if f["code"] == "UNLINKED_ID" and f["path"].startswith(".tickets/"):
        t = f["ids"][1]
        if s.ticket_status(tk(t) or "") == "closed":
            expected.setdefault(t, set()).add(f["ids"][0])
probs = []
for t, ids in data.items():
    text = tk(t)
    if text is None or s.ticket_status(text) != "closed":
        probs.append((t, "not closed at measured_at"))
    elif set(ids) & set(s.ticket_sources(text)):
        probs.append((t, "lists an id in sources"))
got = {t: set(i) for t, i in data.items()}
print(f"closed_missing at {m[:12]} pinned: equal={got == expected} problems={probs[:5]}")
if got != expected:
    print("  only record:", sorted(set(got) - set(expected))[:8], "only tool:", sorted(set(expected) - set(got))[:8])
    print("  differing:", [(t, sorted(got[t] ^ expected[t])[:4]) for t in set(got) & set(expected) if got[t] != expected[t]][:8])

# no_record
data = rec.data("no-record")
headings = set(re.findall(r"(?m)^### (DEC-\d+)\b", (tree / s.REGISTER).read_text(encoding="utf-8")))
stems = {p.stem for p in (tree / ".tickets").glob("*.md")}
probs = []
for t, ids in data.items():
    text = tk(t)
    if text is None:
        probs.append((t, "no ticket"))
        continue
    for i in ids:
        if i in headings or i in stems:
            probs.append((t, i, "names a record"))
        if i not in text:
            probs.append((t, i, "not in text"))
named = {(f["ids"][1], f["ids"][0]) for f in fs if f["code"] == "UNKNOWN_ID"
         and f["path"].startswith(".tickets/") and not f["ids"][0].startswith("tests/")}
left = [(t, i) for t, i in named if i not in data.get(t, [])]
print(f"no_record at {m[:12]} pinned: problems={probs[:5]} unlisted={left[:5]}")

# variant_findings: branch tool vs the commit's own tree's tool
import inspect  # noqa: E402
print("cleanup commits:", [c[:12] for c in rec.commit_list("cleanup")])


def free(fs_):
    return {key for key, finding in s.by_pair(fs_).items() if finding.get("text")}


for commit in s.marks_commits(rec):
    sha = s.full(commit)
    vt = s.make_clone(base / f"variant-{sha[:12]}", sha)
    (vt / s.REGISTER).write_text(s.variant_register(sha), encoding="utf-8")
    s.commit_all(vt, "the register without the marks the commit appends")
    a = free(s.links_json(vt, home))
    b = free(s.links_json(vt, home, src=s.pinned_src(vt)))
    print(f"variant {sha[:12]}: branch-tool text={len(a)} own-tool text={len(b)} equal={a == b} only_branch={sorted(a-b)[:4]} only_own={sorted(b-a)[:4]}")
