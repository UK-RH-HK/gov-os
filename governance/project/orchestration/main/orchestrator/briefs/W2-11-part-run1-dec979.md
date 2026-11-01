You are the ticket lead for ticket `DAEO-k7hz` (`W2-11`, "briefs and the orchestration skill"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-11` on branch `w2/W2-11`.

**This is round 1 (r1) of two declared rounds (DEC-916; ROLES-SPEC-1 §6.3).** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-k7hz.md`, every KPI line) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-11"), with the DEC-808, DEC-791 (ii) and DEC-866 lines in it;
- `governance/project/orchestration/packages/ROLES-SPEC-1.md` §6.3 (W2-11's two rounds), §6.5 (W2-11's paragraph) and the gap table rows G13, G14 and G15; approved by the owner with DEC-957's answers;
- `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §2 (the skill template, §2.6 test design) and §5.3 items 3 to 5; DEC-959 items 1, 3, 5, 6 and 7;
- DEC-866 and `governance/project/orchestration/packages/SWEEP-2026-10-20.md` (what this ticket must stop teaching), DEC-820, DEC-861, DEC-862, DEC-847, DEC-430, DEC-808, DEC-951 item 5, DEC-943 item 1, DEC-954 (Q7: its CIT-P is one of the combined K3 CIT-P), DEC-957, DEC-979;
- `governance/project/briefs/JUDGEMENT.md`, `governance/project/briefs/LEAD-w2-common.md` (the common brief the kernel's lead template must catch up with, role-independent rules only) and `governance/project/orchestration/brief-gaps.md` (its "Fixed by" column).

## Why you start now

- **The owner's order (DEC-979 item 5 b):** the roles run in parallel with memory's chain: W2-11, W2-33, W2-60a and W2-60b, W2-83; then ACT 2 and the three layers.
- **Who waits on you:** W2-60a is held for your r1 (ROLES-SPEC-1 G13: no generated skill copy carries a version, and W2-60a's reader refuses a launch whose skill has none); W2-33 r2 follows your r1's skill versions; W2-98, W2-99 and W2-103 (new skills) start after your r1 and the skill harness W2-104.

## r1 = the ticket's KPIs, with ROLES-SPEC-1's re-scope

- **In r1:** every KPI line of the ticket file except the three-layer split; plus
  - **G14:** `brief-lead.md` brought to the common brief's role-independent rules after ACT 1, with a `brief_gaps:` section in its return;
  - **G15:** JUDGEMENT's rules (the two questions word for word, the two lines per finding, "no" is a row never a round) in `brief-reviewer.md` and the audit skill;
  - **G13:** a version in every generated skill copy (DEC-832 item 2), in full (DEC-981): the version line of every skill's `SKILL.md`, the kernel's source and its copies under `.claude/skills/`, `.rulesync/skills/` and `template/.rulesync/skills/`, are in your paths for that line only; **not the adopt skill's** (W2-52 holds its files: list it for after W2-52's merge). Nothing else in those files changes.
  - **The new kernel files:** the skill template `template/governance/kernel/templates/skill.md` (DEC-959 item 5: the sections, under about 150 lines, three test scenarios written before the text); the `qa-review` skill and its copies; orchestration's three reference files (integration-queue, nightly-sheriff, incident-response); the test-design skill's work order in parallel, red against the ticket's base, the black-box techniques, the proportion rule (W2-60a's 2,980 test lines for 713 code lines named) and the README map form `gov accept` reads (DEC-959 items 6 and 7).
- **Not in r1 (r2, a later run):** `orchestration` split into `orchestration`, `stream-orchestration` and `ticket-loop`; `brief-senior-engineer.md`; the checkpoint skill's stream checkpoint and morning handover (G7 to G9).
- **Not yours:** `template/governance/kernel/roles/orchestrator.md` and its copies are still in your paths, but ROLES-SPEC-1 gives the role files to W2-33: change in them only the sentences DEC-866's sweep names (no LEAD_CHECKPOINT, no context-limit line, no listing refusal, no fixed ceiling), nothing else.
- **Generated copies only through the adapter** (`.claude/`, `.rulesync/`, `template/.rulesync/`): edit the kernel source, regenerate, and show the copies match.
- **The route (CAP-33):** a kernel skill change. Write `docs/changes/W2-11-CIT-P.md` (the evidence, the change, its tests); an independent reviewer judges it (below); the owner's approval comes through the combined K3 CIT-P (DEC-954 Q7), which the CTO brings. Return with the CIT-P ready; the merge waits for the owner's approval.

## This run's order (the common brief's work order, DEC-963)

1. **In parallel:** a fresh independent test designer (sandboxed, `--effort high`, in the `W2-11-tests` worktree, retrieving only from the integration branch's store) writes `tests/acceptance/W2-11/` from the KPIs, in proportion, and revises the W1-35 cases that require the old sentences (each with `Rewrite-Reason: <the new decision>`, nothing else lowered; the card names them); a fresh product-spec worker (sandboxed, `--effort high`) writes the templates, skills and reference files from the spec and the KPIs, never reading the tests. Split the product-spec work into batches of about 90 minutes (for example: the templates and the sweep; the skill template and qa-review; test-design and orchestration's reference files; the copies and versions).
2. You merge the tests branch here (`-F` message file) and check the cases red on `@@HEAD@@` for their stated reasons; then the product-spec worker, or a fresh one, runs them once, reading results only.
3. **The CIT-P's independent review** (a fresh reviewer, brief A3 and `JUDGEMENT.md`, effort high): does any template, skill or role file still teach a superseded rule; does the skill template meet DEC-959 item 5; do the kernel files carry nothing scoped to this repository (those go to the project prompt). Its record under `docs/probes/DAEO-k7hz/`.
4. Verification: the scoped set `select_tests.py` gives, once, in the close's form (DEC-968); the skill validator and `gov check` on this worktree's code.
5. Return DONE (r1 built, the CIT-P ready for the owner) or PACKAGES.

## Running beside you

- **No running ticket holds your paths.** W2-52 (paused) holds `template/governance/kernel/skills/adopt/**` and `.claude/skills/adopt/SKILL.md`: not yours. W2-33 (open) will hold the role files and roster; W2-60a (held) holds the launcher's role reader. Keep clear of the critical chain's files (DEC-979 item 5): `src/gov/retrieval/**` and `governance/project/path-map.yaml`. You change no `src/` file.

## Known

- The leads' load wait still holds until the heavy-job limit runs (DEC-979); a step held more than 90 minutes: checkpoint and return PACKAGES.

**Estimate:** r1 about 600 to 900 lines of templates, skills and copies and about 200 of tests; about 8 to 10 hours (the tests and the product-spec batches in parallel about 5, the red check and the run about 1, the CIT-P's review about 1.5, the scoped run about 1).

If your session nears its end first, write your checkpoint and return PACKAGES naming what is left.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).
