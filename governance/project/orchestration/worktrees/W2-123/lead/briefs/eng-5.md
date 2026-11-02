# Brief: engineer, DAEO-qzrq (W2-123) run 2, STANDARD — resolve the merge of the DEC-1033 emergency patch

You are a fresh engineer. Ticket: DAEO-qzrq (W2-123), profile STANDARD, run 2. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-123` on branch `w2/W2-123`. **The lead has started a merge of `w2/integrate` into
this branch and left it uncommitted:** `src/gov/retrieval/ollama.py` has conflict markers; everything else merged
cleanly (`src/gov/retrieval/semantic.py` included). You resolve `ollama.py`, keeping both sides' behaviour, test it,
and stage it. **You do not commit:** the lead commits the merge after you return. Keep it small.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-qzrq','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-qzrq`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-123` and `w2/W2-123`).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. A command that could outlive the Bash tool's ten minutes is not run. Return
  only after your resolution is staged (you make no commit in this batch).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for
  verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random:
  `cd /home/usain/gov-os-worktrees/W2-123 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -m gov.cli.main retrieve "<question>" --json`
  (this worktree's store is from run 1 and may be a little behind the merge; for what changed, read the files). Never
  run a rebuild here. **Never one giant query or context (DEC-860):** a large question is taken in batches
  (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)**
  uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a
  load of the whole graph.
- **Policy 2 (DEC-820):** reads are open, with four refusals: (a) secrets and keys, never printed; (b) the contents of
  the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
  (c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-123/` by any tool, in this worktree,
  in `/home/usain/gov-os-worktrees/W2-123-tests` or in git history (you may run those tests and see their names,
  results and failure messages, through `gov accept` only); (d) the hidden half of any evaluation set, by whoever is
  measured by it. Writes stay inside your paths.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the
  repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named
  folders instead, and count the refusals in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; anything longer goes in a script file under
  `/home/usain/gov-os-worktrees/W2-123/.gov-runtime/scratch/eng/` written with the Write tool, then run. A refused
  form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of
  this repository); copy single named files only, never `governance/project/`. Tests that need a repository build a
  temporary one from scratch under pytest's `tmp_path`. No clone, copy or programme file under any `.gov-runtime/`
  folder (DEC-673). Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a
  session `.gov-runtime/freeze` may show as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your budget (DEC-898):** 8 GB and 400,000 files and folders outside the tracked tree (your share of the ticket's
  20 GB and 1,000,000). Set `TMPDIR=/tmp/gov-os-lead-W2-123` on every test run (where `gov launch`'s sandbox sets its
  own temp folder, keep that one and count it). Keep pytest's own temp retention; never `--basetemp`. Clean what you
  make as soon as it is no longer needed. Measure (`du -sh` and `du -s --inodes` of `.gov-runtime/scratch/eng/` and
  your temp use) at the start and the end; give the figures in `evidence`.
