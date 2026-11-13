# fresh80: the fresh 80's tools (FRESH-80-1 §2 items 14 to 19; DEC-1097 (1))

Built 2026-11-08 for the CTO (session `ad44f5fe`), for one independent review. **Nothing here has run against the
real set.** Every test runs on a planted synthetic set (tests/conftest.py) with a fake gov and a fake model; no
search, GPU or model call was made.

## The rules every tool keeps
- **Paths.** Each tool takes `--sets-root ~/gov-os-eval` and derives the set (`memory-verdict-2/hidden`) and the run
  folder (`runs/fresh-80/`) in its own code (`f80lib.paths`). No command below names a hidden folder.
- **Output.** Standard output carries ids and counts only. `f80lib.say` (and `say` in the bash scripts) refuses a
  line naming the sets root's folders, `memory-verdict-2/` or `fresh-80/`; the E4 bash copies print the run folder as
  `<run folder>`. No question, gold answer, answer, or category beside its id is printed. Helper stderr goes to files
  in the run folder, never the log.
- **The reader's prompt is E2's, byte for byte** (readiness review F6). `READER_SYS` (with the "may be incomplete"
  line), `READER_SCHEMA`, `GRADER_SYS`, `GRADER_SCHEMA`, `CAP` (3), `prompt_of`, `items_of`, `outcome` (the A1/A2/A3
  cut) and `mcnemar` are read from `drafts/d4b/e2_run.py` by its syntax tree (`f80lib.e2_parts`), never retyped; the
  file is pinned by sha256 (`E2_SHA256`), so a changed e2_run.py refuses the run. The attempt loop is e2_run.py's.
  `tests/test_reader.py` checks the hashes of the strings, the code of `prompt_of` and `outcome`, and runs one
  question through e2_run.py's own `one()` and the reader's `one()`: the same prompts in the same order.
- **The store** (readiness reviewer 1): run_measure.sh refuses to start while `GOV_STORE` is set (S6: W2-116 makes it
  win over the clone) and runs every measure with `GOV_STORE` and `GOV_TICKET` unset; it **does not rebuild** the
  clone's store (S7: e0_run.sh's rebuild step is dropped; the 80 runs on E0's clone store as written 2026-11-07
  15:58); it records `store.db`'s sha256 before and after each attempt (a change is a fault that stops everything),
  and integrate's head and the new lines of `log/integration-store.log` over the run window (S5). Tests:
  `test_refuses_gov_store_and_writes_nothing`, `test_no_rebuild_in_the_script`, `test_full_run_counts_attempt_1`
  (store sha unchanged, head and log recorded), `test_store_change_is_a_fault_that_stops`.
- **ACT-GUARD-SETS-1 first** (readiness-7 F1): `run_measure.sh`, `preflight.py`, the reader, the data tool, the
  figures, `f80_e5_live.sh` and `f80_e4_prep.sh` refuse before writing anything unless the main tree's
  `governance/project/path-map.yaml` holds a `sets_root_hidden` block for this sets root with `runs/fresh-80/**` and
  `fixtures/evaluation/memory-verdict-2/**` among its hidden globs and the orchestrator among its refused roles, and
  the live `.claude/hooks/pretooluse.py` holds the sets-root rule (`sets_root_rule`). Checked by content, never by hash
  (`f80lib.act_applied`). Tests: `test_refused_without_the_act` (bash), `test_refused_without_the_act_nothing_written`
  (pre-flight), `test_reader_refused_without_the_act`.
- **A retrieval answered otherwise than declared** (code review F1): a search whose bundle was not reranked by the
  shared service (`rerank.by` other than `service`: a private worker or `unavailable`), a route (lexical or semantic)
  missing or unavailable, or the pool's rerank fallen back (`f80lib.degraded`). In the measure and the control every
  kept search is read: one such search makes the attempt not whole (a §3.5 fault) and fails the control; counts by
  `rerank.by` are printed. In the reader such a later search is a failed search (item 17), with its kind and
  `rerank.by` kept. Tests: `test_degraded` (8 cases), `test_degraded_search_is_a_fault_then_one_restart`,
  `test_degraded_later_search_counted`.
