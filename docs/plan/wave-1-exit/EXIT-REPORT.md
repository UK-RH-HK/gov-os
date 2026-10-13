# Wave 1 exit report (W1-42, DAEO-gjjf)

Written by the ticket lead of DAEO-gjjf (role orchestrator) on 2026-10-13, at the end of run 5 of the exit run. The form is the one `tests/acceptance/W1-42/README.md` asks for. Kept answers are under `docs/plan/wave-1-exit/evidence/`. The exit criteria are those of `docs/plan/WAVE_1_WBS.md`, section 4.

- **Overall verdict:** NOT MET
- **Commit of the exit run:** this branch `w1/W1-42` at `e08d042d` before the report's own commit; a-dev exit clone at `30996b6` (feature branch) and `2d3d098` (its main); b-dev exit clone at `fc28272`.
- **Why NOT MET, in one line:** the governance share is measured in total on one ticket only (ORION-im02, 4.49 %), ARGUS has no `gov close`, the two scenario retrievals return no evidence in the adopted clone, the doctor exits 3, and the owner's steps B2 part 2 and B3 are open.

The independent exit audit (W1-43, DAEO-03pw) follows this report and judges it. Nothing here is the auditor's verdict.

## Exit criteria

| Criterion | Verdict | Evidence |
|---|---|---|
| 1 Spec-first cycle end to end on both programmes | NOT MET | ORION ran every step and its implementation ticket ORION-im02 is closed by a clean `gov close` (`docs/plan/wave-1-exit/evidence/close-ORION-im02.json`), but its CI did not pass (no remote, three red checks from earlier history) and the merge is the lead's on a throwaway clone, not an owner merge. ARGUS stops at the close: `gov close ARGUS-im01` refused with `CONTEXT_FAILED` (`docs/plan/wave-1-exit/evidence/close-ARGUS-im01-refused.json`); no CI and no merge there. Step by step in the two programme sections. |
| 2 RETR-A-04 and RETR-X-02 are run | NOT MET | Run with `gov retrieve` in the adopted a-dev clone, both return one empty batch, no evidence, `FACET_UNAVAILABLE` (`docs/plan/wave-1-exit/evidence/RETR-A-04.json`, `docs/plan/wave-1-exit/evidence/RETR-X-02.json`): the clone's semantic index stays empty after a full `gov rebuild`. What is shown instead: the scenario cases of W1-21 pass on the test harness's own indexed dev tiers (run 1), and one real retrieval by ids in a-dev gives two batches, 14 items cited by id and hash, one named parent expansion and a valid bundle (`docs/plan/wave-1-exit/evidence/retrieval-a-dev-feature.json`). No synthesis note was needed anywhere (1,652 of 6,000 tokens). |
| 3 MR-3 containment holds | NOT MET | No breach in the exit run: only test-designer commits change the test folders of both clones, every worker session was started by `gov launch` in the sandbox, and the lead wrote no test (`docs/plan/wave-1-exit/evidence/mr3.json`). It is not reported as met because the guard answers allow for the tool `MultiEdit` for every role until the W1-02 round of DEC-685 merges (not on this branch), and because the post-command check undid eleven Bash effects on the acceptance-test folder by two product-spec adoption workers on 2026-10-12, whose cause was not established. The exit auditor judges. |
| 4 Governance share at most 15 % on each programme's run | NOT MET | Not measured per programme. Per ticket (DEC-677): estimated shares 0.95 % to 4.21 %; the measured total exists for one ticket, ORION-im02, 4.49 % (`docs/plan/wave-1-exit/evidence/telemetry-ORION-im02.json`); every other ticket has no close record. The threshold is 15 %. The exit auditor judges this criterion on the section "Governance share" (DEC-677). The two other learning metrics are in "Learning metrics". |
| 5 Independent wave-exit audit against Contract v4 | NOT REACHED | W1-43 (DAEO-03pw) runs after this report; it is in progress and has produced no finding rows yet. |
| doctor `gov doctor` is green on this repository | NOT MET | Exit 3 (`docs/plan/wave-1-exit/evidence/gov-doctor.json`). See "The doctor": version drift alone makes it unhealthy (DEC-667), and in this ticket worktree three more sections fail. |
| canaries the dev tiers' canaries hit, no canary secret in a derived store | NOT MET | In the a-dev clone the lexical canary hits and the semantic canary does not (`docs/plan/wave-1-exit/evidence/gov-doctor-a-dev.json`: semantic `FACET_UNAVAILABLE`). No secret in a derived store was found: the secrets-indexing family is green in both clones' `gov check` (`docs/plan/wave-1-exit/evidence/gov-check-a-dev-before-close.json`, `docs/plan/wave-1-exit/evidence/gov-check-b-dev.json`) and `gov ci staged-secrets` found 0 in a-dev (`docs/plan/wave-1-exit/evidence/ci-a-dev-staged-secrets.json`). b-dev's canaries were not run (b-dev is at A2). |
| check-and-commands `gov check` 17 of 17 families, twelve commands implemented | MET | `docs/plan/wave-1-exit/evidence/gov-check.json` (17 families, 23 checks, none red, at the start of the exit run) and `docs/plan/wave-1-exit/evidence/gov-commands.json`. Today's answer in this worktree is red on two families from a stale store: see "gov check and the twelve commands". |

## Programme ORION

- **Feature:** dimension-checked addition and subtraction in the Python numerical reference (specification ORION-SPEC-DIMADD), and, as a second small feature decided by the owner (DEC-682), the named dimension `ACCELERATION = LENGTH / (TIME * TIME)`.
- **Adoption stage reached:** A8 (a-dev exit clone, stages A0 to A8; A6 and A8 in run 3, `docs/plan/wave-1-exit/evidence/adopt-a-dev-A8.json`).
- **Close result:** clean gov close of ORION-im02 (exit 0, no disposition, no exception). ORION-im01, the first implementation ticket, is open: its one `gov close` refused with `TRAILER_MISSING` and was left without a disposition.

