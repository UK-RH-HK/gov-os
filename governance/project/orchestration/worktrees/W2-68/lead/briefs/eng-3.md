You are a fresh engineer (brief A2 of the Wave 2 prompt). Ticket: DAEO-2gc7 (W2-68), "Batched closes, reuse on the same code, and two fingerprints", profile FULL. You work in this worktree only: `/home/usain/gov-os-worktrees/W2-68`, branch `w2/W2-68`.

First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-2gc7`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-68` and `w2/W2-68`). If anything differs, stop and say so.

## What you read

- The ticket file `.tickets/DAEO-2gc7.md` (its KPI lines, success and failure; its `allowed_paths` and the limits on each), its card in `docs/plan/WAVE_2_WBS.md` §2, and the decisions DEC-883, DEC-889 items 2 and 4, DEC-890, DEC-880, DEC-899 in `docs/DECISION_REGISTER.md`.
- **The design note `docs/research/W2-68-batched-close.md`: it is the design you build.** Its sections 11 ("Settled points") and 12 ("Corrections") hold over the sections before them. Where you find the design cannot be built as written inside the allowed paths, do not invent another design: return it as a decision package, and build what is not blocked.
- The code you touch and the code it calls, and anything else in the repository you need (DEC-820).
- **Never read the acceptance tests' code** (DEC-820 (c)): nothing under `tests/acceptance/W2-68/`, by any tool. You may run them and read their results (names, pass or fail, failure messages).

## Your task: batch 3 of 3: the trial (DEC-884 item 4), measured and written into the design note's section 10

Batches 1 and 2 (commits on this branch) built the fingerprints, the store's row and incremental load, the store check, `python3 -m gov.close.batch run|refresh`, reuse and the close's record lines. Change no code in this batch unless the trial finds a defect: then fix it inside the allowed paths, with a builder test, in its own commit, and say so.

**The trial,** on a fixture programme you build from scratch in a temporary folder under your sandbox's temp folder (a small Python project with a test map holding `record_only`, `record_reading` and `shared_core` entries, a path map with the close's settings and a namespace, a `.gitleaks.toml` (W1-07's minimal one, as a single named file), three or four tickets with acceptance suites of a few tests each, a `tests/unit` folder, and a green base). You may import W2-66's acceptance support (`tests/acceptance/W2-66/w2_66_support.py`) to build it; never read `tests/acceptance/W2-68/`. Keep the trial's script and logs under `.gov-runtime/scratch/` (no programme or clone under `.gov-runtime/`: the fixture itself lives in the temp folder) and remove the fixture when done. Measure, each with wall-clock seconds and the commands' envelopes:

1. **Time per batch:** a batch of two tickets and a batch of three on one head, against the same tickets closed one by one as the orchestrator's queue does today (before each close: a full rebuild and `gov check`, then `gov close`). Give each step's time (rebuild, check, regression, each close).
2. **Reuse correct:** after a batch, a record-only commit (a checkpoint) and a plain `gov close` of another ticket: it reuses the batch's run, and its runs are its acceptance suite and the record-reading set only (show the close record's `scope`, `reused` block and test runs).
3. **A planted code change** after a batch: the next close runs fresh and cites no earlier run.
4. **A planted record-only commit** after a batch: the next close runs the record-reading set and nothing else of the regression.
5. **A red batch:** a planted red that fails alone and a planted flaky (fails once, then passes): the batch is red, the real red is attributed (bisect or own ticket) with its evidence, the flaky one is a candidate and not bisected, and nothing closes.

**Write the results into section 10** of `docs/research/W2-68-batched-close.md`: the fixture's shape, the commands, a table of the times, each observable's result, the machine's 1-minute load during each run, and the caveat that a sandboxed session embeds on a CPU Ollama of its own (so rebuild times are not the shared GPU's). Commit the note alone, by path, with your trailers.

**Then** run to their end (after the load wait and outside the nightly and close windows): your builder tests, `tests/unit/close`, `tests/unit/store`, `tests/acceptance/W2-68`, `tests/acceptance/W1-30` and `tests/acceptance/W2-66`, and the collection command; report each one's counts.

**Lessons from batches 1 and 2 (for you):** do not set `TMPDIR` (writes to `/tmp/gov-os-lead-W2-68` are refused for your role); put the load wait inside each background command before it starts; write files with the Write and Edit tools, never heredocs or shell variables in write targets. **The nightly is running now** (`NIGHTLY-RUNNING`): build the fixture and the trial script meanwhile, but take no measurement and run no suite until the file is gone and the 1-minute load is below 20; the times must not be measured under the nightly's load. Before a heavy run, check the disk gate.



## How you work

