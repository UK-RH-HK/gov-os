# D6-PART2 — the code tidy-up, part 2: items, home tickets, order (DEC-1109 (2))

**Basis:** DEC-1109 (2) restarted D-6 part 2 beside D-5. P1-PLAN's D-6 row and §D: E-2's four coupling edges,
`retrieve.py` and `measure.py`, `gov links`' code and test findings (LINK-INTEGRITY §7). The rows filed into it:
DECIDED-NOT-DONE rows 24 (the W2-130 sitting), 41 (W2-147), 60 (DEC-1108 (5)) and 65.
**Measured at `0240833b` (11-09):** `gov links --all` 2,036 standing, 2.9 s. In `tests/`: 557 UNKNOWN_ID and 73
ENFORCES_SUPERSEDED (29 cite DEC-002 or DEC-013 inside planted registers and records; 40 cite DEC-798 and 4 DEC-876 in
README history lines, real citations). Six STATUS_CONFLICT on MR-1 to MR-6. The loader's verbless change labels give
ten wrong changer pairs by the CTO's probe (the sitting counted 8).

**How it runs (emergency mode, DEC-1109):** the CTO launches each worker with `launch_worker.sh`, at most one at a
time, waits by pid only. Tests first: the independent test designer, then the engineer, then one review. Records go to
a product-spec worker with one review. Branches are reported READY with their heads; nothing merges into
`w2/integrate` here. W2-139, W2-140 and D-5 are others' and are not touched.

| item | what | home ticket | why there | worker chain | branch(es) | state |
|---|---|---|---|---|---|---|
| A | `gov links` skips planted ids in test fixtures: an id inside a non-docstring string literal of a Python test file gives no UNKNOWN_ID, and its ENFORCES_SUPERSEDED is not carried. This covers the 29 places that cite DEC-002 or DEC-013 | **W2-129** (`DAEO-q7lk`), new **S17** | the code is `src/gov/links/**`, W2-129's own; W2-55's propagation is left unchanged | designer → engineer → review | `w2/W2-129-d6-tests`, `w2/W2-129-d6` | **READY** 11-09: `w2/W2-129-d6` head `0eb83d9ad` (accept 150/0; review READY, 3 rows: F1 the embedded-program comment counted as planted, F2 strings like skip reasons are quiet by design, F3 t-strings; none blocks); `--all`: test designer UNKNOWN_ID 560 → 60, ENFORCES_SUPERSEDED 73 → 45; not merged |
| B | the loader's verbless **Changed by:** labels: only the ids at a clause's head are changers (the ten wrong pairs) | **W2-92** (`DAEO-n0wb`), new **S11** | `src/gov/store/loader.py` is W2-92's | designer → engineer → review | `w2/W2-92-d6-tests`, `w2/W2-92-d6` | **READY** 11-09: `w2/W2-92-d6` head `27d9ecaa3` (accept 143/1, S11 28/0, F6 27/0; the 1 red, `test_w2_92_unchanged.py::test_u1_…[unknown symbol]`, is red on the base too, so it goes to D-10's list; review READY, 4 rows, none blocks); not merged |
| C | MR-1 to MR-6 regenerated from `contract.yaml` (status ACCEPTED, version 4.2) | **W2-151** (`DAEO-qzca`, new, LITE) | no open ticket holds `docs/contract/master-rules/`. Taken out of D-5's list, so it is done once | product-spec → review | `w2/W2-151` | **READY** 11-09: `w2/W2-151` head `539437dff` (six records ACCEPTED, version 4.3; STATUS_CONFLICT 6 → 0; review READY, no finding). Re-run it if W2-139 changes the version or a master rule; not merged |
| D | the live-hook suites write to a temporary call-log folder (`GOV_GUARD_CALLS_DIR`), set once in `tests/conftest.py` and in each suite that builds the hook's environment | **W2-141** (`DAEO-xwro`), new **S4**; `tests/conftest.py` added to its paths | DECIDED-NOT-DONE row 60 gives it to W2-141's designer; tests only | designer → review | `w2/W2-141-d6-tests` | **READY** 11-09: head `92b38e74e` (accept 184/0; the scratch HOME holds no call log after the runs; review READY, 1 row: the conftest header lacks the line). Five unit suites run the template's hook with an environment built from nothing; that hook keeps no call log today (rows for their tickets); not merged |
| E | E-2's four coupling edges, including `retrieve/command.py` and `retrieval/measure.py`; `gov.decisions/__init__` made lazy; moved names re-exported | **W2-150** (`DAEO-ijf5`, new) | the edges cross W2-92, W2-55, W2-61h, the guard and close; no one ticket holds them | designer (static import walk) → engineer (senior) → review | `w2/W2-150-tests`, `w2/W2-150` | **READY** 11-09: `w2/W2-150` head `b85efb879` (accept 26/0; the walk goes from 101 modules and 25,596 lines to 53 and 11,095, with no gate module; `import gov.guard.decide` 15.0 → 14.5 ms; review READY). Row R1: copies of `_Glob`, `load_yaml_unique` and `close.repo.git` sit in `gov.util.parts` and `gov.store.loader`, latent fail-open if the originals are fixed alone; follow-up E2 (the originals re-import, in `guard/protected.py`, `guard/heldout.py`, `close/repo.py`), with or right after the merge; not merged |
| F | the rest of `gov links`' test findings after A: the 44 README citations (DEC-798, DEC-876) and the UNKNOWN_IDs left in comments | **W2-130** (`DAEO-q8cl`) for `**Kept:**` lines in the register; the test designers for any rewrite | record work, W2-130's paths | CTO (records), sized after A lands | — | after A |
| F2 | W2-55's narrower relation check (`decisions/tags.py`) removed (LINK-INTEGRITY §7) | **W2-55** (`DAEO-arrl`) | `src/gov/decisions/**` | engineer → review | — | after E (both touch `decisions/`) |
| F3 | any W2-130 mark the loader's wrong pairs proposed is checked and corrected | **W2-130** | its marks | CTO | — | after B |
| G | `gov plan`'s cycle row | W2-147 | — | — | — | **DONE** (merged `7ed72a1e`, review READY); closes at the lift's re-pin |

