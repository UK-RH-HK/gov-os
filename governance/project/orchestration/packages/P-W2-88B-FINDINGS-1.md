# P-W2-88B-FINDINGS-1 — W2-88b's smoke run: what failed, and what to do with each finding

Short form (DEC-1176 (2): every failure is a finding returned to the owner, never fixed in W2-88b). 2026-11-14,
CTO session 6ff2ee7c. W2-88b closed at 7ccc0bb61 (merge queue). Record: `experiments/W2-88/smoke-run.md`.

**Result in one line:** gov adopt reached all ten stages on both copies (MA, A0 to A6, A8, A9). A9 failed on both,
for two different reasons. Nothing was fixed.

## F-1 — redis, A9, `FABRIC_INCOMPLETE` (code graph not built)
- **What:** `codegraph: RuntimeError: codebase-memory-mcp query_graph failed (exit code 0)`, raised at
  `src/gov/adopt/fabric.py:705-708`. The rebuild's own record lists codeintel as done (22.3 s), so A9's check of the
  graph failed after the build said it was done.
- **Why it matters now:** EXAMIN's A9 (W2-27) builds the same code graph. If the cause is the repository's language
  or layout, EXAMIN's adoption can stop at its last stage.
- **Options:** **(a)** reopen W2-88 (DAEO-2bdu, closed) under DEC-1164 (18) to find the cause and fix it or name the
  condition, with a narrow independent check, **in the same run as P-RELEASE-1's P-1** (same file, `fabric.py`), before
  the release cut. Cost: about 2 to 3 lead-hours on top of P-1's run. **(b)** A Wave 3 row; EXAMIN's A9 finds out.
  Cost: 0 now; risk: a failed A9 on EXAMIN's copy and a second release.
- **Recommendation: (a), confidence ~75 %.** Ordinary work: yes. Consequence: other (refuses; fails closed).

## F-3 — grafana, A9, `ADOPT_GIT_FAILED` (the repository's own `.gitignore`)
- **What:** grafana's `.gitignore:84` ignores `.claude/skills/*`. A9's `git add` of the files gov writes there was
  refused, after 7 h 26 min of A6.
- **EXAMIN:** its copy's `.gitignore` names neither `.claude` nor `governance/` (read just now), so this does not hit
  W2-27.
- **Options:** **(a)** A9 force-adds only the paths it wrote, and lists them in its commit (about 1 h). This overrides
  the repository's own rule. **(b)** MA (or A0) checks the repository's ignore rules against gov's paths and refuses at
  the start with a named code and the rule's line, before any long stage; the repository's owner then decides (about
  1 to 2 h). **(c)** A sentence in the adopt skill only (0.3 h).
- **Recommendation: (b), confidence ~70 %, in the same W2-88 run as F-1.** It fails closed at minute one instead of
  hour seven, and leaves the repository's rule to its owner.

## F-2 — the auditor's verdict path for A5, A7 and A10 is named nowhere
- The first path the lead chose was refused by the guard (run 3); run 4 used `docs/audit/A5-path-map-verdict.md`.
- **Recommendation:** a Wave 3 row (the adopt skill names the path; a kernel change through CIT-P). EXAMIN's CTO
  gets the run-4 path in its notes.

## Observation — A6's time on a large repository
- grafana's A6 took 7 h 26 min. The secret scan ran once per file, serially, at about 2 files a second, in two passes
  (about 3.4 h each), plus 5,729 s of embedding. MA's memory estimate for grafana (38.4 GB) was far above the measured
  peak (6.6 GB), because A9 stopped before its build.
- **Recommendation:** a Wave 3 row (a parallel or batched scan in A6; MA's estimate checked against a finished build).

## Your line
`P-W2-88B-FINDINGS-1: F-1 (a), F-3 (b), F-2 row, A6 row` (or other letters). F-1 and F-3 go into P-1's run, if you
answer before P-RELEASE-1's run starts.