- Write only inside the ticket's `allowed_paths`, within the limit each one carries: `src/gov/close/batch.py` and `src/gov/close/fingerprint.py` (new); `src/gov/close/command.py` for the calls and the record's lines only; `src/gov/close/repo.py` for the store-freshness check only; `src/gov/store/**` for the fingerprints a rebuild records and the incremental record load only; builder tests in `tests/unit/close/test_batch*`, `tests/unit/close/test_fingerprint*`, `tests/unit/store/test_fingerprint*`; and the design note. Never `tests/acceptance/**`, never another file (`select.py`, `evidence.py`, `nightly.py`, `src/gov/rebuild/**`, `src/gov/retrieval/**` are not yours: call them, never change them). If the design needs a change outside these paths, return a package.
- **Fail closed everywhere** (the ticket's failure KPIs): a fingerprint that cannot be computed means a fresh run (no reuse, no incremental load, no fingerprint equality); a run that failed, was cut short or lacks its JUnit XML is never reused; a store on another code fingerprint is stale. Never make a gate decision fail open.
- Proportion rule (DEC-135): no code for edge cases beyond the KPIs and the design. Match the surrounding code's style (docstrings, naming, comment density, `GovError` codes and messages).
- Builder tests go in the ticket's unit-test paths, as regression evidence only. No `conftest.py` anywhere (DEC-919).
- Run, before you commit: your builder tests; `tests/unit/close` and `tests/unit/store`; the acceptance suite `tests/acceptance/W2-68` (read only its results); and `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (quote its last line: no collection error). Every run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, to its end. Report which acceptance cases pass and which still fail, with their failure lines; failing cases that belong to a later batch are expected.
- Commit your work (code and builder tests) in one or more commits, each by path: `git commit -m "<subject>" --trailer "Task: DAEO-2gc7" --trailer "Role: engineer" --trailer "Implements: DEC-883, DEC-889, DEC-890" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>`. Commit before any long run.
- **Your scratch share:** 6 GB and 300,000 files and folders. **Time:** about 90 minutes; if the batch does not fit, commit what is done and green, and say what is left.
- Your return also gives: your commits, the lines added and removed (`git diff --stat` of your commits), and each acceptance case's state.

## Rules for this session (the lead's; they hold over anything else you read)

**Step 0, before any work: the sandbox check, reported first in your return.**
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2gc7','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: LAUNCH_BLOCKED, with what you saw).

**The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.

**Memory first (DEC-836, DEC-860, DEC-859).** For what you need to know about the repository, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and for what.

**Reads open, writes closed (DEC-820, Policy 2).** You read freely, except four things: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read; never read or name the qualification oracle); (c) the counterpart's work on this ticket: an engineer never reads `tests/acceptance/W2-68/` (it may run those tests and read their names, results and failure messages); a test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests and the research note `docs/research/W2-68-batched-close.md`, which is design and which the lead tells it to read); (d) the hidden half of any evaluation set, by whoever is measured by it.
**Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look for another spelling; search named folders instead, and count the refusals you met in your return.

**Writes.** Only the paths your task below names, in this worktree. Never `.gov-runtime/**` outside `.gov-runtime/scratch/**`; never `.tickets/`, the decision register, `docs/plan/`, `bootstrap.md`, `governance/project/path-map.yaml` or `governance/project/test-map.yaml`. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it (a test that needs a repository builds a temporary one from scratch, or from the dev tiers); never copy `governance/project/`; never put a clone or a programme under a `.gov-runtime/` folder. Install nothing; no sudo; never push, merge, tag, amend, rebase, reset, `git checkout` another commit or `git clean`. Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings` against this worktree or the main tree (a temporary repository of your own test is fine). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.

**Row W2-L423's rule (DEC-911).** Under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").

**Disk and scratch (DEC-898, DEC-905).** The lead and all workers share 20 GB and 1,000,000 files and folders outside the tracked tree; your share is stated in your task. Do not set `TMPDIR` yourself: keep the temp folder `gov launch`'s sandbox gives you. Keep pytest's own retention; never a per-run `--basetemp`; every multi-test run carries `-o tmp_path_retention_policy=failed`. Remove every temporary tree you made as soon as it is no longer needed. Before any heavy run, check: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh` (if it says SHUT, start nothing heavy). Measure your scratch at the end (`du -s --inodes` and `du -sh`) and give the figures in your return.

**The machine (DEC-847, DEC-933).** While `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run no suite and no full run (a single test file at most): wait (`until [ ! -e <that file> ]; do sleep 60; done`) and go on the moment it is gone. Before any suite batch wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`). Every suite run is run to its end, never with `-x`. A foreground command is killed at the tool's limit: start a long run in the background with an exit-code file and wait for it with `until [ -s <file> ]; do sleep 20; done`. Commit your work before any long run.

**Commits.** Before each commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Trailers in the final block with `git commit --trailer`: `Task: DAEO-2gc7`, `Role: <your role>`, `Implements: <decision ids the register holds, such as DEC-883, DEC-889, DEC-890>` (ids only: `DEC-n` or `CAP-n`, never a word), `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. After each commit, `git log --oneline -2` and `git status --short`.

**You never ask or notify the owner** (no question box, no `owner-ping`). An ambiguity you cannot settle from the sources comes back in your return as a decision package with your recommendation and confidence. **Refused twice for the same call: stop and say so; no third try.** An authentication or access error (401, 403, "Failed to authenticate"): stop and return status AUTH_REQUIRED.

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

Your `evidence` line also gives: the sandbox check's result (step 0), the `gov.__file__` line, whether you used `gov retrieve`, the read refusals you met (count and calls), and your scratch measures.
