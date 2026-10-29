## The lead's amendment E to the design note (fold it in first, as section 11's point E, and change sections 3 and 6 to match)

**E. The batch drives the whole batch, its closes included.** The acceptance tests read DEC-883 item 1 ("queued closes on one integrated head ... then each ticket's own checks, one after another") as one command that closes the tickets, and that is the better reading of a merge queue. So `python3 -m gov.close.batch run <ticket> [<ticket> ...] --root <project> --json` does, after steps 1 to 7 of section 3:

8. **Commits the run record** (the batch's record under `docs/close/nightly/`, a record-only path) in a commit that names no task: trailers `Role: <the caller's GOV_ROLE, else orchestrator>`, `Implements: DEC-883`, `Co-Authored-By` as the caller's environment gives none (no Co-Authored-By when none is known). A red run's record is committed too, and the batch ends there (exit 3): nothing closes on a red run.
9. **Closes each ticket, one after another, in the order given:**
   - before each close, makes the store fresh at HEAD: the incremental record load where the store's code fingerprint equals HEAD's; else (a fingerprint that cannot be computed) a full rebuild at HEAD;
   - runs `gov close <ticket>` in-process (the close's own code path, with `--check-result` set to the batch's check result), which reuses the batch's run by section 4 and so runs only its own checks;
   - commits the close's outputs as the orchestrator's queue does today (the ticket file, `docs/close/<ticket>/`, `docs/checkpoints/<ticket>/`; trailers `Task: <ticket>`, `Implements: DEC-883`, `Role: <as above>`), so the next close finds a clean tree;
   - **a refused close ends the batch** (as the owner's queue rule of 2026-10-27: a refusal ends the queue with a non-zero status): the closes before it stand, the tickets after it are not closed, the envelope names the refusal (its code and its findings), exit 3. What the refused close left (its repair ticket) is left in the tree, uncommitted.
10. **The envelope:** the run record, each ticket's close (its record path, or its refusal), and the store loads made.

**A fingerprint that cannot be computed** (no test map, an invalid one): the batch still runs (steps 2 to 7, its record stating the fingerprints as null), and each close then runs fresh: no reuse, its own `gov check`, a full rebuild before it. This replaces step 1's `FINGERPRINT_UNKNOWN` refusal.

**A record that names no JUnit XML file** (an empty `junit_xml`) is never reused (condition 4): W2-66's planted green nights name none.

**Residuals (section 9):** the orchestrator's queue keeps its own gates around a batch (the keyword warning, the collection, the network check, the gitleaks scan of the staged outputs, the skip guard reading the reused skip count); the batch does not run gitleaks on what it commits.
