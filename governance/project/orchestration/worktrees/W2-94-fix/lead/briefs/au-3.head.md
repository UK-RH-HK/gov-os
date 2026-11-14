# W2-94: the narrow independent check of the W2-149 counts-schema pin's one-map revision, the auditor's brief (DAEO-g87r)

You are a fresh, read-only independent auditor under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; read KPI lines S12 and S13 and the ticket body's
"Path case 2026-11-14 18:05" paragraph). This is a **narrow independent check of one test revision only** (DEC-1154,
DEC-1156 (7)): S13 itself was checked and passed at `ff6ba10be89a` (`docs/probes/DAEO-g87r/PR-DAEO-g87r-s13.md`, its
finding F1 being this path case); the fix flow was reviewed at `fac8d2026`. Do not re-review either. You write nothing in
the repository. Your final message is the probe record's body; the lead commits it as
`docs/probes/DAEO-g87r/PR-DAEO-g87r-s13b.md`.

## What you check (head `@HEAD@` of `w2/W2-94-fix`, worktree `/home/usain/gov-os-worktrees/W2-94-fix`, base `f192e50da`)
The CTO's answer to the path case P-W2-94-S13-1 was (a) (DEC-1156 (7), written in the ticket at `02f08dac1`): the ticket
gains `tests/unit/orchestration/test_w2_149_indep_launch.py`, and S12's and S13's "the W2-149 cases pass unchanged" now
read "unchanged except this one entry". The revision: in `test_counts_schema_closes_every_object_and_string`, the
hard-coded `optional` map gains `fix` for the whole schema's root (`id(whole): {"fix"}`, or the file's own form for the
root), because S13 added the optional root property `fix` to
`governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json`. Nothing else in that file or any other
file was to change. It was made by a fresh engineer given only the failing output (session `@ENSESSION@`, commit
`@ENCOMMIT@`). Between `f192e50da` and that commit the branch also holds the merge of `w2/integrate` at `820f5d3ab`
(which brought the ticket's path case `02f08dac1` and other tickets' integrated work); that merge is not under review.

## The three things you confirm, each as findings with the two lines below
1. **The diff is that one map only.** `git diff 820f5d3ab @HEAD@` (the branch's own change since the merge) and
   `git diff f192e50da @HEAD@ -- tests/unit/orchestration/test_w2_149_indep_launch.py` touch only the `optional` map in
   `test_counts_schema_closes_every_object_and_string`, adding `fix` for the root and nothing else; no other line,
   comment, case, import or file of the branch's own changes. Check the commit's trailers too (`Task: DAEO-g87r`,
   `Role: engineer`, `Implements:` only ids in the ticket's `sources:`, all trailers in one final paragraph).
2. **The case still refuses.** The revised case still fails for an unrequired root key other than `fix`, and still
   fails if `fix` itself lost `additionalProperties: false` or a required key of its own (`id`, `code`, `action`). Show it:
   copy the schema into your `$TMPDIR`, change one thing there (for example, add an optional root property `extra`, or
   drop `action` from `fix`'s `required`), and run the case against the copy (the case reads the schema through the
   module's `schema()` helper; point it at the copy by the file's own means, or monkeypatch in a one-off script under
   your `$TMPDIR`); each must turn the case red, and the real schema keeps it green.
3. **The suites pass.** S13's file (`tests/acceptance/W2-94/test_w2_94_s13_counts_fix.py`) and the W2-149 suites
   (`tests/acceptance/W2-149/` and `tests/unit/orchestration/test_w2_149_indep_launch.py`) pass at the head, with the
   W2-173, W2-178 and W2-94 fix-flow unit suites as S12's check.

Run the suites on their planted stand-ins only, from your sandbox's `$TMPDIR`:
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94/test_w2_94_s13_counts_fix.py tests/acceptance/W2-149/ tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_173_indep_launch.py tests/unit/orchestration/test_w2_178_indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
(run it from the worktree; if the slot tool cannot run in your sandbox, run the same pytest without it and say so; a
resource gate's refusal is a wait).

## Walls (hard)
Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder
named `hidden` outside your `$TMPDIR`, any `fixtures/evaluation/examin/visible` or `hidden` folder of any tree, the
owner's EXAMIN copy or EXAMIN's real repository. You need none of them. No GPU, model, network or installs; no real
`claude` session. One simple command per Bash call; longer things in a script file under your sandbox's `$TMPDIR`
(`/tmp` is read-only in the sandbox). Refused twice for the same call by the guard, the sandbox or a hook: stop and say
so; never work around a refusal. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in
different words if the first does not answer.

## How you judge (the committed governance/project/briefs/JUDGEMENT.md, word for word)
