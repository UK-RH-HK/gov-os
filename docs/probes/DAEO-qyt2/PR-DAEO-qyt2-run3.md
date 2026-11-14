---
type: probe
task: DAEO-qyt2
reviewer_session: "independent-auditor au-3 77ed47a8-c74c-42d1-badb-cbaaa088cead (the narrow independent check of run 3's test revision only, DEC-1156 (7); launched read-only by W2-185's lead through gov launch, claude-opus-5-5 high, class C2, 2026-11-14); not an author of the change"
implementer_session: "independent-test-designer td-4 5a4643b6-9496-4788-bcdf-48ce6fc31844 (4808016acb5c); merges 6b4bafb7197cf6f7f03fb1d4f8c8b73726c58005 (w2/integrate e2a0d6191) and 997e25f1e9c670b17c7db880319d96c2119e4a44 (the tests) by the lead"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 997e25f1e9c670b17c7db880319d96c2119e4a44
---

# Probe record: W2-185 (DAEO-qyt2), the narrow independent check of run 3's revision, on 997e25f1e9c6

task: DAEO-qyt2
decisions_applied: DEC-1167, DEC-917, DEC-1156, DEC-801, DEC-808, DEC-1010

## Scope

The CTO's P-W2-185-REDS-2 (a), under DEC-1156 (7), widened the ticket by `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py`.
Two of its `[PostToolUse]` cases still expected one entry where DEC-1167 (4) adds the context watch beside the guard's
entry. A fresh independent test designer (td-4) revised both in one commit, 4808016ac, with `Rewrite-Reason: DEC-1167 (4),
DEC-1156 (7) (W2-185 run 3)`. A new helper, `_the_guard_line`, picks the guard's entry by its program. This check
judged only that revision, `git diff 6b4bafb71..997e25f1e` (one file), on three points:
1. each revised case keeps its point;
2. plants;
3. scope and trailers.

Since run 2's PASS at 16bddf807, the code under `src/` and `template/` has changed only by w2/integrate's own files,
merged cleanly in 6b4bafb71 (the reviewer checked this: `git show --cc 6b4bafb71 -- src template` is empty). The
reviewer's verdict block below is copied as returned; the lead writes no verdict over it.

## The reviewer's result, in short (its full return: the lead's `log/au-3.result.md`)

- **Point 1, each case keeps its point: pass.**
  - The guard's entry is picked by its program. With the two PostToolUse entries in swapped order, all 19 cases stay green.
  - Two guard entries, or none, are red. The line is still compared with the kernel template's exactly (DEC-917).
  - PostToolUse must hold exactly the guard plus the context watch (DEC-1167 (4)).
  - PreToolUse and PostToolUseFailure assert at least what they did before.
  - The lifecycle events are unchanged.
  - Nothing goes beyond DEC-1167 (4), and no skip, xfail, flaky or rerun mark was added.
- **Point 2, plants: pass.** Every plant went into the copy's `template/.rulesync/hooks.jsonc`, so the generated case runs
  through rulesync. Unplanted: 19 passed.
  - (a) A second `posttooluse.py` entry: both `[PostToolUse]` red (`assert 2 == 1`).
  - (b) The guard command changed by one character: both red.
  - (c) The guard entry removed: both red (`assert 0 == 1`).
  - Six more plants (d to i) behaved as expected: a doubled watch; the watch also under PreToolUse or under
    PostToolUseFailure; swapped order (green); a doubled `stop.py`; a one-character PreToolUse change.
  - Before: the base file against today's template gives 2 failed, 17 passed.
- **Point 3, scope and trailers: pass.** The commit touches only the widened file. Its trailers are in one final
  paragraph, and its `Implements:` ids come from `sources:`. The merge's tree equals 4808016ac's.

## The lead's runs on 997e25f1e9c6

- `gov accept W2-185`: pass, 18 passed, 0 failed (`log/accept-997e25f1e.txt`).
- The widened file, the eight run-2 files, W2-185's own cases, program_env, W2-23 S6 and W1-38 rulesync, all with
  `--optin lifted,breadth`: 327 passed, 2 failed (`log/cases-997e25f1e.txt`). The 2 are `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource`
  and fail the same way on w2/integrate e2a0d6191 alone (`log/rulesync-base-e2a0d6191.txt`).
- `lead_verify` with `GOV_TESTS_OPTIN=lifted,breadth`: parallel 10734 tests, 14 failed, 0 errors, 27 skipped; serial 2
  entries, 10 tests, 0 failed (`log/verify/summary.txt`).
  - The two `[PostToolUse]` reds of run 2 are gone.
  - The 14 that remain are the 14 run 2 classified, and all 14 fail on w2/integrate e2a0d6191 alone
    (`log/reds14-base-e2a0d6191.txt`, 14 failed). None is in `skip_known.json`.

## Findings

Classification: no findings. No round proposed.

## Verdict (the reviewer's, as returned)

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```
