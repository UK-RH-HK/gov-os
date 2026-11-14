# W2-101 (DAEO-6icv), independent auditor: the narrow independent check of the three domain skills

**Role:** independent-auditor, a fresh read-only session. Write nothing in any tree; your verdict goes in your return.
**Worktree:** `/home/usain/gov-os-worktrees/W2-101`, branch `w2/W2-101`. **Probe:** head `0b0d4cb3053d`.
**Ticket:** `DAEO-6icv` (W2-101), profile STANDARD, class C2: domain skills B, the engineer's skills for frontend, UI/UX
and DevOps. Its text, KPI lines (S1 to S6, F1 to F5) and its `## Interface` (the CTO's decision at claim) are in
`/home/usain/gov-os-worktrees/W2-101/.tickets/DAEO-6icv.md`; its sources DEC-959, DEC-957, DEC-616, DEC-645, CAP-24.b,
DEC-315, DEC-1112 (read each by id in `/home/usain/gov-os-worktrees/W2-101/docs/DECISION_REGISTER.md`, grep only by
id; CAP-24.b under `docs/contract/`). Content source: ROLES-RESEARCH-1 §2.7
(`governance/project/orchestration/packages/ROLES-RESEARCH-1.md`, lines 135 to 156). The skill template:
`template/governance/kernel/templates/skill.md`. Precedent: W2-98's spec-writing skill (`docs/probes/DAEO-wi46/`).

## What is under review (base `2748a2b19622`, the interface merge)

- `b465043d5c79` (product-spec, session `9784c9b7-f14d-4f47-b37f-27211b3d19ee`): the three `scenarios.md`, first.
- `fb784e756147` (same session): the three `SKILL.md` and the byte-equal `check_domain_skill.py` (I1).
- `c0f72460ec39` (same session): byte copies into `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/`.
- `33d10146ee6d` (independent test designer, session `8ec9e7ec-6045-4491-8b61-e15767a0fcdf`) merged at `b27f27354`:
  the acceptance suite `tests/acceptance/W2-101/` (in scope only as to whether it judges the KPI lines faithfully).
- `9905c9951763` and `33484a699983` (product-spec fix, session `a116b758-80e7-4430-a8a1-fe53f84ec12c`): after frontend
  scenario 3 failed twice on the real model (the session ranked an open support-list question "not P1", following the
  skill's own Output text, and had no code to change), the scenario got a code snippet and the skill text was made
  consistent (P1), version 1.1.0.
- `0b0d4cb3053d` (product-spec, session `fad698e6-c98d-4c63-a213-b18c0321e8ce`): the harness's
  `scenario-records.yaml` as written by the lead's real `gov skilleval` runs, the hand-written `scenario-summaries.md`,
  and their copies.

**How the records and summaries were made (lead):** three real runs of `gov skilleval` (model `claude-opus-5-5`,
effort high): run 1 without capture (frontend 2/3, ui-ux 2/3, devops 3/3); a diagnostic run of frontend and ui-ux
(frontend 2/3, ui-ux 3/3); after the fix, a final run of all three (9/9 pass). The `--json` envelope carries no reply
text, so for the last two runs a pass-through wrapper named `claude`
(`/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/capture/bin/claude`, read it) sat first on `PATH`,
running the real program unchanged and appending each process's prompt and stdout to
`/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/capture/replies.jsonl` (lines 1 to 12 the diagnostic
run, 13 to 30 the final run; a session line then its judgement line per scenario). The summaries were written from the
extracts `.gov-runtime/scratch/lead/briefs/ps-3-final-replies.md` and `ps-3-diag-replies.md`.

**The lead's results:** `gov accept W2-101`: 271 passed, 6 failed; the six are
`test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source[*]` and
`::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[*]`, because `.claude/skills/<skill>/` is placed
only by the copies ACT after the owner's yes (DEC-315, DEC-1112 (3); out of the ticket's paths).

## Check (each answer with the command and what it showed)

1. **I1 against the Interface:** read `template/governance/kernel/skills/frontend/check_domain_skill.py`; `cmp` the
   three copies. Plant copies in your own TMPDIR and confirm: each of the eight sections, the five parts and the
   area's points, when absent, is named (`REFUSED <skill>: missing <name>`, exit 1); a permission line
   (`allowed-tools: Bash`, `permissions:`, `- allow: ...`, front matter included) is named with its line number; the
   real three print `PASS`. Look for an ordinary-work way it passes a skill that lacks one of them (fail open), for
   example a section or label only inside a code fence, a label with different case or spacing, Sources not last. Note
   that the script builds its permission keys from string pieces (it says why); judge whether that hides anything.
2. **The skills against S1, S2, S3:** each `SKILL.md` holds the five parts and ROLES-RESEARCH-1 §2.7's points
   (frontend: accessibility, state, browser support; ui-ux: user flows reviewed by the owner as scenarios, not code;
   devops: hermetic builds, pinned versions, rollback); the template's sections in order; front matter closed (the
   validator: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.check.skill_validator template/governance/kernel/skills/frontend template/governance/kernel/skills/ui-ux template/governance/kernel/skills/devops`, run in the tree);
   body ≤ about 150 lines; escalation mapped to P3/P2/P1/Emergency consistently with DEC-957's rubric; nothing that
   grants or implies a permission, and no step telling the engineer to write outside its ticket's paths (CAP-24.b,
   DEC-995, DEC-996). Is the method right for an honest engineer (no rule that would lead it into a wrong or unsafe
   act in ordinary work)?
3. **S4 and F3, the order:** `git log --diff-filter=A` shows each `scenarios.md` added no later than its `SKILL.md`.
   Judge the fix: frontend's `scenarios.md` was revised (`9905c9951`) after the skill text existed. Was the scenario
   weakened, or made judgeable, and does that offend S4/F3's intent?
4. **Records and summaries:** each `scenario-records.yaml` is what the harness writes (fields, the last three entries
   pass at the current `skill_version`); each `scenario-summaries.md` has one entry per record entry with the exact
   `run_at`, and its three-line summaries are faithful to the capture (spot-check at least one entry per skill against
   `replies.jsonl`; the frontend scenario-3 diagnostic failure must read as a failure). Is the capture method a fair
   reading of the Interface's "a three-line summary of the reply as `gov skilleval --json` returned it"?
5. **Copies:** `diff -r` of each kernel folder against `.rulesync/skills/<skill>/` and
   `template/.rulesync/skills/<skill>/` is empty; nothing of the ticket under `.claude/`.
6. **Scope and trailers:** `git diff --stat 2748a2b19622 0b0d4cb3053d` touches only the ticket's paths plus
   `tests/acceptance/W2-101/`; every commit carries `Task: DAEO-6icv`, a `Role:` matching its author, and
   `Implements:` with ids only from the ticket's `sources:`.
7. **Tests (optional; the lead runs them):** if you run any, use a `--no-hardlinks` clone of the tree at
   `0b0d4cb3053d` in your own TMPDIR, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
   with `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`; remove the
   clone at the end (`chmod -R u+w` first).

Out of scope: the shipped code the ticket does not change (the validator, the adapter, `gov skilleval`), and the
`.claude/skills/` copies (the copies ACT's).

KPI id for the verdict block: `w2-101-narrow`.

