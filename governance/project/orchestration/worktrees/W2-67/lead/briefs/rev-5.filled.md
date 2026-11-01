You are a fresh reviewer. Ticket DAEO-9nys (W2-67, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, worktree `/home/usain/gov-os-worktrees/W2-67`, branch `w2/W2-67`. All three declared rounds are built and each has a passed review (round 1: `docs/probes/DAEO-9nys/PR-DAEO-9nys.md`; rounds 2 and 3: `docs/probes/DAEO-9nys/PR-DAEO-9nys-run3.md`). On 2026-10-31 the lead merged `w2/integrate` (`c07a1115577f`) into the branch (merge `0568d91baf56`, DEC-954). That merge had to resolve **one conflict in a file the earlier review judged**, `tests/acceptance/W1-30/test_w1_30_close.py`, so under DEC-953 (its lifted DEC-895: "a new review only if a merge had to resolve conflicts in files your review judged") **you review that resolution only**, at effort max. You probe the head `__HEAD__` (the lead's `gov checkpoint` record on top of the merge; it adds only that record). You write nothing. Return each finding as a described behaviour, with its severity.

## Step 0: the sandbox check (before any work; report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return with the twelve fields, saying which.

## What you review

- **The conflict:** in the KPI S1 / CAP-38.c case `test_task_trailer_exact_match_not_substring` ("Task: AB must not count as a commit of ticket A"):
  - this ticket's side (first parent `bdc1bb3e1d43`): the round-1 revision I2 F2 against plant PF15: ticket A has its checkpoint, the fixture asserts A has no commit, the refusal is the trailer gate's (names `Task: <A>` exactly, does not name AB's commit), A is not closed; ids `PROJ-tska`/`PROJ-tskab`, `W1-tka`/`W1-tkab`;
  - `w2/integrate`'s side (second parent `c07a1115577f`): W2-64's fixture correction (`be76f9a39ef7`, DEC-954 P-W2-64-1 (a), `Rewrite-Reason: DEC-872 item 2`): ids the ticket schema takes, `PROJ-tkaa`/`XPROJ-tkaa`, `W1-947`/`W1-9471`; its body asserted only `ok is False`.
  - The resolution, by a fresh independent test designer (td-9): W2-64's ids with this ticket's assertions kept whole. See `git show 0568d91baf56` (its message), `git diff bdc1bb3e1d43 0568d91baf56 -- tests/acceptance/W1-30/test_w1_30_close.py` and `git diff c07a1115577f 0568d91baf56 -- tests/acceptance/W1-30/test_w1_30_close.py`.
- **What you judge:**
  1. Does the resolution keep both sides' intent and lower nothing: every assertion of this ticket's revision, W2-64's schema-valid ids everywhere in the file (also `WBS`, `other_wbs`, the planted folder, which merged cleanly), the docstring true to the ids?
  2. Does the case still fail under PF15 (a close that counts a commit carrying `Task: AB` as a commit of A, a substring match) on the merged close? Probe it: a plant of your own in your temporary folder (a plugin or a stand-in imported ahead of the worktree's module), never in the worktree; one run of this single case under the plant, and one without. Do not re-run the suite (DEC-959 item 1); the lead's results are below.
  3. The designer's own note (its package P-W2-67-PF15-PREFIX): with W2-64's ids, A's id sits at the end of AB's, so the case no longer catches a close that matches only at the start of the trailer value (an unanchored `startswith`, or a search for `Task: <A>` with no end anchor), which the old pair did. Judge it by the two questions below: can a real ticket id be another valid id plus trailing characters under the ticket schema (`template/governance/kernel/schemas/common.schema.json`), and does any other case in W1-30 or the unit suite catch an end-unanchored match?
  4. Scope: the merge drops nothing of either side in any file (`git diff --stat` of the merge against each parent; `git merge-tree` agrees with the result apart from the one resolved file).
- **The lead's verification of the merged head** (logs under `.gov-runtime/scratch/lead/log/`):
__VERIFY__

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-9nys`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-67` and `w2/W2-67`) and `git rev-parse --short=12 HEAD` (expect `__HEAD__`). If anything differs, stop and say so. `git status --short` shows one untracked file, `tests/acceptance/W1-27/w2_67_td4_plant.py`: an emptied plant a sandbox could not remove (DEC-920 item 5); it is not part of the head. Untracked dot-names (`.bashrc`, `.mcp.json` …) are the sandbox's placeholder devices.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another. You write nothing: return when your findings are complete. Your budget is about 45 minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree. Read older versions with `git show <commit>:<path>`.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands the guard may refuse some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Policy 2 (DEC-820):** you read everything, tests and code alike, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its name may be seen; never read, print, search, diff or copy it, never type its path); (c) the counterpart's work on this ticket is closed only to the counterpart: the engineer never reads this ticket's acceptance tests, and the test designer never reads this ticket's implementation; you are no counterpart, so nothing of this ticket is closed to you; (d) the hidden half of any evaluation set, by whoever is measured by it, is never read. Never read or name the qualification oracle.
- **Protected places:** never list, glob, search, read or write in `~/gov-os-workbench`; dev-tier material by `GOV_DEV_TIERS` by name only. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673). Never copy the repository or a folder of it; copy single named files into your temporary folder if a probe needs them.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- Write no file of the repository and make no commit (the guard's fifth rule: a reviewer writes only its own review record, and here the lead writes it). No subagents that write. Install nothing (an install is a P1 in your return). No push, merge, rebase or tag.
- **Disk and inodes (DEC-898), your share:** the ticket's budget is 20 GB and 1,000,000 files and folders for the lead and all workers together; **your share is at most 2 GB and 50,000 files and folders at any moment**, in your temporary folder. Keep `TMPDIR` as the sandbox sets it. Keep pytest's own retention; never pass a per-run `--basetemp`. **Pass `-o tmp_path_retention_policy=failed` on every pytest run** (DEC-905). Never run with `-x`. Measure your temporary folder (`du -s --inodes`, `du -sh`) before and after your probe run and give the figures in `evidence`.
- **Command forms:** write probe files with the Write tool and literal absolute paths; no here-documents, no shell variables as write targets, no long inline `python3 -c` with braces.
- If the guard or the sandbox refuses something you needed, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try.** You never ask or notify the owner.

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

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), with nothing before them. **After them, the probe record's content** for the lead to commit (you write nothing): a first line `Verdict: pass` or `Verdict: fail`; the head you probed; step 0's result; the `gov.__file__` line; the classification of your findings on one line (DEC-809); what you probed and found sound, part by part (1 to 4 above); and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. You repair nothing (MR-4). Say also your scratch figures, the read refusals met, and whether you used `gov retrieve` (and the code-graph tool), and for what.

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
