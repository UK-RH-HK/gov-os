---
id: W2-98-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-12
branch: w2/W2-98
base: 6c2c3ed93bee
head: {HEAD12}
ticket: DAEO-wi46 (W2-98)
author: orchestrator (the ticket lead of W2-98), for two product-spec sessions
review: a read-only independent reviewer (independent-auditor, Opus), after the acceptance tests went green; probe record docs/probes/DAEO-wi46/PR-DAEO-wi46.md
decisions_carried: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-1083, DEC-1084, DEC-315, DEC-1112, DEC-1156]
owner_approval: {OWNER_LINE}
state_class: EVIDENCE
---

# W2-98: change-impact proposal (CIT-P) for the new kernel skill spec-writing

This change adds one kernel skill, `template/governance/kernel/skills/spec-writing/`, the product-spec session's
method for writing a spec (ROLES-RESEARCH-1 §5.3 item 7, approved by DEC-959 item 8), and its two `.rulesync`
copies. It is a kernel skill change, so it goes through CIT-P (CAP-33): evidence, independent review and the owner's
approval line before the merge. No existing kernel file changes.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | product-spec has no method for a spec: the problem, users and scenarios, goals and non-goals, KPIs as observable behaviour each with a failure line, open questions as packages, who accepts | DEC-959 item 8; ROLES-RESEARCH-1 §2.4 | No skill |
| T2 | The owner's test-data section: the data the tests need, imported or synthetic, who secures it and how (licence, privacy, no secrets, a hidden half where it measures); unsecurable data escalated as a P1 | DEC-959 item 8 | No skill |
| T3 | One skill template for every kernel skill | DEC-959 item 5 (W2-11 r1) | Template in force |
| T4 | Imported text adopted only with its licence checked and recorded | DEC-1084 | No record for this skill |
| T5 | The check's interface I1-I4 | DEC-1156 (5) (P-W2-98-IF-1 (a)) | Decided 2026-11-12 |

## 2. What changes

| File (kernel source; the two `.rulesync` copies are byte-equal) | Change |
|---|---|
| `template/governance/kernel/skills/spec-writing/SKILL.md` | New. The skill in the one template: front matter (name, version 1.0.0, a third-person description); When / not when; Inputs; Steps (an 11-item checklist naming the nine parts and the check); Done when (five yes/no items, among them "every KPI line testable without naming code" and "every data source with its owner and its licence or recipe"); Output and handover (the twelve fields); Escalation (P3, P2, P1, Emergency; unsecurable data is a P1); Never; Sources last. Body under 150 lines |
| `.../spec-writing/spec-form.md` | New. The one-level reference: the nine `##` headings, the KPI form `- K<n>:` with its `Fails if:` line, the Test data table's eight columns and values, what "names code" means, the open-question package form, the check's output words, the imports rule, a clean example |
| `.../spec-writing/check_spec.py` | New. Standard library only (I1). `python3 check_spec.py <spec.md>`: `REFUSED <part>: <reason>` per failed item, exit 1; `P1 Test data: <source> cannot be secured` plus `<spec stem>.P1.md` (options with cost, a recommendation), exit 2; `PASS` alone, exit 0 (I3). A KPI's behaviour, its continuation lines and its `Fails if:` text are judged for code. `--imports <folder>`: every `<!-- imported: <part> -->` marker needs a record in `imports.yaml` with an allowed licence (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, CC0-1.0, CC-BY-4.0), else `REFUSED import <part>: ...`, exit 1 (I4) |
| `.../spec-writing/imports.yaml` | New. The skill's import record, `imports: []` (it imports nothing) |
| `.claude/skills/spec-writing/` | **Not in this change.** Generated from the kernel source by the CTO's copies ACT (DEC-315, DEC-1112 (3)); until then two acceptance cases stay red by design |

## 3. sha256 of every file, before and after

Before: none of these files exists at the base `6c2c3ed93bee` (every "before" is `absent`). After, at `{HEAD12}`:

| File | Before | After (sha256) | Lines |
|---|---|---|---|
{SHA_ROWS}

## 4. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended) | Merge the skill and its `.rulesync` copies; the CTO's copies ACT writes `.claude/skills/spec-writing/` | This ticket's change (four files, about 470 lines with the reference and the check), one review; the copies ACT |
| Defer | Keep product-spec without a spec method until a later wave | Specs keep arriving without failure lines or test-data owners; W2-27 (which lists W2-98 as a dependency) waits |
| Re-baseline | Fold the spec form into an existing skill (discovery or planning) instead | Re-opens DEC-959 item 8's approved card and W2-11's split of skills; a larger change to two skills in force |

## 5. Impact

| Area | Impact |
|---|---|
| Kernel skills | One new skill; no existing skill, hook, role file or the guard changes |
| Generated copies | `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/` byte-equal to the source; `.claude/skills/spec-writing/` after the copies ACT; the adapter check reports `GENERATED_DIFFERS` for it until then |
| Acceptance suite | `tests/acceptance/W2-98/` (94 cases, by the independent test designer): 92 passed, 2 red until the copies ACT |
| Decisions | None changed |

## 6. Independent review and approval

A fresh read-only reviewer probed the head; its record is `docs/probes/DAEO-wi46/PR-DAEO-wi46.md` (verdict {VERDICT}).
The owner's approval line (CAP-33) is written here before the merge: `owner_approval:` in the front matter.
