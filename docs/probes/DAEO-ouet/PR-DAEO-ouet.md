---
type: probe
task: DAEO-ouet
reviewer_session: cef1ac98-daa4-4f57-b407-8be31bccb127
implementer_session: aaade71a-d60f-45cd-9aea-6b49f21ab6b2
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 90122df096e7bb40c1890485b64a5638e335922f
---

# Probe record: W2-96 (DAEO-ouet) `gov accept`, reviews 3, 4 and 5 (run 2's round and the owner's third review, DEC-987)

## The lead's judgement

- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, session `cef1ac98-daa4-4f57-b407-8be31bccb127`, 2026-11-01, effort max, started through `gov launch` under its OS sandbox with the reading tools alone. It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in any tree.
- **What was probed.** Head `90122df096e7` of `w2/W2-96`. This review judged only what changed since review 4's head `0e0883b80397`, as the owner decided (DEC-987, the owner's exception to DEC-916 for this ticket): the engineer's `44dbc90ee340` (session `aaade71a-d60f-45cd-9aea-6b49f21ab6b2`, the last implementer: `gov accept` becomes a subreaper and stops and reaps every process of the run, whatever its session, before its clean-up) and the independent test designers' R16 cases `4b9353954f88` and the one-constant rename `d19019ca483e` (a gitleaks false positive that turned `secrets-indexing` red; `Rewrite-Reason` in that commit), with the lead's merges `9d2d27e2b5bd` and `d86588d52809` and checkpoint records. A first launch of this review on `c9daee7c9ce8`, before the rename, was stopped by the lead before it returned anything, so that the review judges the final head.
- **Review 3** (session `2ddd0f47-0cc9-4858-a7bd-17c976e23674`, head `382e6d8fba8c`, run 2's first) failed on V1 (yes / fails open: the clean-up's removal stopped at the first entry an own-session process had removed, giving `crash` and test-named leftovers). R14 (a tolerant removal) and R15 (linear in its entries) fixed it, with review 3's cases. Its record is kept as a draft, not committed (DEC-733).
- **Review 4** (session `6051140e-4d52-4a9e-9697-9c3eadf24f57`, head `0e0883b80397`, run 2's second and last, DEC-916) confirmed V1 fixed and failed on W1 (yes / fails open: after a stop of `gov` alone, an own-session nested run outlived it and recreated test-named folders in the caller's TMPDIR); W2 and W3 are Wave 3 rows. The owner chose P-W2-96-R4 (a) (DEC-987): the two cases first, then the subreaper fix (R16), then this third review of that change alone. Its record is kept as a draft, not committed (DEC-733).
- **Judged by the threat model (DEC-801, DEC-808).** Only "yes" with "fails open" or "loses work" fails a probe. W1 is fixed: it did not reproduce in 33 stops during a nested pytest, and the positive control (the subreaper switched off) saw it in 3 of 3. X1 is "yes / other": it fails closed (a test that judges an ended orphan by a pid probe sees `gov`'s held zombie and fails under `gov accept` where pytest passes); it is a residual returned to the orchestrator with the reviewer's optional package PKG-R5-X1, not a round. X2 is a row for the Wave 3 hardening pass.
- **Judgement: pass.**

## The reviewer's record

## Probe record: W2-96 (DAEO-ouet) `gov accept`, review 5 (the third review, of the subreaper change alone; DEC-987)

probed_commit: 90122df096e7bb40c1890485b64a5638e335922f

**Scope.** Only what changed since review 4's head 0e0883b80397:
- the engineer's 44dbc90ee340: R16, with `gov` becoming a subreaper and stopping and reaping every process of the run before its clean-up;
- the test designer's 4b9353954f88 (R16's two cases and their premise), merged in 9d2d27e2b5bd;
- the test designer's d19019ca483e (one constant of the R16 support renamed), merged in d86588d52809;
- `w2/integrate` merged in 943543cea0e8, which touches nothing under `src/gov/accept/`;
- the lead's checkpoints c9daee7c9ce8 and 90122df096e7.

