# Brief: independent test designer, DAEO-drhj (W2-104), run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-drhj` (W2-104), profile STANDARD. You work only in
the tests worktree `/home/usain/gov-os-worktrees/W2-104-tests` on branch `w2/W2-104-tests` (DEC-963); you never read
or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-104`. You write the ticket's acceptance tests from
its KPI lines and its sources, in parallel with the engineer (DEC-959 item 7), and you show them red against the
ticket's base.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-drhj','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-drhj`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-104-tests` and
  `w2/W2-104-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and
  nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
  *For you, in the tests worktree, "this worktree" is `/home/usain/gov-os-worktrees/W2-104-tests`:* your red run uses
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104-tests/src` and you quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104-tests/src python3 -c "import gov; print(gov.__file__)"`. Your tests
  must find the code under test from their own location (the repository the test file sits in, its `src/`), never
  from a fixed path and never from an installed copy, so that once the lead merges them into
  `/home/usain/gov-os-worktrees/W2-104` they exercise that worktree's code. The README says how.
- **Reads (DEC-820, Policy 2):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of
  the held-out qualification material (never read, print, search, diff or copy the held-out file under
  `governance/project/`, never type its path; never read or name the qualification oracle); **(c) the counterpart's
  work on this ticket: you never read this ticket's implementation**, that is any file that the branch `w2/W2-104`
  changes against its base (`git diff --name-only w2/integrate...w2/W2-104` names them), other than your own
  tests, by any tool, and you never read anything under `/home/usain/gov-os-worktrees/W2-104/src/gov/skilleval/` or
  `/home/usain/gov-os-worktrees/W2-104/tests/unit/skilleval/`; **(d) the hidden half of any evaluation set** is never
  read by whoever is measured by it.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  **only from the integration branch's store**: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve
  "<question>" --json`. Never this ticket's worktree's store. For what changed on `w2/integrate` since that store's
  last refresh, read `git show w2/integrate:<path>`. **P-R1:** drop unread any retrieve result whose path is under
  `src/gov/skilleval/`, `tests/unit/skilleval/` or `governance/project/skill-imports.yaml` (this ticket's
  implementation paths), and name in your return every such result you were served. **Never one giant query
  (DEC-860):** a large question goes in batches (`--batch-size`, then `--continue <token>`), ranked and stacked
  within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`,
  `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root,
  `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders
  instead. Count the refusals you met and report them. Run no glob, search or listing over `governance/project/`;
  name the files you need there one by one. Never read `.claude/settings.json`.
