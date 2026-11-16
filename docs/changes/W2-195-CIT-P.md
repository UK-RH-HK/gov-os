---
id: W2-195-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-16
branch: w2/W2-195
base: 06cd7f869ea6
head: 8ec12d149e9c
ticket: DAEO-d8df (W2-195)
author: orchestrator (the ticket lead of W2-195)
review: 'pending (one independent auditor, fresh and read-only, after the open path cases are settled)'
decisions_carried: [DEC-1204, DEC-039, DEC-801, DEC-1010, DEC-974, CAP-33, CAP-24.b]
owner_approval: 'pending (DEC-1204 (7), the owner approves the committed bytes by their sha256)'
state_class: EVIDENCE
---

# W2-195: change-impact proposal (CIT-P) for the kernel skill judging-work and the judging roles' Skills lines

DEC-1204 merges ADR-0001 / DEC-039's threat model, DEC-801's blocking test and DEC-1010 item 1's convergence into one
golden rule and puts it in one kernel skill, `judging-work` (the owner's "yes judging-work 0fc1c502"). This change
installs that skill in the kernel and its rulesync mirror, and names it in the Skills lines of the four roles that judge
or triage work. It is a kernel change, so it goes through CIT-P (CAP-33): evidence, independent review and the owner's
approval of the bytes before the merge. The product code that briefs, checks and ships the skill (`src/gov/`) is in the
same branch and is not a kernel file; it is listed in section 5 for the review.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | One golden rule for judging work, in one kernel skill preloaded by every judging role | DEC-1204 (5); P-GOLDEN-RULE-1 sections 2 to 4 | The rule lived in three register entries and in hand-pasted brief paragraphs |
| T2 | The skill's text is the owner-approved `judging-work.SKILL.md`, word for word | DEC-1204 ("yes judging-work 0fc1c502") | `governance/project/orchestration/packages/judging-work.SKILL.md`, sha256 `0fc1c502…` |
| T3 | Kernel skills and role files change only by CIT-P with independent review and the owner's approval | CAP-33; CAP-24.b (skills grant no permissions) | In force |

## 2. The skill's bytes: the approved text with one value quoted

The approved text's front-matter `description:` value holds an unquoted `": "` (`...merged by DEC-1204): the threat
model...`), so YAML refuses the front matter (the store's rebuild reports it as "mapping values are not allowed here",
and `gov adapters generate` and the brief's version reader could not read it). The kernel copy wraps that one value in
double quotes. Every other byte is the approved text's.

| | sha256 | bytes | lines |
|---|---|---|---|
| Approved text (`governance/project/orchestration/packages/judging-work.SKILL.md`) | `0fc1c502f553eb780bb0af4652b04f676853b10e097270c2d6ad2bea89a5f5c7` | 3681 | 58 |
| Kernel copy (the approved text, `description:` value double-quoted) | `3fd8864b4b095b01b8748da01acd6a5a0dbd1295aa28ee7e97007dc21d48bf4d` | 3683 | 58 |
| Sections 1 to 3 of the kernel copy (from the line `## 1. The threat model` up to, not including, `## 4. Doing it`): what every judging brief carries | `36f94490027fdaaddb32105e651621a7a83af7d82fdb36a31a8263df79ec7ac3` | | |

The one changed line (line 3), as `diff approved kernel` shows it: `description: The one rule …` becomes
`description: "The one rule …"` (two added bytes: the opening and the closing quote). Front matter `version: "1.0.0"`.

## 3. sha256 of every kernel file, before and after

Before is the base of the build run `bc91df0ab080` (equal to `06cd7f869ea6` for these files); after is `8ec12d149e9c`.

| File | Before | After (sha256) | Lines |
|---|---|---|---|
| `template/governance/kernel/skills/judging-work/SKILL.md` | absent | `3fd8864b4b095b01b8748da01acd6a5a0dbd1295aa28ee7e97007dc21d48bf4d` | 58 |
| `template/.rulesync/skills/judging-work/SKILL.md` | absent | `3fd8864b4b095b01b8748da01acd6a5a0dbd1295aa28ee7e97007dc21d48bf4d` | 58 |
| `template/governance/kernel/roles/independent-auditor.md` | `4b4a5f947206517e167d6b39c9531d3fa7a96476b1d0658ea52e84277a92746c` | `31681ded211608fb784690eb82c656f42090711f6b24d1452bff0624de4fb776` | 35 |
| `template/governance/kernel/roles/qa-engineer.md` | `40fd68fdadf35df679a14842f86e6b51ce849eec65d241cf6fca04f63b362f3a` | `e73c8537a2bc78839ffe4fed5dba13c2db79f06c9e6f04485206c140b9e85ea5` | 28 |
| `template/governance/kernel/roles/orchestrator.md` | `08ba69e63d51adeb901ef8998f6dc2a21490dff9b326c69a603fafbf14d47d10` | `211260c7a78e2849038c94177c3ccdd55e0b0ca5bb3e67c797c597e6f7e09e9e` | 26 |
| `template/governance/kernel/roles/ticket-lead.md` | `0c93598c82daf3f5401c9d5c3293a00144a40565682fd878f289926593b355af` | `929c2b04281645937ba64457b5d1ea6e717d3353eec722560c2224e49e345441` | 35 |
| `template/governance/kernel/templates/role-reviewer.md` | `eff256eb02771c1edf8433dc563f190df56df509d2cc8076b91cd6e97bdb65b7` | `e816d0d874699b065cdaf4456bc239981c5e9cc319da7db8a9efcae63cc29be3` | 43 |
| `template/.rulesync/subagents/independent-auditor.md` | `b6892aaff0a58832e2278624f1aee802765409ebffb9af53bfb3b0b8ebd21a71` | `2b9081844c4da3a208317338eddca56eda1410edcf286bb9eb36e3bd8a75c0e0` | 82 |
| `template/.rulesync/subagents/qa-engineer.md` | `5f41e7bc74071d57bab55e26726c20ea55048316704dcc47c1e465be553249d3` | `4aa5744ea67abcb18b221daee3783529377fa12086048872c331adeafff3dde1` | 37 |
| `template/.rulesync/subagents/orchestrator.md` | `5db8f0cbac35e30ebb81757bb8b92001c611a8080ba8dba9402bd6a4b6a222ba` | `dc052783a094c8c42802f4984b90189299fc09a1612690445420b10178e1dd59` | 110 |
| `template/.rulesync/subagents/ticket-lead.md` | `8e7dc98b499bc2271b797079afeab5cd2b8712a503dc63c52ade8870b1b758f9` | `fbf5e756c1d1dd2161e181dfa6fb13ee8c4015a10ce4723c15565dc76a610c10` | 44 |

The wheel's committed copy `src/gov/_shipped/template/governance/kernel/skills/judging-work/SKILL.md` (not a kernel
file; the wheel's package data) is the same bytes, `3fd8864b…`.

## 4. The lines that change in the role files, the template and the mirrors

Each file changes only the lines shown; `judging-work` is appended (membership, not position). P-GOLDEN-RULE-1
section 4 sketched `audit, judging-work, retrieval` for the auditor; the bytes here append it (`audit, retrieval,
judging-work`), which the owner approves by the sha256 above.

| File | Before | After |
|---|---|---|
| `roles/independent-auditor.md` line 7 | `- **Skills:** audit, retrieval` | `- **Skills:** audit, retrieval, judging-work` |
| `roles/qa-engineer.md` line 8 | `- **Skills:** qa-review` | `- **Skills:** qa-review, judging-work` |
| `roles/orchestrator.md` line 7 | `- **Skills:** orchestration, planning, checkpoint, change, retrieval` | `- **Skills:** orchestration, planning, checkpoint, change, retrieval, judging-work` |
| `roles/ticket-lead.md` line 7 | `- **Skills:** orchestration, checkpoint, retrieval` | `- **Skills:** orchestration, checkpoint, retrieval, judging-work` |
| `templates/role-reviewer.md` line 5 | `skills: [audit]` | `skills: [audit, judging-work]` |
| `.rulesync/subagents/independent-auditor.md` lines 7, 54 | `skills: ["audit"]`; `- **Skills:** audit, retrieval` | `skills: ["audit", "judging-work"]`; `- **Skills:** audit, retrieval, judging-work` |
| `.rulesync/subagents/qa-engineer.md` lines 7, 17 | `skills: ["qa-review"]`; `- **Skills:** qa-review` | `skills: ["qa-review", "judging-work"]`; `- **Skills:** qa-review, judging-work` |
| `.rulesync/subagents/orchestrator.md` lines 7, 91 | `skills: ["orchestration"]`; `- **Skills:** orchestration, planning, checkpoint, change, retrieval` | `skills: ["orchestration", "judging-work"]`; `- **Skills:** orchestration, planning, checkpoint, change, retrieval, judging-work` |
| `.rulesync/subagents/ticket-lead.md` lines 7, 16 | `skills: ["orchestration", "checkpoint", "retrieval"]`; `- **Skills:** orchestration, checkpoint, retrieval` | `skills: ["orchestration", "checkpoint", "retrieval", "judging-work"]`; `- **Skills:** orchestration, checkpoint, retrieval, judging-work` |

The mirrors' `claudecode.skills` is what preloads a generated agent (`.claude/agents/<role>.md`'s `skills:`).

