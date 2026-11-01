You are the ticket lead for ticket `DAEO-i89t` (`W2-120`, "The skill validator refuses a brief without the twelve-field rule and a skill whose front matter carries a permission field"). It is profile STANDARD, W2-11's child engineer ticket (DEC-995, DEC-996, P-W2-11-9 (c)), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-120` on branch `w2/W2-120`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-995, DEC-996, DEC-992, CAP-24.b, AR-5, AR-6); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-120/`) are set; its dependency is closed: W2-11 (`DAEO-k7hz`, merged and closed today: its five brief templates, its skill template and its skills are what you check).

**Read first:** the ticket file; `src/gov/check/skill_validator.py` as it stands; W2-11's merged `template/governance/kernel/templates/brief-*.md` and `skill.md`; row W2-L097 in `docs/plan/WAVE_2_LIST.md` (the validator checks `gov` commands against the reserved list, not the installed gov).

## The decisions for this run
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort high) in `/home/usain/gov-os-worktrees/W2-120-tests`, retrieving only from the integration branch's store, writes `tests/acceptance/W2-120/` from the spec and KPIs (planted briefs and skills in a temporary project; W2-11's removed validator case is not copied: written afresh). In parallel a fresh engineer (sandboxed, effort high) builds to the spec, never to the tests; it runs the acceptance tests once merged, through `gov accept DAEO-i89t`, results only.
- **What it must name, not fix:** the six vendored openspec skills under `.claude/skills/openspec-*` carry `allowed-tools`; DEC-996 item 5 has the CTO strip it from our copies. Your validator names each vendored skill so found; if the CTO's strip has not landed when you verify, the validator's finding on them is expected and named in your return, not a red of yours.
- **Scope:** `src/gov/check/skill_validator.py` and `tests/unit/check/test_w2_120*` only.
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh`. Never the full suite. `gov check` once after a rebuild: quote the skill-regression family.
- **One role (DEC-995):** code only; a skill or brief text that fails your validator is product-spec's (W2-11's round 2), named in your return. **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified. **No review (STANDARD).**

**Estimate:** about 80 lines of code and 120 of tests; about 3 hours. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-120`.

---
