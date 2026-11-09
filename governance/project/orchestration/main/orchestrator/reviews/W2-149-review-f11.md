**Sandbox check (Step 0, `launch_worker.sh`): passed.**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-52ku` was refused: `OSError: [Errno 30] Read-only file system`.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (`1ae28402a109`), and so did `git update-index --refresh`.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing. I started no embedder, reranker or model.

- **task:** W2-149 (DAEO-52ku), the narrow review of the F11 follow-up (DEC-1112 (3); ACT-SETS-GLOBS-1 §3). The change adds `--setting-sources project` to the session's line and the canary's line. Branch `w2/W2-149-f11`, `d1e53016e..99cdce97a`.
- **status:** DONE. S9, S10 and S11 pass. There are two findings, F16 and F17. Both are in scope with ordinary work yes and consequence other, so neither blocks; `verdict.py` should compute READY.
- **work_completed:**
  - Read the six-file diff and the code path: `session_flags`, `run_canary`, `run_session`.
  - Read the ticket's S9, S10 and S11 lines, its failure lines and its last notes; round 1's F11; ACT-SETS-GLOBS-1 §3; ACT-INDEP-WALLS-1 §2 and §6.
  - Read the wall template (settings, hook, `CLAUDE.md`, `tree-exclude.txt`) with the Read tool only.
  - Read the installed CLI's help for `--restricted` and `--setting-sources`.
  - Ran the unit tests, the acceptance folder at the head, and a red check against the old script.
- **files_changed:** none. `git status` is clean. Step 0 (b) wrote one git object, as the brief requires. My scratch files were in the sandbox's temp folder and are all removed.
- **evidence:**
  - **Code:** `indep_launch.py:721-730` (`session_flags`), `:803-804` (the canary) and `:841-842` (the session). A grep finds no other place that starts `claude`. The diff is one hunk (3 lines added, 1 removed). No other file under `src/`, `governance/`, `template/` or `.claude/` changed.
  - **CLI help:** Claude Code 2.1.318 (`claude --help` and `--version`, run with an empty scratch HOME; no session started, and nothing was written to that HOME).
    - `--restricted`: "… and ignores user, project and local settings files (managed settings and --settings still apply; add --strict-mcp-config to skip MCP servers too). Also confines the file tools to the working directories (--add-dir included) …"
    - `--setting-sources <sources>`: "Comma-separated list of setting sources to load (user, project, local)."
    - `-p`: "Settings files that fail validation are silently ignored in this mode."
  - **Records:**
    - r1's F11: `W2-149-review-r1.md:151-154`; its open question at `:33`.
    - ACT-SETS-GLOBS-1: lines 83-114 (§3).
    - ACT-INDEP-WALLS-1: §2 (a)(1) at lines 70-72, which already says restricted mode "ignores user, project and local settings"; session B at line 191. Per `rehearse.sh:315-317`, session B ran `--setting-sources project` without `--restricted` or `--settings`.
    - `docs/assessment/2026-10/E-roles-context.md:939` quotes 2.1.292's help the same way.
  - **Searches:** two Grep searches in all (DEC-1092 (1)): the worktree, then the main tree's scratch. No `gov retrieve` (forbidden in the sandbox).
  - **Scratch:** at most about 5.2 MB and 1,223 files and folders in the sandbox's temp folder; now 0.
- **tests:** all at `99cdce97a` unless noted. Every run went through the heavy slot with `-p no:cacheprovider --optin=lifted --optin=breadth`, `PYTHONPATH=<worktree>/src`, an empty scratch HOME, `PYTHONUSERBASE=/home/usain/.local` and `PYTHONDONTWRITEBYTECODE=1`.
  - **Unit tests:** `tests/unit/orchestration/test_w2_149_indep_launch.py` gave **74 passed**. The required `-m "not local_only" -k "not real and not green_here and not time_limit"` left none out.
  - **Acceptance folder:** `tests/acceptance/W2-149` gave **77 passed, 3 skipped (live), 1 deselected**. The `-k "not real"` exclusion left out `test_w2_149_seed_content.py::test_s6_two_real_builds_draw_different_63_bit_seeds`, which uses only the stub and no model. Run alone it gave 1 passed. That makes **78/0/3**, the engineer's count. No case is marked `local_only`.
  - **Red check:** I exported `d1e53016e`'s script and schemas with `git archive` into scratch and ran `test_w2_149_canary_session.py` against it through the support file's `W2_149_SCRIPT`. Result: **1 failed, 14 passed**. The failure is the new case, at line 220: "the canary's line gives --setting-sources []; want exactly ['project']".
  - **Sandbox hiccup:** the first acceptance attempt did not start. bwrap reported "Can't get type of source …/.git/config.lock" (another session's lock file had disappeared). The single retry ran normally.
  - **Live cases:** not run, because they need a real session and are the CTO's to run outside the sandbox. I took their results from the brief; I did not find their log.
- **discoveries:**
  1. `--restricted` already ignores the user, project and local settings files (2.1.318's help). See F16 and F17.
  2. The operator's launcher (W2-148, `governance/project/operator/operator_launch.py:42-46`) runs `claude -p --restricted --settings …` without `--setting-sources project`. By the help it does not need the flag. Adding it for parity is the CTO's call and outside this ticket.
  3. The launch sandbox can fail at setup when another session's `.git/config.lock` disappears while the sandbox is being built. I saw it once; a retry worked.
  4. Today there is no `~/CLAUDE.md`, `~/CLAUDE.local.md` or `~/.claude/CLAUDE.md` (I checked existence only).
- **risks:**
  - How `--restricted` and `--setting-sources project` combine is not documented.
  - If the second flag turns the project source back on under `--restricted`, the settings cannot widen: the project source is the wall's own file. But project memory files might load where `--restricted` alone may not have loaded them: the wall's own `CLAUDE.md`, and any `CLAUDE.md` in the folders above the wall. This is not verified.
  - None exists under HOME today. I did not check the real sets root's top level, because of the hidden-half rule.
- **lessons:**
  - Read a flag's effect in the installed CLI's help before a package states it. Here one line of 2.1.318's help answers round 1's open question.
  - In this harness a Glob pattern with no folder part matches at any depth. My `CLAUDE*.md` search at HOME listed file names, not contents, across HOME, including under `~/gov-os-runs/`. No hidden-half path appeared in what was shown.
  - My one existence check also named `~/.claude/CLAUDE.md` (absent). Both checks went wider than the brief allows. No contents were read.
- **proposed_decisions:**
  1. **Keep the flag, but correct its stated reason.** The flag does no harm. It keeps the user and local files out if a later Claude Code narrows `--restricted`, and may keep out a future `~/.claude/CLAUDE.md`.
     - The records to correct, when they are next touched (DEC-802): S10's [changed] clause, the evidence file's F11 section, the ticket's last note, and ACT-SETS-GLOBS-1 §3.
     - What they should say: `--restricted` already ignores those files; the wall's settings load by `--settings`; `--setting-sources project` is a second guard.
     - A row, not a round. Confidence: high on the help text, medium on how the flags combine.
  2. **Optional probe, for the CTO outside the sandbox,** to settle how the flags combine.
     - Plant a wall with a marker `CLAUDE.md` in the folder above it.
     - Run the canary's line with and without `--setting-sources project`, with `--debug-file`.
     - See whether the marker or the project source loads.
     - A row; not blocking.
- **unresolved:**
  - How the two flags combine.
  - Whether `--restricted` stops `CLAUDE.md` discovery; its help names settings files only.
  - The log of the live run at `99cdce97a`, which I did not find.
- **recommended_next_action:** READY by `verdict.py` over the block below: no finding is in scope, ordinary work and fails open or loses work. Record F16 and F17 as rows. The CTO merges as planned; the probe is optional.

## Checks 1-4

1. **The flag on both lines: yes.**
   - `session_flags` now starts `-p --restricted --setting-sources project --settings <wall>/.claude/settings.json --add-dir <tree>`. No other flag moved or changed.
   - Only two places start `claude`, and both take their flags from `session_flags`: the canary (`:803-804`, which adds its own folder as a second `--add-dir`) and the session (`:841-842`). So each line carries the flag exactly once, next to `--restricted`.
   - These are unchanged: the prompt and `PROMPT_SHA256` (`:92-94`), the environment (`SESSION_ENV` at `:87`, `clean_env` at `:715-718`), and everything after the session.
   - The unit tests pin the whole session line, and check that the canary's flags equal the session's except `--session-id`.

2. **Nothing the wall needs is lost: yes, but not for the reason the record gives (F16).**
   - Under `--restricted`, "managed settings and --settings still apply". So the wall's settings and its hook load by `--settings`, with or without the new flag.
   - The new flag only chooses among the user, project and local sources. At most it turns the project source back on, and that is the wall's own file again. It cannot add any other refuser of the canary's Read, and it cannot drop the `--settings` file or its hook.
   - The canary still proves the settings loaded. With one key corrupted, the file is silently ignored on every route that names it, because every route names the same file. The Read in the canary's own `--add-dir` folder is then not refused, and the launch refuses with 16 (`:822-831`).
   - If a future CLI rejected the flag, the canary would exit non-zero and the launch would refuse with 16, so it fails closed.
   - The CTO's live S9, as reported, shows both directions.

3. **The case tests what S10 now says, with one limit (F17).**
   - The stub's rule matches the documented `--setting-sources` on its own (with no flag, every source loads). The premise loop drives the stub without `--restricted`, where that is right.
   - The stub does not model `--restricted`'s rule about settings files.
   - Red without the flag and green with it: both confirmed above.
   - No existing case was weakened:
     - The case file's diff only adds lines.
     - The stub's new canary check over `(user, loaded)` is the old check whenever no user file is planted, and only the new case plants `<HOME>/.claude/settings.json`.
     - `--setting-sources` was already parsed as a flag with a value (`w2_149_support.py:291-294`, unchanged).
     - The other 14 cases pass against both scripts.

4. **Failure lines: none now passes where it should fail.**
   - Line 5: every flag it names is still on the session's line (pinned by the unit tests). The working folder and the environment are unchanged.
   - Line 4: the canary's decision code is untouched.
   - Line 10: the new case uses only the planted HOME. Its premise loop runs with `HOME=world.home`.

## Findings

**F16 (scope: in). `--restricted` already keeps the user, project and local settings files out. The record's reason for the flag, and its claim that the wall's file also loads as the project source, rest on a premise the CLI's help contradicts. How the two flags combine is undocumented.**
- At `d1e53016e`, both lines already carried `--restricted`, so they already kept `~/.claude/settings.json` and `.claude/settings.local.json` out. That answers round 1's open question.
- ACT-SETS-GLOBS-1 §3 (lines 103-105) says the user file's allow lines, `acceptEdits` and its environment variable "load into every wall". That does not hold for these lines.
- Four records credit the new flag with keeping those files out, or say the wall's file also loads as the project source:
  - S10's [changed] clause;
  - the evidence file ("Only the wall's own project settings load");
  - the ticket's last note;
  - ACT-SETS-GLOBS-1 §3 (lines 106-109).
- Under `--restricted`, the wall's settings load by `--settings`.
- Session B, which the records cite, ran the flag without `--restricted` or `--settings`. So it says nothing about the two flags together; only the CTO's live run at `99cdce97a` does.
- What still holds: nothing the wall needs is lost, the canary still refuses with 16, and the flag is a real second guard if `--restricted` narrows later.
- Ordinary work: yes, because every launch carries both flags, and every later reader of S10, the evidence file or ACT-SETS-GLOBS-1 §3 will take the stated reason as the mechanism.
- Consequence: other (nothing fails open and no work is lost; the cost is a wrong reason on record and an undocumented interaction between flags).

**F17 (scope: in). The stub models `--setting-sources` but not `--restricted`'s rule about settings files, so the new case's red at `d1e53016e` happens only in the stub, not in Claude Code.**
- `user_source` (`w2_149_support.py:416-423`) turns the user source on whenever `--setting-sources` is absent, even when `--restricted` is on the line.
- So in the stub, the old line loads the planted user file. Claude Code 2.1.318 would not load it.
- The case still checks S10 fairly:
  - The KPI's own Verify line asks for exactly this stub behaviour.
  - The stub always loads the `--settings` file, as the help says.
  - The stub is stricter than Claude Code, so a line without the flag can only fail, never pass.
- The README row that says "red at `d1e53016e` … the stub loads the planted user file" is true of the stub only.
- Ordinary work: yes, because the case runs in every `gov accept W2-149`, and its README row is what a reader sees.
- Consequence: other (the stub is stricter than Claude Code; it cannot pass a line without the flag, and no work is lost).

```verdict
{"kpis": [{"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": [{"id": "F16", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F17", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S11", "verdict": "pass", "findings": []}]}
```