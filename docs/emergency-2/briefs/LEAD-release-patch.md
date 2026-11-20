# Lead brief: releasing on the owner's behalf, slice (a): the patch release (a new feature ticket, W2-209; the owner, DEC-1223, DEC-1224 (3))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (worktree, the machine rule, memory first, the flow,
trailers, models, **the C3 trial**). Name: `release-patch`; worktree `/home/usain/gov-os-worktrees/E2-release-patch`,
branch `e2/release-patch` from `w2/integrate`. **Do not merge**; the CTO lands it.

**This is a new feature** (DEC-1219 (6): a new ticket only for a new feature; DEC-1223 (6), RB-6 (a)): create its
ticket, W2-209, with the repository's ticket form (copy the shape of a recent ticket such as `.tickets/DAEO-k1us.md`:
id, `wbs_id: W2-209`, `external-ref: W2-209`, `profile: FULL`, `allowed_paths`, `kpis.success`/`failure` each with a
`verify`, `acceptance_tests.path: tests/acceptance/W2-209/`, `sources`, every list value a quoted string where YAML
could read it as a number), status `in_progress`, in your branch. The ticket's body: the spec is
`docs/emergency-2/proposals/RELEASE-ON-BEHALF.md` (approved, DEC-1223); this ticket is **slice (a)**; slice (b), the
automatic update, is a later slice of the same ticket (its KPI lines added when W2-207 allows, DEC-1224 (3)).

**Slice (a), the owner's words (DEC-1224 (3)):** "the patch rule, the gates, `gov release --patch`, the general re-pin
with its rollback, and the push. ... The proving check (G3) uses the kept outputs of the W2-81 run now going. Rehearse
on a scratch clone, then turn the authority file on and tell me." The design's sections to build from: "What a patch
release is" (P1 to P5, RB-7: keep both of P2's third path and P5), "The gates and the cut" (G0 to G4; G2 the full suite
on the exact commit with the weekly tier; G3 the update rehearsal on W2-81's kept repositories, RB-2 (a)), "What the
CTO may run, and where a release lives", "Re-pin and its rollback" (the general re-pin from
`docs/emergency-2/release-0.1.4/repin.sh`, which already carries the five-hook check and the store rebuilds; the
`rollback.sh`; `burned`), "The pushes" (the release push's text, at most 190 characters; `NOTE.md`). Its KPI lines K1
to K10: take the ones slice (a) covers, word them as observable lines each with its verify and failure line.

**Also in slice (a):** the full-suite runner gains the weekly tier as an option recorded in its record (G2 reads it:
today the CTO sets `GOV_TESTS_OPTIN=weekly` by hand); `docs/releases/<X>/kind.json` with a `kind` key (`patch` or
`bigger`), which W2-17's new `gov doctor` `updates` part already reads (`src/gov/update/pending.py`); the authority file
`governance/project/release-authority.yaml` with `patch_releases: off` as committed (G0 refuses while it is off: the CTO
turns it on by a decision-record commit after the rehearsal; you never turn it on).

**The rehearsal (yours, at the end):** on a scratch clone of this repository and a scratch `$HOME` (never the real
`~/.local/bin/gov`, pins or `w2/integrate`): a planted patch (fix commits only, `Fix:` trailers) passes G1, a planted
bigger change (a `docs/contract` edit, a closed feature ticket, a new command, a new schema) is refused by name; with a
planted green record and G3 stood in, `gov release <X> --patch` cuts, re-pins in the scratch `$HOME`, and a planted
failing post-pin check rolls back and marks the release burned. Write the rehearsal's evidence to
`docs/plan/wave-2/w2-209-rehearsal/` on your branch. G3 on real kept outputs needs the W2-81 run now going
(`~/gov-os-runs/W2-81/run-0.1.4/` when its lead finishes): build G3 against its form and test it with the
self-tests' stand-ins; say what remains for the real G3.

## C3 trial (DEC-1222 (2)) — this is one of the two trial tickets
`src/gov/release/**` and `src/gov/close/**` are C3. Test designer **Opus** (`model: opus`, prompt carrying
`Task: <the new ticket id>`); engineer **Sonnet** (no model). Your return gives: acceptance runs from the engineer's
first commit to the first all-green `gov accept W2-209`, each send-back with its cause, the minutes, the cost.

## Order, green, return
Ticket and KPI lines (`Role: orchestrator`, `Class: F`) → test designer (Opus): `tests/acceptance/W2-209/`, red on the
base, README mapping each KPI line (S/F names), `Role: independent-test-designer` → engineer (Sonnet) until `gov accept
W2-209 --root <worktree>` is green → green: `gov accept W2-209`, `gov accept W2-17`, `gov accept W2-16`, `tests/unit/release`,
`tests/unit/close`, `tests/unit/optin`, W2-18 → the rehearsal → return: branch and head; each KPI line with its tests;
the summary lines; the rehearsal's evidence; what G3 still needs from the real W2-81 outputs; the trial figures; reds not
yours. Every commit's trailers in ONE final paragraph.

Not here: slice (b) (the automatic update, the quiet point); `gov update --auto`; turning the authority file on.
