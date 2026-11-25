# Lead brief: the 0.1.6 release suite's wall reds (six; a fix under W2-204, from FM-5)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-25. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies** (never open a hidden sets root, never glob `/home/usain/*`, never cut a `gov retrieve` result, list your retrieves in your return, one trailer paragraph with no blank line before `Co-Authored-By`). Decide, never ask (I-10). Use `systematic-debugging`. **This blocks the 0.1.6 patch release: work fast and small.**

## The reds
The release full suite on `7b5650f44` (record `docs/close/nightly/NR-20261125T003933Z-7b5650f44543.json`; junit under `.gov-runtime/nightly/20261125T003933Z-7b5650f44543/`) failed six wall cases after FM-5 (`e2/fix-memaudit-3`, landed `8b00034df`) put a Stop hook into `governance/project/orchestration/tools/`'s wall `settings.json.tmpl` for the writer kind:
- `tests/acceptance/W2-178/test_w2_178_auditor.py::test_s1_the_auditor_s_wall_differs_from_the_base_build_only_by_the_dropped_subtree` and `::test_s1_a_set_with_no_dropped_folder_builds_the_same_auditor_wall_as_before`
- `tests/acceptance/W2-178/test_w2_178_unchanged.py::test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it[writer-round-2]` and `[checker]`, `::test_s1_the_wall_of_a_set_without_a_dropped_folder_equals_the_base_build[writer-round-2]` and `[checker]`
- `tests/acceptance/W2-149/test_w2_149_tree_settings.py::test_s8_the_settings_are_the_template_filled_for_this_wall`
Each says the head's wall differs from the base build in `.claude/settings.json` and `WALL.json`. The lead of FM-5 said the hook is cut out for every kind but the writer and "everything else in the template is byte-identical": the checker and auditor walls show otherwise.

## What
1. The checker's, auditor's and every non-writer wall must be byte-identical to the base build's (settings and manifest): fix the rendering so the cut leaves no trace (whitespace, commas, the template's own hash in `WALL.json` if the test reads it). That is the code's fix (an engineer).
2. The writer's wall differs by the approved Stop hook only: where a test compares the writer wall with the base build byte for byte, the test designer states the one allowed difference (the hook block, and the template hash it changes), naming FM-5 and DEC-1248; nothing else may differ.
3. W2-149 S8: the settings equal the template filled for the wall, the hook included for the writer.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-fix-walls`, branch `e2/fix-walls` from `w2/integrate`. Code area: `governance/project/orchestration/tools/indep_launch.py` and its templates, `src/gov/memaudit/` only if the rendering lives there. Another lead (fix-phase0-reds) works in `src/gov/rebuild*` and the kit hook.

## Green
The seven cases green; W2-178, W2-149, W2-204 folders green; `tests/unit/memaudit` and `tests/unit/orchestration` green; then exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-ma4q=e2/fix-walls --onto w2/integrate --select`), through the heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; the cause in two lines; the seven cases before and after; the selected suites' summary; your retrieves.
