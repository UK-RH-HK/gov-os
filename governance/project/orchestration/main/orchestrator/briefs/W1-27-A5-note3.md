**Resume note (third start of W1-27; read it before the rest, and where it differs from the rest, it holds).** Keep `.gov-runtime/scratch/lead/CHECKPOINT.md` current.

## The second start's result (`ffe0a3fa`) is accepted except for two points

Everything else stands and is not redone: the merge-back `94bc7635`, the schema compatibility, the recovery check, the isolation measurement, the commits and their trailers. The main orchestrator read the code against the KPI lines and found two points. Both are fixed test first (DEC-136), each by a fresh launched worker, in this order: designer (cases red, you check red to the end of the suite), engineer (within the ticket's paths), then you verify.

1. **`gov rebuild` recreates no derived store but the record graph.** KPI line 2: "rebuild recreates every derived store". `src/gov/rebuild/command.py` runs the record loader, then creates three empty lexical tables from a copy of W1-17's table definitions, and then says "skipped" for the semantic and the code index with two constant sentences, whether or not their tools are there. The second start's cases asked only that the tables exist, so empty tables passed. What holds (decided by the main orchestrator under DEC-416):
   - the lexical index is recreated by the code that owns it (`gov.retrieval.lexical.refresh(root)`, which needs only git and the tree); rebuild holds no copy of another module's table definitions; after a rebuild of a project with tracked files the lexical index is fresh (`freshness(root)`), and a case shows it by a search that finds a tracked file's text;
   - the semantic index and the code index are recreated by the code that owns them **when their tool answers**, and are named as not recreated, with the measured reason, when it does not. Rebuild itself still succeeds with nothing but git (failure KPI: "rebuild needs anything not in git"). The designer reads from W1-19's and W1-16's sources which call recreates each; if one has no such call, that is a package, and that store is named as not recreated with that reason;
   - the result names every derived store with what was done to it: recreated, or not recreated and why. A constant sentence is not a measured reason.
2. **`gov doctor` is healthy when a measurement failed.** In `src/gov/doctor/command.py`, `healthy` is true unless a section says "fail" or "drift"; and a section says "unmeasured" both when its component is absent and when its measurement raised an error ("canary runner failed", "cannot check index freshness"). So a doctor that could measure nothing exits 0 and says `healthy: true`. KPI line 1: "non-zero on any failure"; DEC-425: unmeasured is never green. What holds (DEC-416):
   - a section whose measurement raised an error, or whose input exists and cannot be read, is a **failure**, with the error named;
   - a section whose component is not installed in this project (no tool registry, no hook configuration, no `framework.lock`, no index yet) stays "unmeasured" with its reason, does not by itself make the project unhealthy (KPI line 5: a repository with only the kernel installed passes at the minimal level), and the adoption level says so: a project with an unmeasured section is never reported at the top level;
   - the designer checks each of the eleven sections against these two sentences and says, per section, which of its "unmeasured" results is an absence and which was an error.

## Then

- `w1/integrate` has moved since your merge-back by two commits that touch only the register and two ticket files. Merge it once more in one committing command with the trailers (never `--no-commit`); after it `git diff --stat w1/integrate HEAD -- tests/acceptance` lists only this ticket's own files and its own lines in the W1-07 files.
- Verify every suite to its end, the model- and tool-dependent ones alone; `tests/acceptance/W1-17` and `W1-19` must be unchanged and green (rebuild now calls their code).
- Run `gov doctor --json` on this worktree and give its output section by section. The second start's table said "expected for a worktree" for hooks, canaries and `framework.lock`: say for each whether the thing is absent from this repository or only not found by doctor (the canary runner exists since W1-22 and runs on this repository).
- No review round. Return as the steps below say, with the lines of source per file.

---

