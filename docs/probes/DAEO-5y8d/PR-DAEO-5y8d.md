---
type: probe
task: DAEO-5y8d
reviewer_session: independent-auditor 991178a6-c70e-4a74-a116-581f95bacd50 (run 4's narrow check, launched read-only by W2-182's run-4 lead through gov launch, Opus high, class C1, 2026-11-13); run 3's reviewer 3d1a5b33-9322-47bc-9079-77479dfbf12d below; neither an author of the change
implementer_session: W2-182's test designers (run 1, commits 6e3697785 and 498968115; run 2, td-3 f627f541-5763-4a26-9e3c-cc78b6670d71 and td-4 92ae32ec-f43e-43ae-9acb-3629dc24ef13; run 4, td-5 3a4bb44c-66c2-4f39-8cf9-bc4258ca7566 and td-6 d66ec227-3f6f-4bdf-9780-994943883e4e) and the CTO session (f0cb5284d, E (a)'s line, delegated P3; f299a5eb6, its revert)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 5110578c830aeea23c1bfdfbd2fdfd5594764e0b
---

# Probe record: W2-182 (DAEO-5y8d), the narrow independent check, run 3, on f0cb5284d117

task: DAEO-5y8d
decisions_applied: DEC-1163, DEC-1156, DEC-1150, DEC-105, DEC-801, DEC-808, DEC-1010

## Scope

A narrow independent check (profile LITE, class C1). It covers the ticket's change since `2bf4430f4`, read as its own diff
against its merge base with integrate (`git diff w2/integrate...HEAD`, merge base 4233668ea, 14 files, 5 commits:
6e3697785, 498968115, cc7867f93, 10213e3bb, f0cb5284d). It judged four points: each revised case still catches its planted
break; no mark was added; only the ticket's files changed; the README maps every line, and E's line matches the root
form, with E's "portability exits 0" judged against its unchanged findings. The reviewer's verdict block below is the
reviewer's, copied as returned. The lead writes no verdict over it.

## The reviewer's result, in short (its full return: the lead's `log/au-1.result.md`)

- **Point 1, the planted breaks: all six bite.** Each case was green unplanted, red planted and green again after the
  plant was reverted, in a copy of HEAD. B: an unrecorded `frobnicate` command. C: W1-18's retrieval starting the stand-in
  server; W2-123's last failed try not recorded. R: a stand-in status writing into the state folder, and 20/20 passes
  beside 20 busy workers. D: `gov plan` called from `src/gov/check/` and from `src/gov/session_watch_extra/`. E: an unwired
  eighth hook. F: the "until W2-56" line planted back into `role-lead.md`.
- **Point 2: no mark added, no assertion lowered.** Each removed assert was replaced by the decided form.
- **Point 3: only the ticket's files.** All 14 paths are in `allowed_paths`, with no `src/gov/**` change. The trailers
  are as required, with `Rewrite-Reason:` on both rewrites.
- **Point 4: the map is complete** (`gov accept W2-182`: 7/7 lines, 9 passed, 0 unmapped). **E's entry equals the root's
  byte for byte** except the adopted path `governance/kernel/hooks/`. Portability inside `template/` exits 1 with the same
  nine findings before and after the line.

## Findings (the reviewer's, each with its two lines)

- **F-E1.** After E's line, the repository-root hooks drift comparison (DEC-805, `src/gov/adapters/portability.py:350-359`)
  reports `HOOKS_MATCHER_DIFFERS` on postToolUse: the root has `['Bash']`, the template `['Bash', 'Bash']`. The cause:
  `posttooluse.py` was lifted from the root (DEC-971 item 3), and ACT-CONTEXT-WATCH-1 then gave the root a postToolUse of
  its own. `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` goes from green on the
  parent to red on the head.
  Ordinary work: yes, because every unit-suite run and every nightly hits it, with no construction.
  Consequence: other (a new red test; nothing passes that should not, and no work is lost).
- **F-E2.** E's Verify says "`python3 -m gov.adapters.portability` exits 0 on the template". Inside `template/` it exits 1,
  before and after, with the same nine findings (`RULESYNC_VERSION_UNKNOWN` and eight `TEMPLATE_COPY_MISSING`). Those
  findings come from `template/` not being an adopted project. The line adds none there, but the literal clause is not met,
  and at the root the line adds F-E1.
  Ordinary work: yes, because every run of that Verify clause shows exit 1.
  Consequence: other.
- **F-C1.** W2-123's revised case stays green when the rebuild's `retries` list entry is not written. It judges the last
  failed try's record by the stage's reason. The case had the same reach before the revision, so nothing was lowered.
  Ordinary work: no, because the list is still checked by the W2-123 `refresh` cases.
  Consequence: other.
- **F-F1.** The no-lowering case does not see a skip inside a helper the case calls, or an annotated `pytestmark`. The
  ticket's diff carries neither.
  Ordinary work: no, because only this ticket's `gov accept` reads the guard, and the ticket's own diff is clean.
  Consequence: other.
