You are a fresh independent test designer (MR-3). Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-05-tests` on branch `w2/W2-05-tests`, made from the ticket's head `f217353e59fa`. This is the ticket's one repair batch (DEC-906): two acceptance-test constructions that no longer reach what they test, because the code or the repository they lean on changed as decided. You change how each case is built, never what it expects.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"`: a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh`: git's own writes. They **must work**. If either fails, stop there and return with the exact error (you could not commit).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0z8c`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05-tests` and `w2/W2-05-tests`) and `git rev-parse --short=12 HEAD` (expect `f217353e59fa`). If anything differs, stop and say so. Inside the sandbox `git status` shows placeholder device files at the worktree root (`.bashrc`, `.gitconfig`, `.mcp.json` and the like, character devices `1, 3`): they are not real; never stage them.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
  - **For you, "this worktree" is the tests worktree:** use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05-tests/src` on every run, and quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05-tests/src python3 -c "import gov; print(gov.__file__)"` (it must point under `/home/usain/gov-os-worktrees/W2-05-tests/src/`). Its `src/` is the ticket's code at `f217353e59fa`, the same as the ticket's own worktree. Run nothing from `/home/usain/gov-os-worktrees/W2-05`. The suites' support puts the `src/` beside the test files first on the `PYTHONPATH` of the processes it starts; keep it so.
- **What you may not read (DEC-820 (c) and (d)).** (c) Never read this ticket's implementation: no file that `git diff --name-only w2/integrate...HEAD` names (run it in your worktree and keep to it), other than the tests under `tests/acceptance/`. That list includes `src/gov/guard/decide.py`, `src/gov/guard/containment.py`, `src/gov/util/gitenv.py`, `src/gov/adapters/portability.py` and others. Nothing in the ticket's worktree `/home/usain/gov-os-worktrees/W2-05`, by any tool. The existing code as it stands on the integration branch you may read with `git show w2/integrate:<path>`; the guard's behaviour as this ticket changed it is stated below, and that is what you test. (d) Never read the hidden half of any evaluation set.
- **Memory first (DEC-836, DEC-860, DEC-859, DEC-963).** Use `gov retrieve` for what you need to know before reading files at random, **on the integration branch's store only**, never this ticket's store: `cd /home/usain/gov-os-worktrees/W2-00-store && timeout 300 gov retrieve "<question>" --json` (a read; that store holds `w2/integrate` as of its last refresh; for what changed since, read `w2/integrate` itself with `git show w2/integrate:<path>`). A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget, never one giant query or context. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **P-R1:** drop unread any result under this ticket's implementation paths (its `allowed_paths` outside `tests/acceptance/`: `src/gov/**/*.py`, `src/gov/util/gitenv.py`, `lefthook.yml`, `template/lefthook.yml`, `template/.rulesync/hooks.jsonc`, `tests/unit/gitenv/**`, `docs/research/AR-2-git-sweep.md`), and name in your return any such result you were served. In the sandbox a call may hang on the embedder: the `timeout` caps it. Say in your return which questions you asked.
- **Read refusals (DEC-849).** Until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead. Count the refusals you met and give the count in your return.
- **The guard has five rules now (ACT 1, DEC-953 item 2, DEC-954):** the implementer never writes acceptance tests; reviewers and auditors write only their own records; no reads of the hidden half of an evaluation set or of the held-out material; no reads of secrets; no installs without the owner. Shell command forms are no longer refused by the guard, but the tool's own command checker refuses here-documents, `$TMPDIR` in compound commands and `rm` (a permission prompt nobody can answer): write long scripts with the Write tool under your temporary folder and run them; leave folders pytest does not remove for the end of your session. Report every refusal you meet (its time, the command's form in one line, the reason it gave, and whether it was one of the five rules or a false positive).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: keep each run within that (under this week's load W1-02 takes 6 to 7 minutes per ten files: run it in parts of at most about ten files). Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- **Protected material (DEC-820).** Never read, print, search, diff or copy the held-out material under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never print a secret. **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees. Every hook test runs in a temporary repository built from scratch, with its own stand-in `.claude/settings.json` where one is needed; no test reads the real one.
- Inside a launched session `.gov-runtime/freeze` and some dotfiles show as placeholder device files: conclude nothing from them, and never add them to a commit.
- No subagents. Install nothing: an install you need is raised as a P1 escalation in your return (DEC-957). Never write `.gov-runtime/**`. Never run `gov close`, `gov adopt`, `gov pause`, `gov rebuild` or `gov checkpoint`.
- **You write only these files:** under `tests/acceptance/W1-02/`, `w1_02_deadline_support.py`, `test_w1_02_deadline.py`, `test_w1_02_deadline_in_time.py`, `test_w1_02_unknown_tools_failure.py` and `README.md`; under `tests/acceptance/W2-05/`, `test_w2_05_hooks_source.py` and `README.md`. No other path.
- **Disk and files (DEC-898).** Your share of the ticket's budget is 3 GB and 150,000 files and folders outside the tracked tree. Your temporary folder is the one `gov launch`'s sandbox set: keep it (do not set `TMPDIR` yourself). Keep pytest's own temp retention (never `--basetemp`). Measure `du -sh` and `du -s --inodes` of your temporary folder at the end and give the figures in `evidence`.
- **Row W2-L423's rule (DEC-911).** In anything you write, give commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- Never ask or notify the owner (no question box, no `owner-ping`): a question comes back to the lead as a package in your return. On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status `AUTH_REQUIRED`.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The decisions in `docs/DECISION_REGISTER.md`: DEC-951 (item 2), DEC-580, DEC-783 (item 2), DEC-802, DEC-805, DEC-953 (item 2), DEC-906, DEC-136, DEC-462, DEC-491, DEC-866; row W2-L160 in `docs/plan/WAVE_2_LIST.md`.
- W1-02's suite as the previous designer left it (commit `a8b9cd07e1ae`, in your head): `tests/acceptance/W1-02/README.md` (its new section on the deadline routes), `w1_02_deadline_support.py` and the three test files.
- W2-05's hooks-source cases: `tests/acceptance/W2-05/test_w2_05_hooks_source.py` and its rows in `tests/acceptance/W2-05/README.md`.

## Task A: W1-02's five Bash-bookkeeping cases (P-B1-2, DEC-802)

**What changed.** The previous designer (`a8b9cd07e1ae`) moved the look-up's cases to routes the guard still takes, but kept a stand-in `git` first on `PATH` for the cases whose slow step is the guard's **Bash bookkeeping** (the git calls the hook makes around a Bash call: its record of the work tree before the command). Since then the ticket's batch 2 gave that bookkeeping git **by the same absolute path as the freeze look-up** (the system folders `/usr/bin`, `/bin`, `/usr/local/bin`, `/opt/homebrew/bin`, never by name from `PATH`; it refuses, never passes, when no git is found). So the stand-in is never started, and these five are red at `f217353e59fa` for that reason alone (the lead ran them outside the sandbox):

- `test_w1_02_deadline.py::test_a_decision_still_running_at_the_deadline_is_refused[a-Bash-call-by-the-orchestrator-whose-every-program-takes-a-few-seconds]`: allowed after 0.4 s;
- `test_w1_02_deadline.py::test_the_deadline_s_refusal_carries_nothing_of_the_call` and `::test_nothing_the_hook_started_is_left_running_after_its_answer`: through that same call;
- `test_w1_02_deadline_in_time.py::test_a_step_that_ends_before_the_deadline_leaves_an_allowed_call_allowed[a-Bash-call-by-an-engineer]` and `::test_a_tiny_limit_named_stops_no_work[a-Bash-call-by-an-engineer-with-a-tiny-limit-named-and-a-slow-step]`: "the hook neither started the stand-in program nor waited on the repository's configuration".

**What to do.** Build each of them on a route the guard still takes, as the others now are: the support's named pipe in the hook's bookkeeping folder, its late input, or a repository setting that makes the real git wait (the `.git/config` pipe you will find in the support). The real git of both the look-up and the Bash bookkeeping reads the project's own repository configuration. Never a `git` first on `PATH`, a slow machine, a weaker rule or a switch of the product. **No expectation lowered, no case removed:** each case keeps what it showed (the orchestrator's Bash call whose every step is slow is refused at DEC-580's 20 s deadline, with its lower bound, by a slow step the look-up's 15 s does not cover; an allowed engineer's Bash call with a step that ends in time stays allowed; a tiny limit named stops no work; the refusal carries nothing of the call; nothing the hook started is left running after its answer). The failure message for an allowed call ("the guard keeps no deadline of its own") stays reachable. If the stand-in on `PATH` is then used by no case, remove it from the support. If a case cannot keep its expectation on an allowed route, do not lower it: return a package.

The lead is passing the previous designer's package P-W1-02-CHILD (the grandchild check) to the orchestrator: leave it as it is.

## Task B: W2-05's "order of the hooks" case (ACT 1, DEC-953 item 2)

`test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the order of the hooks of an event]` builds its two sources from this repository's live `.rulesync/hooks.jsonc`, and reaches into its `postToolUse` event. The owner's ACT 1 (`6c36c7b5`, DEC-953 item 2) took `postToolUse` and `postToolUseFailure` out of the repository's hooks source (the template, `template/.rulesync/hooks.jsonc`, keeps both), so the case now fails in its own construction, not in the check. Build its sources so that it tests what it says whatever the repository's live hooks source holds today (for example, from the template's source, or from a fixed source written in the case): two sources that differ **only** in the order of the hooks of one event must leave adapter-portability green. Lower nothing; keep its id. Make the other cases of that file that read the live source robust in the same way **only** where they too fail in their construction for this reason (say which).

**Do not change** `test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`: it is red because the two real sources now differ by ACT 1; that is a decision the orchestrator holds (package H). Say in the README that it is red for that reason until that decision.

## Runs (outside nothing: you run inside your sandbox; say where a case fails for the sandbox alone)

- **Before you change anything:** the three deadline files, and `tests/acceptance/W2-05/test_w2_05_hooks_source.py`:

      PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05-tests/src python3 -m pytest tests/acceptance/W1-02/test_w1_02_deadline.py tests/acceptance/W1-02/test_w1_02_deadline_in_time.py tests/acceptance/W1-02/test_w1_02_unknown_tools_failure.py tests/acceptance/W2-05/test_w2_05_hooks_source.py -q -p no:cacheprovider -rfEs

  Report the counts and each red with its reason, as "at `f217353e59fa`, before my change".
- **After your change:** the same, then W1-02 whole (in parts of about ten files) and W2-05 whole, to the end, never with `-x`. Expected: the five W1-02 cases and the order case green; no other case changed state but these; `test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` still red (package H); the load-sensitive `test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms` may be red under load (re-run alone; name it); W2-05's cases that fail inside a launched session for a reason not their own (five retrieval-regression cases without an embedder; the code-index case, whose daemon folder is read-only in the sandbox) are named as such.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Stage only the files you changed, by name (never `git add -A` or `git add .`). One commit, the trailers in the final block (DEC-182, DEC-476, DEC-491), `Implements:` holding decision ids only (DEC-927 item 2), one `Rewrite-Reason:` per task; each changed case also names its reason in its docstring or a comment beside it:

    git commit -m "W1-02 and W2-05 (via DAEO-0z8c): the Bash bookkeeping's cases and the hooks-order case built on routes that still reach them" --trailer "Task: DAEO-0z8c" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-951, DEC-802, DEC-953, DEC-906" --trailer "Rewrite-Reason: DEC-951 (P-B1-1); DEC-802 (P-B1-2): the Bash bookkeeping starts git by absolute path; W2-L160" --trailer "Rewrite-Reason: DEC-953 item 2 (ACT 1): the repository's hooks source has no postToolUse; the case's construction, not its expectation" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short` and quote them.

## Return

Your commit's hash (12 digits); each revised case with what it now does (its slow step or its sources, what it asserts, its bounds); the lines added and removed; every run's counts and every red case with its reason; the `gov retrieve` questions you asked and any P-R1 result you were served; the read refusals you met; any package. Put these in the fields below.

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

Put the sandbox check's result (a) and (b) first in `evidence`. After the twelve fields, a section `guard_refusals:` (one line per refusal, or `none`) and the count of read refusals.

Refused twice for the same call: stop and say so.
