# W2-176 delta review (no cap; R8): CAP-33 independent review

- **Task:** DAEO-ktiw (W2-176)
- **Reviewer:** independent auditor, fresh read-only session, Opus 5.5
- **Probe:** head `3b6c5cb79d39`; base: the withdrawn approved bytes `3a580a4b4d42`
- **Delta:** `git diff 3a580a4b4d42..3b6c5cb79 -- template tests docs/changes`
- **decisions:** DEC-1141 (2)(3), DEC-1140 (1)(b), DEC-1118 (A) (replaced), DEC-1010, DEC-801, DEC-808, DEC-1073, DEC-1014

**Classification:** 2 findings, both in scope, ordinary work yes, consequence other. Neither blocks; no round is proposed.

## Verdict
w2-176-delta: **pass**.

The cap and the CTO-only branch are removed. Every session is reminded once per window at 85 % of its own model's window: 850k for a 1M model, 170k for a model not in the table. R8 is fixed: the text is built before the marker, and a failed build leaves no marker and retries.

## Checked
- **Hashes:** context_watch.py `213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242` and precompact.py `ee19c22dc02e8ed7207dc535e55744e233d527635729a4d37ef252c8fa7e12cf` equal CIT-P §2. precompact.py is unchanged since the approved bytes.
- **Scope:** three files, all in the ticket's allowed paths.
- **No cap:** `HANDOVER_CAP`, `is_cto` and `min()` are gone. `DEFAULT_LIMIT = 200_000` is the unknown-model window that S2 requires. The role branch picks only which file the text names.
- **R8:** the committed planted case was red at `f50d59033` and green from `4dec7ec3c`, run in my own clone.
- **No-cap tests:** red at `e36a9c51b` (33 failed, 44 passed, matching the commit by name), green at head (77 passed; with the precompact file, 95).
- **`tests/unit/hooks` at head:** 193 passed, 2 skipped, 36 deselected. Two guard cases (`test_live_hook.py`, `rm -f ~/.bashrc`) failed because my scratch HOME sits under `/tmp`. They pass with the real HOME. This delta does not touch the guard.
- **Earlier rounds' findings still sound:** fail-safe, R1 re-arm, R2 subagent skip, sidechain skip, 256 KiB tail and 50 MB under 100 ms, state confinement, F1 (no decision key, only the state file written, no bytecode). R3 and R6 remain rows.

## Wording only the CTO saw before, now gone
Before, the duty clause read: "the RESUME HERE section of `<root>/.gov-runtime/scratch/orchestrator/CHECKPOINT.md`, `<root>/governance/project/orchestration/packages/DECIDED-NOT-DONE.md` and `<root>/.gov-runtime/scratch/orchestrator/log/report-state.json`".

Now it reads: "your CHECKPOINT, `<root>/.gov-runtime/scratch/orchestrator/CHECKPOINT.md`".

The names DECIDED-NOT-DONE.md and report-state.json are gone. The read-first line is unchanged.

## Findings
### F1: the CTO's reminder no longer names DECIDED-NOT-DONE.md or report-state.json; S2 as amended at 448e9faf4 still lists them
- **Behaviour:** the orchestrator on the coordination ticket now gets the same text as any main-tree orchestrator. DEC-1141 (2) ordered the CTO-only branch removed, but S2's file list was not amended to match. S2's verify line passes.
- Ordinary work: yes, because every CTO session at 85 % gets the shorter text.
- Consequence: other.
- Scope: in.
- **Reversed by:** a decided item lost through a CTO compaction because the file went unnamed ("loses work"), or an owner ruling that the wording was meant to stay ("fail").
- **Options:** (a) amend S2 to drop the two names, with no new bytes (recommended); (b) name both files for every main-tree orchestrator located by `checkpoint_rel`, with no ticket branch and no cap. Option (b) is new bytes and needs a short re-review.

### F2: the record's `decisions_carried` lists DEC-1118 and not DEC-1141
- **Behaviour:** the record's front matter keeps the replaced DEC-1118 (A) and omits DEC-1141. The body cites DEC-1141 correctly.
- Ordinary work: yes, because a reader of the front matter gets the replaced rule.
- Consequence: other.
- Scope: in.
- **Reversed by:** a rule that `decisions_carried` lists only the original proposal's decisions.
- **Fix:** ride along with the approval edit (DEC-802).

## Not done
My own probe script was refused by the quiet-hours rule and queued for the morning package; I did not retry it in any form. Its points are covered by the committed cases run in my clone and by reading the code.

```verdict
{"kpis": [{"kpi": "w2-176-delta", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
