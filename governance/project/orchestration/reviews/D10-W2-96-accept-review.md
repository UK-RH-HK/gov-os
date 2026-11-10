# D-10's red-fix list: the review of gov accept's opt-in groups (S-D10a) and map reader (S-D10b) (W2-96, DAEO-ouet)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-96-accept-review.md`; tests `88c0772ff` (w2/W2-96-d10b-tests), code `04b52305a`, `3ac8e892f` (w2/W2-96-d10b); reviewer log `/home/usain/gov-os-worktrees/W2-96-d10b/.gov-runtime/scratch/lead/log/D10-W2-96-accept-review.json`.
- verdict.py: NOT READY (s-d10b-reader: F1 blocks: in scope, ordinary work, fails open). Round 2 to come.

Sandbox check: (a) refused, as it should be: the write outside the tree failed with `Read-only file system`. (b) worked: `git hash-object -w` returned `1ae28402a109…` and `git update-index --refresh` succeeded.
ps check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing, at the start and at the end.

**task:** DAEO-ouet (W2-96). D-10's review of S-D10a (opt-in groups) and S-D10b (the map reader), at HEAD `08c31e7ff` (`git rev-parse HEAD` matches).
**decisions:** DEC-1112 (3), DEC-959 item 6, DEC-1061 (2), DEC-970 (PKG-1 (a)), DEC-105, DEC-801, DEC-1010.

**status:** PACKAGES. The review is complete. S-D10b fails on one of the designer's cases (F1, blocking). PKG-D10a-scope is the CTO's decision; I recommend (b), confidence medium-high.

**work_completed:** I read:
- the ticket, the D-10 engineer brief and JUDGEMENT.md;
- both D-10 test files, the README map rows, the premise diff, the runner diff and the D-10 unit tests.

I ran:
- the designer's cases (both opt-ins, `-n 4`);
- `tests/unit/accept`;
- `gov accept W2-96` the declared way.

I compared the old reader (`bbe222c59`) with the new one over all 116 acceptance READMEs, worked out which opt-in groups each readable map now enables, counted W1-46's cases per group, and checked the trailers. This took well over the 15-minute estimate: the unit run had to be repeated, and the scope question needed the map sweep.

**files_changed:** none. `git status --porcelain` is empty.

**evidence:** Every run went through `heavy_slot.sh` with `PYTHONPATH=<tree>/src`, a TMPDIR of my own, and `-p no:cacheprovider -o tmp_path_retention_policy=failed`.
- My scratch folder `/tmp/gov-launch-b1ouagix/claude-1000/rev-d10b` peaked at 2.3M and 571 inodes. It is cleaned except `home2/.local`, a link to `/home/usain/.local`: the guard refused its `rm`, and I took the refusal.
- The guard also refused the Write tool for a probe script in my TMPDIR. I took that refusal too and ran the same read-only probes as inline `python3 -I -c` commands, which write no file.

**tests:**
- **Designer's cases** (`d10a`, `d10b` and the premises file; `--optin=lifted --optin=breadth -n 4`): 48 collected, **47 passed, 1 failed**. The failure is `test_s_d10b_a_cell_of_the_maps_in_use_reads_every_line_or_refuses_naming_the_cell[words-between-the-names]`. So 24 of the 25 cases that were red at integrate are now green. All five guards and all 20 premises pass.
- **`tests/unit/accept`** (both opt-ins, `-n 4`): **162 passed**. The `-k "not real…"` exclusion left out exactly one case, a pure string-parse case whose id holds "real" (`test_w2_96_d10b_every_listed_line_is_read[…in a real session: after-names9]`). I ran it alone and it passed, so 163/163. `-m local_only` left out nothing.
- **`gov accept W2-96`**: **exit 3, outcome fail**, `optin: ["breadth"]`, totals 146 passed and 1 failed.

  | Line | Passed / failed | Outcome |
  |---|---|---|
  | S1 | 14/0 | pass |
  | S2 | 22/0 | pass |
  | S3 | 23/0 | pass |
  | S4 | 11/0 | pass |
  | S5 | 36/0 | pass |
  | S7 | 13/0 | pass |
  | **S8** | **14/1** | **fail** |
  | F1 | 18/0 | pass |
  | F2 | 23/0 | pass |
  | F3 | 11/0 | pass |
  | F4 | 31/0 | pass |
  | unmapped | 33/0 | — |

  The engineer's "109/0 pass" was measured before the designer's 38 cases were merged (109 = 74 in the full run plus 35 in breadth).

