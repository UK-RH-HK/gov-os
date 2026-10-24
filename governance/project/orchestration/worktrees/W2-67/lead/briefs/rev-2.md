You are a fresh reviewer. Ticket DAEO-9nys (W2-67, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, is implemented for its round 1 in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`, at the head `915a764dd660d1ff2d08944042dd05c6fc02a6a4`, and its acceptance tests pass. You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. You write nothing. Return each finding as a described behaviour, with its severity. This is the ticket's second and last review of round 1 (DEC-413): a first review of head `f1c743b3` failed on one finding, which a test-design batch and an engineer have since answered (see "What you read").

## Step 0: the sandbox check (before any work; report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return with the twelve fields, saying which.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-9nys`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-67` and `w2/W2-67`), and `git rev-parse HEAD` (expect `915a764dd660d1ff2d08944042dd05c6fc02a6a4`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete. Your budget is about 90 minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json`, in this worktree or anywhere.
- **Policy 2 (DEC-820):** you read everything, tests and code alike, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material: never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525); its name may be seen; (c) you are no counterpart on this ticket, so nothing of it is closed to you; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **Protected places:** never list, glob, search, read or write in `~/gov-os-workbench`; dev-tier material is used by `GOV_DEV_TIERS` by name only and cloned into a temporary folder. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase or tag. Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- **Disk and inodes (DEC-898), your share:** the ticket's budget is 20 GB and 1,000,000 files and folders for the lead and all workers together; **your share is at most 6 GB and 300,000 files and folders at any moment**, in your temporary folder. Keep `TMPDIR` as the sandbox sets it. Keep pytest's own retention; never pass a per-run `--basetemp` to a run of your own except inside a probe that tests the refusal, into a folder of your probe's own. **Pass `-o tmp_path_retention_policy=failed` on every pytest run you make** (DEC-905). Never run a whole folder of W1-07, W1-25, W1-26 or W1-27 at once (the lead has run them). Measure your temporary folder (`du -s --inodes`, `du -sh`) before and after any heavy probe and give the figures in your return's `evidence` line. If you pass your share, stop at once and return.
- **The machine:** before any run of more than a few cases, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`). Never run with `-x`.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try.** You never ask or notify the owner.

## What you read

- The ticket file `.tickets/DAEO-9nys.md`: its KPI lines, its body (rounds; roles and the acceptance files named for its test designers, DEC-907) and its `allowed_paths` (`tests/unit/close/**` (round 2), `tests/unit/guard/**`, `tests/conftest.py`). Its card: `docs/plan/WAVE_2_WBS.md` §2, W2-67.
- The sources and the decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-889 (item 7), DEC-892, DEC-898, DEC-899, DEC-904, DEC-905, DEC-906, DEC-907, DEC-866, DEC-491, DEC-385, DEC-399, DEC-114, DEC-456; MR-3. Lens I: `docs/assessment/2026-10/I3-retrieval-context-resume.md` F9, `docs/assessment/2026-10/I4-records-plan-rest.md` F1, F5, §2.1, §2.2.
- **The first review's finding, as it was given (F1, high; ordinary work: yes; loses work):** the end-of-run clean-up removed the base folder of a run still going in another Bash command, because each sandboxed Bash command runs in a PID namespace of its own while they share one `TMPDIR`, and the clean-up judged a run over when its `.lock` was not flocked and its pid was not found in the sweeper's own namespace. Shown for `gov close`'s own nested test runner, a run of a project of its own (not loading this conftest), and a suite run still in its first test's setup; under `tmp_path_retention_policy=none` no newer folders were needed. Also F2 (medium; ordinary yes; other): a killed run's folder was kept or removed by pid coincidence. Its rows F3 (the KPI 4 static guard does not see an f-string `--basetemp=`), F4 (the root conftest sits outside the guard's acceptance protection) and F5 (the KPI 4 exemption rests on a parameter's name) stay rows; you need not re-raise them unless something changed.
- **The answer to it:** test-design batch 5 (`165ff06d`: `tests/acceptance/W1-27/test_w2_67_sweep_namespaces.py`, `w2_67_ns_launch.py`, `w2_67_ns_probe.py`, the "Batch 5" section of `README-W2-67.md`), then the engineer's `c8674271` in `tests/conftest.py`: a suite run's controlling process holds a shared `flock` on its `.lock` from the moment its base folder is made and writes `.lock-held` beside it; the clean-up judges a run over only when its folder has no `.lock`, or its `.lock` can be locked exclusively and `.lock-held` is there, or its `.lock` names a pid at or above `pid_max`; every other folder is kept. The engineer reported, as a residual for round 2, that a nested project run killed by `gov close`'s time limit inside `tests/unit/close` leaves an unmarked folder that is now kept until pytest's three-day rule.
- **Round 1's change, and only it:** `git diff w2/integrate...HEAD` (`git log --oneline w2/integrate..HEAD`). Above all:
  - `tests/conftest.py` (new, engineer `75a64b28`, then `c8674271`): refuses a per-run `--basetemp` (opt-out `GOV_ALLOW_BASETEMP=1`), and at a run's end removes older base folders whose run is shown to be over, past pytest's retention of three;
  - `tests/acceptance/W1-07/w1_07_support.py` (`b20a481f`): `copy_working_tree` switches `gc.auto` off before its first commit;
  - `tests/unit/guard/test_decide.py` (`75a64b28`): the fixed `/tmp` folder becomes `tmp_path`;
  - the KPI tests `tests/acceptance/W1-27/test_w2_67_copies.py`, `test_w2_67_temp_folders.py` (with batch 4's exemption, `ceed1134`), `test_w2_67_basetemp_refusal.py`, and their READMEs (`README-W2-67.md`, `README-W2-67-fixtures.md`);
  - the revised weak cases in `tests/acceptance/W1-26/`, `W1-27/` and `W2-02/` (KPI 5), each with a `Rewrite-Reason`, and their READMEs `README-W2-67.md`.
- The untracked file `tests/acceptance/W1-27/w2_67_td4_plant.py` is a test designer's emptied plant that its sandbox could not remove; it is not part of the head.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work (for example: the conftest's clean-up removing a base folder that a live run, a concurrent session, a nested run, an xdist worker or a run that does not load this conftest still uses, in any PID namespace and at any point of its run; or removing anything outside pytest's own numbered base folders); check first that F1 is answered in every form the first review showed, and that the answer opens no new way to lose a folder;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open (for example: the `--basetemp` refusal passed by an ordinary run that gives one, or a refusal that stops ordinary runs of the suites or of `gov close`; a revised weak case that cannot fail for its fault, or an expectation lowered; a copy that still races gc; the KPI 4 guard's exemption wider than the refusal's own cases).

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

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

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), with nothing before them. **After them, the probe record's content** for the lead to commit (you write nothing): a first line `Verdict: pass` or `Verdict: fail`; the head you probed; step 0's result; the `gov.__file__` line; what you probed and found sound; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. The lead passes findings to a test designer; you repair nothing (MR-4). Say also your scratch figures, the read refusals met and whether you used `gov retrieve`.

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
