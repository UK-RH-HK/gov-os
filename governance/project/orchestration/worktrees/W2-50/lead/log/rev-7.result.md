I've finished the probe. All twelve fields first, then the payload.

task: Fresh FULL read-only probe of DAEO-kl5e (W2-50) at head 56240ffb7d02bf5dd0e841da8db10d9a4d177eca: the merge-back e61b67f5 under the probe gate, and DEC-853's scan fix (a403309e, tests 878467c9, ticket file c2b094da).

status: DONE. Judgement **pass**: eight findings, none both reachable in ordinary work and failing open or losing work. Four fail open, but only after accidents no ordinary step produces; all eight are rows.

work_completed:
- Step 0 sandbox check passed: (a) the write was refused with a read-only file system error; (b) both git commands worked.
- Identity checks matched: role independent-auditor, ticket DAEO-kl5e, this worktree, branch w2/W2-50, the stated head.
- Read the ticket file, DEC-853/779/785/790/801/750/754/757/347/290, P-W2-49, the four commits, the scan module and its tests, and the probe gate (`src/gov/close/command.py`, `history.py`, `repo.py`, plus the check runner).
- Ran 16 probe scripts against temporary projects in my session's temp folder (temporary HOME, canaries built at run time and never printed). I also compared the pre-run-8 scan module, extracted with `git show 0affa162:…` into my temp folder, side by side with the head's.
- Read-only git checks of both merges.
- Ran the W2-50 suite, its DEC-853 file with the large cases separately, `tests/unit/secrets`, W1-15, W1-16 and W1-17.

files_changed: none in any repository. My scripts, temporary projects and logs are all in my session's temp folder. The guard's own hooks wrote their per-call snapshots and `last_head.json` under this worktree's `.gov-runtime/` as they do for every session, and `.gov-runtime/records.jsonl` changed at 06:01:05, the minute of my `gov retrieve` calls (I did not read it to tell which wrote it). `secrets-clean.json` (03:48) and `query-vector-cache.db` (02:32) are untouched.

evidence:
- **Commits and trailers.**
  - a403309e: Task DAEO-kl5e, Role engineer, Implements DEC-853.
  - 878467c9: Role independent-test-designer.
  - c2b094da: Role orchestrator; changes only the ticket file.
  - e61b67f5: merge of 0affa162 and 7f95e6f5; Task DAEO-kl5e, Role orchestrator.
  - 56240ffb: Role orchestrator; the checkpoint only.
- **The merge-back.** Its tree ec3722a5… equals `git merge-tree --write-tree 0affa162 7f95e6f5` (exit 0, no conflict). It leaves every ticket path as on the ticket's side. It differs from w2/integrate's side in exactly the 39 files the ticket changed since the merge base 00fe09b6.
- **The outward merge.** w2/integrate is now 7bb02cb7, 17 commits past 7f95e6f5. `git merge-tree --write-tree w2/integrate HEAD` is clean (tree 0dca14e3…), and every ticket path in it equals this head's. None of the 17 commits touches a ticket path, and no commit anywhere in the range carries Role independent-auditor.
- **Scan reproductions:**
  - WAL case, writer open: new code green (exit 0) with "clean result reused … store.db"; old code on the same state reports `.gov-runtime/store.db`.
  - WAL case, writer killed after its commit: new code green with `store.db` reused.
  - Runner timeout at 15 s: `_run_command` returned None (RED), the scan ran on with 20 gitleaks processes, finished 135 s after the start and wrote the record.
  - Timing: on stand-ins at this worktree's scale, the first full scan took 438.5 s (peak 6.2 GB).

