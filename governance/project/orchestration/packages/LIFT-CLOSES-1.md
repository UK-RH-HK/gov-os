# The lift's formal closes, prepared: each ticket's acceptance check on integrate (DEC-1125 (3) (ii))

Run by the CTO's helper on the night of 2026-11-10/11, 01:13 to 01:55 UTC, from a shared clone of `w2/integrate` at
`797495bdfc70` under `/tmp/gov-os-emg-closes/clone` (nothing written into the main tree). Each ticket ran as
`gov accept <W2>` through `heavy_slot.sh`, one at a time, with the clone's own `src/`. No ticket, status or test was
changed. `gov close` was not run: it has no dry-run, and a refused close of the kind noted below would be counted.
Raw answers: `/tmp/gov-os-emg-closes/<W2>.json` (W2-96's clean re-run: `W2-96-rerun.json`; W2-92 with the code-graph
tool visible: `W2-92-withtool.json`).

## 1. The table

| ticket | ready to close | reds | minutes the close will take |
|---|---|---|---|
| W2-92 (`DAEO-n0wb`) | **no, one small test-side fix** | 30 cases skipped, not red: the real code-graph tool is hidden from every suite but a short list (W2-56 S1). With "W2-92" added to that list: 144 passed, 0 skipped | accept 1 min; close about 15 to 20 |
| W2-05 (`DAEO-0z8c`) | **no, one record fix and a new probe** | 1 red, new: the sweep record does not name 5 files that start git | accept 2.4 min; close about 15 to 20, plus the probe |
| W2-96 (`DAEO-ouet`) | **yes** | none. The first run showed 3 reds (SIGHUP cases); they came from how the helper started the run, and the clean re-run is 190 of 190 | accept 4.5 min; close about 20 to 25 |
| W2-112 (`DAEO-clon`) | **no, no probe record** | none (59 of 59); a FULL ticket with no `docs/probes/DAEO-clon/` | accept 1.4 min; close about 15 to 20, plus a review round |
| W2-122 (`DAEO-blwa`) | **yes**, with one noted gap | none (22 of 22) | accept 2.3 min; close about 15 to 20 |
| W2-123 (`DAEO-qzrq`) | **yes** | none (50 of 50) | accept 1.2 min; close about 15 to 20 |
| W2-126 (`DAEO-jpr0`) | **yes**, with one noted gap | none (28 of 28) | accept 2.1 min; close about 15 to 20 |
| W2-151 (`DAEO-qzca`) | **no `gov close` route; a recorded CTO close** | none to run (LITE, no folder); its two lines hold on my own checks | about 10 for the record, no test run |
| W2-15a (`DAEO-rd0g`) | **no** | no acceptance run (research, no folder); the evidence route refuses it today | record fixes about 30, plus a probe; closes with W2-32 |
| W2-32 (`DAEO-0pyc`) | **no, a line is the owner's** | none (257 passed, 0 failed, 2 skipped); S9 is open: hit@5 was 58.3 %, below 85 % | not before the owner decides S9 |

Minutes for a close are an estimate, not a measurement: the acceptance run is measured (above); the rest is
`gov close`'s scoped regression and gates. On a merged ticket the scope has no diff, so it selects the ticket's own
folder plus the unit tree (116 targets; 443 paths ignored, 349 cases deselected, 94 `lifted` cases left out). The
older measure is 10 to 20 minutes a close (PLAN-W2-DEC953 section 2). I did not time the unit tree.
`python3 -m gov.close.batch run <tickets>` does one full rebuild, one `gov check` and one full regression for all,
then closes each in order; it closes nothing on a red run, so the two named warm-latency reds (DEC-1125 (1)) must be on
the known-reds lists first, or the CTO uses single closes.

## 2. The list, checked

- **Kept, as briefed:** W2-05, W2-96, W2-112, W2-122, W2-123, W2-126 (P1-PLAN P1-13, W-9); W2-92 and W2-151 (row 97).
- **Added:** W2-15a and W2-32. The records say they close at the lift together: P1-13 (`741faf90`), DECIDED-NOT-DONE
  row 35 ("closed together at the lift"), FORECAST-W2-2 (W2-15a "merged, not closed, closes at the lift"). Both are
  `not ready` above, for reasons that are not test reds.
- **Not added, named:** W2-20 (its S12 start half is W2-123's S7, which passes; the rest of W2-20 closes after the
  lift, FORECAST-W2-1). The forecast counts 34 merged-not-closed tickets (W2-139, 140, 149, 150, 56 and others); only
  these ten were in my brief, so the other 24 are not checked here.
