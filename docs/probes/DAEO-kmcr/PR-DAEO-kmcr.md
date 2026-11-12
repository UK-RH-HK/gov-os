---
type: probe
task: DAEO-kmcr
reviewer_session: 7cd1f104-151c-4ed5-8115-bff55fe8d0b4
implementer_session: eae7b551-2a08-43ed-9bff-1d06d5e1ab6b
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: d2034dcf1478b1a6ba149f8dabcce305eaba00a2
owner_exception: P-W2-23-8 (a), DEC-1142 (2)
decisions_applied: DEC-954, DEC-1010, DEC-1052, DEC-1112, DEC-1142
---

# Probe record: W2-23 (adoption safety on a real repository), FULL: rounds 1 and 2, and the fix of R2-1 verified by the lead in place of a third round

**The owner's exception, stated first.** DEC-1010 allows two review rounds. Round 2 failed S3 on one finding, R2-1.
The owner decided P-W2-23-8 (a) (DEC-1142 (2), ACCEPTED, 2026-11-12): fix R2-1, with one test case from the test
designer, and let **the lead's verification stand in place of a third review round**. No independent auditor probed
`d2034dcf1478`. The last reviewer, round 2's (`7cd1f104-151c-4ed5-8115-bff55fe8d0b4`), probed `3e7194a45a58`. The
step from `3e7194a45a58` to `d2034dcf1478` is the integrate merge-back, the R2-1 test and the R2-1 fix, and the lead
(orchestrator, run 5) verified it as recorded below. `judgement: pass` is the orchestrator's judgement under that
exception. It is not a reviewer's READY at this head.

## Round 1 (probe head `fd1bc056f5ba`): NOT READY on S3

- Reviewer: a fresh independent auditor, session `bb401577-a555-4b31-867c-1909c88adde2` (claude-opus-5-5, high,
  read-only). It wrote nothing.
- Verdict:
  - S1, S2, S4, S5, S6, S7 and F1 pass.
  - S3 fails on R1 and R2, both fails-open: a folder or `../` tail citation that ends a sentence is missed, and the
    store's folder was taken per file.