- **Heavy steps (DEC-979 D1, DEC-1008):** one test or one test file is not heavy. More than one test file runs as
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <the pytest command>`.
  **You run no rebuild of this worktree or of any real tree;** the lead runs those. Never run
  `gov rebuild --no-embeddings` on a real tree (DEC-719).
- **Never the real embedding servers:** your tests never send a request to, stop, or start anything at
  127.0.0.1:11434 or 127.0.0.1:11435, and never run the real `ollama`. Every test sets `HOME`, `OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST` (free ports on 127.0.0.1) and `GOV_OLLAMA_BIN` (a planted executable under `tmp_path`), and
  stands up its own stand-in endpoint that times out the first one, two or three tries (`tests/unit/ollama/` and
  `tests/unit/retrieval/` show how stand-ins are made). Lower `TIMEOUT_S` and `RETRY_WAITS_S` in your tests so they
  run fast.
- Install nothing: an install is a P1 package in your return. No push, merge, rebase or tag. Never write
  `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`. No subagents that write. Never
  ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command, stop
  and return it.

## What you read

- The ticket file `.tickets/DAEO-qzrq.md` as the merge leaves it (read-only): success-7 now says the query server
  starts "with the GPU visible (DEC-1033, replacing DEC-798)"; success-8 says `ensure_query_available` starts the
  query server without hiding the GPU (no `CUDA_VISIBLE_DEVICES=-1`).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-1033 (it replaces DEC-798's CPU-only query embedder), DEC-1032,
  DEC-1014, DEC-1017, DEC-866.
- The two sides of the conflict: `git diff 6ed6a5ae^1 6ed6a5ae -- src/gov/retrieval/ollama.py` (the emergency patch:
  `NO_GPU` removed, `ensure_query_available` no longer adds it, docstrings say the GPU is left visible) and this
  branch's `ollama.py` (`git show HEAD:src/gov/retrieval/ollama.py`: run 1's capped start, which adds `NO_GPU` for
  the query server in its own start path, about line 207, and in `ensure_query_available`).
- The unit tests that read the query server's environment: `tests/unit/retrieval/test_w2_123_embedding_cap.py` (run 1's,
  yours to update), `tests/unit/retrieval/test_emg_query_device.py` and `tests/unit/retrieval/test_semantic_cpu_embedder.py`
  (the patch's; not in your paths: read only, they must pass).

## What to resolve

- **Keep both:** run 1's capped start exactly as it is for both servers (the configured or default CPU list, niceness
  and `OLLAMA_NUM_PARALLEL`, applied in the started process and inherited by its children; an unreadable value
  refuses the start; the `settings` in the result; the probe and the safe restart), **and** the patch's rule: the
  query server is started with the GPU left visible. No `CUDA_VISIBLE_DEVICES=-1` is added anywhere by the code (not
  in `ensure_query_available`, not in run 1's start path, not in a safe restart), and the caller's own environment
  reaches the daemon as it is. `NO_GPU` goes, as the patch removed it, unless something still needs the name (say so).
- Docstrings and comments follow the patch's wording (the query embedder, DEC-1033), with run 1's cap described.
- No other behaviour changes. `semantic.py` merged cleanly: do not edit it.
- **The cap on an automatic start (the CTO asks):** confirm, by a unit test of your own with a planted executable,
  that when the code itself starts the query server (`ensure_query_available` with nothing listening), the started
  process runs with the configured (or default) CPU list and niceness, the same as the shared server; say so in your
  return with the test's name.

## What you write

- Only `src/gov/retrieval/ollama.py` (the resolution) and `tests/unit/retrieval/test_w2_123*` (update run 1's unit
  tests that expected the hidden GPU; add the automatic-start cap test). Nothing else. If anything else needs a
  change, return a package naming it.
- Proportion (DEC-135). Say how many lines the resolution changed against `HEAD`.
- Check that no conflict marker is left anywhere: `git diff --check` and `grep -n "^<<<<<<<\|^>>>>>>>" src/gov/retrieval/ollama.py`.
- Run, to their end, never with `-x`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src TMPDIR=/tmp/gov-os-lead-W2-123 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests/unit/ollama tests/unit/retrieval tests/unit/semantic -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (if `/tmp/gov-os-lead-W2-123` is read-only in your sandbox, use the sandbox's own `TMPDIR` and say so).

## Stage, do not commit

1. `git add src/gov/retrieval/ollama.py` and your unit test files. **Do not run `git commit` or `git merge`:** the lead
   commits the merge. Then `git status --short` and quote it (the merge's other files appear staged; that is the
   lead's merge).
2. Do not run the acceptance tests in this batch: the lead runs `gov accept` after the merge is committed and the
   designer's revised tests are merged.

## Return

Your sandbox check (first); your commit's hash (12 digits); the files changed; the lines added and removed; how a
time-out is told from another failure; how `retries` and the reason are formed; the tests you ran with their results;
the `gov accept` result if run; each existing test or caller whose expectation you had to keep (and how); the
`gov retrieve` queries you ran; the read refusals you met; anything you were refused or could not settle, as a
package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them:

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
