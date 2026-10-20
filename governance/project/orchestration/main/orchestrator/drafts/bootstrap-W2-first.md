
## Wave 2 list: the FIRST item and the adoption-readiness block (2026-10-15; DEC-712, DEC-714)

**FIRST, before any pilot adoption of an owner repository (DEC-712):** the pre-commit hook, run in a linked worktree, wrote two foreign commits "adopted" onto `w1/W1-42` (`4b051fde`, `dc6aa34c`; restored by DEC-710, kept by DEC-711). `src/gov/retrieval/retrieve_check.py` runs `git -C <temporary clone> add -A` and `commit` with the hook's inherited `GIT_*` variables. Parallel tickets in worktrees are the method, so every adopted project with hooks installed would be hit.
- Checks and tests that run git clear the inherited `GIT_*` variables.
- A sweep: every check, test helper and command that runs git in another folder, and which of them inherit the hook environment.
- `lefthook install` and `uninstall` re-sort `.claude/settings.json` (hook events and fields alphabetically); installing the hooks must never leave adapter-portability red.

**The adoption-readiness block, opening Wave 2; it passes before any pilot adoption (DEC-714):**
- ARGUS's cycle completed on b-dev (adopted to A2 only).
- The three reds in the a-dev clone: context reproducibility (ORION-gp01), claims and schema (ade-ke2y's fields, the `close` record type of ORION-im02).
- RETR-X-02 shows a parent expansion, or the case is ruled for a question about an id that exists nowhere.
- ARGUS's governance share measured and at most 15 %.
