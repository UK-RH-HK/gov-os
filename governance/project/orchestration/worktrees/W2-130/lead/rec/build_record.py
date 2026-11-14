"""Build docs/research/W2-130-link-cleanup.md and LINK-RECONCILIATION.md (the lead, run 3). Read-only on git;
writes the two files in the worktree and rec/build.json. Run from the worktree's root with PYTHONPATH=src."""
import collections
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

W = Path("/home/usain/gov-os-worktrees/W2-130")
sys.path.insert(0, str(W / "tests/acceptance/W2-130"))
import w2_130_support as s  # noqa: E402

L = W / ".gov-runtime/scratch/lead"
REF = W / ".gov-runtime/scratch/ref"
TMP = W / ".gov-runtime/scratch/tmp/build"
HOME = W / ".gov-runtime/scratch/empty-home"
F = s.full
key = lambda x: int(x[4:])  # noqa: E731

R12, LESSONS_C, MARKS4, SOURCES2 = F("8d245901b"), F("8f8d707f0"), F("bce798c3a"), F("57cbacfbf")
E12, C44 = F(s.FIRST), F(s.SECOND)
LAST = SOURCES2
assert F("HEAD") == LAST or s.is_ancestor(LAST, "HEAD")


def clone(rev):
    d = TMP / F(rev)[:12]
    shutil.rmtree(d, ignore_errors=True)
    d.parent.mkdir(parents=True, exist_ok=True)
    return s.make_clone(d, rev)


def findings_at(rev):
    tree = clone(rev)
    return tree, s.links_json(tree, HOME)


start_tree, start_f = findings_at(s.START)
last_tree, last_f = findings_at(LAST)
MEASURED = F("HEAD")  # run 4: the merged head (w2/integrate merged in 6b62de94e); after counts, left and tickets here
head_tree, head_f = (last_tree, last_f) if MEASURED == LAST else findings_at(MEASURED)


def counts(findings, tree, rev, label, measured=None):
    by_code, by_role, unlinked = collections.Counter(), collections.defaultdict(collections.Counter), collections.Counter()
    for f in findings:
        by_code[f["code"]] += 1
        by_role[f["code"]][f["role"]] += 1
        if f["code"] == "UNLINKED_ID" and f["path"].startswith(".tickets/"):
            unlinked[s.ticket_status((tree / f["path"]).read_text(encoding="utf-8"))] += 1
    at = measured or F(rev)
    out = {"head": F(rev)}
    if measured:
        out["measured_at"] = measured
    return {**out,
            "command": f"gov links --all --json --root "
                       f"<a git clone --shared of this repository checked out at {at[:12]}> (the tool of "
                       f"{F('HEAD')[:12]}, src/gov/links unchanged since {LESSONS_C[:12]}: PYTHONPATH=<worktree>/src, HOME empty, run as python3 -m gov.cli.main links); {label}",
            "by_code": dict(sorted(by_code.items())),
            "by_code_role": {c: dict(sorted(r.items())) for c, r in sorted(by_role.items())},
            "unlinked_by_status": dict(sorted(unlinked.items()))}


counts_before = counts(start_f, start_tree, s.START, "at the clean-up's starting head")
counts_after = counts(head_f, head_tree, LAST, f"at {MEASURED[:12]}, the merged head after the last clean-up commit "
                     f"{LAST[:12]} (the sources follow-up; the merges of w2/integrate since change no clean-up line, "
                     f"only other tickets' files, so 'head' names the last clean-up commit and 'measured_at' the tree "
                     f"counted)", measured=MEASURED)

# ---------------------------------------------------------------- census, the 87, archive-13
cen = json.loads((L / "rec/census.json").read_text())
census, ids87 = cen["census"], cen["ids87"]
drift_head = json.loads((REF / "drafts/work-drift-head.json").read_text())
archive13 = [{"changed": r["id"], "changer": c} for r in drift_head["rows"] for c in r["only_in_archive"]]
assert len(archive13) == 13

# ---------------------------------------------------------------- judged wrong (this run's audit, B and C tables)
aud_text = (L / "aud-marks-1-return.md").read_text()
EARLIER = {("DEC-853", "DEC-884"): "F14 (reviews/w2-130-marks.md part 2)",
           ("DEC-1050", "DEC-1057"): "F1 (reviews/w2-130-marks.md part 1)",
           ("DEC-120", "DEC-173"): "F2 (reviews/w2-130-marks.md part 1)",
           ("DEC-724", "DEC-860"): "F3 (reviews/w2-130-marks.md part 1)"}
