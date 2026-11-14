---
id: W2-101-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-14
branch: w2/W2-101
base: 2748a2b19622
head: 1ef54a70037a
ticket: DAEO-6icv (W2-101)
author: orchestrator (the ticket lead of W2-101), for five product-spec sessions and one test-designer session
review: 'two narrow independent checks by fresh read-only auditors (independent-auditor, Opus, high): round 1 FAIL on 0b0d4cb3053d (F1, the harness would show scenario-summaries.md to the session under test; fixed in W2-104 under DEC-1164 (18)), round 2 PASS on 1ef54a70037a (F1 and the lead''s L1 fixed; rows F2-F9) (docs/probes/DAEO-6icv/)'
decisions_carried: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-315, DEC-1112, DEC-1157, DEC-1164]
owner_approval: '"W2-101 CIT-P approved at 42c1cc38" (the owner, chat, 2026-11-14; DEC-1178 (2))'
state_class: EVIDENCE
---

# W2-101: change-impact proposal (CIT-P) for three new kernel skills: frontend, ui-ux and devops

This change adds three kernel skills, `template/governance/kernel/skills/{frontend,ui-ux,devops}/`, with two `.rulesync`
copies of each. Each is the engineer's skill for its area (ROLES-RESEARCH-1 §2.7, approved by DEC-959 item 4; DEC-957
Q5). Each holds the area's conventions, a pre-commit checklist, its unit-test focus, its common mistakes and when to
escalate. Because it changes the kernel's skills, it goes through CIT-P (CAP-33): evidence, independent review and the
owner's approval line before the merge. No existing kernel file, role file, hook or `src/` file changes in this
ticket's own commits. The merge from `w2/integrate` brought W2-104's harness fix, which is W2-104's change, landed and
reviewed there.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | The engineer loads one domain skill per ticket beside its vendored skills. These are the other three of the seven areas: frontend (accessibility, state, browser support), UI/UX (user flows reviewed by the owner as scenarios, not code) and DevOps (hermetic builds, pinned versions, rollback) | DEC-957 Q5; DEC-959 item 4; ROLES-RESEARCH-1 §2.7 | No skill for these areas (W2-100 brings backend, api, data and security) |
| T2 | One skill template; three scenarios written before the text and run on fresh sessions | DEC-959 item 5 (W2-11 r1; the harness, W2-104) | Template and harness in force |
| T3 | The skill grants nothing | CAP-24.b | Rule in force |
| T4 | The interface at claim: each skill's own check `check_domain_skill.py` (I1) and the readings of the clauses that bind code | P-W2-100-IF-1 (a), the CTO under DEC-1157 (3) and (12), as for W2-100; condensed 2026-11-14 (CTX-1 (a)) | Decided |

## 2. What changes

Each skill folder holds five files. The two `.rulesync` copies of each are byte-equal to the kernel source.

| File (each of the three skills) | Change |
|---|---|
| `SKILL.md` | New. It follows the one template. The front matter holds `name`, `version` (frontend 1.2.0, ui-ux 1.1.0, devops 1.1.0), a third-person description, `output: "<allowed_path>/** (one entry of the ticket's allowed_paths)"` and `metadata.version`. The sections, in order: When / not when; Inputs; Steps (a checklist carrying the labelled parts **Conventions:**, **Unit-test focus:**, **Common mistakes:** and **Pre-commit checklist:**); Done when; Output and handover (the twelve fields); Escalation (P3, P2, P1, Emergency, with a `When to escalate:` line); Never; Sources last. Bodies are 143 (frontend), 130 (ui-ux) and 144 (devops) lines. Each carries the area's named points as labels. There is no permission line, and no step widens the engineer's reads or writes. Writes stay in the ticket's paths |
| `check_domain_skill.py` | New, byte-equal in the three folders (I1, standard library only). `python3 <skill>/check_domain_skill.py <SKILL.md>` prints `REFUSED <skill>: missing <section\|part\|point>` or `REFUSED <skill>: permission line <n>: <text>` and exits 1. Otherwise it prints `PASS` and exits 0 |
| `scenarios.md` | New. It was committed before the skill text (`b465043d5c79` at 01:25:55, before `fb784e756147` at 01:28:08). It holds three scenarios in `gov skilleval`'s form. Frontend scenario 3 was revised once (`9905c9951763`), after it failed twice for want of code to change: it gained a code snippet and now expects P1 for an open support-list question. Round 1 judged that revision and found it made the scenario judgeable without weakening it |
| `scenario-records.yaml` | New. The harness's records of the lead's real `gov skilleval` runs, unedited, with every run kept (frontend 12 entries, ui-ux 12, devops 9) |
| `scenario-summaries.md` | New. One hand-written entry per record entry (scenario, verdict, `run_at`, skill version, and a three-line summary of the reply). The replies come from the lead's pass-through `claude` capture, because the harness's envelope carries no reply by design. The harness now leaves this file out of the session's copy (W2-104, DEC-1164 (18)) |
| `.claude/skills/<skill>/` | **Not in this change.** The CTO's copies ACT generates it from the kernel source (DEC-315, DEC-1112 (3)). Until then nine acceptance cases stay red by design: W2-101's three `.claude` copy cases and three adapter generated-drift cases, and W2-11's three `four_places` cases |

