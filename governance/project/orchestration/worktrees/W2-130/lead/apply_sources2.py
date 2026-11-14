"""Follow-up (1): apply gov links --propose-sources (open and in-progress tickets) less DEC-1123 (2)'s forms.

Writes: the tickets' sources: (dry run unless --apply), lead/patch-sources-2.patch (the open/in-progress sections,
byte for byte), lead/dec-1123-linked.yaml, lead/sources-added.json.
"""
import json, re, sys, yaml, collections
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-130")
LEAD = ROOT / ".gov-runtime/scratch/lead"
patch = (LEAD / "propose-sources-r3.patch").read_text()
env = json.loads((LEAD / "links-all-r3.json").read_text())
findings = env["result"]["findings"]


def fm(text):
    return yaml.safe_load(text.split("---", 2)[1]) or {}


tickets = {}
for p in (ROOT / ".tickets").glob("*.md"):
    t = p.read_text()
    tickets[f".tickets/{p.name}"] = (t, fm(t))
wbs = {str(f.get("wbs_id")): f.get("id") for _, f in tickets.values() if f.get("wbs_id")}

sections = {}
for sec in re.split(r"(?m)^(?=diff --git )", patch):
    m = re.match(r"diff --git a/(\S+) b/", sec)
    if m:
        sections[m.group(1)] = sec


def ids_of(sec):
    added = [l[3:].strip() for l in sec.split("\n") if l.startswith("+- ")]
    olds = [l[1:] for l in sec.split("\n") if l.startswith("-sources:")]
    news = [l[1:] for l in sec.split("\n") if l.startswith("+sources:")]
    for o, n in zip(olds, news):
        b = (yaml.safe_load(o) or {}).get("sources") or []
        added += [str(i) for i in ((yaml.safe_load(n) or {}).get("sources") or []) if i not in b]
    return added


live_sections, linked, to_add = [], collections.OrderedDict(), collections.OrderedDict()
for path, sec in sections.items():
    text, f = tickets[path]
    if f.get("status") not in ("open", "in_progress"):
        continue
    live_sections.append(sec)
    src = [str(s) for s in (f.get("sources") or [])]
    lr = [str(x.get("id") if isinstance(x, dict) else x) for x in (f.get("list_rows") or [])]
    for i in dict.fromkeys(ids_of(sec)):
        form = None
        if i == "DEC-798" and "DEC-1033" in src:
            form = {"id": i, "form": "dec-798", "via": "DEC-1033"}
        elif i in wbs and wbs[i] in src:
            form = {"id": i, "form": "wbs", "via": wbs[i]}
        elif re.match(r"W\d+-[A-Z]\d+$", i) and i in lr:
            form = {"id": i, "form": "list_rows", "via": i}
        if form:
            linked.setdefault(f["id"], []).append(form)
        else:
            to_add.setdefault(path, []).append(i)

# cross-check against gov links' UNLINKED_ID on live tickets
live_unlinked = {(fd["path"], fd["ids"][0]) for fd in findings if fd["code"] == "UNLINKED_ID"
                 and fd["path"].startswith(".tickets/") and tickets.get(fd["path"], ("", {}))[1].get("status") in ("open", "in_progress")}
proposed = {(p, i) for p, ids in to_add.items() for i in ids} | {
    (f".tickets/{t}.md", e["id"]) for t, es in linked.items() for e in es}
print("live UNLINKED_ID", len(live_unlinked), "proposed", len(proposed), "diff", sorted(live_unlinked ^ proposed)[:10])
print("forms", sum(len(v) for v in linked.values()), "to add", sum(len(v) for v in to_add.values()), "tickets", len(to_add))
for p, ids in to_add.items():
    print(" ", p, ids)

(LEAD / "patch-sources-2.patch").write_text("".join(live_sections))
(LEAD / "dec-1123-linked.yaml").write_text(yaml.safe_dump(dict(linked), sort_keys=True, default_flow_style=False))
(LEAD / "sources-added.json").write_text(json.dumps(to_add, indent=1))

if "--apply" in sys.argv:
    for path, ids in to_add.items():
        p = ROOT / path
        lines = p.read_text().split("\n")
        end = lines.index("---", 1)
        k = next(n for n in range(1, end) if lines[n].startswith("sources:"))
        if lines[k].rstrip().endswith("]"):
            line = lines[k].rstrip()
            inner = line[len("sources:"):].strip()[1:-1].strip()
            lines[k] = "sources: [" + (inner + ", " if inner else "") + ", ".join(ids) + "]"
        else:
            j = k + 1
            while j < end and lines[j].startswith("- "):
                j += 1
            lines[j:j] = [f"- {i}" for i in ids]
        p.write_text("\n".join(lines))
    print("applied")
