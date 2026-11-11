# W2-32 S9's cases revised (DEC-1129 (1)): independent test designer, round 1

Hand-built brief (DEC-1130 (1): W2-32 is reviewed and in progress, so it launches on a hand-built brief until it
closes). `gov brief lead DAEO-0pyc --run tests` at 1a3669e6a refused: BRIEF_NOT_READY: KPI_NO_VERIFY S1-S8, S10, S11,
F1, F2; DEPENDS_NOT_CLOSED DAEO-rd0g (W2-15a). The S9 line now carries its Verify clause.

Your worktree is on branch `w2/W2-32-s9-tests` at w2/integrate's head `1a3669e6a`. Commit your three files there, one
commit, trailers `Task: DAEO-0pyc`, `Role: independent-test-designer`, `Implements: DEC-1129`, and
`Rewrite-Reason: DEC-1129 (1)`. Never push, never merge; the CTO lands it. RUBRIC-2: class C2, Sonnet at high.
Judged on the S9 line (and F1 unchanged) only, at most two rounds (DEC-1010).

Task: revise W2-32's S9 acceptance cases to the new S9 (DEC-1129 (1); `Rewrite-Reason: DEC-1129 (1)` on each rewritten case).
Role: independent-test-designer under ticket W2-32 (DAEO-0pyc), the ticket's own acceptance folder
`tests/acceptance/W2-32/`. Read the KPI text, not any engineer code:

> S9 K9's memory line (DEC-1083 (2), re-worded by DEC-1097 (1)(d)): on the verdict set, judged once on the declared
> configuration, right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5 reported beside it.
> Judged on the fresh 80 at window 4's pin: 78 of 79 right (98.7 %), 0 wrong claims, hit@5 67 of 79 (84.8 %)
> [FRESH-80-RESULT, DEC-1098 (1)]. A later fall below 85 % is brought to the owner by the memory audit (DEC-1101 (1),
> DEC-1125 (2)), whose first run on 11-23 measures today's pin. Verify: the S9 cases of tests/acceptance/W2-32/, re-pointed
> to the end-to-end figure ... and the evidence note's S9 row ... [re-worded, DEC-1129 (1)]

Files you change (only these, all inside the ticket's acceptance folder):
1. `tests/acceptance/W2-32/README.md`: the S9 row of the KPI map (about line 138) and the "S9 and F1" paragraph (about
   lines 150-160): S9 is about the end-to-end figure now; F1 keeps its noise-band rule unchanged. Keep the S9 row's
   mapping to test ids in the form `gov accept` reads.
2. `tests/acceptance/W2-32/w2_32_record.py`: `s9_state` and its constants (`FLOOR, TARGET = 85, 95` stay as the end-to-end
   bar and target). `s9_state` takes the end-to-end percentage (and wrong-claim percentage, bar 5 %), not hit@5:
   below 85 % or wrong claims above 5 %: "owner told" (the audit brings it; the old "next round" and "owner decides" after
   two rounds no longer apply); 85 % or above and wrong claims at most 5 %, under 95 %: "met, under target"; 95 % or
   above: "met". hit@5 is carried beside, reported, never judged. `main`'s printed line follows. Keep the F1 code
   (`noise_band`, `f1_verdict`, `baseline_records`, `form_problems`) as it is.
3. `tests/acceptance/W2-32/test_w2_32_record.py`: the six S9 parametrised cases (about lines 63-67) re-pointed to the
   end-to-end figure, with boundaries at 85 % and 5 % wrong, 95 %, and one on 79 questions (68 right, 3 wrong claims is
   the bar; 76 the target; 78 of 79 and 0 wrong: met, at target). The evidence-file case (about lines 70-77): the S9 line
   of `docs/changes/W2-32-evidence.md` carries the end-to-end figure (78 of 79, or its percentage), the wrong-claims figure
   (0), hit@5 beside it, and names `FRESH-80-RESULT`; F1's half of that case is unchanged. Do not read
   `~/gov-os-runs/` or any hidden folder; the S9 cases need no record outside the evidence file and the stated figures.
KPI: the S9 line above (and F1, unchanged). Do not touch other cases of the folder.

Check: `PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-32/test_w2_32_record.py -q -p no:cacheprovider
-o tmp_path_retention_policy=failed` first, then `gov accept W2-32` scoped to S9 and F1 (through
`.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`; about 4 minutes). The new S9 evidence-row case passes against the
row as now edited in `docs/changes/W2-32-evidence.md`; red on the old row (no end-to-end figure). Return the twelve fields,
the list of rewritten cases each with its `Rewrite-Reason`, and the `gov accept` summary.

