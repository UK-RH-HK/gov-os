You are a fresh reviewer. Ticket DAEO-cy5o (W2-57, "the rulesync probe, the doctor probes, the serial pass and its route to the nightly"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`, at the head `8d9d78d93529`, and its acceptance tests pass. Probe the final code for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. You write nothing: return the probe record's content and the lead commits it. Return each finding as a described behaviour, with its severity.

**This is a judgement-only re-probe (owner, DEC-895 item 2), not a new round.** The ticket's last review (`docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md`, verdict pass, probed commit `8f61bda0eb5c`) went stale when the lead merged `w2/integrate` at `8555aafc0ba6` into this branch (merge `91f5b19af1af`; the head adds only the lead's checkpoint record `docs/checkpoints/DAEO-cy5o/CP-DAEO-cy5o-0012.md`). That merge brought W2-07's round 2 (merge `8555aafc0ba6`), which changed one file the earlier probe judged: `src/gov/close/command.py`, one line, gate (h)'s (the `recorded` subtraction before `_check_unmeasured`). git merged it beside W2-57's serial-phase line in `_run_tests` with no conflict. The earlier record's findings and classification stand unless a change touches them.

## Step 0: the sandbox check (before any work; report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return with the twelve fields, saying which.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-cy5o`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-57` and `w2/W2-57`) and `git rev-parse --short=12 HEAD` (expect `8d9d78d93529`). If anything differs, stop and say so. Inside the sandbox `git status --short` shows about 11 `??` entries (`.bashrc`, `.gitconfig`, `.mcp.json`, `.idea` and the like): they are the sandbox's placeholder mounts, not files of the head.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete. Your budget is about 45 minutes; the scope is narrow.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree. To read an older version of a file, use `git show <commit>:<path>`.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -m gov.cli.main retrieve "<question>" --json` (the worktree's store was rebuilt at the merge `91f5b19af1af`; the head adds only a checkpoint record, so a facet may read "stale": if so, say so and read the named files). **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve` (and the code-graph tool), and for what.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`, in this worktree or anywhere.
- **Policy 2 (DEC-820):** you read everything, tests and code alike, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material: never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path; its name may be seen; (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-57/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests); you are no counterpart, so nothing of this ticket is closed to you; (d) the hidden half of any evaluation set, by whoever is measured by it, is never read. Never read or name the qualification oracle.
- **Protected places (DEC-820):** never write in `~/gov-os-workbench`; dev-tier material is used by `GOV_DEV_TIERS` by name only and cloned into a temporary folder. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A probe that needs a repository builds a temporary one from scratch in your temporary folder, or copies single named files, never `governance/project/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase or tag. Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (a probe's own temporary project is yours to use). Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- **Disk and inodes (DEC-898), your share:** the ticket's budget is 20 GB and 1,000,000 files and folders for the lead and all workers together, outside the tracked tree; **your share is at most 6 GB and 300,000 files and folders at any moment**, in your temporary folder. Keep `TMPDIR` as the sandbox sets it. Keep pytest's own retention (never `--basetemp`). **Pass `-o tmp_path_retention_policy=failed` on every pytest run you make** (DEC-905). Never run the whole of `tests/` or a whole folder of W1-07, W1-25, W1-26, W1-27 or W1-30 at once; run named files or cases. Clean up as you go. Measure your temporary folder (`du -s --inodes`, `du -sh`) before and after any heavy probe and give the figures in your return's `evidence` line. If you pass your share, stop at once and return.
- **The machine:** other sessions share it. Before any run of more than a few cases, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`). **The nightly (owner, DEC-933 item 2.4):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite, at most a single test file; wait, checking each few minutes. Never run with `-x`. A time-sensitive case that fails under load is re-run alone before you call it red.
- **Inside your sandbox** the code-graph tool's folder `/tmp/gov-cbm-<uid>` is read-only (until W2-56), `gov` uses a private Ollama on the CPU, and no live session can be launched: judge live, real-model and daemon cases by reading and by the lead's records; for a run you needed and could not make, describe it exactly (command and what it would show) and mark the finding as not reproduced. Never try to reach a refused place another way.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try.** You never ask or notify the owner.

## Your scope: judgement-only

- **The files to judge:** every file the earlier probe judged (the files this ticket's own commits changed: `git log --no-merges --grep='Task: DAEO-cy5o' --format=%h 8f61bda0eb5c`, each commit's paths) that changed between `8f61bda0eb5c` and the head (`git diff --name-only 8f61bda0eb5c HEAD`). The lead's intersection gives one file: **`src/gov/close/command.py`**. Check that intersection yourself.
- **The change in it:** `git diff 8f61bda0eb5c HEAD -- src/gov/close/command.py`. The line is gate (h)'s `recorded = _gates.decision_records(...)`; the behaviour behind it is in `src/gov/close/gates.py` (`decision_records`, `owner_listed`, `_ever_accepted`, `RECORD_PREFIXES`, `EVER_ACCEPTED`; `git diff 8f61bda0eb5c HEAD -- src/gov/close/gates.py`), which is W2-07's file, not this ticket's. Read it as far as it bears on `command.py`'s flow.
- **Your question:** does any change alter what the earlier probe found, or let the close pass something W2-57's change refused? In particular:
  1. **the serial phase's entries:** does the close still give the serial run exactly the entries the list routes `serial` (not `nightly`), with an unreadable route kept serial, and does `test_runs` / `cases` still state what ran;
  2. **the nightly route:** does a routed entry still leave both phases of the close, and does nothing outside the route drop a serial entry;
  3. **the order of the commit gates before any test:** do the probe gate, the trailer gate, accepted history, gate (h) (`_check_unmeasured` after the `recorded` subtraction) and the ratchet lists still all refuse, before any test runs and without spending an attempt, as they did at `8f61bda0eb5c`; does the widened `recorded` set (decision-record commits now allowed to touch `.tickets/`, `docs/checkpoints/`, `docs/close/`, `docs/probes/`; commits the owner's lists name, whatever they change) let a commit of W2-57's own range or a commit touching a file W2-57's change governs (`src/gov/close/serial.py`, the serial call in `command.py`, `tests/acceptance/serial-only.txt`) escape the gate in ordinary work.
- **Not in scope, and not to be re-raised:** the earlier record's findings F1 to F4 and their classification (they stand unless the merge touches them; say so if it does); W2-07's own round 2 judged on its own merits, except as it bears on question 3.
- Run the code; do not judge it by reading alone. Where you can, plant a case in a temporary project of your own (a small git repository with its own `tests/acceptance/serial-only.txt` and stand-in cases, closed by `gov close` in that temporary project as W2-57's route case does), never in the worktree. A finding you could not reproduce is marked as such.

## What you may read for context

- The earlier records: `docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md` and `PR-DAEO-cy5o.md`.
- The ticket `.tickets/DAEO-cy5o.md`; `docs/DECISION_REGISTER.md`: DEC-895, DEC-896 (item 1), DEC-923 (item 2), DEC-906, DEC-868, DEC-527, DEC-549, DEC-916, DEC-933.
- W2-07's round 2 probe and close records, if present under `docs/probes/DAEO-r9ss/` and `docs/checkpoints/DAEO-r9ss/`.

## The lead's verification at the merge `91f5b19af1af` (code identical at `8d9d78d93529`)

- `gov.__file__`: `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`.
- Full `gov rebuild --json`: exit 0 (lexical, semantic and code-intelligence stores recreated). The keyword warning (row W2-L423's rule): 0 files.
- `gov check --json`: ok; 17 families, 15 GREEN, 2 YELLOW (`core-decision-citations` and `openspec-validate`, the same two as at both earlier reviews), no RED.
- The probe-impact check (DEC-895 item 2) on the merge: "STALE PROBE: W2-57 (DAEO-cy5o): the merge changes 1 judged file(s): src/gov/close/command.py".
- `tests/acceptance/W2-57/` and `tests/unit/close/` in the close's form (parallel run with the close's plugin, under the lock, `-o tmp_path_retention_policy=failed`): 466 passed, 0 failed (3:52). The one serial entry in that scope (`tests/acceptance/W2-57/test_w2_57_designer_read_p95.py`), run alone: 1 passed.
- Collection (`pytest tests --collect-only`, one process): `16690/16692 tests collected (2 deselected)`, no error.
- W2-07's run 5 verified the same merged code in full: 16,479 passed, 0 failed; serial 180 passed.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), with nothing before them. **After them, the probe record's content** for the lead to commit (you write nothing): a first line `Verdict: pass` or `Verdict: fail`; the head you probed; step 0's result; the `gov.__file__` line; the classification of your findings on one line (DEC-809); the intersection of judged and changed files you found; what you probed and found sound, by questions 1 to 3 above; whether the earlier record's F1 to F4 stand; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. You repair nothing (MR-4). Say also your scratch figures, the read refusals met, and whether you used `gov retrieve` (and the code-graph tool), and for what.

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

Refused twice for the same call: stop and say so; no third try.