**Order (one worker at a time):** A, B, D, E, C, then F, F2 and F3. A comes first because it removes most of the
standing noise in `tests/`, which makes F's size known. B before F3. C waits for W2-139's landing only if W2-139 changes
a master rule's text.

**Verification per item:** `gov accept <W2>` on the branch, scoped (no full suite); `gov links --all` before and after
(A, B and C: the expected counts fall); the CTO's structural pass after each record commit; for E, the static walk
and `select_tests.py` on a `src/gov/retrieval/` diff.

**State 11-09 23:00:** A to E are READY and none is merged. These reds were found and are red at the base too; they go
to D-10's list:
- `tests/acceptance/W2-92/test_w2_92_unchanged.py::test_u1_…[unknown symbol]`: the bundle now holds the path map;
- three `tests/acceptance/W2-55/test_w2_55_backfill.py` cases;
- `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`.

Rows:
- five unit suites run the template's hook without `GOV_GUARD_CALLS_DIR` (harmless while that hook keeps no log);
- `gov links` might also check the master-rule records' version.

**Next:** F, F2 and F3, after A, B and E merge.

**State 11-10 00:20:**
- A to D are merged (the CTO).
- **E is READY with its follow-up** on `w2/W2-150`, head `892c6f851`: S6 gives `_Glob`, `load_yaml_unique` and the git
  runner one source each (`gov.util.parts`, `gov.util.gitrun`), so no copy is left. Its review is READY with no
  finding. The CTO's runs at that head, outside the sandbox, with the tree's code under the pinned interpreter:
  - `guard4_check.py` PASS (453 cases run, 0 failed);
  - `test_guard_fix_4.py` 467 passed;
  - `test_g14.py` 151 passed, 1 skipped;
  - `tests/unit/hooks` 102 passed;
  - `gov accept W2-150` 32/0.
- **C still matches** `contract.yaml` 4.3 after W2-139: all six records, every field.
- **F3: no wrong mark.** No W2-130 mark heads with a source from the ten wrong pairs.
- **F is started:** a test designer on `w2/D6-F-tests` (under W2-129) takes the 45 ENFORCES_SUPERSEDED and the 60
  UNKNOWN_ID left in the tests. For each ENFORCES_SUPERSEDED it decides between history (a Kept list for the
  register, the CTO's), an old citation of a current rule (re-cited), or a real finding (reported).
- **F2 waits:** it starts when W2-150 merges (both touch `decisions/`).

**State 11-10 01:20:**
- **F is READY:** `w2/D6-F-tests`, head `2761682a2`. It changes comments, docstrings and READMEs in 53 acceptance
  files; the AST shows no code change. The test designer's findings go from ENFORCES_SUPERSEDED 45 and UNKNOWN_ID 60 to
  8 and 0. Its review is READY.
  - W2-07's Kept lines are on DEC-876 (`6c8a24fc`), so 4 of those 8 are already gone on `w2/integrate`.
  - **The rows:**
    - F1/F2: three stale "wholly on the CPU (DEC-798)" comments (W1-19, W1-21, W1-22 support) and W2-108's README
      line;
    - three findings in `tests/unit` with no owner;
    - the W2-54 `shared_gpu` case still asserts the CPU, against DEC-1033 (2)(b); a designer revision on D-10's list.
- **F2 waits** for W2-150's merge.
- **F3: none.**

**State 11-09 23:30 (machine clock):**
- **F2 is READY in two branches that merge together:**
  - `w2/W2-55-f2`, head `2fe928a4c`: W2-55 S9 removes `tags.py`'s `STATUS_RELATION_UNMARKED`. Accept 55/3; the 3 are
    the base's backfill reds.
  - `w2/W2-129-f2`, head `c031faba0`: W2-129 S18 makes a `**Settles:**` label a change for UNMARKED_CHANGE. Accept
    156/0; `--all` 1,404 → 1,405, adding DEC-026 ← DEC-086.
- **The reviews:** round 1 found F1, blocking (an unmarked Settles was left unreported once the old check went).
  Round 2 is READY. Its rows: R2-F1, a PROPOSED changer gives no finding (by design); R2-F2, a status line naming the
  changer anywhere counts as marked (Wave 3 row).
- **Out-of-date text naming `STATUS_RELATION_UNMARKED`:** W2-129's ticket and LINK-INTEGRITY. Rows.
- **D-6 part 2 is complete** once those two branches merge.
