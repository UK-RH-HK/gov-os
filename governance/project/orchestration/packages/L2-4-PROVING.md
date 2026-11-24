# L2-4: Gov OS's own landing onto `gov queue`: the cause, the proving landing, the retirement list

Lead `l2-4-queue`, 2026-11-20. Branch `e2/l2-4-queue`. Owner's decision: L2-4 / DEC-1217 (1), DEC-1223 (9): "Gov OS's own landing
moves onto `gov queue` after one green proving landing; the scratch landing tools retire."

## The cause (two defects, both found by running the landing, neither by a review)

1. **Documents the branch never wrote refused the landing** (the CTO's find, `SELECTION_REFUSED: 6 changed path(s) nothing maps to
   a suite`). `select.scoped` counts the change as everything since the newest green record, plus the ticket's own commits, plus
   `change` (W2-115 S2, `0fb32b21f`; its test `test_s2_an_unmapped_path_merged_since_the_green_base_refuses` pins it for `gov close`).
   `gov queue` runs it in the warm clone at the tested merge, so the range holds what the CTO committed on the base after the green
   record, and a path of it that no suite places refused the landing as if the branch had written it. **The since-green range is the
   intended model of `gov close` (W2-115) and stays; it leaked into the queue, whose KPI (W2-115b, success 1) is "the branch's own
   commits since the integration head as well as the ticket's".** Owning ticket: **W2-115b (`DAEO-j9z6`)**: its allowed paths hold
   `src/gov/queue/**` and `src/gov/close/select.py`, and its non-goals say `select.py` is open to it only for the keyword the queue
   passes, behaviour without it unchanged. Not W2-202 or W2-206 (they build flags and base reds, not the change model). DEC-891's
   places stay as they are: `record_only` is not widened (W2-66 refuses it).
   **Fix:** with `change` given, a path counted only from the green range (neither the ticket's own commits nor `change` wrote it)
   that nothing places is listed under `unplaced_base` (in `select.scoped`'s answer, `--select`'s object, a dry run's `select.json`)
   and every suite it does reach stays selected; a path the landing wrote that nothing places is still refused, naming only itself;
   without `change` nothing changes. Tests first (Opus designer): `tests/acceptance/W2-115b/test_w2_115b_unwritten_paths.py`
   (success 10 to 13, failure 3), `tests/unit/queue/test_queue_select_unwritten.py`. Sonnet engineer: `ea637c1c0`, then `cb621b2da`.
2. **The ticket `DAEO-gr7t` named the whole `tests/acceptance/` as its acceptance folder** and holds `src/gov/**`,
   `tests/unit/**`: every change under those selected the whole tree and was refused `would run the whole of tests/acceptance/`.
   Behind defect 1 it refused every such landing since 2026-11-18, and would have been the CTO's next refusal. No other ticket has the
   shape. **Fix (a record fix under `DAEO-gr7t`, recorded in its file):** `acceptance_tests.path: tests/acceptance/E2-retire-guard/`
   (holds no test, so the ticket holds no suite). Test first (Opus designer): `tests/unit/close/test_live_tickets_name_no_whole_suite.py`
   reads the live tickets.

## The proving landing (scratch clone, never the real `w2/integrate`)

`/home/usain/gov-os-runs/l2-4-proving/repo`: a clone of this branch; `scratch/integrate` = the clone's head plus a planted green nightly
record, a planted open ticket, and, after both branches forked, three documents on the base (a brief, a `STEPS.md`, a `repin.sh`, none
under `record_only`); `proving/fix` (a new module and its unit test, `Task: DAEO-j9z6` + `Fix:`, under the CLOSED ticket) and
`proving/feature` (the test designer's acceptance commit, then the engineer's, `Task: DAEO-prv1`). Planting script:
the lead's scratchpad `plant_proving.sh` (not committed; the plan is in the paragraph above).

`gov queue DAEO-j9z6=proving/fix DAEO-prv1=proving/feature --onto scratch/integrate`, inside the heavy slot:

| | run 1 (`l2-4-proving-run1-base-reds`) | run 2 (`l2-4-proving`) |
|---|---|---|
| exit, `landed`, `culprits`, `refused` | 0, both, none, none | 0, both, none, none |
| selection | 138 suites; `unplaced_base` = the 3 planted documents | the same |
| run (parallel) | 3,494 passed, 4 failed (base reds), 21 skipped | 3,497 passed, 1 failed (base red), 21 skipped |
| acceptance | `W2-115b` 61 passed; the feature's folder 1 passed | the same |
| seconds | merge 0.1, selection 18, acceptance 22, run 1,906, close 0.2, total 1,964 | selection 18, acceptance 24, run 1,987, total 2,047 |
| head | integration moved from the base to the tested merge + two close commits | the same |
| tickets | both `closed`; `docs/close/<id>/CL-<id>.md` and checkpoints written; the fix's close record holds `fix: true`, the line | the same |
| base reds | 4: my planted ticket's `wbs_id` broke the ticket schema on the base (a fixture fault; the queue recorded them as base reds under Q-CLOSE and landed) | 1: `W1-10 test_every_heading_of_this_repositorys_register_is_one_record_and_none_fails` (`DEC-027` and `DEC-974` have no status line), red on `w2/integrate` too |
| after-step | `gov check --structural`: ok; `gov rebuild --integration`: not built in a clone (its store worktree belongs to the real repository) | same |

Also read-only, on the real repository (nothing moved): `gov queue DAEO-j9z6=e2/l2-4-queue --onto w2/integrate --select --root <this worktree>`
exits 0, 242 suites at `w2/integrate` = `844723c60`, `unplaced_base` = the eleven documents the CTO committed since the green record
(briefs, proposals, `release-0.1.4/STEPS.md`, `repin.sh`, `C3-TRIAL.md`, the W2-81 analysis).

## The command for the real proving landing (the CTO runs it on the next branch it lands; this branch is a fit one)

From the main tree (`w2/integrate` checked out, clean), the machine's rule and node on the PATH (W2-66 and W2-05 cases need `openspec`):

```
T=$(mktemp -d); PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=$T PYTHONPATH=$PWD/src \
  bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m gov.cli.main queue DAEO-j9z6=e2/l2-4-queue --onto w2/integrate ; chmod -R u+w $T; rm -rf $T
```

Read-only first: add `--select` (prints the selection, exit 0, moves nothing). Expect about 35 to 45 minutes (the run is the since-green
selection; a fresh green record shortens it). Expect the one base red above (recorded in the close record's `base_reds`, not a refusal).
`DAEO-gr7t` stays closed with its fix recorded in its file; the branch lands under `DAEO-j9z6` (the fix line is read from its oldest
`Task: DAEO-j9z6` commit that carries `Fix:`).

## The retirement list (after the real proving landing; the CTO's call; one chore)

Scratch, git-ignored, `.gov-runtime/scratch/orchestrator/tools/` (lines as of today):

| Tool | Lines | What still calls it |
|---|---|---|
| `land.py` | 387 | `governance/project/orchestration/tools/dispatch/dispatcher.py` (its default landing command, line 2913; `land_running`, the `landing` job kind, lines 223, 870-876; the `land.txt` lines it accepts are `W2-x=<sha>`, a form `gov queue` does not take); `tests/unit/orchestration/test_dispatcher.py` (strings of a stand-in lander, and the DEC-1014 cases on `land.py` and `close_build.py`, lines 942-994, skipped where the file is absent); scratch tests `test_land_r1_21.py`, `test_land_dec1050.py`, `test_dec1045_switch.py`; `hand_merge_check.sh` calls `kernel_gate.py`, not it |
| `select_tests.py` | 384 | `merge_queue.py` (its default `--select-cmd`, line 717); `land.py`, `close_build.py`, `landing_select.sh`, `lead_verify.sh`; scratch tests `test_select_tests_d4.py`, `test_dec1045_switch.py`; `tests/acceptance/W2-97/w2_97_support.py` (a stand-in of its JSON form); `tests/acceptance/W2-66` names it in a comment only |
| `landing_select.sh` | 270 | nothing in the tracked tree; scratch `test_landing_select.sh`; read by records only. It calls `lead_verify.sh`, `landing_check.py` of the operator (`/home/usain/gov-os-operator/install/`) and `select_tests.py` |
| `lead_verify.sh` | 107 | `governance/project/facts.yaml` lines 73-74 (the `lead_verify` command and its check: the facts file is kernel-adjacent, the CTO's); `landing_select.sh`; scratch `test_lead_verify.sh`; `tests/acceptance/W2-56/w2_56_support.py` mentions it in a docstring |
| `close_build.py` | 601 | `dispatcher.py` (lines 224-225, 870-878: the `close_running` and `closing_w2s` tick fields and the `close` job kind); `merge_queue.py` (comments; its attribution and culprit functions are copies); `test_dispatcher.py` (strings and the DEC-1014 cases); scratch `test_close_build.py`, `test_dec1045_switch.py` |
| `structural_pass.py` | 275 | `land.py` (its after-step); scratch tests `test_structural_pass.py`, `test_land_r1_21.py`; replaced by `gov queue`'s after-step `gov check --structural` |
| `verdict.py` | 45 | no live caller (`tests/acceptance/W2-128` and `W2-193` name it in text only) |
| `landing_check.py` | the operator's copy, outside this tree | `governance/project/criticality.yaml` line 21 lists `governance/project/operator/landing_check.py` as C3 (a path that is not tracked any more); `tests/unit/launch/test_w2_184_criticality.py` line 177, `test_w2_201_launch.py` line 245 and `tests/acceptance/W2-201/test_w2_201_s2_criticality.py` line 26 name it as a path example |
| `kernel_gate.py` | 161 | **stays** (the CTO's own list; run by a wrapper of about 20 lines before `gov queue`): called by `land.py` (line 62) and `hand_merge_check.sh` (line 20); scratch test `test_kernel_gate.py` |

Tracked: `governance/project/orchestration/tools/merge_queue.py` (1,374 lines, C3 in `criticality.yaml` line 20) and its README
(`tools/README.md`); callers: `tests/unit/orchestration/test_w2_97_merge_queue.py` (520), `test_merge_queue_base.py` (184),
`test_merge_queue_q1.py` (262), `test_merge_queue_seed.py` (418), `test_merge_queue_speed.py` (280); `tests/acceptance/W2-97/` (7 files); the
two criticality cases `tests/unit/launch/test_w2_184_criticality.py:176` and `test_w2_201_launch.py:244` (the path stays a C3 example; change
the example, not the rule). No product code calls it. TI-2 retires the merge-queue cases at that point.

**Three notes for the retirement chore:** (a) the dispatcher in `tools/dispatch/` is what the crontab runs each minute
(`run_tick.sh`); it launches `tools/land.py` unless `DISPATCH_LAND_CMD` is set, and takes `land.txt` lines of the form `W2-x=<sha>`:
`gov queue` takes `<ticket>[=<branch>]`, so the dispatcher's landing step needs the product's `src/gov/dispatch/landing.py`
(`landing_command` in `governance/project/dispatch.yaml`, which this repository does not have yet) or an adapter line, not only a
changed command; (b) `facts.yaml`'s `lead_verify` entry goes with `lead_verify.sh` (L2-3 (a): the lead runs `gov accept` only);
(c) the retired scratch tools' own tests (`test_*.py`, `test_*.sh` beside them) go with them.
