Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-f11/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the narrow review of the F11 follow-up (DAEO-52ku)

You are a fresh, read-only independent reviewer. **Narrow scope: one point.** The CTO's delegated decision (DEC-1112
(3); ACT-SETS-GLOBS-1 §3, in the main tree at
`/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-SETS-GLOBS-1.md`): **the launch
script's S10 line carries `--setting-sources project` for the real session and the canary alike, so the real HOME's
user and local settings files never load into a wall; nothing else in the launch changes.** S10's ticket wording is
marked `[changed, DEC-1112 (3): F11]` (`.tickets/DAEO-52ku.md`; read S10, S9 and the ticket's last note). Everything
else in W2-149 was reviewed READY in two rounds and merged (`b4de529b`); it is not re-opened here. Round 1's F11 (the
finding this answers) is in `.gov-runtime/scratch/ref/W2-149-review-r1.md` if your worktree holds it, else in the main
tree at `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/W2-149-review-r1.md`.
READY is computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-149-f11` in `/home/usain/gov-os-worktrees/W2-149-f11`, head `99cdce97a`, from `w2/integrate`
  at `d1e53016e`: `git diff d1e53016e..99cdce97a`. The designer's case (`tests/acceptance/W2-149/`: the stub's user
  settings rule in `w2_149_support.py`, the new S10 case in `test_w2_149_canary_session.py`, the README's S10 lines;
  `8bb4d9726`, merged at `5e3c9abf4`); the engineer's change `b61815b72` (`session_flags` in
  `governance/project/orchestration/tools/indep_launch.py`, the unit tests) and its evidence section `99cdce97a`.
- **The runs:** the engineer's `gov accept W2-149` in the sandbox at `99cdce97a`: **78 passed, 0 failed, 3 skipped
  (live)**, success-10 5/5; unit tests 74/74. The CTO's three live cases outside the sandbox at `99cdce97a` (haiku,
  planted roots, the real HOME for the login): **3 passed** (`GOV_W2_149_LIVE=1`, 2026-11-09 23:3x UTC): the real `claude` accepts `--setting-sources project` beside `--restricted` and `--settings`; the real canary is refused with valid settings (so the wall's settings and hook still load as the project source and by `--settings`) and not refused with one key corrupted (16); every outside Read in the live wall refused (S11); 0 traces (S12).
- **Check:**
  1. **The flag on both lines:** `--setting-sources project` exactly once, on the session's line and the canary's,
     with no other flag moved or changed; the prompt and its sha256 constant, the environment and everything after the
     session unchanged. Read the code path, not only the tests.
  2. **Nothing the wall needs is lost:** the wall's own settings still load (by `--settings`, and as the project
     source from the wall as the working folder); the canary still proves the settings loaded (S9) and would still
     refuse with code 16 if they did not. Can `--setting-sources project` make the canary pass while the wall's
     settings are ignored, or make the wall's hook not run?
  3. **The case tests what S10 now says:** the stub's user-source rule (no flag, or a list naming `user`, loads
     `$HOME/.claude/settings.json`; a list without `user` does not) is a fair model of Claude Code's documented
     `--setting-sources`; the case is red without the flag and green with it; no existing case was weakened.
  4. **Failure lines:** no failure line of the ticket now passes where it should fail (in particular failure line 5:
     a session started without `--restricted`, the wall's `--settings`, `--no-session-persistence`,
     `--strict-mcp-config` or the budget).

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns the F11 point above.

## Write and return
- **You write nothing** in any tree. You may run the tests read-only (`-p no:cacheprovider --optin=lifted
  --optin=breadth`) through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-f11/src` and an empty scratch HOME
  (`PYTHONUSERBASE=/home/usain/.local` so pytest is found). Never run anything against the real `~/gov-os-eval/`,
  `~/gov-os-runs/`, `~/gov-os-wall-trees/`, `~/.claude/` or a real `claude` session. No GPU. Single simple Bash
  commands (DEC-1080). The hidden-half rule holds. Read the template folder `governance/project/indep-walls/` with the
  Read tool only, never naming it in a Bash line.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (task,
  status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), your answer to checks 1-4, every finding with its two lines
  and scope (ids from F16), and at the end the fenced `verdict` block over the lines the change touches:
  `{"kpis": [{"kpi": "S9", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S10", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S11", "verdict": "pass|fail", "findings": [...]}]}`
  with each finding `{"id", "scope", "ordinary_work", "consequence"}`.
Refused twice for the same call: stop and say so; no third try.
