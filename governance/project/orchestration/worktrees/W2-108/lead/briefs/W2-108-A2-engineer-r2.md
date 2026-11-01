# Brief: engineer, W2-108 (DAEO-zoex), repair

You are a fresh engineer. Ticket: `DAEO-zoex` (`W2-108`, "Retrieval checks the stores' freshness once per run"), profile STANDARD, a follow-up of W2-54 (`DAEO-0rfi`, closed; it stays closed). You work only in the worktree `/home/usain/gov-os-worktrees/W2-108` on branch `w2/W2-108`. The ticket's implementation is already on the branch; its acceptance tests are merged and some are red. You repair the implementation so that it fulfils the ticket's specification and KPIs; you build to the spec, never to make the tests pass.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zoex','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK (in this worktree).
If (a) wrote the file or (b) failed, stop there and return, saying which.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-zoex`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-108` and `w2/W2-108`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src` set **per command** (never in a session's `--settings` env). Show `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads open, writes closed (DEC-820, Policy 2).** You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-108/`** (in this worktree, on the branch `w2/W2-108-tests` or in `/home/usain/gov-os-worktrees/W2-108-tests`), by any tool; you may run those tests and see their names, results and failure messages, never their source; **(d) the hidden half of any evaluation set**, by whoever is measured by it.
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead (`src/gov/retrieval/`, `tests/unit/retrieval/`). Count the refusals you met and name them in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (`> "$OUT/x"`, `mkdir -p $D/t`, `sed -i` on a `$VAR` path); no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `.gov-runtime/scratch/` with the Write tool, and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch (pytest's `tmp_path`).
- Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never touch `tests/acceptance/**` (MR-3), and never `.gov-runtime/**` outside `.gov-runtime/scratch/**`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Install nothing (a tool you need is returned as a P1 package). No subagents that write. Never run `gov rebuild` (with or without `--no-embeddings`); the lead rebuilds. Never run `gov close`, `gov adopt` or `gov pause`.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Your scratch budget (DEC-898):** your share is 5 GB and 250,000 files and folders, outside the tracked tree. `/tmp/gov-os-lead-W2-108` is read-only inside the sandbox: keep the sandbox's own temp folder (`$TMPDIR` as `gov launch` sets it) for every suite run, and count it. Keep pytest's own retention (no `--basetemp`). Remove what you make as soon as it is no longer needed. Measure it (`du -s --inodes`, `du -sh`) at the end and give the figures in your return.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- Never ask or notify the owner (no question box, no `owner-ping`): a question is a package in your return.

## What you read

- The ticket file `.tickets/DAEO-zoex.md` (read-only), whole: its KPI lines and its `allowed_paths`.
- The package `governance/project/orchestration/packages/P-W2-54-LOAD-1.md` (the measured profile: 1,252 s at load 40 to 70; about 460 s of freshness checks repeated on each of 328 calls: `semantic._status` 315 s, inside it `_wanted` 228 s; `lexical.freshness` 148 s, "the tracked files listed on each of 656 calls").
- The sources in `docs/DECISION_REGISTER.md`: DEC-969, DEC-968, DEC-966 (item 4), DEC-860, DEC-424; and DEC-342, DEC-344, DEC-322, DEC-381, DEC-135.
- The code on the branch: `src/gov/retrieval/semantic.py` and `src/gov/retrieval/lexical.py` (the ticket's change is `git diff f6af39c1665b HEAD -- src/`), `tests/unit/retrieval/test_w2_108_freshness_once.py`, `docs/research/W2-108-freshness-once.md`; and, read only, how `src/gov/context/context_check.py`, `src/gov/context/__init__.py` and `src/gov/retrieval/retrieve.py` call retrieval.

## What the ticket requires (the KPI lines)

1. Within one process, the semantic store's status (which files should be embedded and whether the store holds them) and the lexical index's freshness are worked out once per store and tree, keyed by the store's fingerprint and the tree's head, and reused by every later retrieval call in that process. Failure: a freshness or status check repeated on every call within one process.
2. Every answer is unchanged: for the same store and tree, each retrieval call returns the same bundle, facets and stopping reason as before, item for item. Failure: any bundle, facet or stopping reason different from before.
3. A change is still seen: a store rebuilt, a file changed (DEC-344: a tracked file is read as it stands in the working tree, so an uncommitted edit counts) or a head moved between two calls is seen as such (a new key, a fresh check); a process that cannot read the fingerprint or the head checks every time, never reuses an old answer. Failure: a stale answer reused after the store, a file or the head changed. Never make a check fail open: when in doubt, check.
4. The measure is the lead's and the record is yours (below).

**Scope:** you change only the freshness and status functions of `src/gov/retrieval/semantic.py` and `src/gov/retrieval/lexical.py` (and small private helpers beside them). W2-13 and W2-32 hold the rest of those files and of `src/gov/retrieval/`: no change to the searches, the embedder's client, the query-vector cache, fusion or the rest. W2-54's time limits are not raised and its tests are not changed. The query-embedding batching is not done here. Proportion (DEC-135): no code beyond the KPI lines.

## The failing output (the acceptance run of 2026-10-31 09:49 on this branch's head, `8c3db504`: 7 failed, 19 passed, 1 skipped)

```
FAILED tests/acceptance/W2-108/test_w2_108_once.py::test_lexical_freshness_is_worked_out_once
FAILED tests/acceptance/W2-108/test_w2_108_once.py::test_lexical_search_checks_freshness_once
FAILED tests/acceptance/W2-108/test_w2_108_once.py::test_semantic_status_is_worked_out_once
FAILED tests/acceptance/W2-108/test_w2_108_once.py::test_retrieve_checks_both_stores_once
FAILED tests/acceptance/W2-108/test_w2_108_once.py::test_every_kind_of_call_shares_one_check
FAILED tests/acceptance/W2-108/test_w2_108_once.py::test_an_unchanged_tree_with_an_uncommitted_edit_is_checked_once
FAILED tests/acceptance/W2-108/test_w2_108_once.py::test_this_repositorys_store_is_checked_once
SKIPPED [1] tests/acceptance/W2-108/test_w2_108_unchanged.py:140: the semantic facet of /home/usain/gov-os-worktrees/W2-108 is unavailable here (stale): no embedder answers, or the store holds no current vectors

test_lexical_freshness_is_worked_out_once:
AssertionError: the freshness check was worked out again in later calls of the same process, on an unchanged store and tree (call number, listing/hashing git commands): [(2, 1), (3, 1), (4, 1), (5, 1)]
  call 1: 3 listing/hashing git command(s), 0 path-map read(s); git: ['-C <tmp>/project rev-parse HEAD', '-C <tmp>/project ls-files -z', '-C <tmp>/project ls-files -z', '-C <tmp>/project hash-object --stdin-paths']
  call 2: 1 listing/hashing git command(s), 0 path-map read(s); git: ['-C <tmp>/project rev-parse HEAD', '-C <tmp>/project ls-files -z']
  call 3: 1 listing/hashing git command(s), 0 path-map read(s); git: ['-C <tmp>/project rev-parse HEAD', '-C <tmp>/project ls-files -z']

test_lexical_search_checks_freshness_once:
AssertionError: the freshness check was worked out again in later calls of the same process, on an unchanged store and tree (call number, listing/hashing git commands): [(2, 1), (3, 1), (4, 1), (5, 1)]
  (calls as above)

test_semantic_status_is_worked_out_once:
AssertionError: the freshness check was worked out again in later calls of the same process, on an unchanged store and tree (call number, listing/hashing git commands): [(2, 1), (3, 1), (4, 1), (5, 1)]
  call 1: 3 listing/hashing git command(s), 1 path-map read(s); git: [rev-parse HEAD, ls-files -z, ls-files -z, hash-object --stdin-paths]
  call 2: 1 listing/hashing git command(s), 0 path-map read(s); git: [rev-parse HEAD, ls-files -z]

test_retrieve_checks_both_stores_once:
AssertionError: the freshness check was worked out again in later calls of the same process, on an unchanged store and tree (call number, listing/hashing git commands): [(2, 2), (3, 2), (4, 2), (5, 2)]
  call 1: 4 listing/hashing git command(s), 2 path-map read(s); git: [rev-parse HEAD, ls-files -z, ls-files -z, hash-object --stdin-paths, rev-parse HEAD, ls-files -z]
  call 2: 2 listing/hashing git command(s), 1 path-map read(s); git: [rev-parse HEAD, ls-files -z, rev-parse HEAD, ls-files -z]

test_every_kind_of_call_shares_one_check:
AssertionError: 8 calls on one unchanged store and tree listed the tracked files 11 times and hashed them 1 times; once per store (the lexical index, the vectors) is at most twice

test_an_unchanged_tree_with_an_uncommitted_edit_is_checked_once:
AssertionError: the freshness check was worked out again in later calls of the same process, on an unchanged store and tree (call number, listing/hashing git commands): [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1)]
  call 2: 1 listing/hashing git command(s), 0 path-map read(s); git: [rev-parse HEAD, ls-files -z]

test_this_repositorys_store_is_checked_once:
AssertionError: the freshness check was worked out again in later calls of the same process, on an unchanged store and tree (call number, listing/hashing git commands): [(2, 2), (3, 2), (4, 2)]
  call 1: 4 listing/hashing git command(s), 1 path-map read(s); git: ['-C /home/usain/gov-os-worktrees/W2-108 rev-parse HEAD', '... ls-files -z', '... ls-files -z', '... hash-object --stdin-paths', '... rev-parse HEAD', '... ls-files -z']
  call 2: 2 listing/hashing git command(s), 1 path-map read(s); git: ['... rev-parse HEAD', '... ls-files -z', '... rev-parse HEAD', '... ls-files -z']
```

(`<tmp>` stands for each test's temporary folder.)

## What you do

- Repair the implementation; keep or extend the builder tests in `tests/unit/retrieval/test_w2_108*.py`; update the design section of `docs/research/W2-108-freshness-once.md` to match (leave its "Measure" section for the lead's figures).
- Run the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -m pytest tests/unit/retrieval -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, to the end, never with `-x`, plus the other retrieval and context unit suites you can reach (`tests/unit/semantic`, `tests/unit/context`, `tests/unit/retrieve`).
- Commit (below), then run the acceptance tests once, reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -m pytest tests/acceptance/W2-108 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`. Report names, pass or fail, and failure messages only. A test you think is wrong is returned as a package, never edited and never worked around.
- Do **not** run `python3 -m gov.context.context_check`: the lead measures it outside the sandbox.

## Commits

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-zoex" --trailer "Role: engineer" --trailer "Implements: DEC-969" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>

`Implements:` holds decision ids the register holds (`DEC-n`) or Contract ids (`CAP-n`), never another word. After each commit check `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

After the twelve fields: the sandbox check's result; your commits' 12-digit hashes; the lines added and removed (code, tests, record) against the ticket's start `f6af39c1665b`; the design in a few lines (the keys, and how each change is seen); the acceptance results; whether you used `gov retrieve` and how often; the read refusals you met (DEC-849); a section `guard_refusals:` (one line per refusal: time | the command's form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and your scratch measure. Refused twice for the same call: stop and say so.
