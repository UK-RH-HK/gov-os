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

**Disk and scratch (DEC-898, DEC-905).** The lead and all workers share 20 GB and 1,000,000 files and folders outside the tracked tree; your share is stated in your task. Every suite run uses `TMPDIR=/tmp/gov-os-lead-W2-68` (where `gov launch`'s sandbox sets its own temp folder, keep that one). Keep pytest's own retention; never a per-run `--basetemp`; every multi-test run carries `-o tmp_path_retention_policy=failed`. Remove every temporary tree you made as soon as it is no longer needed. Before any heavy run, check: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh` (if it says SHUT, start nothing heavy). Measure your scratch at the end (`du -s --inodes` and `du -sh`) and give the figures in your return.

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