- **Command forms the guard can read (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at
  literal absolute paths; anything longer than a line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-104-tests/.gov-runtime/scratch/` and you run that file. A refused form is not
  retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses
  something you needed, do not work around it: return it as a package.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A
  test that needs a repository or project builds a temporary one from scratch under pytest's `tmp_path`. Never write
  in `~/gov-os-workbench`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file:
  conclude nothing from it. Install nothing (an install you need is a P1 package in your return). No subagents that
  write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit
  hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex
  string for a token.
- **Never a real model call and never a key:** your tests use a stub model only (below). No test may reach the
  network or start the real `claude` program; build each test's `PATH` so that only your stub and system folders
  (`/usr/bin`, `/bin`) are on it. A key you plant is an obviously fake string you make up.
- **Scratch budget (DEC-898):** your share is 4 GB and 200,000 files and folders, outside the tracked tree (your
  worktree's untracked and ignored files and your temp folder). Use `TMPDIR=/tmp/gov-os-lead-W2-104` for every
  test run. Keep pytest's own temp retention (never `--basetemp`); add `-o tmp_path_retention_policy=failed` to your
  runs. Remove what you made as soon as you no longer need it. Measure at the end (`du -s --inodes` and `du -sh` of
  your worktree's untracked files and of anything you made under `/tmp/gov-os-lead-W2-104`) and give the figures.

## What you read

- The ticket file `.tickets/DAEO-drhj.md` (read-only): its KPI lines (below, verbatim), its `allowed_paths` and its
  sources.
- The sources: DEC-959 (items 5 and 7) and DEC-820 in `docs/DECISION_REGISTER.md`; ROLES-RESEARCH-1 §5.3 item 13 and
  its lines on the three scenarios (`governance/project/orchestration/packages/ROLES-RESEARCH-1.md`, read by name).
- The skill template and the scenario form, from W2-11 (landing today): read them on `w2/integrate` once landed,
  until then from `w2/W2-11`, read only: `git show w2/W2-11:template/governance/kernel/templates/skill.md` and an
  example `git show w2/W2-11:template/governance/kernel/skills/qa-review/scenarios.md`.
- The command-module convention, as it stands on the base: the docstring of `src/gov/cli/main.py`
  (`git show w2/integrate:src/gov/cli/main.py`): the `--json` envelope `{ok, command, result, error?, session}`, exit
  codes 0, 1, 2 reserved, a command's own exit codes from 3.
- How existing acceptance suites start `gov` against the code of the repository they sit in (for example
  `tests/acceptance/W1-07/` and its conftest), as a model for yours.
- DEC-747 and DEC-970, and the commit `1bf0c1d2` (W2-96's designer recording `accept` in the earlier suites' command
  lists), for the revision below.

## The behaviour to test: the KPI lines, verbatim

Success:
1. `gov skilleval <skill>` runs each of the skill's three committed scenarios on a fresh session with only that skill
   loaded (the model and effort from the role defaults), judges each against its stated pass line, and writes a
   scenario record (skill version, scenario, verdict, cost, time) beside the skill; it is the evidence CIT-E reads
   [DEC-959 item 5, ROLES-RESEARCH-1 §5.3 item 13]
2. An imported skill (Anthropic's collection or another source) is adopted only when
   governance/project/skill-imports.yaml records its source, version, licence and the licence's verdict for this
   use, and its three scenarios pass; the harness refuses to mark an import adopted otherwise [DEC-959 item 5]
3. A scenario run that cannot reach a model (no network, no key) is recorded as not run with its cause, never as a
   pass; the harness reads no secret and prints none [DEC-959 item 5, DEC-820 (a)]
4. Planted skills with a passing and a failing scenario give the expected verdicts, in a temporary project, with a
   stub model [DEC-959 item 5]

Failure:
- F1. A scenario reported as passing that did not run, or failed.
- F2. An import marked adopted with no licence record or a failing scenario.
- F3. A secret read or printed.

## The public contract (set by the lead for both you and the engineer; test through it only)

The engineer builds to this same contract in parallel. Test only what it states; where it leaves something open,
do not test it. If a KPI line cannot be tested through it, return a package rather than guess.

**The command.** `gov skilleval <skill> [--adopt] [--model <model>] [--effort <effort>] [--timeout <seconds>]`
plus the common `--json` and `--root <project>`. `<skill>` is the skill's folder, as a path relative to the project
root (or absolute). `gov --help` offers `skilleval`, and `gov skilleval --help` exits 0 and names it.

**A skill folder** holds `SKILL.md` (front matter with `name` and `version`) and `scenarios.md`, which holds exactly
three scenarios, each a heading `## <n>. <title>` (n = 1, 2, 3) followed by three bullets
`- **Situation:** …`, `- **Expected:** …`, `- **Pass line:** …` (the form of W2-11's `scenarios.md` files).

**The model.** A scenario's session and its judgement are each made by running the executable named `claude` found on
the `PATH` that `gov` runs with, as a new process (never `--resume` or `--continue`), with the arguments
`-p --model <model> --effort <effort> --output-format json` among its arguments and the prompt on its standard input.
It must print one JSON object on standard output with `result` (the reply text), `is_error` (a boolean) and
`total_cost_usd` (a number), and exit 0. The default model and effort are `claude-opus-5-5` and `high` (DEC-839's
worker defaults); `--model` and `--effort` replace them.
- The session's process runs in a new temporary folder outside the project; that folder's `.claude/skills/` holds
  exactly one folder, the evaluated skill's, with its `SKILL.md`, and **no `scenarios.md`** (the session never sees
  its own pass lines). The session's prompt contains the scenario's Situation text.
- The judgement is a second, separate process whose prompt contains the scenario's Pass line, its Expected text and
  the session's reply; the verdict is read only from the judgement's reply: its last line matching
  `VERDICT: PASS` or `VERDICT: FAIL`.
- A stub for tests: a small executable script named `claude` in a folder your test puts first on `PATH`. It may decide
  its reply from marker words you plant in a scenario's Situation and Pass line (both prompts carry them, and the
  session's reply, which you choose, is passed into the judgement's prompt), and it may log its arguments and its
  working folder to a file of your test's for inspection. The harness passes its environment through to the
  executable (the real program needs its own credentials); do not test that the environment is stripped.

**The verdicts.** Each scenario ends `pass`, `fail` or `not-run`:
- `pass` only when the session and the judgement both ran and the judgement's verdict line says PASS;
- `fail` when the judgement says FAIL, or its reply has no verdict line;
- `not-run`, with a `cause` (one line), when a needed model process could not be run or did not answer as above:
  no `claude` on the `PATH`, a non-zero exit, output that is not that JSON object, `is_error: true`, or a run past
  `--timeout` seconds (default 900). A not-run scenario is never a pass.

