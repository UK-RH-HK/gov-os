---
id: DAEO-kt8e
status: closed
deps: [DAEO-sdhj]
links: [DAEO-sdhj]
created: 2026-11-19T20:00:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-208
tags: [kit, adopt, update, adapters, emergency-2, release-path]
wbs_id: W2-208
title: "The kit after Emergency 2: two deny lines only (git push, sudo) and no allow line the kit wrote, gov update removes the legacy lines, the held-out Read deny retires, and the golden rules head every adopted repository's CLAUDE.md and AGENTS.md and the judging-work skill"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-sdhj]
waits_on: []
allowed_paths:
- template/.rulesync/permissions.jsonc
- template/.rulesync/rules/governance.md
- template/.rulesync/skills/judging-work/**
- template/governance/kernel/settings.json
- template/governance/kernel/skills/judging-work/**
- src/gov/adapters/**
- src/gov/update/**
- src/gov/adopt/**
- src/gov/util/heldout.py
- src/gov/doctor/command.py
- CLAUDE.md
- AGENTS.md
- pyproject.toml
- src/gov/_shipped/**
- .rulesync/skills/judging-work/**
- .claude/skills/judging-work/**
- tests/unit/brief/test_w2_195_inject.py
- tests/unit/launch/**
- tests/acceptance/W1-46/**
- tests/acceptance/W2-88/**
- tests/optin-lifted-breadth.txt
- tests/acceptance/W2-208/**
- tests/unit/adapters/**
- tests/unit/update/**
- tests/unit/adopt/**
- tests/unit/hooks/test_w2_106_template_hook_lines.py
- tests/unit/launch/test_w2_56.py
- tests/acceptance/W1-38/**
- tests/acceptance/W2-17/**
- tests/acceptance/W2-18/**
- tests/acceptance/W2-195/**
- tests/acceptance/W2-56/**
- tests/acceptance/W2-90/**
- tests/acceptance/W2-23/**
- tests/acceptance/W2-98/**
- tests/acceptance/W2-100/**
- tests/acceptance/W2-153/**
est_loc: 500
kpis:
  success:
  - 'K1 After `gov adopt` and after `gov adapters generate`, an adopted repository''s `.claude/settings.json` holds exactly two deny lines, `Bash(git push *)` and `Bash(sudo *)`, and no allow line the kit wrote (EMERGENCY-2 2.4, DEC-1217 (6)). The kit''s sources say the same: `template/.rulesync/permissions.jsonc` has `git push *` and `sudo *` under `bash` as deny and nothing else (no `.tickets/**` edit rule, no `gov launch` allow), and `template/governance/kernel/settings.json` holds no `allow` and no deny other than those two. Verify: a planted repository adopted from the template (rulesync generates its adapters), with and without a `governance/project/held-out.yaml` of two absolute paths: `permissions.deny` is those two lines and nothing else, `permissions.allow` is absent or empty, no line starts with `Read(`; a deny line and an allow line the owner wrote by hand into `.claude/settings.json` before a second `gov adapters generate` are both kept, beside the two. [EMERGENCY-2 2.4, 2.7; DEC-1217 (6)]'
  - 'K2 `gov update` does not put back what Emergency 2 removed, and takes the legacy lines out. After `gov update` from release 0.1.3 and from release 0.1.0 (planted releases standing for each: A''s sources write `Edit(.tickets/**)` and `Bash(gov launch:*)`, A''s project carries the held-out file and the three legacy lines the 0.1.3 update wrote), the repository''s settings hold exactly the two deny lines and no allow line the kit wrote; a deny or allow line the owner added by hand stays (the three-way merge, Q-UPD). The lines removed are known by their exact text: `Edit(.tickets/**)`, `Read(//<path>/**)` for each path of the project''s `held-out.yaml` (the form `Read(/{p}/**)` the old step wrote), and the allow `Bash(gov launch:*)`. The update''s report (the printed report and the update record `governance/updates/<B>.json`) says what it removed: a `settings` entry with `removed`, the list of the lines. Verify: the planted EXAMIN-like project (settings with the three legacy deny lines and the allow, one owner-written deny `Bash(rm -rf *)`, one owner-written allow `Bash(npm test:*)`): `gov update B` exits 0; afterwards `permissions.deny` is `Bash(git push *)`, `Bash(sudo *)` and `Bash(rm -rf *)` and nothing else, `permissions.allow` is `["Bash(npm test:*)"]`, the report and the record list the four removed lines, `git status --porcelain` is empty; a second planted project whose A has no permission source at all and whose settings hold only the legacy lines ends the same; `gov update B --check` names the settings change and writes nothing. [DEC-1217 (6); the owner: "fix gov update so it does not put back the deny lines Emergency 2 removed"]'
  - 'K3 No code path of the kit writes a `Read` deny for a held-out path: `gov.util.heldout.write_read_rules` is retired (no longer defined, nor called by adopt, update, `gov adapters generate`, the adapter check or a hook); `held-out.yaml`, `heldout.load_held_out` and the transcript scan (`gov memaudit`) stay as they are. Verify: with a planted held-out file, `gov adapters generate`, `python3 -m gov.adapters.portability` and `gov update B` leave no `Read(` line in any settings file they touch and do not mention the held-out step; `hasattr(gov.util.heldout, "write_read_rules")` is false; `load_held_out` still returns the paths and still refuses a malformed file with `HeldOutError`; the memaudit scan tests (`tests/unit/memaudit`) stay green. [EMERGENCY-2 2.7; DEC-1217 (6)]'
  - 'K4 The head of CLAUDE.md and AGENTS.md in an adopted repository is the text of `docs/emergency-2/briefs/LEAD-kit-e2.md` (the block under "The head''s text"), generated from `template/.rulesync/rules/governance.md` (front matter kept) by `gov adapters generate`, at adoption and at update, followed by the kernel''s roles as the role files give them today (nine: engineer, independent-test-designer, independent-auditor, orchestrator, product-spec, research, qa-engineer, senior-engineer, ticket-lead, each with the one line of its role file) and no "Proposing changes" section (no kernel file defines that flow for an adopted repository). The old text is gone: no "Guard" section, no "under the guard", no CIT-P or CIT-E, no CAP-33. Verify: a planted repository adopted from the template, then updated to a release B whose head text differs: the generated block of CLAUDE.md and AGENTS.md begins with `# Governance`, holds the four golden-rule bullets in the head''s words (Value first; The threat model; Trust, then catch and correct; How work is judged with its three sub-bullets), the "How we work" and "Roles" sections and the nine roles, and none of the old strings; the project''s own lines outside the block are byte-identical; the two files'' blocks are equal; after the update to B the block is B''s. [DEC-1217 (7)]'
  - 'K5 The `judging-work` skill is shipped to every adopted repository and its text agrees with the head. `template/.rulesync/skills/judging-work/SKILL.md` and `template/governance/kernel/skills/judging-work/SKILL.md` stay byte-equal; the skill carries the threat model (honest mistakes, accidents and drift; not a same-privilege adversary; catch and correct, not prevent), what may block, when a review happens and how reviews converge, in the head''s words where the head states them, plus the Value-first rule; it names no guard, sandbox or permission prompt as in force; its version is raised. Verify: after `gov adopt` and after `gov update`, `.claude/skills/judging-work/SKILL.md` exists, equals the template''s; a check reads the head and the skill and finds, for each of the head''s four rules, the same key phrases in the skill (`honest agent mistakes`, `same-privilege adversary`, `deliberate construction`, `at most two`, `the owner once`); the skill is in the wheel''s shipped list (`pyproject.toml`). [DEC-1217 (7); EMERGENCY-2 3.7]'
  - 'K6 This repository''s own `CLAUDE.md` and `AGENTS.md` gain the line `- **Value first.**` in their golden-rule section, reading: "What matters is tests and code that match the KPIs and the spec and pass green. Everything else, practicality and security work included, must justify itself against that." (the CTO approves this kernel and instruction text by naming it, EMERGENCY-2 3.5), and nothing else in them changes. Verify: `git diff` of each file against the base adds those lines and removes none; the two files'' golden-rule sections stay equal to each other. [DEC-1217 (7)]'
  failure:
  - 'F1 A kit file that names the guard, the sandbox or a permission prompt as in force fails a check by name. The check `KIT_TEXT_GUARD_IN_FORCE` is a finding of the adapter check (`python3 -m gov.adapters.portability`, with a fixed file list: the head `.rulesync/rules/governance.md`, the `judging-work` skill under `.rulesync/skills/` and `governance/kernel/skills/`, `.rulesync/permissions.jsonc`, `governance/kernel/settings.json`); it names the file and the line, exits non-zero. A line that says the guard, the sandbox or the permission prompts are retired (the word "no" or "retired" before it, as the head says "No guard, no sandbox, no permission prompts") is not a finding. Verify: planted copies of the head with "Six roles operate under the guard", with a "## Guard" section, with "inside the sandbox" and with "a permission prompt appears" each give the finding naming the file and line and exit non-zero; the shipped head and skill give none. [DEC-1217 (6); EMERGENCY-2 2.2]'
  - 'F2 An update that would drop an owner''s own deny or allow line fails and rolls back. The legacy lines and the old release''s generated lines are the only lines it may take out of `permissions.deny` and `permissions.allow`; after the settings are regenerated the update compares them with the lines before, and a line that is neither of those and is gone fails the update, naming the line, with the step (`settings`) and the rolled-back tree of every update failure (HEAD as before, every file byte-identical). Verify: a planted update whose regeneration (a fixture `rulesync` that rewrites `permissions.deny` without the owner''s line) loses the owner''s `Bash(rm -rf *)`: `gov update B` exits non-zero naming the line and `settings`, says it rolled back, HEAD and every file are as before and the lock still names A; a normal update keeps it (K2). [Q-UPD; DEC-1217 (6)]'
non_goals:
- 'Scrubbing the guard, sandbox and permission-prompt wording from the kit''s other files (about 45 skills, role files, templates and commands still say "the guard decides"): the F1 check covers the head, the judging-work skill and the permission files only; the rest is a follow-up row for the CTO'
- 'Releasing 0.1.4 and EXAMIN''s update to it (the owner''s); this repository''s own `.claude/settings.json` and `.rulesync/` (not the kit''s)'
- 'Changing `held-out.yaml`, `load_held_out` or the transcript scan'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: ["EMERGENCY-2 2.2", "EMERGENCY-2 2.4", "EMERGENCY-2 2.7", "EMERGENCY-2 3.7", "DEC-1217 (6)", "DEC-1217 (7)", DEC-1204, DAEO-sdhj, docs/emergency-2/briefs/LEAD-kit-e2.md]
acceptance_tests:
  path: tests/acceptance/W2-208/
  author: independent-test-designer (MR-3); written before implementation
track: A
---

# W2-208: the kit after Emergency 2

Written 2026-11-19 by the kit lead from the CTO's brief `docs/emergency-2/briefs/LEAD-kit-e2.md` (DEC-1217 (6) and (7), the owner's words). Class F, on the release path: release 0.1.4 carries it to EXAMIN by `gov update`.

## What is wrong today

1. `gov update` 0.1.3 wrote three deny lines and one allow line into EXAMIN's `.claude/settings.json` (its report 28): `Edit(.tickets/**)`, `Read(//home/usain/gov-os-eval/**)`, `Read(//home/usain/gov-os-workbench/**)` and the allow `Bash(gov launch:*)`. Sources: `template/.rulesync/permissions.jsonc` (the `.tickets/**` edit deny and the `gov launch` allow), `template/governance/kernel/settings.json` (the allow) and `src/gov/util/heldout.py` `write_read_rules`, called by `src/gov/adapters/merge.py` (`generate_into`) and `src/gov/adapters/portability.py` (`_generated_findings`). EMERGENCY-2 2.4: two denies only, `git push` and `sudo`; 2.7: a hidden set is protected by the transcript scan, not by a deny. The kit has no `git push` deny today: it is added.
2. The kit's rules head `template/.rulesync/rules/governance.md` says "Six roles operate under the guard", has a "Guard" section and the CIT-P workflow, and holds none of the golden rules.

## Lead's rulings of 2026-11-19 (on the test designer's two proposals)

- **The skill's version and this repository's copy:** the version is raised (K5) and the launcher requires the installed copy's version to equal the kernel's, so the shipped copy `src/gov/_shipped/template/governance/kernel/skills/judging-work/SKILL.md`, this repository's own `.rulesync/skills/judging-work/` and `.claude/skills/judging-work/` copies and the pins in `tests/unit/brief/test_w2_195_inject.py` (approved sha of sections 1 to 3: the CTO approves the new text by naming it in the brief) move with it.
- **AGENTS.md's preamble:** rulesync writes its own preamble at the top of AGENTS.md; the head is compared from its first `# Governance` line on. The engineer does not strip it.

## Interface (so tests and code agree)

- **The two lines:** `Bash(git push *)` and `Bash(sudo *)` (rulesync writes a `bash` key `"git push *": "deny"` as `Bash(git push *)`, as it does `sudo *` today).
- **Update's settings step:** after `forget_generated` (the old release's generation unmerged) and the pinned gov's `adapters generate`, `gov.update.core` removes the legacy lines by exact text (the held-out ones from the project's own `governance/project/held-out.yaml`, read before the update) from `permissions.deny` and `permissions.allow`, journals the write, and records `settings: {"removed": [...]}` in the report (key `settings`) and in `governance/updates/<B>.json`. It then compares the deny and allow lines before and after (F2). `--check` lists the removal under `settings`.
- **The head:** `template/.rulesync/rules/governance.md` front matter as today (`root: true`, targets claudecode and agentsmd); the head's text from the brief; the nine roles one line each, after it.
- **The check:** `gov.adapters.portability.kit_text_findings(root)` returns findings `{"code": "KIT_TEXT_GUARD_IN_FORCE", "file": ..., "line": ...}`; `main()` runs it for a project that has the head file.

## Closed on its record (the owner, DEC-1219 (4))
W2-208 should not have been a ticket: by the rubric its deny-line work is a fix recorded in `gov update`'s own ticket W2-17 (`DAEO-sdhj`, section "Fix: two deny lines only ...") and its golden-rules head is a chore. The owner's ruling (2026-11-19 about 13:55) did not reach the running lead (a message to a `claude -p` lead is not read), so the work was built and committed here; it is recorded under W2-17 and this ticket is closed on this record. Its acceptance folder `tests/acceptance/W2-208/` stays as the fix's tests.
