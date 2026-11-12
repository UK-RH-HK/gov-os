# Brief: engineer, DAEO-emq1 (W2-115), FULL, class C3 — the smart close's reds (build run 2, eng-2, iteration 2)

Budget: projection 8 USD. Keep your context short: read only what each red needs; cut long outputs to head and tail.

You are a fresh engineer for ticket DAEO-emq1 (W2-115), in `/home/usain/gov-os-worktrees/W2-115` on `w2/W2-115`
(DEC-963). The smart close is built (head 646f14e0a5e8, four engineer batches); the independent acceptance tests are
merged (13d518369dad). `gov accept W2-115` gives 64 passed, 13 failed; the lead's scoped verify gives 26 failed. You
fix the reds that are this change's, from the failing output only.

## Step 0 and standing rules

Step 0 (the sandbox check) and every standing rule, the writes, the never-read rule for `tests/acceptance/W2-115/**`,
the commands, the commit form and the return are those of the previous engineer's brief, copied beside this one:
`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/eng-1.md` (read it whole; its Interface section is
binding). Do step 0 first and report it first. The previous engineer's return, as its decisions to keep:
`/home/usain/gov-os-worktrees/W2-115/docs/research/W2-115-smart-close.md` and the commits `git log f4f9c3204..HEAD`.
**Every pytest run adds `PYTHONUSERBASE=/home/usain/.local`** to the brief's `env` (under the empty `HOME` pytest is
not found otherwise).

## The failing output

`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/reds-1.txt` (19 cases, each `=== <node id>`, the
message and the traceback's tail). Read only the message and the call shape there; do not open the test files.

## The lead's answers to eng-1's packages (binding)

1. **P1 (a), the batch's entry point (S6, F3):** the batch is driven as W2-68's existing form,
   `python3 -m gov.close.batch run <ticket> <ticket> ... --root <project>`: each candidate is a ticket of the project
   whose work is on its unmerged `w2/<its wbs_id>` branch. In a scoped project, `run` does the isolation (the merged
   result without each candidate, freshly merged onto the base; never a revert), sends only the culprits back, lands
   the rest on the same run, and refuses `BATCH_UNEXPLAINED` or `CANDIDATE_NOT_ISOLATED`; in a strict project (or no
   `close.yaml`) `run` is today's, unchanged (F4). "Land on the same run": the landed tickets' close records name the
   same `commit`; the culprits' are not closed. The close record of a landed ticket lists the culprits in `culprits`.
   Keep `isolate` if you like, as the same code path.
2. **P-TD-1 (a), what a load-sensitive case is (S4):** an entry of the serial phase's own list
   (`gov.close.pytest_plugin.gov_close_serial_only.LIST_REL`, `tests/acceptance/serial-only.txt`) whose comment's kind
   is `latency` (`# serial: latency: <reason>`; 10 such entries exist here). Reading that list is the serial phase's
   own reading and is allowed; the accepted-reds and `load_sensitive` lists (F2) stay unread. **Not** a pytest marker:
   remove `@pytest.mark.load_sensitive` as the source. A load-sensitive red gets 3 rounds alone after its run and 3 on
   the head without the change; others one each way.
3. **Not yours (the lead's packages to the CTO; do not change, do not work around):**
   `tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay` (the overlay now holds
   `close.yaml`, the Interface's file) and the W2-77 cases' exact-key checks of the nightly record (S8's
   `secrets_full_scan`). But keep the nightly record's additions to the fewest, deterministic keys: `secrets_full_scan`
   (true or false), and nothing time-varying (drop `rebuild` timings from the record, or keep only a fixed-shape
   outcome), so that W2-77's "a failed clean-up does not change the verdict" compares equal apart from the key set.
4. **Not yours either:** `test_w2_115_reds.py::test_no_clone_is_built_for_the_nightly_baseline` (the lead sends it to
   the test designer: the warm clone of S10 holds the project's committed `docs/close/nightly/`, which that test misreads
   as a baseline clone). Do not move or hide the warm clone for it.

## The reds that are yours

From reds-1.txt: S2's three (`records alone` selected the own suite, not the `record_reading` one; an unmapped change
is not refused by `--select` or by the close: exit 0, no `SELECTION_REFUSED`), S4's three-rounds case (answer 2), S6's
six and F3's two (answer 1), S8's rebuild (no store under `.gov-runtime/` written between the nightly's start and its
first test: the nightly must rebuild the planted worktree's stores, with `GOV_SECRETS_FULL_SCAN=1`, before its run),
S13's refused selection (`--verify` must exit 2 on it), and your own unit test
`tests/unit/close/test_w2_115_select.py::test_s3_select_prints_the_set_and_options` (its expected options differ on the
lead's machine: make `--select`'s options independent of the caller's environment, or the test's expectation read
from the same function).

## Done

Your unit tests pass; the brief's strict suites still pass (F4); then run outside your sandbox only if it allows:
`gov accept W2-115 --root /home/usain/gov-os-worktrees/W2-115` (with a HOME that keeps the user site, as eng-1 did) and
quote its per-line result. Commit each fix with eng-1.md's commit form. Return as eng-1.md says; `status` DONE when
every red above is green in your runs, else PACKAGES with each open one.
