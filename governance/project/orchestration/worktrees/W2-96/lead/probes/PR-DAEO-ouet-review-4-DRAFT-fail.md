# Probe record: W2-96 (DAEO-ouet) `gov accept`, review 4 (run 2, the round's last, DEC-916)

probed_commit: 0e0883b80397f351b5a67c0ce77377ee5705b5ff

**Scope.** This probes what changed since review 3's head 382e6d8fba8c:
- the engineer's b3dd46f82321;
- the test designer's 588e43ae11ff and c348af6bc9ae, merged in a1d14a3f37e1;
- `w2/integrate` merged in 064c69f8b785, which touches nothing under `src/gov/accept/`;
- the lead's checkpoint 0e0883b80397.

**Method.** Read-only. 165 planted runs were built from scratch in the reviewer's TMPDIR, 82 of them with a nested `gov accept` in a session of its own (W2-96's harness form). Signals were sent from outside, timed by disk state or `/proc`. The given TMPDIR was checked when `gov` ended and again once the test's processes had ended.

## Probed and found sound

- **R14, V1 again and wider.** 76 stopped nested runs all ended by an ordinary exit 143, 130 or 129, never `crash`, and the marker never reached stdout or stderr.
  - Stop forms tried:
    - SIGTERM, Ctrl-C once and twice, and SIGHUP;
    - coreutils `timeout`;
    - to `gov` alone, to both govs at once, and to the whole process tree at once.
  - Moments tried:
    - at the nested removal's first sign;
    - 0.07–0.32 s after the nested pytest ended;
    - at random;
    - while the nested test slept or wrote.
  - When `gov` ended, nothing of its run was in the given TMPDIR in 75 of 76. The 76th already held W1's rebuilt chain.
  - Review 3's head failed 7 of 23 such stops.
- **Processes outside the child's group, no stop.** Writers in sessions of their own never turned a run into `crash`. The results came back as the tests gave them, 0 or 3, in 22 runs. Forms tried:
  - writing;
  - adding folders;
  - removing entries, racing the clean-up;
  - a daemon-style double fork.

  A remover, and writers that stop when their folder is gone, left nothing (8 of 8).
- **The `..` check.** A folder holding 30,000 files, or its parent, was moved while the removal was inside it (16 runs). Targets: higher inside the private folder, the given TMPDIR, the planted project, and an outside folder.
  - The removal never left the moved folder. No entry of any target was removed or changed, including the 102 planted files there whose names collide with the moved folder's own entries.
  - Moves inside the private folder left nothing.
  - The moved folder's own content, which came from the private folder, was emptied, and the folder was left where the mover put it.
  - With review 3's removal put back (comparison only), the same move emptied the whole outside folder: the check closes a real escape.
- **Links and permissions.** Every link was removed, never followed. The outside folder, the project and `/` were unchanged, contents and permissions alike. This held for a pass, a fail, SIGTERM and Ctrl-C. Forms tried:
  - links at depth 0, 60 and every 400 levels down to 1,500, beyond the longest path the system takes;
  - link targets: an outside folder, its subfolder, the project, `/`, `..`, `.`, a file, and nothing (dangling);
  - links inside folders without read, write or execute permission;
  - files without permission;
  - folders turned into files and back between passes (5 runs);
  - folders swapped with links to an outside folder about 1,000–3,800 times during the removal (10 runs).
- **R15.** The removal grows with the entries, not their square: 8,000 sibling folders take 0.37 s against 0.31 s for a plain recursive removal; review 3's head took 22.7 s. A 1,500-deep chain together with wide folders takes 0.67 s against 0.67 s.
- **Spot checks of R9, R10 and R12.**
  - R9: 80–81 Ctrl-C presses through a clean-up of about 4 s were held, then `gov` exited 130.
  - R10: a 1,500-deep chain with locked folders and files: pass 0, fail 3, nothing left.
  - R12: after a clean-up that met lasting errors, `gov` still exits 143, 129 or 130.
- **The changed cases.**
  - 588e43ae11ff tests R14 and R15 as stated. By design, its nested races avoid any moment when a nested pytest is still alive, so W1's path is outside them; its README says so.
  - c348af6bc9ae only ties R9's second press to the start of the removal. It still requires two presses, exit 130, an empty TMPDIR, no marker and the child gone. Nothing is lowered.
- **No leak in output; no write.**
  - The marker never reached stdout, stderr or the envelope in any run, and unstopped runs' output held none of pytest's words.
  - Planted projects changed only where the planted mover itself moved a folder in.
  - The worktree's status was unchanged.
