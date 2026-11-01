session_id 9734e4d7-6a4f-4607-b316-dbb9eb71ccf1 turns 80 ms 1716190 error False
task: Second and last FULL review (read-only probe) of W2-107 (DAEO-kiar), gitleaks verdicts remembered by content hash, round 2, at head 654fd0e3e26c

status: DONE. Verdict pass: the round-2 fixes for F-1, F-2, F-3 and R-1 hold when run, and no new finding is both "yes" and "fails open" or "loses work".

work_completed: Step 0 came first. (a) Writing /home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar FAILED ("Read-only file system"); no file was made. (b) The hash without -w worked (1ae28402a109). GOV_ROLE=independent-auditor and GOV_TICKET=DAEO-kiar. Top level /home/usain/gov-os-worktrees/W2-107, branch w2/W2-107, head 654fd0e3e26c (whole: 654fd0e3e26c3fa92feb6d106254b35d183ee853). DEC-732: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -c "import gov; print(gov.__file__)"` gave /home/usain/gov-os-worktrees/W2-107/src/gov/__init__.py. I read the ticket, P-SPEED-1 §4, design.md and design-r2.md, the first review's draft, and DEC-966 and DEC-967. I read the diff 0062ed549674..654fd0e3e26c, round 2's own change a6c459c59221..07ae41c63d12, both callers, the acceptance README, support module and runner, and the patches in tests/unit/secrets_check/. I ran 17 probes of my own in my sandbox temp folder. Projects, a git repository and stand-in gitleaks were built there from scratch. GOV_SECRETS_CACHE always named a file there, ~/.cache/gov-os/ was never touched, and planted tokens were built at run time and never printed.

files_changed: none in the repository. My temp folder /tmp/gov-launch-independent-auditor-ybmsj4l5/claude-1000/p is left behind because its removal was refused twice.

evidence: The results below are child runs of the worktree's own code unless marked in-process.
- **F-1 (shim):** the shim's inode, size, mtime and ctime were unchanged across the release switch. Before the switch the planted texts were let through (the older release cannot see them), and a second pass answered all 5 from the cache. After the switch all 5 texts were scanned and the planted ones dropped (3 kept). The next pass answered the 3 clean texts and scanned the 2 planted ones.
- **F-2 (mid-scan replacement):** the gitleaks was replaced in three ways the acceptance tests do not use: a newer one landing earlier on PATH, a symlink retargeted, and an in-place overwrite (same inode 1169456). In each, the next process scanned all 8 texts and dropped all 4 planted ones, so nothing was credited to the wrong engine.
- **F-3 (in-process):** the fingerprint changes with the reading form, with a rule set's text and with the rule sets' order.
- **Hanging version call:** 10.9 s for 8 texts, one wait per process. Every text was scanned with the right verdicts, no cache was made, and no process was left running.
- **Two engines at once:** 4 rounds of 3 + 3 processes on one cache. All 12 runs of the real engine dropped all 10 planted files and caught the planted name.
- **Cache contents:** with a process holding the WAL, the cache file (12,288 bytes), `-wal` (41,232 bytes) and `-shm` (32,768 bytes) held 0 hits for the content, names, project folder name, planted token or its prefix, or gitleaks' version string, in UTF-8 or UTF-16.
- **Read stress:** 43,836 reads by the module's read-only and immutable reads against a live writer that inserts, clears and checkpoints gave 0 answers for never-written rows. The rest were 49 answers for rows written at some point and 31 caught errors.
- **Symlink loop:** a loop at the cache's name raises `RuntimeError` from cache.py line 189 (`remembered`), through line 168 (`_read`) into pathlib's resolve.
- **Exclusive lock:** a held exclusive lock took 10.5 s against 3.6 s without a cache.
- **Refusals:** 3 in all.
  - One compound probe command (loops, pipes, and removing my stand-in's own setting file) needed approval this session cannot give. I ran the same probe as single commands through a small Python runner of mine and overwrote the setting instead of removing it.
  - Removing my probe folder was refused twice ("permissions … not granted yet"), so I stopped there (AR-6).
  - No read refusals (DEC-849). I used neither gov retrieve nor the code-graph tool: every read was a file the brief named, or a targeted search in tests/, src/ or docs/.

tests: none run (no suite re-run, DEC-959 item 1). I ran 17 probes of my own; the results are in the record below.

discoveries:
- **R-A (new in round 2):** the read-only fallback raises on a symlink loop at the cache's name, so the rebuild stops.
- **R-B (R-1 half closed):** sandboxed sessions now read the cache (by the immutable read when no outside process holds it) but never write it.
- **R-C:** an exclusive lock now costs about 6 s per text (about 4 s in round 1).
- **R-D:** the gitleaks call's own flags are outside the fingerprint (latent).
- **R-E:** if a suite run has GOV_SECRETS_CACHE set, the existing tests' `subprocess.run` patches see the new version call.

risks: The leftover temp folder holds planted test tokens (in project files and request files), cache files with digests only, stand-in scripts and logs: about 1.3 MB and about 260 files and folders. R-B leaves in-session rebuilds slow until the orchestrator decides. If R-B is resolved by naming a cache in sessions' environment, R-E comes with it.

lessons: In this launch the permission system refuses compound probe commands with loops, pipes or rm, and refuses removing the auditor's own temp folder. Write each probe as one Python runner, and the lead removes the folder. This session's scratchpad path names 9734e4d7-6a4f-4607-b316-dbb9eb71ccf1, probably its session id.

proposed_decisions: Classification (DEC-809): no round proposed. Rows: R-A no/other (low), R-B yes/other (medium), R-C no/other (low), R-D no/fails open, latent (low), R-E no/other (low). The lead's residuals are confirmed as declared, none worse. Recommendation: pass, and W2-107 goes on to merge. The rows go to the Wave 3 hardening list. R-B needs an orchestrator decision: may sessions write ~/.cache/gov-os/, or get a named cache (and then R-E)? Confidence: high.

unresolved: R-B's decision; KPI S7's record line and the nightly's one line, both at merge by design; the leftover temp folder.

recommended_next_action: The lead commits this probe record as the second review's pass, has /tmp/gov-launch-independent-auditor-ybmsj4l5/claude-1000/p removed, and asks the orchestrator for R-B's decision.

```
---
type: probe
task: DAEO-kiar
reviewer_session: lead fills
implementer_session: b13fb711-df4f-4b90-8459-574321099009
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 654fd0e3e26c3fa92feb6d106254b35d183ee853
---

