session: cef1ac98-daa4-4f57-b407-8be31bccb127 is_error: False turns: 120 duration_ms: 2745392
Since my start, only the guard's runtime file `.gov-runtime/secrets-clean.json`, the lead's own log `parallel5.out` and the top folder's timestamp (the sandbox's placeholders) changed. Nothing is mine. All probing is complete; here is the return.

**Step 0 (sandbox check):**
- **(a)** The write outside the worktree failed with `OSError: [Errno 30] Read-only file system`. No file was written.
- **(b)** `echo sandbox-trial | git hash-object -w --stdin` printed 1ae28402a109… and exited 0. `git update-index --refresh` exited 0.
- **Identity:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-ouet`. Top `/home/usain/gov-os-worktrees/W2-96`, branch `w2/W2-96`, head 90122df096e7.
- **Code under test:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-96/src/gov/__init__.py`.

task: Review 5 (FULL, read-only; the third review, DEC-987) of W2-96 (DAEO-ouet) `gov accept` at head 90122df096e7. I judged only the subreaper change (44dbc90ee340) and the two R16 cases (4b9353954f88, renamed in d19019ca483e), against KPI 2 and the two judgement questions.

status: DONE. The probe passes. R16 held in every path probed and W1 did not reproduce on this head. One side effect of the change was found (X1, "yes / other": fails closed), plus its fail-open form as a Wave 3 row (X2). No finding is both "yes" and "fails open" or "loses work".

work_completed:
- **Read:**
  - the ticket, with its KPIs and allowed paths;
  - DEC-987, DEC-916, DEC-959 (items 6 and 7), DEC-957, DEC-820 and DEC-317;
  - review 4's draft record and full return;
  - `design.md` and `design-r1.md` to `design-r3.md`;
  - the engineer's diff and its 14 builder tests;
  - the whole runner as it now stands;
  - the cases commit (test file, support additions, README);
  - the rename commit.
- **Ran `gov accept DAEO-ouet --json` once, first,** with a given TMPDIR of my own.
- **Planted runs, built from scratch in my TMPDIR:**
  - 100 CLI runs of `gov` at the head, 2 of them invalid through my own harness error. 63 of them have a nested `gov accept` in a session of its own (W2-96's harness form).
  - 41 stops sent to the outer `gov` alone, 33 of them while a nested pytest was running.
  - 9 positive-control runs, with the subreaper made unavailable by a shim that makes `import ctypes` fail on the outer `gov`'s path (the runner's own fall-back).
  - 16 plain pytest runs for comparison.
  - 7 in-process calls (not ordinary) to check the subreaper setting.
- **Tracing:** every run's processes carry a marker in their environment and are found by it. This Bash call's PID namespace held nothing else.
- **Checked in every run:**
  - the exit code and the envelope;
  - stdout and stderr;
  - the given TMPDIR when `gov` ended and again 4.0–30.5 s later;
  - live processes at both looks;
  - the planted project's tree, and `git status --porcelain --ignored` for 2 planted repositories.

files_changed: none in the repository. The head is unchanged (90122df096e7). The worktree's `git status --porcelain --ignored` showed 143 lines before and after. No bytecode file under `src/` or `tests/` is newer than my first script. Since my start, only the guard's `.gov-runtime/secrets-clean.json`, the lead's `parallel5.out` and the top folder's timestamp changed; none of them is mine.

evidence:
- **Commits probed:**
  - 44dbc90ee340 (`Task: DAEO-ouet`, `Role: engineer`, `Implements: DEC-987, DEC-959, DEC-317`): `src/gov/accept/runner.py` +62/−4 and `tests/unit/accept/test_w2_96_review4.py` (new). Both are in `allowed_paths`.
  - 4b9353954f88 (`Role: independent-test-designer`, `Implements: DEC-987, DEC-959`), merged in 9d2d27e2b5bd (`Role: orchestrator`).
  - d19019ca483e (`Role: independent-test-designer`, `Implements: DEC-987, DEC-911`, `Rewrite-Reason` present), merged in d86588d52809.
