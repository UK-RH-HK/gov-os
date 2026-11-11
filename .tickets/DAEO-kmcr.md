---
id: DAEO-kmcr
status: in_progress
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-23
tags: [wave-2, implementation, full]
wbs_id: W2-23
title: Adoption safety on a real repository
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-49o5
allowed_paths:
- src/gov/adopt/**
- src/gov/adapters/**
- template/governance/project/path-map.yaml
- tests/unit/adopt/**
- tests/unit/adapters/**
- tests/acceptance/W1-41/test_w1_41_migration.py
- fixtures/adopt/**
- CLAUDE.md
- AGENTS.md
# .claude/settings.json out of the paths: a launched session cannot edit it (DEC-315), and a change to this repository's own file goes by ACT; the adapter code and the fixtures that merge such a file stay in the paths (the CTO's delegated decision, DEC-1112 (3))
kpis:
  success:
  - 'Rollback never deletes an untracked file it did not create; it refuses or preserves. Verify: a planted fixture with one untracked file created by the user before an adoption batch and one created by the batch: after rollback the user''s file is present byte for byte (or the rollback refuses and names it) and the batch''s file is removed [W2-H036]'
  - 'Adapter generation merges a programme''s own CLAUDE.md, AGENTS.md and .claude/settings.json instead of overwriting them, keeping their order. Verify: a planted programme whose three files each hold its own lines: after generation each file still holds every one of the programme''s lines in the original order plus the generated lines, and none is replaced by the generated file alone [W2-H050, W2-M232, W2-M312, W2-M229]'
  - 'The A8 dependency proof finds every listed citation form. Verify: a planted set holding one citation of each listed form: the A8 proof prints every one of them as found, and a planted citation of an unlisted form is the only one not found [W2-H035, W2-M225]'
  - 'A failed or interrupted batch leaves a resumable record and no half-staged state. Verify: a planted batch that fails at its third step, and one killed between steps: each leaves a record from which the resume command continues at the failed step, and `git status` shows nothing staged [W2-M219, W2-M220, W2-M224]'
  - 'A project without .gitleaks.toml, or with a .gitignore that omits .gov-runtime/, is set up, not refused late. Verify: a planted project with neither the file nor the ignore line: adoption writes `.gitleaks.toml` and adds `.gov-runtime/` to `.gitignore` at set-up, and no later stage refuses for either [W2-M217, W2-M218, W2-M307]'
  - 'Every command and hook works in a repository whose path contains a space (~/EXAMIN APP). Verify: a planted repository in a folder named `EXAMIN APP`: each `gov` command and each kernel hook run there exits as it does in a path without a space, and none prints a word-splitting or path error.'
  - 'A move to a target that no namespace holds is refused before it runs. Verify: a planted move whose target path is in no namespace: the move is refused with a message naming the target, before any file is moved (the tree is unchanged) [W2-M216]'
  failure:
  - 'The fixture''s own instruction files and every untracked file survive an adoption and its rollback byte for byte. Verify: a planted fixture with instruction files and untracked files, sha256 listed before; after an adoption and its rollback the same listing is equal; any difference is named and fails.'
profile: FULL
sources:
- DEC-729
- DEC-1052
- DEC-954
- DEC-315
- DEC-1112
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-23/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- W2-H036
- W2-H035
- W2-H050
list_rows:
- W2-H035
- W2-H036
- W2-H050
- W2-I014
- W2-L181
- W2-L184
- W2-L185
- W2-L186
- W2-L187
- W2-L188
- W2-L189
- W2-L192
- W2-L205
- W2-L264
- W2-L265
- W2-M042
- W2-M214
- W2-M216
- W2-M217
- W2-M218
- W2-M219
- W2-M220
- W2-M221
- W2-M223
- W2-M224
- W2-M225
- W2-M226
- W2-M229
- W2-M232
- W2-M237
- W2-M261
- W2-M277
- W2-M300
- W2-M307
- W2-M311
- W2-M312
- W2-M319
---
# W2-23 Adoption safety on a real repository

**DEC-954:** depends on W2-16 (DAEO-49o5), not W2-18 (Wave 3). It shares src/gov/adopt/ with W2-52 and W2-88, split by file; whichever merges second merges back.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-23), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/adopt/**`, `src/gov/adapters/**`, `template/governance/project/path-map.yaml`, `tests/unit/adopt/**`, `tests/unit/adapters/**`, `fixtures/adopt/**` (new: a repository with its own `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, untracked files, and a path with a space).
- **KPIs, success:**
  - Rollback never deletes an untracked file it did not create; it refuses or preserves [W2-H036].
  - Adapter generation merges a programme's own `CLAUDE.md`, `AGENTS.md` and `.claude/settings.json` instead of overwriting them, keeping their order [W2-H050, W2-M232, W2-M312, W2-M229].
  - The A8 dependency proof finds every listed citation form [W2-H035, W2-M225].
  - A failed or interrupted batch leaves a resumable record and no half-staged state [W2-M219, W2-M220, W2-M224].
  - A project without `.gitleaks.toml`, or with a `.gitignore` that omits `.gov-runtime/`, is set up, not refused late [W2-M217, W2-M218, W2-M307].
  - Every command and hook works in a repository whose path contains a space (`~/EXAMIN APP`).
  - A move to a target that no namespace holds is refused before it runs [W2-M216].
- **KPIs, failure:** the fixture's own instruction files and every untracked file survive an adoption and its rollback byte for byte.

## Interface (DEC-1052; the CTO's delegated decision, DEC-1112 (3), 2026-11-11: the lead's P-W2-23-2 as written, alternatives left out)

1. S1 "rollback": the restore a failed stage or batch runs (`project.restore`, called by `project.commit` and `_batch`), not a new command. It deletes only paths the tool wrote and names in the call; every other untracked path stays byte for byte; an untracked directory does not raise. (Bootstrap.md 2393: "A rollback deletes every untracked, non-ignored file; an untracked directory would make it raise.")
2. S4 "resume command": running `gov adopt --lite --stage A6` again resumes. A failed batch commits the A6 record with `status: failed`, `failed_batch: <n>`, the batches done with their commits and dispositions, and per-run rollback refs (`refs/gov/adoption/rollback/<run-id>/batch-<n>`); refusal code stays `ADOPT_BATCH_FAILED`. A killed batch (moves staged, no commit): the next A6 run finds the staged set equal to a recorded in-progress batch, unstages it to its rollback point and continues there; anything else staged is refused naming the paths (never reset).
3. S5 "set-up": A0 writes `.gitleaks.toml` (the template's text) when absent and adds `.gov-runtime/` to `.gitignore` when not ignored, both in A0's record commit; an existing `.gitleaks.toml` is never touched; A3 and A8 then never refuse for either.
4. S7: A3 refuses `ADOPT_TARGET_UNHELD`, naming each target no namespace holds, before its record is written (tree unchanged); A6 refuses the same before any batch.
5. S2 "adapter generation": a new command `gov adapters generate` (src/gov/adapters/command.py; the CLI finds command modules by folder, so no change to src/gov/cli/main.py), which runs `rulesync generate` into a temporary folder and merges into the project: CLAUDE.md and AGENTS.md keep every programme line in order with the generated text in one marked block (`<!-- gov:generated begin -->` ... `end -->`) after them, replaced in place on the next run; `.claude/settings.json` is merged key by key, the programme's keys and list entries kept in their order, generated keys and hook entries added after, an `env` block merged with the programme's own entries first and no compaction threshold (DEC-838: every session uses its model's full window; W2-M229's 300k entry rests on DEC-636, which DEC-838 superseded; the CTO's P-W2-23-4 (b)).
6. S3 "listed citation forms": the list of bootstrap.md line 2362: a word character or `-` directly before the path or id; backslashes; URL-encoding; another letter case; a path split across lines; a citation of only the store's folder or a glob; `../` followed by only the tail of the path; an id cited in a record's prose. The planted unlisted form (the one that must stay "not found") is the test designer's choice, named in the test.
7. S6 "each gov command and each kernel hook": every name in `gov.cli.main` COMMANDS plus the discovered command modules, each with `--help` and with one real read invocation (status, doctor, retrieve, context --dry-run, adopt --lite --stage A0 on a clean fixture), and the six hooks of `template/governance/kernel/hooks/` fed a minimal event JSON, through the settings' own hook command lines, with `CLAUDE_PROJECT_DIR` holding a space. See P-W2-23-3 for where a fix would land.

- **Delegated (the CTO, DEC-1112 (3), 2026-11-11), run 1's packages:** P-W2-23-1 (a): `src/gov/adopt/stages.py` (already
  inside `src/gov/adopt/**`) may be edited for call sites only, in `a0`, `a3`, `_batch` and `a6` (about 20 lines), the logic
  in a new `src/gov/adopt/safety.py`; W2-52's own change there (`run()` and `STAGE`) is not touched and no hunk overlaps;
  whichever merges second merges back (DEC-954's rule). A narrowing of DEC-954's split by file to a split by function,
  listed in the digest for the owner to overturn. P-W2-23-3 (a): S6 stays; a red whose fix lies outside the allowed paths
  returns as a package naming the file and line.
- **Delegated (the CTO, DEC-1112 (3), 2026-11-11), run 2's packages:** P-W2-23-4 (b): no compaction threshold in the
  merged `env` block (`AUTO_COMPACT = {}`; DEC-838 standing), Interface item 5 reworded above; the S2 acceptance assertion
  revised by the test designer under a Rewrite-Reason. P-W2-23-5 (a): `tests/acceptance/W1-41/test_w1_41_migration.py`
  added to the paths for its one failed-batch case only, revised by W2-23's test designer to read the per-run rollback
  refs (Rewrite-Reason: DEC-866, Interface item 2). P-W2-23-6 (b): the fixture programme moves under
  `tests/unit/adapters/fixtures/programme/` (inside the paths), so no path-map change; `fixtures/adopt/**` stays unused.
