You are a fresh reviewer (the QA engineer, role `independent-auditor`). Ticket DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`, at the head `ba807a032603`. The ticket's earlier work passed its review at `ecbdf689f283` (probe record `docs/probes/DAEO-0z8c/PR-DAEO-0z8c.md`). This is a **short review of one new round only** (DEC-970: package I (b) and P-W2-05-DRIFT-BASE): you judge that round's commits, not the earlier work. You read the code, the tests and the results below; you re-run no suite (DEC-959 item 1), and run the code only to probe behaviour the tests miss. You write nothing in the repository.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"`: a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh`: git's own writes. They **must work**. If either fails, stop there and return with the exact error.

These two writes of step (b) are the only writes you make in the repository; they change no file and no branch.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-0z8c`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`) and `git rev-parse HEAD` (expect a full commit id beginning `ba807a032603`; give it in full in your return: it is the probe record's `probed_commit`). If anything differs, stop and say so. Inside the sandbox `git status` shows placeholder device files at the worktree root (`.bashrc`, `.gitconfig`, `.mcp.json` and the like, character devices `1, 3`): they are not real; conclude nothing from them.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **What you may read.** Everything: the code, the tests, the history (DEC-820: reviewers read everything), except (a) secrets and keys, never printed; (b) the contents of the held-out material (never read, print, search, diff or copy it, never type its path, DEC-525); (d) the hidden half of any evaluation set. Never read or name the qualification oracle. Never read `.claude/settings.json` or `.claude/settings.local.json`, anywhere, and nothing under `~/.claude/`. Run no glob, search or listing over `governance/project/`: name the files you need there one by one (DEC-508).
- **Memory first (DEC-836, DEC-859, DEC-860).** Use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 300 python3 -m gov.cli.main retrieve "<question>" --json`. A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget, never one giant query or context. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. The lead is rebuilding this worktree's store beside you, so an answer may be stale or unavailable for a while: then read the named files. Say in your return which questions you asked.
- **Read refusals (DEC-849).** Until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead. Count the refusals you met.
- **The guard has five rules now (ACT 1, DEC-953 item 2, DEC-954):** the implementer never writes acceptance tests; reviewers and auditors write only their own records; no reads of the hidden half of an evaluation set or of the held-out material; no reads of secrets; no installs without the owner. The tool's own command checker refuses here-documents, `$TMPDIR` in compound commands and `rm`: put a long probe in a script file under your temporary folder and run it. Report every refusal you meet (time, the command's form in one line, the reason it gave).
- Run everything in the foreground, one command after another. A foreground command is killed after 10 minutes: keep each probe within that. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no commit, no amend, no rebase, no merge, no push, no tag in this worktree.
- Write no file of the repository. Your probes run in your temporary folder (the one `gov launch`'s sandbox set; do not set `TMPDIR`), and every temporary repository you need is built there from scratch with `git init`.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package (with the `PYTHONPATH` above) or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Never run `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees.
- Never run `gov close`, `gov adopt`, `gov pause`, `gov rebuild` or `gov checkpoint` against this worktree or the main tree. Install nothing (an install you need is a P1 escalation in your return). No subagents.
- **Disk (DEC-898).** Your share of the ticket's budget is 3 GB and 150,000 files and folders outside the tracked tree. Measure `du -sh` and `du -s --inodes` of your temporary folder at the end and give the figures in `evidence`.
- **Row W2-L423's rule (DEC-911).** In anything you write, give commit hashes as 12 digits (the probed head in full only where asked), and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- Nobody asks or notifies the owner. On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status `AUTH_REQUIRED`.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6).

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

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-970 (its W2-05 line; the register's "`GOV_CONFIG_GLOBAL`" means git's `GIT_CONFIG_GLOBAL`), DEC-710, DEC-580, DEC-777, DEC-804 (item 3), DEC-805, DEC-953 (item 2); row W2-M161 in `docs/plan/WAVE_2_LIST.md`; ADR-0001.
- The previous review's record, `docs/probes/DAEO-0z8c/PR-DAEO-0z8c.md` (its package I finding and its DRIFT-BASE note).
- **This round's change** (`git diff 0cfa8684f720..ba807a032603`):
  - engineer `b173cb5792e2` (package I (b): `runner_env` in `src/gov/util/gitenv.py`; `_started` in `src/gov/close/command.py`; `_bisect` in `src/gov/close/nightly.py`; unit tests `tests/unit/gitenv/test_runner_env.py`, `test_batch2.py`; sweep rows) and `ee4e3bae9333` (sweep row 66, `gov release`, open);
  - test designer `f5968e9cffb7` (merged as `8be7828faa72`): the drift cases of `tests/acceptance/W2-05/test_w2_05_hooks_source.py` now build their base pair from one fixed source and check it green before planting; README;
  - the lead's checkpoint record `ba807a032603`.

## Results so far (judge from these; do not re-run the suites)

- Engineer, sandboxed, at `ee4e3bae9333`: `tests/unit/gitenv` 39 passed, 1 failed (package H's `test_this_repository_s_two_hooks_sources_agree`); `tests/unit/close` 477 passed. Package I's measure: `tests/unit/containment/test_dec_572_lift.py` run through `_started` with the close's environment: 4 passed under the new form, 3 failed and 1 passed under the old `/dev/null` form. W2-05 acceptance: 41 passed, 7 failed (package H's case, five retrieval-regression cases with no embedder in the sandbox, the code-index case whose daemon folder is read-only in the sandbox).
- Test designer, sandboxed: a mutation check (every plant made to do nothing) showed `[an event whose matcher differs]` passing with nothing planted before the change, and all five drift cases failing with nothing planted after it. The hooks-source file: 9 passed, 1 failed (package H) before and after.
- The lead's scoped verification is running beside you; you will not see it.
- **Known, not new (classify only if this round changes them):** package H (ACT 1 against DEC-805 item 2, the owner's); P-W2-05-R3-1 (the owner's); `gov release` (W2-16's `src/gov/release/__init__.py`, merged but not closed, so W2-05 may not change it under DEC-777; recorded as sweep row 66, open).

## What you probe

- **`runner_env` against package I (b):** the test run gets only the person's `user.name`, `user.email` and `init.defaultBranch` from their global files (the XDG file and `~/.gitconfig`, the later winning, as the caller's `HOME` and `XDG_CONFIG_HOME` name them); nothing else of the person's configuration (`trace2.*`, `core.*`, `include`/`includeIf`, aliases, hooks path, credential helpers, `safe.directory`) reaches it; reading the person's files lets no setting there act (a planted `trace2.eventTarget` writes nothing); a repository's own configuration still wins; values with quotes, backslashes, `#`, `;`, leading or trailing spaces or newlines survive as git would read them, and no value can inject another key or section into the generated file; no `GIT_*` variable of the caller reaches the run; the file is removed when the run ends, on a time-out and on an interrupt too; nothing is left in the project.
- **W2-M161's guarantee still holds:** a trace setting the person planted in `~/.gitconfig` reaches no test run of `gov close` or the nightly; the system configuration is still unread.
- **`_bisect`:** `bisect start`, `run` and `reset` get the same environment as a test run; arguments, paths and order unchanged; the generated file lives as long as the bisect.
- **Fail closed:** when the temporary folder cannot be written, or git cannot be found to read the person's files, the run does not go ahead unpinned, and no gate answers "pass" because of it.
- **The DRIFT-BASE edit:** no expectation lowered, no case removed, ids kept; each drift case is red only because of its plant (its control requires the base pair green); the not-drift cases and package H's case unchanged.

And, as before, behaviour the tests miss that could lose work or make the guard or a gate fail open in this round's change. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

Before you return, run `git status --short` and `git log --oneline -1` and quote them: the status must show nothing but the sandbox's placeholder files, and the head `ba807a032603`.

## Return

The head you probed (in full); your judgement, `pass` or `fail` by the rules above (fail only for a finding with "Ordinary work: yes" and "Consequence: fails open" or "loses work"); and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines. Say also what you probed and found sound, and give the probe record's content (front matter fields `judgement` and `probed_commit`, the method, the findings) in your return: the lead writes the record from it. You repair nothing (MR-4).

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

Put the sandbox check's result (a) and (b) first in `evidence`, and your judgement (`judgement: pass` or `judgement: fail`) and your findings in `work_completed` and `discoveries`. After the twelve fields, a section `guard_refusals:` (one line per refusal, or `none`) and the count of read refusals.

Refused twice for the same call: stop and say so.