- **F-R1.** The W2-182 README's "Known reds" still says line E is red until the template line lands, which has been stale
  since f0cb5284d.
  Ordinary work: yes, because any reader of the README sees it.
  Consequence: other.

Classification: 5 findings; none in scope, ordinary work yes and fails open or loses work.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F-C1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F-E1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-E2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "F-F1", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F-R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

## The lead's verification on the same head (not a verdict; it stops the land)

- `gov accept W2-182` on f0cb5284d: pass, 9 passed, 0 failed, every line pass.
- The scoped run (`lead_verify.sh`, DEC-968, once): **RED, 5604 tests, 6 failed** in the parallel phase; the serial phase
  was 2/0. Each red was run alone on the head and on its parent 80b19dc16 (without E's line), in clean copies:
  - **Caused by E's line (green on the parent, red on the head), 4:**
    - `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` (F-E1).
    - `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`
      (the same `HOOKS_MATCHER_DIFFERS`).
    - `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist`: W1-38's adopted-project
      fixture copies six hook scripts (`w1_38_support.py:94` `HOOK_SCRIPTS`). The generated settings now name
      `governance/kernel/hooks/context_watch.py`, which the fixture never copied.
    - `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked`:
      the same missing script, run from a subfolder.
  - **Red on the parent too, 2 (their cause is still on w2/integrate 5003357b49e2; the W2-88a close names them red on integrate):**
    - `tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition[]` and
      `tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition`. The generated
      `.rulesync/subagents/orchestrator.md` still carries the "until W2-56" line that b88a76172 removed from the kernel
      template.
- None of the four is in this ticket's allowed paths, and the reviewer's subset run saw only the first. The land waits on
  the CTO's routing of E (the lead's return, PACKAGES).

# Run 4: the narrow independent check of the revert and the README change, on 5110578c830a

task: DAEO-5y8d
decisions_applied: DEC-1163, DEC-1156, DEC-105, DEC-801, DEC-808, DEC-1010

## Scope

The owner chose P-W2-182-E-1 (1) (DEC-1167 (4)): E's template line was reverted on the branch (f299a5eb6, the CTO), and
line E and its template path moved to W2-185 (`DAEO-qyt2`) (95a55bfca). Run 4 merged `w2/integrate` (0abe795e2), and a test
designer changed the acceptance folder's map (0564b50a8, the count fixed in b826e2007, merged by 5110578c8). This check
judged only those two changes. The first was the revert: the template is as it was before E's line, the ticket's own
change stays inside its paths, and the four cases E's line turned red pass. The second was the README: the map runs B, C,
R, D, F and Failure 1 (8 cases); W2-23 S6 is still scanned by Failure 1 and is named as a base red owned by W2-185; the
redirect fires only on a run of the folder alone. Run 3 judged the revised cases B, C, R, D and F, and its record stays
below. The verdict block at the end of this record is the run-4 reviewer's, copied as returned (its full return: the lead's
`log/au-2.result.md`). The lead writes no verdict over it.

## The reviewer's result, in short

- **Point 1, the revert: PASS.** `git diff w2/integrate...HEAD -- template/` is empty. f299a5eb6 removes exactly the 6
  lines f0cb5284d added. The ticket's own change is 14 files, all in `allowed_paths`, with no `template/` and no
  `src/gov/**`. The four cases E's line had turned red (`test_program_env` two hooks sources, W2-05 hooks source, W1-38
  hook stubs, W1-38 any folder) gave `4 passed` on a copy of HEAD.
- **Point 2, the README: PASS.** The folder alone collects 8 and gives 8 passed. With a skip planted on W2-23 S6, Failure 1
  goes red (`... carries ['skip']`, `test_w2_182_no_lowering.py:72`); with that row deleted from the README it goes red
  on `6 >= 7`. A mixed run of W1-32 and the folder collects 53 = 52 + 1. The README's words agree with the ticket and the
  map.

## Findings (the reviewer's)

None.

Classification: 0 findings; none in scope, ordinary work yes and fails open or loses work.

## The lead's verification on the same head (not a verdict)

- `gov accept W2-182` on 5110578c8: pass, 8 passed, 0 failed, 0 unmapped (lines success-1 to success-5 and failure-1).
- The rebuild on 5110578c8: complete, nothing in `not_built`.
- The scoped run (`lead_verify.sh`, DEC-968, once): parallel 5477 tests, 2 failed, 0 errors, 6 skipped; serial 2/0. Both
  reds are outside the ticket's paths and are red on `w2/integrate`'s content:
  - `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`:
    the base red owned by W2-185 (`DAEO-qyt2`), DEC-1167 (4).
  - `tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository`:
    `SCHEMA_UNREADABLE_RECORD` on `docs/changes/W2-98-CIT-P.md`, whose frontmatter is not YAML. The file is byte-identical
    to `w2/integrate`'s (last written by ab2d4fdc9, W2-98), and the ticket's own diff touches nothing under
    `docs/changes/`. Red again when run alone.
  - The four reds E's line caused in run 3 are gone.

## The run-4 reviewer's verdict block

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```