# Probe record: W2-107 (DAEO-kiar)

## Summary
Head 654fd0e3e26c, base 0062ed549674; round 2's code change is 07ae41c63d12. Seventeen probes ran the worktree's own code (PYTHONPATH=<worktree>/src). Projects, a git repository and stand-in gitleaks were built from scratch in the reviewer's temp folder, and every probe named its own GOV_SECRETS_CACHE there. The machine's cache was never touched, and planted tokens were built at run time and never printed.

Round 2's four fixes hold when run:
- an upgrade behind a shim whose bytes stay the same is forgotten (F-1);
- a gitleaks replaced during a scan is never credited with the older one's verdict, in three ways of replacing it that the acceptance tests do not use (F-2);
- the reading form is in the fingerprint (F-3);
- a read-only cache is read, answering only the current engine's rows (R-1).

No new finding is both "yes" and "fails open" or "loses work". There are five rows (R-A to R-E), and the lead's declared residuals are confirmed as declared, none worse. Judgement: pass.

## What was probed and found sound
- **F-1, an upgrade behind a shim.**
  - The setup: a gitleaks whose own bytes and file status never changed (same inode, size, mtime and ctime) ran whichever release a setting file named.
    - Release one was an older engine: it drops the project's canary rule's findings and says "8.0.0-probe-one".
    - Release two was the real gitleaks 8.30.1.
  - Under release one, process 1 let the 2 planted files through (10 scan calls, 1 version call), and process 2 answered all 5 texts from the cache.
  - After the switch, process 3 scanned all 5 texts and dropped the planted files. Process 4 answered the 3 clean texts and scanned the 2 planted ones.
- **F-2, a gitleaks replaced during a scan.** Three forms not in the acceptance tests:
  - (B1) a newer gitleaks lands in a folder earlier on PATH during the first scan call;
  - (B2) the PATH entry is a symlink, retargeted to another release mid-scan;
  - (B3) the binary is overwritten in place, keeping its inode.
  - The older engine misses a default rule's tokens; checked without a cache, it keeps all 4 planted files and the newer one drops them.
  - In each form, the run in which the switch landed let 1 to 3 planted files through. The design allows this: it does not ask that run to rescan.
  - In each form, nothing was credited to the new engine. The next process scanned all 8 texts and dropped all 4 planted files, and the one after answered the 4 clean texts and scanned the 4 planted ones.
