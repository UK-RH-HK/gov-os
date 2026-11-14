# W2-104 (DAEO-drhj), independent auditor: run 4's narrow check (the integrate merge and `skilleval` beside `impact` only)

**Role:** independent-auditor, a fresh read-only session. Write nothing in any tree; your verdict goes in your return.
**Worktree:** `/home/usain/gov-os-worktrees/W2-104`, branch `w2/W2-104`. **Probe:** head `97b06de4eba1`.
**Ticket:** `DAEO-drhj` (W2-104), profile STANDARD, class C2: `gov skilleval`, the skill evaluation harness. Its text
is `/home/usain/gov-os-worktrees/W2-104/.tickets/DAEO-drhj.md`; its sources DEC-959 and DEC-820 (read each by id in
`/home/usain/gov-os-worktrees/W2-104/docs/DECISION_REGISTER.md`, grep only by id). DEC-1020 (a) decided that `skilleval`
is recorded in `RECORDED_GOV_COMMANDS`; DEC-747 is the rule that a new `gov` command is recorded there. DEC-1173 (1)
sets the merge form checked below (read it by id).

## Why this check
Run 3 ended at `39ceaec2a` (narrow check PASS). Since then W2-37 merged into `w2/integrate` (`72c6def8871a`), adding
`impact` on the same lines where this ticket adds `skilleval`. Run 4 did, and only this is under review:

1. `0e469cc37` (lead): merge of `w2/integrate` at `72c6def8871a`. **The merge form (DEC-1173 (1)):** every conflicted
   file (`src/gov/check/commands.py`, `tests/acceptance/W1-07/README.md`, `test_w1_07_recorded_commands.py`,
   `w1_07_support.py`, `tests/acceptance/W1-32/test_w1_32_command_set.py`) takes integrate's side exactly, no conflict
   markers, no edits of the lead's own; a merge whose result differs from both parents in a test file breaks W1-01's
   rule.
2. `4999dd9ec` (engineer): `skilleval` back in `commands.py`, beside `impact`, as run 3 had it (DEC-1020).
3. `5ded8afe7` (test designer): `skilleval` back in W1-07's lists and README and W1-32's command-set assertion.
4. `97b06de4e` (lead): merge of the tests branch (tip `5ded8afe7`).

## Check
1. **The merge form:** at `0e469cc37`, `git diff 72c6def8871a 0e469cc37 -- <each of the five files>` is empty;
   `git diff 72c6def8871a 0e469cc37 --stat` lists only this ticket's own paths (`docs/probes/DAEO-drhj/`,
   `src/gov/skilleval/`, `tests/unit/skilleval/`, `tests/acceptance/W2-104/`, `governance/project/skill-imports.yaml`)
   and `docs/checkpoints/DAEO-drhj/`, and nothing else; `git grep -n -E '^(<<<<<<<|>>>>>>>) ' 97b06de4eba1` finds no marker. W1-01's own rule on both
   run 4 merges: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 /home/usain/gov-os-worktrees/W2-104/.gov-runtime/scratch/lead/offences4.py 0e469cc37 97b06de4e`
   (a read-only script calling `tests/acceptance/W1-01/w1_01_support.py`'s `merge_offences`; read it first) prints
   `[]` for each. Run 3's WIP merge `349341ab8` is known red there and waits on the owner's exemption (DEC-1173 (1));
   it is out of scope.
2. **commands.py:** `git diff 72c6def8871a 97b06de4eba1 -- src/gov/check/commands.py` adds exactly one line recording
   `skilleval`, after the `impact` line, the same text as at `39ceaec2a`; integrate's entries are kept unchanged. The
   module imports, and `python3 -m gov.check.commands` (this tree's `src/`, run in the tree) exits 0.
3. **W1-07 and W1-32:** `git diff 72c6def8871a 97b06de4eba1 -- tests/acceptance/W1-07 tests/acceptance/W1-32` adds only
   `skilleval`: integrate's lists, comments, `RECORDED_HERE` subtraction and the cases' points intact; no assertion
   removed or weakened; the pinned sets are integrate's plus `skilleval` (W1-07: eleven with `lock`; W1-32: ten `gov`
   commands); the README's new paragraph and counts say the same, and no other README line changed beyond naming
   `skilleval`. Compare with `39ceaec2a`'s text that `skilleval` is added as run 3 had it.
4. **Nothing else:** `git diff 39ceaec2a 97b06de4eba1 --stat` differs from `git diff 39ceaec2a 72c6def8871a --stat`
   only by these five files (integrate's changes plus the `skilleval` lines).
5. **Trailers:** each of the four commits carries `Task: DAEO-drhj`, a `Role:` matching its author (orchestrator for
   the two merges), and `Implements:` naming only DEC-959 and DEC-820; `5ded8afe7` carries
   `Rewrite-Reason: DEC-1020 skilleval, after W2-37's impact (run 4)`.
6. **Tests (optional; the lead runs them):** if you run any, use a `--no-hardlinks` clone of the tree at `97b06de4eba1`
   in your own TMPDIR, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
   with `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, and
   `-m "not local_only" -k "not real and not green_here and not time_limit"`; remove the clone at the end (`chmod -R u+w`
   first).

Out of scope: the harness's own behaviour (reviewed in runs 1 and 2), run 3's work (checked at `39ceaec2a`), and
anything integrate brought.

KPI id for the verdict block: `w2-104-run4-narrow`.

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

Every finding also carries `scope: in` only if it concerns run 4's merge or the `skilleval` lines.

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
  recommended_next_action), your session id and the probed commit in `evidence`; your answers to checks 1 to 5 (and 6
  if run); every finding with its two lines and scope; then `REVIEW_MD_BEGIN`, the review record in markdown,
  `REVIEW_MD_END`; at the end the fenced `verdict` block
  `{"kpis": [{"kpi": "w2-104-run4-narrow", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 20 minutes.
