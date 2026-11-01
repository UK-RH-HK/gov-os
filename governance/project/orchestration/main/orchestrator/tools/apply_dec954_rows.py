"""DEC-954: W2-78's three list rows (TICKET-EDITS §6), W3-P12 (§3 W2-20), and the WBS rows of the tickets filed for
DEC-957's memory gaps; one decision-record commit each."""
import json
import re
import subprocess
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
from te_lib import ORCH, ROOT, commit  # noqa: E402

NEW = json.loads((ORCH / "log/tickets-2026-10-30d.json").read_text())
REC = ["Task: decision-record", "Implements: DEC-954", "Role: orchestrator", "Decided-by: owner (chat, 2026-10-30)"]


def scan(p):
    r = subprocess.run(["python3", str(ORCH / "tools/placeholder_scan.py"), str(p)], capture_output=True, text=True)
    assert "0 hit(s)" in r.stdout, r.stdout


H064 = ("| W2-H064 | `gov.check.pathmap` (core-pathmap) reports green without checking anything when the path map's "
        "`namespaces` is a mapping, which this repository's is: `src/gov/check/pathmap.py:47-49` returns no finding "
        "unless `namespaces` is a list. It also returns none when the path map cannot be parsed (`:40-45`). So \"every "
        "tracked path matches exactly one namespace\" is not checked here or in an adopted repository (found by W2-78's "
        "lead, 2026-10-30) | engineer | core-pathmap reads the mapping form the path map's schema states. It judges each "
        "tracked path against exactly one namespace, naming each path in none or in two. A path map that cannot be read "
        "or parsed is a finding, never green. Planted cases for both forms | W2-78's lead (DAEO-v4is, run 1, discovery "
        "3); P-W2-78-PARK §5; DEC-954 Q5. Ordinary work: yes, because every `gov check` here runs it. Consequence: fails "
        "open. **A package to the owner before any round (WBS §6); recommended: folded into W2-88** |")
L453 = ("| W2-L453 | `gates.RECORD_PREFIXES` (`src/gov/close/gates.py`) does not name `governance/project/records/`, so a "
        "`Task: decision-record` commit that edits a record file there is not measured as a record commit. It matters "
        "only once W2-78's record files exist: the folder is not on `w2/integrate` | engineer | `RECORD_PREFIXES` names "
        "the folder, in the same change that creates it (W2-78's resume) | W2-78's lead (discovery 6); P-W2-78-PARK §5. "
        "Ordinary work: no, not before W2-78 merges. Consequence: other. **Triage: Wave 3, with the parked W2-78** |")
L454 = ("| W2-L454 | W2-62's prompt-in-force acceptance case runs on stand-in prompts, not the live ones, so a change to the "
        "live prompt's form is not caught. The case is in the test map's `record_reading` set because W2-78's KPI named "
        "it | independent-test-designer | the case reads the live prompt of the wave in progress (or the stand-ins are "
        "generated from it), with `Rewrite-Reason:` naming this row; no expectation lowered | W2-78's test designer "
        "(discovery 8); P-W2-78-PARK §5. Ordinary work: yes. Consequence: other, a weak test, not a fail-open of the "
        "product. **Triage: Wave 3** (no exit criterion broken), or W2-67's next round if its brief has room |")

p = ROOT / "docs/plan/WAVE_2_LIST.md"
s = p.read_text(encoding="utf-8")
if "| W2-H064 |" not in s:
    lines = s.split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("| W2-H063 |"))
    lines.insert(i + 1, H064)
    i = next(k for k, l in enumerate(lines) if l.startswith("| W2-L452 |"))
    lines[i + 1:i + 1] = [L453, L454]
    s = "\n".join(lines)
    s = s.replace("### 3.1 high (62)", "### 3.1 high (63)", 1).replace("### 3.3 low (448)", "### 3.3 low (450)", 1)
    p.write_text(s, encoding="utf-8")
    scan(p)
    print(commit("Wave 2 list: W2-78's discoveries as rows W2-H064, W2-L453, W2-L454 (DEC-954 Q5, P-W2-78-PARK §5)",
                 [p], REC))

p = ROOT / "docs/plan/WAVE_3_PARKING.md"
s = p.read_text(encoding="utf-8")
if "| W3-P12 |" not in s:
    row = ("| W3-P12 | W2-20 machine-agnostic: on any machine the Gov OS reads its resources (CPU, memory, disk, GPU) and "
           "plans the execution to that capacity | the owner (DEC-954 Q12) | 2026-10-30 |")
    lines = s.split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("| W3-P11 |"))
    lines.insert(i + 1, row)
    p.write_text("\n".join(lines), encoding="utf-8")
    scan(p)
    print(commit("Wave 3 parking: W3-P12, W2-20 machine-agnostic (DEC-954 Q12)", [p], REC))

p = ROOT / "docs/plan/WAVE_2_WBS.md"
s = p.read_text(encoding="utf-8")
if "| W2-91 |" not in s:
    rows = [
        f"| W2-91 | B | **New (DEC-957, MEMORY-SPEC-MAP gap 1).** Full embeddings: the root files, `governance/**` and `schemas/**` embedded; the hidden half, generated copies and `cli/**` stay out (`{NEW['W2-91']}`) | implementation | engineer | STANDARD | W2-86 | 30 | CAP-10.a, DEC-957 |",
        f"| W2-92 | B | **New (DEC-957, gaps 2 and 3).** The knowledge graph and the code graph as routes of plain-question retrieval (`{NEW['W2-92']}`) | implementation | engineer | STANDARD | W2-87, W2-03 | 200 | CAP-12, CAP-13, CAP-18, DEC-957 |",
        f"| W2-93 | B | **New (DEC-957, gap 6).** W2-81's held-out half: hidden questions and planted-problem variants per synthetic repository (`{NEW['W2-93']}`) | audit | independent-auditor | STANDARD | W2-81, W2-84 | 0 | DEC-941, DEC-828, DEC-957 |",
        f"| W2-94 | B | **New (DEC-957, gap 7).** EXAMIN's question set, a visible and a hidden half, before W2-27; W2-61's KPI 6 moves here (`{NEW['W2-94']}`) | audit | independent-auditor | STANDARD | W2-84 | 0 | DEC-828, DEC-957 |",
    ]
    lines = s.split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("| W2-90 |"))
    lines[i + 1:i + 1] = rows
    s = "\n".join(lines)
    # the tk ids of the two drafted rows
    s = s.replace("(memory quick win a) |", f"(memory quick win a; `{NEW['W2-86']}`) |", 1)
    s = re.sub(r"(\| W2-88 \| A \| \*\*New \(DEC-954 Q9f; Wave 2's minimum\)\.\*\*)",
               r"\1" + f" (`{NEW['W2-88']}`; gaps 4 and 5 too, DEC-957)", s, count=1)
    p.write_text(s, encoding="utf-8")
    scan(p)
    c = REC[:1] + ["Implements: DEC-957, DEC-954"] + REC[2:]
    print(commit("WBS: rows W2-91 to W2-94 (DEC-957's memory gaps) and the tk ids of W2-86 and W2-88", [p], c))
