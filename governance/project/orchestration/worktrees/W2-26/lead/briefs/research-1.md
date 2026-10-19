# Brief: research worker, W2-26 run 1

You are a fresh research worker. Ticket: `DAEO-2ds6` (`W2-26`, "EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)"), profile STANDARD, class research. You work only in the worktree `/home/usain/gov-os-worktrees/W2-26` on branch `w2/W2-26`, plus a throwaway folder `/tmp/gov-os-W2-26/`. You measure EXAMIN's committed tree on a clone and leave one evidence record, committed. You are a headless session: nobody answers questions while you work, and only your final message is read.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `research` and `DAEO-2ds6`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-26` and `w2/W2-26`). If anything differs, stop and say so.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. The owner's copy at `/home/usain/gov-os-workbench/examin` is read by one command only, the clone, exactly:
  `git clone --no-hardlinks /home/usain/gov-os-workbench/examin /tmp/gov-os-W2-26/examin`
  Nothing else runs in, lists, globs, searches or writes the workbench: no `ls`, no `find`, no `du`, no `git status`, no `git log` there.
- **EXAMIN's real repository (`~/EXAMIN APP`) is never touched, not even read.** The folder `/tmp/gov-os-W2-26/EXAMIN APP` below is your own second clone, not that repository.
- **Long runs go in the background, with an exit-code file, and you wait for them.** A foreground command that outlives the Bash tool's time limit is killed. Start the clone, the test suite (if it runs) and each indexing run with Bash's `run_in_background`, writing its output and exit code to files under `/tmp/gov-os-W2-26/runs/` (for example `... > /tmp/gov-os-W2-26/runs/clone.out 2>&1; echo $? > /tmp/gov-os-W2-26/runs/clone.rc`). Wait with Bash only: `until [ -s /tmp/gov-os-W2-26/runs/<name>.rc ]; do sleep 20; done`, with the longest timeout the tool allows, repeated until the file exists. Never use the `Monitor` tool or any `mcp__` tool: the guard refuses tools it does not know (DEC-685). Never end your session while a run of yours is still going. One indexing run at a time, never two in parallel (this is a heavy ticket on a shared machine).
- **If the guard refuses a write under `/tmp/gov-os-W2-26/`,** do not work around it (no other folder, no other spelling): stop and return it as a package with the refusal's exact text.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. No push, merge or tag.
- Run no glob, no search and no listing over `governance/project/`: name files there one by one (DEC-508). Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path. Never read `.claude/settings.json` or `.claude/settings.local.json`, here, in a clone, or anywhere. Read nothing under `~/.claude/`. Never read or name the qualification oracle.
- Never copy this repository or a folder of it anywhere: no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository. The only clones you make are the two named in this brief.
- Write files in this worktree with the Write and Edit tools and literal absolute paths; the guard refuses here-documents and unresolvable variables in Bash write targets. No subagents that write. **Install nothing** (no pip, no npm, no apt, no venv creation with installs): a tool you need is returned as a package.
- **The code under test (DEC-732, owner decision of 2026-10-16; word for word):** "in this worktree, **every test run and every `gov` command** (the indexing runs on the clones included) **runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src` set **per command** (never in a session's `--settings` env). The evidence record shows it: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src python3 -c "import gov; print(gov.__file__)"`, with its output pointing into this worktree, and the same prefix on every `gov` command it records. **This rule goes into the worker's brief word for word.** It does not apply to EXAMIN's own test suite, which runs EXAMIN's code on the clone."
  For you this means: never `PYTHONPATH=src` (relative), never an exported `PYTHONPATH`; the absolute prefix on every `gov` command and every direct call of gov's functions, written into the record exactly as run.
