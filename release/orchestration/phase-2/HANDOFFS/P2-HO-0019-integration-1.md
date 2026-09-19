# P2-HO-0019 — Repair iteration 1, round 1: integration builder

| Field | Value |
|---|---|
| Handoff | P2-HO-0019 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` **integration builder**, run **P2-AR-0022** — not any round-1 builder |
| Base | the commit your worktree is checked out at (release branch with every round-1 run report and outcome recorded) |
| Branches to integrate (all from base `c6b60bc`) | `phase2/repair-1-ws03` (P2-AR-0016), `phase2/repair-1-ws04` (P2-AR-0017), `phase2/repair-1-ws05` (P2-AR-0018), `phase2/repair-1-ws06` (P2-AR-0019), `phase2/repair-1-ws08` (P2-AR-0020), `phase2/repair-1-ws09-11` (P2-AR-0021), `phase2/repair-1-ws02` (P2-AR-0015), `phase2/repair-1-ws01-12` (P2-AR-0014) |
| Output directory | `release/capability-baseline/repair-1/integration/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0022.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` (integrated tree builds and every suite is green) or `INCOMPLETE` |

## Who you are

A builder. You make the eight round-1 repairs work **together** in one tree. You do not grade them, you do not start
round-2 classes, and you do not wire integration points beyond what is needed to make the union build and its tests pass.
Read `P2-HO-0010-repair-1-common-protocol.md` — its preservation rules, build hygiene and prohibitions apply to you.

## Task

1. Merge the eight branches with `git merge --no-ff`, in the order listed above (WS-3 first: it owns `cli/src/main.rs`
   semantics and the role/guard API every other workstream now runs under).
2. **Textual conflicts.** Resolve as the union of both sides' intent. Known: `cli/src/main.rs`, where several workstreams
   appended `Cmd` variants and `command_name` arms at the same spot.
3. **Every new subcommand registered with WS-3's G0 guard.** WS-3 made unclassified commands refused: every subcommand added
   by other workstreams (e.g. `gov oracle`, `gov artefact`, `gov context verify|show|receipt`, WS-2's scheduler surface) must
   get its correct effect/authority class in `control::COMMAND_GUARDS` / `g0_label`. A read-only command is classified
   read-only; anything that writes governed state gets the authority class the policy requires. Do not classify a mutating
   command as read-only to make a test pass.
4. **Semantic conflicts.** Known from the orchestrator's trial integration of five branches (tests 86/2):
   - WS-9 writes `MPLAN-GOVERNANCE-ADOPTION.consumers` as structured objects while WS-4's `record.schema.json` makes
     `consumers` a relation field of strings — adoption A11 fails with three HIGH `schema_invariants` findings. Resolve so
     both requirements hold (BC-P2-21 edge direction and identity on the WS-4 side; BC-P2-21 catalogue/plan identity on the
     WS-9 side) — e.g. a structured field under a non-relation key, or the relation field carrying ids with the structure
     elsewhere. Do not loosen the schema into accepting anything.
   - WS-4's context packet no longer carries `semantic_candidates`, still listed in `CONTEXT_POLICY.retrieved_fields`,
     so the `context_reproducibility` family reports it. Reconcile the policy and the packet without dropping the
     supplementary retrieval block the policy requires.
   - Expected after WS-3: tests and probes written by other workstreams that relied on the old default-orchestrator role or
     on `--by`-style human answers now fail. Update such **builder tests** to declare the role they need and to answer gates
     through WS-3's owner-signed channel test helpers (`tests/certification/ws03.rs`), never by re-introducing a default role
     or an unauthenticated answer path.
   - WS-2 added `framework/health/SKILL_SCENARIO_CHECKS.yaml`; `framework/KERNEL.yaml` `payload_dirs` does not list `health`
     (WS-2 IP-16), so an installed kernel would lack it. Register it if the union needs it for installed projects, and
     confirm kernel-manifest/lock and `gov kernel verify` stay consistent (this touches the R1-listed kernel payload: run the
     R1 held-out suites, step 5).
   - WS-2 found a race in `kernel::embedded_kernel_dir` (concurrent materialisation of the embedded kernel leaves a corrupt
     cache marked complete) and worked around it on its side by resolving kernel trust before its threads start (WS-2
     IP-15). Its root-cause fix is **round 2** (WS-8), but confirm the integrated tree does not trip it: run the WS-2
     scheduler under concurrency against a cold `~/.cache/gov/kernels` entry (use a private `XDG_CACHE_HOME`).
5. Build and run everything at the integrated tip: `cargo test --lib`, `cargo test --test certification`, the Python plugin
   tests, `cargo fmt --check` on touched files, and **every prior R1 held-out suite unedited**
   (`release/verification/4.1.6-r1{,-2,-3,-4}/evidence/heldout-tests/`). Report counts against the recorded baselines
   (AR-0027 26/3, AR-0029 26/2 with `ho_f` non-compiling, AR-0031 27/7, AR-0033 31/0). AR-0033 `hv_a::a1` is known to fail
   on any tree larger than candidate 4 because it pins 84 files / 740 functions: report it, and run AR-0033's own census with
   only the size assertion removed (in a clearly labelled copy under your evidence directory — never edit the held-out suite
   in place) to show the §6 result.
6. Re-run each round-1 builder's own probe script(s) from its `repair-1/<ws>/evidence/` directory against the integrated
   binary and report any line that passed on that builder's branch but fails integrated (an integration regression).

## Rules

- A change you make to product code must be the minimum that makes the union correct; describe every one in your report
  with the reason (conflict, semantic reconciliation, guard registration, test update).
- Never weaken a check, schema or test to make the union pass; if two repairs genuinely contradict each other, stop that
  item and describe it precisely in the report (the orchestrator routes it).
- `export CARGO_BUILD_JOBS=4`. Commit merges and fixes on your branch; then write
  `release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`, `evidence/`, and your run report naming the
  final work commit. Do not rebase, tag, push, or touch any other branch or worktree.
- Prohibitions as in P2-HO-0010 (no transcripts, task-output stores or auto-memory; no sub-agents; no owner contact).