- **No restart into the same outage** (code review R1): before each attempt, `run_measure.sh` checks the live reranker
  READY from the pin (its last READY pid running the pin's `rerank_service.py`) and a probe search answered as
  declared, then runs the control, the families line and the declaration's digest again. Failing before the restart:
  nothing is spent, no STOPPED, and the one `--restart` stays open for when the servers are back. Tests:
  `test_live_check`, `test_no_restart_into_the_same_outage`.
- **The digest and the declaration** (readiness-7 F6, F12): the run refuses unless the declaration is committed in
  the main tree, has no `____` left, and its digest line equals the set's digest now and the pre-flight's (rechecked
  before USED and before each attempt); the reader rechecks the digest; the figures print it. Test:
  `test_refused_declaration_blank_uncommitted_or_digest_moved`, `test_reader_refused_when_the_digest_moved`.
- **Errors** (readiness-7 F10): each Python tool runs in `f80lib.run_tool`: standard error goes to
  `<run folder>/<tool>.err`; the CTO sees one line (a refusal's text, or `ERROR: <class>`). Test:
  `test_traceback_goes_to_the_run_folder`.
- **Item 6's drop** (readiness-7 F2, code review R2): an id that now exists is the declared drop (recorded,
  `dropped: true`, the pre-flight still clean), never a stop. Test: `test_nonexistent_id_now_exists`.
- **The hold** (readiness-7 F5): `hold.sh begin` never overwrites an existing `log/act-in-progress.txt` (it stops and
  shows it); `hold.sh end` ends only the FRESH-80 hold. Test: `test_hold_never_overwrites_and_ends_only_its_own`.
- **Rows taken along:** one runner at a time (`flock` in run_measure.sh, a lock in the reader: R3); `--restart` when
  USED stands and no attempt began (R9); 2 GiB free for the run folder and /tmp (R5); E5's live part and E4's prep
  require every judged question run with no brake stop (R4); the figures refuse a denominator other than 79 (R10).
- **Pins.** After the review is READY, the CTO pins the files (below). run_measure.sh, the reader, the data tool and
  the E4 and E5 scripts refuse to run unless every pinned file matches.

## The files
| file | what |
|---|---|
| `f80lib.py` | paths, `say`, E2's parts, the loader (the measure's `_load`), the ledger and brake, `claude` (a call that returned nothing run once more), `search` (failures and degraded answers counted), `degraded`, `set_digest`, `act_applied`, `run_tool`, the bar, the exact (Clopper-Pearson) and Wilson intervals, the pin check |
| `hold.sh` | the hold: begin only when no mark stands; end only its own |
| `preflight.py` | items 1, 2, 5, 6, 12; writes `preflight.json` (not once USED exists) |
| `f80_check.py` | run_measure.sh's checks: families line, clone, pre-flight, store digest, ACT applied, the declaration, the live reranker and a probe, the control, an attempt whole (every kept search answered as declared) |
| `run_measure.sh` | USED, the control, the 80, the fault rule (§3.5), head and store records |
| `fresh80_reader.py` | the judged reader run (A1/A2/A3; A2 judged), resume, brake, items 6, 8, 16, 17, 18; `--dry` |
| `fresh80_figures.py` | the verdict line (judged only), the beside-figures, the data table |
| `fresh80_data.py` | the data conditions e3, e3sa, e5, e4, e2g (each its projection and brake; `--dry`) |
| `f80_e5_live.sh` | E5's second live retrieval of the 80 (page 40, 12,000 tokens) |
| `f80_so_measure.sh` | so_measure.sh for the 80 (one set; records under the run folder; GOV_STORE unset) |
| `f80_e4_prep.sh` | E4 on the 80: run A (live 0.6B for missing texts, backstop), run B, seeds, window caches, the count |
| `f80_e4_window.sh`, `f80_e4_replays.sh` | built by `make_f80_e4.py` from `score-once/e4_window.sh` (WITH its F1 restore fix) and `e4_replays.sh`; the changes are the list in make_f80_e4.py |
| `tests/` | 74 tests on the planted set: `pytest drafts/fresh80/tests` |

