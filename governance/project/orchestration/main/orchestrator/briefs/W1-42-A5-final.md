You are a fresh ticket lead continuing ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. **This is the final pass of the exit run. It records the owner's steps, reflects the owner's decisions since run 7 in the exit report, re-measures a-dev after two ticket-tool closes, settles the red cases of W1-42's suite that a record can settle and names exactly what each other one waits for, and ends verified.** No worker writes code; no `gov close` runs in this pass.

**Read first:** `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree, run 7's state file `.gov-runtime/scratch/lead/log/r7-state.txt`, the exit report `docs/plan/wave-1-exit/EXIT-REPORT.md` as run 7 left it (`5eb3b012`), and run 7's helpers under `.gov-runtime/scratch/lead/` (you may reuse them, checking each path and head first). Then merge `w1/integrate` into this branch (one committing command, `-m`, trailers `Task: DAEO-gjjf` and `Role: orchestrator`; the merge-base rule of the common part applies; the hook runs on it: rebuild first, as the rules say) and read in `docs/DECISION_REGISTER.md`: DEC-428, DEC-442, DEC-458, DEC-668, DEC-692, DEC-698, DEC-703 to DEC-709.

**The guard in this worktree refuses a tool it does not know (DEC-685), `Monitor` and every `mcp__` tool among them. Wait for background work with Bash (`until [ -s <file> ]; do sleep 20; done`). A foreground command that outlives the tool's limit is killed: start every long run, every commit included, in the background and wait for its exit-code file.**

## Rules (they override the common part below where they differ)

- **Every `gov launch` carries the model (DEC-460).** Workers in the dev-tier clones are launched from inside the clone's directory:
  `(cd <clone path> && PYTHONPATH=<clone path>/src python3 -m gov.cli.main launch <role> <ticket id> -- --model claude-opus-5-5 -p --output-format json --permission-mode acceptEdits --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" < <brief file> > <log file> 2> <error file>)`
  The brief file, log file and error file are under `.gov-runtime/scratch/lead/` in THIS worktree (not the clone's), with literal absolute paths. The clones have no `src/`, so this falls through to the installed `gov` (accepted, DEC-654).
- **Every worker commit, the test designer's too, carries `Implements:`** with ids the clone's own store holds (DEC-476, DEC-662 package 7), besides `Task: <ticket id>`, `Role: <role>` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Check each worker commit's trailers the moment it exists.
- **A test designer's brief states behaviour and sources only, never a name of the code to be written (DEC-462).**
- **Every worker brief says, word for word:** "Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists." and "No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree." and "Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read the settings file of the harness, in this clone or anywhere."
- **Every worker brief ends with the twelve-field block below, word for word** (section "The twelve-field return").
- **The exit run is run from the kernel's orchestration skill and brief templates (DEC-537).** Use the templates under `template/governance/kernel/templates/` in this worktree for every worker brief.
- **A real checkpoint at each round boundary (DEC-511):** `PYTHONPATH=src python3 -m gov.cli.main checkpoint --ticket DAEO-gjjf --role orchestrator --trigger ticket-transition --next "<next step>" --json` in this worktree; commit the record.
- **Acceptance suites:** `env -u PYTHONPATH python3 -m pytest tests/acceptance/<suite> -q -p no:cacheprovider -rs`; unit tests: `PYTHONPATH=src python3 -m pytest tests/unit -q -p no:cacheprovider`.
- Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree; nobody pushes (DEC-465). **Nobody runs `gov pause` anywhere, the clones included (DEC-428, DEC-660).** No other lead is running; the main tree is not yours.
- **The lefthook pre-commit hook now runs on every commit in this worktree (B3, DEC-706).** It runs `gov ci checks G1 G2` (about 5 minutes) and a scan of what is staged. **Before each commit here: stage, then `PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json` in this worktree, then commit (DEC-709).** That is the only `gov rebuild` run against this worktree. Never `--no-verify`, never `core.hooksPath`, no other way past the hook: **a refused commit is not worked round; return PACKAGES at once with the hook's output word for word** (keep it in `.gov-runtime/scratch/lead/log/`). Run each commit in the background with an exit-code file, since the hook can outlive the tool's limit. The clones have no hook installed: their commits are unchanged.
- Nobody lists `~/gov-os-workbench/` or any folder in it; nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/`. **Never read the settings file of the harness anywhere, a clone's generated one included.** No one reads anything under `~/.claude/`.
- **No clone, no copy of a clone and no file of a programme is ever put under a `.gov-runtime/` folder of this repository or of this worktree (DEC-673):** the programmes hold planted secrets, and the secrets-indexing check scans that folder. Refer to a planted secret by its file's name, never by its value (DEC-604).
- **An ESCALATION_BLOCKED (exit 4) from `gov close` always stops for the owner (DEC-651).** If any `gov close` in a clone returns exit 4, start nothing more on that ticket, close nothing with `tk close` in its place, and return PACKAGES at once with the envelope word for word.
- **At about 300k tokens:** write `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree and return LEAD_CHECKPOINT.

## The clones

- `/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/a-dev-exit`: feature branch `feature/dimension-checked-addition` at `127227c` (checked out), its main at `736669f`. `/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/b-dev-exit`: at `fc28272`, main `3b1ad56`. **Check each head and `git status` first**; if either is missing or at another head, return PACKAGES with that as the first line. Under the guard a lead writes only in its worktree and under `/tmp`, so they stay there (DEC-699). You never read or list `~/gov-os-workbench/`.
- **b-dev: nothing is run there** (DEC-687). **a-dev: no commit, no push, no merge in this pass**; you only measure there (`gov check`, below).
- Keep every answer you need for the report in `.gov-runtime/scratch/lead/log/` as soon as you have it (shapes and counts, never a programme's text, DEC-673).

## Decided ground since run 7 (the owner, 2026-10-14 and 2026-10-15; apply as written)

- **DEC-704:** ORION-im01 was closed in a-dev with `tk close` by the owner's decision (`5fb754d`), named for the exit auditor: its second `gov close` refused only with TRAILER_MISSING on `540004a`, before a-dev's base `bb1852e`, because `gov close`'s trailer gate does not read `trailers_base` (on the Wave 2 list). **ORION's cycle proof for criterion 1 stands on ORION-im02's clean `gov close`, CI and merge.**
- **DEC-708:** the repair ticket `ade-ke2y` was closed with `tk close` (`127227c`), accepted by the owner.
- **DEC-703:** DAEO-cdoi (W1-41) was closed in this repository with `tk close` after the round of DEC-694 (probe PASS, merge `945643ec`, every test green); its worktree is removed.
- **DEC-668, DEC-706, DEC-707, the owner's steps:** B1 (Stop and SubagentStop) done at `71ae763f`; B3 (the lefthook install) done; B2 (the manual freeze, pause and lift from a plain terminal) done in two parts, on a throwaway repository (DEC-668) and on this one (DEC-707), with a write refused while frozen. W1-42's KPI line for it is met.
- **DEC-709:** every commit here is staged, rebuilt (`--no-embeddings`), then committed through the hook; a refusal is returned, not worked round.
- **DEC-692 stands:** this branch is not merged into the integration branch until its red cases are resolved; the merge and the worktree's removal are the main orchestrator's, after your return.
- **Criterion 4:** a `tk close` gives no close record and no telemetry, so ORION-im01 still has no row; say so.

## What you do, in this order

### Piece 1: a-dev re-measured after the two ticket-tool closes

`gov check --json` in a-dev on its feature head `127227c` (as run 7 ran it, with embeddings available; rebuild there only if the check says the index is stale, and say so). Report every family's colour, each red finding counted by cause, and how each differs from run 7's three red checks (context reproducibility, core-claims through ade-ke2y, core-schema). Do not run `gov ci`, push or merge again: run 7's CI and merge stand as reported, and the report says that the closes came after them.

### Piece 2: the owner's steps as records (in this worktree)

1. `docs/plan/wave-1-exit/evidence/owner-freeze-check.json`, in the form W1-42's suite reads (`tests/acceptance/W1-42/test_w1_42_exit_report.py`, the case `test_owner_froze_paused_and_lifted_on_a_throwaway_repository_and_on_this_one`, and `w1_42_support.py`): an entry `throwaway` and an entry `this`, each with `repository`, `terminal: "plain"` and the four steps in the order `gov pause`, `gov status`, `gov pause --off`, `gov status`, each with its answer **exactly as the owner reported it** in DEC-668 (throwaway: `~/gov-b2-throwaway`, a copy of the a-dev-exit clone, since deleted) and DEC-707 (this repository). The owner's report gives each command's output; the commands follow from those outputs (`{"ok": true, "command": "pause", ...}` is `gov pause`; the `"pause": {...}` status lines are `gov status`; the prompt `type LIFT-… to lift the freeze` is `gov pause --off`, `src/gov/pause/command.py`). Put the status before the freeze, which comes before the four steps, in a field of its own (`status_before`). Say in a `note` field that the commands are read from the outputs the owner reported. `this` carries `refused_write`: `PreToolUse:Write hook error: frozen: all writes denied` (on a Write of `.gov-runtime/scratch/orchestrator/b2-probe.txt`, not created). Nothing invented: a value the records do not give is left out and named in your return.
2. The report's "Owner's steps" table: B1, B2, B3 each `done`, each with its record named (the register entries by id, the evidence file for B2).

### Piece 3: the exit report brought to the owner's decisions

`docs/plan/wave-1-exit/EXIT-REPORT.md` and its evidence:
- **Criterion 1:** ORION's cycle with ORION-im01's close as it went (`tk close` by DEC-704, after a refused `gov close` on pre-base history), the proof standing on ORION-im02 (DEC-704); `ade-ke2y` closed (DEC-708); ARGUS exactly as before, with the line that the owner weighs it at the exit decision (DEC-687).
- **Piece 1's measurement** beside run 7's.
- **For the exit auditor:** one line each for DEC-703, DEC-704, DEC-706, DEC-707, DEC-708, DEC-709, beside the lines earlier runs wrote.
- **Evidence list:** the backups as DEC-698, DEC-705 and DEC-706 record them, quoted (live-run7 for both clones; live-run7b for a-dev at `127227c`/`736669f`); the live clones' paths and heads, which this pass does not change.
- The overall verdict is whatever the criteria then give: **do not turn a criterion to MET that the evidence does not carry.**

The report and its evidence are written the way run 7 wrote them. Commit (rebuild first): `--trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c"`.

### Piece 4: verify and the red cases

W1-42's suite: name each case still red and exactly what it waits for. Run 7 had four:
- the owner's freeze: piece 2 should settle it; if it stays red, say which assertion and why;
- the worktree list (`git-worktree-list.txt`): it waits for this ticket's own worktree to be removed, which follows the merge DEC-692 holds back; say so, and write nothing for it;
- RETR-X-02's parent expansion and the governance share on each programme: say again, from the cases' own assertions, what each one needs, and what in the evidence would or would not give it. Change nothing to make them pass.

Then every suite under `tests/acceptance` in the close's form (parallel with the close's plugin, then the serial-only entries, in the background with an exit-code file; run 7's helpers show the form), `tests/unit`, the validator. Latency cases and the W1-46/W1-49 live-session cases: a failure there is run alone once more and both results reported (DEC-372, DEC-676, DEC-689). Then a checkpoint (`gov checkpoint` for DAEO-gjjf), committed (rebuild first), and your return.

## Decision packages

You decide none. A hook refusal, a head that is not as stated, anything about weakening a check or a test, an install, or the owner's steps: return at once.

## Return

`DONE` with: the branch head and commits, each with its hook result; a-dev's `gov check` family by family against run 7's; the evidence file's fields and anything the records did not give; each verdict and the overall verdict, and what differs from run 7; W1-42's suite with each red case and what it waits for; each other suite's result; residuals for `bootstrap.md`; learning metrics; deviations; temp folders left; the clones' paths and heads. Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`. **Whatever the first word, the message carries the twelve fields below.**

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

## Rules for every ticket lead (brief A5, orchestrator prompt v4.2)

You are a headless session: nobody can answer questions while you work. Everything the main orchestrator needs goes in your final message, and only that message is read.

**Four rules that leads have broken, each of which makes the main orchestrator discard the round:**
- **Writing workers are started with `gov launch` and in no other way.** A test designer, an engineer, a product-spec worker or a research worker is never an Agent-tool subagent. The Agent tool is only for a reviewer that writes nothing.
- **You never write or edit a file under `src/`, `template/`, `tests/` or `docs/` yourself, for any reason**, a one-line fix included. A reviewer's finding goes to a test designer first (a red case), then to a launched implementer. You write only under `.gov-runtime/scratch/lead/` and you commit merges.
- **You decide no decision package.** The delegation of DEC-220 and DEC-416 is the main orchestrator's. You return packages.
- **You never end your turn while a worker or a test run of yours is still running, and you never run the verification with `-x`.** Wait in the foreground (`until [ -s <file> ]; do sleep 20; done`, repeated); run each suite to its end. Your return is one message, your last, complete in itself.

**First**
- Run `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD`. Expect role `orchestrator`, your ticket id, your worktree and your branch. If anything differs, stop and say so.
- Read `governance/project/prompts/w1-orchestrator.md` in this worktree: sections 4, 5, 8, 9 and 10, and Appendix A (briefs A1 to A5). Read "Rules for every ticket" in `docs/plan/WAVE_1_WBS.md`, your ticket file in `.tickets/` (read-only), and the decisions named below in `docs/DECISION_REGISTER.md`.
- If `.gov-runtime/scratch/lead/CHECKPOINT.md` exists in this worktree, you are resuming: read it and continue from it.

**How you start a worker**
- Write its brief with the Write tool to `.gov-runtime/scratch/lead/briefs/<name>.md` in this worktree. Start from the matching brief A1 to A4, add the ticket's profile (DEC-221), the decisions that apply, and the standing notes below. Never give a worker your notes, the loop count or another worker's output; a repair worker gets only the failing test output.
- Start it in the background (Bash with `run_in_background`), never in a foreground call, from this worktree, **with `gov launch`** (owner decision DEC-371; W1-46 is closed). `gov` is not on the PATH, so the call is always spelled:
  `cd <this worktree> && PYTHONPATH=src python3 -m gov.cli.main launch <role> <ticket id> -- -p --output-format json --permission-mode acceptEdits --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" < .gov-runtime/scratch/lead/briefs/<name>.md > .gov-runtime/scratch/lead/log/<name>.json 2> .gov-runtime/scratch/lead/log/<name>.err`
  The launcher builds the session's settings (identity, sandbox, network profile) itself: never pass `--settings`, `--add-dir`, `--bare`, `--setting-sources` or a bypass flag, which it refuses. Roles it starts: `engineer`, `independent-test-designer`, `independent-auditor`, `research`, `product-spec`. Read the JSON's `result` field when it ends.
- **If `gov launch` refuses** (the log holds an envelope with `ok: false`, or the `.err` file names the refusal), do not fall back to a bare CLI session. Read the refusal; if it is something you may put right inside this worktree (for example the ticket is not `in_progress` here because `w1/integrate` is not merged in), put it right and launch again. Otherwise return PACKAGES with the refusal's text.
- **A product-spec worker** is started with `gov launch product-spec <ticket id>` like the others (DEC-386, merged with W1-28); it is held to a ticket whose role is product-spec. The DEC-183 form is ended for every role.
- **A launched session's temp folder, its scratchpad included, is removed when the session ends** (DEC-386). A worker returns everything you need in its final message or leaves it under `.gov-runtime/scratch/` of the worktree; nothing it wrote to its scratchpad survives.
- A launched session is sandboxed: it cannot write `.tickets/`, `.claude/` or `.gov-runtime/` outside `scratch/`, and it has its role's network profile. If a worker reports a refusal it needed to get past for the ticket, that is a package, not something to work around.
- Do not end your turn while a worker runs. Wait for it; if you have to poll, use a bounded loop on its log file and repeat it. If a log stays empty after the process has ended, look at `git status` and `git log`, and start a fresh worker on what remains.
- One writing worker at a time in this worktree. Never edit or commit here while a worker runs: containment would attribute your change to it.
- The reviewer (brief A3, FULL tickets) writes nothing. Run it as a headless session started with `gov launch independent-auditor <ticket id>` and `--allowedTools "Bash" "Read" "Grep" "Glob"`, or as an in-session read-only subagent.
- Every worker brief says: check `printenv GOV_ROLE GOV_TICKET` first; the guard refuses here-documents and unresolvable variables in Bash write targets, so write files with Write and Edit and literal paths; no subagents that write; install nothing; no push, merge, rebase or tag; never write `.gov-runtime/**` outside `.gov-runtime/scratch/`; trailers with `git commit --trailer` (`Task: <ticket id>`, `Role: <role>`, and `Implements: <ids>` for implementers).

**The held-out path (read this twice)**
- Never read, print, search, diff or copy `governance/project/held-out.yaml`. Never display the held-out deny line of `.claude/settings.json` (use `git diff --stat` only on that file). Never type a held-out path. Never read anything under `~/gov-os-workbench/w1-tests/`, and never list `~/gov-os-workbench/` itself. Put this in every worker brief.
- **No worker copies the tree.** On 2026-10-05 a test designer bulk-copied the tracked files into its scratchpad for a throwaway stand-in, and the copy took `governance/project/held-out.yaml` with it. Every worker brief says: never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository) anywhere; a throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. Tests that need a repository build a temporary one from the dev tiers or from scratch.
- **Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists.** A worker does not conclude from it that the tree is paused, and code under test that reads a flag is tested in a temporary repository.

**The loop (section 5)**
1. Tests first, by a fresh test designer (A1). You never write or edit `tests/acceptance/**` (MR-3).
2. Check red yourself: the tests fail for the reason their README states.
3. Implement, by a fresh engineer (A2) or product-spec worker (A4, ticket mode), inside the ticket's `allowed_paths` only.
4. Verify yourself, in this worktree: this ticket's suite, every earlier suite under `tests/acceptance/`, `tests/unit`, and `python3 docs/plan/tools/validate_s1.py` (expect ALL PASS). Use `python3 -m pytest <path> -q -p no:cacheprovider`, in the background for the slow suites (W1-02, W1-03, W1-04 about 100 s each; W1-05 about 5.5 min; W1-47 is large), with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. **Latency cases (DEC-372):** `test_a_call_waits_under_100_ms_p95_for_the_hook` (W1-05) and `test_decision_p95_is_under_100_ms` (W1-02) fail under machine load; when one fails, re-run its file alone after your other suites have ended; a pass alone counts, and you report each occurrence. If red: a fresh worker with the failing output. You hold the loop count and tell nobody; after three consecutive iterations that don't converge, return ESCALATION.
5. FULL tickets: after green, a fresh reviewer (A3). Findings that could lose work, let an implementer change acceptance tests, or make the guard fail open are fixed: a test design batch first, as described behaviours, never code (DEC-136), then a fresh engineer. The rest are residuals for `bootstrap.md`, which you return.
6. A KPI dispute or an ambiguity is a decision package, never a guess. You don't decide packages; return them with your recommendation and confidence, and keep working on whatever they don't affect.
7. An install is never yours or a worker's: return it as a package (tool, exact version, source and checksum, need, disk and RAM, uninstall command).

**Never**
- Edit `.tickets/`, `docs/DECISION_REGISTER.md` or `governance/project/bootstrap.md`; merge into `w1/integrate`; push, tag or rebase; touch `main`; sudo; write `.gov-runtime/**` outside `.gov-runtime/scratch/**`.
- You may merge `w1/integrate` into your ticket branch here when your brief says so or the main orchestrator sends you back for a merge conflict; nothing else.

**Context limit.** At about 300k tokens, write `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree (state, commits, what runs, what is next, the loop count) and return LEAD_CHECKPOINT.

**Return one compact summary** (no worker transcripts), starting with one of:
- `DONE`: branch head and the commits; each suite's result as you ran it; reviewer findings and what was done with each; residuals for `bootstrap.md`; learning metrics (KPI disputes; acceptance tests rewritten after implementation, with reasons, counting "planned: command implemented" apart; tests added after implementation; LOC added and removed against the estimate; engineer iterations as "converged" without the count; false findings).
- `PACKAGES`: each package in full (question, why now, options, impact, reversibility, cost, recommendation, confidence), plus the state of the branch and what you can still do meanwhile.
- `ESCALATION`: what doesn't converge, with the evidence.
- `LEAD_CHECKPOINT`.


**Read this first: a headless lead's turn ends its background work.** After you start a worker or a test run in the background, wait for it in the foreground before you say anything: `until [ -s (its log or exit-code file) ]; do sleep 20; done` with the longest timeout allowed, repeated until it is there. Never end a message with "waiting". **Your return is one message, your last, and complete in itself**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

**If a worker's log or your own call shows an authentication or access error (401, 403, "Failed to authenticate", "access grant"): start nothing more, write your checkpoint, and return at once with the first line `AUTH_REQUIRED` and the state of the branch (DEC-420).**

**An engineer starts only on decided ground.** A package the implementation depends on stops the part it touches, not the rest. You decide no package.

## What you do, in order

1. The branch starts at the current `w1/integrate`; no merge is needed now. If you merge `w1/integrate` later: first compare the list of paths under `tests/acceptance` and `.tickets` that your branch changed since the merge base with the list that `w1/integrate` changed since it (`git diff --name-only`); a path on both lists means no merge until a test designer has brought the branch's file to `w1/integrate`'s version plus the branch's own lines (DEC-412). **A merge is always one committing command with `-m` and the trailers `Task:` and `Role: orchestrator`; never `git merge --no-commit` (DEC-436).** After it, `git diff --stat w1/integrate HEAD -- tests/acceptance` lists only this ticket's own files and its own lines in shared files; anything else is a defect of the merge: return it.
2. **Test design** (brief A1, fresh, through `gov launch independent-test-designer`, in proportion, DEC-221). No throwaway implementation left in the tree. Shared lists (W1-07's `w1_07_support.py`) are touched only on lines of its own; W1-24, W1-26 and W1-50 are adding lines there on other branches.
3. **Check red** yourself, to the end of the suite, behaviour assertions apart from the absent module.
4. **Engineer** (brief A2, fresh, through `gov launch engineer`). Proportion rule DEC-135. It runs its tests in the foreground and commits before it ends its turn. **Every worker's commit carries both a `Task:` and a `Role:` trailer; you check each one (`git log -1 --format='%(trailers:key=Role,valueonly)'`) before going on; a commit without it is amended by a worker of the same kind while it is still the unpushed tip.**
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, each to its end, never `-x`. A latency case that fails under load is run again alone and reported (DEC-372); so are W1-16's `test_this_repository_is_not_indexed_by_the_run` and W1-46's live sessions.
6. **Review:** as the top of this brief says for this ticket.
7. Return DONE or PACKAGES, one message, your last: head, commits with roles, each suite's count, findings and what was done, residuals for `bootstrap.md`, the interface as built, the three learning metrics (KPI disputes; acceptance tests rewritten after implementation began, with reasons; source lines against the estimate), temp folders left.


**Last of all: your one return message carries the twelve fields of "The twelve-field return" above, each as a labelled line.**
