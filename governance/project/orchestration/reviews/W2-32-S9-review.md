# W2-32 S9's cases: independent review, round 1 (DEC-1129 (1), DEC-1131)

Reviewer: independent-auditor, claude -p (Opus, high, C2), launched by the CTO in W2-32-s9-tests at 669707a76; not the author. The record is the session's final message, unchanged.

**Step 0, sandbox check (launch_worker.sh):** passed. Running as `GOV_TICKET=DAEO-0pyc`.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-32` failed with `OSError: [Errno 30] Read-only file system`, and no file exists.
- (b) `git hash-object -w --stdin` worked (`1ae28402a`) and so did `git update-index --refresh` (exit 0 for both).

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing (exit 1).

**Identity:** `git rev-parse HEAD` is `669707a760b7869bc5e8934b76eac7a40f55cf8c`, on `w2/W2-32-s9-tests`. `git status --porcelain` is empty at the end, so nothing was written in the tree.

---

- **task:** DAEO-0pyc (W2-32). Independent review, round 1, of S9's re-pointed cases and of F1 being unchanged (DEC-1129 (1), DEC-1131).
- **status:** done. Verdict READY.
- **work_completed:** I made the five checks in the brief.
  1. The commit `669707a76` changes only the three files the brief names. It carries `Rewrite-Reason: DEC-1129 (1)` and `Task: DAEO-0pyc`.
  2. The S9 cases test the line's own words, and every wrong `s9_state` I planted turns them red.
  3. The evidence-row case reads `docs/changes/W2-32-evidence.md` and holds the 80's judged figures and FRESH-80-RESULT.
  4. F1's code and cases are unchanged.
  5. The README's KPI map parses with `gov.accept.runner.parse_map`, and every item names a test that collects.
- **files_changed:** none in the repository. My only scratch was a copy under `$TMPDIR/rev`.
- **evidence:**
  - **Changed files:** `git diff --stat 1a3669e6a 669707a76` lists only `tests/acceptance/W2-32/README.md`, `test_w2_32_record.py` and `w2_32_record.py`.
  - **F1 in the diff:** `test_f1_reverts_a_round_below_the_baselines_noise_band` and its 5 cases, `noise_band`, `f1_verdict`, the F1 verdict line in `main()`, and the README's F1 row are all untouched.
  - **The 79-question boundaries are right:**
    - 67/79 = 84.8 %, below the bar; 68/79 = 86.1 %, at or above it.
    - 3/79 = 3.8 % wrong claims is allowed; 4/79 = 5.06 % is over 5 %.
    - 75/79 = 94.9 %, under target; 76/79 = 96.2 %, at target.
    - The percentage cases test 85.0 and 95.0 as included, 84.9 and 94.9 as below, 5.0 wrong as allowed and 5.1 as refused.
  - **Planted wrong `s9_state` / `s9_report`:** the unchanged copy gave 21 passed, 2 skipped. Each planted variant failed at least one case:

    | Planted mistake | Failed cases |
    |---|---|
    | `<=` at the 85 % bar | 1 |
    | `>=` at the 5 % wrong-claim limit | 1 |
    | wrong claims ignored | 2 |
    | `<=` at the 95 % target | 1 |
    | no "under target" state | 11 |
    | hit@5 judged as well | 6 |
    | hit@5 judged instead of end to end | 6 |
    | bar set to 80 | 2 |
    | wrong-claim limit set to 10 | 2 |
    | percentages taken over 48 instead of 79 | 6 |

  - **Evidence-row case, run against changed copies of the evidence file:**
    - The 91535d990 row (before the re-wording) fails.
    - Without FRESH-80-RESULT it fails.
    - With 70 of 79 / 88.6 % it fails.
    - With 2 wrong claims it fails.
    - With no hit@5 it fails.
    - With **hit@5 28 of 79 it passes** (finding F-1).
    - The original file passes.
  - **KPI map:** `parse_map` gives keys success-1..5, 7..11 and failure-1. success-9 has 5 items and failure-1 has 3; `names_a_test` is True for each, and all 7 test functions collect.
- **tests:** I ran `test_w2_32_record.py` only, in the `$TMPDIR` copy, with `HOME` set to an empty folder and `W2_32_RUNS` pointed at an empty path. The 2 skipped cases are the baseline-record cases (`test_the_baseline_record_holds_both_figures_against_their_bars`, `test_the_baseline_was_run_more_than_once_on_one_commit_so_it_has_a_noise_band`), because I may not open `~/gov-os-runs/`. I ran no whole folder, so the real-model exclusion left nothing out.
- **discoveries:** The S9 cases test the rule as `w2_32_record.py` states it, which lives in the test folder itself. That is the nature of a measured line. What actually ties S9 to the result is the evidence-row case.
- **risks:** The hit@5 figure in the evidence row is not pinned (F-1).
- **lessons:** none new.
- **proposed_decisions:** none.
- **unresolved:** I did not run the baseline-record cases on the real records (forbidden path). They rest on the CTO's run: 266 passed, 0 failed, 2 skipped.
- **recommended_next_action:** Treat S9's cases as ready. Record F-1 to F-4 as rows; the hit@5 pin in F-1 is a one-line change the designer can make when the ticket next resumes. No round is needed (DEC-802).

decisions: [DEC-1129, DEC-1131, DEC-1097, DEC-1098, DEC-1010, DEC-801, DEC-808, DEC-802, DEC-1014]

## Findings

**Classification:** 0 blocking. 3 recorded rows on S9 (in scope, not blocking) and 1 out of scope.

**F-1. S9, blocking: no.** The evidence-row case accepts any hit@5 figure. It requires `hit@5 <n> of 79` or `hit@5 <x> %`, not 67 of 79 / 84.8 %. I replaced the row's figure with "hit@5 28 of 79" and the case passed. The 48-set baseline written as "hit@5 58.3 %" (the mix-up that 1a3669e6a corrected) would also pass the regex. The ticket's Verify line says the row records "hit@5 67 of 79".
- Ordinary work: yes, because an honest engineer can copy the baseline's or another set's hit@5 into the row.
- Consequence: other. hit@5 is reported and never judged; S9's verdict rests on 78 of 79 and 0 wrong claims, and both are pinned.
- Fix: require `hit@5 67 of 79|84\.8 ?%`.
- What would reverse it: an owner ruling that the reported figure only has to be present, not that particular value.

**F-2. S9, blocking: no.** The evidence case checks its four conditions (end-to-end figure, wrong claims, hit@5, FRESH-80-RESULT) separately, each across every line that mentions S9. They do not have to be on S9's own row, so the figures could come from different lines, such as the `gov accept` summary lines that name S9.
- Ordinary work: no, because the S9 row would have to lose its figures while another line naming S9 carried each one.
- Consequence: other.
- Fix: select the table row that begins `| **S9**` and check all four on that row.
- What would reverse it: a planted split where the case still fails.

**F-3. S9, blocking: no.** `test_the_baseline_record_holds_both_figures_against_their_bars` stays mapped under S9. It checks the 48-set baseline record's form, including the hit@5 field `floor: 85`, which the re-worded S9 line does not name. The README notes "reported, not S9's judgement".
- Ordinary work: yes, because a change in the baseline record's form would turn S9 red.
- Consequence: other. It fails closed and skips when there are no records.
- Fix: map the case under F1 only, since it is the base of F1's band.
- What would reverse it: a decision that S9's line includes the baseline's form.

**F-4. Out of scope (a row, never a round).** In the reviewer's tool `w2_32_record.main()`, hit@5 is divided by `QUESTIONS = 48` for every round record, so a 79-question record would print a wrong hit@5 percentage. Separately, `s9_state` gives `wrong_percent` a default of 0.0, so a direct call that leaves out the wrong claims is judged "met".
- Neither is used by the acceptance cases, and neither affects S9's verdict, which is judged on the evidence row.
- Ordinary work: no.
- Consequence: other.
- Fix: take the denominator from `total.hit_at_5.of`, and make `wrong_percent` a required argument.
- What would reverse it: S9's verdict being computed by `main()` on a round record.

**Probed and found sound:**
- The bar and target boundaries, as percentages and as counts of 79.
- The wrong-claim limit (5 % allowed, 5.1 % refused).
- hit@5 is never an input to the state: values 0, 67 and 79 all give "met" at 78 of 79.
- The old rules ("next round", "owner decides") are gone.
- F1's rule and cases are byte-identical.
- The README's node ids parse and collect.
- The commit touches only the three named files and carries its trailers.

```verdict
{"kpis": [{"kpi": "S9", "verdict": "pass", "findings": [{"id": "F-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F-3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```

**Verdict: READY**