## 3. sha256 of every file, before and after

None of these files exists at the base `2748a2b19622`, so every "before" is `absent`. "After" is at `1ef54a70037a`,
read from the git objects. Each `.rulesync/skills/<skill>/<file>` and `template/.rulesync/skills/<skill>/<file>` has the
same sha256 as its kernel file. The check found no copy that differs, no extra file and nothing under `.claude/skills/`.

| File | Before | After (sha256) | Lines |
|---|---|---|---|
| `template/governance/kernel/skills/frontend/SKILL.md` | absent | `ac86c6384f58c1dcf1f94efe93a5490f88d92ea06bc90aae062da96c11805edc` | 143 |
| `template/governance/kernel/skills/frontend/check_domain_skill.py` | absent | `3532f93de84972ded38ef7725dac323f45bab78e5c4735dc90d8ed84ddc9d62a` | 163 |
| `template/governance/kernel/skills/frontend/scenario-records.yaml` | absent | `44f6d05d0f56d526cec2d7c0f2c8e945b5088180ceabbf16d532a495a07cdcfd` | 133 |
| `template/governance/kernel/skills/frontend/scenario-summaries.md` | absent | `a3f597664ece8d9e9e690b8db9cca99360b4988df3d38619d329cfed7fc1a11d` | 140 |
| `template/governance/kernel/skills/frontend/scenarios.md` | absent | `d572be6bb9143e2a70e4499771e554ba2bba16a259c2601417c84f2dac60640a` | 52 |
| `template/governance/kernel/skills/ui-ux/SKILL.md` | absent | `9a50b6f26539936f50775b65eea717a5906c841aa5cf033f04da39c400f8be54` | 130 |
| `template/governance/kernel/skills/ui-ux/check_domain_skill.py` | absent | `3532f93de84972ded38ef7725dac323f45bab78e5c4735dc90d8ed84ddc9d62a` | 163 |
| `template/governance/kernel/skills/ui-ux/scenario-records.yaml` | absent | `9b038c094435183aa0866866222f8f5931f69e9dc0285bd28fa290514eaf146e` | 133 |
| `template/governance/kernel/skills/ui-ux/scenario-summaries.md` | absent | `665707193be00eb7f888a623b55327e043bd95617a1a9279be177363c202895b` | 139 |
| `template/governance/kernel/skills/ui-ux/scenarios.md` | absent | `714ecf9e1d15b597c3dd938fc2427218b52ba403cbd79e4f12cb5d5bf9caabc9` | 44 |
| `template/governance/kernel/skills/devops/SKILL.md` | absent | `468257eb1ee4ee66b1c36cf388ae05b4808ef807533b7655f9c54cf4684b6fd3` | 144 |
| `template/governance/kernel/skills/devops/check_domain_skill.py` | absent | `3532f93de84972ded38ef7725dac323f45bab78e5c4735dc90d8ed84ddc9d62a` | 163 |
| `template/governance/kernel/skills/devops/scenario-records.yaml` | absent | `87f6c71296571252c7bd82b4f0062c03be7f8396a1bf8c13c4d7a5f7edd25b28` | 100 |
| `template/governance/kernel/skills/devops/scenario-summaries.md` | absent | `6b5c340edba9fbee9d2a4664749fe34de99eeae8d4c7d4fbbbd125c0681575f0` | 106 |
| `template/governance/kernel/skills/devops/scenarios.md` | absent | `a6a737c6c2db84d0b905f38c3532337b9387b4d0ab70b87f2c9fe963a19dd5d9` | 41 |

## 4. The evidence

