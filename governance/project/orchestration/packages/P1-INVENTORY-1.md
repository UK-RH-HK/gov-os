# P1-INVENTORY-1 — The tests and the code inventoried (DEC-1039 item 2): the list of deletions, merges and revisions, for the owner first

Written 2026-11-02 19:50 by the CTO (session debdb3f7). The full report: `INVENTORY-TESTS-CODE-1.md` beside this file
(a read-only analyst's, every figure with its command; estimates marked).

## 1. Context
DEC-1039 item 2 (the owner, 2026-11-02): before the full suite, a report of the code's size and the tests, which are no
longer needed, which repeat or can be merged, even across tickets; then test designers refactor the tests (an
independent reviewer checks them) and a senior engineer refactors the code; every KPI line stays covered by at least
one test; **the list of deletions and merges goes to the owner first**. The inventory could start in parallel with
item 1; the refactor waits for stable infrastructure.

## 2. What was found
- **Size:** product code (`src/`) 18,963 code lines; tests 175,510 (unit 24,215, acceptance 151,144): about 7.7 test
  lines per product line. Kernel template 11,458; the CTO's tools about 16,200.
- **Tests:** 19,285 cases (3,498 unit in 39 folders, 15,787 acceptance in 86 ticket folders); the guard about 9,000 of
  them. Measured case time 32,298 s.
- **True repetition is small:** 3 groups of byte-identical test bodies; 72 same-file families differing only in
  values; 162 groups of copied helpers. The count comes from breadth (roles x tools x input forms), not copies.
- **One costly repeat:** W2-54's two "green here" cases each run a full `gov check --json` on this repository, once
  per phase: about 900 to 1,800 s a nightly (M1).
- **Side findings:** the 11-02 nightly wrote no JUnit XML (no per-case durations: the nightly should pass
  `--junitxml`, as `close_build.py` does; it rides the gitleaks engineer's `nightly.sh` change now in work); the
  register's status lines still say ACCEPTED for DEC-798 (replaced by DEC-1033), DEC-947, DEC-466 and DEC-929 (listed
  in `ARCHIVE-SUPERSEDED.md`), so W2-55's propagation check cannot see tests that still enforce them.

## 3. Why it matters
The full suite must go green on the re-pinned head (DEC-1039 item 3) and stay affordable once a day. Removing dead and
repeated cases cuts the nightly and the noise; keeping every KPI line covered keeps the evidence EXAMIN's copy relies
on. The savings are modest (3 to 8 % of case time); the larger cost is in breadth, which this list does not touch.

## 4. The list (each row: approve or reject)
| Id | Kind | What | Reason | Saving | KPI line kept by |
|---|---|---|---|---|---|
| D1 | delete | W1-01's 28 interim cases (`test_w1_01_settings_deny.py`, `test_w1_01_history.py`) and the `interim` fixture | enforce the interim guardrail DEC-084 retired; skip on every run | 28 cases, ~95 lines | W1-01's record cases and the guard's W1-02/04/05/33/47 cases; Failure 3 retired as spent (as DEC-925 did for Failure 2) |
| D2 | delete | `tests/unit/install/test_install.py::test_unfrozen_repo_asks_install_for_orchestrator` | byte-identical to `test_orchestrator_install_gets_ask` | 1 case | the twin |
| D3 | delete | W1-24 `test_the_hash_is_stable_across_two_runs` | the same calls and assertion as `test_the_same_ticket_and_commit_give_the_same_packet_hash` | 1 case | the twin (CAP-38.b) |
| M1 | merge | W2-54's two "gov check gives ... green here" cases into one run | one `gov check --json` paid twice a nightly | ~900-1,800 s (est.) | the merged case (S3, S4) |
| M1b | merge (designer judges) | W2-54's time-limit case reads its seconds from M1's run | the same context check again | ~150-630 s (est.) | S2 |
| M2 | merge | W1-45's two orchestrator scratch-write cases | same writes, same expectation | 1 case | Success 7 |
| M3 | merge (optional) | W2-02 / W2-03's byte-identical "this worktree's code" case | one check | 1 case | `tests/acceptance/conftest.py` |
| M4 | fold | 72 same-file families (152 functions) into parametrised tables | same body, other values | ~1,070 lines (case ids change; READMEs updated) | unchanged |
| M5 | fold | W1-27's 3 stale-path cases | same run, another planted path | ~50 lines | CAP-06.d |
| M6 | share | 162 copied helper groups into shared support modules | copies | ~1,500 lines | n/a |
| M7 | share | W1-19 / W1-21's real-model dev-tier build into one session build | the same build twice | ~40-80 s (est.) | unchanged |
| M9 | merge (after W2-54's revision) | `test_emg_query_device.py` into `test_semantic_cpu_embedder.py` | two rounds' cases of the same calls | 2-3 cases | n/a (unit) |
| R1 | revise | W2-66 `test_the_path_map_s_test_inputs_are_in_the_test_map` | skips forever; no other coverage (deletion blocked) | — | itself, revised |
| R2 | revise | W1-26 `test_exit_0_when_all_checks_green` | 46 s then a skip; no other coverage | up to 46 s | itself, revised |
| R3 | revise | W1-35 "a stated ceiling of tickets in flight" clause | enforces DEC-737/776/786, replaced by DEC-847 and DEC-942 | — | the row's other clauses |
| R4 | revise | W1-19 / W1-21 `HIT_AT_5_PASS_LINE = 80.0` | DEC-833's floor is 85 | — | the same cases |
| R5 | revise | unit `test_lexical.py::test_the_chunking_is_the_carried_one` | the carried govbridge code is retired | — | itself |

Not listed: W2-54's DEC-798 cases, being revised now under DEC-1033 (emergency item 1).

**The code (for the senior engineer, after the infrastructure is stable):** 15 frontmatter parsers (5 byte-identical
in `src/gov/check/*`) into one; 3 identical `_ids` helpers; 3 sha256 helpers; 14 git wrappers (only with care: the
guard's are on its hot path); one dead function (`close/evidence.py` `junit_rel`). `retrieval/synthesis.py` is built
but unwired (reached only by tests): kept under DEC-953 unless you decide otherwise.

**Options:** (a) approve the list as recommended below; (b) approve only the deletions and revisions, no merges or
folds now; (c) defer all of it until after the lift. Cost of (a): about 3 to 4 hours of test designers' and one
reviewer's work once item 1 is stable, then a scoped run of the touched suites; risk low (each case's KPI line named,
an independent reviewer checks coverage). (b) saves less than 1 % of nightly time (M1 is a merge). (c) leaves the
1,800 s repeat in every nightly until then.

## 5. Recommendation (confidence high for D1-D3, M1, M2, R1-R5; medium for M4-M7)
(a): approve D1, D2, D3, M1, M2 and R1 to R5 now, to be done by test designers with one independent reviewer as soon
as item 1's fixes are live; M1b at the designer's judgement; M4 to M7 later, when there is time; M3 optional; M9 after
the W2-54 revision lands. The code list to the senior engineer after the infrastructure is stable. And, under DEC-866
item 1 (no decision needed, the rule says mark at once), I mark DEC-798, DEC-947, DEC-466 and DEC-929's status lines
with what superseded them in the next records commit, so the propagation check sees them. Classification: no finding
fails open or loses work; the deletions remove only cases that skip always or have an exact twin.

## 6. What it blocks, and what waiting costs
It blocks only the test refactor (item 2's second half); item 1's fixes and the full run go on without it. Waiting
costs up to about 30 minutes per nightly (M1) and keeps 30 dead or duplicate cases in the count.
