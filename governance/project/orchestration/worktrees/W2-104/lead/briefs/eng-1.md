# Brief: engineer, DAEO-drhj (W2-104), run 1

You are a fresh engineer. Ticket: `DAEO-drhj` (W2-104), profile STANDARD. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-104` on branch `w2/W2-104`. You build the ticket's code to its specification and
KPIs (DEC-957: to fulfil the spec, never to make the tests pass), with your own unit tests as you go.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-drhj','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-drhj`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-104` and `w2/W2-104`).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and
  nothing started in the background is ever read. Commit your work before you run any long suite. Return only
  after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Reads (DEC-820, Policy 2):** you read freely, except: (a) secrets and keys, never read or printed; (b) the
  contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under
  `governance/project/`, never type its path; never read or name the qualification oracle); **(c) the counterpart's
  work on this ticket: you never read `tests/acceptance/W2-104/`** by any tool (nor the tests worktree
  `/home/usain/gov-os-worktrees/W2-104-tests`); you may run those tests, only through `gov accept`, and see their
  names, results and failure messages, never their source; **(d) the hidden half of any evaluation set** is never
  read by whoever is measured by it.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This
  worktree's own store is not built yet (its rebuild waits for the machine), so retrieve from the integration
  branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; it
  holds `w2/integrate` as of its last refresh; for anything newer, read the file in this worktree).
  **Never one giant query (DEC-860):** a large question goes in batches (`--batch-size`, then `--continue <token>`),
  ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal
  (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root,
  `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders
  instead. Count the refusals you met and report them. Run no glob, search or listing over `governance/project/`;
  name the files you need there one by one. Never read `.claude/settings.json`.
- **Command forms the guard can read (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at
  literal absolute paths; anything longer than a line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-104/.gov-runtime/scratch/eng/` (if that write is refused, under your session's
  own `TMPDIR`) and you run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses
  something you needed, do not work around it: return it as a package.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`).
  A test that needs a project builds a temporary one under pytest's `tmp_path`. Never write in `~/gov-os-workbench`.
  Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
  Install nothing (an install you need is a P1 package in your return). No subagents that write. Never write
  `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit
  hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex
  string for a token.
- **Never a real model call and never a key in your tests:** your unit tests use a stub `claude` executable on a
  `PATH` you build (only the stub's folder and `/usr/bin`, `/bin`), never the real program, never the network.
- **Scratch budget (DEC-898):** your share is 8 GB and 400,000 files and folders, outside the tracked tree (this
  worktree's untracked and ignored files and your temp folder). `gov launch`'s sandbox sets your session's own
  `TMPDIR` (under `/tmp/gov-os-lead-W2-104/`, the only writable place there): keep it, never set `TMPDIR` yourself
  (the parent folder is read-only in the sandbox, and Python then falls back to the working folder). Keep pytest's
  own temp retention (never `--basetemp`); add `-o tmp_path_retention_policy=failed`. Remove
  what you made as soon as you no longer need it. Measure at the end (`du -s --inodes` and `du -sh`) and give the
  figures.

## What you read

- The ticket file `.tickets/DAEO-drhj.md` (read-only): its KPI lines (below, verbatim) and its `allowed_paths`.
- The sources: DEC-959 (items 5 and 7) and DEC-820 in `docs/DECISION_REGISTER.md`; ROLES-RESEARCH-1 §5.3 item 13 and
  its lines on the three scenarios (`governance/project/orchestration/packages/ROLES-RESEARCH-1.md`, read by name).
- The skill template and the scenario form, from W2-11 (landing today): on `w2/integrate` once landed, until then
  from `w2/W2-11`, read only: `git show w2/W2-11:template/governance/kernel/templates/skill.md` and
  `git show w2/W2-11:template/governance/kernel/skills/qa-review/scenarios.md`.
- The command-module convention: the docstring of `src/gov/cli/main.py` (where the module goes, what it exposes,
  `ACT_PATHS`, `EXIT_CODES` from 3, `HELP`, `CLASS`, `GovError`, a light top level); an existing command module such
  as `src/gov/accept/command.py` as a model; how `src/gov/launch/` starts the `claude` program.
- The code the ticket touches.

## The behaviour: the KPI lines, verbatim

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

Failure (each must still refuse; never fail open):
- F1. A scenario reported as passing that did not run, or failed.
- F2. An import marked adopted with no licence record or a failing scenario.
- F3. A secret read or printed.

## The public contract (set by the lead for both you and the independent test designer)

The test designer writes the acceptance tests to this same contract in parallel. Build exactly this interface;
where it leaves something open, choose the simplest fail-closed behaviour and say so in your return.

**The command.** `gov skilleval <skill> [--adopt] [--model <model>] [--effort <effort>] [--timeout <seconds>]`
plus the common `--json` and `--root <project>`. `<skill>` is the skill's folder, as a path relative to the project
root (or absolute). `gov --help` offers `skilleval`, and `gov skilleval --help` exits 0 and names it. It is a command
module by the convention (`src/gov/skilleval/command.py`, an act command; its `ACT_PATHS` cover the record beside a
skill and `governance/project/skill-imports.yaml`).

**A skill folder** holds `SKILL.md` (front matter with `name` and `version`) and `scenarios.md`, which holds exactly
three scenarios, each a heading `## <n>. <title>` (n = 1, 2, 3) followed by three bullets
`- **Situation:** …`, `- **Expected:** …`, `- **Pass line:** …` (the form of W2-11's `scenarios.md` files; a bullet's
text may run over several indented lines).

