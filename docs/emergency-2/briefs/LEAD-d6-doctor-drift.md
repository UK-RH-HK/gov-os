# Lead brief: D6, `gov doctor` reports a patch-only CLI/extension gap with exit 0 (a fix under W2-22, `DAEO-xm6l`)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `d6-doctor-drift`; worktree
`/home/usain/gov-os-worktrees/E2-d6-doctor-drift`, branch `e2/d6-doctor-drift` from `w2/integrate`. **Do not merge.**
It rides release 0.1.5. **Models (DEC-1225):** every helper Sonnet; spawn with no `model`.

**The owner's decision, DEC-1227 D6 (a):** a difference of patch version only (same major and minor) between the
Claude Code CLI and the VS Code extension is drift, reported, exit 0; a larger difference still fails (exit 3). Read
`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` rows P1 and A1: `src/gov/doctor/command.py:793-799` makes any
difference `drift` and `:926-929` counts `drift` as unhealthy; the extension auto-updates, so a patch gap is the normal
state; `tests/acceptance/W2-22/` does not exist, so no test caught it.

## The fix lines (failing test first; recorded in DAEO-xm6l's record as a fix, `Fix:` trailer)
- **A1 Patch-only gap: exit 0, named.** Verify (the analysis's A1 verify): `gov doctor` in a scratch repository with a
  stand-in CLI 2.1.329 and extension 2.1.328 and no registry entry: exit 0, the drift named in its output and JSON.
- **A2 Larger gaps still fail.** Verify: CLI 2.2.x against extension 2.1.x (minor), 3.x against 2.x (major), a CLI
  below the minimum, and a CLI sha256 mismatch at the recorded version: each exit 3, `DOCTOR_UNHEALTHY`, the part named.
- **A3 The Contract's words.** Contract v5 CAP-25 ("exits non-zero on drift") and CAP-61.e ("aligned with the
  extension's bundled version") read the other way. Do not edit the Contract: write the exact replacement wording for
  both in your return; the CTO lands it (the owner's D6 (a) is the decision).
- The tests live in `tests/acceptance/W2-22/` (new folder, README map form other folders use, so `gov accept W2-22` reads it).

## Green and return
`gov accept W2-22` green, `tests/unit/doctor` (or wherever doctor's unit tests live), `tests/unit/optin`. Return: branch
and head; A1 to A3 with their tests; the Contract wording; the trial figures (runs to green, send-backs, minutes, cost);
reds not yours.
