You are a fresh ticket lead finishing the short round on ticket `DAEO-3ef2` (`W1-38`), working only in the worktree `/home/usain/gov-os-worktrees/W1-38` on branch `w1/W1-38`, head `832fd8d4`. The round's first lead returned PACKAGES with one package, DP-1; it is decided. Everything else of the round stands as that lead left it: the designer pass on three cases (`9dd9c052`), the 19 cases of the DEC-664 piece (`e3377271`), the engineer's one line (`74d83913`). You repeat none of it. Read `.gov-runtime/scratch/lead/` in this worktree for that lead's notes and logs if you need them, and `git log cdf7f17c..HEAD`.

**This is the round's one further run (the owner's finish line, DEC-584). You commission no reviewer: the main orchestrator has a fresh reviewer probe the final code before the merge. Your DONE return names the head, and nothing is committed after it.**

## The decision (DEC-675; it is in the main tree's register, not yet in this worktree's: its words are here)

**DP-1, option (a).** Two cases are red since `9dd9c052`: `tests/acceptance/W1-28/test_w1_28_fixture_copies.py::test_a_fixture_that_copies_from_the_repository_leaves_the_held_out_file_out` for `W1-33/w1_33_support.py::generate_definition`, tracked and untracked. Decided: W1-28's synthetic repository gets one more made-up file at the adapter source's place for the research definition (`.rulesync/subagents/research.md` in the synthetic repository), and W1-33's helper is split into a copy step the check can call and a generation step with no root parameter. **The check keeps its reach: it still sees and runs the copy.** Not taken: a helper the check no longer sees; widening the copy.

The second rewritten W1-49 case is kept as written. Nobody touches W1-49.

## What you do

1. **One test designer session** (brief A1, fresh, through `gov launch independent-test-designer DAEO-3ef2` with the model, in this worktree). It writes only under `tests/acceptance/W1-28/` and `tests/acceptance/W1-33/`. Its brief states the decision above as behaviour: after its commit, W1-28's fixture-copy cases for W1-33's helper are green, tracked and untracked; the W1-33 case on the research definition still holds the generated file to what the registered rulesync generates from its source, and still fails when the file differs; no other case of W1-28, W1-33 or W1-50 changes its answer. It runs W1-28, W1-33 and W1-50 to their end before it commits. **Limits, word for word in its brief:** "Never read, print, search or copy this repository's held-out file or its settings file, and never type either path; the made-up file in W1-28's synthetic repository holds made-up text only. Change nothing in W1-28's check that makes it see or run fewer helpers." One commit, with `Task: DAEO-3ef2`, `Role: independent-test-designer`, `Implements: CAP-38.b`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, and a `Rewrite-Reason:` trailer naming DEC-675 for each existing case it changes. If it finds that option (a) cannot be done without narrowing the check, it commits nothing and you return that as a package.
2. **You check:** the two cases green; W1-28, W1-33, W1-49, W1-50 and W1-38 each to its end; the diff read line by line, with this question: does W1-28's check see and run fewer helpers than before, or accept a helper it refused before? If yes, return it as a package.
3. **Then the whole of `tests/` in the form the close uses** (`python3 -m pytest tests -n auto` with the close's plugin keeping the declared cases out, then the entries of `tests/acceptance/serial-only.txt` alone), `tests/unit`, the validator. A case that fails under load and passes alone is named (DEC-372). `W1-49/test_w1_49_live_session.py` varies with the live model's reply (DEC-671): if it fails, run it alone once more and report both.
4. **A checkpoint** (`PYTHONPATH=src python3 -m gov.cli.main checkpoint --ticket DAEO-3ef2 --role orchestrator --trigger ticket-transition --next "<next step>" --json`), committed with `Task: DAEO-3ef2`, `Role: orchestrator`, `Implements: CAP-38.b`. Then return.

## Rules

- **Every `gov launch` carries the model (DEC-460):** `PYTHONPATH=src python3 -m gov.cli.main launch <role> DAEO-3ef2 -- --model claude-opus-5-5 -p --output-format json --permission-mode acceptEdits --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" < <brief> > <log.json> 2> <log.err>`, with literal absolute paths, in the background, waited for in the foreground.
- **The guard's read rule is live in this worktree.** Write "the settings file" and "the held-out file", never either path. A here-document or a redirect to a path held in a variable may be refused: write files with the file tool. A search from the project root or over `governance/` that gives no path may be refused: search `src`, `tests`, `template` or `docs` by name.
- **Every worker brief says, word for word:** "Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists." and "No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree." and "Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read the settings file of the harness, in this worktree or anywhere, and never type its path or the path of the held-out file in a command." **And it ends with the twelve-field block below, word for word.**
- A test designer's brief states behaviour and sources only (DEC-462). A canary or planted secret is named by its id, never by its value (DEC-604).
- Acceptance suites run without `PYTHONPATH` (`env -u PYTHONPATH python3 -m pytest tests/acceptance/<suite> -q -p no:cacheprovider -rs`); unit tests with `PYTHONPATH=src`. Nothing is installed by anyone.
- Nobody runs `gov close`, `gov pause`, `gov adopt` or `gov rebuild` against this worktree or the main tree; nobody pushes; nobody merges `w1/integrate` into this branch in this run. No one reads anything under `~/.claude/`, lists `~/gov-os-workbench/`, or reads `~/gov-os-workbench/w1-tests/` or `qualification-oracle/`. A worker never copies or clones this tree.
- You decide no package. Anything that would narrow W1-28's check, or touch the guard, the launcher or a generated file of this repository, is returned at once.

## Return

**DONE with the head named and nothing committed after it**, or PACKAGES. In it: the designer's commit with its trailers checked; the rewritten and added cases counted, with reasons; each suite's count; the answer to the question of step 2 in one line; residuals; learning metrics for this run added to the first lead's (it reported: 0 KPI disputes; 3 rewrites, reason DEC-665; 19 cases added; +1 −2 source lines against 50; converged; 0 false findings).

**Read this first: a headless lead's turn ends its background work.** After you start a worker or a test run in the background, wait for it in the foreground before you say anything: `until [ -s (its log or exit-code file) ]; do sleep 20; done` with the longest timeout allowed, repeated until it is there. Never end a message with "waiting". **Your return is one message, your last, and complete in itself.**

**If a worker's log or your own call shows an authentication or access error (401, 403, "Failed to authenticate"): start nothing more and return at once with the first line `AUTH_REQUIRED` and the state of the branch (DEC-420).**

## The twelve-field return (active since 2026-10-13, DEC-442, DEC-668)

The SubagentStop hook is registered. It refuses (exit 2) the return of any subagent whose last message does not carry all twelve fields of the worker return contract, each as a label at the start of a line, followed by a colon and at least one word:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | LEAD_CHECKPOINT | BLOCKED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

- **Your own last message carries the twelve fields**, in this form, after your summary or as its frame. No field is left empty: write "none" where there is nothing.
- **Every brief you write, for a launched worker or for an in-session subagent, ends with this block word for word and asks for the twelve-field return.** A subagent started through the Agent tool without it will be refused on its return and loop.
- The fields frame the return; they do not shorten it. What the brief asks for in the return (commits with trailers, suite counts, residuals, learning metrics) goes into the matching fields.

**Last of all: your one return message carries the twelve fields above, each as a labelled line.**
