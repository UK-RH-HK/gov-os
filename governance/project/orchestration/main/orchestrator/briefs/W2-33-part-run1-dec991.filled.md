You are the ticket lead for ticket `DAEO-lrre` (`W2-33`, "The three layers' roles and the typed handoff: the CTO, the Senior Engineer, the ticket lead's role file, machine-readable defaults per role"). It is profile STANDARD, a role-definition ticket on the roles stream (DEC-979 item 4), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-33` on branch `w2/W2-33`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (CAP-22.b, CAP-22.c, DEC-094, DEC-954, DEC-957, DEC-959, DEC-983); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-33/`) are set; its dependency W2-01 (`DAEO-g0ip`) is closed. **It starts only after W2-11's round 1 has landed** (they share `template/governance/kernel/roles/orchestrator.md` and `.claude/agents/orchestrator.md`); your base holds W2-11's role-file changes.

**Read first:**
- the ticket file (`.tickets/DAEO-lrre.md`), its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-33") and its rows (W2-L250, W2-L251, W2-L252, W2-M084, W2-M085, W2-M321) in `docs/plan/WAVE_2_TRIAGE.md`;
- ROLES-SPEC-1 (`governance/project/orchestration/packages/ROLES-SPEC-1.md`, approved with DEC-957's answers) and ROLES-RESEARCH-1 §2.9 (the QA engineer);
- DEC-954 Q6 and Q13, DEC-957 (the work order, the escalation rubric), DEC-959 items 3 and 7, DEC-963, DEC-983, DEC-839 item 5 (effort per role);
- the kernel role files (`template/governance/kernel/roles/*.md`) as they stand after W2-11, and how W2-60a's launcher reads role defaults (`src/gov/launch/role.py` on its branch `w2/W2-60a`: read only).

## The decisions for this run
- **DEC-992 (P-W2-11-3): DEC-808's schema fields come to you,** with the typed handoff record (`template/governance/kernel/schemas/handoff*`, `templates/handoff.md`): the two judgement lines a finding carries (`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`) as typed fields.
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort high) in `/home/usain/gov-os-worktrees/W2-33-tests`, retrieving only from the integration branch's store, writes `tests/acceptance/W2-33/` from the spec and KPIs; in parallel a fresh product-spec worker (sandboxed, effort high) writes the role files and the handoff schema to ROLES-SPEC-1 and the KPIs, never to the tests; it runs the acceptance tests once merged (`gov accept`), reading results only.
- **The generated copies under `.claude/agents/**` are not your workers'** (Claude Code's safety check refuses `.claude/` writes in a headless session, as W2-11 met). Your worker writes the kernel role files and the rulesync sources in your other paths; when they are done, return the exact generator command (rulesync into an empty folder, then only the in-path files) in your return as a package for the CTO, who writes and commits the copies here with the owner's daytime approval (as DEC-992 did for W2-11). Never try another way.
- **Fail closed:** a role built other than as ROLES-SPEC-1 states it, a role file placed by hand rather than generated, a role without its machine-readable defaults (model, effort, skills).
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh`. Never the full suite. **No review (STANDARD).**
- **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified; the CTO lands it through the merge queue, which merges and closes it in one step.

**Estimate:** about 260 lines; about 5 hours. Scratch budget (DEC-898): 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-33`.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
