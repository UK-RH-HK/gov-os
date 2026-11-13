---
id: W2-98-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-13
branch: w2/W2-98
base: 6c2c3ed93bee
head: f0259229e2b5
ticket: DAEO-wi46 (W2-98)
author: orchestrator (the ticket lead of W2-98), for three product-spec sessions
review: two rounds by fresh read-only reviewers (independent-auditor, Opus); round 1 FAIL on 384c92b8b429, fixed; round 2 FAIL on c530a0a1a236 (F1-F3); the owner's P-W2-98-R2 (a): one fix batch, then a narrow independent check, PASS on f0259229e2b5 (docs/probes/DAEO-wi46/PR-DAEO-wi46.md)
decisions_carried: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-1083, DEC-1084, DEC-315, DEC-1112, DEC-1156]
owner_approval: none yet (CAP-33; to be written here before the merge)
state_class: EVIDENCE
---

# W2-98: change-impact proposal (CIT-P) for the new kernel skill spec-writing

This change adds one kernel skill, `template/governance/kernel/skills/spec-writing/`, and its two `.rulesync` copies.
The skill is the product-spec session's method for writing a spec (ROLES-RESEARCH-1 §5.3 item 7, approved by DEC-959
item 8). It is a kernel skill change, so it goes through CIT-P (CAP-33): evidence, independent review and the owner's
approval line before the merge. No existing kernel file changes.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | product-spec has no method for a spec. A spec needs the problem, users and scenarios, goals and non-goals, KPIs as observable behaviour each with a failure line, open questions as packages, and who accepts it | DEC-959 item 8; ROLES-RESEARCH-1 §2.4 | No skill |
| T2 | The owner's test-data section: the data the tests need, imported or synthetic, and who secures it and how (licence, privacy, no secrets, a hidden half where it measures). Unsecurable data is escalated as a P1 | DEC-959 item 8 | No skill |
| T3 | One skill template for every kernel skill | DEC-959 item 5 (W2-11 r1) | Template in force |
| T4 | Imported text is adopted only with its licence checked and recorded | DEC-1084 | No record for this skill |
| T5 | The check's interface I1-I4 | DEC-1156 (5) (P-W2-98-IF-1 (a)) | Decided 2026-11-12 |

## 2. What changes

The two `.rulesync` copies are byte-equal to the kernel source files listed here.

| File | Change |
|---|---|
| `template/governance/kernel/skills/spec-writing/SKILL.md` | New. The skill in the one template. Its front matter has name, version 1.0.0 and a third-person description. Its sections: When / not when; Inputs; Steps; Done when; Output and handover; Escalation; Never; Sources, last. Steps is an 11-item checklist naming the nine parts and the check. Done when has five yes/no items, including "every KPI line testable without naming code" and "every data source with its owner and its licence or recipe". Output and handover gives the twelve fields. Escalation maps to P3, P2, P1 and Emergency, and unsecurable data is a P1. The body is under 150 lines |
| `.../spec-writing/spec-form.md` | New. The one-level reference. It states the nine `##` headings and the KPI form (`- K<n>:` with its `Fails if:` line, continuation lines and list items). It gives the Test data table's eight columns, their values and the placeholder class that counts as empty, and the rule for an unbulleted KPI-id line. It also covers what "names code" means, the open-question package form, the check's output words, the imports rule and a clean example |
| `.../spec-writing/check_spec.py` | New. Standard library only (I1). `python3 check_spec.py <spec.md>` prints `REFUSED <part>: <reason>` per failed item and exits 1. For unsecurable data it prints `P1 Test data: <source> cannot be secured`, writes `<spec stem>.P1.md` (options with cost, a recommendation) and exits 2. It prints `PASS` alone and exits 0 only when every item holds (I3). A KPI's behaviour, its continuation lines and its `Fails if:` text are judged for code. An off-form list item under KPIs is refused. Empty privacy and secrets cells are refused. One placeholder class (empty or no letter or digit; a lone `<...>` slot; a deferral such as TBD, TBC, TODO or `to be <word>`; an absence word alone such as none, nobody, n/a), matched against the whole text after emphasis, backticks, brackets and trailing punctuation are peeled, counts as missing in a KPI's behaviour, its `Fails if:` text and the owner, source and licence/recipe cells; a licence cell saying no licence was found (`unlicensed`, `none found` ...) is refused too. An unbulleted line under KPIs that starts with a KPI id is refused, quoted. `--imports <folder>` reads records only under `imports:`: every `<!-- imported: <part> -->` marker needs records whose licences are all allowed (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, CC0-1.0, CC-BY-4.0), else it prints `REFUSED import <part>: ...` and exits 1 (I4) |
| `.../spec-writing/imports.yaml` | New. The skill's import record, `imports: []` (it imports nothing) |
| `.claude/skills/spec-writing/` | **Not in this change.** The CTO's copies ACT generates it from the kernel source (DEC-315, DEC-1112 (3)). Until then, two W2-98 acceptance cases and one W2-11 case stay red by design |

## 3. sha256 of every file, before and after