- **Dropped:** none.

## 3. One block per ticket

Lines are the ticket's `kpis` lines (S = success, F = failure). "Cases" are from `gov accept`'s per-line counts; each
README's "KPI map after D-4's cut" section names them. A line with no case is named.

### W2-92, the record graph and the code graph as routes (STANDARD)
- **Command:** `gov accept W2-92`. **Counts:** first run 114 passed, 0 failed, 30 skipped, rc 3 (a fail by the
  runner's rule: a line with only skipped cases fails). With the tool visible (scratch clone, `tests/conftest.py`
  with "W2-92" in `_CBM_SUITES`): **144 passed, 0 skipped, pass**.
- **Red, cause:** not load, not a named red. `tests/conftest.py` (W2-56 S1) keeps `codebase-memory-mcp` off PATH for
  every suite but W1-16, W1-20, W1-41, W2-69 and `test_w1_06_digests.py`; W2-92's cases need the real tool and skip
  (`api` fixture: "codebase-memory-mcp is not on PATH"). Known since D10-REDS item 14 ("W2-92's 30 tool cases skip in
  every full run"), never fixed. Skipped cases: S1 9, S2 7, S3 6, S4 9 (half), F1 9, F2 6, F3 6.
- **Lines met (with the fix):** S1 9, S2 7, S3 6, S4 19, S6 15, S7 33, S8 28, S9 9, S10 1, S11 28, F1 9, F2 6, F3 6,
  F6 27. F5 (partial supersession, status on register chunks) has no line of its own: its cases sit under S8 and S9.
  **Not shown by a case:** S5 and F4 (W2-61's measure, both figures): the record `docs/research/W2-92-memory-measure.md`
  (hit@5 11 of 20, full evidence 13 of 20, control 11 and 11). S6 is met in part: the cases pass, but the cold
  `gov retrieve` median (about 1.2 s target) is the CTO's measure and is recorded nowhere (D9-FATES; evidence note).
- **The close needs:** one test-side change before the close: add `"W2-92"` to `_CBM_SUITES`, `tests/conftest.py`
  line 324 (one word; no other test pins the list). It is a tests path and a control question for the CTO to route;
  I did not touch it. STANDARD: no probe needed. Then `gov close DAEO-n0wb`.

### W2-05, the git environment of every check, hook and helper (FULL)
- **Command:** `gov accept W2-05`. **Counts:** 64 passed, 1 failed, 0 skipped, rc 3. Alone: the same case, named below,
  fails again (65 cases with `--optin=breadth`: 64 passed, 1 failed; the 30 default cases: 30 passed).
- **Red, cause (new):** `test_w2_05_sweep.py::test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`:
  `docs/research/AR-2-git-sweep.md` does not name 5 of the 33 files of `src/gov` that start git:
  `links/command.py` (W2-129), `rebuild/command.py`, `rebuild/integration.py` (W2-116), `util/gitrun.py` and
  `util/role_paths.py` (W2-150). I read each: all five already use `git_env` (role_paths its own `_git_env`), so this is
  a stale record, not a missing code fix. It was not in the D-10 lists I read.
- **Lines met:** S2 7, S3 28, F1 25 all pass; S1 32 passed and 1 failed (the sweep record, S1's "the sweep record
  lists every call").
- **The close needs:** five rows added to `docs/research/AR-2-git-sweep.md` (in W2-05's allowed paths; an engineer or
  the orchestrator). That is a commit on the ticket's work path after the last probe (`327f63e55`, pass at
  `9ca161a6fe38`), so the close's probe gate wants a fresh probe of the final head (`_check_probe`). Order: rows, fresh
  probe, then `gov close DAEO-0z8c`. Est. 30 min for the rows and the probe.

### W2-96, `gov accept`, the opaque acceptance runner (FULL)
- **Command:** `gov accept W2-96`. **Counts:** first run (helper started with `nohup`): 187 passed, 3 failed, 42
  unmapped; clean re-run from the session's own shell: **190 passed, 0 failed, 0 skipped, 42 unmapped passed, pass**.
- **Reds, cause:** the first run's 3 are `test_r2_…[SIGHUP]`, `test_r12_…[SIGHUP-twice-5-ms-apart]` and
  `test_premise_r11_…`. They tested "gov ends on SIGHUP"; a process started under `nohup` begins with SIGHUP ignored
  and the cases fail ("gov accept did not end within 60 s of signal 1"; premise "1 1 0", expected "0 1 0"). Not a code
  fault. They pass alone (6 passed). **Lesson for the CTO:** run the signal cases of W2-96 (and any close that runs
  them) from a shell that does not ignore SIGHUP (no `nohup`), or the close will see three false reds.
- **Lines met:** S1 14, S2 22, S3 23, S4 11, S5 36, S7 24, S8 38, F1 18, F2 23, F3 11, F4 31, all pass.
  **Not shown by a case:** S6 (a brief line; the README says it has no test). By reading, the engineer's template
  `role-engineer.md` line 15 names `{CMD:accept}` (`gov accept`, `facts.yaml:49`) and `LEAD-w2-common.md` names it; the
  word-for-word "only way" is the CTO's reading to confirm (D9-FATES said met in half).
- **The close needs:** `gov close DAEO-ouet`. Three W2-96 commits sit after the last probe (`8f6e66a17`, pass): README
  wording of W2-05 and W2-92 and S-D10a's text (`d269ed550`, `ba5cf0f87`, `1905b2969`, reviewed READY, 
  `reviews/D10-lift-maps-review.md`). They are not code; expect the probe gate to pass, and if it refuses, one more
  fresh probe. Do not start the close from a `nohup` shell.

### W2-112, one reranker serves every session (FULL)
- **Command:** `gov accept W2-112`. **Counts:** 59 passed, 0 failed, 0 skipped, pass (84 s).
- **Lines met:** S1 7, S2 5, S3 3, S4 14, S5 2, S6 13, S7 15, F1 13, F2 7, F3 3. No line without a case. S5 passes on
  the research record being present and naming the measure; its 48-question half is "not yet measured"
  (`docs/research/W2-112-shared-reranker.md`, "After W2-61h": a line met in part, D9-FATES).
- **The close needs:** a probe record. `docs/probes/DAEO-clon/` does not exist, and `_check_probe` refuses a FULL
  ticket with `PROBE_MISSING` (before any test, so not a counted refusal). W2-112 was accepted as built in D-1 without a
  review round on its final code. So: a fresh independent reviewer (one FULL round, never a third) on the head,
  its probe record committed with `Role: orchestrator`, then `gov close DAEO-clon`. Est. 1 to 1.5 h with the review.
  Owner or CTO to decide the S5 48-question half: run it after the lift, or re-word.

### W2-122, seeded rebuilds (STANDARD)
- **Command:** `gov accept W2-122`. **Counts:** 22 passed, 0 failed, 0 skipped, pass (140 s).
- **Lines met:** S1 10, S2 11, S3 1, S4 8, F1 10. S3 (the measure) passes on the evidence file naming it; the
  evidence note says a cold rebuild strictly alone was not measured and the seed base was the cold run's tree, not the
  integration store (`docs/changes/W2-122-evidence.md`): met in part, by the note's own words.
- **The close needs:** `gov close DAEO-blwa`. STANDARD, no probe.

### W2-123, the shared embedding server serves several requests (STANDARD)
- **Command:** `gov accept W2-123`. **Counts:** 50 passed, 0 failed, 0 skipped, pass (71 s).
- **Lines met:** S1 9, S2 17, S3 3, S4 1, S5 16, S6 13, S7 8, S8 4, F1 31. All lines have cases. S7 is also the start
  half of W2-20's S12 (D9-FATES), so W2-20's S12 needs nothing more from this close.
- **The close needs:** `gov close DAEO-qzrq`. STANDARD, no probe.

### W2-126, a machine-wide vector cache (STANDARD)
- **Command:** `gov accept W2-126`. **Counts:** 28 passed, 0 failed, 0 skipped, pass (128 s).
- **Lines met:** S1 5, S2 2, S3 5, S4 2, S5 2, S6 1, S7 11, F1 3, F2 1, F3 4. All lines have cases. S6 passes on the
  evidence file; its per-day "after" figure was not measured (needs the shared embedder's log after the cache lands;
  `docs/changes/W2-126-evidence.md`): met in part.
- **The close needs:** `gov close DAEO-jpr0`. STANDARD, no probe. Depends on W2-123 (`deps: [DAEO-qzrq]`): close
  W2-123 first.

### W2-151, MR-1 to MR-6 regenerated (LITE, specification, no acceptance folder)
- **Command:** none for tests. Read-only checks in the clone: `gov links --all` gives 0 STATUS_CONFLICT and no line
  naming `master-rules`; `python3 -m gov.check.schema` gives `ok: true`, 980 records. The six records say
  `status: ACCEPTED`; the diff of the merge (`6990f7f3e`) is 12 lines in, 12 out, six files, nothing else.
- **Lines met:** S1 (status, title, text, acceptance, version from `contract.yaml`: shown by the evidence note's
  per-record table and the diff), S2 (shown by the two checks above). F1, F2 by the diff. No case exists.
- **The close needs (the answer to "does `gov close` take the evidence route?"): no.** The evidence route
  (`EVIDENCE_CLASSES`) is research, audit, integration and coordination; W2-151 is `specification`. For that class
  `gov close` asks `gov readiness --ticket`, which answers `SPECIFICATION_NOT_FOUND` ("DAEO-qzca names no
  specification"), then needs acceptance tests and answers `NO_ACCEPTANCE_TESTS`. That refusal is counted (three end in
  an escalation). So do not run `gov close` for it: a recorded CTO close on the evidence note
  (`docs/changes/W2-151-evidence.md`) and the two checks above, delegated (DEC-1112 (3)). I found no earlier
  specification ticket closed through `gov close` without a folder.

### W2-15a, EXP-003 pass 1, the baseline (FULL, research, status open)
- **Command:** none to run (no folder). I called the evidence gate read-only: `EVIDENCE_REFUSED`, "names no evidence
  record under acceptance_tests.evidence" (the ticket has only `judged_by`).
- **Lines:** S1 (metric fixed before the first run, section 2), S2 (five modes, section 4) and S3 (the stacking
  test, section 6) and S4 (the evidence record holds every measure, names the gaps, section 8) are in
  `docs/research/EXP-003/w2-15a-baseline.md`. S3 is met in part: the lighter reranker was "not run (not installed)"
  (D9-FATES). The three moved lines went to W2-15b.
- **The close needs:** (1) the ticket's `acceptance_tests.evidence` naming the baseline record (a ticket edit: the
  CTO's); (2) the record has no front matter, and for research the gate wants `type: research` (a record edit; the
  file is in the ticket's paths); (3) a probe record: `docs/probes/DAEO-rd0g/` does not exist (FULL, `PROBE_MISSING`);
  (4) the S3 gap named in the close note. It closes with W2-32.

### W2-32, retrieval components and bounded improvements (STANDARD)
- **Command:** `gov accept W2-32`. **Counts:** 257 passed, 0 failed, 2 skipped, pass (235 s). Skips: S5's
  "keeps the order of a smaller one" skips by design when the build refuses a limit above its cap; the other is in a
  record case that needs the baseline measure folder (`W2_32_RUNS`), which I did not open.
- **Lines met:** S1 4, S2 13, S3 38, S4 12, S5 6, S7 75, S8 53, S9 8, S10 7, S11 35, F1 7. **Without a line:** S6
  (dropped, DEC-1083 (3)), F2 (its cases are counted under S11: "a pool setting absent or 0 that changes what a
  search returns; a request past the padded bound").
- **Why not ready:** S9 passes as a rule (the escalation logic and the record's wording), but the measured level is
  hit@5 58.3 % (28 of 48), below the 85 % floor, and "no improvement round has run yet" (the evidence note). The
  ticket's own words send that to the owner (escalate; at the third round the owner decides). W2-15a also gates it
  (`deps`). And DEC-1125 (2) now says the memory audit replaces ad-hoc re-measures.
- **The close needs:** the owner's disposition of S9 (close with the level reached, or keep open), then `gov close
  DAEO-0pyc` together with W2-15a.

## 4. Things for the morning

1. **Test-side fix, W2-92:** add `"W2-92"` to `_CBM_SUITES` (`tests/conftest.py`). Tests path; route it by role.
2. **Record fix, W2-05:** five rows in `docs/research/AR-2-git-sweep.md`, then a fresh probe.
3. **Review, W2-112:** one fresh probe round; its record committed by the orchestrator.
4. **Ticket and record edits, W2-15a:** `acceptance_tests.evidence`, `type: research`, a probe.
5. **Owner, W2-32 S9** (the 58.3 % level against 85 %), and whether W2-15a and W2-32 close at the lift at all.
6. **W2-151:** a recorded CTO close; `gov close` would refuse twice, counted.
7. **Launch hygiene:** run W2-96's signal cases from a shell that does not ignore SIGHUP.
8. **Not checked:** `gov close`'s own gates (trailers, `_check_unmeasured`, containment, collection, `gov check`) were
   not run, so each close can still find something the acceptance run does not.