**discoveries:**
- With an empty HOME (the D-4b rule for test runs), `gov accept` answers `crash` for every ticket. The runner drops all `PYTHON*` variables from the child's environment, including `PYTHONUSERBASE`, and the child then cannot import pytest. My first unit run showed it: 35 crashes, 40 passes. See F4.
- `tests/optin-lifted-breadth.txt` holds `rep: tests/unit/accept/`, so a unit run without breadth gets only 75 of the 163 cases.
- xdist does not print deselection counts.

**risks:** As built, eight readable maps make a formal accept run switched-off-feature (`lifted`) cases and count their reds (F2, PKG-D10a-scope).

**lessons:** Measure `gov accept` only after the designer's cases are merged in. When HOME is a scratch folder, give it a `.local` link (as the W2-96 suite does), not `PYTHONUSERBASE`.

**proposed_decisions:** PKG-D10a-scope (b), below.

**unresolved:**
- I did not measure how W1-46's 107 reds split between the groups. A breadth-only run of its 370 cases would settle it.
- W2-150's `S6 (S1)` cells may be prose or a listing; I'm not judging them.
- The leftover link (see evidence).

**recommended_next_action:** F1's fix goes into the ticket's resume (DEC-802), with the designer's existing red case as its test. The CTO then decides PKG-D10a-scope. This is review round 1 of at most 2.

## The checks

**1. Runs.** Counts are in `tests` above.

**2. No fail-open.**

S-D10a: no fail-open found.
- A line with zero run cases still fails (the three ZERO variants and a unit case).
- Another ticket's cases never run: its same-named failing twin and its failing file, both in breadth, did not run.
- The report names exactly the groups it enabled: the designer checks the exact sets breadth, lifted, both, and none. The caller's own `GOV_TESTS_OPTIN` never reaches the child.
- No test content leaks: the marker probe passed in every D-10 case, and the `optin` key only ever holds the two fixed group names.
- It is not a looser rule: enabling a group only adds cases.

S-D10b: refusals work, but one form is still dropped silently.
- An unreadable cell is refused before any test runs, and the refusal names the cell: two row variants, the text form, and a heading refusal in the unit tests. Test and file names inside the cell are masked, and it is capped at 120 characters.
- No existing readable form changed meaning. The 45 maps refused before are refused now, and no map is newly refused. Only three maps read differently, and each now reads more of the lines it lists:
  - W1-05 `Success 3–7.` now gives success 3 to 7;
  - W2-71 `K4 (…), K1 (…)` now adds success-1;
  - W2-87 row 36 now adds failure-4.

  The designer's seven guard forms read as before.
- The reader still drops a listed line silently when words come between the names (F1).

**3. Scope question (PKG-D10a-scope).** My view: **(b)**, confidence medium-high.
- **(a), as built:** it contradicts DEC-1061 (2). That decision says lifted is "not counted… report-only… its reds filed against each lifted feature's home ticket", and the list's own header says the same. Under PKG-1 (a), any red case, mapped or not, fails the run. Eight readable maps enable lifted today: W1-05 and W1-46 (with breadth), and W1-30, W1-33, W2-107, W2-53, W2-71 and W2-72. W1-46's accept now runs 123 lifted cases out of 493; the engineer measured 386 passed and 107 failed.
- **(c), mapped node ids only:** it is worse on both counts.
  - Mapped lifted cases still run and still count, and W1-46's map names whole files, so the contradiction stays.
  - Unmapped breadth reds stop counting, such as W1-27's 19. Those are acceptance cases of live features, cut from the full run only for time. Hiding them loosens PKG-1 (a).
- **(b):**
  - Breadth runs across the ticket's whole folder, as built. That restores the acceptance set from before the cut, so the KPIs stay measured and PKG-1 (a) holds.
  - Lifted is never enabled in a formal accept. A line resting only on lifted cases stays a fail, as S-D10a's "runs zero stays a fail" requires, and the report names `lifted` as report-only.
  - This needs the CTO's amendment of its own delegated line (DEC-1112 (3)). It also means a designer rewrite of the variants `a-case-in-lifted-passes` and `lines-in-both-groups-through-every-list-name`.
- **What would reverse this view:** a reading of DEC-1061's "report-only" as binding only the full run.