judged = []
section = None
for line in aud_text.split("\n"):
    if line.startswith("## B."):
        section = "B"
    elif line.startswith("## C."):
        section = "C"
    elif line.startswith("## ") and section:
        section = None
    m = re.match(r"^\| (DEC-\d+) <- (DEC-\d+) \|", line)
    if section and m:
        cells = [c.strip() for c in line.strip()[1:-1].split(" | ")]
        pair = (m.group(1), m.group(2))
        verdict, fate = cells[2], cells[-1]
        earlier = EARLIER.get(pair)
        if pair[0] in ("DEC-454", "DEC-455", "DEC-480", "DEC-490", "DEC-492"):
            earlier = "F4 (reviews/w2-130-marks.md part 1)"
        finding = f"{section} (aud-marks-1, 2026-11-13)" + (f"; earlier {earlier}" if earlier else "")
        judged.append({"changed": pair[0], "changer": pair[1], "verdict": f"{verdict}: {fate}", "finding": finding,
                       "in_gov_links": pair in s.EIGHT})
assert len(judged) == 19, len(judged)
judged_pairs = {(j["changed"], j["changer"]) for j in judged}
assert {p for p in judged_pairs if p in s.EIGHT} == set(s.EIGHT)

# ---------------------------------------------------------------- audits
var = json.loads((L / "rec/variants.json").read_text())
ve, vc, vb = var[E12], var[C44], var[MARKS4]
tails = {E12: ve["tails"], C44: vc["tails"], MARKS4: vb["tails"]}


def committed_mark(commit, a, b):
    return tails[commit][f"{a}<-{b}"].removeprefix(" · ")


def proposed(v, a, b, fallback):
    return v["marks"].get(f"{a}<-{b}") or fallback


e12_committed = {tuple(p) for p in ve["committed"]}
free_e12 = []
for a, b in [tuple(p) for p in ve["committed_text"]]:
    free_e12.append({"changed": a, "changer": b, "mark": proposed(ve, a, b, committed_mark(E12, a, b)),
                     "verdict": "right", "fate": "committed", "committed_mark": committed_mark(E12, a, b)})
DROP_E12 = [("DEC-120", "DEC-173", "F2"), ("DEC-724", "DEC-860", "F3")] + [
    (a, b, "F4") for a, b in [("DEC-454", "DEC-904"), ("DEC-455", "DEC-904"), ("DEC-480", "DEC-899"),
                              ("DEC-480", "DEC-904"), ("DEC-490", "DEC-868"), ("DEC-490", "DEC-899"),
                              ("DEC-490", "DEC-908"), ("DEC-492", "DEC-904"), ("DEC-492", "DEC-908")]]
for a, b, fid in DROP_E12:
    assert (a, b) not in e12_committed
    free_e12.append({"changed": a, "changer": b, "mark": f"**Changed by:** {b}", "verdict": "wrong", "fate": "dropped",
                     "finding": fid})
assert len(free_e12) == 19
SPECIAL_E12 = {
    ("DEC-1050", "DEC-1057"): {"mark": "**Changed by:** DEC-1057 (8)", "verdict": "wrong", "fate": "dropped",
                               "finding": "F1"},
    ("DEC-1084", "DEC-1087"): {"mark": "**Changed by:** DEC-1087 (W2-33's layer lines moved to Wave 3, W3-P23: "
                                       "reversed by (13)", "finding": "F5 (part rewritten)"},
    ("DEC-941", "DEC-946"): {"mark": "**Changed by:** DEC-946 (item 6))", "finding": "F5 (part rewritten)"},
    ("DEC-988", "DEC-989"): {"mark": "**Changed by:** DEC-989 (items)", "finding": "F5 (part rewritten, should)"},
    ("DEC-1032", "DEC-1033"): {"mark": "**Changed by:** DEC-1033 (items)", "finding": "F5 (part rewritten, should)"}}
e12_text = {tuple(p) for p in ve["committed_text"]}
pool_e12 = sorted([f"{a}<-{b}" for a, b in e12_committed - e12_text] + ["DEC-1050<-DEC-1057"])
assert len(pool_e12) == 132, len(pool_e12)
SEED_E12 = 1302
drawn_e12 = random.Random(SEED_E12).sample(pool_e12, 20)