tests:
- `tests/unit/secrets`: 26 passed.
- `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py`: 23 passed: 20 with `-k "not large"` (103 s), then 3 with `-k large` run alone (422 s; 169.0 s, 168.3 s, 84.4 s).
- The rest of W2-50: 154 + 204 + 255 passed. **Whole W2-50 suite: 636 passed, 0 failed, 0 skipped.**
- W1-15: 124 passed.
- W1-17: 65 passed.
- **W1-16 cannot run in this sandbox:**
  - As is: 8 passed, 159 errors, because its fixture makes its sandbox under `/tmp`, which is read-only here.
  - With a small pytest plugin, kept in my temp folder, that sends that one folder elsewhere: 106 passed, 33 failed, 28 errors. Every failure I inspected comes from the code-graph tool's folders under `/tmp` (`/tmp/gov-cbm-1000/…`, `/tmp/cbm-daemon-1000`, its CLI endpoint). None involves a verdict of the scan.
  - In its four secrets-related files: 101 passed, 3 failed, 9 errors, all from `/tmp`.

discoveries:
- **F1, a fail-open:** a SQLite store's clean result is reused on its main file's bytes, while rows still in its `-wal` are only seen by a fresh scan.
- **The code-graph tool writes in WAL mode:** `codebase-memory-mcp`'s binary carries both `PRAGMA journal_mode = WAL;` and `= DELETE;`, so `code.db` is written in WAL mode while the tool works.
- **gitleaks' verdict depends on timing:** on identical bytes, which tokens `gitleaks stdin` misses depends on how the input reaches its pipe.
- **The `[extend] path` file is outside the reuse key.**
- **The runner's timeout orphans the scan:** dash forks the command, and the timeout kills only the shell.
- **This sandbox's `.gov-runtime/` is read-only:** inside a launched session it is mounted `ro`, so a worker's check cannot write the record but reads and reuses one written by an unsandboxed session.
- **`gov retrieve` is stale:** FACET_UNAVAILABLE.

risks:
- My stores are stand-ins. The real `code.db` schema is unknown, so my timings (141 s and 438 s for first full scans) are lower than the lead's 876 s on the real worktree stores.
- F2 is shown at the gitleaks level, but not end to end inside the check.
- W1-16 was only partly run.

lessons: for committing this record so the gate accepts it:
- Write `probed_commit` as the full id 56240ffb7d02bf5dd0e841da8db10d9a4d177eca. A short id makes the failed record count again, and the new one is refused as a moving name.
- Commit the record alone, with `Role: orchestrator` only. Don't put the ticket file in the same commit.
- My session id, as my scratchpad path shows it, is 621773c3-6783-4280-ac9c-0ff58adb1967. It differs from every trailer value.
- Commit nothing on the ticket's paths after 56240ffb. The CIT-E has no DEC-853 section, and adding one now makes this probe stale. A ticket-file edit is fine only as an orchestrator or owner commit changing that file alone.
- Merge outward with a plain `git merge`.

proposed_decisions: no round. Classification: F1–F5 are "ordinary work: no" (rows); F6–F8 are "ordinary work: yes, consequence other (fails closed)". None justifies a round.
- F1, F3, F4 to the Wave 3 hardening pass or the scan's next owner. Recommended fix for F1: never reuse a SQLite store with a `-wal` or `-journal` beside it, or key the reuse on all three files. High confidence.
- F2, F5: Wave 3 rows. Medium confidence.
- F6, F7, F8: rows for the check runner's owner (W2-45). For F6, kill the check's process group on timeout. Medium-high confidence.

unresolved:
- Whether a frozen gitleaks miss (F2) ever occurs inside the check under the real stores' load.
- The real code graph's schema and its WAL behaviour during queries.
- A full W1-16 run in a session where `/tmp` is writable.

recommended_next_action: Commit this pass record for 56240ffb (orchestrator role, the record alone), take F1–F8 as rows, then merge W2-50 into w2/integrate with a plain merge and run `gov close`.

---

**Step 0.**
- (a) `open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kl5e','w')` failed with "OSError: [Errno 30] Read-only file system".
- (b) `git hash-object -w --stdin` gave `1ae28402a109c3397a44b19239a00adfa9472eb0` (exit 0); `git update-index --refresh` exited 0.

