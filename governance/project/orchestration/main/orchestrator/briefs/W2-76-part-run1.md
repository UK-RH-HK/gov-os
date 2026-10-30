You are the ticket lead for ticket `DAEO-tgk2` (`W2-76`, "gov rebuild: per-stage timings, a 30-minute watchdog that records what it waits on, and one rebuild at a time on the machine"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-76` on branch `w2/W2-76`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-tgk2.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-76");
- DEC-939 (item 2 and its "How it is applied"), DEC-889, DEC-866, DEC-898 and DEC-941; rows W2-M408 and W2-L451 in `docs/plan/WAVE_2_LIST.md`;
- `src/gov/rebuild/command.py` (`run`, its stages and `_compact`) and `src/gov/rebuild/check.py`;
- the orchestrator's interim diagnosis, `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_diag.sh`, for what it records today;
- the launcher's sandbox (`src/gov/launch/sandbox.py`), for what a sandboxed session may open and lock.

## Why you start now

- **A rebuild took 6 h 39 min and nobody can say why.** A main-tree rebuild ran from 04:10 to 10:49 on 2026-10-29, against 271 s alone at 12:23, while W2-68's lead rebuilt its own stores. Its output timed only the lexical stage (row W2-L451).
- **The lock is held by hand today.** Every rebuild is wrapped in `flock /tmp/gov-os-rebuild.lock` by its caller: the queue, the nightly, every lead brief (DEC-939 item 2). A session that forgets runs beside another, unannounced (row W2-M408). Your lock makes it the rebuild's own.
- **Block A, fast closes (DEC-941):** every close starts with a rebuild, so a slow or contended one costs a close slot.

## The decisions for this run

- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour; it is a plan, not code. It says:
  - **the stages timed,** in the output and in the record: the lexical, semantic and code-index stores, the secrets filter where it runs, and the compaction; and where the record lives;
  - **the watchdog:**
    - its threshold is set by the project, default 30 minutes;
    - past it, a record of the stages done with their times, each of the rebuild's processes with its state and wait channel, and the load, written and kept updated while the rebuild runs;
    - the rebuild flags itself slow in its output and goes on to the end. The watchdog never stops or fails a rebuild, and a fault of the watchdog itself is reported, never fatal;
  - **the lock's path, measured, never assumed:** one path that every session on the machine reaches, the main tree, a worktree, a clone and a sandboxed worker included. Measure it with a launched sandboxed worker (below) and write the result in. If no path works without a change to the launcher's sandbox (`src/gov/launch/**`, held by W2-60a and W2-56), return PACKAGES;
  - **the interim wrapper:** until the re-pin that carries this ticket, the queue, the nightly and every lead keep running `flock /tmp/gov-os-rebuild.lock gov rebuild`, and the pinned gov takes no lock of its own. State how the two live together:
    - a new rebuild started under the wrapper never deadlocks and never waits on itself;
    - an old wrapped rebuild and a new one never run at once;
  - **a waiting rebuild** says what it waits for (the holder, where known), and records its wait apart from its own stages, as the nightly records `lock_wait_s` apart from `setup_s` (DEC-939 item 6);
  - **fail closed:** a lock it cannot create or take is never ignored. The rebuild waits, or refuses with the reason; it never runs beside another unannounced;
  - **nothing else changes:** the same stores and the same digest on the same tree.

  It goes into the test designer's brief as text.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-76/`:
  - **its first task, after step 0, is the lock measurement:** can it create and take a lock on each candidate path, and does a lock you hold on that path outside the sandbox block its non-blocking take? It reports this first. You finish the design's lock line from that report before the engineer starts;
  - one case per KPI line, success and failure, in temporary repositories built from scratch, small enough that a rebuild runs in seconds;
  - **the threshold and the lock's path are set through the interface the design states,** to seconds and to a temporary path. No case takes the machine's real lock or waits 30 minutes: a case left on the real lock would wait on every real rebuild on the machine, and contend with the nightly's and the queue's;
  - two rebuilds started at once, as two processes: they run one after the other, and the second says what it waits for and records the wait apart;
  - a rebuild started under `flock` on the same lock path, the wrapper's form, ends within a stated bound, with no deadlock;
  - a planted slow stage (a stand-in that sleeps past a threshold of a few seconds): the record exists, is updated, and names each process's state and wait channel; the output flags it; the rebuild ends with the same stores;
  - a lock that cannot be created (an unwritable folder): the rebuild waits or refuses with the reason, and never runs;
  - every stage's time in the output and the record; the same digest from two rebuilds of the same tree.
- **The engineer** (fresh, launched sandboxed where its suites allow, `--effort high`) works only in the allowed paths: `src/gov/rebuild/**` and new files `tests/unit/rebuild/test_w2_76*`.
  - **Every stage is timed from the rebuild's side.** The stores' code (`src/gov/store/**`), the code index (`src/gov/codeintel/__init__.py`) and the secrets filter (`src/gov/secrets/**`) are other tickets' (below). Nothing is edited there.
- **Fail closed:**
  - no watchdog path stops or fails a rebuild;
  - no lock fault passes silently;
  - a rebuild that could not take the lock never runs beside another.
- **Running beside you:**
  - **W2-03** (`DAEO-ym8a`, merge-back) holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py` and their unit tests. **No file overlap with your `src/gov/rebuild/**`:** the rebuild calls the stores and does not edit them. W2-68 (closing) also holds `src/gov/store/**`.
  - W2-05 (`DAEO-0z8c`, merge-back) holds `src/gov/**/*.py` for the git environment of git calls, and `src/gov/util/gitenv.py`. Leave how the rebuild's git calls build their environment as it stands; the later merge takes the conflict.
  - W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
  - W2-61 holds `src/gov/retrieval/measure.py`.
  - W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`. W2-56 holds `src/gov/launch/**` and `src/gov/codeintel/__init__.py`.
  - W2-77 holds `src/gov/close/nightly.py`.
  - W2-68 and W2-58 are closing.

  Do not touch their files. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite, no full run and no rebuild. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00. Wait for the nightly to end.
  - **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **Your verification rebuild runs this worktree's new code under that wrapper.** It is the coexistence case live: run it only after the wrapper case is green, and bound it (`timeout 3600` inside the `flock`), so a hang never holds the machine's lock for long. A hang is a red, named, and a package.
  - **Never rebuild the main tree,** and never run the queue or the nightly.
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **No review (STANDARD).**

## This run's order

1. The design note (yours, in scratch), with the lock line left open.
2. Tests first (the test designer, whose first task is the lock measurement); you settle the lock line; then **check red yourself.**
3. The engineer.
4. Rebuild (bounded, under the wrapper) and verify in full.
5. **Return** DONE or PACKAGES. DONE means the branch is ready to merge; the next re-pin carries it, and the orchestrator then drops the hand-held wrapper from the queue, the nightly and the briefs.

**Estimate:** about 80 lines, about 6 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
