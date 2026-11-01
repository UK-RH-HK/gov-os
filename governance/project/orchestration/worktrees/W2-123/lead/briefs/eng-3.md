# Brief: engineer, DAEO-qzrq (W2-123), STANDARD — batch 3 (the evidence and the measured defaults)

You are a fresh engineer. Ticket: DAEO-qzrq (W2-123), profile STANDARD. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-123` on branch `w2/W2-123`. Earlier engineers built the ticket's code (commits
`e404e268f3fb` and `3dabcdaca633`: `src/gov/retrieval/ollama.py`, `tests/unit/retrieval/test_w2_123_embedding_cap.py`);
read them there. The lead has measured KPI 3 in its own session; you write its evidence and set the measured defaults.

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
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -m gov.cli.main retrieve "<question>" --json` (this
  worktree's store, rebuilt by the lead). **Never one giant query or context (DEC-860):** a large question is taken
  in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question
  (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and
  targeted, never a load of the whole graph.
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
- Never copy the repository or a folder of it. No clone, copy or programme file under any `.gov-runtime/` folder
  (DEC-673). Never write in `~/gov-os-workbench`. Inside a session `.gov-runtime/freeze` may show as a placeholder
  device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token. In the evidence file
  too, name commits by 12 digits.
- **Your budget (DEC-898):** 2 GB and 100,000 files and folders outside the tracked tree. Inside the sandbox
  `/tmp/gov-os-lead-W2-123` is read-only: keep the sandbox's own `TMPDIR` and count it; if pytest writes
  `pytest-of-usain/` into the worktree, leave it and name it. Never `--basetemp`. Measure (`du -sh` and
  `du -s --inodes`) at the start and the end; give the figures in `evidence`.
- **Heavy steps (DEC-979 D1, DEC-1008):** one test file is not heavy: run test files one at a time. You run no
  rebuild and no measurement. Never run `gov rebuild --no-embeddings` on a real tree (DEC-719).
- **Never the real embedding servers:** your tests never send a request to, stop, or start anything at
  127.0.0.1:11434 or 127.0.0.1:11435, and never run the real `ollama`.
- Install nothing: an install is a P1 package in your return. No push, merge, rebase or tag. Never write
  `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`. No subagents that write. Never
  ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command, stop
  and return it.

## What you read

- The ticket file `.tickets/DAEO-qzrq.md` (its KPI 3 line above all) and DEC-1014, DEC-1017, DEC-996 item 3 in
  `docs/DECISION_REGISTER.md`.
- **The lead's figures:** `/home/usain/gov-os-worktrees/W2-123/.gov-runtime/scratch/lead/measure/FIGURES.md` (the
  tables, the method, the findings and the chosen setting), with the raw records beside it in that folder
  (`sweep-1.jsonl`, `cases-2.jsonl`, `det_matrix-2242.jsonl`, `np_check-2314.log`, the measuring scripts) and the
  cold rebuild's stage record named in `FIGURES.md`. Use only these figures; invent none, round none beyond one
  decimal, and say where each comes from.

## What to do

1. **Write `docs/changes/W2-123-evidence.md`** (new), the implementer's evidence for KPI 3 (DEC-996 item 3 A). It holds,
   in this order:
   - what was measured, how and where (the private server instance, its port, the binary and model, the cap applied
     in the started process as the ticket's start applies it, the rebuild's request form replayed, the chunk counts,
     the machine's load at the time, the commit whose code was measured);
   - **the table of the 16 measured cases** of `FIGURES.md` (parallel requests 1, 2, 4 and 8; under the CPU cap and
     without it; alone and with three rebuilds' embedding at once), one row each, with its chunks per second and its
     semantic stage in seconds, the server's cores busy and its determinism check;
   - the further figures of `FIGURES.md` (what the runner was really started with; the cap and the niceness apart;
     the determinism matrix; the cold rebuild's semantic stage on the shared server);
   - a line that begins exactly `Chosen setting:` and names the parallel requests and the CPU cap chosen and why, as
     `FIGURES.md` gives it;
   - what this means and what it does not show (the findings of `FIGURES.md`), in plain words.
2. **Set the measured defaults** in `src/gov/retrieval/ollama.py` as `FIGURES.md`'s "Defaults" part says, each named
   constant's comment naming its source (this evidence file and its figure). Nothing of this machine (its CPU
   numbers, its ports) is written in the code. If a default stays as it is, only its comment changes.
3. Run your unit tests and the existing unit files one file at a time, to their end, never with `-x`:
   `tests/unit/retrieval/test_w2_123_embedding_cap.py`, `tests/unit/ollama/test_ollama.py` and each file in
   `tests/unit/retrieval/`, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -m pytest <file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
4. Commit (below), then run the acceptance tests once, reading results only, through
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src python3 -m gov.cli.main accept DAEO-qzrq --json` only (never
   `pytest` on `tests/acceptance/`), and report pass or fail per KPI line and the counts.

## What you write

- Only `docs/changes/W2-123-evidence.md`, `src/gov/retrieval/ollama.py` and `tests/unit/retrieval/test_w2_123*`.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only your paths, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-qzrq" --trailer "Role: engineer" --trailer "Implements: DEC-1014, DEC-1017" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your sandbox check (first); your commit's hash (12 digits); the files changed; the lines added and removed; the
`gov accept` result per KPI line with counts; the unit tests you ran with their results; the `gov retrieve` queries
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
