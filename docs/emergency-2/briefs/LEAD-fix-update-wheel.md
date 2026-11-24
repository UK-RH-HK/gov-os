# Lead brief: fix I-17, `gov update` refuses its own release's wheel (a fix under W2-17)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10). Use the `systematic-debugging` skill: find the cause before changing code.

## The bug
I-17 in `docs/emergency-2/integration/FINDINGS.md`: in EXAMIN (`/home/usain/gov-os-runs/W2-27/examin`, read only), plain `gov update 0.1.5` refuses: it rebuilds the wheel from the manifest's commit and gets sha256 `e07845c9...`, while the manifest (`docs/releases/0.1.5/manifest.json`) records `9d129a12...`. The cut wheel `~/.local/share/gov-os/wheels/ba09214f2024/gov-0.1.5-py3-none-any.whl` matches the manifest, and `gov update 0.1.5 --wheel <it>` works. Every adopted repository meets it (ASMO OS adopts next). It fails closed and loses nothing.

## What
1. Find why the rebuilt wheel differs (compare the two wheels' file lists, contents and metadata; timestamps, file order, a version or build stamp, a file present at build time and absent from the commit are the usual causes).
2. Fix it at the cause: a reproducible wheel build (so a rebuild from the commit gives the manifest's hash), and/or `gov update` using the release's cut wheel when it is present and its hash matches, falling back to a rebuild. Choose and say why. Never weaken the hash check: a wheel whose hash differs from the manifest is still refused.
3. Failing test first (a fix): a test that rebuilds from a planted release commit and checks the hash, red on the base. Record the fix as a `## Fix:` section in `.tickets/DAEO-sdhj.md` (W2-17, closed) with the line `Fix: I-17 gov update refuses its own release's wheel`, and that trailer on your commits. If the cause is in `gov release` (the build), the fix also goes under W2-16 (`.tickets/DAEO-49o5.md`); say so.

Code area: `src/gov/update/` (wheel resolution only; another lead adds the hook install there: touch only the wheel code), `src/gov/release/` build, `src/gov/install*`. Do not cut a release, re-pin, or touch `~/.local/share/gov-os/` beyond reading.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-fix-update-wheel`, branch `e2/fix-update-wheel` from `w2/integrate`.

## Green
The failing test, then the fix; the unit and acceptance tests of `update`, `release` and `install`; then the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue fix=e2/fix-update-wheel --onto w2/integrate --select`, exactly that list, through the heavy slot (DEC-1244 X-1).

## Return
Branch and head; the cause in two lines with the evidence; the fix and why that choice; the test red on the base and green after; the selected suites' summary lines; reds not yours.
