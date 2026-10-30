You are the ticket lead for ticket `DAEO-03dg` (`W2-80`, "Acceptance tests for the close queue's gates (a) to (h) and its refusal path"), profile STANDARD, a test-design ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-80` on branch `w2/W2-80`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. `git ls-files governance/project/orchestration/tools/` must list `close_queue.sh`, its gate tools (`disk_gate.sh`, `keyword_warn.py`, `net_check.py`, `trailer_gate.py`, `unmeasured_gate.py`, `tree_diff.py`, `skip_gate.py` with `skip_known.json`), `test_close_queue_refusal.sh`, `test_close_queue_gate_d.sh` and `README.md`. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-03dg.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-80");
- the package `governance/project/orchestration/packages/P-TOOLS-REVIEW-1.md`: §2 (the queue's and the gate tools' rows) and §4 (a);
- DEC-941 (item 5), DEC-942 (items 4 and 5, and its "How it is applied" for `close_queue.sh`), DEC-929 (item 3), DEC-868, DEC-899 (item 7), DEC-892, DEC-898, DEC-911, DEC-922, DEC-889 (item 2), DEC-862 and DEC-936 (item 3.1);
- the committed queue, its gate tools, its two scratch tests and the README under `governance/project/orchestration/tools/`;
- the nightly's tests, `governance/project/orchestration/nightly/test_nightly.sh`, for the mutation checks' form and `nightly_cron.sh`'s self-check.

## Why you start now

- **P-TOOLS-REVIEW-1 (a), accepted by the owner (DEC-941 item 5):** commit and test the orchestrator's tools, then an independent auditor's review.
- **The queue decides whether a close starts and what reaches the commit.** Its own faults cost closes this fortnight: T8 (exit 0 after a refusal), S1 (no rebuild first), S2 (a close started under load) and T9 (a collect log too big). The orchestrator's tooling is present in 14 of 18 refused closes.
- **Only the refusal path has a test,** and it runs a line range cut out of the script.
- **The queue changed today** (DEC-942): gate (d) on the tool's exit, `stop_after`, the rebuild under the rebuild lock, `CLOSE-PENDING`, the verification lock and the 20-minute cap on the quiet wait. None of it is tested.

## The decisions for this run

- **Who writes what.**
  - A fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`) writes `tests/acceptance/W2-80/**`: the cases, the stand-ins, and a README that maps each KPI line to its cases and its red reason, states the interface, and lists the mutants. Nothing else.
  - Nobody in this ticket changes the queue or a gate tool. The orchestrator's change turns the red cases green after your merge, as a record commit under `governance/project/orchestration/tools/` (the card).
  - No engineer runs here, and you write no test.
- **The precondition (the orchestrator's, before your launch):** the files named in the check above are committed on `w2/integrate` under `governance/project/orchestration/tools/`, the queue as changed on 2026-10-29, and are in your head. If they are not, return PACKAGES. Never copy them from the main tree's `.gov-runtime/scratch/orchestrator/tools/`.
- **How the cases find the queue:** `governance/project/orchestration/tools/close_queue.sh` of the repository that holds the test file, found from the test file's own location; never an absolute path into the main tree. A missing file or a missing interface fails, naming it; nothing is skipped.
- **No case ever runs the queue against anything real. This is the ticket's first risk.**
  - Today's queue changes into the main tree, takes `/tmp/gov-os-verify.lock` and `/tmp/gov-os-rebuild.lock`, writes `CLOSE-RUNNING` and `CLOSE-PENDING` there, commits a checkpoint, rebuilds and calls the pinned `gov close`. A case that runs it with any value left at its default acts on the real repository.
  - Inside a close, a nightly or a lead's verification, which hold the verification lock, such a case would also wait on that lock for ever.
  - So every case sets every interface value to a temporary one: the repository root, the log, lock and marker paths (both locks, `CLOSE-RUNNING`, `CLOSE-PENDING`, `NIGHTLY-RUNNING`), the tools folder, the pinned gov, the secrets scanner, the load source and the wait lengths.
  - **Before it runs the queue,** each case checks that the committed queue honours every one of them. If one is missing, the case fails naming it, **without running the queue.** That is most cases' red reason today.
  - Stand-ins for `gov`, `gitleaks` and the gate tools come through the interface, in a temporary git repository built from scratch.
- **Today's changes against the ticket's text (DEC-866).** The README states each case's expected state against the committed queue, not against the ticket's description of the old one. Name each difference in your return; it is not a dispute.
  - **Gate (d)** now stops on its tool's own exit (no pipe through `head`). So KPI line 4's "red first for that reason" describes the old queue: its case is red today only for the missing interface.
  - **A stop after the close** now says "STOPPED AFTER THE CLOSE (exit 0), OUTPUTS NOT COMMITTED" for a staging, scan or commit fault (exit 3). KPI line 6's red-first case is likewise red only for the interface.
  - **The quiet window (KPI line 8) is changed by DEC-942 item 4** (closes never starve; if your register lacks DEC-942, this text holds):
    - the queue waits for 5 quiet readings (the 1-minute load below 3, no nightly) for at most 20 readings;
    - it then starts anyway and logs the load it started at;
    - it never starts while the nightly's marker exists.

    Test that. The KPI's "no close starts while the load stands at or above the threshold" is superseded for the load; the nightly clause stands. Name it under DEC-866 in the README and in your return (old: the ticket's KPI line 8; new: DEC-942 item 4), so the orchestrator updates the ticket.
  - **DEC-942's new behaviours, covered too:**
    - `CLOSE-PENDING` is set at the start, and removed when the first close starts and on every exit, a stop included;
    - the verification lock is held from before the quiet wait to the end, and the queue waits while another holder has it;
    - the rebuild runs under the rebuild lock.
