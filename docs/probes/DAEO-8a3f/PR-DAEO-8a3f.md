---
type: probe
task: DAEO-8a3f
reviewer_session: aa5e31e2-c8a5-4aab-b986-0cd13daab9af
implementer_session: not recorded
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 4916311219bda0a224e6874caf33f093c529f008
decisions_applied: DEC-1052, DEC-1073, DEC-1010, DEC-801
---

# Probe record: W2-158 (DAEO-8a3f) gov check --structural, STANDARD review, round 1

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (Opus, high, class C2) launched by W2-158's lead through
  `launch_worker.sh` (log `~/gov-os-worktrees/W2-158/.gov-runtime/scratch/lead/log/rev-1.json`, brief
  `.../lead/briefs/rev-1.md`), on head `4916311219bd` of `w2/W2-158` (the ticket's work plus w2/integrate merged at
  0aec6e10c). Round 1 of at most 2 (DEC-1010). The sandbox trial file stayed absent. The tripwire showed changes only
  in other trees (the queue's landing to 010399309d69, W2-115, W2-146 and W2-159 leads), none in W2-158.
- **Verdict PASS.** Every line S1-S5 and F1-F4 passes. 0 blocking, 1 major (F-1), 4 minor (F-2 to F-5); no finding
  fails open or loses work (DEC-801): the pass gates nothing.
- **F-1 (major, S4).** `git diff --name-only <base>..HEAD` with rename detection hides a kernel role, skill or hook
  file moved out of its folder, so portability reads `skipped (no such change)`; the fix is `--no-renames`. A missed
  notice, never a refusal. Not fixed in this ticket: it is a row for the CTO (a one-flag fix with a planted `git mv`
  case; the reference tool `structural_pass.py:184` has the same gap).
- **F-2 (minor, S3/F1).** Under `| head -1` a closed stdout ends the pass with exit 120 and a BrokenPipeError
  traceback, not 0. No gate reads it. A row (catch BrokenPipeError around the prints).
- **F-3 (minor, S5).** Links gets its own full bound after the families, so the worst case is about twice the bound;
  the reading L7 states it. Measured well inside the limit on this repository. A row.
- **F-4 (minor, S1).** A declaration with no `family` and an id starting `skill-regression` counts as skills (the
  engineer's recorded reading 3). Today's declarations all carry the field. A row.
- **F-5 (minor, S5).** Settled: the lead's main-tree measurement is in `docs/changes/W2-158-evidence.md` (9.37 s on
  010399309d69 without a base; the reviewer's 19.66 s with a base on a clone of the head).
- **The lead's verify of this head.** `lead_verify.sh`: 4220 tests, 6 failed, all six W2-96 signal cases in
  `tests/unit/accept/test_w2_96_{run2,review3,review4}.py`; re-run alone on this head and on w2/integrate's head
  010399309d69: the same 17 of 20 parametrised cases fail on both (a shared base red, not this ticket's; logs
  `.../lead/log/basered-{head,integrate}.txt`). Every W2-158 case green. `gov accept W2-158`: pass, 61 passed, 0
  failed, all nine KPI lines.
- **Judgement: pass.** No new round. F-1 to F-4 go as rows to the CTO.

## The reviewer's record (as returned)

task: DAEO-8a3f (W2-158), independent audit (STANDARD review, round 1 of 2), head `4916311219bd`

status: DONE

work_completed: **Step 0:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-8a3f`. `rev-parse HEAD` gave `4916311219bda0a224e6874caf33f093c529f008`. The sandbox trial write failed as expected (`OSError: [Errno 30] Read-only file system`) and no file was made. **Audit:** I read the ticket's KPI lines S1-S5 and F1-F4, the lead's readings L1-L10, `structural.py`, the `command.py` diff, the dispatch in `main.py`, `gov links`, the evidence and both test sets. I probed planted trees under my TMPDIR, re-measured the pass on a clone of the head, and ran five mutations of the fail-open paths on mirror copies.

files_changed: none. `git status --porcelain` is empty in the worktree.

evidence:
- **S1 / F3, sound:**
  - Each family is looked up by `id` in `template/governance/kernel/checks`, then in `governance/kernel/checks` (`structural.py:93-133`). No family has a built-in command.
  - A family with no declaration reads `skipped (no declaration)`.
  - Every command is started at once, one thread and one process each, each in its own session (`structural.py:147-148, 257-260`).
  - At the bound, `os.killpg(SIGKILL)` kills the whole process group, then the pipes are closed. The pass never waits past the bound for one command.
- **S2 / F2, sound:** a timed-out command reads `NOTICE not measured: ...`. A command that cannot start, an unreadable YAML file or a file with no string `command` makes only its own family a NOTICE. I found no exception path between the families' handling and the result.
- **S3 / F1:**
  - "no folder" gives exit 2 with the reason on stderr; I planted it.
  - Searching `src` for `structural` finds only `src/gov/check/{structural,command}.py` and a docstring in `graph.py`. Nothing in close, launch or queue calls it.
  - Plain `gov check` and `--list` take the same path as before.
- **S4, mostly sound:**
  - A deleted role file runs portability (planted).
  - A base that does not resolve runs portability and gives `links: NOTICE gov links could not run`.
  - Without a base, both are left out and named.
  - Exception: a role file moved out of the kernel skips portability (F-1).
- **S5, sound:**
  - Git reads use `git --no-optional-locks`, and children run with `PYTHONDONTWRITEBYTECODE=1`.
  - Re-measured on a `--shared` clone of `4916311219bd` with base `HEAD~3`: wall time 19.66 s, exit 0, against a limit of 60 s.
  - The only file written was `.gov-runtime/links/mark`, with no `__pycache__`.
- **F4, sound:**
  - The scoped diff lists `src/gov/check/{command,structural}.py`, `tests/unit/check/test_w2_158_structural.py`, `docs/changes/W2-158-evidence.md` and `tests/acceptance/W2-158/*`.
  - The acceptance tests changed only in `92590dae7` (Role: independent-test-designer) and in its merge commit `c963ec71a`.
- **Product names:** no `w2/`, `integrate`, `DAEO-` or CTO tool path appears in `structural.py`.

tests:
- `tests/acceptance/W2-158` plus `tests/unit/check/test_w2_158_structural.py`, run through `heavy_slot.sh` (TMPDIR set to the sandbox's own, because `/tmp` is read-only; `-k` filter as in the brief): **89 passed, 16 deselected in 38.98 s.**
- The first attempt was stopped by the 10-minute background time limit while still queued for a slot, before any test ran. The re-run above is the result.
- I did not run S5's real-repository timing case under pytest. The manual re-measure above covers it.
- **Mutations: all five caught by the acceptance tests.** I confirmed by hand that m2 and m3 failed for the planted reason.

| mutation | planted change | caught by |
|---|---|---|
| m1 | a timeout reads ok | `test_f2_a_timed_out_family...` |
| m2 | exit 1 on a notice | `test_s3_a_failing_planted_check...` (`assert self.code == 0`) |
| m3 | built-in command when no declaration | `test_f3_a_tree_with_no_declaration_at_all...` (the built-in printed `schema: ok`) |
| m4 | portability always runs | `test_s4_a_change_elsewhere_skips_portability...[docs/readme.md]` |
| m5 | only the child is killed | `test_s1_a_check_past_the_bound_is_killed...` (the grandchild outlived the bound) |

discoveries:
- **The configuration loads before the pass.** `gov` loads it first (`main.py:240-242`, DEC-185, every command). An invalid configuration file would end the command with exit 1 before the pass runs, which is neither 0 nor 2. This rule belongs to the command line, not this ticket. I found it by reading the code and did not plant it.
- **Each pass with a base moves the links mark.** `gov links --since <base>` writes the mark at HEAD. A later plain `gov links` then judges from that head, so findings already shown as `links: NOTICE` are not new again. S4 allows this ("writes only links' own mark"), but whoever reads the lines should know.
- **The CTO's reference tool has the same rename gap as F-1** (`structural_pass.py:184`).

risks:
- **F-1:** a change that moves a kernel role, skill or hook file out of its folder reads `portability: skipped (no such change)`, so no notice is given.
- **F-4:** on a loaded machine the pass can last nearly twice the bound.

lessons:
- Path-touch tests that only add files miss git's rename detection. A planted `git mv` out of the watched folder is a cheap case to add to such tests.

proposed_decisions: none

unresolved:
- Whether a family wrongly read "skipped" counts as failing open. I read it as not failing open: no gate reads the pass, and nothing is refused or lost. If the owner reads it as F2's analogue, F-1 becomes blocking. The fix is one flag either way.

recommended_next_action: Land after the lead verifies. Take F-1's one-flag fix and F-2's guard as accepted fixes in this ticket, with no new round (DEC-802). Record F-3 to F-5 as rows. Classification: 0 blocking, 1 major, 4 minor; no round proposed.

```
verdict: PASS
head: 4916311219bd
findings: 5
- F-1 | major | S4 | src/gov/check/structural.py:210 | Portability skips a role moved out of the kernel. Planted: base with template/governance/kernel/roles/eng.md, then `git mv` of it to docs/eng.md and a commit; `gov check --structural base` printed `portability: skipped (no such change)` (should have run). `git diff --name-only base..HEAD` lists only docs/eng.md because of rename detection; with --no-renames it also lists the role path. Smallest fix: add `--no-renames` to the diff call. Ordinary work: yes, because retiring or moving a role file is routine. Consequence: other (a missed notice; no refusal, no lost work). Reversed if the owner rules a wrongly skipped family as failing open (then blocking), or if a planted git mv out of roles runs portability on this head.
- F-2 | minor | S3/F1 | src/gov/check/structural.py:272-285 | A closed stdout ends with exit 120. Planted: `gov check --structural b2 --root <planted> | head -1`, three runs, each exit 120 with a BrokenPipeError traceback (expected exit 0). Smallest fix: catch BrokenPipeError around the prints in run_structural and return 0. Ordinary work: yes, because piping to head is common at a terminal. Consequence: other (a non-zero exit not caused by findings; no gate reads it). Reversed if an exit of 0 is shown under `| head -1`.
- F-3 | minor | S5 | src/gov/check/structural.py:221,273 | Links gets a fresh full bound after the families. So the worst case is about 2 x bound plus git time, and S5's bound + 10 s holds only when the families end well before the bound. L7 reads it this way ("within the bound", each). This repository measured 19.7 s on a clone of the head. Ordinary work: yes, because a family can reach 50 s on a loaded machine. Consequence: other (a slow notice). Reversed by a ruling that S5's limit is a measurement on this repository, not a promise of the pass.
- F-4 | minor | S1 | src/gov/check/structural.py:122 | A declaration with no `family` field whose id starts `skill-regression` counts as skills. The lead's L3 says skills is exactly `family: skill regression`; the evidence records this as reading 3. Ordinary work: no, because today's three skill declarations all carry the field. Consequence: other. Reversed if L3 is read as also allowing the name.
- F-5 | minor | S5 | docs/changes/W2-158-evidence.md:62 | The evidence measures S5 on the W2-158 worktree at head 883ebbf548b0, not on "this repository's main tree" as S5's Verify asks; the lead re-measures. My re-measure on a clone of 4916311219bd: 19.66 s wall, exit 0. Ordinary work: yes. Consequence: other. Reversed by the lead's main-tree figure recorded in the evidence.
```

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": [{"id": "F-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": [{"id": "F-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F-3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F1", "verdict": "pass", "findings": [{"id": "F-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": []}
]}
```

guard_refusals: none. The read-only refusal of the step-0 trial write came from the sandbox and was the expected result, not a guard refusal.