## The command sequence (the CTO)
Set once: `F=.gov-runtime/scratch/orchestrator/drafts/fresh80; PY=~/.local/share/gov-os/pin-bcea09060ebc/bin/python;
mkdir -p ~/gov-os-runs/fresh-80`. Every wait or stop by pid or `-pgid` with `tools/proc.sh` only.

0. **Review and pin** (after READY): `cd $F && python3 make_f80_e4.py --check && sha256sum f80lib.py preflight.py
   f80_check.py run_measure.sh fresh80_reader.py fresh80_figures.py fresh80_data.py f80_e5_live.sh f80_so_measure.sh
   f80_e4_prep.sh f80_e4_window.sh f80_e4_replays.sh hold.sh > FRESH80-REVIEWED.sha256`.
1. **Pre-flight** (after the checker's staleness pass and ACT-GUARD-SETS-1 applied; the tools refuse otherwise). The
   checker reports its digest as `cd <set folder> && LC_ALL=C sha256sum *.yaml | sha256sum`:
   `$PY $F/preflight.py --sets-root ~/gov-os-eval --expect-sha256 <the checker's digest> --expect-changed <its re-labelled count>`.
   It must end `PRE-FLIGHT: every check as expected`. Anything else: fix before any search (§3.5: the set is unused).
2. **The declaration**: fill every `____` of `FRESH-80-DECLARATION.md` (the ACT's commit, the digest, the counts, the
   interval, the rubric version) and commit it before any search; run_measure.sh refuses a blank, an uncommitted copy
   or a digest that is not the set's. Wait for the integration store's refresh line after this commit (readiness-7
   F11).
3. **The hold begins**: `bash $F/hold.sh begin` (it stops and shows any mark already in place: never overwritten);
   W2-139/W2-140 held.
4. **Control and measure** (one command; the control first, the 80 only if it passes):
   `setsid bash $F/run_measure.sh --sets-root ~/gov-os-eval > ~/gov-os-runs/fresh-80/measure.out 2>&1 < /dev/null &
   echo $! > ~/gov-os-runs/fresh-80/measure.pid`; wait with `bash tools/proc.sh wait --max 3600 $(cat
   ~/gov-os-runs/fresh-80/measure.pid)`. Exit 0: an attempt counts. A backstop trip or machine stop: stop the group
   (`proc.sh stop -<pgid>`), then the same command with `--restart` (allowed once). "Not ready before the restart"
   (the live reranker or the control): to the owner; `--restart` once the servers are back. A second fault: to the
   owner.
5. **The judged reader run**: `$PY $F/fresh80_reader.py --sets-root ~/gov-os-eval --dry`, then
   `$PY $F/fresh80_reader.py --sets-root ~/gov-os-eval > ~/gov-os-runs/fresh-80/reader.out` (its standard error goes
   to the run folder by itself; projection 15 USD,
   brake 30). After a stop, the same command resumes (finished questions are never run again); a brake stop goes to
   the owner first.
6. **The hold ends**: `bash $F/hold.sh end` (only the FRESH-80 hold; any other mark is shown and left).
7. **The verdict figures**: `python3 $F/fresh80_figures.py --sets-root ~/gov-os-eval` (re-run after each data
   condition: it adds the data table).
8. **Data conditions** (DEC-1097 (1)(c); each `--dry` first; all "data only, not judged"):
   - `$PY $F/fresh80_data.py e3 --sets-root ~/gov-os-eval` (36 / brake 72)
   - `$PY $F/fresh80_data.py e3sa --sets-root ~/gov-os-eval` (19 / 38)
   - `$PY $F/fresh80_data.py e2g --sets-root ~/gov-os-eval` (14 / 28)
   - E5: `setsid bash $F/f80_e5_live.sh --sets-root ~/gov-os-eval > ~/gov-os-runs/fresh-80/e5-live.out 2>&1 < /dev/null &`
     (about 20 min of GPU), then `$PY $F/fresh80_data.py e5 --sets-root ~/gov-os-eval` (17 / 34)
   - E4: `DRY=1 bash $F/f80_e4_prep.sh --sets-root ~/gov-os-eval`, then `setsid bash $F/f80_e4_prep.sh ... &` (one
     light GPU job); `DRY=1 bash $F/f80_e4_window.sh --sets-root ~/gov-os-eval`, then `setsid bash
     $F/f80_e4_window.sh --sets-root ~/gov-os-eval > ~/gov-os-runs/fresh-80/e4-window.out 2>&1 &` (the quiet GPU
     window: live service stopped and restored by its trap; stop it only by TERM to its pid with grace 300);
     `bash $F/f80_e4_replays.sh --sets-root ~/gov-os-eval` (no GPU); `$PY $F/fresh80_data.py e4 --sets-root
     ~/gov-os-eval` (22 / 44).
9. **Figures again** (step 7), then the result record to the owner: the verdict line, then the data table.

## Spend (projections from the 138's measured cost per question, times 80; brake at twice)
| part | projection | brake |
|---|---|---|
| control, measure, E5 live, E4 prep and window | 0 (GPU only) | |
| **the judged reader run** (E2: 0.157 a question) | **15** | **30** |
| e3 (E3: 61.93 for 140) | 36 | 72 |
| e3sa (E3-SA: 31.70 for 280 runs) | 19 | 38 |
| e5 (E5: 29.50 for 140) | 17 | 34 |
| e4 (E4: 37.33 for 280 runs) | 22 | 44 |
| e2g (E2G: 24.32 for 140) | 14 | 28 |
| **data conditions together** | **108** | 216 |

FRESH-80-1 §5 3(c), the option the owner chose, said "about $60 to $70 more"; the measured per-question costs give
108. Tell the owner the corrected figure with the launch notice (readiness-7 F8). The e2g figure on the 80 cannot
decide GLOSSARY-1 (DEC-1097 (6) open; §3.4 item 4; readiness-7 F9).

## Open for the CTO (design choices made, each reversible before the pin)
1. **The interval.** "Exact" is Clopper-Pearson: 70 of 79 gives 79.5 to 94.7 %. FRESH-80-1 §4.3's example (79.7 to
   93.9 %) is Wilson's interval. The figures print both; the declaration should name the one beside the verdict.
