# W2-32 S9 edit report (DEC-1129 (1), option (a1)); product-spec helper, class C1

## What was edited (main tree, not committed, not staged)
`.tickets/DAEO-0pyc.md`:
- The unlabelled escalation line (the old S9) replaced by the (a1) line from `packages/W2-32-S9-DISPOSITION.md` §3, word
  for word, labelled "S9", with a `Verify:` clause added, ending `[re-worded, DEC-1129 (1)]`. DEC-1126 (6) is cited inside the
  `Verify:` clause ("DEC-1126 (6) asked for the disposition"), so the line ends with the marker the brief names.
  The old escalation sentences are not repeated (the package says they stay as the audit's rule).
- Title (front matter) and the H1 heading below it: "the hit@5 85 row" -> "the memory line". Body line 101
  ("the hit@5 85 row on the dev queryset [W2-M341]", DEC-725 history) left as it was.
- `sources`: DEC-1097, DEC-1098, DEC-1129 appended (none was there). DEC-1126 is cited in the line text but was not added to
  `sources` (the brief names three ids).

`docs/changes/W2-32-evidence.md`: the S9 row rewritten (KPI cell, how-verified cell, result cell). It now gives the 80's
figures (78 of 79 right, 0 wrong claims, hit@5 67 of 79, window 4's pin, `c00d525f`), their records
(`packages/LIFT-1/FRESH-80-RESULT.md`, `FRESH-80-DECLARATION.md` `16d3d61b`, DEC-1098 (1), DEC-1129 (1), the disposition
package), and replaces "no improvement round has run yet" with the rounds that ran, each with its record: S7 (G1), S8
(G3, with the phrasings), S11 (pool v456; D4B-MORNING-2026-11-05 §1), DEC-1068 M1 to M5, S6 dropped (DEC-1083 (3)). It
says the 58.3 % (28 of 48) is the measure-1 baseline, not the 80. The older accept results are kept; a line says the
post-DEC-1129 accept result is to be added by the CTO.

## Checks
- Front matter parses (PyYAML): 11 success lines, title and sources as intended.
- `structural_pass.py`: all 8 families ok (portability and links skipped, no base given).
- `PYTHONPATH=src python3 -m gov.context.context_check`: answers only "unmeasured: stale store (built from 8f00bb90810b, not
  from HEAD 73c7594b9c92)". It cannot judge until the store is rebuilt from HEAD; so "no new error" is not shown, only that
  nothing the edit adds is a W2 id in `sources`.
- `git status`: only the two files modified.
- The acceptance case `test_the_evidence_file_states_s9s_and_f1s_outcome` (hit@5 figure on an S9 line) still finds one
  (the 28 of 48 baseline and percentages are on the row); the designer's revision should look for the end-to-end figure.

## Exact brief for the independent test designer (not the helper)

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

Note for the CTO: the designer's tests land after this ticket-file edit is committed (the case reads the evidence file).
