# P-W2-20-THREAD-BUDGET: a heavy run's child programs stay within its slot's share (KPI proposal, DEC-1003)

For the owner. One decision: add the KPI lines below to W2-20 (`DAEO-r30l`, the machine-wide resource gate, the
product), so every adopted repository's heavy runs keep their child programs within their share. Proposed by the CTO
2026-11-02 ~17:10 under DEC-1038 (4) and the owner's order to map the CTO's gate fix into the product the same day.

## Why
On 2026-11-02 at 16:20 this machine's load reached 76 on 20 CPUs from one landing that the gate had admitted: the
gate caps a run's pytest workers, not the threads its tests' child programs start; W2-69's secret-scan tests each start
gitleaks (Go: every CPU by default), and 31-49 of them held about 10 cores from one slot (incident record
`log/incidents/2026-11-02-1620-T1-cpu.md`). W2-20's KPIs give heavy jobs slots "sized so that the load stays near the
number of processors" but say nothing of what a slot's run may start; any adopted repository whose tests start a
multi-threaded program (Go tools, OpenMP or BLAS libraries, Rust, torch) breaks the gate's promise the same way.

## The CTO's fix (live on this machine once reviewed; the model for the product)
`heavy_slot.sh` exports to every program a slot's run starts a thread budget of max(1, (CPUs / slots) / workers):
`GOMAXPROCS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `RAYON_NUM_THREADS`,
`NUMEXPR_NUM_THREADS`, `NUMEXPR_MAX_THREADS`, `VECLIB_MAXIMUM_THREADS`; inherited values overridden; one setting
overrides the number.

## Proposed KPI lines for W2-20
- success: 'A heavy job''s slot carries a thread budget: every program the job starts (children, grandchildren, xdist
  workers, programs started by its tests) receives the common runtimes'' thread limits (Go, OpenMP, MKL, OpenBLAS,
  Rayon, numexpr, Accelerate) set to the slot''s share of the logical CPUs divided by its workers, at least 1, derived
  from the machine at start (never a number fixed for one machine); a value inherited from the caller does not raise
  it; the configuration file may set it, with its date and source [DEC-1038 (4), DEC-1037 (4)]'
- success: 'Measured, in the evidence: a planted test suite whose tests each start a program that uses every CPU, run
  in one slot, keeps the machine''s busy cores within the slot''s share plus one, where without the budget it does not;
  and its time with the budget against without (no more than 20 % slower on the planted suite) [DEC-1038 (4)]'
- failure: 'A heavy job whose child programs together use more CPUs than its slot''s share because they start their
  own thread pools.'
- A follow-up line, left to the fresh session's engineer brief (CPU sets per slot, `taskset`) and to W2-121: the slot's
  CPU set, so a program that ignores every thread variable is still held to its share.

## Options
(a) Add the three lines to W2-20 now (recommended; W2-20 is in progress, STANDARD; the lines are small and the CTO's
script is the reference). (b) A ticket of its own after W2-20. (c) Defer to Wave 3.