2. **The digest's form** is `LC_ALL=C sha256sum *.yaml | sha256sum` in the set's folder; the checker's brief should
   carry that line word for word (readiness-7 F3), with F4's four cases.
3. **A failed later search** is counted and named (item 17) but not retried, as E2 ran. Retrying once would not
   choose between answers; say if it should.
4. **A store change during an attempt** stops everything (no restart: §3.5's restart needs the same store).
5. **The control runs before every attempt** (the first, the in-script restart and `--restart`), after the live check.
   Code review F1 says the shared service "or private"; the coordinator's word is "other than the shared service":
   `rerank.by: private` is a fault here too (stricter; a private worker is the same model on a GPU slot).
6. **`GOV_ROLE=orchestrator`** is set for the reader's later searches, as the measure ran (E2 inherited the CTO's).
7. **e3_run.py's second call:** for a one-call question it took the next question's first call; fixed in the data
   copy (data only; the judged run is untouched).
8. **The hold** is the line `FRESH-80 HOLD` in `log/act-in-progress.txt` (hold.sh): run_measure.sh and the reader
   require it; the data conditions and E4/E5 scripts refuse while it stands.
9. **Left as rows:** R6 (no timeout on `gov retrieve` or `claude`, as in E2; the resume recovers a hang), R7 (an
   exception after an answer leaves no row; the question runs again on resume), R8 (the reader does not re-check the
   clone and store around its later searches; the hold covers it).
