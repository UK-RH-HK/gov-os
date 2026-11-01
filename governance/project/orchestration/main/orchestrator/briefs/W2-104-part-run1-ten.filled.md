You are the ticket lead for ticket `DAEO-drhj` (`W2-104`, "The skill evaluation harness: each skill's three scenarios run on a fresh session and recorded, and every imported skill's licence check recorded before adoption"). It is profile STANDARD; W2-98 to W2-103 (the domain skills) wait for it (DEC-959 items 4 and 5), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-104` on branch `w2/W2-104`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-959, DEC-820); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-104/`) are set; no open dependency. W2-11 (landing today) brings the skill template (`template/governance/kernel/templates/skill.md`) and three scenarios per skill: read them on `w2/integrate` once landed; until then, from `w2/W2-11` (read only).

## The decisions for this run
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort high) in `/home/usain/gov-os-worktrees/W2-104-tests`, retrieving only from the integration branch's store, writes `tests/acceptance/W2-104/` from the spec and KPIs: planted skills with passing and failing scenarios, a stub model, a temporary project; never a real model call, never a key. In parallel a fresh engineer (sandboxed, effort high) builds `src/gov/skilleval/**` (`gov skilleval <skill>`, a command module by the command-module convention) to the spec, never to the tests; it runs the acceptance tests once merged, through `gov accept DAEO-drhj`, results only.
- **Fail closed:** a scenario that cannot reach a model is recorded as not run with its cause, never a pass; an import without a licence record or with a failing scenario is never marked adopted; no secret read or printed (DEC-820 (a)).
- **A new `gov` command:** record it in both lists (the tests' list, W1-07, and `RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`, DEC-747). The second is outside your paths: name it in your return for the CTO (a small path addition, or W2-120's engineer).
- **Scope:** `src/gov/skilleval/**`, `tests/unit/skilleval/test_w2_104*`, `governance/project/skill-imports.yaml`. Nothing else.
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh`. Never the full suite.
- **One role (DEC-995, DEC-996):** the harness is code; a skill or scenario text that needs changing is product-spec's, named in your return. **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified. **No review (STANDARD).**

**Estimate:** about 250 lines of code and 200 of tests; about 5 hours. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-104`.

---