- **DAEO-ouet run** (`r5/logs/daeo-summary.json`, `daeo-out.json`):
  - exit 0 in 138.5 s, `outcome: pass`;
  - passed per line: success 1–5 are 14/22/23/11/36, failure 1–4 are 18/23/11/31;
  - `unmapped` 23 passed; `totals` 109 passed;
  - stderr 0 bytes, no leak word in the envelope;
  - the given TMPDIR peaked at 27,616 entries and was empty at the end and 5 s later;
  - no process was left in the namespace.
- **Head runs** (`r5/logs/*.jsonl`, tallied by `r5/scripts/tally.py`):
  - In all 98 valid runs: the given TMPDIR was empty when `gov` ended and at the later look; no process of the run was alive at either look; no leak; stderr empty; no project changed.
  - Exit codes: 143 ×14, 130 ×12, 129 ×7, 124 ×2 (coreutils `timeout` without `--preserve-status`), 0 ×41, 3 ×10, 4 ×3. The storm and concurrent runs add 130 ×3, 143 ×3 and 0 ×3.
- **Positive control** (`control_shim`): W1 came back in 3 of 3.
  - 1–2 processes of the run were alive when `gov` ended.
  - 6–8 entries appeared later, such as `gov-accept-…/tmp/pytest-of-usain/pytest-0/test_rv5mark_outer0/rv5mark-given-1`.
  - One run left a file of test-written content.
- **X1 and X2** (`zombie`, `compare_head`, `compare_shim`), summarised in the table:

  | Planted test | Plain pytest | `gov accept`, fall-back | `gov accept`, head |
  |---|---|---|---|
  | W1-02's form | pass 4/4 | pass 2/2 | fail, exit 3, 2/2 |
  | "has the daemon ended" | pass 6/6 | pass 2/2 | fail, exit 3, 4/4 |
  | "does the daemon still run" | fail 6/6 | fail, exit 3, 2/2 | pass, exit 0, 4/4 |

tests: no suite was re-run (DEC-959 item 1). I ran `gov accept DAEO-ouet --json` once: 109 passed, exit 0. Besides that, only my own probe runs, as counted above.

discoveries:
- **X1 (held zombies).** As a subreaper, `gov` takes in every orphan of the run but reaps nothing until its clean-up. A pid probe from a test therefore sees an ended orphan as still present.
  - The kernel's own PreToolUse hook (`template/governance/kernel/hooks/pretooluse.py`, DEC-580) creates such orphans at its deadline: it kills its decision's group and waits only for the decision.
  - W1-02's acceptance support judges those processes by a signal-0 probe.
  - The other process checks found (W2-96's, W1-30's, W2-54's, and the close's builder test) count a zombie as gone and are unaffected.
- **The engineer's stated risk did not appear:** a fork-and-exit chain with no pause was caught 2 of 2. A process spends almost all its life inside fork, where SIGKILL ends it.
- **By R16's design:** a daemon a test starts (for example the embedder that retrieval leaves running) no longer outlives `gov accept`.
- **Nit:** the change dropped a space after `=` on the `FOLDER` line. It is cosmetic.

risks:
- **My probe folders stay**, since `rm` is refused and was not tried. They are under `/tmp/gov-os-lead-W2-96/gov-launch-independent-auditor-t9q011f1/claude-1000/r5/`:
  - `runs/`, with 17 batch folders;
  - `scripts/`, `logs/`, `shim/`, and the empty `daeo-tmp/`.

  What stays in them:
  - planted projects and probe records;
  - the W1 chains in `runs/control_shim/{1,2,3}/given`;
  - plain pytest's own leftovers in the plain-run folders.

  The TMPDIR now holds 15 MB and 3,428 files and folders (`r5`: 3,420).