**Head probed:** 56240ffb7d02bf5dd0e841da8db10d9a4d177eca.
**`gov.__file__`:** `/home/usain/gov-os-worktrees/W2-50/src/gov/__init__.py`

**`git status --short`**, before and after, identical. All twelve are `/dev/null` character devices the sandbox mounts:
`?? .bash_profile`, `?? .bashrc`, `?? .gitconfig`, `?? .gitmodules`, `?? .idea`, `?? .mcp.json`, `?? .profile`, `?? .ripgreprc`, `?? .vscode`, `?? .zprofile`, `?? .zshrc`, `?? docs/source`

**`gov retrieve` questions:** "secrets-indexing check SQLite store rows WAL journal scanned content DEC-290", and "what governs the secrets scan's reuse of a clean result" with `--id DEC-853 --id DEC-290`. Neither helped: both returned FACET_UNAVAILABLE (lexical and semantic stale), and the closure facet returned no items. I read sources by name instead.

**Guard read refusals: 1.** A compound call that included `ls governance/` was refused as possibly reading the settings or held-out file. I took the refusal and read the named files instead. Other refusals, none repeated:
- the guard refused a write to a path given by a shell variable it could not resolve; I redid it with literal temp-folder paths;
- the guard refused an inline heredoc it could not read (DEC-409); I moved it to a script file;
- the harness declined one `sh -c` command it could not check; I moved it to a script file.

**Judgement: pass.** Under the judgement rules and DEC-790, only "Ordinary work: yes" together with "fails open" or "loses work" fails a probe, and no finding has that.

## Findings

**F1 (medium; reproduced).** A SQLite store's clean result is reused because its main file's bytes are unchanged. But a fresh scan reads the store's rows through SQLite, and those include rows still in the store's write-ahead log.
- *What I did:* scanned a WAL-mode store clean. Then a writer committed a row holding a secret to the WAL, and either stayed open or was killed after its commit. I tried both the kernel canary rule and a default-rule token shape. The secret stood across a page boundary of the WAL, so neither file's bytes are flagged.
- *What happened:* the check was green, labelling `store.db` as reused. The `-wal` was scanned by its bytes, found clean, and reused on the next run. The pre-run-8 scan on the same state reports `.gov-runtime/store.db`. The check goes red only once the WAL is checkpointed into the main file.
- *What should happen:* red, or at least the store's rows read again.
- When the secret sits whole inside the WAL (the usual case), the `-wal`'s own scan finds it and the check is red, naming `store.db-wal`.
- Ordinary work: no, because it needs four things at once:
  - a secret already past the pre-index filter;
  - a WAL-mode store with frames not yet checkpointed while the check runs. The project's own stores never use WAL (no `journal_mode` anywhere in `src/`); only the external code-graph tool writes `code.db` that way, while it works;
  - the store's main file unchanged since a clean scan;
  - the secret standing across a WAL page boundary.
- Consequence: fails open.
- Reach: any session that runs the check, a launched worker included, since it reuses the record an unsandboxed session wrote. But only the tools of unsandboxed sessions leave such WAL frames: a launched worker's `.gov-runtime/` is mounted read-only. This is not a guard text-parsing finding.

**F2 (low; the timing dependence reproduced, a frozen miss not).** `gitleaks stdin` misses different tokens in identical bytes depending on how the input reaches its pipe. With reuse, the first scan of a store's bytes decides for every later run.
- *What I did:* fed 1.2 MB of binary-like bytes holding 1,199 token-shaped values (a) as the scan feeds gitleaks and (b) unevenly.
- *What happened:* quiet feeds always miss the same single token. Uneven feeds miss 1 to 4 others, a different set each run. Twelve concurrent feeds made the way the scan makes them, beside threads rendering rows as the scan does, gave 6 different missed sets. A single-token text store at an offset missed in 4 of 12 contended feeds was still found by 24 of 24 first scans of the real check.
- *What should happen:* a verdict that depends only on the bytes, rules and binary, which is the reuse key's premise.
- Ordinary work: no, because it needs a secret past the filter, and a moving fragment boundary falling inside its only occurrence in that one first scan. A SQLite store holds each value several times; the check missed none of 24 first scans.
- Consequence: fails open.
- Reach: any session that runs the check. No session creates the precondition through the guard.

