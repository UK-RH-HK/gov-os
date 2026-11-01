"""DEC-957 / DEC-954: files W2-86, W2-88 and the memory-gap tickets W2-91 to W2-94 (tk create, draft in place, one
commit each with its own Task). Map: log/tickets-2026-10-30d.json. Safe to re-run (filed ones are skipped)."""
import json
import re
import subprocess
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
from te_lib import ORCH, ROOT, T, commit  # noqa: E402

D = ORCH / "drafts/tickets"
MAP = ORCH / "log/tickets-2026-10-30d.json"
ids = json.loads(MAP.read_text()) if MAP.exists() else {}

T95_OLD = "hit@5 against CAP-10''s floor of 85, full evidence against the owner''s target of 99 %"
T95_NEW = "hit@5 against CAP-10''s floor of 85 and the owner''s target of 95 % (DEC-957), full evidence against 99 %"


def prep(w2, text):
    if w2 == "W2-86":
        assert T95_OLD in text
        text = text.replace(T95_OLD, T95_NEW)
    if w2 == "W2-88":
        old = "Each figure is reported against CAP-10''s floor of 85 and the owner''s target of 99 %."
        assert old in text
        text = text.replace(old, "Both figures are reported: hit@5 against CAP-10''s floor of 85 and the owner''s target "
                                 "of 95 % (DEC-957), full evidence against 99 %.")
        text = text.replace("- src/gov/store/layout.py\n", "- src/gov/store/layout.py\n- src/gov/store/loader.py\n")
    deps = {"W2-88": ["DAEO-ym8a", "DAEO-siiz", "DAEO-tgk2", "DAEO-l78m"], "W2-91": [ids.get("W2-86", "?")],
            "W2-92": ["DAEO-s9qc", "DAEO-ym8a"], "W2-93": ["DAEO-l78m", "DAEO-m1u3"], "W2-94": ["DAEO-m1u3"]}
    return text, deps.get(w2)


for w2 in ["W2-86", "W2-88", "W2-91", "W2-92", "W2-93", "W2-94"]:
    if w2 in ids:
        print(w2, ids[w2], "already filed")
        continue
    text, deps = prep(w2, (D / f"tickets/{w2}.md" if False else D / f"{w2}.md").read_text(encoding="utf-8"))
    title = re.search(r"^title: '(.*)'$", text, re.M).group(1).replace("''", "'")
    prio = re.search(r"^priority: (\d)$", text, re.M).group(1)
    tid = subprocess.run(["tk", "create", title, "-p", prio, "--external-ref", w2], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    text = text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created)
    text = text.replace("deps: [DEPS-PLACEHOLDER]", "deps: []").replace("depends_on:\n- DEPS-PLACEHOLDER\n", "depends_on: []\n")
    path.write_text(text, encoding="utf-8")
    t = T(tid)
    if deps:
        t.deps(deps)
    if w2 == "W2-86":
        t.add("sources", "DEC-957", "DEC-954")
    if w2 == "W2-88":
        t.kpi_append("A store of another layout version is never read as missing or as current: the store's open path "
                     "(src/gov/store/loader.py, through layout.py) reads the layout version and refuses an older or "
                     "newer one with STORE_LAYOUT_STALE naming both versions, and gov rebuild rebuilds it; the main "
                     "tree's STORE_MISSING of 2026-10-30 (a store built before W2-03's span column) is a planted case "
                     "[DEC-957, CAP-20]")
        t.add("sources", "DEC-957")
        t.body_line("**DEC-957 (2026-10-30):** this ticket also closes MEMORY-SPEC-MAP gaps 4 (the store layout, "
                    "with the STORE_MISSING cause) and 5 (the large-repository measure, its Scale KPI). "
                    "`src/gov/store/loader.py`'s open path is added for the layout check (W2-03 is merged and closing: "
                    "split by function). The mapping of a query failure to STORE_MISSING in `retrieve.py` (W2-87's "
                    "file) is named for the retrieval tickets if the open-path check does not make it unreachable.")
    t.save()
    ids[w2] = tid
    MAP.write_text(json.dumps(ids) + "\n", encoding="utf-8")
    r = subprocess.run(["python3", str(ORCH / "tools/dor_hand.py"), tid], capture_output=True, text=True,
                       env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"})
    print(r.stdout.strip(), r.stderr.strip()[-300:])
    sha = commit(f"{w2} ({tid}) filed: {title[:90]} (DEC-957, DEC-954)", [path],
                 [f"Task: {tid}", "Implements: DEC-957, DEC-954", "Role: orchestrator"])
    print(w2, tid, sha)