- **Scenarios on fresh sessions (S4, DEC-959 item 5).** The real `gov skilleval` ran on Opus at high effort. Run 3
  started at 03:43 UTC, after the last skill-text commit (`3cd17b73e3ee`, 03:43:17), and is clean (the harness leaves
  the summaries out). Each skill passed 3 of 3 at its current version: frontend 1.2.0, ui-ux 1.1.0, devops 1.1.0.
  Round 2 checked the capture and found no sight of the summaries or the expected answers in any session.
- **Earlier runs, all kept in the records:**
  - Run 1 (1.0.0, no capture): frontend scenario 3 and ui-ux scenario 2 FAIL; the rest pass.
  - Diagnostic run (1.0.0): frontend scenario 3 FAIL; ui-ux 3 of 3.
  - Run 2 (frontend 1.1.0 after the fix, the others 1.0.0): 9 of 9 pass. These sessions could not read the summaries,
    which were committed after the run.
- **Acceptance (`gov accept W2-101`):** 271 passed, 6 failed. Success-1 to success-5 and failure-1 to failure-4 pass.
  The 6 failures are the `.claude/skills/` cases under success-6 and failure-5 (3 copy comparisons and 3 adapter
  generated-drift cases), red until the copies ACT.
- **The lead's scoped run (`lead_verify`, DEC-968) at `1ef54a70037a`:** 6328 tests, 9 failed, 7 skipped, 0 errors. The
  9 are the `.claude/skills/` cases (W2-101's 6 and W2-11's 3 `four_places` cases), red until the copies ACT. Nothing
  else failed.
- **Generated copies:** `diff -r` of each skill folder against both `.rulesync` copies is empty.

## 5. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended) | Merge the three skills and their `.rulesync` copies. The CTO's copies ACT then writes `.claude/skills/{frontend,ui-ux,devops}/` | This ticket's change: 15 kernel files of 1,794 lines (the records and summaries included) and 30 byte copies; then the copies ACT |
| Defer | Engineers keep working without these three domain skills until a later wave | Interface tickets carry no written accessibility, state or browser-support method; flows are not put to the owner as scenarios; deploys carry no written rollback or pinning rule |
| Re-baseline | Fold the areas into one engineer skill, or drop the in-skill check in favour of a validator change | Reopens DEC-959 item 4's card and the Interface (P-W2-100-IF-1 (a)); an engineer pair on shipped modules |

## 6. Impact

| Area | Impact |
|---|---|
| Kernel skills | Three new skills. No existing skill, hook or role file changes. The guard does not change (S2: its decision for an engineer is the same with and without a skill present) |
| Generated copies | The `.rulesync` copies are byte-equal. `.claude/skills/<skill>/` comes with the copies ACT and carries every file of the folder, `scenarios.md`, the records and the summaries included. An engineer who loads the skill can read them; the harness copies from the kernel folder and leaves them out (round 2's discovery) |
| Acceptance suite | `tests/acceptance/W2-101/`, 277 cases written by the independent test designer (td-1). At `1ef54a70037a` all pass except the six `.claude` cases, which stay red until the copies ACT |
| Other suites | W2-11's `test_the_skill_carries_one_version_in_all_four_places[frontend\|ui-ux\|devops]` stays red until the copies ACT. W2-11's output-class cases pass (L1) |
| Rows for Wave 3 | F2 to F9 (`docs/probes/DAEO-6icv/`). F8 is an entry criterion (DEC-803) for any ticket that gives the harness's sessions tools: the summaries in the repository would then be within reach |
| Decisions | None changed |

## 7. Independent review and approval

Two fresh read-only auditors probed the branch. Their records, with the lead's triage, are
`docs/probes/DAEO-6icv/PR-DAEO-6icv.md` (round 1) and `PR-DAEO-6icv-r2.md` (round 2):

- **Round 1 (`0b0d4cb3053d`): FAIL on F1.** The harness copied `scenario-summaries.md` into the session (fails open).
  The CTO fixed it in the product by reopening W2-104 (DEC-1164 (18)). Rows F2 to F6. The lead added L1: W2-11's
  output-class case refused the skills' `output:` value.
- **Round 2 (`1ef54a70037a`): PASS, the last round (DEC-1010).** F1 and L1 are fixed. F2 to F6 keep their
  classification. F7 to F9 are new rows; none of them blocks.

The owner's approval line (CAP-33) is written here before the merge, in `owner_approval:` in the front matter.
