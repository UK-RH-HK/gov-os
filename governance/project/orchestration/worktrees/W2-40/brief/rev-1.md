# The FULL review of W2-40 (DAEO-6ox0): EXP-002's hook-limit record, round 1 of at most 2

Template: role-reviewer@1.0.0 (`template/governance/kernel/templates/role-reviewer.md` in the tree; read it). Written by the ticket lead (orchestrator, W2-40), 2026-11-11. Budget: projection_usd 5.

You are a fresh, read-only independent reviewer (role `independent-auditor`, ticket `DAEO-6ox0`) of the head **`9f71c6bc4240`** of the tree `/home/usain/gov-os-worktrees/W2-40` (branch `w2/W2-40`). You read everything; you change nothing; you write nothing in any tree.

## Step 0, the sandbox check, before any work, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6ox0','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work (the form of `EMG-d4b-launched.md`, copied beside this brief). If (a) wrote the file or (b) failed, stop there and return. Write any hash it prints as 12 digits only.

## First
- `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-6ox0`).
- `git -C /home/usain/gov-os-worktrees/W2-40 rev-parse --short=12 HEAD` must equal `9f71c6bc4240` at the start **and at the end** of your review; if it differs, stop and say so.

## The history (what you need to judge)
- The ticket (`.tickets/DAEO-6ox0.md` in the tree) is a FULL research ticket. Its one live KPI line, **S1**: "Each of these is measured: the harness's behaviour at a hook's time limit, so that the guard's deadline sits below it. Verify: the experiment's evidence record holds, for a planted hook that sleeps past the limit, the measured outcome the harness gave (the call allowed, denied or failed, the time it took) as a number with its unit, and the guard's configured deadline recorded below that measured limit [W2-H052, W2-M347, W2-L328]". The ticket's other three lines are lifted (DEC-1083: the sandbox cases, file tools/hooks/MCP outside the sandbox, auto-compaction): they are non-goals here. Also non-goals: any change to `.claude/settings.json`, the hook programs, the guard, `src/`, `template/`, the path map (a recommendation goes in the record as a draft, never into a file: those are controls, by ACT only); `tests/**`; the ticket file.
- The earlier, delegated run (DEC-578, 2026-10-09, Claude Code 2.1.288): `docs/research/EXP-hook-time-limit.md`: at a 5 s PreToolUse limit a hook sleeping 25 s let the call through. It measured a limit the repository does not use; the repository's entries carry `"timeout": 60` and the guard's PreToolUse program keeps its own 20 s deadline. Hence this run's 60 s cases.
- **The split:** the experiment starts headless `claude -p` sessions, which need the model API; a research worker's sandbox has none. So: a first research session (Sonnet, sandboxed) wrote `experiments/EXP-002/run_hook_limit.py`, its `README.md` and the record's skeleton (commit `37320b6a5889`); **the lead** ran the thirteen cases outside the sandbox on 2026-11-11, one call each, `--model claude-haiku-4-5-20251001`, `--base /tmp/gov-os-lead-W2-40/hook-exp` (outside every repository; removed afterwards), `--out` the lead's scratch; a second, fresh research session wrote the record from the result lines (commit `6b01098c505e`). The lead then merged `w2/integrate` (W2-105's land, no file the record cites) into the branch: `9f71c6bc4240`. The ticket's own change is `git -C /home/usain/gov-os-worktrees/W2-40 diff --name-only w2/integrate...9f71c6bc4240` (all under `experiments/EXP-002/`).
- You re-run nothing (you have no model API, and a reviewer re-runs nothing the lead ran).

## The judged paths
- `experiments/EXP-002/**`: the record `hook-limit-record.md`, the script `run_hook_limit.py`, `README.md`, and `results/` (thirteen JSON lines, copies of the lead's).
- **The lead's raw result lines**, for comparison: `/home/usain/gov-os-worktrees/W2-40/.gov-runtime/scratch/lead/exp/results/` (the same thirteen file names; the lead's scratch inside the tree).
- The ticket file `.tickets/DAEO-6ox0.md`.
- For the facts the record cites, at the probed head: `.claude/settings.json`, `.claude/hooks/pretooluse.py`, `template/.rulesync/hooks.jsonc`, `src/gov/guard/decide.py`, `docs/research/EXP-hook-time-limit.md`, and the decisions in `docs/DECISION_REGISTER.md` (grep `### DEC-n`; it is large): DEC-160, DEC-578, DEC-580, DEC-587, DEC-590, DEC-827, DEC-1083. Rows W2-H052, W2-M347, W2-L328 in `docs/plan/WAVE_2_LIST.md`.

## What to judge
(i) **S1 as its `Verify:` says, each word:** a planted hook that sleeps past the limit; the measured outcome the harness gave (allowed, denied or failed) and the time as a number with its unit, for the limit the repository uses (60 s) as well as the 5 s case; the guard's configured deadline recorded below the measured limit: the 20 s and the 60 s read from the files at the probed head, path and line true.
(ii) **A fair test:** the control refuses and is honoured; the hook really ran past its limit (the ticks and the sleep); the setup could not have been influenced by a user-level hook or the guard's own hooks (`--setting-sources project`, the `CLAUDE*`/`GOV_*` removal, a project outside any repository); n = 2 agrees; the record holds no number the lines do not hold (check every row of `Measurements` against its line).
(iii) **The conclusion says no more than the numbers** (one version, one tool, one model, headless, a shell hook, not the guard's program), and the recommendation names a control change as an ACT, never as a file change here.
(iv) The rows W2-H052, W2-M347, W2-L328 are answered or named "not measured".
(v) Nothing under `experiments/EXP-002/` holds a secret, a raw stream, or a settings file's contents beyond the throwaway ones.
Say what you probed and found sound, as well as what you found wrong. Describe each finding as behaviour (what was done, what happened, what should have), never as code.

## Rules
- **DEC-732, word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- `gov retrieve` is not available in your sandbox (DEC-1065): read with the Read and Grep tools; if a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all.
- **DEC-820:** reads are open; never read or print secrets or keys; never the held-out qualification material's contents; never the hidden half of any evaluation set (`~/gov-os-eval/`, `~/gov-os-runs/`, any `hidden`, `memory-verdict` or `memory-verdict-2` folder). Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`): take the refusal, never another spelling; read named files instead; count the refusals in your return.
- **Row W2-L423's rule (DEC-911):** in your return write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string for a token.
- **One bar, two rounds (DEC-1010, DEC-1131):** a finding blocks only if it is in scope (the S1 line, not the non-goals), reachable in ordinary work, and fails open or loses work; everything else lands as a recorded row. This is round 1 of at most 2. A KPI line you mark `fail` blocks on its own (DEC-1131 (3)).
- Single simple Bash commands; no installs; no GPU; you write nothing in any tree: `git -C /home/usain/gov-os-worktrees/W2-40 status --porcelain` is empty when you finish.
- **Refused twice for the same call: stop and say so; no third try.**

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## Your record (your session's final message, in full)
- The twelve labelled fields first (below); put the probed commit `9f71c6bc4240` and your session id in `evidence`; the sandbox check result first in `evidence`.
- Your record's `task: DAEO-6ox0` and `decisions:` (the ids your findings rest on, DEC-1073).
- Your answers to (i) to (v).
- Every finding: what was done, what happened, what should have; `scope: in|out`; `Ordinary work: yes|no, because …`; `Consequence: fails open|loses work|other`; what evidence would reverse it (DEC-1014).
- At the end, the fenced `verdict` block, one entry, KPI id exactly `S1`:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
Refused twice for the same call: stop and say so.
