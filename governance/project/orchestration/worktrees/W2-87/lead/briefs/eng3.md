## Standing rules for every worker of DAEO-s9qc (W2-87) — read first

- **Step 0, before any work: the sandbox check, reported first in your return.** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-s9qc','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.
- Then run `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect your role, `DAEO-s9qc`, `/home/usain/gov-os-worktrees/W2-87` and `w2/W2-87`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src` set **per command** (never in a session's `--settings` env). Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory (DEC-836, DEC-860, DEC-859):** before reading files at random, ask `gov retrieve`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used it.
- **Reads open, writes closed (DEC-820):** you read freely, except (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read or name the qualification oracle); (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-87/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests); (d) the hidden half of any evaluation set (`fixtures/evaluation/**/hidden/**`), by anyone, in any tree. Writes stay inside the paths your brief gives.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead. Count the refusals you met and give the count in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file in your own session scratchpad (the folder your session names; the guard refuses `.gov-runtime/scratch/lead/`), written with the Write tool, and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never read the held-out material's contents; never print a secret; never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A test that needs a repository builds a temporary one from scratch. No clone or copy of a programme under `.gov-runtime/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (and in your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Git:** no amend, no rebase, no reset, no `git checkout` of another commit, no `git clean`, no `--no-verify`, no push, merge or tag. Trailers in the final block with `git commit --trailer`. Never edit `.tickets/`, the decision register or `docs/plan/`. Never run `gov close`, `gov adopt`, `gov pause`, or `gov rebuild` (of any kind; never `--no-embeddings`). Install nothing.
- **Disk (DEC-898):** your share of the ticket's budget is 3 GB and 200,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never `--basetemp`); clean up what you make as soon as you no longer need it; measure your scratch (`du -sh`, `du -s --inodes`) at the end and give the figures.
- **Run everything in the foreground,** one command after another; return only after your commit exists. Never run a suite with `-x`. While `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run at most a single test file.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return `AUTH_REQUIRED`.

# Brief: engineer, DAEO-s9qc (W2-87) — one red from the lead's verification

You are a fresh engineer. Ticket: DAEO-s9qc (W2-87), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-87` on branch `w2/W2-87`. The branch's code is done (commits `006ad0bb36ce` and `060e03ef57ea`); the lead's full verification found one red that this ticket caused.

## The failing output

```
FAILED tests/acceptance/W2-61/test_w2_61_visible_half.py::test_every_source_exists_at_head_and_every_heading_is_found_there
AssertionError: q11.yaml: heading '    fused = rrf(routes)' is not a line of src/gov/retrieval/retrieve.py
```

## Bounds

- Write only `src/gov/retrieval/retrieve.py` (and, if you need one, a new `tests/unit/retrieval/test_w2_87*` file). The evaluation set under `fixtures/evaluation/` and W2-61's tests are not this ticket's: never edit them. Never read `fixtures/evaluation/**/hidden/**`.
- The bundle `gov retrieve` gives must not change at all: this is a change of form, not of behaviour.

## Done when

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/acceptance/W2-61/test_w2_61_visible_half.py tests/acceptance/W2-87 tests/unit/retrieval -q -p no:cacheprovider` passes (run it; never read `tests/acceptance/W2-87/`'s source).
- One commit:

      git commit -m "<subject>" --trailer "Task: DAEO-s9qc" --trailer "Implements: DEC-952" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

Your commit (12 digits) and its trailers; the lines changed; the suites you ran with counts; your sandbox check; your `gov retrieve` use; read refusals met; your scratch figures.
Your final message is your return. It starts with these twelve labelled lines, then any payload:

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

The twelve fields come first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
