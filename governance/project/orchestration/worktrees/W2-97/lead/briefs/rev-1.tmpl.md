# Brief: reviewer, DAEO-wq2b (W2-97), run 2 (read-only; review of this resume's changes only)

You are a fresh reviewer. Ticket `DAEO-wq2b` (`W2-97`, "the local merge queue"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-97` on branch `w2/W2-97`, at the head `@HEAD@`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing.

Ticket DAEO-wq2b is implemented in this worktree and its acceptance tests pass. Probe the final code for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. Return each finding as a described behaviour, with its severity. You write no file: you return the probe record's content in your last message, and your lead commits it.

## Your scope: only what this resume changed (the resume brief, DEC-985)

The tool (`governance/project/orchestration/tools/merge_queue.py`, 650 lines, with its README and unit tests) was built in run 1 and is not re-reviewed as a whole. Review what changed since `fb9b7e4ce06c` (the merge of `w2/integrate` before this resume): `git diff fb9b7e4ce06c @HEAD@ -- governance/project/orchestration/tools tests/unit/orchestration tests/acceptance/W2-97`. Run 2 made three changes:
1. The production default run's two test commands (the parallel run and the selected serial-only cases) now run through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <command>`, which takes one of the machine's heavy-job slots (`heavy_slot.sh` beside it; DEC-979 D1, KPI 1 as DEC-983 changed it). The alone re-runs and the traces take no slot; a `--test-cmd` stand-in replaces the whole run command.
2. A selection whose `scope` is anything but `scoped` is never run: the run stops (exit 4), nothing advances, nothing is ejected for it, the entries stay approved (KPI 3 as DEC-983 changed it: the full suite never runs here, only in the nightly).
3. The acceptance suite: the `enqueue` helper passes `--repo` (P-W2-97-ENQ-1, DEC-985), and one case was added for change 2.

Probe above all: can a run now advance `w2/integrate` without a completed, scoped test run (for example when the slot wrapper fails, is missing, waits, or returns a code the queue misreads)? Can a selection that is not scoped still be run on some path (a batch, a later round, a re-merge after the head moved, the trace without the batch)? Does the slot hold for long enough, or so long that it deadlocks with itself (the parallel run then the serial run, each taking a slot; the nightly holding all three, DEC-984)? Did the acceptance revision lower any expectation beyond the one line DEC-985 allows?

## Standing rules (read first)

- **Step 0, before any work: the sandbox check,** reported first in your return: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wq2b','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.
- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-wq2b`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-97` and `w2/W2-97`), and `git rev-parse --short=12 HEAD` must be `@HEAD@`. If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read.
- You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase or tag. Never run `gov close`, `gov adopt` or `gov pause`, and never `docs/plan/tools/validate_s1.py`.
- **Reads are open (DEC-820):** you read everything, tests and code alike. Only these are refused: secrets and keys (never printed); the contents of the held-out qualification material (never read or name the qualification oracle; never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path, DEC-525); the hidden half of any evaluation set. Never read `.claude/settings.json`. Never write in `~/gov-os-workbench`.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Take a refusal, never look for another form, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. A refused form is not retried in another disguise.
- **Never copy the repository** or a folder of it (no `cp -r`, `rsync`, `git archive`, second worktree or clone of this repository). A probe that needs a repository builds a temporary one from scratch in your own temporary folder (planted repositories, stub commands, as the unit and acceptance tests do), and removes it when done. **Never take a real heavy-job slot** (`/tmp/gov-os-heavy-slot-*.lock`) and never run a real suite: where you probe the slot, use `GOV_HEAVY_DIR` pointed at your own temporary folder, or read the code. No test of yours touches this repository's branches, its stores, `~/gov-os-runs/` or the network.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Tests are not re-run by you (DEC-959 item 1):** your lead ran the scoped set; read its results in `/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/` (`verify.rc`, `parallel.txt`, `serial.txt`, `select.json`) and the engineer's acceptance results in `log/eng-4.json`. You may run small probes of your own (a planted repository and the tool), and a single unit or acceptance case where a probe needs it.
- **Memory (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 -m gov.cli.main retrieve "<question>" --json`, in this worktree) for what you need to know before reading files at random; never one giant query (DEC-860: `--batch-size`, then `--continue <token>`); a code question uses the code-graph tool's own small traversal (DEC-859). Inside the sandbox it has hung on ollama.com: give it about 3 minutes, then read the named sources and say so.
- **Row W2-L423's rule (DEC-911):** write commit hashes in your return as 12 digits, except `probed_commit`, which is the full id; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Scratch:** your share is 1 GB and 50,000 files and folders, in your session's own temp folder (do not set `TMPDIR` to `/tmp/gov-os-lead-W2-97`; your sandbox cannot write it).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- **On an authentication or access error:** stop and return with status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-wq2b.md`: its KPI lines and its `allowed_paths` (`governance/project/orchestration/tools/merge_queue.py`, `tests/unit/orchestration/test_w2_97*`, `governance/project/orchestration/tools/README.md`, and the test designer's suite `tests/acceptance/W2-97/`).
- The sources and the decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-985, DEC-983 (item 4), DEC-979 (D1), DEC-984, DEC-968, DEC-959 (item 1), DEC-953 (item 4), DEC-848, DEC-954, DEC-491.
- The lead's specification of the tool's interface: `/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/briefs/part-spec.md` and its run-2 changes `part-spec-2.md`.
- The diff above, the code at the head, the acceptance tests and the unit tests; `verify_lock.sh`, `heavy_slot.sh` and `heavy_slots.conf` in `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/` (read only).

## Judgement rules

@JUDGEMENT@

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work or fails open, with its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Say also what you probed and found sound, and your verdict: `pass` (no finding is both "yes" and "fails open" or "loses work") or `fail`. Then the probe record's body in Markdown (a summary, the findings with their two lines, what was sound), which your lead commits under `docs/probes/DAEO-wq2b/`. The lead passes findings to a test designer; you repair nothing (MR-4).

After the probe record: your sandbox check's result; whether you used `gov retrieve` and for what; the guard's refusals you met (time, the command's form, the reason given), or "none"; and anything your brief did not tell you that you had to find out, with the minutes it cost.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
