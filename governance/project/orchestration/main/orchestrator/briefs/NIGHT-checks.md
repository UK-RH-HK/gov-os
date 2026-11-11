# Anti-drift audit (e, part 1, and f): every deterministic check at the re-pin candidate (DEC-1125 (3) (iii) e, f)

Read `NIGHT-common.md` first. Role: orchestrator helper, Sonnet high, class C1. **Read-only** except your report.

## The candidate
`w2/integrate` head when you start (record it); `src/` is frozen tonight. Other helpers write records in the main
tree: run the checks on a clean clone (`git clone --shared -q` under `/tmp/gov-os-emg-checks/`) with
`PYTHONPATH=<clone>/src`, except the checks that must read the live store or logs.

## The checks (each: command, result line, red or notice with its cause)
1. **gov check** at the candidate (all families; `PYTHONPATH=<clone>/src python3 -m gov.cli.main check --json` or
   its documented form), through `tools/heavy_slot.sh`. Read `product-traceability-trailers` as a warning (DEC-1123
   (3)); name every other red.
2. **The structural pass** (`.gov-runtime/scratch/orchestrator/tools/structural_pass.py <clone>`), all families.
3. **The guard and walls checks:** find the CTO's guard check and walls check tools (`drafts/g14/guard4_check.py`, the
   walls' check for `indep-briefs`/ACT-INDEP-WALLS-1, `tools/` in the orchestrator scratch, `gov guard` subcommands);
   run each read-only form; never install or change a hook.
4. **The call log:** the replay check of the guard's call log (ACT-OPERATOR-2 §8, row 87; find the tool) over the
   last 24 h: refusals, false refusals, anything unexplained.
5. **Memory and retrieval:** the integration store (`/home/usain/gov-os-worktrees/W2-00-store`): its commit against
   integrate's head (fresh? the `reference-transaction` hook refreshes it after every integrate update; if stale, say
   so, do not rebuild); index freshness; path-map coverage (the structural pass's unindexed-path notice, `gov check`'s
   path-map family); `gov links` (count, new since `622e9b741`); the register consistent (ids unique, the version
   table's last row and "Next free id" agree); `python3 -m gov.context.context_check` (expect `0 error(s)`); this
   week's records searchable: three small searches through the live store
   (`gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<q>"`): DEC-1123's trailers ruling, DEC-1125's
   memory audit cadence, W2-155. Report hit or miss for each with the rank.

## Write
`governance/project/orchestration/packages/AUDIT-NIGHT-1/f-checks.md`: a table (check, command, result, red or
notice, cause, who fixes) then a short note per red. Scratch under `/tmp/gov-os-emg-checks/`. Nothing else.

## Return
The twelve fields, short, with the table. Estimate 1-1.5 h.