| Step | Result | Ticket ids | Evidence |
|---|---|---|---|
| discovery | done | ORION-sp01 | `docs/plan/wave-1-exit/evidence/launch/a-spec.json`; the owner's answers are DEC-656 and DEC-662 in `docs/DECISION_REGISTER.md` |
| closed specification | done | ORION-sp01, ORION-gp09 | closed at clone commit fb1104a (`docs/plan/wave-1-exit/evidence/a-dev-history.txt`); `gov readiness` answers closed, no open row (the entry readiness of `docs/plan/wave-1-exit/evidence/gov-commands.json`) |
| independent specification audit | done | ORION-sp01 (audit ticket ade-0y1v) | first audit failed on one finding, second audit by a fresh auditor passed: `docs/plan/wave-1-exit/evidence/launch/a-audit.json`, `docs/plan/wave-1-exit/evidence/launch/a-audit2.json` |
| linked gap tickets | done | ORION-gp01 to ORION-gp09 | `docs/plan/wave-1-exit/evidence/a-dev-history.txt` |
| independent tests | done | ORION-gp09, ORION-im02 | 84 cases (930b197) and 43 cases (f49924a), each checked red before the implementation: `docs/plan/wave-1-exit/evidence/launch/a-tests2.json`, `docs/plan/wave-1-exit/evidence/launch/a-im02-tests.json` |
| implementation | done | ORION-im01, ORION-im02 | 13 lines (c7b4818) and 1 line (6a78498) in the reference's dimensions module: `docs/plan/wave-1-exit/evidence/launch/a-eng.json`, `docs/plan/wave-1-exit/evidence/launch/a-im02-eng.json` |
| close | done | ORION-im02 | `docs/plan/wave-1-exit/evidence/close-ORION-im02.json` |
| CI | not reached: `gov ci` ran without a remote and did not pass. `checks G1 G2` exit 3 `CHECK_FAILED` (core-claims, core-schema, product-traceability-trailers, none on ORION-im02's commits), `job` exit 1 `CI_NOT_MEASURED` (openspec not on the runner), `staged-secrets` exit 0; `push` and `record` need a remote | ORION-im02 | the three kept answers are named in the text below |
| merge | done | ORION-im01, ORION-im02 | clone commit 2d3d098 on the clone's main, one committing command, with trailers (`docs/plan/wave-1-exit/evidence/a-dev-history.txt`). It is the lead's merge on a throwaway clone, not an owner merge |

CI answers: `docs/plan/wave-1-exit/evidence/ci-a-dev-checks.json`, `docs/plan/wave-1-exit/evidence/ci-a-dev-job.json`, `docs/plan/wave-1-exit/evidence/ci-a-dev-staged-secrets.json`. The three red checks are 43 trailer findings on commits of runs 1 and 2, and six findings on the repair ticket ade-5rcs, which `gov close` wrote on ORION-im01's refusal without role, allowed paths and KPIs. After the merge the clone's test folders give 127 passed on its main. The programme's own tests of the reference give 31 passed and 1 failed (TestCrossValidation, test_exact_agreement); the case failed before the change too and is not ORION-im02's.

Tickets of the cycle in a-dev: ORION-sp01 (specification), ORION-gp01 to ORION-gp09 (gap tickets), ORION-ad01 to ORION-ad03 (adoption and repair), ade-0y1v (audit), ORION-im01 and ORION-im02 (implementation), ade-5rcs (repair ticket of the refused close). Spec, audit, gap and adoption tickets were closed with the ticket tool and a note (DEC-658).

## Programme ARGUS

- **Feature:** the data retention rule (REQ-004): `retention_decision(kind, created_at, now)` in the pyargus package (specification closed at clone commit ac332e2).
- **Adoption stage reached:** A2: the one worker round DEC-658 allows was not enough to take b-dev further; its legacy records fail the schema (records without type and state class, overlapping ids between its DEC and ADR series, one file in no namespace), so eight check families are red at `fc28272` (`docs/plan/wave-1-exit/evidence/gov-check-b-dev.json`).
- **Close result:** refused. `gov close ARGUS-im01` answered `STORE_STALE` before the gates (exit 1), and after a rebuild `CONTEXT_FAILED` (exit 3): the ticket lists the source REQ-004, which b-dev's store does not hold at A2. Left without a disposition; no further close in b-dev (DEC-674).

| Step | Result | Ticket ids | Evidence |
|---|---|---|---|
| discovery | done | ARGUS-sp01 | `docs/plan/wave-1-exit/evidence/launch/b-spec.json`; the owner's answers are DEC-657, DEC-662 and DEC-666 in `docs/DECISION_REGISTER.md` |
| closed specification | done | ARGUS-sp01, ARGUS-gp09, ARGUS-gp13 | closed at clone commit ac332e2 (`docs/plan/wave-1-exit/evidence/b-dev-history.txt`) |
| independent specification audit | done | ARGUS-sp01 (audit ticket bde-c1yl) | passed with one major finding, PKG-7, left open by the finish line (DEC-674): `docs/plan/wave-1-exit/evidence/launch/b-audit.json` |
| linked gap tickets | done | ARGUS-gp01 to ARGUS-gp13 | `docs/plan/wave-1-exit/evidence/b-dev-history.txt` |
| independent tests | done | ARGUS-gp13 | 65 cases (2db35a4), red before the implementation on the absent module alone: `docs/plan/wave-1-exit/evidence/launch/b-tests.json` |
| implementation | done | ARGUS-im01 | 39 lines and 2 in the README (7b0e68d), 65 of 65 green: `docs/plan/wave-1-exit/evidence/launch/b-eng.json` |
| close | not reached: `gov close ARGUS-im01` refused with `CONTEXT_FAILED`, exit 3; left without a disposition | ARGUS-im01 | the two kept answers are named in the text below |
| CI | not reached: no close; nothing more was run in b-dev (DEC-674) | ARGUS-im01 | no answer exists |
| merge | not reached: no close and no CI | ARGUS-im01 | no merge exists; b-dev's main is at 3b1ad56 |

Close answers of b-dev: `docs/plan/wave-1-exit/evidence/close-ARGUS-im01-store-stale.json` and `docs/plan/wave-1-exit/evidence/close-ARGUS-im01-refused.json`. Tickets of the cycle in b-dev: ARGUS-sp01, ARGUS-gp01 to ARGUS-gp13, ARGUS-ad01, bde-c1yl (audit), ARGUS-im01, bde-0kr6 (repair ticket of the refused close).

## Clean close

- **Ticket:** ORION-im02
- **Kept answer:** `docs/plan/wave-1-exit/evidence/close-ORION-im02.json`
- **Exception:** none

This is the DEC-511 proof in the form DEC-678 option (d) and DEC-682 set: one small new implementation ticket in a-dev, done by the book and closed with one `gov close`.

- **Which change and why it qualified:** the owner decided it (DEC-682): the named dimension ACCELERATION, sourced on MATH-SPEC-003, section "Compound dimensions", accepted by the owner for that one constant. The acceptance is recorded in a-dev's own register as ADR-011 (clone commit 418913b), by the orchestrator in the owner's words, as the kernel's orchestration skill says of an owner answer. The closed specification ORION-SPEC-DIMADD was not edited.
- **By the book:** the ticket was created and started (6c32d15, 47febd0); the independent test designer wrote 43 cases first (f49924a; red at 29 failed, 14 passed, checked by the lead); the engineer wrote one line (6a78498; 43 passed, the 84 earlier cases passed); a checkpoint (82affc9); one `gov close` (94cceae, 30996b6). Every one of these commits carries `Task: ORION-im02`, `Role:` and `Implements: MATH-SPEC-003`; each was checked (`docs/plan/wave-1-exit/evidence/a-dev-history.txt`).
- **The envelope, word for word:** `{"ok": true, "command": "close", "result": {"ticket": "ORION-im02", "close_record": "docs/close/ORION-im02/CL-ORION-im02.md", "checkpoint": "docs/checkpoints/ORION-im02/CP-ORION-im02-0004.md", "test_runs": [{"run": "acceptance", "form": "parallel", "seconds": 5.82, "passed": 43, "failed": 0, "errors": 0, "skipped": 0, "workers": "auto"}, {"run": "regression", "form": "parallel", "seconds": 0.89, "passed": 84, "failed": 0, "errors": 0, "skipped": 0, "workers": "auto"}], "governance_share": {"measured": "not measured", "estimated": "not measured", "total": "not measured"}}, "session": ""}` (the two paths in it are paths of the clone).
- **No disposition, no exception, no baseline entry.** Before the close `gov check` in a-dev exited 3 on three hard-block families, none of them ORION-im02's (`docs/plan/wave-1-exit/evidence/gov-check-a-dev-before-close.json`). The close's governance-checks gate did not run, by the close's own rule: no commit of the ticket touches a governance path.
- **As plainly, the two refusals.** `gov close ORION-im01` refused with `TRAILER_MISSING` on the lead's own commit `540004a` (run 2's commit that created the ticket file, without `Implements:`); it was left without a disposition (`docs/plan/wave-1-exit/evidence/close-ORION-im01-refused.json`). `gov close ARGUS-im01` refused with `CONTEXT_FAILED`; it was left without a disposition (`docs/plan/wave-1-exit/evidence/close-ARGUS-im01-refused.json`). Neither was exit 4. Both tickets are open, with repair tickets ade-5rcs and bde-0kr6.

