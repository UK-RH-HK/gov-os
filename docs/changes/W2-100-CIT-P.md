---
id: W2-100-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-14
branch: w2/W2-100
base: 627bcaa19351
head: f7637bd03e25
ticket: DAEO-uw5h (W2-100)
author: orchestrator (the ticket lead of W2-100), for seven product-spec sessions and two test-designer sessions
review: 'two narrow independent checks by fresh read-only auditors (independent-auditor, Opus, high): check 1 PASS on f8e7c0fad6c6 (all twelve KPI lines; rows F1, F3-F5; F2 out of scope, package P-W2-100-F2), check 2 PASS on f7637bd03e25 (the follow-up to F1 and F3; rows N1-N4) (docs/probes/DAEO-uw5h/)'
decisions_carried: [DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112, DEC-1157]
owner_approval: 'pending'
state_class: EVIDENCE
---

# W2-100: change-impact proposal (CIT-P) for four new kernel skills: backend, api, data and security

This change adds four kernel skills, `template/governance/kernel/skills/{backend,api,data,security}/`, and their two
`.rulesync` copies each. Each is the engineer's skill for its area (ROLES-RESEARCH-1 §2.7, approved by DEC-959 item 4;
DEC-957 Q5): the area's conventions, a pre-commit checklist, its unit-test focus, its common mistakes and when to
escalate. It is a kernel skill change, so it goes through CIT-P (CAP-33): evidence, independent review and the
owner's approval line before the merge. No existing kernel file, role file, hook or `src/` file changes.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | The engineer loads one domain skill per ticket beside its vendored skills; four of the seven areas (backend, API, data, security) with their main points | DEC-957 Q5; DEC-959 item 4; ROLES-RESEARCH-1 §2.7, §2.12 | No domain skill |
| T2 | Any security finding is a P1; secrets and security are P1 | DEC-957 | Not stated in any engineer skill |
| T3 | One skill template; three scenarios written before the text, run on fresh sessions | DEC-959 item 5 (W2-11 r1; the harness W2-104) | Template and harness in force |
| T4 | The skill grants nothing | CAP-24.b | Rule in force |
| T5 | The interface at claim: each skill's own check `check_domain_skill.py` (I1) and the readings of the code-bound clauses | P-W2-100-IF-1 (a), the CTO under DEC-1157 (3) and (12) (`0a706dc4c`) | Decided 2026-11-14 |

## 2. What changes

Each skill folder holds five files; the two `.rulesync` copies of each are byte-equal to the kernel source.

