You are the ticket lead for ticket `DAEO-dy7j` (`W2-83a`, "A playbook per stream: the form in the kernel template, its schema in gov check, and the adopt step"). It is profile STANDARD, a template ticket on the roles stream (DEC-979 item 4), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-83a` on branch `w2/W2-83a`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-944, DEC-941, DEC-872, DEC-880, DEC-866, CAP-44.a, CAP-33.a, CAP-24.a, DEC-954, DEC-957, DEC-983); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-83a/`) are set; its dependency W2-64 (`DAEO-0uhh`) is closed. **It starts only after W2-11's round 1 and W2-52 have landed** (W2-11 versions every kernel skill's `SKILL.md`, adopt's included; W2-52 holds `template/governance/kernel/skills/adopt/**` and `.claude/skills/adopt/SKILL.md`).

**Read first:**
- the ticket file (`.tickets/DAEO-dy7j.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-83a");
- DEC-944 item 3 (playbooks per stream), DEC-239 and CAP-50.a (the shared frontmatter), DEC-872 item 2 (core-schema), CAP-44.a and CAP-24.a (adoption and the adapter's copies), CAP-33.a (CIT-P);
- `src/gov/check/schema.py` (how core-schema maps a record type to its schema), the adopt skill as it stands after W2-52 and W2-11, and the skill template W2-11 added.

## The decisions for this run
- **CIT-P first:** `docs/changes/W2-83a-CIT-P.md` before any kernel file changes, reviewed independently (a fresh independent-auditor, read-only) and **approved by the owner before the merge**: return it as a package once reviewed, and keep working on what it does not block; the CIT-E after.
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort high) in `/home/usain/gov-os-worktrees/W2-83a-tests`, retrieving only from the integration branch's store (planted playbooks and a product built from the template at a temporary path, never this repository's `docs/`); in parallel a fresh product-spec worker for the form, the schema and the adopt step, and an engineer for `schema.py`; one acceptance run through `gov accept` once merged, results only.
- **The generated copies under `.claude/skills/adopt/**` are not your workers'** (Claude Code's safety check refuses `.claude/` writes in a headless session). Your workers write the kernel skill and the rulesync sources; return the exact generator command as a package for the CTO, who writes and commits the copies here with the owner's daytime approval (as DEC-992 did for W2-11).
- **Nothing project-specific in the kernel:** no keystone, no EXAMIN, no workbench, no path of this repository.
- **Verification (DEC-968, DEC-983):** the scoped set, once, in the close's form, through `verify_lock.sh`; `gov check` green. **No code review (STANDARD)** beyond the CIT-P's.
- **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified; the CTO lands it through the merge queue, which merges and closes it in one step.

**Estimate:** about 350 lines; about 6 hours, plus the owner's CIT-P approval. Scratch budget (DEC-898): 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-83a`.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
