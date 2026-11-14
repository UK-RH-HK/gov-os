# W2-94 fix flow — the independent review of the launch script's one-question fix flow, the auditor's brief (DAEO-g87r)

You are a fresh, read-only independent auditor under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; its text is at the end). You write nothing in the
repository. Your final message is the probe record's body; the lead commits it as
`docs/probes/DAEO-g87r/PR-DAEO-g87r-fix.md`.

## What you check (head `@HEAD@` of `w2/W2-94-fix`, worktree `/home/usain/gov-os-worktrees/W2-94-fix`, base `340cd0efb`)
The owner decided **DEC-1180 (2)** (P-Q02-RUN-1 (a)): "the launch script gains a one-question fix flow that runs the
owner's approved q02 variant (0703aebf, DEC-1178 (5)) byte for byte unchanged: it stages only `q02.yaml`, the check's
reason code and round 1's sample, and replaces only `hidden/q02.yaml`." The ticket's KPI lines S6 to S12 and failure
lines F4 to F6 state it; the lead made the interface exact (below) before the work started.

- **The change under review:** `git diff 340cd0efb @HEAD@ -- governance/project/orchestration/tools/indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py`
  (engineer commits `e48c99a67`, `560293740` (session `8ad38fe1-a1ed-4122-bb7c-2e684744584f`) and `fac8d2026`
  (session `ccf43198-9304-4f8f-a23e-26ed4e54856b`)).
- **The acceptance cases:** written first by the independent test designer (session
  `da4a1f0a-e7a6-4757-b070-fa7d0d63f36e`, commit `8a6beb7e4`, merged at `94e2ad773`):
  `tests/acceptance/W2-94/test_w2_94_fix_flow.py`, `w2_94_fix_support.py`, the README rows, and the variant fixture
  `tests/acceptance/W2-94/fixtures/EXAMIN-writer-q02-fix.md` (a byte copy of the approved variant, sha256
  `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`).
- **The variant:** read the fixture above in full (front matter; sections 1 to 5).

## Questions to answer, each as findings with the two lines below
1. **Code against the lines.** Does the diff implement S6 to S12 and F4 to F6 exactly? For each line, say where (file
   and line) and whether a case covers it. Name anything the diff changes outside the fix flow (S12: every flow
   without `--fix` behaves as before).
2. **The variant and the flow agree.** Its front matter is accepted as written (no `sample:`; `rounds: 1` and
   `variant_of`); the wall gives it what its section 2 and 3 name (`input/q02.yaml`, `input/verdict.txt`,
   `input/sample.json`) and delivers what its section 5 names (`out/q02.yaml`, `out/result.json`, `out/conflicts.md`
   only on a stop). Also judge this: the variant tells the writer that the **fixed writer brief's** sections 3, 4, 5, 7
   and 9 apply to it in full, but the wall's tree leaves out `governance/project/indep-briefs/**` (the template's
   `tree-exclude.txt`), and only the variant is staged as `brief.md`. Can the walled writer read the fixed brief's
   rules at all? If not, what is the consequence for q02's run, and is it something this ticket's flow could or should
   fix within S7's "exactly three inputs", or a residual for the owner?
3. **Nothing hidden beyond the one question reaches the wall**, its result, its counts, the launch log, stdout or
   stderr (F4): read `plan_fix`, `round1_sample` and the staging in `build_and_run`; check that no other file of the
   set or the sets root is copied, and that the round-1 sample (paths of EXAMIN's tree, from the round-1 run's own
   archive) is the only thing read from the earlier run.
4. **The set is never left changed** except `hidden/<id>.yaml` on delivery (F5): read `deliver_fix`, `pack` and the
   refusal paths (`_after_refusal`); a refusal at any stage leaves every set file byte-unchanged; the old file is in
   the run's tar at `<run>/replaced-hidden/<id>.yaml` and nowhere under the set.
5. **Fail open?** Could a result or an `out/` of an honest but wrong session be delivered when it should be refused
   (S8, S9), or could the flow replace the wrong file?
6. **Points the lead names for your judgement:** (a) `out/conflicts.md` beside a good (not stopped) result refuses 20
   (the KPI lists conflicts.md among the files `out/` may hold; the variant says "only if you stop"); (b) to keep
   W2-149's pinned count of 10 documented `python3 ` lines, the `--dry` usage line was folded into prose and `--fix`/
   `--reason` are hidden from `--help`'s option list (`argparse.SUPPRESS`); (c) the counts schema
   `indep-schemas/indep-counts.schema.json` is closed and outside the ticket's paths, so a fix run's counts (with
   `fix`) do not validate against it (`finish()` logs "counts schema failed"; `--counts-only` of a fix run refuses
   17); (d) `fix` appears in the counts from the argument check on, `action` null until the result passes.

You may run the suites on their planted stand-ins only, from your sandbox's `$TMPDIR`:
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_173_indep_launch.py tests/unit/orchestration/test_w2_178_indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py tests/acceptance/W2-94/test_w2_94_fix_flow.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
(the engineer's run at this head: 187 passed; if the slot tool cannot run in your sandbox, run the same pytest without
it and say so; a resource gate's refusal is a wait). You may copy the script into your `$TMPDIR`, change one thing
there, and point the acceptance cases at the copy with env `W2_94_FIX_SCRIPT=<copy>` to see a case turn red.

## Walls (hard)
Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder
named `hidden` outside your `$TMPDIR`, any `fixtures/evaluation/examin/visible` or `hidden` folder of any tree, the
owner's EXAMIN copy or EXAMIN's real repository. You need none of them. No GPU, model, network or installs; no real
`claude` session. One simple command per Bash call; longer things in a script file under your sandbox's `$TMPDIR`
(`/tmp` is read-only in the sandbox). Refused twice for the same call by the guard, the sandbox or a hook: stop and say
so; never work around a refusal. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in
different words if the first does not answer.

