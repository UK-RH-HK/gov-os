"""Build docs/probes/DAEO-g87r/PR-DAEO-g87r-gold.md: the lead's front matter and summary, then au-2's record verbatim."""
from pathlib import Path

LOG = Path("/home/usain/gov-os-worktrees/W2-94/.gov-runtime/scratch/lead/log/au-2.result.md")
OUT = Path("/home/usain/gov-os-worktrees/W2-94/docs/probes/DAEO-g87r/PR-DAEO-g87r-gold.md")

result = LOG.read_text(encoding="utf-8")
cut = result.index("# Probe record: W2-94 GOLD")
body = result[cut:].split("\n", 1)[1].lstrip("\n")

head = """---
type: probe
task: DAEO-g87r
reviewer_session: c3eb75b3-0434-4362-9f9c-afaaed5a4e22
implementer_session: afd71a8e-9188-42a7-b9be-9a3deb5f4ba6
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 19e9739430ba5d9e1a9e01ab071814c161592269
decisions_applied: [DEC-957, DEC-828, DEC-820, DEC-845]
scope: "W2-94 GOLD: the change to check_gold.py only, (i) to (iii) and the guard cases"
---

# Probe record: W2-94 GOLD (DAEO-g87r), the narrow independent check of the change to `check_gold.py`

## Summary

- **What was probed.** Head `19e9739430ba5d9e1a9e01ab071814c161592269` of `w2/W2-94`: the one-file change to
  `fixtures/evaluation/examin/check_gold.py` (commit `19e973943`, base `6c7772ef6`), against the owner's W2-94 GOLD
  (2026-11-13; to be recorded as DEC-1175, not yet in the register) changes (i) to (iii) and the guard cases. The
  GOLD cases came first, from the independent test designer (`133b79626974`, merged `95ac3ec049bb`; 29 red against the
  unchanged script). The question set is not in the tree; neither the lead, the engineer nor the reviewer read it.
- **Who wrote it.** An engineer: session `afd71a8e-9188-42a7-b9be-9a3deb5f4ba6` (`19e973943`).
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, Opus, effort high, session
  `c3eb75b3-0434-4362-9f9c-afaaed5a4e22`, 2026-11-13, started through `gov launch` under its OS sandbox; its brief
  carried `governance/project/briefs/JUDGEMENT.md` word for word. It wrote nothing in the repository: the lead's
  tripwire shows no change in this worktree and `git status` is empty after its session.
- **Verification at this head.** `gov accept W2-94` pass, 463 passed 0 failed; the scoped run (`lead_verify`, DEC-968)
  GREEN, 5744 tests, 0 failed, 0 errors, 6 skipped.
- **The lead's judgement: pass.** 4 findings, all scope out. F1 and F2 are ordinary work yes and fail open, but each is
  the owner-decided rule implemented to the letter ((i) with the unchanged rule 2b; (ii)'s substring segments), so they
  go to the owner as rows; F3 and F4 are ordinary work no, Wave 3 rows. No finding is in scope, ordinary work yes and
  fails open or loses work, so none blocks and no round follows (DEC-1010 item 1).
- **Rows for the CTO and the owner.** F1 and F2: the reviewer's option (b) is a read-only count on the real set before
  the close (answers that lost every token under (i) and have no content word; path tokens held only by the segment
  rule); 0 in each means the row is not realised in this set.

## The reviewer's record (verbatim)

"""
OUT.write_text(head + body.rstrip("\n") + "\n", encoding="utf-8")
print(OUT, len(head + body))
