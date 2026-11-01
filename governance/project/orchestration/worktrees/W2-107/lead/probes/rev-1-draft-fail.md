session_id f9562598-f40e-41ef-b83d-85b313082ca8 turns 52 ms 1227999 error False
I found three ways a secret can be answered "clean" from the cache, all reproduced, so the verdict is **fail**. The fail-closed cases, the cache's contents, the commit-hash exemption and the unchanged interfaces all held. Nothing in the repository was written. My probe folder could not be removed: removing it was refused twice, so I stopped there (AR-6).

```
task: Read-only FULL review (probe) of W2-107 (DAEO-kiar), gitleaks verdicts remembered by content hash, at head a6c459c59221
status: DONE — probe complete; verdict fail: findings F-1, F-2 and F-3 are each "yes" and "fails open"
work_completed: Step 0 first: (a) the write of /home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar FAILED ("Read-only file system"; no file made); (b) the hash without -w worked. GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-kiar; top level /home/usain/gov-os-worktrees/W2-107, branch w2/W2-107, head a6c459c59221. DEC-732: python3 -c "import gov; print(gov.__file__)" gave /home/usain/gov-os-worktrees/W2-107/src/gov/__init__.py. Read: the ticket, P-SPEED-1 §4, the lead's design note and checkpoint, DEC-966, 967, 911, 285 and 853, the diff 0062ed549674..a6c459c59221, both callers, the acceptance README and support module, and the patches in tests/unit/secrets_check/. Ran 9 probes of my own: projects, repositories and stand-in gitleaks built from scratch in my temp folder, each with GOV_SECRETS_CACHE in that folder; ~/.cache/gov-os/ was never touched.
files_changed: none
evidence: probe A (shim): fingerprint unchanged across the upgrade; the token file was let through with 0 gitleaks calls, in-process and in a fresh process; the same newer engine without a cache drops it. Probe B (engine replaced during a scan): calls by the old release then the new one; the next rebuild let the file through with 0 calls, in-process and in a fresh process; without a cache it is dropped. Probe C (reading form): fingerprint unchanged with _FORM bumped; the fixed reading let the file through from the cache; without a cache it is dropped. Probes D to H and the template check are in the record below. Refusals: 2, both for removing my own probe folder (the compound command needed approval for its removal; the removal alone was refused: "permissions ... not granted yet"); 0 read refusals (DEC-849).
tests: none run (no suite re-run, DEC-959 item 1); 9 probes of my own, results in the record
discoveries: F-1, F-2, F-3 (below). R-1: in a sandbox that makes ~/.cache read-only (this session's does), the cache is never made, and a populated one is never read either, so rebuilds run inside sessions get no speed-up. The lead's measures used a scratch cache under /tmp, which hides this. The engine identity departs from the approved design's version string (P-SPEED-1 §4), and the lead's stated reason does not hold: under pytest with no named cache, no fingerprint is computed at all.
risks: F-3 is latent: it becomes real as soon as the filter's reading changes, and DEC-911 item 6 already schedules such a change (row W2-L419's reader, Wave 3). R-1 may leave the speed goal unmet for in-session rebuilds. Leftover folder /tmp/gov-os-lead-W2-107/gov-launch-independent-auditor-5r_tibq1/claude-1000/probe (964 KB, 217 files and folders); it holds planted test tokens made at run time.
lessons: In this launch the guard asks approval to remove the session's own temp folder, so a reviewer cannot clean up and the lead must. gov retrieve was not used: every read was a file the brief named, or a targeted search in tests/ and src/. This session's scratchpad path names f9562598-f40e-41ef-b83d-85b313082ca8, probably its session id.
proposed_decisions: Classification (DEC-809): F-1 yes/fails open (medium); F-2 yes/fails open (low); F-3 yes/fails open (medium, latent); R-1 yes/other; R-2 yes/other; R-3 no/fails open; R-4 no/other; R-5 no/other. Recommendation: a repair round of W2-107 (it has not merged; under DEC-802 the fixes ride in that resume), test designer first (MR-3): (1) the engine's identity also carries gitleaks' version string, as the approved design says, beside the binary's digest; (2) one fingerprint per judgement, taken before the scan and used for both the lookup and the write, with nothing written if the engine on PATH changed during the scan; (3) the form of what a scan reads (the module's _FORM) in the fingerprint. Confidence: high that F-2 and F-3 are real and cheap to close; medium on how ordinary F-1 is. The alternative for F-3 under DEC-803 is an entry criterion of the ticket that changes the reading (row W2-L419's). R-1 needs an orchestrator decision: may rebuilding sessions write, or at least read, ~/.cache/gov-os/?
unresolved: R-1: only this auditor's sandbox was seen, not the rebuilding roles'; KPI S7's record line is deferred to merge by design; the leftover probe folder
recommended_next_action: The lead gives F-1, F-2 and F-3 to a test designer for failing tests, then one repair round, and asks the orchestrator about R-1 before the measures are taken as the ticket's evidence.
```

---

