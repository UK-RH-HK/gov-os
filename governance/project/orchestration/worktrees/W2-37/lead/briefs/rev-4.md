You are a fresh, read-only independent reviewer (role independent-auditor) for ticket DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. Two jobs in one session, at one head: (1) the **independent review of a CIT-P** on kernel skill bytes (the change skill's impact section), which goes to the owner for approval; (2) a **narrow independent check** of what this resume changed (F1 (a) in the code, and that section). The ticket's final probe already passed at `65e8c076` (DEC-1010: no round after it); this is not a round, it checks only the resume's change. You write nothing in any repository: you probe, and you return your findings and verdict blocks in your last message; the lead commits nothing of yours and writes the records.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-6n5k`); `git -C /home/usain/gov-os-worktrees/W2-37 rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37`, `w2/W2-37`); `git -C /home/usain/gov-os-worktrees/W2-37 rev-parse HEAD` (expect prefix `{SKILL_HEAD}`). If anything differs, stop and say so.
- Read-only: no write, commit, checkout, reset, stash, merge or edit in the worktree. Temporary repositories for probes go under your sandbox's own TMPDIR only (never under the repository or ~/gov-os-runs). Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`; search with Read and Grep, and once more in different words if the first does not answer.
- DEC-732: every probe and test uses this worktree's code: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` per command; quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -c "import gov; print(gov.__file__)"`.
- Every pytest through the heavy slot: `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (TMPDIR your sandbox's own). A slot wait or a resource gate refusal is a wait. Cases that build a code index skip or error inside the sandbox: the lead ran them outside (below); do not work around it.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## The threat model (DEC-801, ADR-0001) and the bar (DEC-1010)
Judge against honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. A finding blocks only if it is **in scope** (the ticket's KPI lines below, and for the CIT-P: the section's bytes as the owner will approve them), **reachable in ordinary work**, and **fails open or loses work**. Everything else is a row. Classify every finding on those three axes.

## The ticket's scope now
- KPI S1: "What's the impact of X?" in plain language runs `gov impact` [CAP-33.g, DEC-167]. Verify: a planted question "what is the impact of DEC-NNN?" given to the plain-language entry runs gov impact on DEC-NNN and prints its result.
- KPI S2: it also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result; **G-24's "no record names the item" counts the store's stated links too (a ticket's sources and closes, the register's Under and Changes lines): a planted decision named only by a ticket's sources is not deletable** [F1 (a), DEC-1163 (7)].
- DEC-816 and DEC-1163 (7): the change skill's `## Impact assessment` section, in `template/governance/kernel/skills/change/SKILL.md` and its byte copy `template/.rulesync/skills/change/SKILL.md`, routes the question to `gov impact`. The root `.rulesync/skills/change/SKILL.md` and `.claude/skills/change/SKILL.md` are the CTO's copies ACT after the owner's approval: they are not changed here (the `[claude-copy]` routing case stays red until then: known).

## What changed in this resume
- `0c266d752`: merge of w2/integrate (carries the widened ticket df9d442e8).
- `000fd9a52` (engineer): F1 (a): `_Records` adds the store's `stated_links` (via `gov.retrieval.graph_route.stated_links`) to `named_by`; a store with no stated-links table reads the record graph `stale`. Reading R8's comment updated.
- `202fbf723`, merged at `96498443f` (test designer): `tests/acceptance/W2-37/test_w2_37_stated_links.py` (5 cases).
- `{SKILL_COMMIT}` (engineer, skill section): the two template skill files.
- Diffs: `git -C /home/usain/gov-os-worktrees/W2-37 diff 65e8c076 HEAD -- src/gov/impact tests/acceptance/W2-37 tests/unit/impact template/governance/kernel/skills/change/SKILL.md template/.rulesync/skills/change/SKILL.md`.
- The CIT-P to review: `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/changes/W2-37-CIT-P.md` (in scratch: `docs/changes/` is outside the ticket's paths).

## The lead's verification (outside the sandbox)
{LEAD_VERIFY}

## What to check
1. **CIT-P review.** The record's lines are verbatim what the commit changed (`git show {SKILL_COMMIT}`); the sha256 before and after it states for both files are right (`git show 96498443f:<path> | sha256sum`, `sha256sum <path>`); the two files are byte-equal; nothing outside the impact section (and any version line the record names) changed; every id the section cites exists and is ACCEPTED in `docs/DECISION_REGISTER.md` or `docs/contract/` (grep by id); what the section says `gov impact` does matches the command (`src/gov/impact/command.py`, run `gov impact --help` and one planted question); the impact and options it lists (DEC-105) are honest, including the `gov check` skill finding it names (P-7). Judgement: sound or not, with findings.
2. **Narrow check of F1 (a).** On a temporary repository: a decision named only by a ticket's `sources:` (and by `closes:`, a register `**Under:**` line, a `**Changes:**` line) is not deletable and the radius is not R0; a decision no edge and no stated link names stays deletable on a current graph; what the item itself names does not count; an older store without the stated-links table never makes an item deletable. That nothing green before changed (refusals, no writes, baseline radii), and every commit since `65e8c076` stays in the ticket's allowed paths with `Task: DAEO-6n5k` and its role's trailer (the merges excepted).

## Return (your last message)
The twelve fields as labelled lines ("none" where nothing): task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then "## CIT-P review" (each check sound or not, findings with setup, fault, scope, ordinary work, consequence) and its judgement (pass or fail) with this fenced block:

```verdict
{"kpis": [{"kpi": "w2-37-cit-p", "verdict": "pass|fail", "findings": [{"id": "C1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}], "reviewer": "independent-auditor, fresh read-only session; not the author"}
```

Then "## Narrow check" (findings as above), your judgement (pass or fail) and **this fenced block, last**, in exactly this form (one entry per KPI line S1, S2; findings may be empty lists):

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, {"kpi": "S2", "verdict": "pass|fail", "findings": [{"id": "N1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