def e12_item(p):
    a, b = p.split("<-")
    sp = SPECIAL_E12.get((a, b), {})
    item = {"changed": a, "changer": b, "mark": sp.get("mark") or proposed(ve, a, b, committed_mark(E12, a, b)),
            "verdict": sp.get("verdict", "right"), "fate": sp.get("fate", "committed")}
    if item["fate"] == "committed":
        item["committed_mark"] = committed_mark(E12, a, b)
    if sp.get("finding"):
        item["finding"] = sp["finding"]
    return item


labelled_e12 = [e12_item(p) for p in drawn_e12]
also_e12 = [e12_item(f"{a}<-{b}") for a, b in SPECIAL_E12 if f"{a}<-{b}" not in drawn_e12]

c44_committed = {tuple(p) for p in vc["committed"]}
c44_text = {tuple(p) for p in vc["committed_text"]}
free_c44 = []
for a, b in sorted(c44_text, key=lambda p: (key(p[0]), key(p[1]))):
    note = ("the free-text f5 mark: \"This replaces DEC-761 item 1's line\"" if a == "DEC-761"
            else "a group B ruling's mark (DEC-1098 (3)), applied as the ruling names it")
    free_c44.append({"changed": a, "changer": b, "mark": proposed(vc, a, b, committed_mark(C44, a, b)),
                     "verdict": "right", "fate": "committed", "committed_mark": committed_mark(C44, a, b),
                     "basis": note})
pool = sorted([f"{a}<-{b}" for a, b in c44_committed - c44_text] + ["DEC-853<-DEC-884"])
SEED_C44 = 1302
drawn = random.Random(SEED_C44).sample(pool, 20)


def c44_item(p):
    a, b = p.split("<-")
    if (a, b) == ("DEC-853", "DEC-884"):
        return {"changed": a, "changer": b, "mark": "**Changed by:** DEC-884 (item 4)", "verdict": "wrong",
                "fate": "dropped", "finding": "F14"}
    return {"changed": a, "changer": b, "mark": proposed(vc, a, b, committed_mark(C44, a, b)), "verdict": "right",
            "fate": "committed", "committed_mark": committed_mark(C44, a, b)}


labelled_c44 = [c44_item(p) for p in drawn]
also_c44 = [c44_item(p) for p in pool if p not in drawn]

b_items = []
for a, b in [tuple(p) for p in vb["committed"]]:
    b_items.append({"changed": a, "changer": b, "mark": proposed(vb, a, b, committed_mark(MARKS4, a, b)),
                    "verdict": "right", "fate": "committed", "committed_mark": committed_mark(MARKS4, a, b),
                    "finding": "F1 (part corrected)" if a == "DEC-1115" else "F2 (part named)"})
assert not vb["committed_text"]

audits = [
    {"commit": E12, "audit_head": F("2f9c80b1f"), "audit_date": "2026-11-08T01:35:59+00:00",
     "audit_source": "the independent auditor's review, part 1 (.gov-runtime/scratch/orchestrator/reviews/"
                     "w2-130-marks.md; session ad44f5fe, subagent agent-abeeaeb52fe9d7a0a, verdict first written "
                     "2026-11-08T01:35:59Z), which checked every free-text mark by hand and every labelled mark by "
                     "script against the changer's own label",
     "seed": SEED_E12, "draw": "random.Random(1302).sample(sorted(pool), 20); pool: the 132 labelled marks the "
                               "auditor checked for a1 and a2, as 'DEC-a<-DEC-b' strings (e12f8a30c's 131 committed "
                               "labelled marks and DEC-1050<-DEC-1057, dropped by F1); also_judged: the auditor's other "
                               "rulings on labelled marks (F1, F5) not drawn",
     "free_text": free_e12, "labelled": labelled_e12, "also_judged": also_e12,
     "labelled_all_checked": "every one of the 132 labelled marks checked by script for the changer's own label "
                             "naming the marked entry (part 1, 'What I checked'); F1 dropped one, F5 rewrote three parts"},
    {"commit": C44, "audit_head": F("ce7f10eb8a2a"), "audit_date": "2026-11-09T00:41:51+00:00",
     "audit_source": "the independent auditor's review, part 2 'Final patches' (.gov-runtime/scratch/orchestrator/"
                     "reviews/w2-130-marks.md; same session and subagent, verdict first written 2026-11-09T00:41:51Z)",
     "seed": SEED_C44, "draw": "random.Random(1302).sample(sorted(pool), 20); pool: every labelled mark the auditor "
                              "judged for c4420040f, as 'DEC-a<-DEC-b' strings (30: f5's 16 labelled, the 13 group B "
                              "ruling marks less DEC-024<-DEC-074, DEC-786<-DEC-942, DEC-927<-DEC-1057); the other "
                              "10 are in also_judged",
     "free_text": free_c44, "labelled": labelled_c44, "also_judged": also_c44},
    {"commit": MARKS4, "audit_head": F("09542040f"), "audit_date": "2026-11-13T22:46:14+00:00",
     "audit_source": "this run's independent auditor (session d51ff894-0d36-4511-87bf-05ca51f1a74a, "
                     "aud-marks-1, verdict block dated 2026-11-13T22:46:14+00:00 at 09542040f)",
     "seed": None, "free_text": [], "labelled": b_items}]

