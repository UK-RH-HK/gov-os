You are the ticket lead for ticket `DAEO-wnnz` (`W2-56`, "`gov launch` usable for every worker: the code graph in the session's temp folder, the write list, no placeholders, a cleaned environment"), profile FULL, keystone 6, working only in the worktree `/home/usain/gov-os-worktrees/W2-56` on branch `w2/W2-56`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `23079f92a6fa`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-wnnz.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-56 "); the ticket's KPIs widen the card, and the ticket holds;
- W2-60a's ticket file (`.tickets/DAEO-cv58.md`), its paragraph on W2-56 above all;
- DEC-799, DEC-789, DEC-826 (Q5), DEC-801, DEC-786, DEC-180, DEC-315, DEC-159, DEC-728, DEC-402, DEC-313, DEC-784, DEC-877 (item 4) and DEC-941 (item 1.3);
- rows W2-M393 (`docs/plan/WAVE_2_LIST.md`) and W2-I012 (`docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`);
- lens E (`docs/assessment/2026-10/E-roles-context.md`) F1, F13, F17 and R6;
- the launcher as it stands (`src/gov/launch/launcher.py`: `build_settings`, `_check_cli_args`, `launch`), and `DAEMON_BASE` in `src/gov/codeintel/__init__.py` (line 35) with its use at line 56.

## Why you start now

- **The `gov launch` trial (DEC-789, DEC-799):**
  - What worked: the sandbox refused writes outside the worktree, and git could commit.
  - The code graph: `/tmp/gov-cbm-<uid>` is read-only inside the sandbox, so a worker whose suites build the code graph starts unsandboxed, in the old form, with the tripwire (DEC-799 item 3).
  - The write list: a worker's script can write anywhere in its worktree, because the launcher's `.gov-runtime/` deny rules are patterns, which the Linux sandbox skips.
  - Placeholders: placeholder files appear in the worktree while a sandboxed worker runs (row W2-I012).
