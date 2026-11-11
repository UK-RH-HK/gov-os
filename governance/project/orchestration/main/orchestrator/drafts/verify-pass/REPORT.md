# The `Verify:` pass (DEC-1130 (1)): in/out table

Written by the product-spec helper, 2026-11-11, resumed after the WSL restart. Step 1 was run with
`gov brief lead <ticket> --run tests` on every non-closed ticket (99; scan in `tmp/before.txt`, evidence in `tmp/evid.txt`).
98 refuse on `KPI_NO_VERIFY` (the 99th, DAEO-8s85 / W2-153, does not). Failure lines count: each F line needs a `Verify:` too
(W2-156's F1 to F4 refuse today).

Rule used. OUT: a review or probe record concerns it; an acceptance folder with TESTS-READY; a review-round commit;
in_progress (every one has a launched branch with work, checkpoints or merges, or is about to close); merged work.
IN: open, none of these. A name that only appears in a forwarded rule list or a dependency note is not a review of the
ticket (W2-28, W2-30, W2-47 in w2-32-m245.md; W2-154 in w2-153-s3-amended.md; W2-115 in D10-serial-only-1a-review.md).

| W2 id | Ticket | Status | In/out | Why | Lines refused (S+F) |
|---|---|---|---|---|---|
| W1-01b | DAEO-vhad | status in_progress | out | filed and claimed, no branch; D9 fates and DEC-1126 (7): closes at the D-10 green run (unsure: out) | 3 |
| W2-00 | DAEO-sdxk | open | out | the CTO's own standing ticket (W2-00) | 1 |
| W2-04 | DAEO-u4oz | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 8 |
| W2-05 | DAEO-0z8c | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 4 |
| W2-11 | DAEO-k7hz | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 19 |
| W2-13 | DAEO-zqvn | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 8 |
| W2-15a | DAEO-rd0g | open | out | merged work (w2/W2-15a merged: EXP-003 pass 1 record, link census) and kept open at the lift (DEC-1126 (6)) | 4 |
| W2-15b | DAEO-swdu | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 12 |
| W2-17 | DAEO-sdhj | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 5 |
| W2-18 | DAEO-057v | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 6 |
| W2-19 | DAEO-jzvg | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 6 |
| W2-20 | DAEO-r30l | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 24 |
| W2-23 | DAEO-kmcr | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 8 |
| W2-27 | DAEO-h4rh | open | out | reviewed: w2-27-citp.md reviews its CIT-P note; commit e64fbe211 records the independent review | 17 |
| W2-28 | DAEO-csj8 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 2 |
| W2-29 | DAEO-b926 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 1 |
| W2-30 | DAEO-60rw | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 1 |
| W2-32 | DAEO-0pyc | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 12 |
| W2-33 | DAEO-lrre | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 7 |
| W2-34 | DAEO-yadm | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 5 |
| W2-35 | DAEO-2keg | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 1 |
| W2-36 | DAEO-w19l | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 1 |
| W2-37 | DAEO-6n5k | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 2 |
| W2-40 | DAEO-6ox0 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 1 |
| W2-42 | DAEO-fau3 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 8 |
| W2-42a | DAEO-03ub | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 13 |
| W2-45 | DAEO-neam | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 5 |
| W2-46 | DAEO-nn1s | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 7 |
| W2-47 | DAEO-jip3 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 3 |
| W2-52 | DAEO-siiz | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 4 |
| W2-55 | DAEO-arrl | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 12 |
| W2-56 | DAEO-wnnz | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 21 |
| W2-60a | DAEO-cv58 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 11 |
| W2-60b | DAEO-ecac | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 13 |
| W2-61h | DAEO-h2k3 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 12 |
| W2-66b | DAEO-zuiy | status in_progress | out | named and read by the review of W2-66c (D10-W2-66-review.md: "W2-66b could be closed as satisfied"); in_progress, no branch (unsure: out) | 2 |
| W2-66c | DAEO-btcs | open | out | reviewed: D10-W2-66-review.md reviews W2-66c; its D-10 tests branch merged | 3 |
| W2-81 | DAEO-l78m | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 17 |
| W2-82 | DAEO-4k3l | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 5 |
| W2-88 | DAEO-2bdu | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 22 |
| W2-90b | DAEO-nqa2 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 7 |
| W2-90c | DAEO-fu3n | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 6 |
| W2-91 | DAEO-a3u2 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 10 |
| W2-92 | DAEO-n0wb | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 16 |
| W2-93 | DAEO-6y0x | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 7 |
| W2-94 | DAEO-g87r | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 8 |
| W2-96 | DAEO-ouet | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 12 |
| W2-98 | DAEO-wi46 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 11 |
| W2-100 | DAEO-uw5h | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 12 |
| W2-101 | DAEO-6icv | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 11 |
| W2-104 | DAEO-drhj | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 7 |
| W2-105 | DAEO-zpdj | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 8 |
| W2-110 | DAEO-3r1j | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 8 |
| W2-111 | DAEO-qvff | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 7 |
| W2-112 | DAEO-clon | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 10 |
| W2-113 | DAEO-g29a | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 6 |
| W2-115 | DAEO-emq1 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 23 |
| W2-116 | DAEO-f58b | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 8 |
| W2-120 | DAEO-i89t | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 1 |
| W2-121 | DAEO-cb2b | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 22 |
| W2-122 | DAEO-blwa | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 5 |
| W2-123 | DAEO-qzrq | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 9 |
| W2-124 | DAEO-mb2t | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 7 |
| W2-126 | DAEO-jpr0 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 10 |
| W2-128 | DAEO-t8mp | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 11 |
| W2-129 | DAEO-q7lk | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 24 |
| W2-130 | DAEO-q8cl | open | out | reviewed: w2-130-marks.md is an independent audit of its batches; work merged (rulings, link clean-up) | 12 |
| W2-131 | DAEO-r8vq | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 2 |
| W2-133 | DAEO-k4wm | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 2 |
| W2-134 | DAEO-m4rq | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 4 |
| W2-135 | DAEO-c4pb | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 2 |
| W2-136 | DAEO-p3ln | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 5 |
| W2-137 | DAEO-5emz | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 4 |
| W2-138 | DAEO-rmhj | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 3 |
| W2-139 | DAEO-ongl | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 2 |
| W2-140 | DAEO-5ce2 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 1 |
| W2-141 | DAEO-xwro | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 4 |
| W2-142 | DAEO-qskx | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 1 |
| W2-145 | DAEO-2tfd | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 5 |
| W2-146 | DAEO-f6x3 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 3 |
| W2-147 | DAEO-zi7s | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 3 |
| W2-148 | DAEO-xafn | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 15 |
| W2-149 | DAEO-52ku | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 11 |
| W2-150 | DAEO-ijf5 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 4 |
| W2-151 | DAEO-qzca | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 4 |
| W2-152 | DAEO-o5x1 | status in_progress | out | in_progress with a launched worktree/branch and work, checkpoints, rounds or merges (unsure: out) | 3 |
| W2-154 | DAEO-l4gf | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 7 |
| W2-155 | DAEO-ar89 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 6 |
| W2-156 | DAEO-ylsh | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 4 |
| W2-157 | DAEO-ozyt | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 4 |
| W2-158 | DAEO-8a3f | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 4 |
| W2-159 | DAEO-6lid | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 4 |
| W2-160 | DAEO-fd0p | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 4 |
| W2-170 | DAEO-61vm | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 5 |
| W2-171 | DAEO-k1e2 | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 5 |
| W2-172 | DAEO-p8tv | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 5 |
| W2-173 | DAEO-qz4p | open | IN | no review/probe record, no acceptance folder, no TESTS-READY, no review-round commit, no merged work | 4 |
| - | DAEO-feon | open | out | repair ticket made by the refused close of W2-122 (reviewed); not a planned ticket | 8 |

## Result

44 tickets edited, 295 KPI lines (success and failure) given a `Verify:` clause; 0 lines left. `git diff --stat`: 44 files, 302 insertions, 302 deletions, all under `.tickets/`.
Checks: every front matter parses, KPI counts unchanged, no other field or body text changed (`tmp/cmp.py`); words of each line kept in order, the only moves are decision/provenance brackets placed after the clause (W2-15b S2, S4, S6 carry `[moved from ...]`, which now follows the clause); structural pass: all 8 families ok. `gov brief lead <id> --run tests` no longer prints `KPI_NO_VERIFY` for any of the 44.
Plain YAML lines had to be single-quoted so `Verify:` parses (W2-15b to W2-40, W2-42, W2-45). A few lines gained a full stop before the clause (W2-15b S2, S4, S6; W2-35 S1, W2-36 S1 take the clause at the end because their brackets sit mid-line). W2-93 and W2-94 checks use planted stand-ins only.
**None of the 44 is briefable yet.** Every one still refuses on `NON_GOALS_MISSING` and `SIZE` (4000 prose characters); also DEPENDS_NOT_CLOSED, EST_LOC_OVER (W2-88, W2-121, W2-170 to W2-172), READS_MISSING (W2-170 to W2-173). These are outside this pass: owner or CTO call.
The `lifted:` and `moved:` lists in W2-47, W2-82 and W2-88 are not read by `gov brief` and were left alone.

### gov brief refusals after (codes), per ticket

| W2 id | Ticket | Codes after |
|---|---|---|
| W2-18 | DAEO-057v | NON_GOALS_MISSING,SIZE |
| W2-88 | DAEO-2bdu | DEPENDS_NOT_CLOSED,EST_LOC_OVER,NON_GOALS_MISSING,SIZE |
| W2-35 | DAEO-2keg | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-82 | DAEO-4k3l | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-30 | DAEO-60rw | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-170 | DAEO-61vm | EST_LOC_OVER,NON_GOALS_MISSING,READS_MISSING,SIZE |
| W2-101 | DAEO-6icv | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-159 | DAEO-6lid | NON_GOALS_MISSING,SIZE |
| W2-40 | DAEO-6ox0 | NON_GOALS_MISSING,SIZE |
| W2-93 | DAEO-6y0x | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-158 | DAEO-8a3f | NON_GOALS_MISSING,SIZE |
| W2-155 | DAEO-ar89 | NON_GOALS_MISSING,SIZE |
| W2-29 | DAEO-b926 | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-121 | DAEO-cb2b | DEPENDS_NOT_CLOSED,EST_LOC_OVER,NON_GOALS_MISSING,SIZE |
| W2-28 | DAEO-csj8 | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-60b | DAEO-ecac | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-115 | DAEO-emq1 | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-146 | DAEO-f6x3 | NON_GOALS_MISSING,SIZE |
| W2-42 | DAEO-fau3 | NON_GOALS_MISSING,SIZE |
| W2-160 | DAEO-fd0p | NON_GOALS_MISSING,SIZE |
| W2-90c | DAEO-fu3n | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-113 | DAEO-g29a | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-94 | DAEO-g87r | NON_GOALS_MISSING,SIZE |
| W2-120 | DAEO-i89t | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-47 | DAEO-jip3 | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-19 | DAEO-jzvg | NON_GOALS_MISSING,SIZE |
| W2-171 | DAEO-k1e2 | DEPENDS_NOT_CLOSED,EST_LOC_OVER,NON_GOALS_MISSING,READS_MISSING,SIZE |
| W2-23 | DAEO-kmcr | NON_GOALS_MISSING,SIZE |
| W2-154 | DAEO-l4gf | NON_GOALS_MISSING,SIZE |
| W2-33 | DAEO-lrre | NON_GOALS_MISSING,SIZE |
| W2-124 | DAEO-mb2t | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-45 | DAEO-neam | NON_GOALS_MISSING,SIZE |
| W2-46 | DAEO-nn1s | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-157 | DAEO-ozyt | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-172 | DAEO-p8tv | DEPENDS_NOT_CLOSED,EST_LOC_OVER,NON_GOALS_MISSING,READS_MISSING,SIZE |
| W2-111 | DAEO-qvff | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-173 | DAEO-qz4p | NON_GOALS_MISSING,READS_MISSING,SIZE |
| W2-17 | DAEO-sdhj | NON_GOALS_MISSING,SIZE |
| W2-15b | DAEO-swdu | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-100 | DAEO-uw5h | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-36 | DAEO-w19l | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-98 | DAEO-wi46 | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |
| W2-34 | DAEO-yadm | NON_GOALS_MISSING,SIZE |
| W2-156 | DAEO-ylsh | DEPENDS_NOT_CLOSED,NON_GOALS_MISSING,SIZE |

Before: `tmp/before.txt` (each ticket with its refused S/F labels). Sidecars per fork: `G1.md` to `G5.md`. Each Verify text is the helper's reading of the line's own words; the CTO should read the diffs before committing.