comparison = {}
for item in audits:
    c = item["commit"]
    committed = s.committed_pairs(c)
    text = {tuple(p) for p in var[c]["committed_text"]}
    listed = {(m["changed"], m["changer"]) for m in item["free_text"]}
    wrong = {(m["changed"], m["changer"]) for k in ("free_text", "labelled", "also_judged") for m in item.get(k, [])
             if m["verdict"] == "wrong"}
    comparison[c] = {"unchecked": len((committed & text) - listed), "wrong": len(committed & wrong),
                     "committed_marks": len(committed), "free_text_committed": len(committed & text)}
    assert comparison[c]["unchecked"] == 0 and comparison[c]["wrong"] == 0, comparison[c]

# ---------------------------------------------------------------- patches
pa = {n: (REF / f"drafts/{f}").read_text() for n, f in
      (("patch-a0", "a0-archive-one-per-line.patch"), ("patch-a1", "a1-marks-no-hint.patch"),
       ("patch-a2", "a2-marks-rest.patch"), ("patch-b1", "b1-sources-open.patch"))}
pa["patch-sources-2"] = (L / "patch-sources-2.patch").read_text()
t8 = clone(LESSONS_C)
done = s.run_links(t8, HOME, "--propose-marks", "--all")
pa["patch-marks-3"] = done.stdout
for n, t in pa.items():
    assert not re.search(r"(?m)^```", t), n
    assert t.strip(), n
b1 = {p: sorted(i) for p, i in s.patch_source_ids(pa["patch-b1"]).items()}
assert b1 == {p: sorted(i) for p, i in s.sources_added(E12).items()}

# ---------------------------------------------------------------- trailer residuals
rc = json.loads((L / "rec/recount-out.json").read_text())
drafts_rows = {(r["key"], r["value"]): r for r in json.loads((REF / "drafts/work/residuals.json").read_text())["rows"]}
alias = {}
for p in (W / ".tickets").glob("*.md"):
    fm = yaml.safe_load(p.read_text().split("---", 2)[1]) or {}
    for k in ("wbs_id", "external-ref"):
        if fm.get(k):
            alias[str(fm[k])] = fm["id"]


def task_of(c):
    return s.git("log", "-1", "--format=%(trailers:key=Task,valueonly,separator=%x2C)", c).strip() or None


values = []
for r in rc:
    k, v = r["trailer"], r["value"]
    if k == "Task":
        tickets = [alias.get(v)] if alias.get(v) else [None]
        if alias.get(v):
            should = [alias[v]]
        else:
            should = drafts_rows[(k, v)]["should_have_named"]
    else:
        tickets = sorted({t for t in (task_of(c) for c in r["commits"]) if t} or {None}, key=str)
        if v.startswith("CAP-58"):
            should = ["CAP-58", "CAP-03"]
        elif v.startswith("DEC-084"):
            should = ["DEC-084", "DEC-119"]
        elif v == "AR-9":
            should = ["DEC-900", "DEC-718"]
        else:
            should = drafts_rows[(k, v)]["should_have_named"]
    values.append({"trailer": k, "value": v, "commits": r["commits"], "tickets": tickets,
                   "should_have_named": should, "unresolved": r["tokens"]})
residuals = {"head": F(s.START), "command": "python3 - 232efc47d < (the w2-130:recount block), cwd the repository",
             "values": values}

# ---------------------------------------------------------------- drift
drift_src = (L / "rec/drift.py").read_text()
out = json.loads(subprocess.run([sys.executable, "-"], input=drift_src, cwd=last_tree, capture_output=True, text=True,
                                check=True).stdout)
