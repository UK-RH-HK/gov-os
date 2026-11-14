"""P-W2-88-L8-1 (a): rewrite the two verdict blocks' findings in JUDGEMENT.md's form; nothing outside the fences."""
import json
import re
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-88/docs/probes/DAEO-2bdu")

def f(fid, scope, ordinary, consequence):
    return {"id": fid, "scope": scope, "ordinary_work": ordinary, "consequence": consequence}

# Each value from the record's own text (line numbers in the commit body); N = the form's neutral (non-blocking) value.
R1 = {
    # round-1 l.88 + l.94/105/112: in scope, ordinary work yes, fails open
    "RV1-1": f("RV1-1", "in", "yes", "fails open"),
    "RV1-2": f("RV1-2", "in", "yes", "fails open"),
    "RV1-3": f("RV1-3", "in", "yes", "fails open"),
    # minors l.117/124/130/135/140: "Ordinary work: yes. Consequence: other."; scope: under this ticket's KPI, triage "fix"
    "RV1-4": f("RV1-4", "in", "yes", "other"),
    "RV1-5": f("RV1-5", "in", "yes", "other"),
    "RV1-6": f("RV1-6", "in", "yes", "other"),
    "RV1-7": f("RV1-7", "in", "yes", "other"),
    "RV1-8": f("RV1-8", "in", "yes", "other"),
    # package items l.88/142-146: no ordinary_work or consequence given -> N ("no", "other"); B-1.3 "fails closed" (l.85)
    "RV1-9": f("RV1-9", "in", "no", "other"),
    "RV1-10": f("RV1-10", "in", "no", "other"),
    "RV1-11": f("RV1-11", "in", "no", "other"),
}
R2 = {
    # round-2 l.43-56: round 1's findings "fixed"; the record gives them no ordinary_work or consequence -> N
    **{k: f(k, "in", "no", "other") for k in R1},
    # l.77 + l.90: in scope, ordinary work yes, loses work
    "RV2-1": f("RV2-1", "in", "yes", "loses work"),
    # l.96: "Ordinary work: yes. Consequence: other."; triage "fix with RV2-1"
    "RV2-2": f("RV2-2", "in", "yes", "other"),
}

LINE = re.compile(r'^(\{"kpi": "[^"]+", "verdict": "(?:pass|fail)", "findings": )(\[[^\]]*\])(\}),?$')

for name, table in (("PR-DAEO-2bdu-round-1.md", R1), ("PR-DAEO-2bdu-round-2.md", R2)):
    path = ROOT / name
    lines = path.read_text(encoding="utf-8").split("\n")
    start = lines.index("```verdict")
    end = next(i for i in range(start + 1, len(lines)) if lines[i] == "```")
    before = json.loads("\n".join(lines[start + 1:end]))
    for i in range(start + 1, end):
        m = LINE.match(lines[i])
        if not m:
            continue
        ids = json.loads(m.group(2))
        comma = "," if lines[i].endswith(",") else ""
        lines[i] = m.group(1) + json.dumps([table[x] for x in ids]) + m.group(3) + comma
    after = json.loads("\n".join(lines[start + 1:end]))
    # same KPIs, verdicts, overall and finding ids, in order
    assert [(k["kpi"], k["verdict"], k["findings"]) for k in before["kpis"]] == \
        [(k["kpi"], k["verdict"], [x["id"] for x in k["findings"]]) for k in after["kpis"]]
    assert before["overall"] == after["overall"]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(name, "rewritten;", sum(len(k["findings"]) for k in after["kpis"]), "findings")