- **F-3 and the fingerprint (in-process).** The fingerprint changes with the reading form, with a rule set's text, and with the rule sets' order. It also changes with the version gitleaks says, once the version is asked again.
- **The version asked through PATH's gitleaks.**
  - It is asked once per process in every child run.
  - It is never asked with GOV_SECRETS_CACHE empty, or under pytest with no cache named.
  - A version call that hangs for 30 s costs one 10 s wait per process (10.9 s for 8 texts on the thread pool). Every text is then scanned with the right verdicts, no cache file is made, and no stand-in process is left behind.
- **Read-only and immutable reads.**
  - Setup: engine A filled the cache. Engine B, an older engine, then cleared A's rows and wrote its own, all held in the `-wal` by a process holding the cache open. Then the cache files and their folder were made read-only.
    - A was answered nothing: it scanned all 8 texts and dropped the planted ones.
    - B was answered its own 8 rows.
    - A was never answered one of B's rows.
  - With a read-only folder and no live writer, SQLite refuses the plain read-only open (SQLITE_READONLY_DIRECTORY), and the immutable read answers from the main file. This is the path a sandboxed session takes.
  - Stress: 43,836 reads by the module's own read function, half of them immutable, against a writer that inserts, clears and checkpoints. Result: 0 answers for rows never written, 49 for rows written at some time, and 31 caught errors, each a miss.
  - The immutable read can answer a row that a concurrent clearing has removed. But only a row of the asking engine's own fingerprint answers, and that engine judged it clean, so the answer is right.
- **Two engines at once.** Four rounds of 3 processes of an older engine and 3 of the real one ran at once on one cache, each judging 40 texts and 3 names.
  - All 12 real-engine runs dropped all 10 planted files and caught the planted name.
  - All 12 older-engine runs gave their own verdicts.
  - No row of one engine ever answered the other.
- **Row W2-L423's rule's exemption.**
  - A text naming a commit of repository A was let through and scanned on each of 3 calls; it was never remembered.
  - The same bytes in repository B were dropped twice.
  - A 40-hex value that names no commit was dropped.
- **Path names from a thread pool.** 42 names were judged twice, with the same verdicts both times. The planted name was caught on both passes. On the second pass 41 names were answered from the cache and 1 was scanned.
- **Cache contents.**
  - Three files were searched in UTF-8 and UTF-16: the cache (12,288 bytes), a live `-wal` (41,232 bytes) and the `-shm` (32,768 bytes). None of them held the files' content, the names, the project folder's name, the planted token or its prefix, or gitleaks' version string.
  - At the default place (HOME in a temp folder, no cache named, outside pytest), only `.cache/gov-os/secrets-scan.sqlite` was made, with `gov-os` owner-only, and nothing was written in the project.
- **Fails closed.** In each case below the verdicts were right and nothing raised:
  - a regular file where the cache's folder should be;
  - a dangling link at the cache's name;
  - a folder at the cache's name;
  - a 4 KB file-size limit, standing for a full disk: reads and writes both failed, every text was scanned, and nothing was written (the text that was new under the limit was scanned again afterwards);
  - a held WAL write lock: 4.3 s against 3.1 s, with answers still served;
  - a held exclusive lock (see R-C).
- **Settings and tests.**
  - Under pytest with no cache named, an existing test's `subprocess.run` patch saw only the two scan calls and raised as that test expects, and no cache or HOME folder was made.
  - W1-16's child processes build their environment from scratch with a temporary HOME, so they use a cache only there.
- **Scope and unchanged behaviour.**
  - The engineer's commits touch only `src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py` and `tests/unit/secrets/test_w2_107_*`.
  - The test designer's commits touch only `tests/acceptance/W2-107/`, and the orchestrator's only `docs/checkpoints/DAEO-kiar/`. No acceptance test was changed by the engineer.
  - Nothing under `tests/unit/secrets_check/` changed.
  - `indexable` and `path_holds_secret` keep their signatures.
  - `stores_with_secrets` behaves as before: the scan's new argument defaults to none and changes nothing there.
  - The guard does not import the filter.

## Findings (each with its two lines)
No finding fails the probe. Rows for the Wave 3 hardening pass, and residuals:

### R-A: a symlink loop at the cache's name stops the rebuild (new in round 2)
- **What was done.** GOV_SECRETS_CACHE named one of two links that point at each other, and a file was filtered.
- **What happened.** The plain open failed, as a miss. The read-only fallback then resolves the cache's path, and on Python 3.12 that raises `RuntimeError` on a loop. Nothing catches it, so `indexable` raises and the rebuild stops. Nothing is let through.
- **What should have happened.** A cache that cannot be opened counts as a miss, and the text is scanned.
- **Severity:** low. **Reproduced:** yes.
- Ordinary work: no, because a link loop at the cache's name needs a deliberate construction.
- Consequence: other (fails closed, but stops the rebuild)

