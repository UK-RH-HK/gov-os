You are the ticket lead for ticket `DAEO-cv58` (`W2-60a`, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`.

**This is round 4, declared by the CTO before it starts (DEC-916), for what the owner's decisions of 2026-11-01 add; read your lead checkpoint first.** Round 3 ended DONE (review 3 passed, `e1a3e221`). `git rev-parse --short=12 HEAD` must show `@@HEAD@@` (the CTO merged `w2/integrate` in, with W2-11 landed: the kernel skills now carry `metadata.version`, and their generated copies under `.claude/skills/` hold it), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## What round 4 adds (read the ticket file as the CTO left it, `.tickets/DAEO-cv58.md`)
1. **P-W2-11-1 (DEC-992):** the reader reads a skill's version from `version`, else `metadata.version` (rulesync carries only `metadata.version` into a generated copy).
2. **DEC-995, DEC-996 (the owner's rule: a role is what it may read and write; a skill never widens it):** a role file that names its skills gets those and only those: a skill under `.claude/skills/` or `.claude/commands/` its `Skills` line does not name is not loadable in the session (the CLI's own skill rule, or a package naming the gap) and is recorded as kept out; a named skill that is missing, or whose front matter carries a key outside the skill template's list (`allowed-tools` or any other permission field), refuses the launch, naming the key. The failure line adds: a skill outside the role's list loadable, or a named skill with a permission field that still launches.

## The decisions for this round
- **The work order (DEC-959 item 7, DEC-963):** one fresh test-design batch (sandboxed, effort xhigh as for a FULL ticket) in `/home/usain/gov-os-worktrees/W2-60a-tests` for items 1 and 2 as described behaviours; in parallel one fresh engineer (sandboxed, effort high) on `src/gov/launch/role.py` and `launcher.py` to the spec; the engineer runs the acceptance tests once merged, through `gov accept DAEO-cv58`, results only.
- **W2-56 (in progress, no lead running) shares `src/gov/launch/launcher.py`:** your round 3 return said this branch merges after W2-56 merges it back (DEC-786). Keep your launcher change minimal and say in your return which lines you touched, so the CTO can settle the order with W2-56; never edit W2-56's files.
- **The six ACT 1 reds and the W1-50 flaky candidate you named** are not yours (W2-90b and the nightly); name them again only if they changed.
- **Review (FULL):** up to two reviews in this declared round (DEC-916): a fresh independent-auditor (read-only, effort max) on the final head, with `JUDGEMENT.md`; commit only a passing probe record; a fail after the second is returned as PACKAGES.
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh`. Never the full suite.
- **One role (DEC-995):** code and unit tests only; a role file or skill text that needs changing is W2-33's or W2-11's, named in your return. **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified.

**Estimate:** about 80 lines of code and 120 of tests; about 5 hours with the review. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-60a`.

---