- **My share was exceeded once,** by my own choice of probe. The R9 storm run whose planted test makes 60,000 files held about 63,000 entries for about a second. The DAEO-ouet run's peak was about 27,630.
- **Not probed:**
  - a kernel without the per-thread children file (there `_reap` would see nothing and `gov` would silently keep the old behaviour; this WSL2 kernel has the file);
  - in-process callers with other threads;
  - the signal window right after the subreaper call.
- **Bound not reached:** the 5 s bound against a process SIGKILL cannot end at once (EPERM, or uninterruptible sleep) cannot be produced in this sandbox. It is judged by reading the code and by the engineer's unit test.
- **W1-02's real case** was not run (DEC-959 item 1). Its form was reproduced in a planted test.

lessons:
- Plant with the real HOME: pytest lives in the user site, and a planted HOME turns every run into `crash`.
- A positive control (the subreaper switched off by a shim on the outer `gov`'s path) proves that the harness would see W1.
- When the runner is a subreaper, check whether pid-judging helpers count a zombie as gone.
- Keep planted file counts well under the share.

proposed_decisions:
- **PKG-R5-X1 (optional, it proposes no round).**
  - Classification: 0 yes / fails open or loses work; 1 yes / other (X1); 1 row for Wave 3 (X2).
  - **(a) Apply now:** while it waits, `gov` reaps each process of the run that has ended, never the main child and never one still running. Its stop-and-reap before the clean-up stays. About 10 lines and one case (W1-02's form gives the same result under `gov accept` as under pytest). It would need a review the owner grants, or it rides along with any later resume (DEC-802).
  - **(b) Defer:** X1 and X2 become Wave 3 rows. A line goes into the test-design skill: a process counts as gone once it is a zombie, as W2-96, W1-30 and W2-54 already count it. W1-02's check is made zombie-aware when W1-02 is next touched.
  - **(c) Re-baseline:** R16 states that orphans of the run are held until the clean-up, and that tests must count a zombie as gone.
  - **Recommendation: (b), confidence medium.** X1 fails closed, and in the form this tree has it never hides a failure. Choose (a) if the owner wants `gov accept`'s outcomes to equal pytest's for every test form before W2-96 closes.

unresolved:
- Whether W1-02's real case flips under `gov accept`: predicted by its form, not run.
- The owner may weigh X2's "ordinary work" differently from my "no".

recommended_next_action: The lead commits this record (pass), runs the scoped set, and records X1 and X2 as rows, or takes PKG-R5-X1 to the owner if X1 should be fixed before the close.

---

# Probe record: W2-96 (DAEO-ouet) `gov accept`, review 5 (the third review, of the subreaper change alone; DEC-987)

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

## Probed and found sound

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

## Findings

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

## Verdict

**Pass.** R16 holds as stated in every path probed: a pass, a failure, an error, and a stop by SIGINT, SIGTERM, SIGHUP or coreutils `timeout`, at any moment of a nested run. No process of the run outlives `gov`, and nothing appears in the caller's TMPDIR afterwards. Exit codes, the envelope, R9, R12 and R15 are unchanged, and nothing from the child is printed. No finding is both "yes" and "fails open" or "loses work". X1 is a side effect of the change that fails closed; X2 is its fail-open form, with no instance in this tree.

brief_gaps:
- The brief expects "a sane result (108 cases)". The folder has 109: 106 earlier cases, the two R16 cases and their premise. This matches the engineer's and the lead's runs.
- The brief asks whether reaping takes the main child's status; it does not. It does not say whether outcomes changed by the runner's own environment (X1, X2) count as "a failing test hidden behind exit 0". I judged X2 by the test forms present in this tree; the owner may weigh it otherwise.
- `rm` is refused and was not tried. My folders are listed under risks.

Guard refusals met:
- Read refusals (DEC-849): 0.
- Other refusals: 1, at about 05:43 UTC. An inline `python3 -c` that opened W2-96's support file for reading was refused by the PreToolUse hook as "a command that may write the acceptance tests, which only the independent test designer writes (DEC-953 item 2)". It was not retried. The same lines were then read with the Grep tool.