Before: none of these files exists at the base `6c2c3ed93bee`, so every "before" is `absent`. "After" is at
`f0259229e2b5` (the code is from `0b6d3e07746b`, the fix batch the owner chose for round 2's findings, P-W2-98-R2 (a);
re-written from the rows at `c530a0a1a236`).

| File | Before | After (sha256) | Lines |
|---|---|---|---|
| `template/governance/kernel/skills/spec-writing/SKILL.md` | absent | `34500d5ed3694abce258ee73616bc2832cc169ff0083c66e46b9c82453c8637d` | 105 |
| `template/governance/kernel/skills/spec-writing/check_spec.py` | absent | `b18ebd98028e33aa06c2b3aba634e0a7b012122db304b48436c616aa1c15f310` | 276 |
| `template/governance/kernel/skills/spec-writing/imports.yaml` | absent | `3ddd0e1ab98d22585922395b0915014db4f048994be757b8283422986f9f9cff` | 5 |
| `template/governance/kernel/skills/spec-writing/spec-form.md` | absent | `9174042b22312e69aac2fe4b02ca16e48216566371cf22e781a3985f3c604e4f` | 167 |
| `.rulesync/skills/spec-writing/SKILL.md` | absent | `34500d5ed3694abce258ee73616bc2832cc169ff0083c66e46b9c82453c8637d` | 105 |
| `.rulesync/skills/spec-writing/check_spec.py` | absent | `b18ebd98028e33aa06c2b3aba634e0a7b012122db304b48436c616aa1c15f310` | 276 |
| `.rulesync/skills/spec-writing/imports.yaml` | absent | `3ddd0e1ab98d22585922395b0915014db4f048994be757b8283422986f9f9cff` | 5 |
| `.rulesync/skills/spec-writing/spec-form.md` | absent | `9174042b22312e69aac2fe4b02ca16e48216566371cf22e781a3985f3c604e4f` | 167 |
| `template/.rulesync/skills/spec-writing/SKILL.md` | absent | `34500d5ed3694abce258ee73616bc2832cc169ff0083c66e46b9c82453c8637d` | 105 |
| `template/.rulesync/skills/spec-writing/check_spec.py` | absent | `b18ebd98028e33aa06c2b3aba634e0a7b012122db304b48436c616aa1c15f310` | 276 |
| `template/.rulesync/skills/spec-writing/imports.yaml` | absent | `3ddd0e1ab98d22585922395b0915014db4f048994be757b8283422986f9f9cff` | 5 |
| `template/.rulesync/skills/spec-writing/spec-form.md` | absent | `9174042b22312e69aac2fe4b02ca16e48216566371cf22e781a3985f3c604e4f` | 167 |

## 4. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended, after round 2's findings are settled) | Merge the skill and its `.rulesync` copies; the CTO's copies ACT writes `.claude/skills/spec-writing/` | This ticket's change: four files, about 500 lines, most of them the reference and the check. Two review rounds so far, and the copies ACT |
| Defer | Keep product-spec without a spec method until a later wave | Specs keep arriving without failure lines or test-data owners. W2-27, which lists W2-98 as a dependency, waits |
| Re-baseline | Fold the spec form into an existing skill (discovery or planning) instead | Re-opens DEC-959 item 8's approved card and W2-11's split of skills. A larger change to two skills in force |

## 5. Impact

| Area | Impact |
|---|---|
| Kernel skills | One new skill. No existing skill, hook or role file changes, and the guard does not change |
| Generated copies | `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/` are byte-equal to the source. `.claude/skills/spec-writing/` comes after the copies ACT; until then the adapter check reports `GENERATED_DIFFERS` for it |
| Acceptance suite | `tests/acceptance/W2-98/` has 502 cases, by independent test designers: 94 in run 2, 172 for review round 1 and 236 for round 2's fix (C1-C3). At `f0259229e2b5`, 500 pass and 2 stay red until the copies ACT |
| Other suites | W2-11's `test_the_skill_carries_one_version_in_all_four_places[spec-writing]` (`tests/acceptance/W2-11/test_w2_11_skills.py:140`) stays red until the copies ACT |
| Decisions | None changed |

## 6. Independent review and approval

Two fresh read-only reviewers probed the branch. Their record, with the lead's triage, is
`docs/probes/DAEO-wi46/PR-DAEO-wi46.md`:

- Round 1 failed on F1 and F2; they were fixed through a test-design batch and a fix batch.
- Round 2 failed on three near variants of round 1's findings: a placeholder failure line, an unbulleted KPI id line, and owner placeholders outside the list. That was the last round, so the next step was the owner's decision.
- The owner chose P-W2-98-R2 (a) (2026-11-13): one test-design batch and one fix batch (C1-C3: a placeholder class, unbulleted KPI-id lines refused), then a narrow independent check of exactly that fix. The check (a fresh read-only Opus session) passed on `f0259229e2b5`: all 29 round 2 reproductions refused, the class held on about 230 variants, nothing from round 1 broken; four rows (N1-N4) recorded for a later wave.

The owner's approval line (CAP-33) is written here before the merge: `owner_approval:` in the front matter.
