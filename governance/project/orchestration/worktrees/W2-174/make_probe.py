from pathlib import Path

T = Path("/home/usain/gov-os-worktrees/W2-174")
body = (T / ".gov-runtime/scratch/lead/log/au-1.result.md").read_text(encoding="utf-8").rstrip("\n")
head = """---
type: probe
task: DAEO-zmo4
reviewer_session: ccffb4da-397c-4cb4-8da5-4d8d20c8e8c1
implementer_session: ac8f55ac-c057-4f53-8cee-c78f5bddf205
test_designer_session: 4a5dfbba-55f7-4401-9ee8-3998e551b8e4
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 7920da077ac201ac5247cbeea23e8d60df4655a6
decisions_applied: [DEC-1130, DEC-1083, DEC-1050, DEC-1088, DEC-1121, DEC-1122, DEC-1148, DEC-801, DEC-808, DEC-1010, DEC-820]
scope: "W2-174 narrow independent check: the Verify pass (gov adopt --verify-list, --verify-apply) and the facts step (gov adopt --facts), KPI lines S1-S5 and F1-F3"
---

# Probe record: W2-174 (DAEO-zmo4), the narrow independent check at 7920da077ac2

## Summary

- **What was probed.** Head `7920da077ac201ac5247cbeea23e8d60df4655a6` of `w2/W2-174`, from the base `f2b1d38af`:
  - the engineer's `e993a91af` (the Verify pass) and `de83f12ca` (the facts step), session
    `ac8f55ac-c057-4f53-8cee-c78f5bddf205`;
  - the independent test designer's `638f5be5f` (`tests/acceptance/W2-174/`, 94 cases), session
    `4a5dfbba-55f7-4401-9ee8-3998e551b8e4`, merged by the lead at `7920da077`.
- **Who probed.** A fresh read-only independent auditor (`claude-opus-5-5`, effort high), session
  `ccffb4da-397c-4cb4-8da5-4d8d20c8e8c1`, started through `launch_worker.sh` (`gov launch`, its OS sandbox, the
  reading tools alone), with JUDGEMENT.md word for word in its brief. It wrote nothing; the lead commits its return
  below word for word.
- **The lead's evidence it judged.** `gov accept W2-174` 94/94 pass at `7920da077` (S1 9, S2 15, S3 2, S4 36, S5 12,
  F1 15, F2 2, F3 5, none unmapped); `lead_verify` 5,897 tests, 2 red, neither this ticket's:
  `tests/acceptance/W2-23/test_w2_23_space.py:94` (S6, the CTO's known red) and
  `tests/unit/retrieval/test_w2_112_shared_reranker.py:563` (load-sensitive; green alone, 33 passed).
- **Verdict.** Pass on all eight lines. Four findings, all in scope, ordinary work yes, consequence other (each fails
  closed): rows, no round (DEC-1010 item 1). F1 and F2 are optional Wave 3 hardening; F3 and F4 are information for
  W2-27's CTO.

## The auditor's return, word for word

"""
out = T / "docs/probes/DAEO-zmo4/PR-DAEO-zmo4.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(head + body + "\n", encoding="utf-8")
print(out, len(head + body))
