# P2-HO-0048 — Repair iteration 1, round 4: residual integration points, continuation of P2-AR-0043

| Field | Value |
|---|---|
| Handoff | P2-HO-0048 (addendum to **P2-HO-0042**, which you also read in full) |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0053** |
| Continues | **P2-AR-0043**, terminated mid-run by a weekly model usage limit (2026-09-19) — not a failure of its work |
| Base | your worktree's commit: `phase2/repair-1-r4-residual` tip `55af199` (its five product commits `e752bed`, `00615f1`, `e5336d9`, `3a384d8`, `34e3725`, plus the orchestrator's recovery commit of that run's report and evidence) |
| Branch | `phase2/repair-1-r4-residual-b` (yours; leave the original branch untouched) |
| Output directory | `release/capability-baseline/repair-1/r4-residual/` (extend it; do not rewrite P2-AR-0043's report) |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0053.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Do not redo P2-AR-0043's work.** Its product commits are in your base and its report
`release/capability-baseline/repair-1/r4-residual/00-REPAIR-REPORT.md` records, per item, what it did and why, with evidence
under `r4-residual/evidence/`. Read that report first, then P2-HO-0042 and the documents it names. Everything it claims is
a builder claim, not an acceptance — as are yours.

## What is outstanding

1. **The unfinished check it named as it stopped (preserve this gap).** INT3-O1 made a plugin registration inside a claimed
   task go through an OS-proposed change transaction. The adjacent path it had not checked: does **`gov tools install`**
   (and any writer of `tools/<id>.yaml`, or of other governed files under the same OS-managed or project-plugin prefixes)
   write governed files that a task close treats the same way — refusing the close for a material change the OS itself
   made, or letting an unattributed write through? Establish the behaviour with a probe, then:
   - if it is refused like INT3-O1 was, extend the same mechanism (Contract v3 K3 auto-triggered impact simulation plus F4's
     authoritative gate, exactly as P2-HO-0042 item 1 states) so the tool installation is change-controlled without the
     worker hand-filing a CIT;
   - if it already behaves correctly, show that with evidence;
   - if closing it needs a trade-off the sources do not make, return `OWNER_DECISION_REQUIRED` for that item alone and
     continue with the rest.
   Cover the writers of `tools/**` in the same way `capabilities/governance.rs` covers registration, and keep the §6 (R1)
   signature/sink duties P2-AR-0043 describes in its §1.4 intact.
2. **`claims.yaml`** for the whole run in `release/capability-baseline/repair-1/r4-residual/claims.yaml`: a `claims:` list of
   `{item, status}` covering every item P2-HO-0042 routed (INT3-O1, INT3-O2, the WS-2/3/4/6/7/8/9 IPs, the optional list)
   plus your own item 1. Derive the statuses from P2-AR-0043's report where it did the work, and mark each claim's `source`
   as `P2-AR-0043` or `P2-AR-0053`. Do not restate its evidence as yours.
3. **Re-establish the run's regression and R1 on your final tree** (the recovered runs were made at `34e3725`, before your
   changes): `cargo build --release` (0 warnings), `cargo test --lib`, `cargo test --test certification` (chunking is fine —
   P2-AR-0043's `evidence/regression/cert-chunk.sh` works; report the union and that it equals the full test list), the
   Python plugin tests, rustfmt on files you touch, and all four R1 held-out suites unedited through a private, uniquely
   named path with the census. Recorded baselines: AR-0027 26/3; AR-0029 26/2 (`ho_f` does not compile); AR-0031 27/7;
   AR-0033 30/1 (the `hv_a::a1` size pin — run its census with only the size assertions removed, in a labelled copy).
   P2-AR-0043 measured lib 265/0, certification 198/0/0, census 123 files / 2329 functions, 0 §6 violations.
4. **A short continuation section** appended to the output directory as `01-CONTINUATION-REPORT.md`: what you verified of the
   recovered work (state plainly that you re-ran the suites yourself), item 1's outcome, your files changed, tests added or
   changed with reasons, your regression and R1 numbers with census, and the remaining integration points for the round-4
   integrator — including anything P2-AR-0043's report lists as not done.

## Constraints

- The parallel round-4 builder **P2-AR-0042** (evidence map, branch `phase2/repair-1-r4-ws01`, completed) owns
  `runtime/src/contracts.rs`, `framework/contracts/**`, `framework/schemas/governance-capability-acceptance.schema.json`,
  `tests/governance/capability-evidence-map.yaml`, `docs/generated/**`. Do not edit those files.
- **Do not rename, remove or `#[ignore]` any existing test**: P2-AR-0042's evidence map names 441 tests by path, and
  `gov contract verify` fails if one moves. New tests are fine; list them in your report so the integrator can map them.
- Availability rule (P2-HO-0031) on everything you touch; new or changed subcommands classified in `COMMAND_GUARDS` /
  `g0_label`.
- `export CARGO_BUILD_JOBS=2`. Commit on your branch only; never check out, merge into, rebase, tag or push any other
  branch, and do not modify the main checkout.
- Do not read any agent transcript or task-output store. `rm` is denied — move files aside and say so.
