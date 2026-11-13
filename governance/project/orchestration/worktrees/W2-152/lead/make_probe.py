"""Compose the probe record from round 2's reviewer return (its session's final message, verbatim)."""
import json
import sys

LOG = "/home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/W2-152-review-r2.json"
OUT = sys.argv[1]

text = open(LOG).read()
dec = json.JSONDecoder()
last = None
i = 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
        if isinstance(obj, dict) and "result" in obj:
            last = obj
        i = end
    except ValueError:
        i = j + 1

assert last and last.get("session_id") == "57de2180-58f9-4a52-8041-8b7e6f345469"
result = last["result"].strip()

head = """---
type: probe
id: PR-DAEO-o5x1
task: DAEO-o5x1
reviewer_session: 57de2180-58f9-4a52-8041-8b7e6f345469
implementer_session: 57fb2b5d-d97e-4e6c-9399-68c22586d1f7
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 09fc68645c0c36580f94077e37255ca511c4b3c2
---

# Probe record: W2-152 (DAEO-o5x1), review round 2, the last (DEC-1010)

- **Probed:** head `09fc68645c0c` of `w2/W2-152` (the fix round for round 1's F1, F3, F4, F6 and F5), against
  `w2/integrate`. Round 1 (`16d052d2fda7`) was NOT READY on F1: `governance/project/orchestration/reviews/w2-152-r1.md`.
- **Reviewer:** a fresh independent-auditor session (session above; `gov launch`, OS sandbox, read-only), launched by
  the CTO on 2026-11-09 with the brief `.gov-runtime/scratch/brief/W2-152-review-r2.md`. It wrote nothing in any tree;
  the tripwire showed no change in this worktree (changes only in other trees, by their own sessions).
- **Implementer:** the fix-round engineer (session above); the first build was session `a9809203-73a6`.
- **Commissioned and judged by:** the orchestrator. The reviewer's verdict is READY; the judgement `pass` is the
  reviewer's own, computed from its `verdict` block below (no finding that is in scope, ordinary work yes, and fails
  open or loses work; DEC-1010 item 1). No verdict is written over the reviewer's.
- **After the probe:** the CTO merged `w2/W2-152` (`b0bbd373f8a3`) and the designer's tests branch (`dea78270a`) into
  `w2/integrate`; the branch then took `w2/integrate` back twice (`6dc3db850050`, `e25bdca86bc1`), both merges made by
  git without a conflict. In the ticket's own paths the only change after the probed commit is the designer's
  `32b89d25a578`: one comment line in `tests/acceptance/W2-152/test_w2_152_rev2.py`, so that `gov links` reads no
  planted id as unknown; no test's behaviour changed. The branch's tree at `e25bdca86bc1` is `w2/integrate`'s tree at
  `33b5651eb65d`. No re-probe is due (DEC-895: no merge resolved a conflict in a judged file). The ticket's profile is
  STANDARD. The lead's resume on 2026-11-12 tried a re-probe of the merged head, as the CTO's brief asked; the launcher's
  resource gate refused it twice (memory, DEC-1088 (5)), and the lead stopped there (DEC-1142 (9)).
- **The lead's verification of `e25bdca86bc1` (2026-11-12):** rebuild exit 0; `gov accept W2-152` 67/67 (every KPI
  line pass); the scoped selection (scoped, `core_changed` none, `unplaced` none) 4168 passed, 3 failed in the parallel
  phase, 90 passed in the serial phase. The three reds are not this ticket's: W2-153's two composition cases (red on
  `w2/integrate` until W2-175 merges; the branch's tree is integrate's) and W2-157's load-sensitive backstop case
  (passed alone).
- **Findings left as rows (Wave 3), as the reviewer and the CTO class them:** F7 to F12 (round 1), F13, F14, F15
  (round 2). F2 was decided by the CTO as option (a). None blocks.

## The reviewer's record, verbatim (its session's final message)

"""
with open(OUT, "w") as fh:
    fh.write(head + result + "\n")
print("written", OUT, len(result))