**The model.** A scenario's session and its judgement are each made by running the executable named `claude` found on
the `PATH` that `gov` runs with, as a new process (never `--resume` or `--continue`), with the arguments
`-p --model <model> --effort <effort> --output-format json` among its arguments and the prompt on its standard input.
It must print one JSON object on standard output with `result` (the reply text), `is_error` (a boolean) and
`total_cost_usd` (a number), and exit 0. The default model and effort are `claude-opus-5-5` and `high` (DEC-839's
worker defaults, until the project states role defaults of its own); `--model` and `--effort` replace them.
- The session's process runs in a new temporary folder outside the project (under `TMPDIR`, removed afterwards);
  that folder's `.claude/skills/` holds exactly one folder, the evaluated skill's, with its `SKILL.md` and its
  reference files, and **no `scenarios.md`** and no record (the session never sees its own pass lines). The session's
  prompt contains the scenario's Situation text. Where the `claude` program offers an option that keeps a session to
  that folder's settings and skills only (check `claude --help` if it is available to you; do not install it), use
  it; say in your return what you used.
- The judgement is a second, separate process (its own empty temporary folder, no skill) whose prompt contains the
  scenario's Pass line, its Expected text and the session's reply, and asks for a last line `VERDICT: PASS` or
  `VERDICT: FAIL`; the verdict is read only from the judgement's reply: its last line matching one of those.
- The harness passes its environment through to the executable (the real program needs its own credentials), and
  itself reads no secret: it opens no key or credential file and never puts the environment, or the child's
  standard error, into its output or records.

