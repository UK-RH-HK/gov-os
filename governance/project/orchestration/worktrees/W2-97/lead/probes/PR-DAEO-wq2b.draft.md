---
type: probe
task: DAEO-wq2b
reviewer_session: 6e5ce25a-c4b3-4930-adc9-feeabe38cce0
implementer_session: 85e03894-715f-42f2-a9bd-043bcdc4df71
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: @PROBED@
---

# Probe record: W2-97 (DAEO-wq2b), run 2 (DEC-985, DEC-983)

## Summary

- **What was probed.** Head `@PROBED@` of `w2/W2-97`. Under DEC-985 the review covers only what run 2 changed since `fb9b7e4ce06c` (the orchestrator's merge of `w2/integrate` before the resume):
  - `56180d9f1ab3` (engineer, session `85e03894-715f-42f2-a9bd-043bcdc4df71`, the last implementer). The default run's parallel and serial-only commands each go through `verify_lock.sh`, which takes a heavy-job slot (KPI 1 as DEC-983 changed it, DEC-979 D1). A selection whose scope is not `scoped` stops the run with exit 4 (KPI 3 as DEC-983 changed it). The README and unit tests follow.
  - `4086936fd579` (independent test designer, `Rewrite-Reason: P-W2-97-ENQ-1`): the `enqueue` helper passes `--repo`.
  - `e9ce64e0e6d3` (independent test designer, `Rewrite-Reason: DEC-983`): one case added, `test_a_full_selection_is_never_run`.
  - `37e4f0d92523`: the lead's merge of the tests branch.
  - `287047f23ab8`: the lead's checkpoint record.
- **Who probed.** A fresh read-only reviewer:
  - role `independent-auditor`, session `6e5ce25a-c4b3-4930-adc9-feeabe38cce0`, 2026-11-01, effort max;
  - started through `gov launch` under its OS sandbox, with the reading tools alone;
  - commissioned by the ticket lead for the orchestrator, and judged by the lead under the orchestrator's rules (DEC-137).

  It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries.
  - Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
  - Only "yes" with "fails open" or "loses work" fails the probe.
  - The lead's judgement: none of the findings is both. F1 to F4 are low residuals (consequence "other"); R1 is a Wave 3 row. No round is opened (DEC-802).
- **The lead's correction.** The reviewer's text gave three run-2 commits with wrong 12-digit ids. They are `4086936fd579`, `e9ce64e0e6d3` and `56180d9f1ab3`, as `git log` shows, and are corrected below. Its `probed_commit` is right.

## The reviewer's record

- probed_commit: @PROBED@
- Scope: `git diff fb9b7e4ce06c 287047f23ab8 -- governance/project/orchestration/tools tests/unit/orchestration tests/acceptance/W2-97` (the resume's three changes, DEC-985)
- Reviewer: independent-auditor, a fresh read-only session, 2026-11-01
- **Verdict: pass**
- Classification (DEC-809): 0 fail open, 0 loses work; 4 "other" (ordinary work: yes, all low); 1 row (ordinary work: no). No round.

### Summary

The default run's two test commands now each take a heavy-job slot through `verify_lock.sh`, and that part is sound:
- The parallel run and then the serial-only run each hold a slot for their whole duration and release it between them. With a single slot, the run completed and did not deadlock with itself.
- A wrapper that is missing, waits, or exits 0 or 1 without running never lets the branch advance: the JUnit file decides, not the exit code.

A selection whose scope is anything but `scoped` is never run on any path tried: a batch, the round after a culprit was ejected, a re-merge after the head moved, and five other scope values.

The acceptance revision lowered nothing. It changes one line as DEC-985 allows and adds one case, both by the test designer; the merge brings nothing else.

The findings are about waiting and stopping (F1, F2), a stop message that hides an ejection made in the same run (F3), and a coverage gap that can be closed (F4).

### Method

- Planted repositories in the reviewer's own temp folder: `main` and `w2/integrate`, tickets with `Task:` trailers, enqueued with `--repo` and approved by the CTO.
- For the production default run (no `--test-cmd`): small stand-in `gov.close` modules in the planted `src/` (the serial-only listing and plugin, one serial-only case), so no real suite ran. A `tests/conftest.py` recorded, as each pytest run started and ended, whether slot 1 of the reviewer's own slot folder was held.
- Every run through the real wrapper had `GOV_HEAVY_DIR` inside the reviewer's temp folder, checked before each run; `GOV_HEAVY_SLOTS=1` and `GOV_HEAVY_WORKERS=2`. No real `/tmp/gov-os-heavy-slot-*.lock` and no real suite were touched.
- Wrapper failures: the tool was imported, `SLOT` pointed at a missing path or a fake script, and the tool's own `main` was run.
- Scope paths: stand-in `--test-cmd` (pytest, which can also move the head under test) and `--select-cmd` (answers per ticket and per call).

### Findings

#### F1: low. A run waiting for a heavy-job slot has no time limit and shows nothing while it waits
- **What was done:** every slot of the reviewer's slot folder was held, then `run` was started on a planted repository with one approved ticket.
- **What happened:** the run sat in the wrapper's wait; it was still running after 25 s. Its `queue.txt` and its output said only "merged A onto …", nothing about the wait. The wrapper's line "all 1 slots taken; waiting" reached `run-1.txt` only after the run ended. Meanwhile a second `run` exited 4 at once ("another run holds the queue's lock"). Once the slot was freed, the run went on within 7.1 s and advanced correctly.
- **What should have happened:** the gate is right; what's missing is notice of the wait. The queue should say in its log, when the wait starts, that it is waiting for a slot. It should also have a limit like the leads' 90 minutes (DEC-984), after which it stops with exit 4 and keeps the entries. As it is, a run that starts during the nightly waits silently, holding the queue's lock for the nightly's whole suite time.
- Ordinary work: yes, because a run started during the 04:00 nightly, or while three leads' runs hold the slots, waits like this.
- Consequence: other (a delay with no sign of its cause; nothing advances without a completed run and nothing is lost).

#### F2: low. Stopping a waiting run by its own process id leaves its slot wait behind, and the wait later runs the suite for nobody
- **What was done:** while the run waited as in F1, SIGTERM was sent to the queue's own process only, not its process group.
- **What happened:**
  - The queue died at once (exit −15) without its cleanup, so its clone under `--work` stayed on disk.
  - `heavy_slot.sh` and its `sleep 10` stayed alive.
  - When the slot was freed 8.1 s later, that orphaned wait took the slot and ran the whole parallel run on the leftover clone, a heavy run nobody reads.
  - Nothing advanced and the entry stayed approved. By contrast, stopping the whole process group (as `timeout` did in R1) left nothing behind.
- **What should have happened:** stopping the run also ends its wait, and its clone is removed.
- Ordinary work: yes, because stopping a run that sits waiting for the nightly with `kill <pid>` reaches only the queue's own process.
- Consequence: other (a slot and the machine's load taken for nothing, and a stale clone on disk; nothing is lost or advanced).

#### F3: low. Exit 4 says "entries kept" even when the same run has already ejected a ticket
- **What was done:** a batch of A and B. A adds a failing test; B's second selection answers `full`.
- **What happened:** A was correctly found as the culprit and ejected (`ejected/A.json`, and "EJECTED A" in `queue.txt`). The next round for B stopped. The run exited 4 with stderr "stopped: the selection for B answered scope 'full' …; entries kept". Neither the exit code nor stderr mentions A's ejection; exit 3 is lost to exit 4.
- **What should have happened:** the stop's message, or the exit code, says that this run ejected a ticket. Alternatively, the README says that exit 4 can follow ejections and where to find them.
- Ordinary work: yes, because any stop in a later round gives this (a refused selection, a failed prepare command, a head that moved three times). Run 2's `full` check adds one more path, which today only a stand-in selection can reach.
- Consequence: other (the ejection is on disk and nothing is lost; the ejected ticket's lead may learn of it late).

#### F4: low. KPI 1's heavy-job slot has no acceptance case, though one could be built
- **What was done:** the acceptance suite was read for KPI 1's slot clause, then the default run was driven through the real wrapper (P1).
- **What happened:** the slot is checked only by the engineer's unit case, which records the command lines through a fake `sh`. The acceptance README says the slot cannot be observed without reaching the machine's own slots and suites. But the wrapper honours `GOV_HEAVY_DIR`, and stand-in `gov.close` modules in a planted `src/` keep the run off any real suite. P1 observed the slot end to end that way in 3.9 s.
- **What should have happened:** an independent acceptance case for the slot (it would depend on the wrapper existing on this machine), or the README stating the gap as a choice rather than an impossibility.
- Ordinary work: yes, because a later change to how the slot is called would be caught only by the implementer's own unit case.
- Consequence: other (coverage; nothing fails open today, since P1, P3 and P5 show the slot path is right and fails closed).

#### R1: row for the Wave 3 hardening pass. A queue run started inside `verify_lock.sh` deadlocks with itself when slots are short
- **What was done:** the whole `run` was started inside the real wrapper, with one slot in the reviewer's folder.
- **What happened:** the outer wrapper held the only slot, and the run's own parallel run waited for it until `timeout` ended everything after 30 s (exit 124). Nothing advanced, the entry was kept, and no process was left.
- With the production size of 3 slots, such a run needs two slots. If the nightly holds the other two, or is waiting for them (DEC-984 takes them one at a time, waiting for each until its latest start), the two wait for each other until that deadline.
- **What should have happened:** the queue refuses to run inside a slot, or its README says never to run it inside one.
- Ordinary work: no, because no brief or README tells anyone to run the queue inside `verify_lock.sh`, and the tools README says the queue takes the slots itself.
- Consequence: other (a hang until the nightly's deadline or a stop; nothing advances or is lost).

### What was probed and found sound

1. **No self-deadlock (P1, one slot).** The parallel run held the slot from start to end. The serial-only run took it again after release. The alone re-run ran with the slot free. `-n auto` ran 2 workers, the wrapper's cap. The run exited 0 and advanced to the merge it tested; the record counts both JUnit files (4 tests, 1 failure, the flaky case named).
2. **All slots held (P2).** The run waited, nothing advanced and the entry stayed approved; a second run exited 4 at once. When the slot was freed, the run continued and advanced to the tested merge.
3. **Wrapper failures (P3, P5, P5c).** A missing wrapper, or one that exits 0 or 1 without running, gave exit 4 ("the test run did not complete"): the head unmoved, nothing ejected, the entry kept.
4. **A wrapper hiding a red as 0 (P5b).** The JUnit failure still counted: the test was red alone, so the ticket was ejected (exit 3) and the head stayed.
5. **Exit codes (read).** The wrapper's own failure codes (`flock`'s 64–73, `bash`'s 126 and 127) are never 0, 1 or 5, so the queue cannot take a wrapper failure for a completed run. The one ambiguous code is the wrapper's "busy" code 213: a command exiting 213 would be re-run in the next slot. Pytest never returns 213.
6. **A selection that is not scoped is never run.** Covered on every path tried: P8a, a batch whose second ticket answers `full`; P8b, the round after a culprit's ejection; P8c, a re-merge after the head moved under test. Each gave exit 4 with the reason ("the full suite runs only in the nightly"), no test call after the answer, nothing advanced, and the entries kept, apart from the culprit's ejection for its own red in P8b. The trace without the batch and the culprit search use no selection, only the JUnit's test ids.
7. **Other scope values (P8d).** `refused`, `Scoped`, `scoped ` (trailing space), null and `none` each gave exit 4, with no test call and the entry kept.
8. **No lock cycle with the nightly (read).** The queue holds no slot while waiting for one (P1, P2). It holds the rebuild lock only during a rebuild, which takes no slot. So the nightly holding all three slots (DEC-984) makes the queue wait, not deadlock.
9. **No suite reaches the real wrapper.** Every unit and acceptance run passes a non-empty `--test-cmd`, and the slot's unit case records `sh`. So the nightly, holding all three slots while its suites run, cannot hang on these suites.
10. **The acceptance revision lowered nothing.** `4086936fd579` adds `--repo` to the enqueue helper: one line, `Rewrite-Reason: P-W2-97-ENQ-1`; the short-id case still asserts the full id. `e9ce64e0e6d3` adds `test_a_full_selection_is_never_run` and a `full` option to the selection stand-in, whose default output is unchanged (`Rewrite-Reason: DEC-983`). Both carry `Role: independent-test-designer`. No assertion was removed or weakened, and the KPI table's rows keep all their tests. The merge `37e4f0d92523` has an empty combined diff and brings only those two commits. The engineer's `56180d9f1ab3` touches only the tool, its README and the unit tests.
11. **The README matches the code:** the two slot commands; the alone re-runs and traces taking no slot; a stand-in run as given; a missing wrapper being "a run that did not complete"; exit 4 for a selection that is not scoped.

### Not reproduced or not run

- The real `select_tests.py`, the rebuild, the three real slots and any real suite were not run; they were read only, as the brief requires.
- The wrapper's busy-code collision (213) was read, not run.
