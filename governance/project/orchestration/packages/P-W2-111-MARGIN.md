# P-W2-111-MARGIN (b): the live guard hook is over its 100 ms bound after ACT-GUARD-FIX-6 (DEC-1186 (2): "if Bash calls go over 100 ms, bring it at once")

## 1. Context
W2-111 (DAEO-qvff) made the product guard hook meet 100 ms at p95 for Bash and many-tree calls. The live hook
(`.claude/hooks/`) is a separate copy. ACT-GUARD-FIX-6 (applied 17:31, fa6135903) brought it to W2-42a's parser,
closing the paired-apostrophe gap that withdrew ACT-GUARD-FIX-5. Its review predicted about 50 ms more per call.
DEC-1186 (2) asked for a measure right after the apply.

## 2. What happened: the measure (W2-111's method)
The hook's own CPU time per call (the hook process and its children), less a reference hook's, p95 over rounds of
40. Measured on the live repository (41 worktrees), 17:33-17:55, load 14-28. Evidence:
`~/gov-os-runs/W2-111/gf6-measure/run-gf6.log` and `result-gf6-after.json`.

| Case group | After ACT-GUARD-FIX-6 | Before (11-14, the same method) |
|---|---|---|
| Bash, five forms (ls, pipeline, write, git status, grep\|wc) | 112-208 ms, all FAIL | 103-167 ms, FAIL |
| Role-checked Read, Write, Edit, NotebookEdit (engineer, test designer, auditor) | 127-153 ms, FAIL | 87-97 ms, PASS |
| No-role Read and Write, Glob, Grep | 71-106 ms, PASS (Edit-engineer passed in round 2) | PASS |

Decisions were unchanged (allow and deny as expected).

## 3. Why it matters
The 100 ms bound is a working-speed bound on every agent tool call, CAP-level (W1-02, W1-05, W2-57). It is not a
safety bound: every refusal still holds, and the hook fails closed. Each call now costs about 40-50 ms more. Over
thousands of calls a day that is real wall time for leads and workers, and the live hook no longer meets the bound
the product meets.

## 4. Options
- **(a) Reopen W2-111 (no new ticket) for the live hook's two costs, then the live-hook ACT's round 2.**
  - Port W2-111's two speed-ups into the live hook: the install check's PATH read once per session, and only the
    target's trees judged (its r4 return names the functions and lines).
  - Cut the hook's fixed ~50 ms of imports and YAML load (`decide.py`, the held-out and parts loaders): lazy imports,
    a parsed-once cache.
  - The second cut touches kernel files, so it needs the owner's approval of the kernel bytes at the land.
  - Then one live-hook ACT (ACT-GUARD-FIX-7) carries both, rehearsed and reviewed, with the owner's yes.
  - Cost: about one day (one FULL lead run plus the ACT's build, review and apply). Risk: medium (the guard).
- **(b) A new ticket for the same work.** The same cost, plus your P1 for a new ticket (DEC-974); no advantage over (a).
- **(c) Accept the live hook over 100 ms until Wave 3.** No cost now. Every agent call stays about 40-50 ms slower,
  and the live hook stays outside the bound the product meets.
- **(d) Undo ACT-GUARD-FIX-6** (`undo ACT-GUARD-FIX-6 6e6c3927`). The role cases return under 100 ms, but Bash stays
  over (103-167 ms), and the paired-apostrophe write gap (a fail-open) reopens. Not recommended.

## 5. Recommendation
**(a)**, confidence medium-high. Keep ACT-GUARD-FIX-6 applied meanwhile: the slowdown fails closed, and undoing it
reopens a fail-open gap. Threat-model classification of the finding: ordinary work yes (every call), consequence
other (speed, not a refusal lost).

## 6. What it blocks, and the cost of waiting
It blocks nothing: EXAMIN's W2-27 and the leads run, about 40-50 ms slower per call. Each day of waiting costs that
on every call machine-wide.

**Your line:** `P-W2-111-MARGIN (a)` (or (b), (c), (d)).
