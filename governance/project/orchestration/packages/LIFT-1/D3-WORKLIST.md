# D-3 — the configuration and text lifts, worked in this order (DEC-1052; P1-PLAN §A P1-2, §B)

**UNDER WAY (2026-11-03, session 33b3628c):** item 8 done; item 5 moved to D-4; items 11 and 12 drafted by product-spec
in `.gov-runtime/scratch/orchestrator/drafts/d3/` for the owner; items 9 and 10 by the CTO next.
**Moved to D-4 (decided by the CTO while writing this list):** items 2-4 (T-6, T-7, T-10: the selection) and 6-7 (Q-8,
Q-10: the ratchet keys): the path map and the test map are in the selection's shared core (a change to either runs
everything), and these rows touch the very suites D-4 cuts, so they go with D-4's test designers and the selection.

The CTO's worklist, from the plan's approved rows whose step is P1-2 (configuration and text on this repository).
Product code switches stay P1-9's (re-scoped tickets after the resume, option A); kernel text stays P1-11's (CIT-P).
Two rules shape it: the prompt is the owner's (prompt §0's own line), so its lines go to the owner as one patch; and
the briefs are rebuilt from the templates in D-5, so brief edits here are only the lines that are wrong today
(DEC-1052 question 4: no text that D-5 replaces anyway).

| # | row | the change here | where | state |
|---|---|---|---|---|
| 0 | (P1-2) | DAEO-tgk2 and DAEO-a3u2 no longer cover `tests/acceptance/` | `.tickets/` | DONE (a3u2 `8562ae79`; tgk2 found clean, `core-mutation` green) |
| 1 | T-3 | policy coverage, skill-version and citations lifted, path-map a warning: on this repository nothing runs `gov check` but the R1-21 structural pass (a notice only, never a refusal), so nothing to configure; the product half is W2-45 (P1-9) and the policy half the CIT-P (P1-11) | — | DONE by R1-21 (notice only) |
| 2 | T-6 | W1-19/W1-21 selected only by model-path changes; the path-map and gitleaks-config couplings dropped | `governance/project/test-map.yaml` | to do |
| 3 | T-7 | a helper import reaches only the suites that call the helper: a `helpers:` exception for `tests/acceptance/W1-07/w1_07_support.py` | `governance/project/test-map.yaml` | to do |
| 4 | T-10 | the suites of features lifted here leave tickets' selections (nightly only), and the owner says whether they count in P1-12's full run | `.gov-runtime/scratch/orchestrator/tools/nightly_only.txt`, `select_tests.py` | to do; the P1-12 question goes with D-4's list |
| 5 | T-11 | CI off here (always red: 42 of 42 pushes) | `.github/workflows/ci.yml` | **moved to D-4** (CTO, 2026-11-03): W1-40's acceptance cases read this repository's own push workflows (`test_w1_40_workflow_text.py`, `support.push_workflows()`), so the switch-off goes with W1-40's fate in D-4's list (the template half is P1-11) |
| 6 | Q-8 | trailers are not refusals; `accepted_history` and `trailers_base` deleted here | `governance/project/path-map.yaml` | after D-4's list: W1-01's history case reads them |
| 7 | Q-10 | the ratchet lists frozen here; the load-sensitive list kept as the CTO's (`tools/load_sensitive.txt`, done in E1) | `governance/project/path-map.yaml` | after D-4's list (the same tests) |
| 8 | G-10 | `refusal_watch.sh` lifted (the harvest already stopped) | `.gov-runtime/scratch/orchestrator/tools/` | DONE 2026-11-03: not running, no caller; moved to `archive/lifted-d3/` |
| 9 | T-1, M-1, R-6, R-12 | the brief's wrong lines only: T-1's reason (the queue runs no `gov check`), step 6a and DEC-1027 H's trimming, the step-6 `gov checkpoint` record, the two-commit rule | `governance/project/briefs/LEAD-w2-common.md` | to do |
| 10 | R-6, R-8, R-12, O-11 | register amendments: DEC-511 lifted; delegated choices as ticket or close-record lines; DEC-896 item 2 and DEC-927 item 2 lifted; DEC-1012 and DEC-1003 scoped | `docs/DECISION_REGISTER.md` (one entry) | to do |
| 11 | R-9, R-11, R-12, O-6, O-11 | the prompt: one DECISIONS-IN-FORCE list (§0 points to it), pings only when work waits on the owner, the two-commit rule, ACTs only for machine changes with restarts by class, DEC-1012/DEC-1003 scoped | `governance/project/prompts/w2-orchestrator.md` | a patch to the owner |
| 12 | R-9, O-6 | DECISIONS-IN-FORCE cut to one list of about 8 KB, LIFTED-BY-DEC953 folded in; the class list of approved restarts (the owner's) | `governance/project/orchestration/DECISIONS-IN-FORCE.md` | with #11 |
