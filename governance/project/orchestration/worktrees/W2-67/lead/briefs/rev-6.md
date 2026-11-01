You are a fresh reviewer. Ticket DAEO-9nys (W2-67, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, worktree `/home/usain/gov-os-worktrees/W2-67`, branch `w2/W2-67`. All three declared rounds are built and each has a passed review. On 2026-10-31 the lead merged `w2/integrate` (`c07a1115577f`; merge `0568d91baf56`, DEC-954); that merge resolved one conflict in `tests/acceptance/W1-30/test_w1_30_close.py`, and a first reviewer (rev-5) reviewed that resolution: **pass**, with two findings, both "Ordinary work: yes", "Consequence: other":

- **F1 (medium):** with W2-64's ids (A `PROJ-tkaa`, AB `XPROJ-tkaa`, AB = A's id with one character in front), the close's fixed-string search for `Task: PROJ-tkaa` never returns AB's commit, so the case `test_task_trailer_exact_match_not_substring` no longer turned red under its plant of record **PF15** (td-6's: a ticket's commits matched by substring of their `Task:` value; `.gov-runtime/scratch/td-6/plant/PLANTS.md` and `site/sitecustomize.py`). The reviewer ran it: 1 passed under the plant. Under the ticket schema only a `Task:` value of A's id **plus trailing characters** (naming no ticket) can show PF15.
- **F2 (low):** the case's row in `tests/acceptance/W1-30/README-W2-67.md` still named A as `PROJ-tska` and recorded it red under PF15.

Under the ticket's one repair batch, a fresh independent test designer (td-10) changed that case and that README in commit `a8c0920abead`; the lead then committed a checkpoint record (`90d41204d412`, adds only `docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0025.md`). Under DEC-953 a new review runs on a repair's change only: **you review `git diff 3a2f2a1f0497 a8c0920abead`** (2 files), at effort max, on the head `90d41204d412`. This is the last review of this change (DEC-413). You write nothing. Return each finding as a described behaviour, with its severity.

## Step 0: the sandbox check (before any work; report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return with the twelve fields, saying which.

## What you judge

1. **F1 is fixed:** the case on the head turns red under PF15 for PF15's own reason, and stays green without it. Probe it: td-6's carrier (`PLANTS.md`, "Commands"), with `PYTHONDONTWRITEBYTECODE=1` and your marker file in your temporary folder (never in td-6's or td-10's folder, never in the worktree); one run of this single case under PF15 and one without. Do not re-run the suite (DEC-959 item 1). td-10's runs: under PF15 after the change, 1 failed, "the refusal does not say that no commit carries Task: PROJ-tkaa", the close refused with `CONTAINMENT_FINDING`, marker "commits of PROJ-tkaa matched by substring: 1, of them exactly: 0"; on the head 1 passed; the whole file 33 passed before and after.
2. **Nothing lowered:** every assertion the case had at `3a2f2a1f0497` is still there and as strong; W2-64's ids for A and AB are kept; the added commit cannot make the case pass or fail for a reason other than the close's matching (does any gate the close runs before or after the matching (the commit gates, containment, the checkpoint) now refuse for the near-miss commit on the head, hiding a fault? Read `src/gov/close/command.py` and `repo.py`).
3. **F2 is fixed:** the README-W2-67 row and its new section "Run 6: the merge of W2-64's ids (repair batch)" are true of the head and of the runs; W1-30's `README.md` is untouched by the repair.
4. **Scope:** the commit `a8c0920abead` touches only those two files, carries `Task: DAEO-9nys`, `Role: independent-test-designer`, an `Implements:` of decision ids, and a `Rewrite-Reason:`; `90d41204d412` adds only the checkpoint record.

## The lead's verification

The lead's rebuild and scoped run in the close's form on `90d41204d412` run while you review; their results go into the probe record beside your verdict. Do not wait for them and do not re-run them. Known so far: `gov.__file__` = `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`; the selection (`select_tests.py`) is `scoped`, `core_changed` [], `unplaced` [], W1-30 selected.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-9nys`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-67` and `w2/W2-67`) and `git rev-parse --short=12 HEAD` (expect `90d41204d412`). If anything differs, stop and say so. `git status --short` shows one untracked file, `tests/acceptance/W1-27/w2_67_td4_plant.py`: an emptied plant a sandbox could not remove (DEC-920 item 5); it is not part of the head. Untracked dot-names (`.bashrc`, `.mcp.json` …) are the sandbox's placeholder devices.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another. You write nothing: return when your findings are complete. Your budget is about 45 minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree. Read older versions with `git show <commit>:<path>`.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands the guard may refuse some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Policy 2 (DEC-820):** you read everything, tests and code alike, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its name may be seen; never read, print, search, diff or copy it, never type its path); (c) the counterpart's work on this ticket is closed only to the counterpart: the engineer never reads this ticket's acceptance tests, and the test designer never reads this ticket's implementation; you are no counterpart, so nothing of this ticket is closed to you; (d) the hidden half of any evaluation set, by whoever is measured by it, is never read. Never read or name the qualification oracle.
- **Protected places:** never list, glob, search, read or write in `~/gov-os-workbench`; dev-tier material by `GOV_DEV_TIERS` by name only. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673). Never copy the repository or a folder of it; copy single named files into your temporary folder if a probe needs them.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- Write no file of the repository and make no commit (the guard's fifth rule: a reviewer writes only its own review record, and here the lead writes it). No subagents that write. Install nothing (an install is a P1 in your return). No push, merge, rebase or tag.
- **Disk and inodes (DEC-898), your share:** the ticket's budget is 20 GB and 1,000,000 files and folders for the lead and all workers together; **your share is at most 2 GB and 50,000 files and folders at any moment**, in your temporary folder. Keep `TMPDIR` as the sandbox sets it. Keep pytest's own retention; never pass a per-run `--basetemp`. **Pass `-o tmp_path_retention_policy=failed` on every pytest run** (DEC-905). Never run with `-x`. Measure your temporary folder (`du -s --inodes`, `du -sh`) before and after your probe runs and give the figures in `evidence`.
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
