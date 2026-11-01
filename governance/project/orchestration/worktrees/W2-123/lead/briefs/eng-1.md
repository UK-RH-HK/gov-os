# Brief: engineer, DAEO-qzrq (W2-123), STANDARD — batch 1

You are a fresh engineer. Ticket: DAEO-qzrq (W2-123), profile STANDARD. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-123` on branch `w2/W2-123`. You build the ticket's code to fulfil its specification
and KPI lines, never to make tests pass (DEC-957).

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
  has no store yet (its rebuild waits for a heavy-job slot; the lead runs it after your batch), so ask the integration
  branch's store, which holds the same code you start from (a read):
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`; and never run a rebuild here.
  **Never
  one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then
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
  **You run no rebuild of this worktree or of any real tree:** the lead runs those, and the lead measures KPI 3 in its
  own session (inside your sandbox `gov` would only reach a private CPU Ollama, DEC-261). Never run
  `gov rebuild --no-embeddings` on a real tree (DEC-719).
- **Never the real embedding servers:** your tests never send a request to, stop, or start anything at
  127.0.0.1:11434 or 127.0.0.1:11435, and never run the real `ollama`. Every test sets `HOME`, `OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST` in the `env=` it passes (free ports on 127.0.0.1), `GOV_OLLAMA_BIN` to a planted executable
  under `tmp_path`, and stands up its own stand-in endpoint (`tests/unit/ollama/test_ollama.py` shows how). A
  safe-restart test stops only a process the test started.
- Install nothing: an install is a P1 package in your return. No push, merge, rebase or tag. Never write
  `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`. No subagents that write. Never
  ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command, stop
  and return it.

## What you read

- The ticket file `.tickets/DAEO-qzrq.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-1014 (items 4 and 6), DEC-1015 (item 2), DEC-1017, DEC-1010
  item 7, DEC-1011, DEC-982, DEC-996 item 3, DEC-260, DEC-261, DEC-798, DEC-135.
- The package `governance/project/orchestration/packages/ACT-OLLAMA-CAP-1.md` (the cap set by hand today, why, and
  how a restart loses it).
- W2-20's ticket `.tickets/DAEO-r30l.md` (its KPI line on the durable cap of both servers, which your start reads).
  W2-20 has not landed: its configuration file has no reader on `w2/integrate` yet; you read the one section S1
  names, in your own code, and nothing else of that file.
- The code the ticket touches: `src/gov/retrieval/ollama.py`, how `src/gov/retrieval/semantic.py` calls it and embeds
  (its model, `BATCH`, its `/api/embed` requests, float32 BLOBs), and every existing test that plants an Ollama
  executable or reads the start's result (`tests/unit/ollama/test_ollama.py`, `tests/unit/retrieval/`, and the
  acceptance suites that use `GOV_OLLAMA_BIN` or `ensure_available`, found by name with `grep -l`, which you may run
  but whose files under `tests/acceptance/W2-123/` you never open). They must stay green: the daemon's command line
  stays `<executable> serve`, so apply the cap in the started process itself (it is inherited by its children),
  not by a wrapper command those tests would see.

## What to build

The ticket's KPI lines, as they stand in its file. The lead fixes this outside so that you and the independent test
designer, who works in parallel and never sees your code, build to the same interface (a lead's reading, logged for
the CTO; if any of it cannot be built as stated, return a package rather than build something else):

{{INTERFACE_SPEC}}

Further, for you:

- **The defaults (KPI 1, KPI 4).** Until the lead's measure (KPI 3) chooses them, use the shared server's `parallel`
  1, the query server's `parallel` 1, a CPU count of 8 (ACT-OLLAMA-CAP-1's cap, as a count, not as CPU numbers) and
  `nice` 10 for both, and a probe's `probe_slow_s` and `probe_hung_s` of your choosing, each a named constant with a
  comment that names its source; a later batch sets the measured values. Say which you chose.
- **KPI 2.** Build `check_determinism` as S5 says; the lead runs it on the real embedder during the measure.
- **KPI 3** is measured by the lead in its own session, with your code, on a server instance of its own. You do not
  write `docs/changes/W2-123-evidence.md` in this batch; a later batch writes it from the lead's figures.
- **The failure line:** a parallel setting that changes a vector is refused by the check; a start is never uncapped
  (an unreadable value refuses the start); no setting without its measure.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/retrieval/ollama.py`, `tests/unit/retrieval/test_w2_123*`. If
  the work needs another path, return a package naming it; never write outside.
- Your own unit tests (test-driven) in `tests/unit/retrieval/test_w2_123*.py`, as regression evidence only, with
  planted executables and stand-in endpoints.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. Never make a gate decision fail open: every
  failure KPI must still refuse. About 80 lines were estimated before the probe and restart lines were added; say how
  many you wrote.
- Run your unit tests, `tests/unit/ollama/` and `tests/unit/retrieval/` to their end, never with `-x`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src TMPDIR=/tmp/gov-os-lead-W2-123 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests/unit/ollama tests/unit/retrieval -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Commit, then the acceptance tests

1. Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file;
   if one is there, stop and return. Never `--no-verify`. Commit only your paths, with the trailers in the final
   block:

       git commit -m "<subject>" --trailer "Task: DAEO-qzrq" --trailer "Role: engineer" --trailer "Implements: DEC-1014, DEC-1017" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

   Then run `git log --oneline -2` and `git status --short` and quote them.
2. **The acceptance tests arrive while you work (DEC-963):** the lead merges them into this worktree between your
   batches. Only if `/home/usain/gov-os-worktrees/W2-123/.gov-runtime/scratch/lead/TESTS-READY` exists when your
   commit is made, run them once, reading results only, through
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src TMPDIR=/tmp/gov-os-lead-W2-123 python3 -m gov.cli.main accept DAEO-qzrq --json`
   only (never `pytest` on `tests/acceptance/`), and report pass or fail per KPI line and the counts. If it does not
   exist, say so and return; the lead starts the next batch.

## Return

Your sandbox check (first); your commit's hash (12 digits); the files changed; the lines added and removed; the
defaults you chose; how the cap is applied and how a child inherits it; the tests you ran with their results; the
`gov accept` result if run; each existing test or caller whose expectation you had to keep (and how); the
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