## Retrieval

Figures of run 1 (2026-10-12), measured on the dev tiers with the real models; kept in `docs/plan/wave-1-exit/evidence/retrieval-hit5.json`, with the two measuring runs' output beside it (`docs/plan/wave-1-exit/evidence/retrieval-w1-19-method.txt`, `docs/plan/wave-1-exit/evidence/retrieval-w1-21-dev-tier.txt`).

| Measure | Figure | Baseline | Comparison |
|---|---|---|---|
| mean hit@5 on the dev query set (52 queries, mean of the 10 classes, W1-19's measure) | 83.33 | 85 | below the S0b2 baseline by 1.67; at or above the pass line of 80 (DEC-414). Through `gov.retrieval.retrieve` the figure is 81.67; forbidden citations in the first five are 2, equal to the baseline |
| callers/impact hit@5 on the code classes (16 queries over tests, callers-impact, where-defined) | 100.0 | 60 | at or above the S0b2 code-intelligence figure for the class; all three code classes together 14 of 16 (87.5) against 75. Same query set and matcher, measured through gov's retrieval and not through the code-intelligence wrapper |

| Query | Kept bundles | Batches | Parent expansions | Synthesis notes | Stopping reason |
|---|---|---|---|---|---|
| RETR-A-04 | `docs/plan/wave-1-exit/evidence/RETR-A-04.json` | 1 (of size 0) | 0 | 0 | `FACET_UNAVAILABLE` |
| RETR-X-02 | `docs/plan/wave-1-exit/evidence/RETR-X-02.json` | 3 (one of size 0 for the missing id; 10 and 4 for the three-location question) | 1 | 0 | `FACET_UNAVAILABLE` |

- **What the two scenario runs show.** In the adopted a-dev clone, `gov retrieve "Which files implement the leapfrog integrator?"` returns no evidence: the semantic facet is "empty" and the lexical facet matches the question as one phrase. A full `gov rebuild` in the clone answered "semantic: recreated" and the facet stayed empty. The missing id DEC-9999 is named as a gap (UNRESOLVED), with no evidence made up. The two cases of the W1-42 suite that read these files stay red for that reason; the files are kept as the command returned them, less the evidence text.
- **The one real retrieval (piece 2 of the run).** In a-dev, a question on the feature with `--ticket ORION-im02 --id ADR-011 --id MATH-SPEC-003 --radius 1`: 2 batches (10 and 4), 14 evidence items each cited by id and sha256 (ADR-011 5, ORION-im02 3, MATH-SPEC-003 6), 1 named parent expansion, no synthesis note (1,652 of 6,000 tokens), stopping reason `FACET_UNAVAILABLE` (semantic empty; lexical and closure available), no gap, no continuation, validator valid with no error: `docs/plan/wave-1-exit/evidence/retrieval-a-dev-feature.json`.
- **Through the harness (run 1).** The W1-21 scenario cases passed on the harness's own indexed dev tiers: several batches, both files of RETR-A-04 cited, the missing id a stated gap; the validator and synthesis-note suites (W1-22, W1-23) gave 35 passed. No parent expansion or synthesis note was inspected on a dev run by a lead.
- **Outside the main context (DEC-080).** Every retrieval answer went to a file; the lead read only its shape.

## gov check and the twelve commands

- **Families:** 17 of 17 governance test families have an executable check (23 checks). At the start of the exit run (`93bcb247`, 2026-10-12): exit 0, 14 families green, 3 yellow (authority/role limits: commits citing decisions their tree does not record; product traceability: openspec has nothing to validate; audit reproducibility: not applicable until the first audit), none red: `docs/plan/wave-1-exit/evidence/gov-check.json`.
- **Today, in this ticket worktree:** exit 3, two families red, index freshness and recovery/rebuild, both because this worktree's store is older than its head after three merges of the integration branch: `docs/plan/wave-1-exit/evidence/gov-check-run5-stale-store.json`. The lead may not run `gov rebuild` against this worktree, so it was not repaired here; the main orchestrator's check on the main tree is the one that counts for the branch.
- **Commands:** all twelve (status, check, readiness, doctor, rebuild, context, closure, retrieve, checkpoint, close, adopt, pause) are implemented, each with a kept call and answer, none a help call, none `NOT_IMPLEMENTED`: `docs/plan/wave-1-exit/evidence/gov-commands.json`. Five answers are from this worktree, five from the a-dev clone, one (`check`) is the answer of the exit run's start, and one (`pause`) is the owner's own output as DEC-668 quotes it, since no agent runs `gov pause` anywhere. Three entries carry a note that their command line was rebuilt and not kept beside the answer (close, adopt, pause).
- **Residual:** `gov --help` still says of `check` that running the checks is not built yet.

## Worker sessions

Every session below was started through `gov launch` with `--model claude-opus-5-5`, one at a time, each inside the launcher's sandbox (enabled, fail if unavailable, no unsandboxed command) with a strict network allowlist that holds no host (only a research ticket gets hosts). Each launch record holds the session's facts, not its return text.

| Programme | Role | Session id | Ticket | Started through | Sandbox | Network profile | Launch record |
|---|---|---|---|---|---|---|---|
| ORION (a-dev) | product-spec | 30d80992-696a-4d46-8448-a8356594b330 | ORION-sp01 (run 1) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-spec.json` |
| ORION (a-dev) | product-spec | d6e1b5d3-6323-4202-8bd6-e2f0beb6f856 | ORION-ad01 (run 2) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-adopt.json` |
| ORION (a-dev) | product-spec | 1ddd5332-9094-473d-b2f4-201bdf5825b9 | ORION-ad01 (run 2) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-adopt2.json` |
| ORION (a-dev) | independent-auditor | 374ba416-f86b-4312-8343-28996934868d | ORION-ad02 (run 2) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-a5.json` |
| ORION (a-dev) | product-spec | cd685872-3076-4747-98f2-54ac15c436f1 | ORION-sp01 (run 2) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-spec2.json` |
| ORION (a-dev) | independent-test-designer | 32ce12c8-8873-4b69-8b30-3fc24d408468 | ORION-gp09 (run 2; its writes were refused, no commit) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-tests.json` |
| ORION (a-dev) | product-spec | c1a6303a-e685-4ed6-9882-90a7fa09a930 | ORION-ad03 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-ad3a.json` |
| ORION (a-dev) | product-spec | dfc527f1-75ac-4ca0-b440-b644138b5904 | ORION-ad03 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-ad3b.json` |
| ORION (a-dev) | independent-test-designer | 11cbaf5d-ca3f-4000-aed9-628ec50dbca4 | ORION-gp09 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-tests2.json` |
| ORION (a-dev) | product-spec | 2f843e1f-73d1-4097-bdad-2b0d0663b386 | ORION-sp01 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-row25.json` |
| ORION (a-dev) | independent-auditor | 3bc91ae2-bb4e-4517-8a6a-3483abbb6e78 | ade-0y1v, the audit ticket of ORION-sp01's specification (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-audit.json` |
| ORION (a-dev) | product-spec | 02231527-05b5-41d3-9df7-e73b2997def3 | ORION-sp01 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-open6.json` |
| ORION (a-dev) | independent-auditor | bcbec398-48e2-4df7-8287-d9288680cb3b | ade-0y1v, the audit ticket of ORION-sp01's specification (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-audit2.json` |
| ORION (a-dev) | independent-auditor | 54c09049-eb6d-4223-963d-d976966b1168 | ade-0y1v, the audit ticket of ORION-sp01's specification (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-audit3.json` |
| ORION (a-dev) | engineer | 17ddef8f-89b7-4d3f-85ec-ab88bdcfc863 | ORION-im01 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-eng.json` |
| ORION (a-dev) | independent-test-designer | c337eafb-07c1-40ce-bc76-3c316f2ce064 | ORION-im02 (run 5) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-im02-tests.json` |
| ORION (a-dev) | engineer | 1ba66f99-d833-4034-aafa-5b1d659a510e | ORION-im02 (run 5) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/a-im02-eng.json` |
| ARGUS (b-dev) | product-spec | 1522beaf-6e63-44ef-872f-2c6452797298 | ARGUS-sp01 (run 1) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-spec.json` |
| ARGUS (b-dev) | product-spec | 94619988-2d84-4359-b2c4-3d22e2eb1c36 | ARGUS-ad01 (run 2) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-adopt.json` |
| ARGUS (b-dev) | product-spec | f2ef7e58-9588-4239-8cec-10cce0de1e5e | ARGUS-sp01 (run 2) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-spec2.json` |
| ARGUS (b-dev) | product-spec | 90d133da-4a93-4338-862d-67a9fb7e7e31 | ARGUS-sp01 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-spec3.json` |
| ARGUS (b-dev) | independent-test-designer | 066cf469-c1ce-475a-ba66-849109e7e86e | ARGUS-gp13 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-tests.json` |
| ARGUS (b-dev) | product-spec | 37d131ef-63a0-4a4b-a179-1173839da13a | ARGUS-sp01 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-row25.json` |
| ARGUS (b-dev) | independent-auditor | 739d9266-24ef-48b9-bb77-971a1f90af8c | bde-c1yl, the audit ticket of ARGUS-sp01's specification (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-audit.json` |
| ARGUS (b-dev) | engineer | 721df431-f0c8-4a4f-9635-012517224284 | ARGUS-im01 (run 3) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/b-eng.json` |
| Gov OS (this worktree) | independent-test-designer | 824751db-712e-4b49-b0c8-396fd2f8360b | DAEO-gjjf (run 2) | gov launch | sandboxed | strict allowlist, no host | `docs/plan/wave-1-exit/evidence/launch/w1-42-tests.json` |

Twenty-six sessions: 17 in a-dev, 8 in b-dev, 1 here. Run 4 started none. The same list as data: `docs/plan/wave-1-exit/evidence/worker-sessions.json`. Besides these, each lead used read-only subagents inside its own session (run 1 and run 5: one reader each for the learning metrics); they wrote nothing.

## Governance share

The exit auditor judges exit criterion 4 on this section (DEC-677). The threshold is 15 %.

| Programme | Share | Cache reads | Record |
|---|---|---|---|
| ORION | not measured: a measured total exists for one ticket only, ORION-im02, 4.49 % (measured parts 1.38 % and estimated 3.12 %); the six other measured rows of a-dev have no close record, so their close part is not measured; their estimated shares are 1.23 % to 4.21 % | 878,924 on ORION-im02; 7,052,938 on the six other rows together; reported separately and not part of any share | `docs/plan/wave-1-exit/evidence/telemetry-ORION-im02.json` and the table below |
| ARGUS | not measured: no ticket of b-dev has a close record (its one `gov close` refused), and on two tickets the session-start and hook parts are of an attachment type no specimen shows; estimated shares 1.29 % to 2.50 % | 5,213,595 on the four rows together; reported separately | the table below |

The table of the main orchestrator's measurement, copied whole (measured by the main orchestrator, 2026-10-13, DEC-655, DEC-677). Its command: `gov telemetry <ticket> --json --root <clone> --ticket-session <session id>=<role>` with the merged reader, Claude Code 2.1.292 read on every ticket, no refusal. Sessions of runs 1 and 2 and the implementation and test-design sessions of run 3. Tokens are the command's figures; cache reads are reported separately by it.

| Programme | Ticket | Sessions | Estimated share | Measured parts (packet / hooks / gov output / checkpoints / close) | Measured total | Why not measured | Output tokens | Cache read tokens | Cost |
|---|---|---|---|---|---|---|---|---|---|
| a-dev | ORION-sp01 | 2 | 1.23 % | 273 / 49 / 3742 / 244 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 70642 | 2520423 | 3.60 |
| a-dev | ORION-ad01 | 2 | 2.02 % | not measured / not measured / 3284 / 244 / not measured | not measured | sessionstart_packet: an attachment line of a type the specimens do not show; hook_output: an attachment line of a type the specimens do not show; close_records: the ticket has no close record yet: it is counted by a measure after the close | 38388 | 2661756 | 2.36 |
| a-dev | ORION-ad02 | 1 | 2.38 % | 283 / 51 / 0 / 122 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 14019 | 527129 | 0.85 |
| a-dev | ORION-gp09 (run 2 session) | 1 | 2.73 % | 165 / 0 / 0 / 122 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 13525 | 383442 | 0.75 |
| a-dev | ORION-gp09 (run 3 session) | 1 | 2.42 % | 165 / 0 / 0 / 244 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 14770 | 550007 | 0.86 |
| a-dev | ORION-im01 | 1 | 4.21 % | 126 / 0 / 0 / 245 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 3306 | 410181 | 0.43 |
| b-dev | ARGUS-sp01 | 2 | 1.40 % | not measured / not measured / 2635 / 244 / not measured | not measured | sessionstart_packet: an attachment line of a type the specimens do not show; hook_output: an attachment line of a type the specimens do not show; close_records: the ticket has no close record yet: it is counted by a measure after the close | 70162 | 1904053 | 3.19 |
| b-dev | ARGUS-ad01 | 1 | 1.29 % | not measured / not measured / not measured / 122 / not measured | not measured | sessionstart_packet: an attachment line of a type the specimens do not show; hook_output: an attachment line of a type the specimens do not show; gov_output: gov through another runner, a form the specimens do not show; close_records: the ticket has no close record yet: it is counted by a measure after the close | 25289 | 2097742 | 1.79 |
| b-dev | ARGUS-gp13 | 1 | 1.64 % | 132 / 0 / 0 / 122 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 22316 | 642130 | 1.24 |
| b-dev | ARGUS-im01 | 1 | 2.50 % | 67 / 0 / 0 / 245 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 4767 | 569670 | 0.69 |
| this repository | DAEO-gjjf (test designer) | 1 | 0.95 % | 0 / 77 / 0 / 809 / not measured | not measured | close_records: the ticket has no close record yet: it is counted by a measure after the close | 55442 | 2059675 | 2.53 |
| a-dev | ORION-im02 (added by the lead of run 5, its own measurement) | 2 | 3.12 % | 248 / 0 / 0 / 496 / 738 | 4.49 % | nothing: the command's list of parts not measured is empty | 19644 | 878924 | 1.27 |

- **ORION-im02's measurement, in full.** `gov telemetry` once, after the close, naming the test designer's and the engineer's sessions. Governance tokens: session-start packet 248, hook output 0, gov output 0, checkpoint records 496, close records 738, total 1,482. Estimated tokens 3,352 (the instruction files of the two roles). Shares: measured 0.01377643504531722, estimated 0.031159656053915873, total 0.04493609109923309. Agent: Claude Code 2.1.292. Output tokens 19,644; cache read tokens 878,924; cost 1.27. The answer names three known gaps of the counter (PreCompact hook output, gov run inside a wrapper, a sub-agent's instruction files).
- **Sessions the table does not hold:** the sessions of run 3 other than implementation and test design (ORION-ad03 two, ORION-sp01 two, ade-0y1v three, ARGUS-sp01 two, bde-c1yl one) were not measured by anyone. The lead's own sessions are not ticket sessions of a clone and are not counted.
- **The close's own share fields** say "not measured" in ORION-im02's envelope: the close measures before its record exists; the measure after the close is the one above.
- **Every worker session of all runs** (programme, ticket, role, session id) is listed in "Worker sessions".

## MR-3

- **Breaches:** 0
- **Record:** `docs/plan/wave-1-exit/evidence/mr3.json`

What was checked: in both clones only commits of the independent test designer change anything under the test folders (a-dev 930b197 and f49924a, b-dev 2db35a4); the engineers' commits change their one source path each; the lead wrote no test in a clone or here.

Named plainly, for the exit auditor to judge:

- **Eleven undone effects.** The guard's findings files of the clones hold 5 (a-dev) and 6 (b-dev) entries "reverted: acceptance test restored from HEAD" on the acceptance-test folder, all on 2026-10-12, all by the product-spec adoption workers (ORION-ad01, ARGUS-ad01) through Bash. The post-command check undid each; nothing of them is in either history. What the workers' commands did there was not established by any lead. No entry is by an engineer and none is later than 2026-10-12.
- **Run 2's test designer was refused.** The template's permission source denied every edit of the acceptance-test folder, the test designer's included; the owner had the line taken out (DEC-664), and the same edit was made in the two clones (c7df8bc, ded2094).
- **A false flag here.** While the W1-42 test designer ran, the containment hook in the lead's session flagged its four test files as outside allowed paths and left them in place (DEC-662).
- **A known hole, not used in the run.** The guard answers allow for `MultiEdit` for every role (DEC-685); a W1-02 round repairs it.

## Learning metrics

One row per Wave 1 ticket. Sources: the decision register, the orchestrator's running record (`governance/project/bootstrap.md`), the ticket files, and the `Rewrite-Reason:` trailers on the test folders, read by a read-only reader on 2026-10-13 and not re-checked line by line by the lead. Where run 1's return gave a figure that no record holds, the cell says so. A rewrite is counted under the ticket whose suite holds the case. "Packages" are a test designer's decision packages in the register that no record calls KPI disputes; they are named and not counted as disputes.

| Ticket | KPI disputes | Tests rewritten after implementation began | Governance share |
|---|---|---|---|
| W1-01 | 4 (KD-1 to KD-4 in the register) | 1 case, reason: owner decision on integration merges (DEC-253); one install case more in the W1-30 fix round | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-02 | 9 (KD-1 to KD-9 in the register); follow-ups none | 18 cases, reason: owner decision P-23 (DEC-557), across four suites; earlier revisions for DEC-115, DEC-117 and DEC-156 without a recorded count | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-03 | 7 (KD-1 to KD-7 in the register) | not recorded: revised under W1-45 for the owner's correction DEC-156, no count kept | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-04 | 2 | 2 cases, reason: owner correction (DEC-156) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-05 | 1 | not recorded: its cases are part of the P-23 set of 18, not broken out | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-06 | not recorded: 5 packages in the register, none called a KPI dispute | not recorded: the records before 2026-10-06 keep no learning-metrics line | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-07 | 3 (KD-1 to KD-3), and 1 package | not recorded: planned revisions (DEC-190) and mirror cases (DEC-429), no count kept | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-08 | not recorded: 10 packages in the register, 2 of them the lead's | not recorded: the records before 2026-10-06 keep no learning-metrics line | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-09 | not recorded: 9 packages from test design and 1 after the review | not recorded: the records before 2026-10-06 keep no learning-metrics line | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-10 | not recorded: packages in the register only (run 1's return said 0, no record states it) | not recorded: no learning-metrics line (run 1's return said 0) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-11 | not recorded: packages in the register only (run 1's return said 0) | not recorded: no learning-metrics line (run 1's return said 0) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-12 | not recorded: packages in the register only (run 1's return said 0) | not recorded: no learning-metrics line (run 1's return said 0) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-13 | not recorded: packages in the register only (run 1's return said 0) | not recorded: no learning-metrics line (run 1's return said 0) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-14 | not recorded: packages in the register only (run 1's return said 0) | not recorded: no learning-metrics line (run 1's return said 0) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-15 | not recorded: packages in the register only (run 1's return said 0) | not recorded: some cases revised by another ticket's designer on an owner decision, no count kept | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-16 | not recorded: packages DP-1 to DP-6 in the register (run 1's return said 4, not verified) | not recorded: one trailer commit for DEC-561, no assertion changed | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-17 | not recorded: packages in the register only (run 1's return said 0) | not recorded: no learning-metrics line (run 1's return said 0) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-18 | not recorded: 3 packages in the register | not recorded: no learning-metrics line | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-19 | not recorded: no figure in any record | not recorded: no figure in any record | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-20 | not recorded: packages in the register only | not recorded: one planned revision of a shared case (DEC-190); run 1's "3 revised" is in no record | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-21 | not recorded: packages in the register only | 1 case, reason: it needs the real models; a shared support file was aligned by owner decision (DEC-412) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-22 | 0 | 0 | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-23 | 0 | 0 | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-24 | 0 | 1 case, reason: planned, the command was implemented | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-25 | not recorded: no figure in any record | not recorded: a follow-up shared with another hooks ticket revised 6 cases on an owner decision (DEC-444); which suite they belong to is not kept | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-26 | 0 | 4 cases, reasons: 2 for DEC-425 (unmeasured is never green), 2 that named uncovered families by a fixed list | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-27 | not recorded: no figure in the round's record | about 30 cases, reason as far as recorded: cases that ran every command on a copy of the tree were revised to a two-file project | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-28 | not recorded: no figure in any record | 2 cases, reason: DEC-675, what they assert is unchanged; earlier mirror revisions without a count | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-29 | not recorded: no figure in the round's record | 1 case, reason: it could not fail (the orchestrator's finding, labelled owner correction); 6 more in the follow-up on an owner decision (DEC-444) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-30 | 3, and the baseline question | not recorded as a count for rounds 4 to 7, reason: behaviour the earlier code claimed without measuring, one reversed case (DEC-480); later rounds: two cases in the fix round, none after implementation elsewhere | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-31 | 9 (three settled by DEC-502, six by DEC-512) | 4 designer commits, reasons: DEC-491 and DEC-495, DEC-501, DEC-502 and DEC-507, DEC-655 (one case rewritten, 30 added) | not measured: the ticket is in progress and has no close record |
| W1-32 | 6 (four from the designer, two from the lead's reading) | 0 | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-33 | not recorded: no figure in any record (run 1's return said 0) | 1 case, reason: DEC-665 (the research definition is the generated file); its helper was split again for DEC-675 | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-34 | not recorded: 1 package in the register | not recorded: no learning-metrics line | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-35 | not recorded for the first build; follow-up none | not recorded for the first build; follow-up none | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-36 | not recorded: no figure in any record | not recorded: no figure in any record | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-37 | not recorded: 4 packages in the register | not recorded: no learning-metrics line | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-38 | 2; the round of DEC-664: 0 | not recorded as a count for rounds 3 and 4, reason: comparisons the lead's code claimed without making; the round of DEC-664 rewrote 6 cases, all in three other suites and counted there | not measured: closed with the ticket tool under its escalation (DEC-683), no close record |
| W1-39 | 0 | 1 case, reason: DEC-499 (a missing lock is not a match, strengthened) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-40 | 0 | 2 cases, reason: DEC-497 | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-41 | 6 (P-9 to P-14); the designer's packages in the register number 14 | 2 cases, reasons: planned, the command was implemented; a stricter reading decided after the probe (DEC-552) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-42 | 0 in the test design of this ticket; the designer's three readings were kept (DEC-662) | 0 | not measured: no close record yet; the test designer's session has an estimated share of 0.95 % |
| W1-43 | open: the exit audit has not run | open: the exit audit has not run | not measured: the ticket is in progress |
| W1-44 | not recorded: no figure in any record (run 1's return said 0) | not recorded: no figure in any record (run 1's return said 0) | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-45 | not recorded: 4 packages, the orchestrator's | not recorded as a count, reason: owner correction (DEC-156); run 1's "14" is in no record | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-46 | not recorded: packages DP-1 to DP-21 in the register (run 1's return said 1) | not recorded as a count: one live assertion on an owner decision (freeze marker), one case corrected, a batch revised for DEC-271 to DEC-273 and DEC-311 to DEC-317; run 1's "13" is in no record | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-47 | not recorded: 8 packages in the register | not recorded: part of the P-23 set, not broken out | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-48 | not recorded: 3 packages in the register | not recorded: run 1's "9 (owner decision)" is in no record | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-49 | not recorded: 5 packages in the register | 2 cases on 2026-10-13, reason: DEC-665 (the auto-compact window is in the user-level settings since the apply block, DEC-635); run 1's "15 (DEC-264)" rests on a commit subject only | not measured: no close record and no telemetry answer is kept for the ticket |
| W1-50 | not recorded for the first build (packages DP-1 to DP-30); follow-up 0 | 5 cases, reason: the freeze mirror, owner decision DEC-429 | not measured: no close record and no telemetry answer is kept for the ticket |

- **Why so many "not recorded".** The running record keeps a learning-metrics line only from W1-22 on; the sources for the two metrics were fixed by DEC-491 on 2026-10-07; the per-ticket file DEC-501 names does not exist for any ticket in this worktree. Run 1's table, returned to the main orchestrator, mixed disputes with packages and held five counts no record supports; this table replaces it.
- **Why every share is "not measured".** No Wave 1 ticket of this repository has a close record with a measured share; the counter's measure after the close was first used on ORION-im02 in the clone.
- **The exit run's own tickets (clones):** KPI disputes 0 on every clone ticket; acceptance tests rewritten after implementation began 0; tests added after implementation 0. Lines of code against estimate: ORION-im01 13 against 30, ARGUS-im01 41 against 40, ORION-im02 1 against 2. Every engineer converged in one session. False findings: none identified (the first ORION audit's finding was true).

## Parallel tickets

- **git worktree list:** not kept yet: the list with no ticket worktree left can only be taken after this ticket's own worktree is removed, by the main orchestrator; the file git-worktree-list.txt is then added to the evidence folder. Today the list holds the main tree and three ticket worktrees (W1-02, W1-31b, W1-42).

| Ticket | Worktree | Branch | Ticket lead | Merged by | Merge commit | Suites re-run after the merge |
|---|---|---|---|---|---|---|
| W1-28 | the ticket's own worktree, gov-os-worktrees/W1-28, removed after the merge | `w1/W1-28` | a fresh ticket lead session (role orchestrator) in that worktree | main orchestrator | `11d5be9a` | every suite; the section "W1-28 residuals" of `governance/project/bootstrap.md` records the post-merge run |
| W1-19 | the ticket's own worktree, gov-os-worktrees/W1-19, removed after the merge | `w1/W1-19` | a fresh ticket lead session (role orchestrator) in that worktree | main orchestrator | `bfda84ab` | every suite; the section "W1-19 residuals" of `governance/project/bootstrap.md` records the regression after the merge and its one latency occurrence |
| W1-50 | the ticket's own worktree, gov-os-worktrees/W1-50, removed after the merge | `w1/W1-50` | a fresh ticket lead session (role orchestrator) in that worktree | main orchestrator | `6a978dbc` | every suite, green; the section "W1-50 residuals" of `governance/project/bootstrap.md` |
| W1-21 | the ticket's own worktree, gov-os-worktrees/W1-21, removed after the merge | `w1/W1-21` | a fresh ticket lead session (role orchestrator) in that worktree | main orchestrator | `0aea779f` | every suite; the section "W1-21 residuals" of `governance/project/bootstrap.md` records the regression after the merge |

- **What the records show.** Up to four ticket leads worked at once, each in its own worktree on a branch named after the ticket; only the main orchestrator merged; a regression followed every merge (DEC-513, DEC-518). The four merges above fall on 2026-10-05 and 2026-10-06. One merge conflict is recorded (W1-20 with W1-28, on shared test-support files). The worktree paths are given by the wave's layout and were not re-checked: those worktrees are gone.
- **Today.** Three rounds ran beside this ticket in worktrees of their own (W1-31, W1-38, W1-02); the main orchestrator merged the W1-38 round into the integration branch and that branch into this one (`44920a2e`).

## Owner's steps

| Step | Result | Record |
|---|---|---|
| B1 | done | DEC-668 in `docs/DECISION_REGISTER.md`; the checklist is `docs/plan/wave-1-exit/OWNER-EXIT-CHECKLIST.md`. Commit `71ae763f` on the integration branch |
| B2 | not done: part 1 (a throwaway repository) is done; part 2, the freeze on this repository, is open and is the owner's, after the leads finish (DEC-668, DEC-670). The file owner-freeze-check.json is written when both halves exist | DEC-668 in `docs/DECISION_REGISTER.md` quotes the five outputs of part 1 |
| B3 | not done: the lefthook install is deferred until W1-42's lead, the W1-31 round and the W1-38 round have all finished, because git hooks are shared with their worktrees (DEC-670). It is the owner's | DEC-670 in `docs/DECISION_REGISTER.md` |

- **B1, as DEC-668 quotes it.** Stop and SubagentStop registered through the operator. Dry run and real run: "held-out step: rules written 1", "deny rules: in force 8, generated 8, lost 0, added 0", "generated files: 44 (new 0, changed 1, already the same 43)"; the one changed file is the settings file of the harness. Portability: `"findings": []`, exit 0. Commit `71ae763fa244976ed0eebfda8ac787c782943c52` (Task: DAEO-gjjf, Role: owner, Implements: CAP-37.b, CAP-37.d); tree clean, nothing pushed.
- **B2 part 1, as DEC-668 quotes it.** The owner ran it himself in a plain terminal on a copy of the a-dev exit clone (since deleted). In order: status before `"pause": {"paused": false, "flag": "absent", "mirror": false}`; pause `{"ok": true, "command": "pause", "result": {"paused": true}, "session": ""}`; status while frozen `"pause": {"paused": true, "flag": "frozen", "mirror": true, "by": "owner", "since": "2026-10-13T13:56:14Z"}`; lift `type LIFT-5786 to lift the freeze: LIFT-5786`, then `{"paused": false}`; status after `"pause": {"paused": false, "flag": "absent", "mirror": false}`.
- **Open, the owner's:** B2 part 2 and B3, after the leads finish. The orchestrator tells the owner when that moment has come.

## Baseline and adoption

- **Adoption complete at:** `1c33dd28` (gov adopt --lite A8, the adoption's last commit, 2026-10-11; DEC-625)
- **Exit run started at:** `93bcb247` (W1-42 claimed, 2026-10-11)

| Fact | Result | Evidence |
|---|---|---|
| gov adopt --lite run | yes | the eight stage records, the last of them `governance/adoption/A8-legacy-import-and-retirement.md` |
| gov check baseline empty | yes | `docs/plan/wave-1-exit/evidence/gov-check.json`: exit 0 at `93bcb247`, no red check, no baseline entry in use |
| capability records present | yes | 273 records under `docs/contract/capabilities/` (62 capabilities and 211 covers items, DEC-614), for example `docs/contract/capabilities/CAP-01.a.md` |

The close exceptions ended with the adoption (DEC-522). Since then two tickets of this repository were not closed by a clean `gov close`: see "For the exit auditor" (DEC-683, DEC-684).

## How the run was run

- **Orchestration skill:** `template/governance/kernel/skills/orchestration/SKILL.md` (installed into each clone with the template; the leads worked in the clones by it)
- **Brief templates:** `template/governance/kernel/templates/brief-test-designer.md`, `template/governance/kernel/templates/brief-engineer.md`, `template/governance/kernel/templates/brief-product-spec.md`, `template/governance/kernel/templates/brief-reviewer.md`
- **Kept briefs:** `docs/plan/wave-1-exit/evidence/briefs/a-im02-tests.md`, `docs/plan/wave-1-exit/evidence/briefs/a-im02-eng.md` (the two briefs of ORION-im02; the 24 other briefs stay in the lead's scratch folder and are not copied, since some quote programme text)
- **Repository orchestrator prompt:** not used for the cycle in the clones: no worker brief was taken from it. The lead itself was started by the main orchestrator's brief, which carries that prompt's rules for ticket leads (appendix A5); that is how every ticket lead of the wave is started, and it is named here so that it is not misread.

Departures from the templates, named: the audit briefs of run 3 prescribed a report form of their own and not the audit skill's (repaired in a-dev, open in b-dev); the designer briefs follow DEC-462 (behaviour and sources only).

## Forbidden outcomes

- **Forbidden outcomes:** none

No write by an implementer or by an orchestrator reached an acceptance-test folder; no share above 15 % is reported as a pass (no programme share is reported as measured at all); no close was forced, classed or excepted; no history was rewritten; nothing was pushed. The events a reader might take for one are named in "MR-3" and in "Deviations of every run".

## The doctor

`gov doctor` exits 3 on this repository (DEC-667). Version drift alone makes it unhealthy: the section claude_code reports drift (CLI 2.1.292, VS Code extension 2.1.296), and the doctor's code turns a section in drift into an unhealthy answer. That is against DEC-210, by which drift is reported and is not a failure. The owner put it on the Wave 2 list (DEC-667); it is named here so that a red doctor from drift alone is not misread.

In this ticket worktree today the answer names four sections (`docs/plan/wave-1-exit/evidence/gov-doctor.json`): tools (pytest-xdist is reported as not found, though the plugin imports as 3.8.0 and the close's parallel runs use it), path_compliance (one moved reference in an adoption record), index_freshness (this worktree's store is stale, as in `gov check`), and claude_code (the drift). The canaries are unmeasured here for the same stale store. Run 1's answer, with a fresh store, named tools, path_compliance, canaries (semantic unavailable) and claude_code (`docs/plan/wave-1-exit/evidence/gov-doctor-run1.json`). So the doctor on this repository is red from drift and from at least two other sections; the main tree's own answer is the main orchestrator's to state.

## For the exit auditor

One line each, from the register:

- **Six red cases on the integration branch and their repair** (DEC-665, DEC-669, DEC-675): three W1-48 cases cleared by two corrected records; two W1-49 cases and one W1-33 case rewritten by a separate designer session inside the W1-38 round, each with a `Rewrite-Reason:` trailer; W1-33's helper split so that W1-28's fixture-copy check keeps its reach.
- **The W1-49 live-session case is flaky** (DEC-671, DEC-676): two failures in six runs alone; the owner's user-level settings hold no hooks block, so no user-level Stop hook is the cause.
- **The secrets-indexing red of 2026-10-13** (DEC-673) was caused by the orchestrator's safety copies of the exit clones under the runtime folder; they were moved out, and no clone or programme file goes under a runtime folder again.
- **The items of DEC-674** are in "Residuals", each marked "Wave 2 list".
- **The a-dev namespace that holds the two secret-named files** keeps its permitted roles as written (DEC-679); a named residual.
- **DAEO-3ef2 (W1-38) was closed with the ticket tool under ESCALATION_BLOCKED**, by the owner's authorisation (DEC-683): its escalation came from history alone, the round's probe passed, the regression was green.
- **A W1-02 round on the guard and the tools it does not know** is running or done (DEC-685): `MultiEdit` judged like `Edit`, an unknown tool refused. It is not on this branch.
- **DAEO-6mk8 (W1-31)** has a pre-authorisation for a close with the ticket tool if its `gov close` returns exit 4 from history alone (DEC-684); it is still in progress on this branch.
- **The doctor** (DEC-667): see "The doctor".
- **Deviations of the leads** recorded by decision: run 1 (DEC-654, DEC-661), run 2 (DEC-662), run 3 (DEC-674); all are repeated in "Deviations of every run".

## Residuals

For the orchestrator's running record. Items of the finish line are marked.

- A closed specification was changed in place (a-dev f59aa0e); a rule is wanted. Wave 2 list (DEC-674).
- PKG-7, the ARGUS audit's major finding: what counts as a missing `created_at`, values that are not aware datetimes, a missing "now", whether the error text is in the contract; `None` raises `AttributeError` today. The lead's recommended rule: `None` is missing, every value that is not an aware datetime is refused with `ValueError`, the message is not in the contract. Wave 2 list (DEC-674).
- The b-dev audit report is not in the kernel audit validator's form (frontmatter and one table). Wave 2 list (DEC-674).
- `gov close` judges every commit that carries the ticket's `Task:` trailer, the lead's own ticket-creating commit included; a clone's path map has no trailers base. Wave 2 list (DEC-674).
- `gov close` leaves its repair ticket untracked, and without role, allowed paths and KPIs: in a-dev that ticket (ade-5rcs) now turns two more check families red. Wave 2 list (DEC-674).
- `python3 -m gov.guard.heldout --help` has no help and executes. Wave 2 list (DEC-674).
- The lesser findings of the ORION and ARGUS audits (the KPI lines of ORION-im01 lack "by its repr", a readiness row's reason is untrue, the owner's answers stand only in the discovery record, stale states; ARGUS F-2 to F-8). Wave 2 list (DEC-674).
- The A5 verdict hash in a-dev is left; the verdict's commit is the anchor (DEC-674). Named residual.
- The permitted roles of the a-dev namespace of the two secret-named files stay as written (DEC-679). Named residual.
- `gov close` judges a ticket by its class instead of requiring acceptance tests from every ticket. Wave 2 list, near the top (DEC-658).
- The doctor reports drift without failing on it. Wave 2 list (DEC-667).
- The W1-49 live-session case asks a small model to repeat four facts. Wave 2 list (DEC-676).
- The template's path map ships paths only (no state class, capabilities, policies, systems, memory class, no test namespace); the claims check and `gov readiness` disagree on which rows need a gap ticket; `gov rebuild` and the whole `gov check` cannot be used inside a launched session; the audit ticket the specification checker writes cites decisions a project's register does not hold; the adoption auditor could not reproduce the A3 proposal hash. Wave 2 list (DEC-662).
- A ticket whose sessions are of more than one CLI version; attachment types no specimen shows; instructions lines that count nothing. Wave 2 list (DEC-663).
- Run 1's template and brief gaps (a plain rulesync run writes one file only; copying the template runs no copier task, so no framework lock; `gov adopt --lite` needs a stage and a clean tree; the clones have no source folder of their own). Wave 2 list (DEC-654).
- New in run 5: a full `gov rebuild` in the a-dev clone answers "semantic: recreated" and the semantic facet stays empty, so a question in plain words returns no evidence there and the semantic canary cannot hit. Not on any list yet.
- New in run 5: the lexical facet matches a question as one phrase; alone it answers a plain-word question with nothing. Not on any list yet.
- New in run 5: the programme test test_exact_agreement of the ORION reference fails before and after ORION-im02; the engineer returned it as a package (recommendation: leave it, a ticket of its own). Not on any list yet.
- New in run 5: the doctor reports pytest-xdist as not found in this worktree while the plugin is installed. Not on any list yet.
- New in run 5: eleven "reverted" entries of the post-command check in the clones' findings files (MR-3 section) were never explained. Not on any list yet.
- New in run 5: `gov --help` says of `check` that running the checks is not built yet (first named in run 1).
- The share of governance cannot be shown per programme while only tickets closed by `gov close` get a measured total.
- ORION-im01 and ARGUS-im01 stay open in the clones, each with a repair ticket; the a-dev close counter of ORION-im01 stands at 1 of 3.

## Deviations of every run

- **Run 1 (2026-10-12).** The lead read the generated settings file of the a-dev clone once (keys, hook commands and a count of deny rules; no rule was printed), against the rule that nobody reads it. It read the S0b2 code-intelligence report by exact path, as DEC-377 allows a worker. Its setup commands differed from its brief's (rulesync targets, the template committed before adoption). The learning-metrics table it returned was compiled by a subagent and not spot-checked.
- **Run 2 (2026-10-12).** The lead wrote and edited clone ticket files as orchestrator and widened one ticket's allowed paths; added the test namespace to a-dev's path map itself; wrote the all-KEEP A3 proposal; a-dev had two repair rounds; gap and adoption tickets were closed with the ticket tool and a note; one b-dev worker ran a Bash here-document; the containment hook flagged the W1-42 designer's four test files in the lead's session and left them; its ticket-creating commit `540004a` lacks `Implements:`, which later refused ORION-im01's close.
- **Run 3 (2026-10-13).** The lead wrote ticket files in the clones and ran the specification checker's close, the ticket tool's close and start there; a closed specification was edited in place; three auditor sessions ran on one a-dev audit ticket; b-dev's close was invoked twice (the first refused before the gates); the lead ran pytest read-only in b-dev while a worker ran there; ARGUS's red rested on the absent module alone, and its designer checked behaviour with an out-of-tree stand-in; b-dev's specification was closed and its engineer run with PKG-7 open; the lead committed the two repair tickets after the refusals; it ran the held-out module's help once in a-dev, which executed and failed harmlessly.
- **Run 4 (2026-10-13).** No worker, no ticket, no close: it returned at once because no ORION change stood on decided ground. One checkpoint command was refused for a here-document and repeated without one.
- **Run 5, one more.** While checking this report the lead typed one malformed Bash here-document in this worktree, which the guard did not refuse; the command made the two wording corrections to this report that it was meant to make and changed nothing else.
- **Run 5 (2026-10-13), this one.** The lead wrote ADR-011 and the ticket file of ORION-im02 in the clone as orchestrator (the skill gives the record of an owner answer to the orchestrator); it checked out the clone's main for the merge and went back to the feature branch. For this report it went beyond the brief's one retrieval in a-dev: the two scenario questions were asked three times each, one full `gov rebuild` and one direct call of the semantic index's refresh function were run in between, and `gov readiness` and `gov doctor` were run there; all of it read-only for the clone's history (heads unchanged, tree clean), but the clone's derived stores were rebuilt. The evidence text was taken out of the kept retrieval answers, so that no programme text is copied into this repository. `gov check` here is red on a stale store that the lead may not rebuild. A read-only subagent compiled the learning metrics from the records, the orchestrator's running record included; the lead did not re-check its line numbers. Three command lines in the kept command answers were rebuilt and are marked so.

## Evidence list

- **Kept answers:** everything under `docs/plan/wave-1-exit/evidence/`, named section by section above. Not kept, each waiting for its owner: the governance share per programme (governance-share.json, written only when both programmes are measured), the worktree list (git-worktree-list.txt, the main orchestrator's after this worktree is removed), the owner's freeze check (owner-freeze-check.json, after B2 part 2).
- **Live clones (under the temp folder, lost on a reboot):** /tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/a-dev-exit, branch feature/dimension-checked-addition at `30996b6`, its main at `2d3d098`, clean; and .../clones/b-dev-exit, branch feature/data-retention-rule at `fc28272`, its main at `3b1ad56`, clean.
- **Backups (DEC-681), made by the operator with a plain archive copy under ~/gov-os-workbench/archive/w1-42-exit-clones/, quoted from the register:** live/a-dev-exit at `82dca10` (repair ticket ade-5rcs, from the refusal of ORION-im01's close); live/b-dev-exit at `fc28272` (repair ticket bde-0kr6, from the refusal of ARGUS-im01's close); safety-run2/a-dev-exit at `8e517f9`; safety-run2/b-dev-exit at `132ca2d`; safety-run1/a-dev-exit at `29ff08f`; safety-run1/b-dev-exit at `ac074b5`.
- **The backup of a-dev is older than the live clone:** ORION-im02's eight commits and the merge (heads `30996b6` and `2d3d098`) exist only under the temp folder until the operator copies the clone again.
- **The lead's logs and briefs:** the scratch folder of this worktree (not committed, by rule): the launch logs with the workers' returns, the briefs of all runs, the lead's checkpoints.
- **Temp folders left:** the two clones above; run 3's two folders of rulesync output (gen-a, gen-b, no programme file) under the scratchpad of session bc5e4511-6d6e-452a-a58f-a68689018d73.
- **Planted secrets:** the programmes hold planted secrets; this report and its evidence name such a file by its name only and hold no value of one (DEC-604).
