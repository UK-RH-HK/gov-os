---
id: W2-37-CIT-P
type: change-impact-proposal
status: APPROVED
date: 2026-11-13
branch: w2/W2-37
base: 96498443f237 (F1 (a) built and its tests merged; the change skill as Wave 1 left it)
head: 7bde87727b0f (the version lines at 1.1.0, on the owner's approval); the approved body 68d9a917b8db (the change skill's impact section, a25b02a7); between them only merges of w2/integrate (31bf5ea07, e8c414b0d), touching neither file
owner_approval: "yes W2-37 CIT-P a25b02a7, version 1.1.0" (owner, chat, 2026-11-13) — the approved body is a25b02a7's (commit 68d9a917b) with the two version lines in each file at 1.1.0 (commit 7bde87727); recorded as DEC-1166 (4)
after_sha256: cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76 (both template files, byte-equal, at 7bde87727)
ticket: DAEO-6n5k (W2-37)
task: DAEO-6n5k
author: orchestrator (W2-37 ticket lead); the section written by a fresh engineer session ca10b5dc-5e68-40ca-bb37-967436902f69
review: PASS, independent-auditor session 64d3d4eb-f24c-4f3a-9c76-4f942d1c0066 (Opus, high) on 68d9a917b at 31bf5ea07, 3 rows (C1-C3), none blocking (W2-37-CIT-P-review.md; verdict.ready True)
decisions_carried: [DEC-167, DEC-816, DEC-1163]
decisions_applied: [DEC-1157, DEC-1083, DEC-105, DEC-817]
state_class: EVIDENCE
---

# W2-37: change-impact proposal (CIT-P) on the change skill's impact section

The change skill's `## Impact assessment` section states Wave 1's method: the plain-language question "what is the
impact of X?" triggers an assessment done by hand with `gov closure`. Wave 2 has `gov impact` (this ticket), which
takes that question itself and answers over both graphs. This change routes the section, and the one `## Tools`
sentence that named `gov closure` for the impact, to `gov impact` (CAP-33.g, DEC-167). DEC-816 named the section;
DEC-1163 (7) put its two source files in the ticket's paths and asks for this CIT-P. The section is in the kernel's
skill files, so the owner approves the bytes before the merge (CAP-33).

## 1. What triggers the change

