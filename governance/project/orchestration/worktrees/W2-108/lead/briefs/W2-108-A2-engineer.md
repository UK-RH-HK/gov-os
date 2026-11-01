# Brief: engineer, W2-108 (DAEO-zoex), run 1

You are a fresh engineer. Ticket: `DAEO-zoex` (`W2-108`, "Retrieval checks the stores' freshness once per run"), profile STANDARD, a follow-up of W2-54 (`DAEO-0rfi`, closed; it stays closed). You work only in the worktree `/home/usain/gov-os-worktrees/W2-108` on branch `w2/W2-108`. You build the code to fulfil the ticket's specification and KPIs, never to make the tests pass.

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
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no tag. The only merge you make is the tests merge below, `--no-ff`.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch (pytest's `tmp_path`).
- Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never touch `tests/acceptance/**` (MR-3), and never `.gov-runtime/**` outside `.gov-runtime/scratch/**`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Install nothing (a tool you need is returned as a P1 package). No subagents that write. Never run `gov rebuild --no-embeddings`; you need no rebuild (the lead rebuilt this worktree's store). Never run `gov close`, `gov adopt` or `gov pause`.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Your scratch budget (DEC-898):** your share is 5 GB and 250,000 files and folders, outside the tracked tree. Use `TMPDIR=/tmp/gov-os-lead-W2-108` for every suite run (or the sandbox's own temp folder where `gov launch` sets one: keep it and count it). Keep pytest's own retention (no `--basetemp`). Remove what you make as soon as it is no longer needed. Measure it (`du -s --inodes`, `du -sh`) at the end and give the figures in your return.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- Never ask or notify the owner (no question box, no `owner-ping`): a question is a package in your return.

## What you read

- The ticket file `.tickets/DAEO-zoex.md` (read-only), whole: its KPI lines and its `allowed_paths`.
- The package `governance/project/orchestration/packages/P-W2-54-LOAD-1.md` (the measured profile: 1,252 s at load 40 to 70; about 460 s of freshness checks repeated on each of 328 calls).
- The sources in `docs/DECISION_REGISTER.md`: DEC-969, DEC-968, DEC-966 (item 4), DEC-860, DEC-424; and DEC-342, DEC-344, DEC-322, DEC-381, DEC-135.
- The code you touch: `src/gov/retrieval/semantic.py` (`search`, `_status`, `_wanted`, `embedded`, `query_vector`) and `src/gov/retrieval/lexical.py` (`freshness`, `_tracked`); and, read only, how `src/gov/context/context_check.py`, `src/gov/context/__init__.py` and `src/gov/retrieval/retrieve.py` call retrieval.

## What to build (the KPI lines)

1. Within one process, the semantic store's status (which files should be embedded and whether the store holds them) and the lexical index's freshness are worked out once per store and tree, keyed by the store's fingerprint and the tree's head, and reused by every later retrieval call in that process. Failure: a freshness or status check repeated on every call within one process.
2. Every answer is unchanged: for the same store and tree, each retrieval call returns the same bundle, facets and stopping reason as before, item for item. Failure: any bundle, facet or stopping reason different from before.
3. A change is still seen: a store rebuilt, a file changed or a head moved between two calls is seen as such (a new key, a fresh check); a process that cannot read the fingerprint or the head checks every time, never reuses an old answer. Failure: a stale answer reused after the store, a file or the head changed. **Note:** the lexical freshness reads each tracked file as it stands in the working tree (DEC-344), so "a file changed" includes a tracked file edited and not committed, which does not move the head: the key must see that too, by something cheaper than hashing every file, or the KPI's failure line is hit. Whatever the semantic status depends on besides the store (the path map's namespaces, for example) is in its key too. Never make a check fail open: when in doubt, check.
4. The measure is the lead's and the record is yours (below).

**Scope (the lead's decision for this run):**
- You change **only the freshness and status functions** of `src/gov/retrieval/semantic.py` and `src/gov/retrieval/lexical.py` (and whatever small private helper they need, beside them). W2-13 and W2-32 hold the rest of those files and of `src/gov/retrieval/` (both open, not running): no change to the searches, the embedder's client, the query-vector cache, fusion or the rest.
- **Not done:** W2-54's time limits are not raised and its tests are not changed (DEC-969). The query-embedding batching is not done here.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines; about 80 lines are estimated.
- Your builder tests go in `tests/unit/retrieval/test_w2_108*.py`, as regression evidence (test-driven: your own unit tests): the count of checks per process, an unchanged answer, and each change (store rebuilt, file edited uncommitted, head moved, key unreadable) seen. Planted repositories in `tmp_path`; deterministic, no network (a stand-in for the embedder on the loopback interface, or a planted store; skip with its reason when `sqlite_vec` is absent).
- Run them: `TMPDIR=/tmp/gov-os-lead-W2-108 PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -m pytest tests/unit/retrieval -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, to the end, never with `-x`. Also run the existing retrieval and context unit tests you can reach (`tests/unit/retrieval`, `tests/unit/context` if present) to see nothing else moved.
- Do **not** run `python3 -m gov.context.context_check` on this worktree or anywhere: the lead measures it outside the sandbox, at measured loads, before and after your change.

## The acceptance tests (DEC-963)

The independent test designer writes them in parallel, in its own worktree. When `/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/TESTS-READY` exists — at your next step, or when you have built and committed — run `git merge --no-ff w2/W2-108-tests -m "Merge w2/W2-108-tests into w2/W2-108: W2-108's acceptance tests" --trailer "Task: DAEO-zoex" --trailer "Role: engineer"` in this worktree (if your git refuses `--trailer` on a merge, put the two trailer lines as the message's final paragraph with `-m` twice), and run them once, reading results only: `TMPDIR=/tmp/gov-os-lead-W2-108 PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -m pytest tests/acceptance/W2-108 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`. Report names, pass or fail, and failure messages only. A test you think is wrong is returned as a package, never edited and never worked around. If TESTS-READY has not appeared by the time you have committed, say so and return: the lead merges and runs them.

## The research record (KPI 4): `docs/research/W2-108-freshness-once.md`

Write it as a skeleton now, with your design (what is keyed by what, why each change is seen, what happens when a key cannot be read), and leave a section "Measure" for the figures. The lead runs the measure (`python3 -m gov.context.context_check` on one rebuilt store, before and after, at two measured loads, with cProfile's time in the freshness checks and in query embedding) and gives you the figures in a resumed turn; you then fill in that section, with the verdict on whether the query-embedding batching is still needed, and commit it.

## Commits

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths (`git commit -m "<subject>" -- <paths>`), with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-zoex" --trailer "Role: engineer" --trailer "Implements: DEC-969" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>

`Implements:` holds decision ids the register holds (`DEC-n`) or Contract ids (`CAP-n`), never another word. Commit your code and unit tests before running any long suite. After each commit check `git log --oneline -2` and `git status --short`.

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

After the twelve fields: the sandbox check's result; your commits' 12-digit hashes; the lines added and removed; the design in a few lines (the keys, and how each change is seen); whether you merged the tests and their results; whether you used `gov retrieve` and how often; the read refusals you met (DEC-849); a section `guard_refusals:` (one line per refusal: time | the command's form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and your scratch measure. Refused twice for the same call: stop and say so.
