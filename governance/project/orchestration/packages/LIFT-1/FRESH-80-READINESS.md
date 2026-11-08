# The fresh 80's readiness: what the owner holds before deciding (2026-11-08, session `ad44f5fe`)

Written for the owner and the next CTO session. The owner's word of 2026-11-08: **hold the experiments' decisions
(FRESH-80-1, M3-ADOPTION-1, GLOSSARY-1); start nothing on the fresh 80 until the owner has decided.** Nothing here is
decided. FRESH-80-1 §2 holds the twenty fixes and §3.5 the fault rule, in full; this record holds the rest of the
report of 2026-11-08 (items 2 to 6).

## 1. A correction to the decisions that could change the 80's answers
The measured commit `c00d525f` (window 4, the pool on) was made at 14:46 on 11-07, **before** DEC-1089. At that commit
only DEC-1079 to DEC-1088 and tickets to W2-136 exist after the 80 were written (11-05). DEC-1089 to DEC-1096 and
W2-137 to W2-142 matter only if the 80 is measured at a later commit.

## 2. The checker's brief (the owner's operator's checker, outside the guard; only counts come back)
- **Task:** for each of the 80, re-read its gold answer and sources at `c00d525f`, in a clean clone checked out there;
  never the main tree, never the CTO's tools.
- **Mark each question:** *unchanged* (every fact true at `c00d525f`); *changed* (name the fact, give the corrected
  fact with new source and lines); *ambiguous* (the repository states it two ways).
