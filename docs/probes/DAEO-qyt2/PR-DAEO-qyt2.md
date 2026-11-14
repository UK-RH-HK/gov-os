---
type: probe
task: DAEO-qyt2
reviewer_session: "independent-auditor 63bde623-33f4-4fd0-b4ad-0f363d973556 (the narrow independent check, STANDARD round 1, launched read-only by W2-185's lead through gov launch, Opus high, class C2, 2026-11-13); not an author of the change"
implementer_session: "engineer en-1 25368ba5-3e09-4b6a-a122-b0ae5653e62a (a0558ff7dfbb08b28cad64ea4b66d68f48259525); test designers td-1 6c4419a7-1872-403c-8e19-820c1fb12428 (58f95c15a, a3a97706d) and td-2 406e76b8-2acd-429b-9a9c-c1d149783b32 (2230cce50); merges e062f921e and 1180e4ec5 by the lead"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 1180e4ec5e13714ba70697ca77d95ff96c9294e4
---

# Probe record: W2-185 (DAEO-qyt2), the narrow independent check, round 1, on 1180e4ec5e13

task: DAEO-qyt2
decisions_applied: DEC-1167, DEC-1163, DEC-971, DEC-805, DEC-1156, DEC-801, DEC-808, DEC-1010

## Scope

A narrow independent check (profile STANDARD, class C2) of the ticket's change since the claim, `git diff
31eab2103..1180e4ec5` (8 files: `template/.rulesync/hooks.jsonc`, `src/gov/adapters/portability.py`,
`tests/unit/adapters/test_w2_185_hooks_exemption.py`, `tests/acceptance/W1-38/w1_38_support.py` and four files in
`tests/acceptance/W2-185/`). It judged six points: S1, S2, S3 and F1 each against its Verify clause with its plants in
copies; scope, non-goals and trailers; and the reds outside the ticket's paths that the change causes. The reviewer's
verdict block below is the reviewer's, copied as returned. The lead writes no verdict over it.

## The reviewer's result, in short (its full return: the lead's `log/au-1.result.md`)

- **S1: pass.** The template's new `postToolUse` entry equals the root's `context_watch.py` entry byte for byte except the
  adopted path `governance/kernel/hooks/` (matcher `Bash`, timeout 10); the `posttooluse.py` entry stays. W2-23's file
  4 passed; an unwired `eighth.py` turns S6 red (`do not reach the seven kernel hooks: ['eighth.py']`).
- **S2: pass.** The exemption is per hook: only the template's entries running `posttooluse.py`, only in `postToolUse` and
  `postToolUseFailure`, and only while the root does not run `posttooluse.py` in that event (DEC-971 item 3's "ending
  when they return with W2-08" made operational). It leaves out strictly less than the old whole-event exemption.
  program_env, W2-05 and the 8 unit cases pass; planted matcher and event drifts give findings.
- **S3: pass.** `HOOK_SCRIPTS` holds the seven hooks; both W1-38 cases pass; with `context_watch.py` removed, both fail.
- **F1: pass.** An extra matcher on the root's `postToolUse` (`HOOKS_MATCHER_DIFFERS`), a template-only `notification`
  event (`HOOKS_EVENT_DIFFERS`), an extra template matcher in `preToolUse` (`HOOKS_MATCHER_DIFFERS`).
- **Scope: pass.** Only the ticket's paths and acceptance folder; nothing under `.rulesync/` or `.claude/` of the root;
  `Task: DAEO-qyt2` on every commit, `Implements:` ids from `sources:` only, `Rewrite-Reason: DEC-1167 (4)` on 58f95c15a.
- **Reds outside the ticket's paths: 18, all decided-behaviour revisions, no defect.** Each is red at the head and green
  at 31eab2103; each assumed one entry in `postToolUse` or the whole-event lift:
  - `tests/unit/gitenv/test_hooks_lifted.py`: `test_a_lifted_event_in_the_template_only_is_no_finding[lifted0]`,
    `[lifted1]`, `[lifted2]`; `test_any_other_event_in_one_source_only_is_still_a_finding_beside_the_lifted_ones[template]`,
    `[ours]`; `test_the_finding_form_is_unchanged` (the lifted entries should run `posttooluse.py`, not `python3 hook.py`).
  - `tests/acceptance/W2-59/test_w2_59_hook_lines.py::test_the_source_holds_the_seven_governance_hook_lines` (8 entries
    reaching the seven hooks); `::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[postToolUse[1]]`
    and `tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py::test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code[postToolUse[1]]`
    (key the import expectation by program: `context_watch.py` imports only the standard library).
  - `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py`: `[PostToolUse-root]`, `[PostToolUse-subfolder]`,
    `[PostToolUse-deep-subfolder]`, `[PostToolUse-outside]` and `TestAProjectFolderWithASpace…[PostToolUse]` (pick the
    guard entry by its guard program).
  - `tests/acceptance/W1-38/test_w1_38_hooks_source.py::TestGeneratedGuardHooks…[PostToolUse]` (compare guard programs).
  - `tests/unit/hooks/test_w2_106_template_hook_lines.py::test_the_settings_line_equals_its_rulesync_source[postToolUse]`
    (pick the entry running `posttooluse.py`).
  - `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the command wrapper]`
    (pair entries by program, skip the exempt entry).

## Findings

Classification: one finding, out of scope, ordinary work yes, consequence other. No blocking finding; no round proposed.

**R1 (out of scope).** The lead's whole-suite run (default selection) named 6 reds outside the ticket's paths; the change
causes 18; the 12 others are parametrised rows the default run leaves out (`rep:` in `tests/conftest.py`) and only the
opt-in suites (`--optin lifted,breadth`) run. The revision list for DEC-1156 (7) must name all 18.
- Ordinary work: yes, because revising exactly the six named lands the branch with 12 reds the next opt-in or nightly run shows.
- Consequence: other (visible reds that fail closed; nothing fails open, no work is lost).

The lead's triage: R1 accepted; the 18 ids go to the CTO in the return's package, for a revision before the land.

## Verdict (the reviewer's, as returned)

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```
