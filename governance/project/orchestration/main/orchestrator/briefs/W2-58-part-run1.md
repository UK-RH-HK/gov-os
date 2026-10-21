You are the ticket lead for ticket `DAEO-5j8b` (`W2-58`, "Policy 2 in the guard and the launcher: reads open, four refusals"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-58` on branch `w2/W2-58`, cut from the integration branch `w2/integrate` at `9afe3d00`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 1.** `git log --oneline -1` must show `9afe3d00`, and `git status --short` must show nothing (anything else: stop and return PACKAGES naming it). Your ticket file `.tickets/DAEO-5j8b.md` holds the KPIs; read it first. Every decision this brief cites is in your worktree's register (up to DEC-864).

## Why you start now, ahead of everything (DEC-857)

The guard still refuses reads that the owner's Policy 2 (DEC-820) opened, and that now slows every agent, the orchestrator included: on 2026-10-19 and 20 the sessions met dozens of such refusals (an `ls governance/project/`, a `Glob` of `governance/project/*`, a `grep` whose pattern names `governance/project`, a `git grep` with a `governance/project/*.yaml` pathspec, a listing of `governance/`). The cause is in the code, not a setting (DEC-857 item 2): `src/gov/guard/heldout.py:19-21` names two protected files, `governance/project/held-out.yaml` (the held-out list) and `.claude/settings.json`, and `src/gov/guard/protected.py` refuses any target that takes either in: the file itself, any folder above it inside the project, or a glob that matches it. The owner approved the change in DEC-821 (CAP-33).

## The decisions for this run (all in your register)

- **DEC-820:** reads open; refused only (a) secrets and keys, (b) the held-out material's contents (its file names may be seen), (c) the counterpart's work on the same ticket, (d) the hidden half of an evaluation set.
- **DEC-821:** the four items of W2-58's change, approved; its failure KPIs.
- **DEC-857 item 3:** the KPIs name both protected files: the held-out list file's names readable, the held-out material's contents refused; the settings file's reads under Policy 2 (a secret anywhere stays refused); searches from the repository root or `governance/project/` no longer refused for the files' sake.
- **DEC-864 item 5:** your paths are the three files that hold the read rules (`protected.py`, `heldout.py`, `decide.py`), a new `reads.py` if needed, `src/gov/launch/**` (the sandbox's read denials only), the path map's `evaluation_sets` block and its schema, and the tests. **Never `src/gov/guard/containment.py`:** W2-05's unmerged branch changes it; a need there is a package.
- **DEC-845:** the path map gains the `evaluation_sets` block; W2-61 is its first user (lens B's 20 questions, visible; a hidden half).
- **DEC-838, DEC-839:** full window; `--effort high` for the test designer and the engineer, `max` for the reviewer.

## Facts for the design

- **This worktree's sessions run the guard code you are changing:** the hook lines call `$CLAUDE_PROJECT_DIR/src` (until W2-59 lands and the owner re-pins), and a launched worker's `CLAUDE_PROJECT_DIR` is this worktree. A broken read rule therefore breaks your engineer's own session. Tell the engineer to keep `python3 -m gov.guard.hooks` loading after every edit, and to fail closed on any error (a guard error refuses, never allows).
- **What must still be refused, by every read route an honest agent takes** (DEC-801, DEC-821 item 4): a secret's content; the held-out material's contents (each path the held-out list names); for an engineer, its own ticket's `tests/acceptance/<W2 id>/**` by tool reads and by the read side of Bash, while `pytest` on that folder still runs and shows names, results and failure messages; for a test designer, the files its ticket's branch changes against its base, other than its own tests; for a measured session, an evaluation set's hidden part.
- **What becomes readable:** the held-out list file itself (its paths are names, not contents), the settings file (no secret is in it; a secret anywhere stays refused by (a)), and every search or listing from the repository root, `governance/`, `governance/project/` or `.claude/`.
- **The evaluation set:** declare the block's shape in the path-map schema (a set's name, its visible paths, its hidden paths, the roles or tickets it measures) and one set for W2-61 with lens B's visible half (`docs/assessment/2026-10/B-memory-retrieval.md`) and a hidden part path that W2-61 will fill. The orchestrator reviews and keeps the block (DEC-861).
- **A full rebuild in this worktree** is the first under the new path map (DEC-856): the orchestrator measures what it uses. Run it in the background with an exit-code file and record its wall time in your return.

## This run's order

1. **Tests first:** a fresh independent test designer, launched sandboxed (`--effort high`), on the five success KPIs and the failure KPI, STANDARD proportion. Its brief carries the "Facts for the design" as behaviour. Every refusal case is asserted by its route (Read, Grep, Glob, Bash `cat`, `grep -r`, `find`, `ls`, `git grep`, `git show <rev>:<path>`).
2. Check red yourself.
3. **Implement:** a fresh engineer, launched sandboxed (`--effort high`), inside the allowed paths only.
4. **Verify** as the loop says (every suite in its own process, `tests/unit`, `gov check` after a rebuild). Known reds you did not cause: W1-42's two accepted reds; W1-49's two retired-window tests (package P-W2-52 with the owner).
5. **Independent review (CAP-33, a guard change):** although the profile is STANDARD, after green run one fresh read-only reviewer (brief A3 with `JUDGEMENT.md`, `--effort max`) on the final code and `docs/changes/W2-58-CIT-E.md`. Commit its probe record under `docs/probes/DAEO-5j8b/` only if it passes.
6. Return.

---