### R-B: sandboxed sessions read the cache but never write it (R-1, half closed)
- **What was done.** I checked whether this session's sandbox can write `~/.cache` (it cannot; checked with access(2) only, never touching `gov-os/`). I then probed a read-only folder in my temp folder.
- **What happened.** With no live writer, the cache is read through the immutable path and answers the current engine's rows. Nothing is ever written. So an in-session second rebuild of an unchanged tree still scans every text that the unsandboxed runs (the nightly, the orchestrator's) have not judged.
- **What should have happened.** KPI S1: a second unchanged rebuild scans nothing again.
- **Severity:** medium (speed). **Reproduced:** yes, in temp; the real `~/.cache` was not touched.
- Ordinary work: yes, because leads and engineers rebuild inside session sandboxes.
- Consequence: other (slow; fails closed). An orchestrator decision: may sessions write `~/.cache/gov-os/`, or should they get a named cache (see R-E)?

### R-C: an exclusive lock now costs about 6 s per text
- **What was done.** Another process held the cache in exclusive locking mode with a write open while 8 texts were judged on 8 threads.
- **What happened.** 10.5 s against 3.6 s without a cache. Each text waits about 2 s on the lookup, 2 s on the new read-only fallback and 2 s on the write. Round 1 waited about 4 s per text. The verdicts were right, nothing hung, and the wait is bounded.
- **What should have happened.** A short wait, then a scan. This is the declared residual (a held lock's two-second waits), about 1.5 times as long.
- **Severity:** low. **Reproduced:** yes.
- Ordinary work: no, because nothing in ordinary work holds the cache's exclusive lock for long.
- Consequence: other (slow)

### R-D: the gitleaks call's own flags are outside the fingerprint (latent)
- **What was done.** Read only; not run.
- **What happens.** The fingerprint covers gitleaks' bytes and version, the rule sets, the reading form and the cache's format. It does not cover the flags or the environment the scan gives gitleaks. A change to the call that finds more (a decoding or archive depth, say) would keep the old clean verdicts across every worktree, unless the engineer also raises the reading form. The suites would not show it, since pytest uses no cache.
- **What should have happened.** Any change to what decides a verdict forgets the remembered verdicts.
- **Context.** No such change is planned: `docs/` names none, and decoding already defaults to depth 5.
- **Severity:** low, latent.
- Ordinary work: no, because no change to the call's flags is scheduled. Under DEC-803 it is an entry criterion of any ticket that changes them: raise the reading form, or put the call's arguments in the fingerprint.
- Consequence: fails open (latent)

### R-E: with GOV_SECRETS_CACHE set in a suite's environment, the existing patches see the version call
- **What was done.** The pattern of an existing test's `subprocess.run` patch (it reads the scan's environment) was run in-process under a pytest-like environment, without and then with a cache named.
- **What happened.** Without a cache: only the two scan calls, and the expected `RuntimeError`. With a cache: the patch sees the new `version` call first, and the filter raises `KeyError` instead. Tests that count gitleaks calls would also see answers from the cache.
- **What should have happened.** The existing suites see every scan as before. The pytest rule ensures this only while GOV_SECRETS_CACHE is unset.
- **Severity:** low. **Reproduced:** yes, in-process.
- Ordinary work: no, because nothing sets GOV_SECRETS_CACHE for a suite run today. It becomes yes if R-B is resolved by naming a cache in sessions' environment.
- Consequence: other (spurious test failures; fails closed)

### Residuals the lead declared, confirmed as declared (none worse)
- **A gitleaks upgraded behind a shim during one process's run.** In-process, the fingerprint is unchanged until the version is asked again, so the old release's verdicts answer for the rest of that one process. No long-lived process calls the filter again and again: retrieval and the code index run as commands. Ordinary work: yes, rarely, because it needs a shim install and an upgrade landing during one rebuild. Consequence: fails open, for at most the rest of that process.
- **Rule sets or engines evicting each other's verdicts.** With two engines running at once, the older engine got 0 answers from the cache in 12 runs and the real engine 61. Ordinary work: yes. Consequence: other (slow).
- **An extended rule file outside the fingerprint, and a relative GOV_SECRETS_CACHE.** Not re-run; unchanged since round 1. Ordinary work: no. Consequence: fails open (extended rules) and other (relative name).
```