aside = [{"changed": d["changed"], "changer": d["changer"]} for d in out["drift"]]
assert all((a["changed"], a["changer"]) in judged_pairs for a in aside)
drift_run = {"head": LAST, "command": "python3 - < (the w2-130:drift block), cwd a clone of the repository at head",
             "output": out, "set_aside": aside, "count_after_set_aside": 0}

# ---------------------------------------------------------------- tickets
closed_missing, no_record, live_unlinked = {}, {}, set()
for f in head_f:
    if f["path"].startswith(".tickets/"):
        st = s.ticket_status((head_tree / f["path"]).read_text())
        if f["code"] == "UNLINKED_ID":
            if st == "closed":
                closed_missing.setdefault(f["ids"][1], set()).add(f["ids"][0])
            elif st in ("open", "in_progress"):
                live_unlinked.add((f["ids"][1], f["ids"][0]))
        if f["code"] == "UNKNOWN_ID" and not f["ids"][0].startswith("tests/"):
            no_record.setdefault(f["ids"][1], set()).add(f["ids"][0])
closed_missing = {t: sorted(i) for t, i in sorted(closed_missing.items())}
no_record = {t: sorted(i) for t, i in sorted(no_record.items())}
linked = yaml.safe_load((L / "dec-1123-linked.yaml").read_text())
assert {(t, e["id"]) for t, es in linked.items() for e in es} == live_unlinked

# ---------------------------------------------------------------- lessons
lessons = {}
for p in sorted((last_tree / "docs/lessons").glob("*.md")):
    t = p.read_text()
    fm = yaml.safe_load(t.split("\n---\n", 1)[0].removeprefix("---\n")) or {}
    src_line = next(ln for ln in t.splitlines() if ln.startswith("**Source:**"))
    lessons[p.stem] = {"sources": [str(x) for x in fm["sources"]],
                       "came_from": src_line.removeprefix("**Source:**").strip(), "agree": True}

# ---------------------------------------------------------------- left
AREAS = {"D-5": ("template/", "docs/contract/"), "D-6": ("src/", "tests/"), "D-9": (".tickets/",)}
left = {}
for area, pre in AREAS.items():
    m = collections.defaultdict(collections.Counter)
    for f in head_f:
        if f["path"].startswith(pre):
            m[f["path"]][f["role"]] += 1
    left[area] = {p: dict(sorted(r.items())) for p, r in sorted(m.items())}
left_by_code = {area: dict(collections.Counter(f["code"] for f in head_f if f["path"].startswith(pre)))
                for area, pre in AREAS.items()}

commits = {"starting_head": F(s.START), "first_commit": E12, "w2_129_landing": F(s.W2_129_LANDING),
           "w2_92_adoption": F(s.W2_92_ADOPTION), "start_decision": "DEC-1097 (9)", "status_decision": "DEC-1098 (3)",
           "status_decision_commit": F(s.DEC1098_COMMIT), "sitting_commit": F(s.SITTING_COMMIT),
           "cleanup": [E12, C44, R12, LESSONS_C, MARKS4, SOURCES2], "marks": [E12, C44, MARKS4],
           "sources": [E12, SOURCES2], "status": [C44, R12], "r12": R12, "lessons": LESSONS_C}
for a, b in zip(commits["cleanup"], commits["cleanup"][1:]):
    assert s.is_ancestor(a, b)

data = {"commits": commits, "ids-87": ids87, "census": census, "archive-13": archive13, "judged-wrong": judged,
        "audits": audits, "comparison": comparison, "trailer-residuals": residuals, "drift-run": drift_run,
        "counts-before": counts_before, "counts-after": counts_after, "closed-missing": closed_missing,
        "no-record": no_record, "dec-1123-linked": linked, "lessons": lessons, "left": left}
(L / "rec/build.json").write_text(json.dumps({"data": data, "left_by_code": left_by_code, "measured": MEASURED,
                                              "recount": (L / "rec/recount.py").read_text()}, indent=1, default=str))
for n, t in pa.items():
    (L / f"rec/{n}.diff").write_text(t)
print("built", {k: (len(v) if hasattr(v, "__len__") else v) for k, v in data.items()})
print("before", counts_before["by_code"])
print("after", counts_after["by_code"])
print("left_by_code", left_by_code)
print("closed tickets", len(closed_missing), "ids", sum(map(len, closed_missing.values())), "no-record", no_record)
shutil.rmtree(TMP, ignore_errors=True)
