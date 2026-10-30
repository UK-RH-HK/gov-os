# Decisions in force (after DEC-952 and DEC-953)

Draft of 2026-10-30. One line each. The register is the authority. What DEC-953 lifts: `LIFTED-BY-DEC953.md`. Superseded and spent decisions: `ARCHIVE-SUPERSEDED.md`.

## Working with the owner
- DEC-065: master rules MR-1 to MR-6. The owner decides (MR-6), the builder never writes its own acceptance tests (MR-3), review and audit stay independent (MR-4).
- DEC-220, DEC-093: the orchestrator decides a P2/P3 itself only if it is reversible, agreed, at least medium confidence, and touches no Charter, MR, Contract scope, guard, install, merge or release. Each is listed for the owner to overturn.
- DEC-949, DEC-850, DEC-855: P1s and owner-only decisions are sent as they arise: a package file, then `owner-ping` as the last act, 07:30 to midnight. Only the orchestrator asks the owner.
- DEC-818: a P1 package stands alone, in six parts.
- DEC-925 item 2, DEC-846: every ACT is a file of exact operator commands, and it is pinged. A settings change runs in full on a clone first.
- DEC-945: no paid notifier and no app install.
- DEC-105: a finding against a closed specification gets three costed options: apply now, defer or re-baseline.
- DEC-954: the plan is approved, with amendments. The order ahead (RESUME HERE): ACT 1, the five-rule guard; then the 10 built tickets and the streams; the roles spec first (W2-60b, W2-11, W2-33 and W2-83 wait for its approval); memory for this repository and any adopted repository; the roles; ACT 2, one re-pin; the three layers in new sessions.
- DEC-957: the work order (product-spec, then KPIs to the test designer, the engineer to the spec never to the tests, the QA engineer alone reads both); installs ask only in the CTO's session; the escalation rubric P3/P2/P1/emergency (prompt §0); the domain skill packs in Wave 2; memory's target 95 % (floor 85 %), all seven gaps before ready; a roles research session.
- DEC-955: ACT 1 first: a close refused before ACT 1 waits for it; right after ACT 1 is committed, a handover and a fresh session under the five-rule guard.
- DEC-954 Q1: EXAMIN's copy starts only when K9's entry criteria are met, never because a date arrived. Dates are weekly estimates.
- DEC-954 Q13: the master orchestrator is the CTO; each sub-orchestrator is a Senior Engineer for its stream, with a coordination ticket each, and the CTO's watchers track their state.
- DEC-946 items 6 and 8: nothing else starts (new ideas go to `WAVE_3_PARKING.md`), and lead launches are staggered by 1 to 2 minutes.
- DEC-953 item 8, DEC-954 Q8: three-layer orchestration starts after ACT 2, once memory, the roles and its foundations have landed.

