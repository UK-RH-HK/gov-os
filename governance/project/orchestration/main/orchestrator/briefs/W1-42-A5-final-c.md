You are a fresh ticket lead continuing ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. **This is the third part of the final pass (run 8c). Your predecessor (run 8b) did steps 1 to 3 below and committed them; the machine (WSL) was then restarted while its verify (step 4) was starting, which killed it before any suite ran and before its checkpoint. You do steps 4 and 5 and return.** No worker is launched; no `gov close` runs; no clone is touched.

**Check first:** the branch head is `da6fb889` ("W1-42 run 8b: the adoption-readiness block and the owner's intended exit in the exit report (DEC-710 to DEC-714)"), its parent `8d119104` (the merge of `w1/integrate` at `3d87550e` into `7217bfa9`, run 8's report and evidence); `git status --short` is empty. Anything else: return PACKAGES with it as the first line. Run 8b's logs are under `.gov-runtime/scratch/lead/log/` (`m1.*`, `c2.*`; `verify8-parallel.txt` is empty from the killed start: overwrite it).

**Read:** `.gov-runtime/scratch/lead/CHECKPOINT.md` (run 8's, superseded by this brief where they differ), `verify8a.sh`, `verify8b.sh`, `regress.py`, and in `docs/DECISION_REGISTER.md`: DEC-710 to DEC-714.

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
- **The git hooks are uninstalled until this ticket is merged (DEC-712)**: the pre-commit hook wrote two foreign commits onto this branch in your predecessor's run (DEC-710, DEC-711). **Before each commit: check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return PACKAGES.** Then stage, run `PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json` in this worktree, then commit (DEC-709); that is the only `gov rebuild` run against this worktree. Never `--no-verify`, never `core.hooksPath`. **After every commit, check `git log --oneline -2` and `git status --short`: a commit you did not make, or a changed index, stops you; return PACKAGES.**
- Nobody lists `~/gov-os-workbench/` or any folder in it; nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/`. **Never read the settings file of the harness anywhere, a clone's generated one included.** No one reads anything under `~/.claude/`.
- **No clone, no copy of a clone and no file of a programme is ever put under a `.gov-runtime/` folder of this repository or of this worktree (DEC-673):** the programmes hold planted secrets, and the secrets-indexing check scans that folder. Refer to a planted secret by its file's name, never by its value (DEC-604).
- **An ESCALATION_BLOCKED (exit 4) from `gov close` always stops for the owner (DEC-651).** If any `gov close` in a clone returns exit 4, start nothing more on that ticket, close nothing with `tk close` in its place, and return PACKAGES at once with the envelope word for word.
- **At about 300k tokens:** write `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree and return LEAD_CHECKPOINT.

## The clones

The restart cleared `/tmp`, so the two live clones under it are gone. Their last state is archived by the owner (a-dev feature `127227c`, main `736669f`; b-dev `fc28272`, main `3b1ad56`), the same heads run 8 measured. **You need neither clone for steps 4 and 5: do not look for them, do not recreate them, and never read or list `~/gov-os-workbench/`.** Report the clones' heads as "archived at the heads above (the /tmp copies cleared by the restart)".

## Decided ground (the owner, 2026-10-15; apply as written)

- **DEC-710:** this branch was reset (`--mixed`) from `dc6aa34c` to `d6d45759`, every file on disk kept. **DEC-711:** the two foreign commits `4b051fde` and `dc6aa34c` stay in the local object store, reachable through the reflog, named for the exit auditor; never pushed; the key file in `dc6aa34c`'s tree is a synthetic test secret, named by its folder `tools/deploy_keys/` only.
- **DEC-712:** the hooks are uninstalled until this ticket is merged; the cause read from the code (not run) is `src/gov/retrieval/retrieve_check.py` running `git -C <temporary clone> add -A` and `commit` with the hook's inherited `GIT_*` variables. It is the FIRST item of the Wave 2 list, before any pilot adoption.
- **DEC-713:** this branch is merged by the main orchestrator with its three red cases named in the exit report. The worktree-list case is recorded by the main orchestrator after the worktree's removal: **you write nothing for it**, and leave the report's line "git worktree list" as it is.
- **DEC-714, the owner's intended exit:** Wave 1 passes with named, accepted exceptions, each in an adoption-readiness block that opens Wave 2 and must pass before any pilot adoption: ARGUS's incomplete cycle (b-dev adopted to A2); the three reds in the a-dev clone (context reproducibility, claims, schema); RETR-X-02; the missing ARGUS share. The exit decision stays the owner's, after the W1-43 exit audit.

## What you do, in this order

1. Done by run 8b: `7217bfa9` (run 8's six files, after the hook check and the rebuild).
2. Done by run 8b: `8d119104` (merge of `w1/integrate` `3d87550e`).
3. Done by run 8b: `da6fb889` (the adoption-readiness block, the verdict beside the owner's intended exit, the auditor's lines for DEC-710 to DEC-714, the deviations, the three red cases under DEC-713). Read the report's new sections to quote them in your return; change nothing in it unless a check below needs it, and then return PACKAGES rather than edit.
4. **Verify:** W1-42's suite (expect 21 passed and the same three red; name each); then `verify8a.sh` and `verify8b.sh` (every suite under `tests/acceptance` in the close's form, `tests/unit`, the validator), in the background with their exit files. Latency cases and the W1-46/W1-49 live-session cases: a failure there is run alone once more and both results reported (DEC-372, DEC-676, DEC-689). Any other red: return PACKAGES with it; change nothing under `src/`, `template/` or `tests/`.
5. **Checkpoint** (`gov checkpoint` for DAEO-gjjf, next step "main orchestrator merges, removes the worktree, records the worktree list, closes"), committed as in step 1, and your return.

## Decision packages

You decide none. A hook file present, a commit you did not make, a head not as stated, a red case beyond the three named and the known flaky ones, anything about weakening a check or a test: return at once.

## Return

`DONE` with: the branch head and each commit with its after-check; the adoption-readiness block's lines as written; the verdict line; W1-42's suite with each red case; each other suite's result; residuals for `bootstrap.md`; learning metrics; deviations; temp folders left; the clones' heads. Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`. **Whatever the first word, the message carries the twelve fields below.**

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