**The verdicts.** Each scenario ends `pass`, `fail` or `not-run`:
- `pass` only when the session and the judgement both ran and the judgement's verdict line says PASS;
- `fail` when the judgement says FAIL, or its reply has no verdict line;
- `not-run`, with a `cause` (one line, a category and an exit code at most; never the child's output text), when a
  needed model process could not be run or did not answer as above: no `claude` on the `PATH`, a non-zero exit,
  output that is not that JSON object, `is_error: true`, or a run past `--timeout` seconds (default 900). A not-run
  scenario is never a pass.

**The scenario record, beside the skill.** Each run appends one entry per scenario to `scenario-records.yaml` in the
skill's folder (a YAML map with the key `records`, a list; earlier entries are kept). Each entry has at least:
`skill` (the name), `skill_version`, `scenario` (1 to 3), `title`, `verdict` (`pass` | `fail` | `not-run`), `cause`
(a string, or null for a pass), `cost_usd` (a number: the session's and the judgement's `total_cost_usd` together,
or null when not run), `seconds` (a number, the wall time), `model`, `effort`, `run_at` (UTC, ISO 8601).

**The envelope.** With `--json`, `result` holds `skill`, `skill_version`, `scenarios` (a list of maps with
`scenario`, `title`, `verdict`, `cause`, `cost_usd`, `seconds`), `record` (the record file's path) and `adopted`
(true or false with `--adopt`, null without).

**Exit codes** (declared in `EXIT_CODES`). Without `--adopt`: 0 when all three passed; 3 when any scenario failed;
4 when none failed and any was not run; 5 when the skill cannot be evaluated (no `SKILL.md`, no `version`, no
`scenarios.md`, or not exactly three complete scenarios): then nothing is run and nothing is recorded. With
`--adopt`: 0 when the import was adopted; 6 when adoption was refused; 5 as above.

**Imports.** `governance/project/skill-imports.yaml` in the project is a YAML map with the key `imports`, a list of
entries, each with `name` (the skill's front-matter `name`), `source`, `version`, `licence`, `licence_verdict` and
`adopted` (a boolean). `gov skilleval <skill> --adopt` marks the entry whose `name` is the skill's name
`adopted: true` (with the adopted skill version and the time) only when the entry exists, its `source`, `version`
and `licence` are non-empty, its `licence_verdict` is exactly `allowed`, and all three scenarios pass in that run;
otherwise it refuses (exit 6, with the reason in the result), the entry, if there is one, ends with
`adopted: false`, no entry is added, and other entries are unchanged. Without `--adopt` the harness never changes
`adopted`. Create this repository's own `governance/project/skill-imports.yaml` with `imports: []` and a short header
comment stating the fields and the rule (no import adopted yet).

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/skilleval/**`, `tests/unit/skilleval/test_w2_104*` and
  `governance/project/skill-imports.yaml`. Nothing else. In particular **not** `src/gov/check/commands.py`: the new
  command must also be recorded in its `RECORDED_GOV_COMMANDS` (DEC-747), which is outside your paths; name it in
  your return, and name any test or check that turns red for it. Never `tests/acceptance/**`.
- Builder tests in `tests/unit/skilleval/test_w2_104*.py` (no `__init__.py`; a unique file name), test-driven, as
  regression evidence: run them with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -m pytest tests/unit/skilleval -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, to the end, never `-x`.
- Proportion (DEC-135): about 250 lines of code; no code for edge cases beyond the KPI lines and the contract. Never
  make a decision fail open: a missing record, a missing verdict or an unreachable model is never a pass or an
  adoption.
- Run the existing command-line suites that hold the command set, read-only, only if you need to see how your module
  is seen by `gov --help`; never edit them.

## The acceptance tests (DEC-963, DEC-959 items 6 and 7)

The test designer works in parallel in its own worktree. Your lead merges its tests into this worktree between your
batches (your sandbox mounts the acceptance tests read-only). **When `/home/usain/gov-os-worktrees/W2-104/.gov-runtime/scratch/lead/TESTS-READY`
exists** (check once your code and unit tests are committed), run the acceptance tests once, reading results only,
**through `gov accept` only**:
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -m gov.cli.main accept DAEO-drhj --json`.
It reports pass or fail per KPI line and the counts; you never run `pytest` on `tests/acceptance/` yourself and never
read a test's source. Report its result per KPI line. If TESTS-READY does not exist yet, return after your commit;
your lead resumes you to run it.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476), before any long run:

    git commit -m "W2-104: <subject>" --trailer "Task: DAEO-drhj" --trailer "Role: engineer" --trailer "Implements: DEC-959,DEC-820" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start
of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them.
Include: the sandbox check's result first in `evidence`; your commits' 12-digit hashes; the files changed; the tests
you ran with their counts; `gov accept`'s result per KPI line if you ran it; the `gov.__file__` line; the lines
added and removed; what you chose where the contract left something open; the `RECORDED_GOV_COMMANDS` addition
needed; whether you used `gov retrieve`; the read refusals you met; your scratch figures; anything you were refused
or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation,
confidence). Refused twice for the same call: stop and say so.

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