**F3 (low; reproduced).** When `.gitleaks.toml` extends another rules file by `path`, gitleaks reads that file, but the reuse key covers only `.gitleaks.toml`'s own text.
- *What happened:* `base.toml` gained a rule finding a value in an unchanged store. The check stayed green with the store reused; the same check without a record was red.
- *What should happen:* any change of the rules in force ends every earlier clean result.
- The same applies by reading (not reproduced) when the gitleaks `PATH` finds is a wrapper or a version manager's shim: an upgrade behind it leaves the key unchanged. This machine's gitleaks is a plain static binary, 8.30.1.
- Ordinary work: no, because this repository and the kernel extend gitleaks' built-in defaults only, never a file by path. It needs an adopting project using that form and an owner's edit of the extended file.
- Consequence: fails open.
- Reach: only with a precondition that no session creates through the guard in ordinary work; a rules edit is an owner act.

**F4 (low; reproduced by forcing the race in-process).** A SQLite store's digest is taken of the bytes read, but its rows are read afterwards from the file on disk.
- *What I did:* replaced a store whose secret is visible only in its rows by a clean one, between the read and the row read.
- *What happened:* the check was green and recorded the first store's digest as clean. With those exact bytes restored, the check stayed green by reuse, while a fresh judgement of them is red.
- Ordinary work: no, because it needs a writer replacing the store inside that window, and then the very same bytes coming back.
- Consequence: fails open.
- Reach: any session's check; the race comes from a store writer, not from a session.

**F5 (low; reproduced).** The reuse label prints each reused file's project-relative path. A clean file under `.gov-runtime/` whose name holds a canary had it printed on standard error on its second run; it was never printed before. Contents are never printed.
- Ordinary work: no, because names under `.gov-runtime/` are made by tools. `gov check` and `gov close` discard a green check's standard error.
- Consequence: other.
- Reach: any session running the check by hand.

**F6 (medium; reproduced).** When the check passes its declared limit, the runner reports RED (fails closed), but the scan goes on.
- `/bin/sh` is dash, which forks the command, and the runner's timeout kills only the shell. The orphaned scan keeps its 20 gitleaks children, finishes, and writes the record after the RED.
- With DEC-853's per-run limit (60 s plus 1 s a MB), an orphan can now run for minutes holding 4.7 to 6.2 GB. Before, the 60 s cap on each run ended it soon on large stores.
- Ordinary work: yes, because a first full scan (after a rules or gitleaks change, or with no record yet) of stores at today's size took 876 s in the lead's run on the real worktree stores.
- Consequence: other (fails closed; it holds CPU and memory while the next check may start; it records only content it scanned clean).
- Reach: any session running `gov check` or `gov close`.

**F7 (low).** The time margin and the working figure.
- First full scans took 876 s of 900 s (lead, real stores), 438 s on my stand-ins at this worktree's scale, and 141 s at the main tree's scale. With the record they take 0.8 to 2.7 s; with one large store changed, 35 to 61 s.
- For SQLite stores, "decided at 1 MB/s" holds per gitleaks run only. A 260 MB `store.db` stand-in hands gitleaks 1,598 MB per rule set, about 3,200 s at 1 MB/s against the check's 900 s. Real gitleaks reads 20 to 30 MB/s here, so the check fits. The acceptance figure is tested on plain stores only.
- Ordinary work: yes, because first full scans follow rules changes and fresh worktrees.
- Consequence: other (fails closed).
- Reach: any session.