**4. Trailers.**
- `04b52305a` and `3ac8e892f` (engineer) carry `Task: DAEO-ouet`, `Implements: DEC-1112, DEC-959`, `Role: engineer` and `Co-Authored-By`.
- `88c0772ff` (designer) carries the same with `Role: independent-test-designer`, plus `Rewrite-Reason` for the premise change.
- Each commit follows the D-10 brief and stays within its allowed paths.
- The scratch merge `08c31e7ff` has no trailers and must not land.

## Findings

Classification: F1 is in scope, reachable in ordinary work, and fails open, so it blocks. F2 and F3 are in scope with consequence "other", so they are recorded rows. F4 and F5 are out of scope with consequence "other", so they are rows for the ticket that owns each.

**F1 (s-d10b-reader).** Done: a map row whose KPI cell names a second line after some words, such as "Success 5 [CAP-37.g], first half, and failure 1" (W1-49 row 88's form). Happened: the run reported success-5 only. Failure-1 was neither reported nor refused, and the run passed with exit 0. Should have: report failure-1 with the row's case, or refuse the map naming the cell.

The same happens with:
- "…second half, and failure 2" (W1-49 row 89);
- "Success 6 with success 4." (W2-92 row 128, a map read today);
- `S2-S4`, `Success 2–Success 4`, `Success 1 or failure 2`, `Success 1 to 3`, `Success 1 (and failure 2)` and `Success 1 — and failure 2`.

Ordinary work: yes, because these forms sit in maps in use. W2-92's map is read today. W1-49's drop becomes live once its "Edge:" and "DEC-259:" rows stop the map from being refused.

Consequence: fails open. In W2-92, success-4 is also mapped on other rows. If row 128's guard case fails while those other cases pass, success-4 is reported "pass": the run as a whole fails, but the per-line verdict that a lines-met count reads is false. A line mapped nowhere else simply vanishes from the report. The KPI's own words name this silent drop as the failure.

Reversed by: a CTO ruling that a line named after intervening words is prose (the finding would then be out of scope). For the consequence alone: evidence that no consumer reads per-line verdicts from a failing run would make it "other".

**F2 (s-d10a-optin).** Done: a map names a case that a lifted list leaves out. Happened: lifted ran across the whole folder, so every switched-off-feature case there ran, mapped or not, and its reds count against the line and the run. Should have: lifted stays report-only (DEC-1061 (2)).

Ordinary work: yes, because eight readable maps trigger it today.

Consequence: other. It fails closed: no work is lost and nothing passes that should fail. It contradicts an owner decision, which is the CTO's call under DEC-105.

Reversed by: a reading that "report-only" covers only the full run.

**F3 (s-d10a-optin).** Done: a run with groups enabled ended in the runner's own crash (no report). Happened: the `error/crash` result does not name the groups it enabled. Should have: name them on every result once they are set.

Ordinary work: yes, because I hit it with an empty HOME.

Consequence: other (an error is never a pass).

Reversed by: reading S-D10a as requiring the groups only on measured results.

**F4 (out of scope).** Done: `gov accept` with an empty HOME and `PYTHONUSERBASE` set, as the D-4b rules ask for test runs. Happened: every run answered `crash`, because the child gets no `PYTHONUSERBASE` and cannot import pytest. Should have: the child should still find pytest.

Ordinary work: yes (the launched workers' common rules). Consequence: other (fails closed). It predates this revision.

Reversed by: evidence that workers never run `gov accept` with an empty HOME.

**F5 (out of scope).** Done: W1-27's S8 maps four bare `test_…[row]` items. Happened: they never match a case, so S8 fails with no failed case whatever groups run. That leaves one of the brief's own motivating lines unmeasured. Should have: the map should use `file::name[row]`, or the matcher should accept the bare form.

Ordinary work: yes. Consequence: other (fails closed). The item form is older than this revision.

Reversed by: reading S-D10a as covering item forms (it would still be "other").

**Probed and found sound:**
- No lost work.
- No role wrote outside its scope.
- The implementer could not change the acceptance tests.
- The premise revision only tightens its check.
- Ranges wider than 50 or reversed are refused.
- A row with no items is never refused.
- A caller's `GOV_TESTS_OPTIN` is dropped.
- An unreadable opt-in list fails closed.

```verdict
{"kpis": [{"kpi": "s-d10a-optin", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "s-d10b-reader", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