| # | Trigger | Source |
|---|---|---|
| T1 | From Wave 2, "what is the impact of X?" runs `gov impact` (the ticket's KPI S1) | CAP-33.g, DEC-167 |
| T2 | The section named for the change, and its synced copies | DEC-816 |
| T3 | The two source files in W2-37's paths; a CIT-P with the lines verbatim, both hashes and an independent review; the root `.rulesync` and `.claude` copies by the CTO's copies ACT after the approval | DEC-1163 (7) |

## 2. The kernel files and their sha256

| file | version | sha256 before (`96498443f`) | sha256 after (`68d9a917b`) | lines +/- |
|---|---|---|---|---|
| `template/governance/kernel/skills/change/SKILL.md` | 1.0.0 (unchanged) | `2af36b728573e930ff4c5ea689f3a66faff11d342aced19a6a1babbfe16dc982` | `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` | +6 / -5 |
| `template/.rulesync/skills/change/SKILL.md` | 1.0.0 (unchanged) | `2af36b728573e930ff4c5ea689f3a66faff11d342aced19a6a1babbfe16dc982` | `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` | +6 / -5 |

The two files are byte-equal before and after (`cmp`).

**At the owner's version (7bde87727, after the approval).** The owner approved a25b02a7 with version 1.1.0 (DEC-1166 (4)).
A fresh engineer session (bee32285-5162-4880-8fcb-05201c38f1ea) changed the two version lines in each file
(`version: "1.0.0"` → `version: "1.1.0"`; `  version: "1.0.0"` → `  version: "1.1.0"`) and nothing else
(2 files, +2/-2 each):

| file | version | sha256 approved body (`68d9a917b`) | sha256 after (`7bde87727`) |
|---|---|---|---|
| `template/governance/kernel/skills/change/SKILL.md` | 1.1.0 | `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` | `cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76` |
| `template/.rulesync/skills/change/SKILL.md` | 1.1.0 | `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` | `cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76` |

The two files are byte-equal at 7bde87727 (`cmp`).

The CTO's copies (not in this change; by the copies ACT after the approval). Expected after-hashes if the generation is
plain:

| copy | sha256 now | expected after (at 1.1.0, 7bde87727) | how |
|---|---|---|---|
| `.rulesync/skills/change/SKILL.md` | `2af36b728573e930ff4c5ea689f3a66faff11d342aced19a6a1babbfe16dc982` | `cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76` | a byte copy of `template/.rulesync/skills/change/SKILL.md` |
| `.claude/skills/change/SKILL.md` | `e22fd92ff3a6f88d15850ba01046f4f66bf0399e1865ca1bfd51258e0569a352` | `dc4d01de95fb22703f3ef2db79ce5ca516990d641bb6f425af1732cce99f7cd8` | its own frontmatter as rulesync writes it today (folded description, metadata `version:` unquoted, no blank line after the closing `---`) with `  version: 1.1.0`, then the template's new body; today its body equals the template's old body |

(The expected hashes before the version, at a25b02a7's bytes, were `a25b02a7…` and `017328ec8c303cc6c04372420685cd317f80c82444327dd3b16ab9bfaec6658d`; superseded. Computed by `../expected_copies_5.py`; the expected `.claude` bytes are `expected-claude-change-SKILL-1.1.0.md` beside this file. The main tree's copies hash the same "now" values today.)

The version line: the change skill's own lifecycle step 5 says "on approval, the skill's frontmatter version is
incremented" (CAP-24.c; CAP-33.d, versioned promotion). It fixes that the version increments, not to what. The bytes
here keep `1.0.0` so that the owner sees and approves the content alone; the increment is for the owner to set at the
approval (for example `1.1.0`). It is two lines in each template file (`version: "1.0.0"` and `metadata.version:
"1.0.0"`) and changes every after-hash above; the lead reruns the hashes on the owner's number. (Review row C2.)
The owner set `1.1.0` (DEC-1166 (4)); the rerun hashes are in the table above and in the copies table.

## 3. The lines, verbatim

`git show 68d9a917b -- template/governance/kernel/skills/change/SKILL.md` (the `.rulesync` template's diff is the same):

```diff
@@ -45,11 +45,12 @@ The owner chooses among these options. CIT-E records what was done. Every versio
 
 ## Impact assessment
 
-Per DEC-167 (CAP-33.f), a question of the form "what is the impact of X?" triggers the impact assessment. In Wave 1, the method is:
+Per DEC-167 (CAP-33.f), a question of the form "what is the impact of X?" triggers the impact assessment. From Wave 2 the question runs `gov impact` (DEC-167, CAP-33.g):
 
-1. Draft an OpenSpec proposal describing the change (DEC-167, CAP-33.f).
-2. Run `gov closure` over the affected records to identify downstream specifications, decisions, tickets, tests and code (DEC-167).
-3. Present the impact summary to the requester (CAP-33.f).
+1. Run `gov impact "What is the impact of DEC-NNN?"`, or `gov impact <id or symbol>...` (DEC-167, CAP-33.g).
+2. It reads the record graph and the code graph. It reports the state of each graph, whether the report is `complete` and its gaps, each stated item with whether it is deletable, the affected specifications, decisions, tickets, tests and code, and the radius (CAP-33.g).
+3. Add `--out <path>` to write the CIT-P as a record. Run `gov impact --compare <CIT-E path>` to check a CIT-E against its CIT-P (CAP-33.g).
+4. Present the result to the requester (CAP-33.f).
 
 ## Audit ticket
 
@@ -57,4 +58,4 @@ Per DEC-088 (CAP-47.d), an accepted CIT-E that changes a closed spine creates an
 
 ## Tools
 
-CIT-P and CIT-E use OpenSpec (installed, v1.13.2) for drafting proposals and recording outcomes (CAP-33.a). Run `gov closure` to compute the downstream impact of a proposed change (DEC-167, CAP-33.f). Run `gov status` to check the current state of a CIT-P or CIT-E (CAP-33.d).
+CIT-P and CIT-E use OpenSpec (installed, v1.13.2) for drafting proposals and recording outcomes (CAP-33.a). Run `gov impact` to compute the downstream impact of a proposed change (DEC-167, CAP-33.g). Run `gov status` to check the current state of a CIT-P or CIT-E (CAP-33.d).
```

Nothing else in either file changed. The `## Tools` sentence is outside the impact section DEC-816 names; it is changed
because it named `gov closure` for the same impact (review row C1: the owner approves it with the rest, or the section
alone). The CIT-P and CIT-E section's step 3 ("drafted via `gov closure`") still names
`gov closure`; it is outside the impact section and DEC-816, and is left as it is.

## 4. Impact

| kind | affected | how |
|---|---|---|
| specifications | none changed | the section applies CAP-33.f and CAP-33.g as they stand |
| decisions | DEC-167, DEC-816 applied; DEC-1163 (7) | no decision changes |
| tickets | W2-37 (DAEO-6n5k) | its acceptance case `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question[template]` turns green; `[claude-copy]` stays red until the copies ACT |
| tests (other tickets) | **W1-35**: `tests/acceptance/W1-35/test_w1_35.py:991` (`TestPlannedVsMisspeltCommands::test_planned_command_is_valid`) and `test_w1_35.py:845` (`TestSkillRegressionGreen::test_skill_regression_green_with_well_formed_skills`) turn red | `gov check`'s skill regression reports `SKILL_UNKNOWN_COMMAND 'impact'` for each backticked `gov impact`: the command list `src/gov/check/commands.py:14-20` (`RECORDED_GOV_COMMANDS`, joined into `GOV_COMMANDS`, which `src/gov/check/skill_validator.py:46,178` reads) does not hold `impact`. This is package P-7 (DEC-812 (6), the CTO's file). It must land with or before this change |
| tests (other tickets, already red, not from these bytes) | **W1-32**: `tests/acceptance/W1-32/test_w1_32_command_set.py:58` (`test_the_command_set_is_the_twelve_and_the_three_recorded_ones`): "gov has commands the command list does not record: ['adapters', 'dispatch', 'impact', 'session-watch', 'wait']" | `impact` is a command on this branch since before this resume; four other tickets' commands are unrecorded too. W1-32 is outside lead_verify's selection. P-7 (DEC-812 (6)) |
| code | none in this change | P-7: `"impact"` in `RECORDED_GOV_COMMANDS` (`src/gov/check/commands.py`), W1-07's pinned list (`tests/acceptance/W1-07/test_w1_07_recorded_commands.py:50`) and W1-32's command-set assertion (`test_w1_32_command_set.py:58`), as DEC-812 (6) names them (review row C3) |
| the CTO's copies | `.rulesync/skills/change/SKILL.md`, `.claude/skills/change/SKILL.md` | by the copies ACT after the approval; expected hashes in section 2 |

Radius: R2 (tests and code one hop away: the skill check's command list, W1-35's cases, and P-7's W1-07/W1-32 lists).

## 5. Options (DEC-105)

1. **Apply now** (recommended): approve these bytes; the CTO lands P-7 (`impact` in the command list) in the same
   hand-merge, then the copies ACT. Cost: `impact` in `commands.py`, in W1-07's pinned list (`test_w1_07_recorded_commands.py:50`)
   and in W1-32's command-set assertion (`test_w1_32_command_set.py:58`); the copies ACT; the owner's version number.
   W1-35's two cases and `gov check` then stay green.
2. **Defer**: the section stays Wave 1's (`gov closure`); W2-37 lands without it and its two routing cases stay red
   (DoD-1 does not hold for S1's skill half). Cost: a later change and another CIT-P.
3. **Re-baseline**: drop the routing from CAP-33.g's reading (the command alone answers the question). Cost: an owner
   decision changing DEC-167/DEC-816 and the two acceptance cases.

## 6. Review

PASS: the independent auditor (session 64d3d4eb-f24c-4f3a-9c76-4f942d1c0066, Opus, high, fresh and read-only)
checked the lines verbatim, both hashes before and after, the expected copies' hashes, the byte equality, the cited
ids and the section against the command. Rows C1 (the `## Tools` sentence), C2 (the version line) and C3 (P-7's
full cost) are corrected in this text; the bytes are unchanged. The review record with the reviewer's fenced
`verdict` block is `W2-37-CIT-P-review.md` beside this file.

## 7. For the owner

Approve the bytes `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` for both template files
(option 1), and say the version: keep `1.0.0` or the number to set (the hashes are rerun on a bump). P-7 lands with
them.

**Approved (2026-11-13, ~13:50 UTC, chat):** "yes W2-37 CIT-P a25b02a7, version 1.1.0" (DEC-1166 (4)). The bytes that
land are a25b02a7's body with the version lines at 1.1.0: `cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76`
for both template files (7bde87727). The version change has its own narrow independent check
(`../probes/PR-DAEO-6n5k-narrow-version-1.1.0.md`).