## 5. The product code beside the kernel files (for the review; not kernel)

| File | What it does |
|---|---|
| `src/gov/brief/judging.py` (new) | Finds the installed skill file (`template/` present: `template/governance/kernel/...`, else `governance/kernel/...`), reads its version (top-level `version`, else `metadata.version` for rulesync's generated form), cuts sections 1 to 3 by their exact heading lines, and refuses `BRIEF_JUDGING_RULE_MISSING` when the file, the sections, the preloaded copy `.claude/skills/judging-work/SKILL.md` or an equal version is missing |
| `src/gov/brief/build.py`, `command.py`, `__init__.py` | A judging brief (`independent-auditor`, the new `qa-engineer` choice on the `role-reviewer` template, `lead --run review`) gets one line `Judging work: the judging-work skill, version <v> (sections 1 to 3 of <path>, verbatim):` and the section bytes, added after the placeholders are filled so they are never edited |
| `src/gov/launch/role.py` | `read_role` refuses `LAUNCH_JUDGING_RULE_MISSING` for `independent-auditor` and `qa-engineer` when the role file's Skills line lacks `judging-work`, the preloaded copy is missing, or its version differs from the kernel file's; ahead of the generic `LAUNCH_REFUSED` |
| `src/gov/adopt/fabric.py`, `pyproject.toml`, `src/gov/_shipped/.../judging-work/SKILL.md` | The skill in `KERNEL_FOLDERS` (target `.claude/skills/judging-work`) and so in `PACKAGED` and A9's install; the wheel carries it |

## 6. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended; DEC-1204: "Both today, top priority") | Merge the kernel files with the product code; the class (b) ACT applied with the merge writes this repository's generated copies (section 7) | Twelve kernel files, eleven of them one or two lines; the copies ACT; the other suites' fixtures that plant judging roles or briefs (section 7) |
| Defer | Keep the hand-pasted golden-rule paragraph in every judging brief (the CTO's interim, P-GOLDEN-RULE-1 section 6) | Reviews keep depending on a paste; nothing checks it; EXAMIN and later products do not receive the rule through the kit |
| Re-baseline | Put the rule into the `audit` and `qa-review` skills instead of a new skill | Re-opens DEC-1204's one-skill decision and two skills in force; the orchestrator and lead (moderators) would not preload it |

## 7. Impact

| Area | Impact |
|---|---|
| Kernel | One new skill; four role files' Skills lines; the reviewer template's skills list; their rulesync mirrors. No hook, guard or permission changes; the rule never lowers a wall (DEC-1204's text) |
| Launch and brief here | Once merged, `gov launch independent-auditor|qa-engineer` and `gov brief independent-auditor|qa-engineer|lead --run review` refuse in this repository until `.claude/skills/judging-work/` exists; `gov launch orchestrator|ticket-lead` refuses with the generic `LAUNCH_REFUSED` (a named skill not loadable). So the class (b) ACT goes with the merge, not after it |
| The class (b) ACT (this repository's generated copies) | Copies `template/.rulesync/skills/judging-work/SKILL.md` to `.rulesync/skills/judging-work/SKILL.md` and `template/.rulesync/subagents/{independent-auditor,orchestrator,qa-engineer,ticket-lead}.md` to `.rulesync/subagents/`, then generates `.claude/skills/judging-work/SKILL.md` (rulesync's form, sha256 `2604d284…` on a scratch clone) and `.claude/agents/{the four}.md` (only the `judging-work` lines change). Rehearsed on a scratch clone at `8ec12d149e9c`: `gov adapters generate` keeps the four agent files unless they are removed first, and also merges CLAUDE.md, AGENTS.md and `.claude/settings.json`, which the ACT must not take (ACT-GOLDEN-RULE-1 owns CLAUDE.md and AGENTS.md) |
| Other suites | See the lead's return: the cases red on this branch, those the ACT turns green, and those that need fixture changes by their owning tickets |
| EXAMIN | Receives the text by REPLIES.md meanwhile (P-GOLDEN-RULE-1 section 5 (a)); its copy gets the product in the release carrying this ticket |
