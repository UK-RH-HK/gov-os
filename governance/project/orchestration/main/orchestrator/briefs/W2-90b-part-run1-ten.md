You are the ticket lead for ticket `@@ID@@` (`W2-90b`, "W2-90's next round: the cases still tied to this repository's live wiring move to the kernel's wiring"), profile LITE, a test-revision ticket whose implementer is an independent test designer, working only in the worktree `/home/usain/gov-os-worktrees/W2-90b` on branch `w2/W2-90b`. **Second in today's launch order (the owner, 2026-11-01: split W2-90b so it does not wait for ACT 2).**

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve; allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-90b/`) are set; its one dependency is closed: W2-106 (`DAEO-0mtg`). The owner's split (2026-11-01) dropped its dependency on W2-105; read the ticket file as the CTO left it.

## The split, and the rule that decides each case
- **Yours (W2-90b), now:** every case that does not depend on W2-105 (the template's install block removed) or W2-110 (a product's CTO-only install rule). At least: **W1-33's four guard-and-launcher cases** and **W1-05's two `test_an_install_by_the_orchestrator_asks_the_owner` setup errors** (their fixture repositories lack the five-rule hook file since ACT 1: ".claude/settings.json does not register ... a PostToolUse hook for Bash"); **W2-54's sandboxed-worker case** (confirm its cause; if it is the same, fix it the same way); **the 14 parametrized ids ACT 1 removed without a red** (W2-59's 10 post-tool ids, W2-65's 4) and W2-59's empty-parameter skip, back on the template's post-tool lines; **the harness homes** (W1-47's installed environment, W1-46's live sessions, W1-50's freeze launcher) using the editable install's gov, so with the hook lines pinned they judge the worktree's code. Any other case that only needs its fixtures to carry the new hook file is yours too.
- **W2-90c's, later (filed by the CTO; after W2-105, W2-110 and you):** W2-90's seven named reds (W1-05's two orchestrator-asks cases, W1-46's research npm-install case, four W2-59 cases) that truly need W2-105's or W2-110's change to judge the kernel's wiring.
- **Case by case:** for each case, decide by what it needs (its fixtures, the kernel's hook file, the template's install rules, the CTO-only rule). If one you expected to fix turns out to need W2-105 or W2-110, do not force it: leave it as it is, and list it in your return with what it needs (it goes to W2-90c). If one listed for W2-90c needs only its fixtures, it is yours.
- **Nothing is lowered (DEC-906, MR-3):** no case deleted, skipped, xfailed or weakened; every revised file's commit carries `Rewrite-Reason: DEC-953 item 2`; a README under `tests/acceptance/W2-90b/` maps every case to its KPI line, and says which went to W2-90c and why.

## The decisions for this run
- **The work order:** the implementer is a fresh independent test designer (sandboxed through `gov launch independent-test-designer @@ID@@`, effort high), in this worktree (no separate tests worktree: there is no engineer). It reads the kernel's wiring and the live-wiring cases; it never reads or changes this repository's live settings to make a case pass.
- **Verification (a test revision, DEC-954's P-W2-64-1 (a)):** the corrected tests and their files' suites once, in the close's form, through `verify_lock.sh` (a heavy-job slot), plus `select_tests.py`'s scoped set once. Never the full suite (DEC-968). Quote the counts before and after: every case you fixed green, none newly red.
- **Running beside you:** W2-105 (`template/.rulesync/permissions.jsonc`; it never edits your files) and W2-81 (`tests/acceptance/W2-81/` only). W2-110's revised cases are on its own branch, not merged: do not touch them.
- **One role (DEC-995, DEC-996):** test files only. A fix that needs code or a settings change is named in your return as a split, never made.
- **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified; the CTO lands it through the merge queue.
- **No review (LITE).**

**Estimate:** about 300 lines of test changes; about 3 hours. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-90b`.

---
