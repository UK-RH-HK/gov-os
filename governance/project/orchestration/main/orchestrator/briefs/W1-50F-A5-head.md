You are a ticket lead for ticket `DAEO-xnbx` (`W1-50`), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-50-freeze` on branch `w1/W1-50-freeze`. This branch carries three lines the owner added to the ticket on 2026-10-05 (DEC-402, DEC-399). **High priority.** Another lead works on the same ticket's containment lines in another worktree (`/home/usain/gov-os-worktrees/W1-50`, branch `w1/W1-50`): you never touch that worktree, `src/gov/guard/containment*`, `tests/unit/containment/**` or `tests/acceptance/W1-50/**`. Wherever the common part below says "the worktree", it is yours.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

**An engineer starts only on decided ground.** If the test designer returns a package the implementation depends on, you return PACKAGES and no engineer runs for the part it touches.

## What this branch is for

Read DEC-402 and DEC-399 in `docs/DECISION_REGISTER.md`, the ticket file's three new KPI lines and its paths (`src/gov/guard/decide*`, `src/gov/pause/**`, `src/gov/launch/**`, `tests/unit/guard/**`, `tests/unit/pause/**`, `tests/unit/launch/**`), "W1-28 residuals", "W1-46 residuals" and "Observations from launched worker sessions" in `governance/project/bootstrap.md`, and DEC-176, DEC-180, DEC-365, DEC-378, DEC-386.

- **The fault.** Launched sessions were refused with "frozen: all writes denied" although nobody had set a freeze, and `.gov-runtime/freeze` was seen as an empty file in a worktree while a worker's sandboxed Bash ran there.
- **The likely cause (owner, DEC-402).** `src/gov/launch/launcher.py` (`_runtime_rules`) denies the freeze flag's path by name also when it does not exist; the sandbox then creates an empty placeholder at that path on the real filesystem while a worker's command runs; the guard (`src/gov/guard/decide.py`, `FREEZE_FLAG`), which runs outside the sandbox, reads the placeholder as a freeze.
- **The decision.**
  - A real freeze flag carries a marker line written by `gov pause` (for example `FROZEN`, with who and when).
  - The guard treats an empty file, or one without that marker, as no freeze, and records its presence as a residual observation.
  - The launcher stops denying the freeze path when it does not exist at launch.
- **DEC-399.** Every fixture that copies the whole tree (`copy_working_tree` in W1-05's and W1-07's support files; W1-25 uses W1-07's) strips the held-out deny line from the copied `.claude/settings.json`, as W1-46's and W1-47's fixtures already do. **Nobody reads, prints, searches or diffs `.claude/settings.json`'s held-out deny line, or the held-out file, in any copy**; the designer takes the stripping from W1-46's or W1-47's fixture as it is written there, and tests it on a synthetic settings file of its own.

## Step 0, before anything is designed or built: verify the cause with one live launched session

The owner asked for this. Do it yourself, read-only apart from the one session:
1. Record that `/home/usain/gov-os-worktrees/W1-50-freeze/.gov-runtime/freeze` does not exist (`ls -la`, `stat`).
2. Start one worker in the background with `gov launch engineer DAEO-xnbx` and a brief that tells it to do exactly one thing: run the Bash command `sleep 75`, then answer "done", writing nothing.
3. While it runs, from your own (unsandboxed) calls, look at the path every few seconds with `stat` (type, size, times) and note when it appears and when it goes; also try, during the sleep, whether a harmless Write of your own under `.gov-runtime/scratch/` is refused with "frozen".
4. After the session ends, look again.
5. If the placeholder appears only while the worker's Bash runs and is empty, the cause is confirmed; say what you saw, with times. **If it is not what you see** (no file appears, it is not empty, it stays, or the refusal comes from somewhere else), stop and return PACKAGES with the observations: nothing is built on an unconfirmed cause.

Never create, write or remove the flag yourself, in this worktree or the main tree, and nobody runs `gov pause` against this repository. A test builds its own temporary project.

## Things the test designer settles from the sources, or returns as packages, never as guesses

- The marker: its exact first line and what "who and when" are (the caller of DEC-365; a time that keeps tests deterministic), and that `gov pause --off`, `--cancel-agents` and `--rollback` go on working (W1-28's suite; a W1-28 case that pins an empty flag or the placeholder is a planned revision, reason "owner decision, DEC-402").
- What the guard does with each shape at the flag's path: absent; empty; text without the marker; the marker; a marker after other lines; a directory; a symbolic link; a file it cannot read; a character device (what a session sees inside the sandbox). The decision names the first four. For the others the stricter reading is "frozen" where the guard cannot tell, **except** shapes the sandbox itself produces, which must not freeze: if the sources and Step 0 do not settle one, it is a package with options.
- Where "records its presence as a residual observation" is written (the findings file, the records file, or elsewhere), once per call or once per appearance, and that recording never blocks the call.
- Every reader of the flag: the guard, `gov pause`'s own state reading, and anything else in `src/gov/` (`gov checkpoint`, the launcher). Each must read it the same way; one outside this ticket's paths is a package.
- The launcher: the path is not denied when the flag does not exist at launch, and is still denied by name when a real flag exists. **The hole to look for:** a freeze set after a session was launched is then not protected inside that session's sandbox, so a worker's Bash could remove or rewrite a real flag; and a worker could create a marked flag itself. Say what holds each (the guard's own Bash rules, the sandbox, nothing) and return a package if something only the launcher's deny held is lost.
- The live guard is the main tree's code: this branch's guard change takes effect only when it is merged. Say in your return whether a merge needs anything refreshed (hook copies, a running session).

## What you do, in order

0. Step 0 above.
1. **Test design** (brief A1, a fresh designer, profile FULL, in proportion), under `tests/acceptance/W1-50/` only in files of its own named `test_w1_50_freeze_*` and `w1_50_freeze_*` (the other lead's designer writes the rest of that folder), plus the planned revisions in W1-05's, W1-07's and W1-28's suites.
2. **Check red** yourself, and that the revised fixtures and the revised W1-28 cases leave every earlier suite as it was.
3. **Engineer** (brief A2, fresh): guard, `gov pause`, launcher. Small. It runs its tests in the foreground and commits before it ends its turn.
4. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator. Red by design on this branch, to report apart: the 26 W1-50 containment cases of the other branch's work.
5. **Step 0 again, on this branch's code**, as far as it can show anything before the merge (the launcher is this worktree's; the guard is the main tree's): with the new launcher, no placeholder appears during a worker's Bash.
6. **Reviewer** (brief A3, fresh). Besides its own probes: any way a session now writes while a real freeze is set (a marker the guard misreads: byte-order mark, CRLF, case, leading blank lines, a huge file, a race while `gov pause` writes); any way a worker lifts, removes or forges a freeze; any reader that still takes an empty file for a freeze; whether the launcher's sandbox is weaker in any other way than the one path.
7. Return DONE, or PACKAGES, with Step 0's observations, the commits, each suite's result, the reviewer's findings and what was done, the residuals for `bootstrap.md` and the learning metrics of this branch, as your last message.

