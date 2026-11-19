# Lead brief: the test suite's cuts TI-2, TI-6, TI-5, then TI-7 (the owner, DEC-1220 (1))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (worktree, the machine rule, memory first, trailers,
models). Name: `ti-cuts`; worktree `/home/usain/gov-os-worktrees/E2-ti-cuts`, branch `e2/ti-cuts` from `w2/integrate`.
**Kind of work:** test retirements and a test tier, plus removing code that only retired tests use. **No ticket**
(DEC-1219 (6)): test commits are the test designer's (`Role: independent-test-designer`, `Task: chore`,
`Rewrite-Reason:` naming DEC-1220 and the audit row); code removal is the engineer's (`Role: engineer`, `Class: C`,
`Task: chore`).

**Read:** DEC-1220 in `docs/DECISION_REGISTER.md`; the audit `docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md` (all of it:
§3 and the table are your work list); the inventory `docs/emergency-2/TEST-INVENTORY-2026-11-19.md` §3.

## Not yours (leave these exactly as they are)
- **TI-1** and **TI-3** (the strict close's tests, `judge_commits`, the secrets-scan tests): they retire with L2's B1, a
  later change. Rows marked `retire (B1)` stay.
- **TI-4** (`breadth` weekly) and the scratch tools' cases in `tests/unit/orchestration` and `acceptance/W2-97`: they go
  with the cut-over (W2-207) and Gov OS's move onto `gov queue`.
- Anything in `src/gov/launch/**`, `src/gov/queue/**`, `gov update` and the kit template: two leads work there now.

## Your work, one commit (or a few) per step, in this order
1. **TI-2, the retired surfaces that are retired today:** W2-159, `tests/unit/session_watch`, and the other rows the audit
   marks `retire` with an A-2 or E2 basis that is already in force. Delete the folder or the cases; keep the fixtures other
   suites import (the audit names them).
2. **TI-6, the tests that pin past records and guard-era rules:** W2-49's CIT-P cases, W2-130, W2-61's line-pinned gold
   sources, W2-51 (audit 07 C-5), W1-01 `bootstrap_record`, W1-05 `switch_over_record`, W1-48 `sandbox_prereqs`, W2-33
   `install_rule`, W2-188 `citp`; the held-out `Read` deny-rule cases (W1-38, W1-28, W1-50, W1-27, W1-46: 59 cases)
   **together with** `gov.util.heldout` and `held-out.yaml` if nothing live uses them (grep `src/`, `template/`, hooks;
   if something live does, keep the code and say what); the 39 hit@k floor cases (W1-19, W1-21, W2-61: EMERGENCY-2 5.2,
   hit@k is no floor: keep each case's measurement if it proves something live, drop the pass line). Keep what guards the
   present (W1-01's authorship rule stays).
3. **The doubtful rows the CTO settles:** the six `retire ?` (W1-42, W2-51, W2-72, W2-113, W2-130, W2-182) and the
   `keep ?` / `thin ?` rows. Rule (the CTO's): retire only when what the case asserts is retired by EMERGENCY-2 or a
   decision from DEC-1211 on, or it is a copy of a kept case; otherwise keep. **W2-72 and `unit/containment` test
   `judge_commits`: leave them for B1.** `gov.tasks.bridge` (W1-14, `unit/bridge`): if nothing in `src/`, `template/` or a
   hook imports it and `gov discover` covers its job, retire the module and its tests; otherwise keep and say why.
   List each settled row with its verdict and reason in your return.
4. **TI-5, the weekly tier:** the 17 `weekly tier` folders' slow cases (over 5 s in the audit's run) move out of the
   default run into a weekly opt-in tier, using the mechanism the suite already has for opt-in sets (`lifted`,
   `breadth`: find it, `tests/unit/optin` tests it); one fast case of each folder stays in the default run. Name the
   tier `weekly`. The nightly and `gov queue --full` keep running the default run; the weekly run is
   `<the opt-in switch> weekly` (state the exact command in your return). Also W1-16's code-graph cases, W1-01's
   merge-walk case and W1-26's planted-defects case (the audit's +493 s).
5. **TI-7, last:** the large parameter sets (W2-94, W2-98, W2-153, W2-11, W2-69's non-B1 part): thin to boundary cases
   where cases differ only in a planted string. The test designer proposes each cut in the commit message (from N to M,
   why the kept ones cover the rest).

## Green and return
- After each step: the folders you touched, `tests/unit/optin`, and a `--collect-only` of the whole default run (no
  collection errors). Through the slot, `-n auto`, as LEAD-COMMON says. No full suite: the CTO runs it.
- **Do not merge.** The CTO lands the branch after the green base of release 0.1.4. Keep the branch mergeable with
  `w2/integrate` (merge it in before you return).
- Return: branch and head; per step the commits and the case counts removed or moved (default run before and after,
  from `--collect-only`); the settled doubtful rows; anything that surprised you.