- **Check above all:** ticket and decision statuses; anything superseded or amended (a decision's *Changed by* line);
  counts and figures; paths and function names that moved; the nonexistent-id question (its id exists nowhere).
- **The writer** updates only *changed* and *ambiguous* entries, one round, keeping the question and its category:
  - a *changed* entry gets the corrected fact and its new source, and **its commit field set to `c00d525fd420`**; the
    old label is kept in `memory-verdict-2/retired/` (never inside `hidden/`);
  - an *ambiguous* entry gets the second place as an alternative source, so the gold accepts either (as DEC-1078 (2)'s
    cross-check added whole places that also state an answer);
  - **the nonexistent-id question:** if its id now exists, flag it only and never change the question (FRESH-80-1
    item 6 drops it from every figure, decided before the run).
- **What the pre-flight checks, which the writer must respect:** no stray files (`*.yaml~`, swap files); the folder
  mode 700; unchanged files keep their modification times (edit in place, never copy the folder back); the number of
  files changed equals the entries re-labelled plus any later anchor fixes; **an ambiguous entry given an alternative
  source counts as re-labelled.**
- **To the CTO:** counts only (unchanged, changed, ambiguous, re-labelled, the nonexistent id flagged yes/no) and the
  new combined digest, computed exactly as: `cd <the set's folder> && LC_ALL=C sha256sum *.yaml | sha256sum`.
  (Corrected 2026-11-08 after readiness reviewer 7's F3 and F4.)
- **Cost:** about 1 to 2 hours.
- **What could have changed (11-05 to `c00d525f`):** DEC-1079 (mxbai dropped), DEC-1080 (the CTO's command rule),
  DEC-1081 (W2-128 filed), DEC-1082 (permissions), DEC-1083 (K9 bar 85 % on the fresh 80, W2-32 S6 dropped, W2-15b out
  of and W2-128 into K9), DEC-1084 (D9-FATES applied: W2-111, W2-55 S1, W2-66b, W2-90c; spill floor 2,048 MiB; exit
  criterion 5 re-worded), DEC-1085 (W2-134), DEC-1086 (S11 re-worded, the 4,000-character cap), DEC-1087 (window 4's
  items; the three layers back in Wave 2), DEC-1088 (`gov plan`; closed tickets never edited); tickets W2-128 to W2-136;
  window 4's code (W2-92, W2-32 S11, W2-131, W2-133, W2-134, W2-61h S7, W2-135, W2-116, W2-129, W2-112's release, D-6
  part 1); the register's growth shifting lines (re-anchoring handles it; FRESH-80-1 §2 item 2 counts it).

## 3. ACT-GUARD-SETS-1: decided, not applied (a miss), the patch out of date
- **Decided:** DEC-1084, apply right after re-pin window 4, the CTO's hidden-set tools converted first.
- **The tools:** converted 11-06 (`drafts/d4b/sets_form.py`: the sets root as an argument, ids and counts only).
- **Applied: no.** START-NEXT-SESSION of 11-07 did not list it; the CTO did not catch it.
- **`apply.sh check` on 11-08:** exit 1, "the files are neither as before nor as applied"; the live
  `.claude/hooks/pretooluse.py` (sha `e406653e…`) and `governance/project/path-map.yaml` (`6d79946f…`) moved since the
  11-06 build. It cannot be applied as built.
- **The reader-folder gap:** the ACT keeps `~/gov-os-eval/runs/**` open (results without question text), but
  FRESH-80-1 §2 item 7 puts the 80's reader rows (questions, gold, answers) under `runs/fresh-80/`. Add that folder to
  the hidden globs.
- **Left:** (1) an engineer rebuilds the patch against today's files, with the reader folder, in a clone; (2) the
  end-to-end rehearsal (DEC-1057); (3) the CTO's review; (4) the owner's operator applies (about 1 minute); (5) the CTO
  runs the guard check; (6) live worktrees merge integrate the same day. About 2 to 3 hours. **Before the 80's use.**

## 4. What a verdict at window 4 (`c00d525f`) covers for EXAMIN's release after the lift
| what the lift's release adds | effect on ranking | covered |
|---|---|---|
| W2-137 (request cap 64) | live hit@5 106 = E0, MRR within noise | yes |
| W2-138 (store commit in results, token commit) | fields only; bundles equal but the token key | yes |
| W2-136 (`gov plan`), W2-20 (launch gate) | not retrieval | not affected |
| W2-141, ACT-GUARD-SETS-1 (the guard) | who may read, not what search returns | not affected |
| W2-142 (search again in the kernel skills) | the practice measured, moved into skills | yes, if the wording stays |
| any G1 change (fewer scored pairs, lower rerank depth, a per-pair cap, a faster reranker) | changes ranking | **no** |
| the glossary as a separate lookup | not in the bundle (E2G: keep it out of the search path) | not affected |
| M3, if adopted later | changes ranking | **no** |

**If retrieval changes after the verdict:** before the release is cut, the 138 at the release commit: E0's retrieval
(35 minutes, no tokens) and E2's two-search run (about $22, 15 minutes), each against the verdict commit's run by
McNemar. Beyond the reader's spread (1 to 3): the verdict does not transfer; to the owner before the release. The 80 is
never used again. Proposed as a fixed step in the release's hash check (W2-27 item (a)).

## 5. Proposal: a final readiness review of memory before the 80 (not decided)
Seven independent, read-only reviewers in parallel; each one record with the JUDGEMENT lines and a verdict block; none
opens the 80 or any hidden or spent set.
1. The store and its refresh hook (W2-116): every merge refreshes; no mixed halves; the backstop; failure modes.
2. The links and status marks (W2-92, W2-129): status, in-force and changed-by right; superseded never read as current.
3. The register ids (W2-131, W2-133): every register chunk its own id; no DEC-999.
4. Chunking and the line cap (W2-135, drop-nested): cuts marked, lines unchanged; G3's overlapping slices and effect.
5. Role filtering and hidden-set protection: `gov retrieve` by role; ACT-GUARD-SETS-1's state and gap; no path for a
   measured role to the 80.
6. The search-again practice in the briefs: the three briefs, W2-128's and W2-142's lines match what E2 measured.
7. The fresh 80's own readiness: FRESH-80-1's twenty fixes, the scripts' one-shot and resume, the fault rule, the
   checker's brief; against the code, without opening the 80.

**Time and cost:** about 1 to 1.5 hours in parallel plus about 1 hour of triage; about 1.2 to 1.8M tokens of in-session
agents; no GPU, no graded runs. **Fixed before the 80:** findings in scope, reachable in ordinary work, that fail open
or would make the verdict wrong (at most two rounds); known already: ACT-GUARD-SETS-1 (rebuilt, with the reader
folder) and the fresh-80 scripts (FRESH-80-1 items 14 to 19). **Rows** (DEC-1010): the rest.

## 6. Everything else open that touches memory or the verdict
- **G3, overlapping slices:** to be decided after E0 (DEC-1090), still undecided. E3: today's bundle (overlaps
  included) is best of five. Recommendation: no change before the 80; a ticket after the lift if the review finds it
  worth it.
- **The fresh-80 scripts** (FRESH-80-1 items 14 to 19) not built; **the checker's pass** (§2) not run.
- **The search-again practice:** in the project briefs; the kernel skills by W2-142 at the lift; W2-128's line with
  W2-128.
- **W2-139 and W2-140** (Contract 4.3, about 279 files): the CTO holds their integrate commits until after the 80 (no
  change between the pre-flight and the 80; FRESH-80-1 item 13). A CTO hold, for the owner to confirm.
- **Harness-only:** E0b's 246 seed conflicts (batch padding, the harness only); W2-138's F1 (a store built from a tree
  with uncommitted edits hashes the edited files; a row; the measure clone is clean).
- **The older window scripts** `live_window.sh` and `score_once_window.sh` still carry the F1 restore defect fixed in
  `e4_window.sh`: never reuse them unfixed.
- **Decisions waiting:** FRESH-80-1 §5 (7 questions; configuration, commit, the K9 bar), M3-ADOPTION-1 §6 (keep the
  0.6B recommended), GLOSSARY-1 §9 (park recommended).
- **ADR-0002:** refresh against the register before the lift's re-pin (DEC-1093); it belongs with §5's findings.
- **The status block counts K9 as done** from stale tags (K7-W2-REMAINDER §5); a hand-kept fix is pending.

## 7. Readiness state, 2026-11-08 (DEC-1097)
| part | state | record |
|---|---|---|
| ACT-GUARD-SETS-1 | rebuilt (reader folder hidden, W2-84's cases deleted, the variable-path line rule), rehearsed 0 failures, `apply.sh check` exit 0; **waits on the owner's operator (§3)** | `packages/ACT-GUARD-SETS-1.md`; `drafts/sets-root-guard/REHEARSAL.md` |
| the fresh-80 scripts | built; code review READY at round 2; 74 tests; **pinned** (`FRESH80-REVIEWED.sha256`, 13 files, sha256 `b9a729fa…`) | `drafts/fresh80/README.md`; `reviews/fresh80-scripts.md` |
| readiness review (seven) | 1 store READY; 2 links READY (F3 mark committed `7a6dad58`); 3 ids READY; 4 chunking READY (G3: no ticket, fold into M5's retest); 5 roles READY but F2; 6 search-again READY; 7 the fresh 80 READY at round 2 | `reviews/readiness-<n>-*.md` |
| readiness 5 F2 | the writer's and checker's transcripts (`~/.claude/projects/-home-usain-gov-os-writer/`, `-home-usain-gov-os-checker/`, and the checker pass's new one) moved into `~/gov-os-eval/transcripts/` (mode 700); **the owner's operator, after the checker's pass** | `reviews/readiness-5-roles.md` |
| the checker's pass | **the owner's checker**, with §2 (corrected `a06dfa80`, `ada040dc`) | — |
| the declaration | drafted, uncommitted until the pre-flight fills its blanks | `packages/LIFT-1/FRESH-80-DECLARATION.md` |
| the cost | the judged run ~$15 (brake $30); every experiment for data ~$108 (brakes $216), after the judged run | `drafts/fresh80/README.md` |

**Then, in order:** the ACT applied and the CTO's live guard check; the pre-flight (counts only); the declaration filled and
committed; the hold; the visible-40 control; the measure on the 80; the judged reader run; the hold ends; the data
conditions; the figures to the owner.

## 8. The owner's run sheet (2026-11-08), paths only
- **The checker's and writer's tree at `c00d525f`:** `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/tree-c00d525f/`
  (`git archive`, no history; the paths both sessions' settings deny removed), readable by both (their settings'
  `additionalDirectories`), protected by the ACT's `fixtures/evaluation/memory-verdict-2/**` once applied; removed
  after the writer.
- **The checker's report:** `memory-verdict-2/STALENESS-CHECK.md` (beside `hidden/`, never inside it). **The writer's:**
  `memory-verdict-2/WRITER-REPORT.md`; old labels in `memory-verdict-2/retired/`.
- **Back to the CTO:** counts only; the digest computed by the operator after the writer
  (`cd .../memory-verdict-2/hidden && LC_ALL=C sha256sum *.yaml | sha256sum`), the files count and the folder mode.
- **Then:** the transcripts moved, the ACT applied; the CTO's live guard check, the worktree merges, the pre-flight
  (`--expect-sha256`, `--expect-changed`), the declaration committed; "ready to launch" to the owner; the run on the
  owner's word.
