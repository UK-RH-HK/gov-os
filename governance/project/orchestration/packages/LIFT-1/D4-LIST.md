# D4-LIST: the test suite cut, for the owner first (DEC-1052; P1, short form)

By the CTO (session 33b3628c), 2026-11-03 ~18:00, combining two test designers' parts: `D4-LIST-A.md` (the guard, its
hooks, the launcher's role checks, the role files) and `D4-LIST-B.md` (every other suite, D-3's moved items, today's
reds). **Nothing is deleted, merged or moved until the owner decides.** One independent reviewer checks the list
(the KPI coverage map, the counts) in parallel; its verdict comes with the owner's answer or before the cut.
Basis: question 3 (tests run where the risk is: the change, or the full suite) and question 4 (a full run in hours,
not a day), with question 2 kept (every kept KPI line covered by at least one case in the full run).

## The count (collect-only at `c39cffc1b191`: 19,955 cases; the two parts add up exactly)

| | cases | case-seconds |
|---|---:|---:|
| today | 19,955 | about 32,975 |
| **tier 2 (recommended): full run** | **4,688** (A 1,050, B 3,638) | **about 9,800 (est.)** |
| tier 1: full run | 5,995 (A 1,404, B 4,591) | about 12,560 (est.) |
| moved to the opt-in suite `lifted` (built but off; not in the full run) | 8,945 (A 6,684, B 2,261) | about 14,450 |
| folded into representative cases (no test function removed) | about 5,026 | — |
| deleted (D1, D2, already approved by DEC-1040) | 29 | — |

- **Tier 1** folds parameters to representatives and moves the lifted features' suites to `lifted`. **Tier 2** adds a
  cap of 6 cases per KPI line (the named case for each line kept first). Only tier 2 reaches about 5,000.
- **The full suite's expected time** (est., from today's ratio of wall time to case time, 5.4 h for about 33,000
  case-s): today about 5.4 h; tier 2 **about 1.5 to 2 h**; tier 1 about 2 to 2.5 h. The guard's own suites fall from
  7,847 cases to 581 (about 320 s to 45-50 s of wall time).
- The cut's counts take representative rows per KPI class; they may move by about ±15 % when the designer picks the
  rows at the cut (each class a KPI line names stays).

## Decisions for the owner (each with the recommendation)
1. **Tier 2** (the cap of 6 per KPI line, after each line's named case is kept). Recommended; medium confidence (the
   cap's case choice is made at the cut and checked by the reviewer against the regenerated README maps).
2. **`lifted` in D-10 (T-10):** not counted in the full run; run once, report-only, in D-10's window, and whenever a
   change reaches its code; its reds filed against each lifted feature's home ticket. Recommended (both parts).
3. **Move, do not delete, the lifted features' cases** (PD-1): they stay built and tested in the product (DEC-953),
   outside the full run. Recommended, high.
4. **W2-84's hidden-half cases** (363): opt-in now, deleted with the guard's hidden-half rule at D-9 (G-3: no guard
   rule needed). Recommended, high.
5. **The live guard hook's tests into the suite** (PD-4, G-9): today the five-rule hook and G-14's `role_paths` have
   no case under `tests/`: their 683 cases live only in the CTO's scratch (`drafts/act-guard-fix-4/`, `drafts/g14/`).
   Move them into `tests/unit/hooks/`, cut to about 60 representative cases. Recommended, high: a guard change
   otherwise has no test in the full suite.
6. **W2-58's counterpart-read cases:** keep about 30 while G-14 holds; rewritten if D-9 adopts `role_paths` as the
   product's. Recommended, medium.
7. **CAP-62's escape hatch:** opt-in, unless the owner wants the five-rule profile to refuse it (then 2 cases stay).
   Recommended opt-in, medium.
8. **One owner line (W1-06's red):** in `governance/project/tool-registry.yaml`, the `gov` entry's `approved_by`
   becomes `DEC-1037` (which names the tool; DEC-1052 does not). The registry is the owner's.
9. **D-3's moved items as proposed in part B §4:** T-6 (W1-19/W1-21 selected only by model-path changes, with
   W2-66's live test-map case revised in the same change); T-7 (a `helper_exceptions.txt` beside `select_tests.py`:
   the test map's schema is closed, so a `helpers:` key would refuse every selection); Q-8 (`accepted_history`,
   `trailers_base` deleted); Q-10 (the ratchet lists frozen, not deleted: W1-01's history case reads
   `acceptance_exemptions`); T-11 (CI off here, with W1-40's workflow cases to `lifted`).
10. **M3** (two byte-identical code-under-test checks): not done (low value).

## How the cut is applied once approved
1. One test designer applies the red fixes first (part B §5: W2-108's PATH filter, with its latent copies in W2-126
   and W2-54; `.claude/hooks` in W1-46's `PROJECT_PATHSPECS`, which clears W2-54's sandboxed-worker case and W1-46's
   live cases; W2-59's planted project), then T-6, T-7, T-11, then the cut part by part, in its own worktree.
2. One independent reviewer checks the regenerated README maps (every kept KPI line has its case) and the counts.
3. The CTO merges it; the scoped selection and `select_tests.py` are re-checked; D-10's full run then uses the cut
   suite.
Est. a day with the review (two designers in parallel, A and B), inside D-4b's machine split (D-4 two heavy slots).

## Open rows (not blocking)
- 78 KPI lines in 13 capped suites of part B are placed by rule; each gets a named case at the cut.
- W2-42a's 13 KPI lines have tests only on its stopped branch (not counted; its fate is D-9's).
- Part B's `unit/hooks` row is 75 → 31 (A takes `test_w2_106_template_hook_lines.py`, 44 cases); the totals above
  already count it once.
