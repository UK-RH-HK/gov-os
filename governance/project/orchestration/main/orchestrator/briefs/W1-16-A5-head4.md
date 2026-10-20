You are the ticket lead for ticket `DAEO-lkeb` (`W1-16`, "codebase-memory wrapper"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-16` on branch `w1/W1-16`. This is the ticket's last, short round: one small behaviour, then it closes.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

## State of this ticket

- The branch (`4543cca3`) is merged into `w1/integrate` and green there: W1-16 157 cases, W1-15 92, W1-17 65. Three earlier lead rounds built the wrapper `src/gov/codeintel/`, the token rule, the per-repository daemon directory (DEC-338) and the second gitleaks scan (DEC-347, DEC-354).
- **DP-1 is decided: DEC-377** (owner). No S0b2 C1 question set exists; W1-16 closes with the designer's 26 questions in `questions.yaml` as they are. The comparable measurement (hit@5 on the dev query set's code classes) is W1-42's, not this ticket's. Nothing changes in the questions; the README says so in one sentence, citing DEC-377.
- **The loopback UI is decided: DEC-362** (owner). The wrapper sets `--ui=false`, so the tool's daemon serves no UI on `127.0.0.1:9749`. An earlier round found that the switch exists and that the tool persists it in its own configuration. That is the one behaviour of this round.
- Read DEC-338, DEC-346, DEC-362 and DEC-377 in `docs/DECISION_REGISTER.md` after step 1.
- The tool's own files live outside the repository (`~/.cache/codebase-memory-mcp`, `/tmp/gov-cbm-<uid>/…`). `/tmp/cbm-daemon-1000` (empty on purpose) and `/tmp/gov-cbm-1000` (the live daemon directory, DEC-346) are not leftovers: nobody removes them.
- **A launched worker is sandboxed** and may not be able to run the real tool (its cache and daemon directory are outside the worktree). If the engineer's or the designer's own run of the W1-16 acceptance suite is stopped by the sandbox, that worker does not work around it: it runs what it can (the unit tests, a stand-in), says so, and you run the acceptance suite yourself. Say in your return what the sandbox stopped.
- This suite is heavy (indexing): run it alone, never beside another suite.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-lkeb` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES. A containment flag on the merge is a record (DEC-254).
2. **Test design batch 5** (brief A1, a fresh designer, profile FULL but in proportion: this is one behaviour). Cases: every tool call the wrapper makes turns the UI off (shown through the public interface: the argument the tool receives, and nothing listening on the UI port after a call where that can be shown without flakiness); a caller's environment or argument cannot turn it back on. The README gets the DEC-377 sentence. These are tests added after implementation, reason "owner decision, DEC-362".
3. **Check red** yourself.
4. **Engineer** (brief A2, fresh): the wrapper change, inside `src/gov/codeintel/**` and `tests/unit/codeintel/**`. A few lines. It reports exactly what the tool persists and where (the file in the tool's configuration that changes), because the main orchestrator records that in the tool registry's notes.
5. **Verify**: W1-16 alone, then W1-15 and W1-17, then every other suite under `tests/acceptance/`, `tests/unit` and the validator. Red by design, to report apart: W1-50.
6. No second review round for this change unless the engineer touched anything beyond the UI switch; say so.
7. Return DONE with the commits, each suite's result, what the tool persists for the UI switch and where, any residual of this round, and this round's learning-metric additions (tests added after implementation, lines).