**The scenario record, beside the skill.** Each run appends one entry per scenario to `scenario-records.yaml` in the
skill's folder (a YAML map with the key `records`, a list; earlier entries are kept). Each entry has at least:
`skill` (the name), `skill_version`, `scenario` (1 to 3), `title`, `verdict` (`pass` | `fail` | `not-run`), `cause`
(a string, or null for a pass), `cost_usd` (a number, or null when not run), `seconds` (a number, the wall time),
`model`, `effort`, `run_at` (UTC, ISO 8601).

**The envelope.** With `--json`, `result` holds `skill`, `skill_version`, `scenarios` (a list of maps with
`scenario`, `title`, `verdict`, `cause`, `cost_usd`, `seconds`), `record` (the record file's path) and `adopted`
(true or false with `--adopt`, null without).

**Exit codes.** Without `--adopt`: 0 when all three passed; 3 when any scenario failed; 4 when none failed and any
was not run; 5 when the skill cannot be evaluated (no `SKILL.md`, no `version`, no `scenarios.md`, or not exactly
three complete scenarios): then nothing is run and nothing is recorded. With `--adopt`: 0 when the import was
adopted; 6 when adoption was refused; 5 as above.

**Imports.** `governance/project/skill-imports.yaml` in the project is a YAML map with the key `imports`, a list of
entries, each with `name` (the skill's front-matter `name`), `source`, `version`, `licence`, `licence_verdict` and
`adopted` (a boolean). `gov skilleval <skill> --adopt` marks the entry whose `name` is the skill's name
`adopted: true` only when the entry exists, its `source`, `version` and `licence` are non-empty, its
`licence_verdict` is exactly `allowed`, and all three scenarios pass in that run; otherwise it refuses (exit 6), the
entry, if there is one, ends with `adopted: false`, and other entries are unchanged. Whether it runs the scenarios
before refusing for a missing or non-allowing licence record is not part of the contract. Without `--adopt` the
harness never changes `adopted`.

**Secrets.** The harness reads no secret and prints none: a fake key you plant (in the environment, or in a
secrets-like file in the temporary project) never appears in `gov`'s standard output or error, nor in any record it
writes, including when the stub prints that key on its own standard error and fails.

## What you write

- Only inside `tests/acceptance/W2-104/` in the tests worktree, plus this one revision of earlier suites: **the new
  command is recorded in the tests' command list (DEC-747)**: add `skilleval` to the earlier acceptance suites that
  hold the set of recorded `gov` commands, the way commit `1bf0c1d2` added `accept` (W1-07's
  `w1_07_support.py`, its recorded-commands case and README, W1-32's command-set case, and any other suite that
  holds that set as an exact list; name each). Touch only the lines of that list. That revision carries
  `--trailer "Rewrite-Reason: DEC-747: the new gov command skilleval is recorded in the tests' command list"`.
- In proportion (STANDARD): every KPI line's success and failure plus the key edge cases; no combinatorial
  expansion beyond what a KPI demands.
- Behaviour through the public contract above, never internals: run `gov` as a process against a temporary project
  you build under `tmp_path`, with planted skills and the stub model. Deterministic, no network.
- A `README.md` in `tests/acceptance/W2-104/` that maps each KPI line (success 1 to 4, failure F1 to F3) to its tests
  and gives the expected red reason of each, and says how the tests find the code under test.
- Red first: run your tests to the end, never with `-x`, against the base:
  `TMPDIR=/tmp/gov-os-lead-W2-104 PYTHONPATH=/home/usain/gov-os-worktrees/W2-104-tests/src python3 -m pytest tests/acceptance/W2-104 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  in `/home/usain/gov-os-worktrees/W2-104-tests`. They fail for the reason the README states (no `skilleval`
  command on the base). Run the revised earlier suites too and report what they show.
- A KPI line you find ambiguous or a dispute is never a guess: return it as a package (question, why now, options,
  impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in the tests worktree, with the trailers in the final block (DEC-182, DEC-476), one
commit for `tests/acceptance/W2-104/` and one for the earlier suites' revision:

    git commit -m "W2-104 tests: <subject>" --trailer "Task: DAEO-drhj" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959,DEC-820" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

(the revision's commit: `--trailer "Implements: DEC-747,DEC-959"` and the `Rewrite-Reason` trailer above).

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start
of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them.
Include: the sandbox check's result first in `evidence`; your commits' 12-digit hashes; the test count; the KPI
lines with their tests; the red reason as you saw it; the `gov.__file__` line; every earlier test you revised, with
its reason; whether you used `gov retrieve` and any result you dropped under P-R1; the read refusals you met; your
scratch figures; any package. Refused twice for the same call: stop and say so.

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
