Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-101 (DAEO-6icv), independent auditor: the narrow independent check, round 2 (the last, DEC-1010)

**Role:** independent-auditor, a fresh read-only session. Write nothing in any tree; your verdict goes in your return.
**Worktree:** `/home/usain/gov-os-worktrees/W2-101`, branch `w2/W2-101`. **Probe:** head `1ef54a70037a`.
**Ticket:** `DAEO-6icv` (W2-101), profile STANDARD, class C2: domain skills B, the engineer's skills for frontend, UI/UX
and DevOps. Its text, KPI lines (S1 to S6, F1 to F5) and its `## Interface` (condensed by the CTO on 2026-11-14) are in
`/home/usain/gov-os-worktrees/W2-101/.tickets/DAEO-6icv.md`; its sources DEC-959, DEC-957, DEC-616, DEC-645, CAP-24.b,
DEC-315, DEC-1112 (read each by id in `/home/usain/gov-os-worktrees/W2-101/docs/DECISION_REGISTER.md`, grep only by
id). The skill template: `template/governance/kernel/templates/skill.md`.

## Round 1 and what this round checks

Round 1 (reviewer session `c324d1ca-8a75-43d0-9ca1-7c006195c7dc`, head `0b0d4cb3053d`) failed on one finding; its
record, with every finding and the lead's L1, is `docs/probes/DAEO-6icv/PR-DAEO-6icv.md` (read it first). This round is
**narrow**: F1 to F6 and L1 only, as fixed or as rows, and anything the fixes themselves broke. It is the last round:
anything still blocking goes to the owner with options.

What changed since round 1 (base `0b0d4cb3053d` → head `1ef54a70037a`):
- `4094fe296`: the lead's round-1 probe record (not under review).
- `57ea2d40bb9f`: the lead's `--no-ff` merge of `w2/integrate`, bringing W2-104's harness fix (`c9f07ef3782b`, the CTO's
  reopen under DEC-1164 (18)): `src/gov/skilleval/harness.py` now leaves `scenario-summaries.md` out of the session's
  copy, next to `scenarios.md` and `scenario-records.yaml` (F1's fix, option (a)), and the condensed ticket Interface.
  The harness is W2-104's code: in scope here only as to whether it closes F1 for these three skills.
- `3cd17b73e3ee` (product-spec, session `c5303202-dc77-4b73-9906-d2016fa5025d`): L1's fix. Each skill's `output:`
  became `"<allowed_path>/** (one entry of the ticket's allowed_paths)"`; versions raised (frontend 1.2.0, ui-ux 1.1.0,
  devops 1.1.0); copies refreshed.
- The lead's run 3 of `gov skilleval` on all three skills (model `claude-opus-5-5`, effort high), 03:44 to 03:55 UTC:
  9 of 9 pass. As before, a pass-through `claude` wrapper
  (`/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/capture/bin/claude`) captured each process's prompt,
  working folder and stdout into `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/capture/replies.jsonl`,
  lines 31 to 48 (session line, then judgement line, per scenario); the extract the summaries were written from is
  `.gov-runtime/scratch/lead/briefs/ps-5-r3-replies.md`.
- `1ef54a70037a` (product-spec, session `42a47518-8137-41b1-a73b-3036d20868ab`): run 3's records as the harness wrote
  them, nine new hand-written summary entries, each file's opening updated, and the copies.

**The lead's results at `1ef54a70037a`:** `gov accept W2-101`: 271 passed, 6 failed (success-6 and failure-5, the same six cases counted under both). `lead_verify` (6328 tests, `.gov-runtime/scratch/lead/log/verify/parallel.xml`): 9 failed, all `.claude/skills/` copies absent: `test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source[*]` (3), `::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[*]` (3, GENERATED_DIFFERS), and W2-11's `test_the_skill_carries_one_version_in_all_four_places[*]` (3). `.claude/skills/<skill>/` is placed only by the copies ACT after the owner's yes (DEC-315, DEC-1112 (3); out of the ticket's paths). W2-11's output-class cases (L1) pass. Judge for yourself whether any of these is caused by this change.

