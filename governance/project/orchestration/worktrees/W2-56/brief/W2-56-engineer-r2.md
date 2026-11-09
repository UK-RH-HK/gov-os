Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-56/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-56 — the engineer's brief, round 2 (DAEO-wnnz)

You are a fresh engineer for **W2-56** (`.tickets/DAEO-wnnz.md`: read it in full, with "The engineer's round-1 points
settled" at its end). Round 1 (head `8eb7a39aa` on `w2/W2-56`) built every line: `gov accept W2-56` 255/0/5 in the
sandbox; the round-1 engineer's return is at
`/home/usain/gov-os-worktrees/W2-56/.gov-runtime/scratch/lead/log/W2-56-engineer.json` (its final `result`). The CTO's
runs outside the sandbox on `8eb7a39aa` (results only):
- `gov accept W2-56` with the real cases: 259 passed, 1 failed (S13's real case: its gov rebuild step is now out of
  S13 by P-1 (b); the test designer is revising that case; nothing for you unless the designer names the product).
- `tests/unit/retrieval/test_w2_112_shared_reranker.py`: all pass outside (round 1's 20 reds were the sandbox's).
- `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`: red on integrate
  too: not yours.

**Your job:**
1. **P-2:** `tests/unit/resources/test_w2_20_round3.py` (now in your paths): its stand-in CLI gets `MARKS` written into
   it instead of from the environment S5 cleans; keep every expectation. Show the file green.
2. **P-3:** `template/.rulesync/permissions.jsonc` (now in your paths): the rule that keeps S14's
   `Bash(gov launch:*)` through a rulesync regeneration; show that the generated template settings keep it (run the
   repository's own check for the template's generation if one exists in `tests/unit`; name the command).
3. **A regression of W1-27's W2-67 cases (D-2), outside the sandbox, on your code** (they pass 5/5 on integrate's code;
   run with `--optin=lifted,breadth`): 4 rows of
   `tests/acceptance/W1-27/test_w2_67_codegraph_folders.py::test_no_daemon_folder_of_a_project_the_case_made_is_left`
   fail, for example:
   `AssertionError: test_w1_27_rebuild_r2.py::test_rebuild_recreates_lexical_index is over, and the daemon folder of 1 project(s) it made is left (TD1C-A, DEC-914 item 2; DEC-898): ['/tmp/gov-cbm-1000/8c09333cb4eeade5 (project <tmp>/…/test_rebuild_recreates_lexical0/repo)']`
   (rows `[conftest-rebuild-project]`, `[make-rebuild-project-and-a-clone]`, `[origin-and-its-clone]`,
   `[w2_67b-rebuild-project]`). A case's nested `gov rebuild` now leaves its project's daemon folder in the shared
   `/tmp/gov-cbm-<uid>` where integrate's code left none: either the nested run no longer finds the test session's
   own folder (S1: "a suite that builds the code graph uses one daemon folder per test session … so no daemon folder
   is left behind"), or a clean-up integrate had is gone. Find which from the code and your own unit cases (never the
   acceptance source); fix it in your paths so no project folder lands in the shared place during a test session.
   You cannot run these cases in your sandbox (it makes `/tmp/gov-cbm-<uid>` read-only): build a unit case in
   `tests/unit/codeintel/` that plants the same shape (a nested `gov` process whose environment is rebuilt with its
   own `TMPDIR`) and shows where its daemon folder lands. The CTO reruns W1-27's cases outside.
4. **S7, seen in a real sandbox (the CTO's second run of the real cases on your code, after the S13 revision: S2, S9,
   S13 pass; S7 red; in the first run S7 passed, so it is intermittent):** three sessions started together in worktrees
   sharing one `.git`, each committing; one session's command fails before it runs:
   "The sandbox tried to bind-mount `config.lock` under the `W2-77` worktree's `.git` directory, and that file doesn't
   exist … a git lock that was present when the sandbox was set up and has since been removed." That is lens E F17
   itself, and it arises per command inside a running session (the CLI builds each command's sandbox), so a start lock
   held only while sessions start does not cover it. Find from the launcher's settings and the CLI's behaviour what
   makes the sandbox name `.git/*.lock` paths (a deny rule or a path the launcher lists that git's lock files sit
   beside, for example the common `.git`'s `config`), and change it in your paths so no git lock file is ever a bind
   source; or show in the CIT-E why it cannot be done in W2-56 and the smallest way that would. Unit-test the settings
   you build (no path under a `.git` folder in them that git rewrites through a lock).
5. Keep every round-1 line passing: `gov accept W2-56` again, and your unit folders.

## Where you work
- `/home/usain/gov-os-worktrees/W2-56`, branch `w2/W2-56` (integrate merged in with the ticket's new paths; the
  CTO merges the designer's S13 revision in when it lands). Your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/`** (G-14, DEC-820 (c)): only `gov accept`'s results and the messages above.
- **The exclusion line (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=acceptance`; every
  Grep or Glob call that could reach it carries `!tests/acceptance/**` (round 1 had one Grep without it: put it on every
  call); find carries `-path '*/acceptance' -prune`; never open the test designer's worktree (base name `W2-56-tests`).
  If a search shows you a line of a case anyway, stop reading it and say so.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56/src` and `-m "not local_only" -k "not real and not green_here and not time_limit"`:
  `tests/unit/launch tests/unit/codeintel tests/unit/resources/test_w2_20_round3.py`; then
  `python3 -m gov.cli.main accept W2-56 --root /home/usain/gov-os-worktrees/W2-56`. Never the full suite.
- **Commit as you go.**

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never touch the Ollama servers, the reranker service, `~/.local/bin`,
  `~/.ollama`, `~/.gov-os/`, `~/.cache/gov-os/` or any service; no GPU job; no installs.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Search again once
  (DEC-1092 (1)).
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-56` with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1112, DEC-799" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it): the twelve labelled fields of
`EMG-common.md` (sandbox and `ps` checks first), what changed for items 1 to 3 (the cause of item 3, with path and
lines), `gov accept W2-56`'s counts per line, the unit counts with every red named.