| File (each of the four skills) | Change |
|---|---|
| `SKILL.md` | New. The one template: front matter `name`, `version` (backend and security 1.0.1, api and data 1.0.2), a third-person description, `output: none`, `metadata.version`; When / not when; Inputs; Conventions; Steps (a checklist); Pre-commit checklist; Unit-test focus; Common mistakes; Done when; Output and handover (the twelve fields); Escalation (P3, P2, P1, Emergency; a `When to escalate:` line); Never; Sources last. Bodies 131 to 143 lines (backend, security) and 147 to 148 (data, api). The named points: backend error handling, idempotence, migrations; api contract-first, versioning, backward compatibility; data schema changes, migration and rollback, data quality; security input checks, secrets never in code, least privilege, NIST SSDF's four groups by name, and "any security finding is a P1". No permission line; no step widens the engineer's reads or writes |
| `check_domain_skill.py` | New, byte-equal in the four folders (I1, standard library). `python3 <skill>/check_domain_skill.py <SKILL.md>` prints `REFUSED <skill>: missing <section\|part\|point>`, `REFUSED <skill>: section order: <section>`, `REFUSED <skill>: permission line <n>: <text>` or (security) `REFUSED security: finding below P1 line <n>: <text>`, exit 1; else `PASS`, exit 0 |
| `scenarios.md` | New, committed before the text (`a7989493b` before `c7686c533`). Three scenarios in `gov skilleval`'s form; security's include a finding that must be routed P1 (scenario 2) and a key in the repository (scenario 3, an Emergency) |
| `scenario-records.yaml` | New: the harness's records of the lead's real `gov skilleval` runs, unedited, every run kept (run 1's api scenario 2 FAIL, run 6's api 2 and data 2 FAILs included) |
| `scenario-summaries.md` | New: one hand-written entry per record entry (scenario, verdict, run_at, a three-line summary of the reply), from the replies the lead captured with a pass-through `claude` on `PATH` (the harness's envelope carries no reply by design); its opening paragraph states that run 5's sessions could read this file (check 1's F1) and that runs 6 to 8 were clean |
| `.claude/skills/<skill>/` | **Not in this change.** The CTO's copies ACT generates it from the kernel source (DEC-315, DEC-1112 (3)). Until then twelve acceptance cases stay red by design: W2-100's four `.claude` copy cases and four adapter generated-drift cases, and W2-11's four `four_places` cases |

## 3. sha256 of every file, before and after

Before: none of these files exists at the base `627bcaa19351`, so every "before" is `absent`. "After" is at
`f7637bd03e25`. Each `.rulesync/skills/<skill>/<file>` and `template/.rulesync/skills/<skill>/<file>` has the same
sha256 as its kernel file (checked from the git objects at that head: no copy differs).

| File | Before | After (sha256) | Lines |
|---|---|---|---|
| `template/governance/kernel/skills/backend/SKILL.md` | absent | `8c4e9e9d9a7e5e1f8a4bc0ba8bfe07e98d3187ea8c1026219fbdff8bcdc0b0da` | 139 |
| `template/governance/kernel/skills/backend/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` | 139 |
| `template/governance/kernel/skills/backend/scenario-records.yaml` | absent | `cf20652e825386ca82b763e811bcd93f94cba6e5ab77a4d5d0de1ac20b8f5476` | 133 |
| `template/governance/kernel/skills/backend/scenario-summaries.md` | absent | `509f68994fa29bc06f1065ff4b6ee3d62c219374efcafe1bdc82da7afe51014d` | 99 |
| `template/governance/kernel/skills/backend/scenarios.md` | absent | `84b71aed50416474ecda06b9d927893b071f7ee190859b982dfe088b7d82409a` | 38 |
| `template/governance/kernel/skills/api/SKILL.md` | absent | `f6956285fd93785fe91534b0c5f76d1ce8bb2cff4d49775f7590cca567e5e965` | 148 |
| `template/governance/kernel/skills/api/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` | 139 |
| `template/governance/kernel/skills/api/scenario-records.yaml` | absent | `a78358a1ffd994e9f8497c08b3cbc3b1fe5f1947095ceda0d5f3995e522bd880` | 199 |
| `template/governance/kernel/skills/api/scenario-summaries.md` | absent | `7c0bc6fa0f15653b3381f3047b911f09fdfb3224d1c41e2982573f1b6007505f` | 147 |
| `template/governance/kernel/skills/api/scenarios.md` | absent | `65b6460ce7b4fb628f9646e03369a40b466b1a12bf475b1a91e4de397c5fbae3` | 36 |
| `template/governance/kernel/skills/data/SKILL.md` | absent | `f388e1a605e2afd57bcc3277b240b3429b804f35bd69e977c8b09fc11843d03e` | 147 |
| `template/governance/kernel/skills/data/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` | 139 |
| `template/governance/kernel/skills/data/scenario-records.yaml` | absent | `11436b7a7ec6ab9000c6ff1f15a9f1082e72cd2ae39c80e3016c202cb6e89589` | 199 |
| `template/governance/kernel/skills/data/scenario-summaries.md` | absent | `cf701bd3ed5523426f1d1e9e2a82f18b309fcddf925c69b34d9fe346d110b135` | 147 |
| `template/governance/kernel/skills/data/scenarios.md` | absent | `514c5e473f2ef48346c9a69b5c30de3122ce997a65095bc0754ca302ef711418` | 37 |
| `template/governance/kernel/skills/security/SKILL.md` | absent | `610371cfbc3410104fe3bfdd52cf8757402b22aaab550e15c5bb49618dcb93a1` | 151 |
| `template/governance/kernel/skills/security/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` | 139 |
| `template/governance/kernel/skills/security/scenario-records.yaml` | absent | `dfcebf97d06b2d1709e7250d72fa2dbfe029e212aefb2a9270a867a4625359df` | 166 |
| `template/governance/kernel/skills/security/scenario-summaries.md` | absent | `4791045bd5b06fac8b4b6eb7d4f9f81f012030e4caed11b8d75ce2a86552e7c6` | 123 |
| `template/governance/kernel/skills/security/scenarios.md` | absent | `477d93046c27d03668d98e848fd248c45d0cdcc59d57050cabd9737e179cb3ea` | 38 |

## 4. The evidence

- **Scenarios on fresh sessions (S4, DEC-959 item 5)**, the real `gov skilleval` (Opus, high), clean runs (no
  summaries in the skill folder) at each skill's current version: backend 1.0.1 run 6 3/3; security 1.0.1 run 6 3/3;
  api 1.0.2 runs 7 and 8 3/3 each; data 1.0.2 runs 7 and 8 3/3 each. Earlier runs, all kept in the records: run 1
  (1.0.0) api 2 FAIL, the rest pass; runs 2 to 4 (1.0.0) pass; run 5 (1.0.1) twelve passes, not clean (check 1's F1);
  run 6 (1.0.1) api 2 and data 2 FAIL, fixed by `3318e42f6` and `05fcc8f2e`.
- **F2, a security finding routed below P1:** a planted copy of the security skill routing a finding as P2 is refused
  by I1 (three REFUSED lines) and fails the real `gov skilleval` (exit 3, scenario 2 FAIL) (the lead's evidence,
  `.gov-runtime/scratch/lead/f2/`).
- **Acceptance (`gov accept W2-100`):** 222 passed, 8 failed; success-1 to success-5 and failure-1 to failure-5 pass; the 8 fails are the `.claude/skills/` cases under success-6 and failure-6 (4 copy comparisons, 4 adapter generated-drift cases), red until the copies ACT
- **The lead's scoped run (lead_verify, DEC-968) at `f7637bd03e25`:** 6270 tests, 12 failed, 7 skipped, 0 errors; the 12 are the `.claude/skills/` cases (W2-100's 8 and W2-11's 4 `four_places`), red until the copies ACT; none else
- **Generated copies:** `diff -r` of each skill folder against both `.rulesync` copies is empty; the adapter check
  gives no `SOURCE_*` finding; its 20 `GENERATED_DIFFERS` are the four skills' absent `.claude/skills/` copies.

## 5. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended) | Merge the four skills and their `.rulesync` copies; the CTO's copies ACT writes `.claude/skills/{backend,api,data,security}/`; P-W2-100-F2 (the harness leaving `scenario-summaries.md` out of the session) taken before the next `gov skilleval` of these folders | This ticket's change: 20 kernel files, about 2,400 lines with the records and summaries; the copies ACT |
| Defer | Engineers keep working without a domain skill until a later wave | Security findings keep no written P1 route in the engineer's method; W2-101 (domain skills B) has no sibling to follow |
| Re-baseline | Fold the four areas into one engineer skill, or drop the in-skill check for a validator change | Re-opens DEC-959 item 4's card and P-W2-100-IF-1 (a); an engineer pair on three shipped modules (P-W2-100-IF-1 (b)) |

## 6. Impact

| Area | Impact |
|---|---|
| Kernel skills | Four new skills. No existing skill, hook or role file changes; the guard does not change (S2: the guard's decision for an engineer is the same with and without a skill present) |
| Generated copies | `.rulesync` copies byte-equal. `.claude/skills/<skill>/` after the copies ACT, which will also carry `scenarios.md`, the records and the summaries (every file of the folder): an engineer loading a skill can read its scenarios (no guard effect; check 1's discovery) |
| Acceptance suite | `tests/acceptance/W2-100/`, 230 cases by independent test designers (td-1; td-2 revised one case's version reading, `Rewrite-Reason` trailer). At `f7637bd03e25` all pass but the eight `.claude` cases, red until the copies ACT |
| Other suites | W2-11's `test_the_skill_carries_one_version_in_all_four_places[backend\|api\|data\|security]` red until the copies ACT |
| The harness | P-W2-100-F2 (out of scope, fails open): `gov skilleval` copies `scenario-summaries.md` into the session (`src/gov/skilleval/harness.py:167-168`); recommended (a): add it to the harness's ignore list in its own ticket |
| Decisions | None changed |

## 7. Independent review and approval

Two fresh read-only auditors probed the branch; their records, with the lead's triage, are
`docs/probes/DAEO-uw5h/PR-DAEO-uw5h-check1.md` and `PR-DAEO-uw5h-check2.md`:

- Check 1 (`f8e7c0fad6c6`): PASS on all twelve KPI lines; no blocking finding. Rows F1 (run 5 not clean) and F3 (api
  scenario 2 borderline), acted on in the same round (DEC-802); F4 and F5 rows; F2 out of scope, a package to the CTO.
- Check 2 (`f7637bd03e25`): PASS; F1 and F3 settled; rows N1 to N4.

The owner's approval line (CAP-33) is written here before the merge: `owner_approval:` in the front matter.