- **`gov accept DAEO-ouet --json`.**
  - Exit 0 in 224 s; `outcome: pass`.
  - Passed per line: success 1–5 are 14/20/23/11/34; failure 1–4 are 16/23/11/30.
  - `unmapped` 22 passed; `totals` 106 passed.
  - stderr was empty, the given TMPDIR was empty afterwards, and the worktree status (ignored files included) was unchanged.

## Findings

**W1. After an ordinary stop of `gov`, a run that a test started in a session of its own carries on. When its pytest ends, it rebuilds the private folder's path in the caller's TMPDIR, down to a folder named after the outer acceptance test. `gov` has already ended with exit 143 or 130 and that TMPDIR empty, and says nothing.**
- **Done.**
  - An outer planted test runs a nested `gov accept` in a session of its own, with its TMPDIR inside the test's temporary folder, as W2-96's harness runs every planted run.
  - The nested test sleeps 1–3 s or writes, then ends.
  - A stop reached the outer `gov` alone while the nested pytest was still running: SIGTERM, Ctrl-C or coreutils `timeout`, at random or while the nested test slept or wrote.
  - The same was tried with the nested TMPDIR set to the child's TMPDIR, and with a test that does not wait for its nested run and is not stopped.
- **Happened.**
  - When `gov` ended, the given TMPDIR was empty. 2.4–3.4 s later, 23 of 24 runs held 6 entries: `gov-accept-XXXX/tmp/pytest-of-usain/pytest-0/test_rv4mark_outer_runner_case0/given-1`, the outer test's name as pytest names its temporary folder.
  - The nested pytest's report writer creates its report's missing folders. The nested gov then removed only its own folder.
  - The no-wait test gave pass, exit 0, then the same 6 entries in 3 of 3 runs.
  - With the child's TMPDIR form, 2 unnamed entries stayed.
  - Stops that reached both govs or the whole tree left nothing (0 of 16).
- **Should have happened.** Nothing of the run is in the caller's TMPDIR after `gov` ends either (R14, KPI 2): no process the run started, in any session, writes there once the clean-up is done.
- **Not new with this head.** It exists at 382e6d8fba8c too: the removal neither causes nor prevents it. Review 1 judged an own-session process unable to write once the folder is gone; review 3 left this case not reproduced.
- **Severity: medium-low.**
  - Folder names only: no source, assertion text or output.
  - It appears when the orphaned test ends. In W2-96's suite that is mostly within a second, but up to 600 s for its sleeping tests.
- Ordinary work: yes, because Ctrl-C, coreutils `timeout` and a closed terminal's SIGHUP reach `gov` and its process group but never processes in other sessions. W2-96's own suite runs every planted `gov accept` that way, so a stop of `gov accept DAEO-ouet` almost always lands during one. No deliberate construction is needed. A whole-tree stop avoids it.
- Consequence: fails open. Test names are left in the caller's TMPDIR, as V1's leftovers were judged.

**W2 (row). A lasting error: after its twenty passes, `gov` passes over it in silence.**
- **Done.** A read-only mount inside the private folder, made in a user namespace.
- **Happened.**
  - `gov` held the signals for about 4.1–4.8 s, then reported as the results said: pass 0, fail 3, 143, 129, or 130 after a Ctrl-C storm.
  - stderr was empty.
  - 9 entries stayed in the given TMPDIR, test-named folders and test-written files among them.
- **Should have happened.** R14 allows the remaining error to be passed over. KPI 2 says the temporary files are removed, and nothing tells the caller they were not.
- **Severity:** low.
- Ordinary work: no, because a lasting error needs a mount, an entry owned by another user, or a process that keeps the folder present through all twenty passes.
- Consequence: fails open (if hit).

**W3 (row). A test that replaces the runner's private folder with a link to a folder outside makes the clean-up change that folder's permissions.**
- **Happened.**
  - The outside folder went from 0755 to 0700.
  - pytest's report was written through the link into the outside folder.
  - `gov` then passed over the link for about 4.5 s and reported pass, exit 0.
- **Not new in kind.** Review 3's head made the same change once, then reported `crash`.
- **Not reproduced:** the narrower race between an entry's check and its permission change (10 link-swap runs).
- **Severity:** low.
- Ordinary work: no, because a test must find and replace the runner's own folder (a deliberate construction).
- Consequence: other.

Classification: 1 yes / fails open (W1); 0 yes / other; 2 rows for Wave 3 (W2, W3).

## Verdict

**Fail.** W1 is both "yes" and "fails open". It is not new with this head, and review 3's V1 is fixed.

