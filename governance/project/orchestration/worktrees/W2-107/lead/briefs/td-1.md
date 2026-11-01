# Brief: independent test designer, W2-107 (DAEO-kiar), profile FULL

You are a fresh independent test designer (MR-3). Ticket: `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-107-tests` on branch `w2/W2-107-tests` (DEC-963); you never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-107`. You write the ticket's acceptance tests from its KPI lines and the design note below, in parallel with the engineer, and you show them red.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) In your worktree, `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside your worktree (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107-tests` and `w2/W2-107-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Never wait in the foreground for more than a few minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store. For what changed on `w2/integrate` since that store was built, `git show w2/integrate:<path>`. **Never one giant query or context (DEC-860):** a large question goes in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `tests/unit/secrets/test_w2_107*`), and name in your return any such result you were served.
- **Reads open, writes closed (DEC-820).** You may read the whole repository, git history and other worktrees, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); **(c) this ticket's implementation: you never read the files the ticket branch changes against its base (`git -C /home/usain/gov-os-worktrees/W2-107 diff --name-only w2/integrate...w2/W2-107` names them), other than your own tests; read the existing code as it stands on `w2/integrate` (`git show w2/integrate:src/gov/secrets/__init__.py`), never the ticket worktree's copy;** (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look for another form, and search named folders instead. Count every refusal you meet and list each in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document (`<<EOF`), no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools at literal absolute paths, and put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-107-tests/.gov-runtime/scratch/td/`, then run it. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (For you, `<this worktree>` is `/home/usain/gov-os-worktrees/W2-107-tests`. Your tests must import `gov` from whatever `PYTHONPATH` the run gives, never from a hard-coded path, so that once merged and run from the ticket worktree they exercise its code; your README says so.)
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (your scratch, your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". In test files, write that rule's id and keywords only in parts, as the existing tests do, and build every planted secret at run time from parts, so no file you commit holds one whole.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A test that needs a repository builds a temporary one from scratch (in pytest's `tmp_path`). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it. Install nothing (a tool you need is a package). No subagents that write.
- **Your budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree, with `TMPDIR=/tmp/gov-os-lead-W2-107` for every test run (where the sandbox sets its own temp folder, keep that one). Keep pytest's own temp retention, never a per-run `--basetemp`; run with `-o tmp_path_retention_policy=failed`. Remove whatever you make as soon as it is no longer needed.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` here. Your tests do not run `gov rebuild` either: they call the filter's public functions (and, where a test needs a child process, `python3 -m gov...` or a small script), so they need no store and no code graph.

## What you read

- The ticket file `.tickets/DAEO-kiar.md` (read-only): its KPI lines (7 success, 6 failure), its `allowed_paths` and its sources.
- The approved design: `governance/project/orchestration/packages/P-SPEED-1.md` (§4), and the design note below.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-966 (item 4), DEC-967, DEC-911 (item 4, the commit-hash exemption), DEC-285, DEC-939 (item 2), DEC-898; and DEC-462, DEC-136, MR-3 for how you work.
- The public interfaces, as they stand on `w2/integrate`: `gov.secrets.indexable(root, paths)` (returns, in order, the paths an indexer may read; drops a file with a secret, a file outside a `memory_class: governance` namespace of the path map, and anything unreadable; raises when it cannot decide) and `gov.secrets.path_holds_secret(root, path)` (whether a path's names hold a secret), and how the existing tests drive them: `tests/unit/secrets_check/test_secrets.py`, `test_commit_exemption.py`, `test_scan_scale.py` (their fixtures build a temporary project with a `.gitleaks.toml` and a path map), and `tests/acceptance/W2-71/` (a logging stand-in gitleaks that hands every call to the real one, and the commit-hash exemption). Use them to learn how a project and a planted secret are built, not what the new code is.

## The design note (the specification; behaviour only)

1. **What is remembered.** The pre-index filter judges two kinds of text with gitleaks: a file's content (for `gov.secrets.indexable(root, paths)`) and a path's names (for `gov.secrets.path_holds_secret(root, path)`). Each judgement whose verdict is **clean** is remembered, so the same bytes judged again under the same engine are answered without starting gitleaks. Nothing else the filter decides (a file's namespace, an unreadable file, a link out of the root) is remembered: those are decided every time, as now. The secrets-indexing check (`stores_with_secrets`) keeps its own record and is unchanged.
2. **Where.** One machine-wide SQLite file, `~/.cache/gov-os/secrets-scan.sqlite` (the home folder from `HOME`), outside every repository, shared by worktrees, close clones, the designers' store and the nightly. Its folder is made if missing (owner-only permissions). The environment variable `GOV_SECRETS_CACHE` names another file instead (tests use it, so no test touches the real one); set to the empty string, no cache is used at all and every text is scanned. While a pytest test is running (`PYTEST_CURRENT_TEST` is in the environment) and `GOV_SECRETS_CACHE` is not set, no cache is used either: the existing suites see every scan exactly as before, and only a test that names a cache file uses one.
3. **The key** of a remembered verdict: the sha256 of the exact bytes judged (the file's content as read; for a path, the bytes of the path and its names as the filter judges them), the kind (`content` or `path`, a column of its own, never joined into a string with the digest), and the engine's fingerprint. **The fingerprint** is a sha256 over: the cache format's version (an integer the code holds), the sha256 of each rule set in force (as the filter builds them from the project's `.gitleaks.toml`, both sets where there are two), and the identity of the gitleaks that `PATH` finds, as the sha256 of that binary's bytes (it changes with every gitleaks version and build, so it stands for the version string and is stronger; it needs no extra process). Tests change the engine by changing the stand-in's bytes or putting another one first on `PATH`.
4. **Only clean is remembered.** Clean means every rule set's gitleaks run ended with no finding at all. Any finding by any rule set is never remembered and is scanned again every time, including a match of row W2-L423's rule that the filter then exempts as a commit of the repository (that exemption depends on the repository, so such a text is judged afresh each time, and stays let through as today). A secret's content is therefore never answered from the cache.
5. **A changed engine forgets everything.** When the fingerprint differs from the one the cache holds, every remembered verdict is deleted before the first read, and the new fingerprint is stored. Every row also carries the fingerprint it was judged under, and a read answers only a row of the current fingerprint, so two engines (or two rule sets) running at once can at worst cause a rescan, never an answer from the other's results.
6. **Fails closed.** A cache that cannot be opened or made, is corrupt, is not of the expected form, or stays locked past a short wait counts as a miss: the text is scanned. A write that fails is ignored (the next run scans again). The cache file is never deleted or replaced by the filter; a damaged one stays a miss until removed. A scan that cannot decide (gitleaks missing, failing, timing out, the rules unreadable) still raises exactly as today, and nothing is written for it.
7. **The full scan.** With `GOV_SECRETS_FULL_SCAN=1` (any value other than empty or `0` counts the same) nothing is read from the cache: every text is scanned, and clean verdicts are written fresh (the nightly sets it; that one line in `nightly.sh` is the orchestrator's at merge).
8. **What the cache holds:** digests, kinds, fingerprints and verdicts only (and, optionally, a time). Never content, never a path or a file name, never a secret's text or a match.
9. **The counts.** `gov.secrets.scan_counts()` returns the running totals of this process, a fresh dict on each call: `{"content": {"scanned": n, "remembered": m}, "path": {"scanned": n, "remembered": m}}`, where `scanned` counts texts given to gitleaks and `remembered` counts texts answered from the cache. A caller takes the difference around its own work. The rebuild's record shows them beside W2-76's stage times; that line is in `src/gov/rebuild/` (W2-76's paths), so it is added at merge, outside this ticket.
10. **Concurrency.** Several rebuilds and the filter's own threads use the cache at once: SQLite in WAL mode with a short busy timeout; no connection is shared between threads unguarded; the fingerprint check and the clearing run in one write transaction. The fingerprint (and the binary's digest) is computed once per process and engine binary, not once per file.
11. **Unchanged:** `indexable` and `path_holds_secret` keep their signatures, return values, order and raising behaviour; a run with an empty cache gives the same verdicts as the code before this ticket.

## The behaviour to test (FULL: thorough, in proportion to the KPIs, no combinatorial expansion)

The tests plant a **stand-in gitleaks**, first on `PATH`, that counts its scan calls (a call with the `stdin` sub-command; log only counts and the rule set's digest, never content) and hands each call to the real gitleaks (find it with `shutil.which("gitleaks")` before `PATH` changes), and a **planted secret** built at run time, so a wrong "clean" is caught. Every test sets `GOV_SECRETS_CACHE` to a file in its own `tmp_path` and never touches `~/.cache/gov-os/`. At least:

- **Remembered:** files judged clean once are not scanned again on a second call with the same bytes, engine and rules (zero scans the second time, for content and for path names); a changed file's new bytes are scanned; the verdicts and order returned are the same as without a cache; two different projects (two temporary roots with the same rules) share the remembered results. The counts (`scan_counts()`) show scanned and remembered per kind, and agree with the stand-in's own count.
- **A secret is never answered clean:** a file holding the planted secret is dropped on every call, and is scanned every time (never answered from the cache); a path whose name holds it likewise. A text whose only match is row W2-L423's rule's match naming a real commit of the temporary repository (built as `test_commit_exemption.py` and W2-71 build it) is still let through, and is scanned again on every call (never remembered).
- **A rule change rescans everything:** after the project's `.gitleaks.toml` changes (a rule added), every text is scanned again; a changed gitleaks (a stand-in with other bytes, or another first on `PATH`) rescans everything; switching back to the first engine also rescans (the old results were forgotten, not kept beside the new).
- **Fail closed:** a cache file of garbage bytes, an empty file, a SQLite file of another form, a cache held locked by another connection, and a cache place that cannot be written (a read-only folder) each give correct verdicts with every text scanned, and the call neither raises nor hangs beyond a short wait; a gitleaks that cannot decide still raises even when the same content was remembered clean under another engine, and nothing is remembered for it.
- **The full-scan setting:** with `GOV_SECRETS_FULL_SCAN=1`, remembered texts are all scanned again; after it, a normal call is answered from the cache (the full scan refreshed it).
- **No content in the cache:** after scans of files with distinctive content and distinctive path names (and the planted secret), none of those bytes, names or the secret's text appear in the cache file or its `-wal` and `-shm` companions.
- **The default place:** in a child process whose environment has `HOME` set to a temporary folder, `GOV_SECRETS_CACHE` and `PYTEST_CURRENT_TEST` both unset, the cache is made at `<HOME>/.cache/gov-os/secrets-scan.sqlite`; with `GOV_SECRETS_CACHE` set to the empty string, no cache file is made anywhere and every call scans.
- **Concurrency:** several threads and two processes judging the same files at once against one cache file get the right verdicts and no error.
- The KPI line on the measured rebuild (seconds before and after) is the lead's measure, not yours: map it in the README to "measured by the lead", with the counts tests above as its testable part.

A test that already passes on the base code (it guards a behaviour the change must keep, such as a secret always dropped) is named in the README as a guard, with why.

## What you write

- Only inside `tests/acceptance/W2-107/` (no `__init__.py` named `secrets`, and no package or module named after a standard-library module). No throwaway implementation is left in the tree. If a KPI requires revising an earlier ticket's acceptance test, name it in your return; do not edit it.
- Behaviour through the public interfaces only (the two functions, the counts function, the environment variables and the cache file as a file), never internals. Deterministic, no network; mark nothing local_only unless it uses the dev tiers (it should not).
- A `README.md` that maps each KPI line (success and failure) to its tests, gives each test's expected red reason on the base code, names the guards, and says how the tests reach the code under test (through `PYTHONPATH`).
- **Red first:** run them, in the foreground, to the end, never with `-x`: `cd /home/usain/gov-os-worktrees/W2-107-tests && TMPDIR=/tmp/gov-os-lead-W2-107 PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests/acceptance/W2-107 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`; they fail on the base code for the reasons the README states. Also check collection of the whole tree stays clean: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-107-tests/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (quote its last line).
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in one commit, with the trailers in the final block:

    git commit -m "W2-107: acceptance tests for remembered gitleaks verdicts" --trailer "Task: DAEO-kiar" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-966, DEC-967" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`. After the commit, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the test count; the KPI lines with their tests; the red reason as you saw it (counts of failed and passed); the guards; every earlier test you would revise, with its reason; the `gov.__file__` line; the collection's last line; every guard refusal you met; whether you used `gov retrieve`, and any result under the implementation paths you were served; any package.

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so.