**Method.** Read-only.
- **Planted runs:** 100 CLI runs of `gov` at the head, built from scratch in the reviewer's TMPDIR. 63 of them have a nested `gov accept` in a session of its own, W2-96's harness form.
- **Tracing:** each run's processes carry a marker in their environment and are found by it.
- **Signals:** sent from outside to the outer `gov` alone, timed by the nested test's own record or at random.
- **Two looks:** the given TMPDIR and live processes were checked when `gov` ended, and again 4.0–30.5 s later, once the nested sleep or the orphan's write would have happened.
- **Positive control:** 9 runs with the subreaper made unavailable (the runner's own fall-back).
- **Not ordinary:** 7 in-process calls, used only to read the setting.
- **Comparison:** 16 plain pytest runs.

### Probed and found sound

- **R16, W1 again and wider.** There were 41 stops to the outer `gov` alone, 33 of them while the nested pytest (in a session of its own) was running.
  - Stop forms:
    - SIGTERM, Ctrl-C once and twice, and SIGHUP;
    - coreutils `timeout`, with and without `--preserve-status`.
  - Moments:
    - when the nested test began;
    - at random between 0.3 and 6 s;
    - while the nested test slept or wrote;
    - aimed at its end, during teardown and report writing.
  - Every stop ended by an ordinary exit: 143, 130 or 129, or 124 from `timeout` itself. A single signal ended `gov` within 0.02–0.07 s.
  - When `gov` ended, and again at the later look, the given TMPDIR was empty and no process of the run was alive, in every run.
  - W1 did not reproduce in any of the 33 stops during a nested pytest. The positive control saw it in 3 of 3: processes of the run alive when `gov` ended, then 6–8 entries later, holding the outer test's folder name and, in one run, a file of test-written content.
  - The nested `gov` given the outer child's own TMPDIR left nothing in 3 of 3; review 4 had seen 2 entries in this form.
- **Runs left going, with no stop.** These were processes outside the child's group:
  - a nested run left going (6 runs);
  - a daemon-style double fork (3);
  - a writer that recreates its folders (2);
  - a forking loop (2);
  - a 300-child breeder (1);
  - a fork-and-exit chain with 5 ms pauses (1) and with none (2).

  The results came back as the tests gave them, 0 or 3. Nothing was alive after `gov` ended and nothing appeared later. Descendants that ignore all three stop signals, or that stopped themselves, were ended at once.
- **The main child's status is never taken by reaping.** Each of these runs also had a process in a session of its own:
  - a failure gave 3;
  - a pass gave 0;
  - pytest killed by a signal gave 4 `crash`;
  - a collection error whose conftest started a process gave 4 `collection`;
  - `--timeout 4` gave 4 `timeout`.

  In-process, the results were the same, and a child the caller had before the run, already ended, kept its exit status for the caller.
- **Nothing outside the run is touched.**
  - Two `gov accept` runs at once, one of them stopped: the other's processes, its nested `gov` and nested pytest included, ran on. It passed with exit 0, and its nested `gov` exited 0 (3 of 3).
  - Three siblings were all alive after both runs ended (3 of 3): one in a session of its own, one in the caller's group, and one started during the run.
  - `gov`'s parent, the harness, was unharmed.
- **The setting does not leak.**
  - In-process, it read 0 before and after a pass, a failure, a crash, a timeout, a run with an orphan, and a SIGTERM stop. A caller that was already a subreaper stayed one.
  - The setting belongs to one process and is not inherited by children, so the caller is never affected.
- **R9, R12 and R15, spot checks in the changed path.**
  - R9 and R12: Ctrl-C every 10 ms from the clean-up's start, with 300 processes to reap or 60,000 files to remove, was held; `gov` then exited 130 with nothing left (3 of 3).
  - R15: 8,000 sibling folders took 0.17–0.56 s from the folders' making to `gov`'s end, against 0.10 s for a plain recursive removal.
  - R14: the removal itself is unchanged.
- **No leak, no write.**
  - No marker or pytest word reached stdout or stderr in any run, and stderr was empty.
  - No planted project changed. Two planted repositories had the same `git status --porcelain --ignored` before and after.
  - The worktree's status and head were unchanged.
- **The cases.**
  - 4b9353954f88 tests R16 as stated:
    - a SIGTERM to `gov` alone while the nested test sleeps, which must give 143;
    - a passing run that leaves its nested run going, which must give the full pass result.

    Each case requires no process of the run alive when `gov` ends, with no grace, and the given TMPDIR empty then and again after the nested sleep plus 4 s.
  - It adds lines only: no earlier case changed. The README adds rows and widens the premises row.
  - It covers a pass and SIGTERM. Failures, errors, SIGINT and SIGHUP are left to the builder tests, and they were probed here.
  - d19019ca483e renames one constant in 4 lines and leaves its value unchanged.
- **`gov accept DAEO-ouet --json`.**
  - Exit 0 in 138.5 s; `outcome: pass`.
  - Passed per line: success 1–5 are 14/22/23/11/36; failure 1–4 are 18/23/11/31.
  - `unmapped` 23 passed; `totals` 109 passed.
  - stderr was empty. The given TMPDIR peaked at 27,616 entries and was empty afterwards. No process was left.
- **The fall-back is as the engineer states it.** Without the subreaper, `gov` keeps the old behaviour, and W1 comes back, silently.

### Findings

**X1. While the run goes on, `gov` holds every orphan of the run that has ended as a zombie, until its clean-up. A test that judges such a process by its pid sees it as still there, so `gov accept` reports a correct implementation's passing case as failing.**
- **Done.** Two kinds of planted test, run under plain pytest, under `gov accept`'s fall-back without the subreaper, and under `gov accept` at the head:
  - W1-02's deadline form. A program forks its work into a session of its own. At a deadline it kills that group and waits only for the leader, as the kernel's PreToolUse hook does (DEC-580). The test then waits up to 5 s for the processes the work started to be gone, counting each as alive while a signal-0 probe of its pid succeeds, as W1-02's acceptance support does.
  - A daemon from a double fork that ends after 0.3 s, checked the same way.
- **Happened.**
  - Under plain pytest and under the fall-back, every one passed: W1-02's form in 4 of 4 and 2 of 2, the daemon in 6 of 6 and 2 of 2.
  - Under `gov accept` at the head, every one failed with exit 3: W1-02's form in 2 of 2, the daemon in 4 of 4. The orphans had ended but had become `gov`'s zombies, which a pid probe still finds.
- **Should have happened.** The tests' outcomes under `gov accept` match pytest's. `gov` should reap each process of the run that ends while the run goes on (never the main child, never one still running), and keep its stop-and-reap before the clean-up.
- **Where it applies.** W1-02's case that nothing the hook started is left running has this form; it was not run here (DEC-959 item 1). The other process checks in this tree (W2-96's, W1-30's, W2-54's, and the close's builder test) count a zombie as gone and are unaffected.
- **Severity: low to medium.** It gives a false failure only, never a false pass, in the form this tree has. The engineer sees only a failing line and cannot learn why, while the lead's pytest run passes.
- Ordinary work: yes, because orphans that end come from ordinary code under test (a program that kills a group and waits only for its leader, a daemon, a background job), and a pid probe is the usual check; the form exists in W1-02's acceptance tests, with no deliberate construction.
- Consequence: other (it fails closed).

**X2 (row). The same held zombie turns a failing "it still runs" check on an orphan into a pass with exit 0.**
- **Done.** A planted daemon that ends after 0.3 s; after 1.5 s the test asserts, by a pid probe, that the daemon still runs.
- **Happened.** Plain pytest failed in 6 of 6 and the fall-back failed with exit 3 in 2 of 2. `gov accept` at the head passed with exit 0 in 4 of 4.
- **Should have happened.** A failure, as under pytest.
- **Severity: low,** since there is no instance in this tree.
- Ordinary work: no, because it needs an acceptance test that asserts by a pid probe alone that a detached process still runs, and no acceptance test in this tree does (the one check of a started daemon, W2-54's, reads the process's command line and its zombie state); the change that closes X1 closes this too.
- Consequence: fails open (if hit). A failing case would be hidden behind exit 0, though the lead's pytest run would still show it.

Classification: 0 yes / fails open or loses work; 1 yes / other (X1); 1 row for Wave 3 (X2).

### Verdict

**Pass.** R16 holds as stated in every path probed: a pass, a failure, an error, and a stop by SIGINT, SIGTERM, SIGHUP or coreutils `timeout`, at any moment of a nested run. No process of the run outlives `gov`, and nothing appears in the caller's TMPDIR afterwards. Exit codes, the envelope, R9, R12 and R15 are unchanged, and nothing from the child is printed. No finding is both "yes" and "fails open" or "loses work". X1 is a side effect of the change that fails closed; X2 is its fail-open form, with no instance in this tree.