## Closes and testing
- DEC-953 item 1: a ticket closes on the audit's 10 practices (AUDIT-GOV-FEATURES-1 §5), nothing more. No Gov OS feature gates this repo, and nothing is deleted from the product.
- DEC-953 item 5: close W2-71, W2-77, W2-57, W2-03 and W2-26 now, then each ticket as its practices pass.
- DEC-953 item 6: the proof of `gov close` happens on the proving ground (W2-81) and EXAMIN's copy, not by re-closing this repo's tickets.
- DEC-906 item 1, DEC-462, DEC-959 item 7: a fresh independent test designer writes the acceptance tests from behaviour and sources, in parallel with the engineer, both from the spec; the engineer runs them once they are ready. Only the designer commits under `tests/acceptance/`.
- DEC-959: the local merge queue (Senior Engineers approve, the CTO's tool tests the candidate merge, advances only on green); tests run once per level (lead scoped once; QA re-runs nothing; the queue once per batch, skipped on identical code; full only nightly and for core); the QA engineer per stream (core one by one, others in batches of about five); the opaque acceptance runner now; one skill template with three scenarios; domain skills after ACT 2; everything before EXAMIN.
- DEC-953 item 4, DEC-952: one selection tool at every level:
  - workers run their own unit tests;
  - a lead runs its acceptance tests plus the affected set (full only when core code changed);
  - the close runs the same set on the merged commit in a clean worktree;
  - the nightly runs everything.
  Governance files never widen a selection.
- DEC-905, DEC-906 item 3, DEC-954: one full run at a time among closes and leads, under one lock (`/tmp/gov-os-verify.lock`; leads through `verify_lock.sh`, closes first), with `tmp_path_retention_policy=failed`; the nightly takes no lock (DEC-961). Listed for the owner's review (DEC-961 item 4).
- DEC-954 (P-W2-64-1): a test revision the owner names is checked by a scoped run of the corrected tests; the nightly covers the rest.
- DEC-137, DEC-498, DEC-413, DEC-916: a FULL ticket gets a fresh review before merge, at most two rounds (two per declared round). It is re-reviewed only if a later merge resolved conflicts in reviewed files.
- DEC-801 to 803, DEC-808, DEC-809: findings are judged by ADR-0001's two questions, each with its two lines. A "no" becomes a row, never a round. Fixes ride the next resume.
- DEC-221, DEC-951 item 5: tests are proportional to the profile.
- DEC-096: a loop that has not converged after three iterations goes to the owner as a package. The count is never disclosed.
- DEC-944 items 2 and 3: readiness is checked by hand at claim until W2-82. Playbooks per stream.

## The guard
- DEC-953 item 2, DEC-954 (narrowing DEC-820): five rules only, switched on by ACT 1:
  - an implementer never writes acceptance tests;
  - independent reviewers and auditors write only their own review and audit records;
  - no reads of the hidden half of an evaluation set (from any worktree), or of the held-out material;
  - no reads of secrets, and secrets are never printed;
  - no installs without the owner.
- DEC-083, DEC-040: the owner approves and makes every install, and it is recorded in the tool registry.
- DEC-849: a refusal is taken, never routed round, and it is recorded.
- DEC-958: every false refusal by the five-rule hook is recorded (time, form, rule, cost), counted in the daily document, and worked round only by an equivalent form. Three of one pattern, five in a week, or one that stops a lead or a close brings the owner a P1 package with a hook fix.
- DEC-723: agents never write in, list or search `~/gov-os-workbench`. Writing work runs on clones under `~/gov-os-runs/<ticket>/`.

## The nightly
- DEC-953 item 3, DEC-934: a plain full run on the integration head from 02:00, by cron, on committed code. No `gov close` and no gates at night. A missed night goes in the morning package.
- DEC-953 item 3, DEC-938 item 1: a red is investigated at once (re-run alone, traced to its change and cause):
  - a small, clear fix is made on the spot and reported;
  - otherwise it goes to the owner as a P1 with a recommendation.
  A red holds nothing.
- DEC-946 item 9: the nightly is frozen. No new features unless it breaks.

## Memory and briefs
- DEC-953 item 6a, DEC-952: memory first: W2-86, W2-87, the register-as-one-record defect, then W2-55, W2-04, W2-05, W2-06, W2-13 and W2-15a. W2-61 measures after each fix. Memory is never cut.
- DEC-836, DEC-943 item 2: once memory measurably helps, the orchestrator uses it at every resume and before every decision, and the leads use it through their briefs.
- DEC-953 item 6b: W2-60a, W2-60b and W2-11 (roles, skills, briefs) run in parallel with memory.
- DEC-860, DEC-859: never one giant query or context: retrieval is batched, ranked and stacked. The code graph is traversed in pages.
- DEC-838, DEC-839: every session uses its model's full window, on claude-opus-5-5, with its effort set per launch.
- DEC-236, DEC-371, DEC-731, DEC-732: a lead runs one ticket in its worktree, never merges into `w2/integrate`, and never edits tickets or the register.
  - It launches workers with `gov launch` in a background run.
  - Tests use the worktree's own `src/`.
- DEC-793, DEC-943: every return carries the twelve fields and `brief_gaps`. Gaps are fixed the same week.
- DEC-420: an authentication error stops all launches with `AUTH_REQUIRED`.

## Records and commits
- DEC-851, DEC-866: each owner rule is written where sessions read it. A superseding decision marks the old entry at once and sweeps whatever cites it.
- DEC-861: the orchestrator commits the owner's decisions (`Decided-by: owner`) and never pushes. The owner's push is the acceptance.
- DEC-463: the record comes before the change it authorises.
- DEC-819, DEC-887: context is committed, with the raw record on `record/w2`. Secrets, held-out material and derived stores are never committed.
- DEC-953 §5 practices 6 and 10, DEC-893: gitleaks runs on staged content and on close outputs. A seconds-long check (YAML, schema, placeholders) runs before record commits.
- DEC-720, DEC-848: `w2/integrate` is never rewritten, and merges use `--no-ff`. The owner pushes daily.
- DEC-182: commits keep their `Task:`, `Implements:` and `Role:` trailers. Nothing refuses on them.
- DEC-952, DEC-792: RESUME HERE (under 8,000 characters) names this list first. The handover each morning goes to a fresh session.

## Machine and disk
- DEC-898, DEC-902: no launch or full run below 100 GiB or 10M inodes free. Each session has a scratch budget. A sweep runs weekly.
- DEC-942 items 1 and 3: there is no fixed number of leads. A lead launches while the load is below nproc, and a running lead is never stopped.
- DEC-961 (with DEC-947's floor and trip-wire): the machine is shared by capacity alone. The gate counts the memory floor, each running lead at what it uses (at least its working size) and the newcomer; nothing is set aside for a full run that has not started. A full run (a close's, the nightly's, a lead's) checks the gate itself and waits for room. No hold for a waiting close and no night window: closes, scoped runs and leads run side by side as capacity and paths allow. The nightly starts at 02:00, takes no lock and holds nothing.
- DEC-939 item 1: long commands run in the background. A watchdog fires at 07:45 if the package is late.

## Reporting
- DEC-948, DEC-878, DEC-952: every report ends with the five-line block, plus the memory-chain line and the leads' interim results.
- DEC-938, DEC-951 B: one P1-MORNING file and one ping at 07:30. No long foreground work runs from 07:15 to 07:35.
- DEC-941 item 4.3, DEC-930 item 2: one daily document, and the weekly numbers (with ticket growth and drift).
- DEC-953: three milestone reports, each pinged. Between them, the block plus at most five lines.