- **A launched worker inherits the parent's whole environment** (lens E F13): `PYTHONPATH` included (row W2-M393, DEC-877 item 4), so a bare `gov` there runs the tree's code; `GOV_DEV_TIERS` included as well.
- **The owner's re-plan (DEC-941 item 1.3):** K6's lead starts as soon as the ticket is filed. Block D (W2-56, then W2-21's `gov launch lead`, W2-20 and W2-42) puts the leads themselves in a sandbox. Today they run unsandboxed (lens E F1). The block is estimated at about 6 lead-days, done by about 2026-11-07 (REPLAN-W2 §3).
- **W2-56 closes before W2-27 starts** (DEC-799 item 4).

## The decisions for this run

- **Design first: the CIT-E** (`docs/changes/W2-56-CIT-E.md`), written by a fresh engineer before any code. It states:
  - **the write list:**
    - each allowed path's form, and how the operating system holds it as a literal path;
    - for a form it cannot hold literally (a name pattern such as `test_batch*`): how it is held, and what stays open beside it. This is named in the note and in the launcher's one line on stderr, never widened silently;
    - what the list adds: git's folders, the session's temp folder (DEC-159) and its own run folder (DEC-728);
    - never `/tmp/gov-cbm-<uid>` (DEC-799 item 2);
  - the code graph's folder: under the session's temp folder inside a sandbox, unchanged outside it, and how the code knows which case it is in;
  - every placeholder name the sandbox makes, and how none reaches a commit. A file outside the paths that this needs (an ignore file, the guard's containment check) is a package;
  - **the cleaned environment:** the variables kept, by name, each with its reason; every `CLAUDE*`, `GOV*` and `PYTHONPATH` value of the parent dropped;
  - the refused arguments, weighed against an accepted-arguments list (lens E R6);
  - the start lock per repository (lens E F17), or the other way the note shows;
  - the split with W2-60a (below), line by line in `launcher.py`.
  
  The test designer reads its behaviour sections; if the guard refuses it the file (one this branch changes, DEC-820 (c)), give them in its brief as text. The reviewer reads the whole note.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`, a measured trial for FULL test designers, DEC-839; its brief must not set `TMPDIR`), in `tests/acceptance/W2-56/`:
  - one case per KPI line, in temporary repositories built from scratch;
  - **the write list, enforced by the operating system:** a worker's script (`python3 -c` with `open(..., 'w')`) is refused when it writes:
    - under `.gov-runtime/` outside the session's scratch;
    - in another worktree;
    - under `tests/acceptance/**`, for every role but the test designer.
    
    A write inside the list succeeds;
  - a suite that builds the code graph runs inside a launched, sandboxed worker, and outside a sandbox the folder stays where it is;
  - each placeholder name planted: an ordinary `git add` (`-A` included) and `git commit` stage and commit none of them;
  - the launcher started with each parent variable set (the session id, the messaging socket and its token, the child-session mark, effort, the compaction window, the subagent model, `GOV_DEV_TIERS`, `PYTHONPATH`): none of them reaches the session;
  - each refused argument, in its spaced and its `=` forms;
  - at least three launches at once, in worktrees that share one `.git`;
  - **live cases** at `claude-opus-5-5 --effort low`, marked and routed as the existing live-session files are (W2-57's README, `tests/acceptance/serial-only.txt`). A new entry in that list is a package;
  - **earlier tests whose meaning this ticket changes:** the designer names each and revises it with `Rewrite-Reason:` naming DEC-799 or DEC-826 Q5, lowering no other expectation.
- **The engineer** (fresh, `--effort high`) works only in the allowed paths. Until this ticket merges, an engineer whose suites build the code graph starts in the old form with the tripwire (the common brief); the brief names which suites need it.
- **Your workers start through the pinned launcher (this ticket only).** This ticket rewrites the write list and the environment that every launched session gets.
  - So start every worker with the pinned `gov launch` (a bare `gov`, with no `PYTHONPATH`), in the common brief's form otherwise. Its `src/gov/launch/` and `src/gov/guard/` are the same as `w2/integrate`'s at the time of writing.
  - A half-built launcher in this worktree never starts your workers; it is exercised by the tests only. That way a fault in it cannot fail open, or refuse, on your own workers.
  - Every test run and every verification command still runs this worktree's `src/` (DEC-732).
- **Fail closed everywhere:**
  - a sandbox that cannot be built still refuses the launch;
  - an allowed path that cannot become a literal rule is named, never widened silently;
  - every refusal the launcher makes today still refuses (DEC-313's, DEC-218's, W2-58's).
- **Beside W2-60a, on `src/gov/launch/` (both tickets' "Beside" paragraphs, DEC-786):**
  - **Yours:**
    - `sandbox.py` (new): the write list and the sandbox settings;
    - `environ.py` (new): the cleaned process environment;
    - `src/gov/codeintel/__init__.py`: the daemon's folder only;
    - `tests/unit/launch/**`, except W2-60a's `test_role*` and `test_launch_record*`, which you never write;
    - `tests/unit/codeintel/**` (the daemon's folder only) and `docs/changes/W2-56-CIT-E.md`;
    - in `launcher.py`: the sandbox's write list and filesystem settings, the process environment the session is started with (the `env=` of the start), the refusals of `--restricted`, `--safe-mode`, `--agents`, `--plugin-dir`, `--plugin-url`, `--mcp-config` and `--system-prompt`, the start lock, and the calls to your modules.
  - **W2-60a's:**
    - `role.py`, `record.py`, its two test-name patterns, `docs/changes/W2-60a-CIT-E.md` and `docs/research/W2-60-rules-probe.md`;
    - in `launcher.py`: the arguments the session is started with (role text, `--model`, `--effort`, `--session-id`, the switches for connectors, user-level agents and skills, and memory), the settings' `env` lines it sets (`CLAUDE_CODE_SUBAGENT_MODEL`), the refusals of `--agent`, `--append-system-prompt` and its file form, `--session-id`, a model not the role's and a compaction threshold, the record's write, and the calls to its modules.
  - **Two edges:**
    - `--agents` is yours and `--agent` is W2-60a's: a refusal of one never catches the other by prefix.
    - Your cleaned environment drops the compaction window that W2-60a's KPI 5 also names: the process environment is yours.
  - **Any change you need in W2-60a's files is a PACKAGES return.** The second ticket to merge merges the first back first.
- **Running beside you:**
  - W2-60a (above): its lead starts after yours, when a lead slot frees (at most 4 leads at once, DEC-941 item 1d).
  - W2-05 (`DAEO-0z8c`, merge-back) holds `src/gov/**/*.py` for the git environment of git calls, `codeintel/__init__.py` included: leave those lines as they are, and the later merge takes the conflict.
  - W2-58 (`DAEO-5j8b`) is in the close queue and still names `src/gov/launch/**` and `tests/unit/launch/**`. A repair from its close that touches the launcher reaches you through the orchestrator.
  - W2-20 holds `src/gov/launch/gate*`: untouched.
  - W2-67 (`DAEO-9nys`) holds `tests/unit/guard/**` and `tests/conftest.py`: touch neither.
  - W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
  - W2-21 follows you on the launcher; it does not run now.
  
  Do not touch their files. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no full run. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
  - **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **Reviews:** two (DEC-413). A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head, given the CIT-E.
  - **The probe asks above all whether any path lets:**
    - a sandboxed worker's script write outside the list;
    - `/tmp/gov-cbm-<uid>` onto the list;
    - an allowed path widen with nothing naming it;
    - a placeholder reach a commit;
    - a parent's `CLAUDE*`, `GOV*` or `PYTHONPATH` value reach the session;
    - a launch whose sandbox cannot be built start anyway;
    - a refusal the launcher makes today stop refusing.
  - Commit the probe record only when it passes.

## This run's order

1. The CIT-E (a fresh engineer batch).
2. Tests first (the test designer), then **check red yourself.**
3. The engineer.
4. Rebuild and verify in full.
5. Review 1. If it fails on a fail-open or lose-work finding an honest agent can hit: one test-design batch, one engineer, a full run, review 2 (the last).
6. **Return** DONE or PACKAGES. DONE means the probe passed and the branch is ready to merge, after or before W2-60a by DEC-786.

**Estimate:** about 250 lines, about two days with the full runs and the reviews.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit). Split the engineer's work into batches that fit.

---
