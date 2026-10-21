You are the ticket lead for ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`, cut from the integration branch `w1/integrate`. You run the exit run for Wave 1 and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

## Rules added since the common part was written (they override it where they differ)

- **Every `gov launch` carries the model (DEC-460).** Workers in the dev-tier clones are launched from inside the clone's directory:
  `(cd <clone path> && PYTHONPATH=<clone path>/src python3 -m gov.cli.main launch <role> <ticket id> -- --model claude-opus-5-5 -p --output-format json --permission-mode acceptEdits --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" < <brief file> > <log file> 2> <error file>)`
  The brief file, log file and error file are under `.gov-runtime/scratch/lead/` in THIS worktree (not the clone's). If `gov launch` is not yet installed in the clone's environment, use `PYTHONPATH=<clone path>/src python3 -m gov.cli.main` instead.
- **Every worker commit, the test designer's too, carries `Implements:` with the capability ids it serves (DEC-476)**, besides `Task: <ticket id>`, `Role: <role>` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **A test designer's brief states behaviour and sources only, never a name of the code to be written (DEC-462).**
- **Every worker brief says, word for word:** "Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists." and "No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree." and "Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508)."
- **The exit run is run from the kernel's orchestration skill and brief templates (DEC-537).** Read `template/governance/kernel/skills/orchestration/SKILL.md` and the brief templates under `template/governance/kernel/templates/` in this worktree. Use those templates for every worker brief.
- **A real checkpoint at each round boundary (DEC-511).** Run `PYTHONPATH=src python3 -m gov.cli.main checkpoint --ticket DAEO-gjjf --role orchestrator --trigger ticket-transition --next "<next step>" --json` in this worktree, commit the record.
- **Acceptance suites:** `env -u PYTHONPATH python3 -m pytest tests/acceptance/<suite> -q -p no:cacheprovider -rs`; unit tests: `PYTHONPATH=src python3 -m pytest tests/unit -q -p no:cacheprovider`.
- Nobody runs `gov close`, `gov rebuild` or `gov pause` against this worktree or the main tree; nobody pushes (DEC-465). The main tree may be running long test runs.
- Nobody lists `~/gov-os-workbench/` or any folder in it besides the clone directories this brief names; nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/`. Never read `.claude/settings.json` anywhere.
- **At about 300k tokens:** write `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree and return LEAD_CHECKPOINT.

## What you read

- The ticket file `.tickets/DAEO-gjjf.md` (read-only): all KPI lines.
- The sources: DEC-080, DEC-086, DEC-088, DEC-089, DEC-091, DEC-106, DEC-161, DEC-235, DEC-377, DEC-414, DEC-428, DEC-467, DEC-472, DEC-511, DEC-522, DEC-537, DEC-585, MR-1, MR-2, MR-3, MR-4, MR-6, CAP-23, CAP-28, CAP-38, CAP-40.
- `docs/plan/WAVE_1_WBS.md` section 4 (the exit criteria).
- The kernel orchestration skill and brief templates.
- The dev query set: `~/gov-os-workbench/synthetic/dev-queryset.yaml`.
- `governance/project/bootstrap.md`: the learning metrics and residuals for every closed ticket.

## State of this ticket

- No acceptance tests yet; nothing written. `allowed_paths`: `docs/plan/wave-1-exit/**`. This ticket writes the exit report there.
- **Gov check on the main tree is ALL GREEN** at `93bcb247` (first time: adapter-portability green after the owner's apply block; product-traceability-trailers green after closing DAEO-2lwj and DAEO-3ef2).
- **48 of 50 tickets closed.** Open: this one (DAEO-gjjf) and DAEO-03pw (W1-43, the exit audit). No worktree remains.
- **Doctor:** tools fail (pytest-xdist sha256, DEC-638 Wave 2 residual), path_compliance fail (moved reference, known), index_freshness stale (this ticket's claim). Claude Code is 2.1.292 with sha256 match.
- **Adoption level:** INTERMEDIATE. Adoption is complete.

## The pieces (six pieces, in order)

### Piece 1: Prerequisites verified (no worker; you verify these yourself)

Read and confirm each of these from the code and the commands, not from this brief's text:
1. `gov check --json` with `GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic` in this worktree: count the families with at least one executable check (the KPI says 17 of 17). Report each family, its check count and its status.
2. All twelve Wave 1 `gov` commands: run `PYTHONPATH=src python3 -m gov.cli.main --help` and verify none is `NOT_IMPLEMENTED`. Report the list.
3. Worktrees: `git worktree list` shows only the main tree and this one.
4. Adoption: `gov adopt --status` or the adoption level from `gov doctor --json`. It must be complete before this run starts.
5. Learning metrics: read `governance/project/bootstrap.md` for each closed ticket's section. Compile the three metrics per ticket (KPI disputes; acceptance tests rewritten after implementation began, with reasons, counting "planned: command implemented" revisions separately; governance share, once the counter can give it). This goes into the exit report.
6. Parallel-ticket evidence: from the orchestrator's checkpoint and bootstrap.md, confirm that the wave ran tickets in parallel in worktrees with ticket leads, merged into the integration branch by the main orchestrator after green, with every suite re-run after each merge. Report the evidence.

### Piece 2: Dev-tier clone setup (no worker; you set up both clones)

The dev tiers are synthetic programmes at `~/gov-os-workbench/synthetic/a-dev` and `~/gov-os-workbench/synthetic/b-dev`. For each one:

1. Clone it by exact path into a temporary directory under the session's scratchpad (not under `/tmp`):
   `git clone ~/gov-os-workbench/synthetic/<tier> <scratch dir>/<tier>-exit`
2. In the clone, apply the governance template:
   `(cd <clone> && copier copy --defaults --overwrite /home/usain/Dynamic-Agentic-Engineering-OS/template <clone>)`
   If copier stops at a conflict (e.g., `.gitignore`): add `--skip <file>` and add the needed lines by hand.
3. Run rulesync generate:
   `(cd <clone> && rulesync generate)`
4. Run `gov adopt --lite`:
   `(cd <clone> && PYTHONPATH=<clone>/src python3 -m gov.cli.main adopt --lite --json)` for stages A0, A1, A2.
5. Rebuild:
   `(cd <clone> && PYTHONPATH=<clone>/src python3 -m gov.cli.main rebuild --no-embeddings --json)`
6. Verify: `gov check --json` in the clone. Report which families are green, yellow and red, and which are not registered (expected: many will be yellow with "no registered check" since the clone has fewer declarations).

### Piece 3: Programme runs — one feature per programme (workers via gov launch)

For each programme (a-dev and b-dev), choose one feature from the programme's existing specs or README and run the full spec-first cycle. The cycle for each feature:

1. **Discovery:** a fresh product-spec worker in the clone answers the discovery questions for the chosen feature.
2. **Specification closure:** `gov readiness` passes on the feature's specification; the spec reaches FULL spines.
3. **Independent specification audit:** a fresh auditor (independent-auditor role) reviews the specification. Contested or owner-level findings become decision packages that you return.
4. **WBS with tickets:** create tickets with KPIs for the feature's implementation, including a linked gap ticket for every required open row (DEC-089).
5. **Independent acceptance tests:** a fresh test designer, in proportion to the profile, writes the tests and they fail for the stated reason.
6. **Implementation:** a fresh engineer implements the feature within the ticket's allowed_paths.
7. **Close:** `gov close <ticket id>` in the clone. **At least one ticket across both programmes must close through a clean `gov close` with no exception (DEC-511).** If it refuses, report why.
8. **CI:** `gov ci push` if lefthook is installed in the clone; otherwise the gate checks.
9. **Merge:** merge the feature's branch into the clone's main branch.

Workers must be started through `gov launch` (DEC-161) inside the clone, sandboxed with their network profiles. **MR-3 containment must hold:** no implementer write reaches `tests/acceptance/**`, and the post-command check catches any Bash form the guard misses, also after a failed command.

Report for each programme: the feature chosen, the ticket id, the workers started (role, session id), the test results, the close result, whether it was a clean close.

### Piece 4: Retrieval measurements (no worker; you run the commands)

1. **Callers/impact hit@5:** run the measurement on the dev query set's code classes, comparable to the S0b2 code-intelligence baseline (DEC-377). The command and method: read `tests/acceptance/W1-21/` and its README for the dev query set form and how the measurement is made.
2. **Mean hit@5 against the S0b2 R1 baseline of 85 (DEC-414):** re-measure the dev query set's mean hit@5 and report it.
3. **RETR-A-04 and RETR-X-02:** run each retrieval with multi-batch evidence bundles, citations by id and hash, named parent expansions (DEC-091), synthesis notes where evidence exceeds the packet ceiling (W1-23), and a stopping reason from the fixed list. The validator must pass. Retrieval must stay outside the main context (DEC-080).

Report: the hit@5 number, the bundle structure, and whether the validator passed.

### Piece 5: Governance share measurement (no worker; you run the commands)

For each programme run in piece 3, measure the governance share with `gov telemetry` (DEC-086), passing the session ids of the workers used. The KPI threshold is 15 %. Report: the share for each programme.

### Piece 6: Exit report (you write this; one file)

Write `docs/plan/wave-1-exit/EXIT-REPORT.md` in this worktree. It gives:
- The commit of the exit run.
- For each exit criterion (WBS section 4): whether it is met, the evidence.
- Per programme: the feature, the ticket, the cycle steps, the clean close result.
- The retrieval measurements (hit@5, bundles, validator).
- Governance share per programme.
- Per ticket (all 50): the three learning metrics.
- Parallel-ticket evidence.
- The list of residuals left for the exit auditor (from bootstrap.md, sections marked "for the exit auditor").
- Any outstanding owner actions (B1, B2, B3 from the exit checklist) that are not done yet — return these as PACKAGES.

Commit: `git commit -m "W1-42 exit report" --trailer "Task: DAEO-gjjf" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c"`.

## Decision packages

P2 or P3, reversible, recommendation at medium-low confidence or higher, not touching the guard, containment, the launcher, scope, installs or the held-out path: the main orchestrator decides quickly (DEC-416). Return them early and precisely. **Anything about the owner's steps (B1, B2, B3) or a gov close that refuses for a reason outside the known baseline:** return at once.

## Return

`DONE` with: the branch head; each suite's result; the exit report path; whether a clean gov close was achieved; the retrieval numbers; the governance share per programme; what is left for the owner (B1, B2, B3 if not done); any packages.
Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`.