- **Rebuilds (DEC-719):** never run `gov rebuild --no-embeddings`, anywhere. Never run any rebuild, index or `gov` command against this worktree's store or the main tree's store; `gov` commands in this ticket always carry `--root` pointing at one of your two clones.
- Nobody runs `gov close`, `gov adopt` or `gov pause`, anywhere, the clones included. On ESCALATION_BLOCKED from any command, stop and return it.
- Never write `.gov-runtime/**` of this worktree (you have no need to); never write `tests/acceptance/**`, `src/`, `template/`, `.tickets/`, the decision register or anything under `docs/` except `docs/research/EXP-003/examin/**`.
- On an authentication or access error from any tool or service, stop and return it with status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-2ds6.md` (read-only): its KPI lines, its allowed path, its "Consequences" and its section "The owner's copy (O-1, recorded 2026-10-16)". Where this brief is stricter than that section (the uncommitted entries, below), this brief holds.
- The card W2-26 in `docs/plan/WAVE_2_WBS.md` §2 (Track B) and the card W2-45 there (for what "the `gov check` budget" refers to).
- The list row W2-I041 in `docs/plan/WAVE_2_TRIAGE.md` and `docs/plan/WAVE_2_LIST.md`.
- In `docs/DECISION_REGISTER.md`: DEC-078 (the indexing envelope: ≈ 80k nodes, ≈ 270k edges, ≈ 2.2 GB peak RSS; note its correction that the code-intelligence tool runs a separate daemon and worker, so a measure of the CLI process alone undercounts), DEC-673 (no clone under this repository's `.gov-runtime/`), DEC-719, DEC-723, DEC-725, DEC-727, DEC-728.
- The research record template `template/governance/kernel/templates/research.md`.
- This repository's indexing code, to know what `gov rebuild` builds and where: `src/gov/rebuild/command.py`, `src/gov/retrieval/lexical.py`, `src/gov/retrieval/semantic.py`, `src/gov/codeintel/__init__.py`, `src/gov/config/loader.py`. Read-only.

## What you do

### 1. The clone

- Make `/tmp/gov-os-W2-26/` and `/tmp/gov-os-W2-26/runs/`. Then run the clone command above, exactly, in the background with its exit-code file, timed with `/usr/bin/time -v`.
- Check the clone's head: `git -C /tmp/gov-os-W2-26/examin rev-parse --short HEAD` must start with `a7cf346`. If it does not, stop and return PACKAGES.
- **The uncommitted entries.** You do not run `git status` (or anything else) in the copy. The record states: the owner's copy carries 9 uncommitted entries (6 modified, 3 untracked) that a clone does not see; the profile measures the committed tree at `a7cf346`; the entries' paths are to be given by the owner for Q-16 (W2-29). This is stricter than the ticket's O-1 section, by the orchestrator's decision.

### 2. The measures, all on `/tmp/gov-os-W2-26/examin`

Each with the command line, the tool's version and the raw output kept.

1. **Size:** tracked files (`git ls-files | wc -l`), lines of tracked text files, tracked bytes, commits (`git rev-list --count HEAD`), all with `git -C /tmp/gov-os-W2-26/examin ...`. Say how binaries were treated for the line count.
2. **Languages:** a table of tracked files and lines by file extension (the top extensions, the rest grouped). **Test runner(s) and their commands:** read the repository's own test configuration and documentation first (for example `pyproject.toml`, `setup.cfg`, `pytest.ini`, `tox.ini`, `package.json`, `Makefile`, CI workflow files, the README's test section). Record which runner(s) and which command(s), and the file each was found in. You may quote a configuration's test command line; never a file's other contents.
3. **The test suite's wall time.** Run the suite on the clone only if it needs no install, no network service, no container, no database and no credential, and only with the interpreter and packages already on this machine; with a time limit of 30 minutes (`timeout 1800`), in the background, timed with `/usr/bin/time -v`. If it needs any of these, do not run it: record what it needs and why it was not run, as a finding. Install nothing. If a run starts and fails on a missing package, stop it there and record that.
4. **Indexing time and peak RSS for each index** (lexical, semantic and the code graph, as this repository's `gov` builds them), against DEC-078's envelope, measured with `/usr/bin/time -v`.
   - First, record which `gov` runs (DEC-732): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src python3 -c "import gov; print(gov.__file__)"`; its output must point into `/home/usain/gov-os-worktrees/W2-26/src/`. If it does not, stop and return PACKAGES.
   - The primary run: from this worktree, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src /usr/bin/time -v python3 -m gov.cli.main rebuild --root /tmp/gov-os-W2-26/examin --json` (a full rebuild; never `--no-embeddings`). Its stores land inside the clone (the clone's own `.gov-runtime/`), which is allowed: they are not this repository's stores. Check the CLI's help first for the exact flags.
   - `gov rebuild` builds the lexical index only when the project has a path map (`governance/project/path-map.yaml` in the target), which an unadopted clone does not have. **Do not write a path map or any other governance file into the clone, and do not adopt it** (`gov adopt` is W2-27's work). If an index is not built for that or any other reason, record what stops it, with the CLI's own message, as a finding; do not work round it.
   - To get a time and peak RSS per index, you may in addition time each of gov's own index functions on its own, unmodified, with the clone as root (for example `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src /usr/bin/time -v python3 -c "from pathlib import Path; from gov.codeintel import index; index(Path('/tmp/gov-os-W2-26/examin'))"`), one at a time. Label these in the record as direct calls of gov's functions, beside the CLI run. Never change `src/`.
   - The code-intelligence tool runs a daemon and a worker (DEC-078's correction) whose runtime folder gov puts under `/tmp/gov-cbm-<uid>/`. `/usr/bin/time -v` may not count them. Sample their RSS while the run goes (for example `ps -o pid,rss,args` on the tool's processes every few seconds, written to a file under `/tmp/gov-os-W2-26/runs/`), and report the peak of each, and the graph's node and edge counts if the tool reports them. Record that gov wrote its daemon folder under `/tmp/gov-cbm-<uid>/`; do not delete anything there.
   - The semantic index asks a local embedding endpoint (Ollama). If the endpoint is not running, record that and do not start one.
   - Record the size of each store the run left in the clone (`du -sh` on the clone's `.gov-runtime/` subfolders only).
5. **Whether a path with a space breaks any command [W2-I041]:** make a second clone **from the first clone** (never from the workbench): `git clone --no-hardlinks /tmp/gov-os-W2-26/examin "/tmp/gov-os-W2-26/EXAMIN APP"`, quoting the path every time. Run the same measuring commands there (size, languages, the suite if it ran, and the indexing, one run at a time), and record each command that breaks and how (exit code, the message), or that none broke. Time and RSS there are recorded too, but the question is whether anything breaks.
6. **The consequences the ticket names**, reported plainly; you decide neither:
   - Are EXAMIN's tests pytest? If not, W2-19 joins W2-27's dependencies (DEC-727).
   - Does indexing, or anything else you measured, exceed its budget at EXAMIN's size (DEC-078's envelope; the `gov check` budget named on W2-45's card, if you can find it stated in this repository)? If so, W2-45 may join them.

### 3. The evidence record

- Write it at `docs/research/EXP-003/examin/README.md` in this worktree, from the research template (front matter; Question, Method, Sources, Measurements, Uncertainty, Conclusion), adding: the environment (machine: `uname -a`, `nproc`, `free -g`; versions of git, python, gov's code-intelligence tool and Ollama if reachable; this worktree's head; the clone's head; the DEC-732 line `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src python3 -c "import gov; print(gov.__file__)"` with its output), every command line (each `gov` command with its `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src` prefix, as run), the measures in one table against DEC-078's envelope, the findings, and what is still unknown.
- Long raw outputs go as files beside it under `docs/research/EXP-003/examin/raw/` (one file per command, named after it).
- **No file of EXAMIN, and no content of one, is copied into this repository:** only measures, command lines, file counts, extension tables and outputs that hold no file contents. Before you commit, read each raw file you keep: drop any line that carries a file's contents, a secret or anything that looks like one (keys, tokens, passwords, connection strings), and say in the record that you dropped it and why. File paths of EXAMIN may appear only where a measure needs them (for example the test configuration file's name); no full file listing.
- The clones stay under `/tmp/gov-os-W2-26/` when you end; record their sizes (`du -sh` on each clone).

## Commit

Commit only `docs/research/EXP-003/examin/**`, with the trailers in the final block:

    git commit -m "W2-26: EXAMIN profile on a clone of the owner's copy at a7cf346 (EXP-003's EXAMIN leg)" --trailer "Task: DAEO-2ds6" --trailer "Role: research" --trailer "Implements: DEC-728" --trailer "Implements: DEC-078" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and return PACKAGES. Never `--no-verify`, never `core.hooksPath`. After the commit, run `git log --oneline -2`, `git status --short` and `git log -1 --format=%B`, and put their output in your return.

## Return

Your final message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so; no third try.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

In `work_completed` or the payload, give the measures in one compact table (files, lines, tracked bytes, commits, languages, test runner and command, suite wall time or why not run, indexing time and peak RSS per index against DEC-078, the space-in-path result), the two consequences, the wall time of your session, and the sizes of the folders under `/tmp/gov-os-W2-26/`. A package is given in full: question, why now, options, impact, reversibility, cost, recommendation, confidence.
