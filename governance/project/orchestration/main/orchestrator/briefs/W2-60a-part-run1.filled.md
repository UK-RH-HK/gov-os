You are the ticket lead for ticket `DAEO-cv58` (`W2-60a`, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL, keystone 3, working only in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `a1629f1860ca`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-cv58.md`) and its cards in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-60 " and "#### W2-60a");
- W2-56's ticket file (`.tickets/DAEO-wnnz.md`), its paragraph "Beside W2-60a" above all;
- DEC-826 (Q1 and Q5), DEC-838, DEC-839, DEC-832, DEC-801, DEC-786 and DEC-941 (item 1.3);
- lens E (`docs/assessment/2026-10/E-roles-context.md`) F2, F13, F14, F15 and R6; lens F (`docs/assessment/2026-10/F-models-context.md`) F1, R1 and R6;
- the launcher as it stands (`src/gov/launch/launcher.py`, `command.py`), the role files (`template/governance/kernel/roles/*.md`) and their generated copies (`.claude/agents/`), and the skills (`template/governance/kernel/skills/`, generated as `.claude/skills/`).

## Why you start now

- **A launched session loads none of its role's text** (lens E F2). Its role reaches it only through a brief written by hand for each run.
- **Nothing ties a session to its stated model, effort and skills:**
  - no launch sets effort;
  - the compaction threshold was a user-level value (lens F F1);
  - the model a subagent runs on is not the one recorded (lens E F14);
  - the loaded skill copy has no version (lens E F15).
- **Today the prompt's launch forms carry these values by hand** (DEC-839 item 5).
- **The owner's re-plan (DEC-941 item 1.3):** K3's lead starts as soon as the ticket is filed, beside the memory work. Block C (W2-60, W2-11, W2-09, W2-33) is estimated at about 7 lead-days, done by about 2026-11-07 (REPLAN-W2 §3). W2-33's skill packs (DEC-832) load through this ticket with no code change, and W2-21 builds on your launch record.

## The decisions for this run

- **The rules probe comes first (KPI line 9, lens G Q4): yours, in your own session, before the engineer starts.**
  - **Where:** a throwaway repository built from scratch in your temp folder (`/tmp/gov-os-lead-W2-60a/rules-probe/`). Never under `.gov-runtime/`, never a copy of this tree. It holds one `paths:`-scoped file under its `.claude/rules/`.
  - **The three questions:**
    1. Does the file load in a headless worker started by `gov launch`? A session quotes a token that only that file holds, once for a path the file matches and once for a path it does not.
    2. What does it cost in tokens? Compare the session's JSON usage with the file and without it.
    3. Can the worker change it? Try its Edit, its Write and a Bash write to it, and record each as refused or not.
  - **How:** build the repository the way the launcher's live tests build theirs (read W1-46's and W1-28's acceptance support files). If `gov launch` cannot start there, use the CLI with the settings `gov launch` builds, and name the difference.
  - **Live sessions:** `claude-opus-5-5` at `--effort low`, no more of them than the three questions need.
  - **Your notes** (figures, session ids, commands) go in `.gov-runtime/scratch/lead/rules-probe.md`. You write no file under `docs/` (the common brief's rule 2), so the engineer's design batch commits them as `docs/research/W2-60-rules-probe.md`, unchanged in substance, naming you as the one who measured.
- **Design first: the CIT-E** (`docs/changes/W2-60a-CIT-E.md`), written by a fresh engineer before any code, in the same batch as the probe record. It states:
  - where the role's text, its skills and its default line are read from (the role file, the generated agent, the synced skill copy), and which copy the session actually loads, so that each recorded hash is that copy's;
  - **the default line's exact form** (model and effort, no threshold). W2-11 writes the line into every role file through its CIT-P (DEC-839 item 5), and no file states its form yet (the role files say only "Model tier: standard"). So it is stated once here; give it in your return, and the orchestrator carries it to W2-11;
  - how connectors, user-level agents and skills, and model-side memory are kept out (the CLI's switches). Anything the CLI gives no switch for is a package naming it, never passed silently;
  - the launch record: its one folder, shared by every worktree of the repository; its keys; written before the session starts; a record that cannot be written refuses the launch;
  - the split with W2-56 (below), line by line in `launcher.py`;
  - **every existing test the change touches.** After this ticket, a repository with no role file, or with a role file that has no default line, is refused. So the note lists every unit and acceptance test whose repository lacks either (look at W1-28, W1-32, W1-46, W1-49, W2-50, W2-58 and `tests/unit/launch/`), and says how each is handled. Never by a fallback that launches without the role: that fails open.
  
  The test designer reads its behaviour sections; if the guard refuses it the file (one this branch changes, DEC-820 (c)), give them in its brief as text. The reviewer reads the whole note.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`, a measured trial for FULL test designers, DEC-839; its brief must not set `TMPDIR`), in `tests/acceptance/W2-60a/`:
  - one case per KPI line, against fixture role files and skills built at test time in temporary repositories (W2-11 has not written the real default lines yet);
  - a test home planted with a connector, a user-level agent, a user-level skill and a model-side memory file; none of them shows in the session's start;
  - each argument refused after `--`, in its spaced and its `=` forms: `--agent`, `--append-system-prompt` and its file form, `--session-id`, a `--model` that is not the role's, and a compaction threshold;
  - **live cases** (a launched session's log showing its role text) at `claude-opus-5-5 --effort low`, marked and routed as the existing live-session files are (W2-57's README, `tests/acceptance/serial-only.txt`). A new entry in that list is a package;
  - **earlier tests whose meaning this ticket changes:** the designer names each and revises it with `Rewrite-Reason:` naming DEC-826 Q1 or DEC-839 item 5, lowering no other expectation. A revision outside its folder that it cannot make is a package.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in the allowed paths:
  - `src/gov/launch/role.py` (new): the role's text, its skills and its default line, read and hashed;
  - `src/gov/launch/record.py` (new): the launch record;
  - `src/gov/launch/launcher.py`: the CLI line, the settings' env lines it sets, its argument checks, and the calls to `role.py` and `record.py` only;
  - `tests/unit/launch/test_role*`, `tests/unit/launch/test_launch_record*`, and the CIT-E and the probe record.
  
  A unit test elsewhere in `tests/unit/launch/` that this change breaks is a package: W2-56 holds that folder.
- **Your workers start through the pinned launcher (this ticket only).** After the engineer's first code commit, this worktree's launcher refuses every launch whose role file has no default line, and the real role files have none until W2-11.
  - So start every worker with the pinned `gov launch` (a bare `gov`, with no `PYTHONPATH`), in the common brief's form otherwise. Its `src/gov/launch/` and `src/gov/guard/` are the same as `w2/integrate`'s at the time of writing.
  - The launcher under test is exercised by the tests only, never trusted to start its own workers.
  - Every test run and every verification command still runs this worktree's `src/` (DEC-732).
- **Fail closed everywhere:**
  - the launch is refused when the role text, a named skill, the default line or the record is missing or cannot be read;
  - the launch is refused when a model given after `--` is not the role's;
  - every refusal the launcher makes today still refuses (DEC-313's, DEC-218's, W2-58's).
- **Beside W2-56, on `src/gov/launch/` (both tickets' "Beside" paragraphs, DEC-786):**
  - **Yours:**
    - `role.py`, `record.py`, `tests/unit/launch/test_role*`, `tests/unit/launch/test_launch_record*`, `docs/changes/W2-60a-CIT-E.md` and `docs/research/W2-60-rules-probe.md`;
    - in `launcher.py`: the arguments the session is started with (role text, `--model`, `--effort`, `--session-id`, the switches for connectors, user-level agents and skills, and memory), the settings' `env` lines you set (`CLAUDE_CODE_SUBAGENT_MODEL`), the refusals of the arguments you now set yourself, the record's write before the session starts, and the calls to your modules.
  - **W2-56's:**
    - `sandbox.py`, `environ.py`, `src/gov/codeintel/__init__.py` (the daemon's folder), the rest of `tests/unit/launch/**` and `tests/unit/codeintel/**`, and `docs/changes/W2-56-CIT-E.md`;
    - in `launcher.py`: the sandbox's write list and filesystem settings, the process environment the session is started with (the `env=` of the start), the refusals of `--restricted`, `--safe-mode`, `--agents`, `--plugin-dir`, `--plugin-url`, `--mcp-config` and `--system-prompt`, the start lock, and the calls to its modules.
  - **Two edges:**
    - The launcher's own line may carry a flag that it refuses after `--`.
    - KPI line 5's "no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in the session's environment" falls on W2-56's cleaned environment. You keep it out of the settings and refuse it after `--`. If your tests are red on the process environment alone, return a package; do not edit the `env=` line.
  - **Any change you need in W2-56's files is a PACKAGES return.** The second ticket to merge merges the first back first.
- **Running beside you:**
  - W2-56 (above).
  - W2-05 (`DAEO-0z8c`, merge-back) holds `src/gov/**/*.py` for the git environment of git calls: leave those lines as they are, and the later merge takes the conflict.
  - W2-58 (`DAEO-5j8b`) is in the close queue and still names `src/gov/launch/**` and `tests/unit/launch/**`. A repair from its close that touches the launcher reaches you through the orchestrator.
  - W2-20 holds `src/gov/launch/gate*`: untouched.
  - W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
  - W2-60b and W2-21 follow you; they do not run now.
  
  Do not touch their files. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no full run. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
  - **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - **A case that launches with this repository's own role files** is refused until W2-11 writes their default line. Name each such case with that cause and change nothing for it. The orchestrator holds the merge until W2-11 (the ticket).
  - Any other red is named with its cause.
- **Reviews:** two (DEC-413). A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head, given the CIT-E and the probe record.
  - **The probe asks above all whether any path lets a launch start with:**
    - no role text;
    - a skill unrecorded, or recorded from another copy than the one loaded;
    - a model other than the role's;
    - a compaction threshold;
    - a user-level agent, skill or connector, or model-side memory.
  - **It also asks** whether a record can be missing, be written after the start, or name another session, and whether any refusal the launcher makes today no longer refuses.
  - Commit the probe record only when it passes.

## This run's order

1. The rules probe (your session).
2. The CIT-E and the probe record (a fresh engineer batch).
3. Tests first (the test designer), then **check red yourself.**
4. The engineer.
5. Rebuild and verify in full.
6. Review 1. If it fails on a fail-open or lose-work finding an honest agent can hit: one test-design batch, one engineer, a full run, review 2 (the last).
7. **Return** DONE or PACKAGES. DONE means the probe passed and the branch is ready to merge once W2-11's default lines are in; it merges after or before W2-56 by DEC-786. Give the default line's form in DONE.

**Estimate:** about 250 lines, about two days with the probe, the full runs and the reviews.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit). Split the engineer's work into batches that fit.

---
