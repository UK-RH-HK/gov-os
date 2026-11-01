# Brief: engineer, DAEO-qzrq (W2-123), STANDARD — batch 2

You are a fresh engineer. Ticket: DAEO-qzrq (W2-123), profile STANDARD. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-123` on branch `w2/W2-123`. You build the ticket's code to fulfil its specification
and KPI lines, never to make tests pass (DEC-957). An earlier engineer built the ticket's code in commit
`e404e268f3fb` (`src/gov/retrieval/ollama.py`, `tests/unit/retrieval/test_w2_123_embedding_cap.py`); read it there.

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
  only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for
  verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This worktree
  has no store yet (the lead rebuilds it after the last batch), so ask the integration branch's store (a read):
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`; never run a rebuild here.
  **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then
  `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph
  tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole
  graph.
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
  this repository). No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in
  `~/gov-os-workbench`. Inside a session `.gov-runtime/freeze` may show as a placeholder device file: conclude
  nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your budget (DEC-898):** 4 GB and 200,000 files and folders outside the tracked tree. Inside the sandbox
  `/tmp/gov-os-lead-W2-123` is read-only, so keep the sandbox's own `TMPDIR` (do not set another) and count it; if
  pytest still writes `pytest-of-usain/` into the worktree, leave it and name it. Never `--basetemp`. Measure
  (`du -sh` and `du -s --inodes`) at the start and the end; give the figures in `evidence`.
- **Heavy steps (DEC-979 D1, DEC-1008):** one test file is not heavy: run test files one at a time. You run no
  rebuild. Never run `gov rebuild --no-embeddings` on a real tree (DEC-719).
- **Never the real embedding servers:** your tests never send a request to, stop, or start anything at
  127.0.0.1:11434 or 127.0.0.1:11435, and never run the real `ollama`.
- Install nothing: an install is a P1 package in your return. No push, merge, rebase or tag. Never write
  `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`. No subagents that write. Never
  ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command, stop
  and return it.

## What to do

1. **The acceptance tests are merged** (`.gov-runtime/scratch/lead/TESTS-READY` exists). Run them once, reading
   results only, through
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -m gov.cli.main accept DAEO-qzrq --json` only (never
   `pytest` on `tests/acceptance/`), and report pass or fail per KPI line and the counts. The evidence file (KPI 3)
   is written by a later batch from the lead's measure; its line may be red now.
2. **The red builder test, decided by the lead (a P3 reading, logged for the CTO):**
   `tests/unit/ollama/test_ollama.py::test_a_missing_executable_degrades_with_one_warning_and_does_not_raise` (W1-18)
   expects today's result exactly when no executable can be found. KPI 1 states the settings of a start; where no
   executable is found nothing can be started, so there are no settings to state. Build it so: **when no executable
   is found (and the server does not answer), the result is today's, with no `settings` key**; in every other case
   (a start made or attempted with an executable, the server already answering, an unreadable value) the result is
   as the lead's interface says (`settings` an object, or `None` for an unreadable value; `CONFIG_INVALID` still
   comes first). Add a unit test of your own for it. Do not edit `tests/unit/ollama/`.
3. Run your unit tests and the existing unit files one file at a time, to their end, never with `-x`:
   `tests/unit/retrieval/test_w2_123_embedding_cap.py`, `tests/unit/ollama/test_ollama.py`, and each file in
   `tests/unit/retrieval/`, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -m pytest <file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
4. Proportion (DEC-135): nothing else changes. Never make a gate decision fail open.

## What you write

- Only `src/gov/retrieval/ollama.py` and `tests/unit/retrieval/test_w2_123*`. You do not write
  `docs/changes/W2-123-evidence.md` in this batch.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only your paths, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-qzrq" --trailer "Role: engineer" --trailer "Implements: DEC-1014, DEC-1017" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then run `git log --oneline -2` and `git status --short` and quote them. After the commit, run `gov accept` once more
(as in step 1) and report it.

## Return

Your sandbox check (first); your commit's hash (12 digits); the files changed; the lines added and removed; both
`gov accept` results per KPI line with counts; the unit tests you ran with their results; the `gov retrieve` queries
you ran; the read refusals you met; anything you were refused or could not settle, as a package (question, why now,
options, impact, reversibility, cost, recommendation, confidence).

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
