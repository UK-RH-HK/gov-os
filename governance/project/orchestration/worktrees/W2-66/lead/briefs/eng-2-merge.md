You are a fresh engineer. Ticket: DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`. The ticket's code is built; `w2/integrate` (with W2-07's close gates) has just been merged into this branch, and a new KPI line has come. Your job this round is the items under "The work" below, until the acceptance tests named there pass. Your budget is about 90 minutes (see "Time").

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-c1uz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`), `git log --oneline -1` (expect `85ed85b6`) and `git status --short` (expect nothing; inside the sandbox it may list entries such as `.bashrc`, `.gitconfig` or `.idea` that are character devices 1,3 owned by nobody: those are the sandbox's placeholders, not changes, and you go on). If anything else differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-66/`, `tests/acceptance/W1-30/test_w1_30_regression_scope.py` nor `tests/acceptance/W1-39/test_w1_39_copy.py`, by any tool (no Read, cat, grep, git show or diff of them; a search over `tests/acceptance` that would read inside them is the same read: narrow it to other folders). You may run those tests and read their results: names, pass or fail, and failure messages;** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take such a refusal as a refusal, never look for another spelling or form, search named folders instead (for example `src/gov/close`, `tests/unit/close`), and **count every refusal in your return**. Name the files you need under `governance/project/` one by one.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Keep the sandbox's own `TMPDIR` (do not replace it) and count it. Keep pytest's own temp-folder retention (three base folders); never a per-run `--basetemp` (the root `tests/conftest.py` refuses one). Pass `-o tmp_path_retention_policy=failed` on every pytest run you make (DEC-905). Remove any temp tree you make by hand as soon as you no longer need it. Measure your scratch (`du -s --inodes` and `du -sh` of your `TMPDIR` and of anything untracked you left in this worktree) before each long run and at the end, and give the figures in your return's `evidence` line. If you pass your share, stop the heavy work, clean what you can and return at once with the measure and its cause.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (tests run `gov close` only inside temporary projects they build), and nobody runs `docs/plan/tools/validate_s1.py`. Never write `governance/project/path-map.yaml` (a shared record no ticket writes; its `test_inputs` key is removed by the orchestrator at this ticket's merge, not by you).
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## Time

Your session is stopped at two hours and its return is then lost. **Commit after each item below** (each with the trailers below), before you run any long suite. If you reach about 80 minutes with items left, commit what you have and return with the items still to do named under `unresolved`; the lead resumes you for them.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md` (read-only): its KPI lines, above all the new one: "The close's pytest runs (its parallel run and its serial-only cases) pass -o tmp_path_retention_policy=failed, so a passing test's temp folder goes as the test ends and a failing test's stays; the evidence block names it [DEC-905, DEC-904 item 1]"; its `allowed_paths`; its body (`command.py`: "the calls into these, `--full`, and the record's lines only").
- `docs/DECISION_REGISTER.md`: DEC-903, DEC-904 (item 1), DEC-905, DEC-896, DEC-899, DEC-868 (items 1 and 3), DEC-135.
- W2-07's card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-07"), and its ticket file `.tickets/DAEO-r9ss.md`: "It shares `src/gov/close/command.py` with W2-66: W2-66 writes the record's evidence lines, W2-07 the gates."
- The code: `src/gov/close/command.py` as merged (the merge commit `03f470a5` and its message say how its conflict was resolved), W2-07's `src/gov/close/gates.py`, this ticket's `src/gov/close/select.py`, `evidence.py`, `nightly.py`, and `tests/unit/close/` (the builder tests, which must stay green).

## The interface (fixed by the test designers; follow it exactly)

Everything of the interface you built in the first round stands. The test designer of this round added:

In item 6 (the evidence block), after the `per_test_timeout` and `distribution` line:

   - `tmp_path_retention_policy`: `failed`, the value every test run of the close was given (item 9).

In item 8 (the nightly), the first bullet now reads:

   - Runs the full uncached regression on `<branch>`'s head (not the working tree) in the close's form (parallel,
     then the serial-only cases alone; the per-test limit; the distribution mode; the retention option, item 9),
     with JUnit XML.

New item 9:

9. **The retention option** (DEC-905, DEC-904 item 1): every pytest run a close makes (the acceptance run, the
   regression's parallel run, the serial-only cases afterwards) and every test run of the nightly is given
   `-o tmp_path_retention_policy=failed`, so a passing test's `tmp_path` goes as the test ends and a failing
   test's stays. The evidence block names it (item 6). *The observable:* a fixture test reads its run's
   `config.getini("tmp_path_retention_policy")` (`failed`) and `config.option.override_ini` (holding
   `tmp_path_retention_policy=failed`), and whether its `tmp_path` is still there after the close. pytest's own
   count of three base folders stays: the fixture's refused close has two failing runs.

## The work (commit after each item)

1. **The record key and the local name the merge left double.** In `run()` of `src/gov/close/command.py` two values are named `evidence`: W2-07's (the paths `_gates.check_evidence` judged for a research, audit, integration or coordination ticket, given to `_judged_by`) and this ticket's (`_scope_evidence(root, scope)`, the evidence block). This ticket's assignment overwrites W2-07's before `_judged_by` reads it, and both then write the key `evidence` of the close record and of the answer (`_evidence.KEY`, and `_judged_by`'s `judged["evidence"]`, applied after). W2-07's card gives the record's evidence lines to this ticket. Make both survive: the evidence block stays under `evidence` (the acceptance tests read it there, in the record, `result.evidence` and `error.details.evidence`); W2-07's judged paths are still stated in the record and the answer, under a key of their own that does not clash, and still reach its judgement unchanged. Keep the change to these lines; name the key you chose in your return. W2-07's acceptance suite `tests/acceptance/W2-07` must stay green.
2. **The retention option (DEC-905, the new KPI line).** Every pytest run a close makes (the acceptance run, the regression's parallel run, the serial-only run afterwards, and a load-sensitive red's run alone) and every run of the nightly command passes `-o tmp_path_retention_policy=failed`; the evidence block names it, as the interface above says.

Builder tests for what you change go in `tests/unit/close/test_select*.py`, `test_nightly*.py`, `test_evidence*.py` (regression evidence only, MR-3). Proportion (DEC-135): no code beyond the KPI lines. Never make a gate fail open: every failure KPI line must still refuse or widen to the full regression, and every one of W2-07's gates must still run and refuse as before.

## What you write

Only inside the ticket's `allowed_paths`: `src/gov/close/command.py` (only the calls into this ticket's modules, `--full`, the record's lines and the retention option; never W2-07's gate functions), `src/gov/close/select.py`, `src/gov/close/evidence.py`, `src/gov/close/nightly.py`, the builder tests above. Not the test map, not the report `docs/research/W2-66-scoped-close.md` (a later round writes it; its three cases in `test_w2_66_research.py` stay red), never the acceptance tests (MR-3): a test you think is wrong is returned as a package (its name, its failure message, why), never edited and never worked around.

## Running the tests

Run, in the foreground, each to its end, never with `-x`, each with `-o tmp_path_retention_policy=failed`:

- the acceptance suites of this round: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m pytest tests/acceptance/W2-66 tests/acceptance/W1-30/test_w1_30_regression_scope.py tests/acceptance/W1-39/test_w1_39_copy.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`; every case must pass except the three report cases (`test_w2_66_research.py`);
- the suites your change can break, which must stay green: `tests/unit/close`, `tests/acceptance/W2-07` and `tests/acceptance/W1-30` (with `-n auto`), `tests/acceptance/W2-01` and `tests/acceptance/W2-53` (they run `gov close` in fixture projects);
- report the counts of each. The lead runs the full verification afterwards.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-c1uz" --trailer "Role: engineer" --trailer "Implements: DEC-905" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

(item 1 uses `Implements: DEC-899`). Check `git log --oneline -3` and `git status --short` after each commit; nothing of yours stays uncommitted.

## Return

Your commits' hashes with their trailers; the files changed; the lines added and removed (`git diff --stat 85ed85b6 HEAD`); the key you chose in item 1; the tests you ran with their counts; the sandbox check; the `gov.__file__` line; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; your scratch measures; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

Your return is one message. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
