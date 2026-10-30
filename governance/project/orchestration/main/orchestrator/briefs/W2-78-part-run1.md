You are the ticket lead for ticket `DAEO-v4is` (`W2-78`, "Governance edits stop widening closes: the path map's lists in record files of their own; prompts and briefs record-only"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-78` on branch `w2/W2-78`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-v4is.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-78");
- the package `governance/project/orchestration/packages/P-SCOPE-RECORDS-1.md`, whole (it is short);
- DEC-941 (item 5), DEC-929 (item 1), DEC-889 (item 2), DEC-880, DEC-757, DEC-766, DEC-862 and DEC-895;
- the four lists in `governance/project/path-map.yaml` (`load_sensitive`, `accepted_reds`, `accepted_history`, `acceptance_exemptions`) and its schema, `template/governance/kernel/schemas/path-map.schema.json`;
- the test map, `governance/project/test-map.yaml` (`shared_core`, `record_only`, `record_reading`);
- the readers: `src/gov/close/ratchet.py`, `history.py`, `gates.py`, `traceability.py` and `select.py`; and, read-only, what `src/gov/close/command.py` and `src/gov/close/pytest_plugin/gov_close_results.py` hand on from them;
- W2-66's close record, `docs/close/DAEO-c1uz/CL-DAEO-c1uz.md` (its evidence block: `why_full`), and W2-66's live test-map case under `tests/acceptance/W2-66/`, the form of a readers' sweep.

## Why you start now

- **A governance edit turns the next close into a full run.** The path map is shared core, and prompts and briefs are placed by nothing. W2-66's close of 10-27 ran full on records alone: 4,186 s of tests against about 300 s for the scoped closes after it, about 65 minutes lost (P-SCOPE-RECORDS-1 §2).
- **Fast closes are the first item of EXAMIN's minimum** (DEC-930 item 1). The owner accepted the package's option (a) as this ticket (DEC-941 item 5).
- **Block A (DEC-941), beside W2-77 rather than after it:** your paths share no file with W2-77's, and every ready ticket whose paths do not overlap is launched (DEC-942 item 1).
- **Record work waits for the gaps between queues until you land** (DEC-929 item 2).

## The decisions for this run

- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour; it is a plan, not code. It says:
  - **the record files:** one per list under `governance/project/records/`, with a schema of their own as new files under `template/governance/kernel/schemas/`. Their entries are the path map's, entry for entry, in order, with every field;
  - **the readers:** which read which file, from where. **One source at any commit:** a reader never reads both the path map's list and the record file, and never their union. A record file that is missing or unreadable is named by the close, never read as empty and never replaced by the path map's list;
  - **the ratchet's rule unchanged on the new files:** a removal from `load_sensitive` runs the ratchet's own suites; a growing entry is refused unless the owner's commit adds it (DEC-757, DEC-766, DEC-862);
  - **the test map:** `record_only` gains the four record files and `governance/project/prompts/**` and `governance/project/briefs/**`. `record_reading` gains every reader the sweep finds. Nothing else in `test-map.yaml` changes: it is shared core, and W2-66's and W2-68's;
  - **the migration's order.** The path map is owner-only and is not in your paths (DEC-757, DEC-766). The entries are the owner's commits, so their move is the owner's commit, or is accepted by decision before the merge (the ticket file). State:
    - which commit holds the record files: the owner's ACT first, or your branch, accepted by decision;
    - the path map's patch that removes the four lists. It is the ACT's content, prepared in your scratch (`.gov-runtime/scratch/lead/act/`), and never committed by this ticket;
    - how an entry later added to the path map's old list is refused rather than silently ignored once the move lands. If that needs `path-map.schema.json`, see W2-58 below.

  It goes into the test designer's brief as text.
- **The migration package, in your return** (DEC-818's six parts): the options of the order above, with your recommendation and confidence, the ACT's patch path, and the output of an entry-for-entry check you run in your scratch. It blocks only the merge, not the work: run the loop to the end, and return PACKAGES with the branch otherwise ready.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-78/`:
  - one case per KPI line, success and failure, plus the key edge cases (STANDARD);
  - **entry for entry:** each record file against the path map's list at the branch's base on `w2/integrate`, order and fields included;
  - **the readers' sweep,** as W2-66's live test-map case does for DEC-891's places. Every test and every module that reads the four lists, or `governance/project/prompts/**` or `governance/project/briefs/**` (W2-62's session-start case among them), is in `record_reading`. A planted new reader missing from it is caught;
  - **the selection:** after an edit of a record file, or of a prompt or a brief, the close's selection stays scoped and runs the record-reading set. An edit of the path map's configuration still runs in full (shared core);
  - a removal from `load_sensitive` selects the ratchet's suites; a planted growing entry without the owner's commit is refused, in a temporary repository built from scratch;
  - **earlier acceptance tests that read the lists** (today W1-01, W2-01, W2-07, W2-53 and W2-57 do; the designer checks): named in the README, never edited. Revising one is outside your paths, so it is a package.
- **The engineer** (fresh, launched sandboxed where its suites allow, `--effort high`) works only in the allowed paths: the five readers in `src/gov/close/`, `governance/project/records/**`, the two lists of `governance/project/test-map.yaml`, new schema files under `template/governance/kernel/schemas/`, and new files `tests/unit/close/test_w2_78*`. It never writes `governance/project/path-map.yaml`.
- **Readers outside your paths, named in your return, never edited:**
  - `src/gov/close/command.py` and the close's pytest plugin (W2-68's and W2-57's paths). If either must change, return PACKAGES;
  - `governance/project/orchestration/nightly/nightly_alone.py` (it reads `accepted_reds` from the path map);
  - the orchestrator's tools that read the lists, under `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/` (`trailer_gate.py`, the queue's gate (e), among them).

  The orchestrator changes them with the ACT.
- **Fail closed:**
  - no entry is lost or changed in the move;
  - no reader is left out of the record-reading set;
  - no growing entry is accepted without the owner's commit;
  - the path map's configuration stays shared core.
- **Running beside you** (paths checked against yours, file by file):
  - **W2-77** (`DAEO-b6hm`) holds `src/gov/close/nightly.py`: no file overlap.
  - **W2-68** (`DAEO-2gc7`, closing) holds `src/gov/close/batch.py`, `fingerprint.py`, `command.py`, `repo.py` and `src/gov/store/**`: no file overlap.
  - **W2-57** (`DAEO-cy5o`) holds `src/gov/close/serial.py`, `command.py` and `tests/unit/close/test_serial*`: no file overlap.
  - **W2-67** (`DAEO-9nys`) holds all of `tests/unit/close/**`, so your `tests/unit/close/test_w2_78*` overlaps it by pattern. Write only new `test_w2_78*` files there, and edit no existing file.
  - **W2-58** (`DAEO-5j8b`, closing) holds `template/governance/kernel/schemas/path-map.schema.json` and `governance/project/path-map.yaml`. Your `template/governance/kernel/schemas/**` covers that schema file. Add new schema files only. An edit of `path-map.schema.json` waits for W2-58's close: return PACKAGES if your design needs one.
  - W2-05 (`DAEO-0z8c`, merge-back) holds `src/gov/**/*.py` for the git environment of git calls, and `src/gov/util/gitenv.py`. Leave how your readers' git calls build their environment as it stands; the later merge takes the conflict.
  - W2-03 holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`. W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`. W2-61 holds `src/gov/retrieval/measure.py`. W2-60a and W2-56 hold `src/gov/launch/**`.

  Do not touch any of these. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite, no full run and no rebuild. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00. Wait for the nightly to end.
  - **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **Never run `gov close`,** the queue or the nightly; the selection is shown by the tests and by `select.py`'s own interface, on a temporary repository or the live test map.
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **No review (STANDARD).**

## This run's order

1. The design note (yours, in scratch).
2. Tests first (the test designer), then **check red yourself.**
3. The engineer.
4. The ACT's patch and the entry-for-entry check (yours, in scratch).
5. Rebuild and verify in full.
6. **Return** PACKAGES with the migration package and the branch ready, or DONE if the register on `w2/integrate` already holds a decision on the migration's order when you return.

**Estimate:** about 150 lines, plus the four record files; about a day with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