**F8 (low; pre-existing; reproduced in general form).** A file that vanishes between the walk and its read makes the check fail closed: 2 of 4 runs beside a process making and removing files under `.gov-runtime/scratch/`. The guard's hooks create and delete snapshot files under `.gov-runtime/snapshots/` on every tool call (seen during my session), so a lead's check run while a worker works in the same worktree can fail this way.
- Ordinary work: yes, because a lead may check while its worker is making tool calls.
- Consequence: other (fails closed).
- Reach: any session's check while another session in the same tree makes tool calls.

## Found sound
- **The merge-back:** both sides kept and nothing dropped (evidence above).
- **The outward merge:** clean, and it leaves the ticket's paths as at this head.
- **The probe gate as W2-01 and W2-53 left it:**
  - The single failed record (probing fc9e6a2a…, an ancestor of 56240ffb) becomes an earlier round once a pass record for 56240ffb exists.
  - c2b094da and e61b67f5 lie before the probed head, so the gate does not measure them.
  - After the head there would only be the record commit, the outward merge (measured against git's own merge) and the 17 w2/integrate commits, none on the ticket's paths.
  - Nothing found that would refuse a passing record of this head, or let a stale one pass, provided the conditions in "lessons" hold.
- **The scan's pool:** the per-run limit grows with size; the pool is the processor count, largest file first, at most two files of 64 MiB or more at once; the large cases pass.
- **Changes and findings:** a store changed by one byte is scanned in full. A finding is never recorded, on any run, also when other stores are reused.
- **The record:**
  - missing, garbage, truncated, edited, of another form or of other rules: full scan;
  - two checks at once: both green, the record whole, no leftover parts;
  - it holds only the current run's digests, so it cannot grow without bound;
  - a record copied from another project reuses only identical bytes, and a canary store is still found.
- **Fails closed, record unchanged:** gitleaks missing, hanging, killed or exiting with an odd code; an unreadable file; a dangling link; a vanishing file. A hot rollback journal also fails closed, as before.
- **Environment:** gitleaks 8.30.1 reads only `GITLEAKS_CONFIG` (removed by the scan) and `GITLEAKS_CONFIG_TOML` (set per run).
- **The indexers' filter and `path_holds_secret`:** they hand gitleaks the same command, bytes and rule sets as before run 8, with the same verdicts (20 runs compared).
- **The ticket's link rule:** byte-identical to before run 8. A link into the temporary HOME's `~/gov-os-runs` is still not followed; a link to a project file holding a canary is still found.
- **No output printed a secret from any file's content.**

## Probe record body

```markdown
---
type: probe
task: DAEO-kl5e
reviewer_session: 621773c3-6783-4280-ac9c-0ff58adb1967
implementer_session: <the run-8 engineer's session>
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 56240ffb7d02bf5dd0e841da8db10d9a4d177eca
---

# Probe record: W2-50, the resume's fresh FULL probe — the merge-back and DEC-853's scan fix

## What was probed
- Head `56240ffb` on `w2/W2-50`: the merge-back `e61b67f5`, the ticket file `c2b094da`, DEC-853's tests `878467c9` and change `a403309e`. A fresh read-only reviewer (independent-auditor, session 621773c3-6783-4280-ac9c-0ff58adb1967, 2026-10-20), sandboxed launch, code under test this worktree's `src/` (DEC-732).
- The merge-back against git's own merge; the outward merge against `w2/integrate` at `7bb02cb7`; the probe gate as W2-01 and W2-53 left it, read against this history.
- The scan, run in temporary projects with a temporary HOME and canaries made at run time:
  - SQLite stores with `-wal` and `-journal` files, an open or killed writer, and a file swapped mid-scan;
  - the reuse key under changes of the rules, an extended rules file, the gitleaks binary and the environment;
  - the record damaged, copied, raced by two checks, and checked for growth;
  - fails-closed cases;
  - links, including into a temporary `~/gov-os-runs`;
  - the reuse label;
  - the time limit, the pool and memory, on stand-ins of today's stores (260 MB `store.db`, 210 MB code graph, 7,600 files);
  - the runner's own timeout;
  - the pre-run-8 module side by side with the head's.
- Suites: W2-50 636 passed (DEC-853 file 23 passed, its 3 large cases run alone); `tests/unit/secrets` 26 passed; W1-15 124 passed; W1-17 65 passed. W1-16 cannot run in the sandbox (its folders are under `/tmp`, read-only there; every failure seen was that).

## What it found
- **F1 (medium).** A SQLite store's clean result is reused because its main file is unchanged, though rows still in its write-ahead log hold a secret that stands across a WAL page boundary. The check is green; the pre-run-8 scan names the store. A secret whole inside the WAL is still found through the `-wal` file.
  Ordinary work: no, because it needs a secret past the pre-index filter, a WAL-mode store with frames not yet checkpointed during the check (only the external code-graph tool writes WAL), its main file unchanged since a clean scan, and the secret across a WAL page boundary, all at once.
  Consequence: fails open.
- **F2 (low).** `gitleaks stdin` misses different tokens in identical bytes depending on input timing, and reuse lets the first scan decide for later runs. Not reproduced end to end: 24 of 24 first scans by the check found the token.
  Ordinary work: no, because it needs a secret past the filter and a moving fragment boundary inside its only occurrence in that first scan.
  Consequence: fails open.
- **F3 (low).** A rules file that `.gitleaks.toml` extends by `path` is outside the reuse key: after it gains a rule, an unchanged store stays green.
  Ordinary work: no, because this repository and the kernel extend gitleaks' built-in defaults, never a file by path.
  Consequence: fails open.
- **F4 (low).** A store's rows are read after its bytes are hashed; a file replaced in between records clean bytes whose rows were never read. Shown by forcing the swap.
  Ordinary work: no, because it needs a writer inside that window and the same bytes returning later.
  Consequence: fails open.
- **F5 (low).** The reuse label echoes a clean file's name, so a secret in a file name under `.gov-runtime/` is printed on standard error.
  Ordinary work: no, because names there are made by tools.
  Consequence: other.
- **F6 (medium).** On the runner's timeout the check is RED, but the scan is orphaned (dash forks; only the shell is killed). It runs on with its gitleaks children and writes the record afterwards.
  Ordinary work: yes, because first full scans at today's size took 876 s of 900 s.
  Consequence: other (fails closed).
- **F7 (low).** First full scans are near the limit (876 s real; 438 s on stand-ins). "Decided at 1 MB/s" holds per gitleaks run, not for SQLite stores within 900 s.
  Ordinary work: yes, because first full scans follow rules changes and fresh worktrees.
  Consequence: other (fails closed).
- **F8 (low, pre-existing).** A file that vanishes during the walk (for example a rotated hook snapshot) fails the check.
  Ordinary work: yes, because a lead may check while its worker makes tool calls.
  Consequence: other (fails closed).

## Found sound
- The merge-back equals git's own merge (no conflict), keeps every ticket path, and drops nothing of `w2/integrate`.
- The outward merge is clean and leaves the ticket's paths as at this head.
- The probe gate: this record makes the failed record (probing `fc9e6a2a`) an earlier round; `c2b094da` and `e61b67f5` lie before the probed head; nothing after it touches the ticket's paths.
- The scan: limits grow with size; the pool is bounded, largest first, at most two large files at once; a one-byte change is scanned in full; a finding is never recorded; damaged, copied and concurrent records are handled; every failure fails closed and records nothing.
- The indexers' filter and the path check decide as before; the link rule is unchanged; no content is printed.

## Judgement
- **pass.** No finding is both reachable in ordinary work and failing open or losing work (DEC-779, DEC-785, DEC-790, DEC-801). F1–F8 are rows; F1's fix is to never reuse a SQLite store with a `-wal` or `-journal` beside it.
```