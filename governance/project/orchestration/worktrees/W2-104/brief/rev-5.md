Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-104/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-104 (DAEO-drhj), independent auditor: run 5's narrow check (`scenario-summaries.md` left out of the session only)

**Role:** independent-auditor, a fresh read-only session. Write nothing in any tree; your verdict goes in your return.
**Worktree:** `/home/usain/gov-os-worktrees/W2-104`, branch `w2/W2-104`. **Probe:** head `ac18ac2ab7c8`.
**Ticket:** `DAEO-drhj` (W2-104), profile STANDARD, class C2: `gov skilleval`, the skill evaluation harness. Its text
is `/home/usain/gov-os-worktrees/W2-104/.tickets/DAEO-drhj.md` (read its last paragraph, "Reopened 2026-11-14"); its
sources DEC-959 and DEC-820 (read each by id in `/home/usain/gov-os-worktrees/W2-104/docs/DECISION_REGISTER.md`, grep
only by id). The reopening is the CTO's under DEC-1164 (18) (read it by id).

## Why this check
W2-104 landed after run 4 (narrow check PASS at `97b06de4eba1`). W2-101's review found (its F1, fails open) that the
harness copies a skill's folder into the session's `.claude/skills/<name>/` leaving out `scenarios.md` and
`scenario-records.yaml` but not a hand-written `scenario-summaries.md` beside them (W2-100's and W2-101's interface),
so the session under test could read its own runs' summaries. Run 5 did, and only this is under review:

1. `3ef7c62c4` (lead): a clean merge of `w2/integrate` at `c82335a401df` (no conflicts). Out of scope beyond check 4.
2. `ac18ac2ab` (engineer): `SUMMARIES = "scenario-summaries.md"` beside `SCENARIOS` and `RECORD` in
   `src/gov/skilleval/harness.py`, added to the `shutil.ignore_patterns(...)` of `run_scenario`'s copy, and one unit
   case `test_w2_104_session_folder_leaves_out_scenarios_records_and_summaries` in
   `tests/unit/skilleval/test_w2_104_skilleval.py`.

## Check
1. **The fix:** at `ac18ac2ab7c8`, the session's copied skill folder can hold none of `scenarios.md`,
   `scenario-records.yaml` and `scenario-summaries.md`, and still holds `SKILL.md` and the skill's other files. Read
   `run_scenario` and every other place the harness puts skill content in front of the session under test (the
   session prompt, any other copy); say whether a summary can reach the session by any other path in ordinary work.
   Note that `ignore_patterns` matches by name at every level of the copy; say whether that matters here.
2. **The unit case:** it plants all three files, runs `gov skilleval` with the stub, and checks the session call's
   file list holds `SKILL.md` and none of the three. Say whether it would fail on the harness at `3ef7c62c4` (the
   engineer reports it did: `assert 'scenario-summaries.md' not in ['SKILL.md', 'reference.md',
   'scenario-summaries.md']`); you may confirm this in a clone (check 5).
3. **Nothing else:** `git diff 3ef7c62c4 ac18ac2ab7c8 --stat` lists only those two files; the harness diff is the
   constant and the one `ignore_patterns` argument; the test diff adds the one case and changes no other line.
4. **The merge:** `git diff c82335a401df 3ef7c62c4 --stat` lists only this ticket's own paths (those from runs 1 to 4,
   under `docs/probes/DAEO-drhj/`, `src/gov/skilleval/`, `tests/unit/skilleval/`, `tests/acceptance/W2-104/`,
   `governance/project/skill-imports.yaml`, `src/gov/check/commands.py`, `docs/checkpoints/DAEO-drhj/` and the W1-07 and
   W1-32 `skilleval` lines run 4 added), and `git grep -n -E '^(<<<<<<<|>>>>>>>) ' ac18ac2ab7c8` finds no marker.
5. **Tests (optional; the lead runs them):** if you run any, use a `--no-hardlinks` clone of the tree at
   `ac18ac2ab7c8` in your own TMPDIR, through
   `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
   `PYTHONUSERBASE=/home/usain/.local`, the clone's own `src/` on `PYTHONPATH`, `-p no:cacheprovider -o
   tmp_path_retention_policy=failed`, and `-m "not local_only" -k "not real and not green_here and not time_limit"`;
   run pytest in the background with a long timeout (the slot may queue); remove the clone at the end (`chmod -R u+w`
   first).
6. **Trailers:** `ac18ac2ab` carries `Task: DAEO-drhj`, `Role: engineer`, `Implements: DEC-959, DEC-820` in one final
   paragraph; `3ef7c62c4` the same with `Role: orchestrator`.

Out of scope: the harness's other behaviour (reviewed in runs 1 and 2), runs 3 and 4 (checked at `39ceaec2a` and
`97b06de4eba1`), and what integrate brought.

KPI id for the verdict block: `w2-104-run5-narrow`.

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

Every finding also carries `scope: in` only if it concerns run 5's change (`ac18ac2ab`) or check 4 of the merge.

## Write and return
- You write nothing in any tree (your own TMPDIR only). Single simple Bash commands. No shell variable or `$(…)` as a
  write target, no here-document, no `bash -c`. Every wait by pid only.
- Reads (DEC-820): open, except secrets and keys (never read or printed), the held-out qualification material's
  contents, and the hidden half of any evaluation set: never open anything under `~/gov-os-eval/`, an evaluation set's
  root, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. You search with the Read and Grep tools, naming
  the folder a search starts at; search once more in other words if the first does not answer, then say "not found".
- Refused twice for the same call: stop and say so; never work around a refusal by another tool or form.
- Commit hashes as 12 digits, never the full 40. There is no token cap.
- **Your record is your session's final message**, in full: the twelve labelled fields first (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action), your session id and the probed commit in `evidence`; your answers to checks 1 to 6; every
  finding with its two lines and scope; then `REVIEW_MD_BEGIN`, the review record in markdown, `REVIEW_MD_END`; at the
  end the fenced `verdict` block
  `{"kpis": [{"kpi": "w2-104-run5-narrow", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