- Triage:
  - R1 and R2 went to the fix round (the CTO's P-W2-23-7 (a)).
  - R3 to R9 are rows (see below).

## Round 2 (probe head `3e7194a45a58`, S3 only, the last round under DEC-1010): NOT READY on S3

- Reviewer: a fresh independent auditor, session `7cd1f104-151c-4ed5-8115-bff55fe8d0b4` (claude-opus-5-5, high,
  read-only). The tree was clean at the start and at the end.
- The fix round before it:
  - The test designer (td-4b, session `22513854`) added `9dc7b24af`, merged by `4111fab26`.
  - The engineer (eng-4, session `65b05ac9`) added `3e7194a45`.
- R1 and R2 are fixed through the A8 call path. No other form of Interface item 6 got worse, and the change only
  adds matches.
- **R2-1** (in scope, ordinary work, fails open), which blocks:
  - A folder citation ending in `?` was not found: `legacy/memory?`, `legacy/memory/?`, `notes/memory?`.
  - Cause: `?` was in `_NOT_MORE_PATH_DIR`'s blocking set as a glob character, and the glob reading of the token
    matched no store file.
- **R2-2** (in scope, consequence other, fails closed with a named refusal), a row:
  - One A8 run's memory-store entries are one store, so a bare mention of their common parent folder holds them back.

## The fix of R2-1 (P-W2-23-8 (a)), verified by the lead (run 5)

- `8024d54fa`: merge-back of `w2/integrate` (`7305b945f`). One conflict, the import line of `src/gov/adopt/stages.py`,
  resolved by keeping both sides (`lite_gates, project, safety`).
- `d3dfb5796`: the test designer (td-5, session `e9f4cafd-689f-42e7-8984-ed33f97cb6ac`, claude-sonnet-5-5, high, C2)
  added `test_s3_a_folder_citation_ending_a_question_is_found`, merged by `dc4123993`.
  - Its parameters are `flat-no-slash` (`legacy/memory?`), `flat-slash` (`legacy/memory/?`) and `nested-no-slash`
    (`notes/memory?`). Before the fix, all three were red in its run: A8 retired the store.
  - A fourth parameter, `glob-question-inside` (`legacy/memory/decisions/leg-00?.md`), was green before the fix and
    guards the glob reading.
- `d2034dcf1`: the engineer (eng-5, session `eae7b551-2a08-43ed-9bff-1d06d5e1ab6b`, claude-sonnet-5-5, high, C2)
  changed `src/gov/adopt/safety.py` and `tests/unit/adopt/test_safety.py`:
  - `_NOT_MORE_PATH_DIR` is now `(?![.?]*[\w/*\[-])`. A `?`, or a run of `?` and `.`, that ends a folder citation is
    a question's stop. A `?` followed by more path still blocks the folder form.
  - In the glob token loop, a trailing `?` is read both ways, as a glob character and as a stop. In doubt the token
    cites the store, so a retirement is held back.
  - New unit cases were added; the docstring now names the `?`.
- The lead's verification at `d2034dcf1478`:
  - `gov accept W2-23`, through heavy_slot.sh outside the sandbox: outcome pass, **33 passed, 0 failed**. By KPI line:
    S1 2, S2 4, S3 13, S4 3, S5 4, S6 4, S7 2, F1 1.
  - `tests/acceptance/W1-41/test_w1_41_migration.py`: 3 passed.
  - The lead probed `safety.citations` directly with 21 inputs (`r2-5.py`). Found:
    - the three R2-1 texts, plus `notes/memory/?`, `legacy/memory?!`, `(legacy/memory?)`, `legacy/memory??`,
      `"legacy/memory?"` and `legacy/memory?.`, each as `folder` with the stop left out of `found`;
    - `Is it legacy/memory/*.md?` as `glob`;
    - `legacy/memory/decisions/leg-00?.md` as `glob`;
    - `See ../memory/index.md?` as `relative tail`.
  - Not found, as wanted: `legacy/memory?x`, `legacy/memory/?.md`, `legacy/memory.db?`, `legacy/memory2?`,
    `Is it in notes/?` (a folder above the store's folder), and `Is it legacy/memoryx/*.md?`.
  - The one input the lead expected found and the code did not find was `legacy/memory/decisions/leg-00?`. That
    glob matches no store file (each store file ends in `.md`), so the code is right and the lead's expectation was
    wrong.
  - The rebuild was ok.
  - lead_verify: `lead_verify.sh` at `d2034dcf1478`: 4358 tests, 7 failed, 0 errors, 6 skipped (`log/verify/parallel.xml`), none of them this ticket's. Six are the W2-96 signal cases in `tests/unit/accept` (`test_w2_96_review3` r14, `test_w2_96_review4` r16, and `test_w2_96_run2` r9/r12 x4), the shared base reds named by the CTO until W2-177 lands; they were the same in run 4. The seventh, `tests/unit/resources/test_w2_157_backstop.py::test_s1_below_then_above_the_limit_pauses_at_the_second_reading`, came in with the integrate merge (W2-157). Re-run alone once it passed (`log/w2-157-alone.txt`, 1 passed in 0.25 s), and `src/gov/resources` and `tests/unit/resources` are the same at this head and at `w2/integrate` `7305b945f`, so it is load-sensitive.
- The lead read the fix's diff (`dc4123993..d2034dcf1`, `safety.py`). The change is limited to the folder lookahead
  and the glob token loop, and no other form or function changed.

## Residual rows (not blocking; recorded for Wave 3)

| id | KPI | where | finding | consequence |
|---|---|---|---|---|
| R3 | S3 | safety.py (glob loop) | leading-wildcard and brace globs are skipped on purpose (imported rules carry `**/*`) | fails open, not ordinary work |
| R4 | S2 | merge.py:97, :117 | CRLF written back as LF; JSON re-indented; every line, key and order kept | other |
| R5 | S2 | merge.py:127-129 | other generated files not refreshed on a second run (out of scope) | other |
| R6 | S4 | stages.py (a4) | the A4 plan still names the shared ref `rollback/batch-<n>` | other |
| R7 | S1 | legacy.py:98, :251, :262 | an ignored file at an A8 import target is overwritten, and deleted if the stage fails | loses work, not ordinary work |
| R8 | S1 | stages.py (restore) | a concurrent write to a planned target mid-run is deleted by the restore | loses work, not ordinary work |
| R9 | S4 | safety.py:213-217 | a kill inside one `git mv` is refused, not resumed | other |
| R2-2 | S3 | safety.py (`_folders`), legacy.py:222-225 | one A8 run's memory-store entries are one store: two stores under one parent are held back by a bare mention of the parent | fails closed, named refusal |

Records: the lead's records under `.gov-runtime/scratch/lead/`:
- reviews: `log/rev-1.result.md`, `log/rev-2b.result.md`;
- packages: `packages/P-W2-23-run3.md`, `packages/P-W2-23-run4.md`;
- run 5's evidence: `log/accept-5.txt`, `log/w1-41-5.txt`, `log/r2-5.txt`, `log/rebuild-5.txt`, `log/verify/`.