```
---
type: probe
task: DAEO-kiar
reviewer_session: lead fills
implementer_session: b13fb711-df4f-4b90-8459-574321099009
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: a6c459c59221e3dbacdac8ef9cd8b5fc56dcad27
---

# Probe record: W2-107 (DAEO-kiar)

## Summary
Head a6c459c59221, base 0062ed549674. Nine probes ran the worktree's own code (PYTHONPATH=<worktree>/src). Projects, git repositories and stand-in gitleaks were built from scratch in the reviewer's temp folder, each probe with its own GOV_SECRETS_CACHE; the machine's cache was never touched. Planted tokens were built at run time and never printed.

The cache does what the acceptance tests ask: it fails closed, holds no text, and never remembers a finding. But the engine's fingerprint leaves out three things that decide a verdict, and each lets a secret reach an index:
- a gitleaks upgraded behind a shim (F-1);
- a gitleaks upgraded while a scan is running (F-2);
- a change to how the filter reads a text (F-3).

Judgement: fail. F-1, F-2 and F-3 are each "yes" and "fails open".

## What was probed and found sound
- **Commit-hash exemption.** A text whose only match is row W2-L423's rule naming a commit of repository A was let through and scanned on every call (scanned 1, remembered 0 each time). The same bytes in repository B, where the hash names no commit, were scanned and dropped.
- **Cache contents.** After scans of distinctive contents and names, a project folder name and a planted canary, none of it (nor its UTF-16 form) is in the cache file (12,288 bytes). The `-wal` (0 bytes) and `-shm` (32,768 bytes), read while a connection held them, hold none either. The cache file is the only file written, and its folder is made owner-only.
- **Fails closed.** In each of these cases the verdicts were right (the planted secret dropped), nothing raised, every text was scanned and nothing hung:
  - a populated cache made read-only;
  - a file-size limit at the cache's size, so writes fail (reads failed too);
  - a cache held under another connection's exclusive lock (6.2 s against 3.5 s for 7 texts);
  - a folder at the cache's place.
- **Two rule sets at once.** Four processes, two projects with different rules, one cache: every verdict right, every exit 0. No engine's row ever answered another's: the fingerprint is part of every row's key and of every read, so a lost clearing cannot cause a wrong answer.
- **Keys.** The bytes hashed are the very bytes scanned (one copy in memory). The kind is a column of its own.
- **Recording a finding.** A finding by any rule set is never remembered. Inside the scan the caller's list of findings shares its name with a local list that is rebound in the loop, but the first rule set that reports anything is always added to the caller's list first. Benign, and confirmed by the exemption probe.
- **Settings.**
  - The default place is under HOME.
  - An empty GOV_SECRETS_CACHE means no cache; a named one is that file.
  - A pytest test without a named cache uses none, and no HOME or an empty HOME means none.
  - GOV_SECRETS_FULL_SCAN counts as a full scan for any value other than empty or 0 (even "false"), which errs toward scanning.
- **Tests and the machine's cache.** Every test that rebuilds a child's environment sets HOME to a temp folder (W1-21's retrieval children get an empty scratch home). So a child can make a cache only in its own temp home, never the machine's.
- **Unchanged behaviour.**
  - `indexable` and `path_holds_secret` keep their signatures, order and raising.
  - Under pytest with no named cache, no fingerprint is computed and no file is opened, so the existing suites see the same calls.
  - The two existing tests that replace the scan take extra arguments.
  - `stores_with_secrets` and its record are untouched, and no file under tests/unit/secrets_check/ changed.
- **Template.** The repository's and the template's rule sets, as the filter builds them, are identical, so adopted copies share verdicts with this repository.

## Findings (each with its two lines)

### F-1: An upgrade behind a shim or wrapper keeps every old verdict
- **What was done.** gitleaks was first on PATH as a small shell shim with constant bytes, running whichever release a "current" link pointed to, as version managers' shims do. The "older release" was the real gitleaks without one default rule (github-pat), standing for a release before that rule existed. The "newer release" was the real gitleaks. A file holding a planted token of that rule was filtered with a cache under the older release. Then the link was moved to the newer release (an upgrade through the version manager), and the file was filtered again, in the same process and in a fresh one.
- **What happened.** The fingerprint was unchanged. Both later calls let the file through from the cache with no gitleaks call. The newer release with no cache drops the file. The nightly's full scan would drop it from its own index, but it never removes the stale clean verdict, so worktree rebuilds keep answering clean until the rules or the shim change.
- **What should have happened.** Any change to gitleaks forgets every remembered result (DEC-966 item 4, KPI S3, failure line F2). The approved design keys on gitleaks' version string (P-SPEED-1 §4), and that string is asked through the shim, so it would have changed. The lead replaced it with the digest of the file PATH finds, which is the shim. The lead's reason for avoiding the version string does not hold: with no named cache under pytest, no fingerprint is computed. Using both the digest and the version string keeps the acceptance tests' engines apart and covers shims.
- **Severity:** medium.
- **Reproduced:** yes.
- Ordinary work: yes, because installing gitleaks through a version manager whose shim stays put while the release behind it changes (asdf's or mise's shims, aqua's proxy, a container wrapper) is an ordinary set-up on an adopting machine, and upgrading through it is an honest act; on this machine gitleaks is a plain binary in ~/.local/bin, so it is not hit here today.
- Consequence: fails open

### F-2: An upgrade during a scan stores the old release's verdict as the new one's
- **What was done.** gitleaks was a plain file first on PATH (the older release, as in F-1). During its first scan call it was replaced, by a rename, with the newer release, as an upgrade landing while a rebuild runs. The token file was filtered with a cache, then filtered again in the same process and in a fresh one.
- **What happened.**
  - The first rebuild let the file through: the older release ran the first rule set and the newer release ran the second.
  - The write then fingerprinted the newer release, cleared every old row, and stored the verdict under the newer release's fingerprint.
  - Both later rebuilds answered clean from the cache with no gitleaks call. The newer release with no cache drops the file.
  - "Any change to gitleaks forgets everything" does not help here, because the clearing runs before the misattributed row is written.
- **What should have happened.** A verdict is kept only under the engine that produced it: one fingerprint taken before the scan and used for both the lookup and the write, and nothing written if the engine on PATH changed during the scan.
- **Severity:** low. Only texts being scanned at the moment of the upgrade are affected (about one per filter thread), and only a secret that the newer release alone recognises.
- **Reproduced:** yes.
- Ordinary work: yes, because a gitleaks upgrade while a rebuild runs (the secrets stage ran 275-548 s with a scan in flight on every thread) is a plausible accident, and it needs no shim.
- Consequence: fails open

### F-3: A change to how the filter reads a text keeps every old verdict, across every worktree
- **What was done.** A UTF-16 file holding the planted canary was filtered with a cache under an emulated older reading, one without the form that drops zero bytes. Then it was filtered under the current reading with the module's scan form (_FORM) bumped, as the module's own convention prescribes for any change to what a scan reads.
- **What happened.** The cache's fingerprint was unchanged. The fixed reading got the older reading's clean verdict from the cache and let the file through. Without a cache, the fixed reading drops it.
- **What should have happened.** A change to what a scan reads makes earlier verdicts unusable, as the DEC-853 record already does with _FORM ("another form is never trusted").
- **Why it matters now.**
  - DEC-911 item 6 schedules such a change: row W2-L419's reader in Wave 3, for a key export the current reading misses.
  - The cache is machine-wide and shared by worktrees on different branches, so one branch's older reading answers another branch's newer one.
  - The fix's own tests would pass (pytest uses no cache), while real rebuilds keep the stale verdict, and the nightly's full scan does not remove it.
- **Severity:** medium, and latent: it bites from the day the reading changes, and only for texts the older reading missed.
- **Reproduced:** yes, with the older reading emulated in-process.
- Ordinary work: yes, because a fix to how the filter reads is ordinary maintenance (_FORM is at 4, and DEC-911 item 6 schedules the next), an engineer following the module's convention bumps _FORM only, and worktrees on different branches share the one cache.
- Consequence: fails open. It is latent; under DEC-803 the alternative is an entry criterion of the ticket that changes the reading.

### Rows (no round)
- **R-1: sandboxed rebuilds never use the cache.** In a session sandbox that makes ~/.cache read-only (this auditor's does; checked with access(2) only), the cache is never made. A populated cache made read-only answered 0 of 6 clean texts (all 7 scanned, verdicts right), because the per-process preparation opens a write transaction even to read. So rebuilds inside such sessions get no speed-up, and KPI failure line F6 ("a second unchanged rebuild that scans everything again") holds there. The lead's measures used a scratch cache under /tmp, which hides this.
  - Ordinary work: yes, because leads and engineers rebuild their worktrees inside the sandbox (inferred from this session's write allowlist; the rebuilding roles' allowlists were not seen).
  - Consequence: other (slow; it fails closed)
- **R-2: different rule sets evict each other.** Two rule sets, or two gitleaks, on one machine clear each other's verdicts at every switch between processes. Project A remembered 5; project B, with one extra rule, cleared them; A then rescanned all 6.
  - Ordinary work: yes, because a branch that changes .gitleaks.toml rebuilds beside the others.
  - Consequence: other (slow)
- **R-3: an extended rule file is not in the fingerprint.** A .gitleaks.toml that extends another rule file brings in rules whose text is not in the fingerprint. This gap already exists in DEC-853's record. Neither the repository's nor the template's file does this. Not run, from reading only.
  - Ordinary work: no, because both files extend gitleaks' defaults only.
  - Consequence: fails open (a row for the Wave 3 hardening pass)
- **R-4: a held lock slows each call by about 2 s.** A lock held by another connection costs about a 2-second wait on each lookup and each write (no hang); one held through a whole rebuild would add about 4 s per file, divided by the threads.
  - Ordinary work: no, because nothing in ordinary work holds the cache's write lock for long.
  - Consequence: other
- **R-5: a relative cache name follows the working folder.** A relative GOV_SECRETS_CACHE resolves against the working folder, so it could make the cache inside a repository (digests only).
  - Ordinary work: no, because the setting is meant for absolute test paths.
  - Consequence: other
```
