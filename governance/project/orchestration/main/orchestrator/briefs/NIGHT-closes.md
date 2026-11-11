# The lift's formal closes, prepared: each ticket's acceptance check on integrate now (DEC-1125 (3) (ii))

Read `NIGHT-common.md` first. Role: orchestrator helper, Sonnet high, class C2.

## Why
After the owner's re-pin in the morning the CTO closes the lift's tickets. Run each one's acceptance check now, so the
closes are quick: what passes, what is red and why, which KPI lines are shown met by which cases, and what each
close needs.

## The tickets
From `governance/project/orchestration/packages/LIFT-1/P1-PLAN.md` row P1-13 and DECIDED-NOT-DONE row 97: W2-05
(`DAEO-0z8c`), W2-96 (`DAEO-ouet`), W2-112 (`DAEO-clon`), W2-122 (`DAEO-blwa`), W2-123 (`DAEO-qzrq`), W2-126
(`DAEO-jpr0`), W2-92 (`DAEO-n0wb`), W2-151 (`DAEO-qzca`, LITE, no acceptance folder: closes on its evidence note);
and W2-15a with W2-32 (`DAEO-rd0g`, `DAEO-0pyc`; DEC-1099 (3)) if the records say they close at the lift. Check the
list against P1-PLAN, D5-STATUS, START-NEXT-SESSION §0/§3 and the tickets; say what you added or dropped and why.

## The task
1. Make one clean clone of `w2/integrate` at its head under `/tmp/gov-os-emg-closes/` (`git clone --shared -q`), so
   nothing is written into the main tree. Read the lift tickets' `gov close` route: `src/gov/close/` and
   `gov accept --help`, `gov close --help` (with `PYTHONPATH=<clone>/src python3 -m gov.cli.main`).
2. For each ticket, in order W2-92, W2-05 first (row 97), then the rest: run `gov accept <W2>` from the clone with
   `PYTHONPATH=<clone>/src`, through `tools/heavy_slot.sh`, one at a time, in the background with a wait by pid
   (`tools/proc.sh wait --max <s> --every 30 <pid>`). Record the counts. A red: re-run that case alone; name its cause
   (load, a named red: the warm-query latency DEC-1125 (1), the guard's lifted rules DEC-953, the trailers warning
   DEC-1123 (3), or new).
3. For each ticket: map every `kpis.success` line to the case(s) that show it met (the acceptance README's map, which
   the new reader reads, `93ac67c0b`); a line with no green case is named. W2-151: check its evidence note and
   whether `gov close` takes the evidence route for a ticket without a folder, else note a recorded CTO close
   (delegated, DEC-1112 (3)).
4. Do not change any ticket, status or test. Do not run `gov close` for real (a `--dry-run` or plan mode only, if it
   has one).

## Write
`governance/project/orchestration/packages/LIFT-CLOSES-1.md`: per ticket one short block: the command, the counts,
each red with its cause, KPI lines met / not shown, what the close needs (route, owner step if any), ready yes or no.
A first table: ticket, ready, reds, minutes the close will take. Scratch under `/tmp/gov-os-emg-closes/`. Nothing else.

## Return
The twelve fields, short, with the table. Estimate 1.5-2.5 h (mostly test time).