## Check (each answer with the command and what it showed)

1. **F1:** read the harness's ignore (`src/gov/skilleval/harness.py`, near `SUMMARIES`) and its unit test. Confirm a
   run's session workspace receives no `scenario-summaries.md` (nor `scenarios.md`, `scenario-records.yaml`): for
   example, run the harness's copy step on one skill folder into your own TMPDIR without a model call, or read the code
   path end to end. Confirm run 3's captured session prompts and outputs (lines 31, 33, ... 47) show no sight of the
   summaries or the expected answers. Is anything else in the skill folder that carries the expected answers still
   copied?
2. **L1:** each skill's `output:` against W2-11's reading (`tests/acceptance/W2-11/w2_11_support.py`: `output_classes`,
   `declares_none`, `write_targets`, `stray_writes`) and the template's meaning of `output`. Is
   `<allowed_path>/**` an honest path class for a method whose writes land in each ticket's own paths, or does it
   mislead (fail open: lets a step write outside the ticket's paths; or imply a permission, CAP-24.b)? Note the
   worker's own lesson: `<…>` matches one segment, so a root-level target (a `Dockerfile`) would be flagged; judge
   whether that matters in ordinary work. Run `tests/acceptance/W2-11/` (see 7) and report its reds.
3. **The re-run and its records:** each `scenario-records.yaml`'s last three entries pass at the current
   `skill_version`; each `scenario-summaries.md` has one entry per record entry, with the exact `run_at`; spot-check at
   least one run-3 entry per skill against `replies.jsonl` for faithfulness; the revised opening lines are true. The
   version raise needed the re-run: is the gate's record now current for each skill?
4. **F2 to F6:** say for each whether the round-1 classification still holds at this head, or whether anything since
   changed it (F6 against the condensed Interface).
5. **Copies, scope, trailers:** `diff -r` of each kernel folder against `.rulesync/skills/<skill>/` and
   `template/.rulesync/skills/<skill>/` is empty; nothing of the ticket under `.claude/`; `git diff --stat
   0b0d4cb3053d 1ef54a70037a` less the merge's own changes touches only the ticket's paths and `docs/probes/DAEO-6icv/`;
   each new commit carries `Task: DAEO-6icv`, a `Role:` matching its author, `Implements:` ids only from the ticket's
   `sources:`, all in one final paragraph.
6. **Anything the fixes broke:** the skills' own checks (`python3 <skill>/check_domain_skill.py <skill>/SKILL.md` →
   `PASS`) and the validator
   (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.check.skill_validator template/governance/kernel/skills/frontend template/governance/kernel/skills/ui-ux template/governance/kernel/skills/devops`).
7. **Tests (optional; the lead ran them):** if you run any, use a `--no-hardlinks` clone of the tree at `1ef54a70037a` in
   your own TMPDIR, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
   with `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`; remove the
   clone at the end (`chmod -R u+w` first). No real model call (`gov skilleval` without a stub costs money; do not
   run it).

Out of scope: shipped code the ticket does not change beyond F1's question, and the `.claude/skills/` copies (the
copies ACT's, after the owner's yes; DEC-315, DEC-1112 (3)).

KPI id for the verdict block: `w2-101-narrow-r2`.

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

Every finding carries `scope: in` only if it concerns this ticket's change (the three skill folders, their copies, the
check script, scenarios, records and summaries) or the suite's fidelity to the KPI lines.

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
  recommended_next_action), your session id and the probed commit in `evidence`; your answers to checks 1 to 6 (and 7
  if run); every finding with its two lines and scope; then `REVIEW_MD_BEGIN`, the review record in markdown,
  `REVIEW_MD_END`; at the end the fenced `verdict` block
  `{"kpis": [{"kpi": "w2-101-narrow-r2", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 30 minutes.
