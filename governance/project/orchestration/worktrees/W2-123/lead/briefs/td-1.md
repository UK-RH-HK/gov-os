# Brief: independent test designer, DAEO-qzrq (W2-123), STANDARD

You are a fresh independent test designer (MR-3). Ticket: DAEO-qzrq (W2-123), profile STANDARD. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-123-tests` on branch `w2/W2-123-tests` (DEC-963). You never read or write
the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-123`. You write the ticket's acceptance tests from its KPI
lines and its sources, in parallel with the engineer, and you show them red.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-qzrq','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-qzrq`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-123-tests` and
  `w2/W2-123-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for
  verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src` set
  **per command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src python3 -c "import gov; print(gov.__file__)"`, quoted in
  your return; it must point into this worktree. Your tests must exercise whatever `gov` the pytest process imports
  (import `gov.retrieval.ollama` from the pytest process; any child process runs `sys.executable` with the pytest
  process's own `PYTHONPATH` inherited), so that, once merged into the ticket's worktree and run there with that
  worktree's `PYTHONPATH`, they exercise the ticket's code. Your README says so.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`
  (a read). Never the ticket worktree's store. **Never one giant query (DEC-860):** a large question is taken in
  batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question
  (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and
  targeted, never a load of the whole graph. What changed on `w2/integrate` since that store's refresh, read with
  `git show w2/integrate:<path>`.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths
  (`src/gov/retrieval/ollama.py`, `tests/unit/retrieval/test_w2_123*`, `docs/changes/W2-123-evidence.md`), and name in
  your return each such result you were served (DEC-820 (c)). You may read `src/gov/retrieval/ollama.py` as it stands
  on `w2/integrate` (`git show w2/integrate:src/gov/retrieval/ollama.py`) to learn today's public behaviour, never the
  ticket branch's.
- **Policy 2 (DEC-820):** reads are open, with four refusals: (a) secrets and keys, never printed; (b) the contents of
  the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
  (c) the counterpart's work on this ticket: you never read this ticket's implementation, the files
  `git -C /home/usain/gov-os-worktrees/W2-123 diff --name-only w2/integrate...HEAD` names (other than your own
  tests), and never anything in `/home/usain/gov-os-worktrees/W2-123`; (d) the hidden half of any evaluation set, by
  whoever is measured by it. Writes stay inside your paths.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the
  repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named
  folders instead, and count the refusals in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; anything longer goes in a script file under
  `/home/usain/gov-os-worktrees/W2-123-tests/.gov-runtime/scratch/td/` written with the Write tool, then run. A refused
  form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of
  this repository). A test that needs a repository builds a temporary one from scratch, under pytest's `tmp_path`. No
  clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`; never
  list, glob or search it; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a session `.gov-runtime/freeze` may
  show as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your budget (DEC-898):** 4 GB and 200,000 files and folders outside the tracked tree (your share of the ticket's
  20 GB and 1,000,000). Set `TMPDIR=/tmp/gov-os-lead-W2-123` on every test run (where `gov launch`'s sandbox sets its
  own temp folder, keep that one and count it). Keep pytest's own temp retention; never `--basetemp`. Clean what you
  make as soon as it is no longer needed. Measure (`du -sh` and `du -s --inodes`) before your red run and at the end;
  give the figures in `evidence`.
- **Heavy steps (DEC-979 D1, DEC-1008):** one test file is not heavy. If your red run covers more than one file, run it
  as `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <the pytest command>`.
  You need no rebuild. Never run `gov rebuild --no-embeddings` on any real worktree.
- **Never the real embedding servers:** no test sends a request to, stops, or starts anything at 127.0.0.1:11434 or
  127.0.0.1:11435, and no test runs the real `ollama`. Every test sets `HOME`, `OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST` in the `env=` it passes (free ports on 127.0.0.1 your test picks), `GOV_OLLAMA_BIN` to a
  planted executable under `tmp_path`, and stands up its own stand-in endpoint. A safe-restart test stops only a
  process your test started. Existing tests on `w2/integrate` that plant an Ollama executable or a stand-in endpoint
  (for example under `tests/unit/ollama/`, `tests/acceptance/W1-18/`, `tests/acceptance/W2-54/`) show how: find them
  and reuse their way.
- Install nothing (a tool you need is a package, P1). No push, merge, rebase or tag. Never write `.gov-runtime/**`
  outside `.gov-runtime/scratch/`. No subagents that write. Never ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command,
  stop and return it.

## What you read

- The ticket file `.tickets/DAEO-qzrq.md` (read-only): its KPI lines, its `allowed_paths` and its sources.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-1014 (items 4 and 6), DEC-1015 (item 2), DEC-1017, DEC-1010
  item 7, DEC-1011, DEC-982, DEC-996 item 3, DEC-260, DEC-261, DEC-798, DEC-135, DEC-221.
- The package `governance/project/orchestration/packages/ACT-OLLAMA-CAP-1.md` (what the cap is and why).
- W2-20's ticket `.tickets/DAEO-r30l.md` (its KPI line on the durable cap of both servers, which this ticket's start
  reads).
- The WBS rules, `docs/plan/WAVE_2_WBS.md` section 0, and the W2-123 card in section 2.
- The code it works with, as it stands on `w2/integrate`: `src/gov/retrieval/ollama.py` and how
  `src/gov/retrieval/semantic.py` embeds and keeps vectors (its model, its `/api/embed` requests, float32 BLOBs).

## The behaviour to test

The ticket's KPI lines, as they stand in its file, and this interface, which the lead fixes so that you and the
engineer build to the same outside:

{{INTERFACE_SPEC}}

## What you write

- Only inside `tests/acceptance/W2-123/` in your worktree. No throwaway implementation is left in the tree.
- STANDARD (DEC-221): every KPI line's success and failure plus the key edge cases (an unreadable value of each
  kind S1 names, the query server's cap and hidden GPU, a cap inherited by a child, a restart refused while the
  server answers and for a foreign process on the port). No combinatorial expansion. Behaviour through the public
  interface above, never internals. Deterministic, no network beyond stand-in endpoints on 127.0.0.1 that your tests
  start and stop. Tests that need a CPU list pick CPUs from `os.sched_getaffinity(0)` at run time, so they pass on
  any machine; nothing of this machine in the tests either.
- KPI 3 (the measure) gets at most one test: the evidence file exists and has S6's table and `Chosen setting:` line.
- A `README.md` there that maps each KPI line (KPIs 1 to 6 and the failure line) to its tests, gives the expected red
  reason of each, and says how the tests exercise the code under test (above).
- Red first: run your tests to the end, never with `-x`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src TMPDIR=/tmp/gov-os-lead-W2-123 python3 -m pytest tests/acceptance/W2-123 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (through `verify_lock.sh` if more than one file); they fail for the reason the README states (the base code reads
  no configuration, starts uncapped, states no settings, and has no probe, restart or determinism check). Collection
  must succeed. Report the counts.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact,
  reversibility, cost, recommendation, confidence). If the KPIs require revising an earlier ticket's acceptance test,
  name it and do not edit it.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only your test paths, in one commit, with the trailers in
the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-qzrq" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1014, DEC-1017" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your sandbox check (first); your commit's hash (12 digits); the test count; the KPI lines with their tests; the red
reason as you saw it; the `gov.__file__` line; every earlier test you rewrote, with its reason (none expected); the
`gov retrieve` queries you ran and any result under the implementation paths you were served; the read refusals you
met; any package.

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