- **The rest, as the KPIs state:**
  - a planted fault per gate stops the queue before the close with exit 2, its reason naming the gate and the ticket, the lock removed, `gov close` never called and nothing committed;
  - gate (g) retries six times, then stops, with the waits shortened through the interface;
  - each gate fails closed when its tool is missing, crashes or gives unreadable output;
  - a refused close exits 4, logs CLOSE REFUSED, removes the lock, commits nothing and attempts no later ticket. Every assertion of the committed `test_close_queue_refusal.sh` is covered, and the README maps them;
  - outputs are committed only after a clean close and the skip guard, with their trailers;
  - `gov close` receives gate (b)'s own result and the item's owner decision for that ticket only;
  - the queue refuses to run when it or a gate tool differs from its commit or is untracked.
- **Mutants:** copies of the single committed queue file, changed in a temporary folder (one named file, never a copy of the tree). One per gate's condition, plus the refusal's exit changed to 0 and the skip guard removed. The README lists each mutant and the cases it fails. A mutant no case kills is a named gap, never left silent.
- **Hermetic:** no network; seconds of sleep at most; under 120 s alone; never skipped.
- **Policy 2 (c) here:** this ticket's implementation is the orchestrator's later change to the queue. The test designer reads the queue as committed at your head.

## Your checks (a script file under `.gov-runtime/scratch/lead/`; never `python3 -c` with braces, DEC-409)

- **Before your first run of the cases,** read their interface check (you read everything) and confirm that no case can run a queue lacking the interface, or with a default left in place. If one can, do not run it: return PACKAGES.
- **Around every run of the cases:** a tripwire snapshot before and a compare after. No `CLOSE-RUNNING` or `CLOSE-PENDING` may appear in `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/`, and no new folder under its `log/`. Any change in the main tree or another worktree: stop and return PACKAGES.
- `tests/acceptance/W2-80/` alone, twice: the red set is exactly the README's, each red for its stated reason; no skip (`-rs`); under 120 s.
- `pytest --collect-only -q` over `tests`: no collection error.

## Verification

The full run in the close's form, under the lock, with the retention option and the disk gate first.
- **W2-80's own red cases are red in it by design:** name each with its README reason. Any other red is named with its cause.
- **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), run no suite and no full run. Wait, and go on the moment it is gone. Your full run also waits for the verification lock.
- **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
- **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
- **Never run the queue** (the committed one, or the scratch one) outside the cases' temporary repositories, and never `gov close`.
- **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.

**Running beside you:**
- No running ticket holds `tests/acceptance/W2-80/**`.
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`. W2-61 holds `src/gov/retrieval/measure.py`. W2-03 holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`. W2-05 holds the git-environment lines across `src/gov/**/*.py`, and `src/gov/util/gitenv.py`. W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`. W2-77 holds `src/gov/close/nightly.py`. W2-68 and W2-58 are closing.

Do not touch any of these.

**No review (STANDARD).**

## This run's order

1. The precondition check (above).
2. The test designer.
3. Your checks, the interface check first.
4. Rebuild and verify in full.
5. **Return** DONE or PACKAGES. DONE means the branch is ready to merge; the orchestrator's change to the queue follows, and the ticket closes when it turns the red cases green.

**Estimate:** about 450 lines, about a day with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit). Split the test designer's work into batches that fit: the interface, the stand-ins and the gates first; then the close, the outputs and the quiet window; then the mutants.

---
