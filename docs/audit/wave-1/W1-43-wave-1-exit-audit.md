---
milestone: wave-1-exit
commit: 60ea6924be2f4c263f000fef6a75c09e92f01404
pack_sha256: 2355ce5f42d2a8d087535fa0dd3bbcc012a0ec43ec0d08f1f712b6dde8e48c23
---

# Wave 1 exit audit (W1-43, DAEO-03pw)

- **Auditor:** independent-auditor, a fresh read-only session (MR-4, CAP-47). It built nothing in Wave 1 and edited no audited file. Identity checked at the start: `GOV_ROLE GOV_TICKET` = `independent-auditor DAEO-03pw`.
- **Audited commit:** `60ea6924` on `w1/integrate`; the tree was clean at the start. Date: 2026-10-16.
- **Context pack:** `docs/audit/wave-1/context-pack-DAEO-03pw.json`, built with `gov context DAEO-03pw --json --role independent-auditor` (stdout only). Its file sha256 is the header's `pack_sha256`. The pack's own hash is `f5af1af1bfdd175d1b765ad949133e1f09a03458a0ddc15c17280fd97abb9659`, the same in two builds, so the pack reproduces. The pack breaks its own ceiling (finding F-M5).
- **The owner's reading of MR-3 applied here (DEC-430):** the core tests for every KPI line are written by the independent test designer before implementation. Cases found in review may be added afterwards, by the test designer only, red before their fix (DEC-136).
- **Yardstick:** the DAEO-03pw ticket; `docs/charter/CHARTER_v5.md` (MR-1 to MR-6); `docs/contract/CONTRACT_v4.md` and `docs/contract/contract.yaml` (149 W1 covers items in 42 W1 capabilities, plus 11 W1 items in capabilities of other waves); `docs/plan/WAVE_1_WBS.md` §4; and `docs/DECISION_REGISTER.md` up to DEC-717, ACCEPTED entries only.
- **Not read:** the held-out file, the settings file the guard protects, the orchestrator's iteration and escalation records (DEC-096), and its notes, briefs and checkpoint. The only orchestrator file read was COMPLIANCE.md, as a set of claims to verify.

## What the auditor ran

The outputs are in the auditor's session scratch folder and are not committed; the numbers below are taken from them.

- **`gov check --json`** at `60ea6924`: exit 3, `CHECK_FAILED`.
  - All 17 of 17 families report, each with at least one executable check.
  - RED: secrets indexing (the check crashed while the suite ran), recovery/rebuild (store digest `b509cf…` against a rebuilt `e16f01…`) and product traceability (8 `MISSING_IMPLEMENTS_TRAILER`, exactly the DAEO-gjjf commits that DEC-717 names).
  - YELLOW: authority/role limits (18 `DECISION_UNRECORDED` citations), openspec absent, audit reproducibility (not applicable until this first audit).
  - The second run, after the suite, is under "Re-runs".
- **`gov doctor --json`:** exit 3, `DOCTOR_UNHEALTHY`.
  - tools: pytest-xdist `found_version null`, although 3.8.0, the pinned version, is installed;
  - path_compliance: four files cite `docs/audit/wave-1/adoption-path-map-verdict.md`, which has moved to `docs/adoption/`;
  - canaries: semantic `FACET_UNAVAILABLE`, a miss;
  - claude_code: drift, CLI 2.1.292 against extension 2.1.301;
  - framework_lock: unmeasured;
  - held_out: pass.
- **The plan validator** `python3 docs/plan/tools/validate_s1.py`: ALL PASS (99 PASS, 2 SKIP).
- **The full suite in the regression's parallel form** (`pytest tests -n auto -p gov_close_serial_only`, 2026-10-16 09:47 to 10:20): **3 failed, 13,189 passed, 31 skipped** (1,984 s).
  - `tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]`: named red (DEC-713, DEC-714).
  - `tests/acceptance/W1-42/test_w1_42_exit_report.py::test_governance_share_is_measured_and_at_most_15_percent_on_each_programme`: named red (DEC-713). It fails because `docs/plan/wave-1-exit/evidence/governance-share.json` has never existed.
  - `tests/acceptance/W1-40/test_w1_40_workflow_text.py::test_no_lefthook_hook_is_installed_in_this_repository`: **not named anywhere**. It turned red when the hooks were reinstalled on 2026-10-16 at 09:42, as DEC-712 foresaw (F-M4).
  - DEC-713's third red, the worktree list, now passes.
- **The serial-only cases alone** (the 55 entries of `tests/acceptance/serial-only.txt`, with the plugin's given list; 2026-10-16 10:25 to 10:52): **263 passed, exit 0** (1,639 s).
  - W1-19's measured mean hit@5 is 83.33: at or above DEC-414's pass line of 80, and 1.67 below the 85 baseline.
- **Re-runs:** no test case was re-run. `gov check` and `gov doctor` were run a second time after the suite, on a quiet machine.
  - **`gov check`, second run:** exit 3. All 17 families report: 13 GREEN, 3 RED, 1 YELLOW.
    - Secrets indexing is now GREEN; the first run's crash came from load.
    - Audit reproducibility is now GREEN: the validator judged this report.
    - RED: recovery/rebuild, with the same mismatch both times (cleared by the rebuild below); product traceability, with the same 8 DAEO-gjjf findings; and **schema/invariants**, newly red with `SCHEMA_INVALID_TYPE` on this report itself (F-M13).
  - **`gov doctor`, second run:** unchanged.
  - **After `gov rebuild --no-embeddings`** (the commit step), the pre-commit hook's `gov ci checks G1 G2` failed on core-schema and product traceability only. So the recovery/rebuild red was a store older than the head, not a defect.
- **The commit of this report:** refused by the pre-commit hook.
  - Output: `gov ci: CHECK_FAILED: hard-block checks failed: core-schema, product-traceability-trailers`, exit status 3, after 318 s. Staged secrets: 2 scans, 0 secrets.
  - The auditor did not retry and did not work round the hook (F-M13). History is unchanged at `60ea6924`, with no foreign commit (the DEC-710 failure mode).
  - **This report was committed after the owner uninstalled the lefthook hooks through the operator, on the owner's instruction (F-M13).**
- **Independent checks in the exit clones:** done on a copy in the auditor's scratch folder; the archive was not written.
  - At ORION-im02's test commit `f49924a`, its acceptance cases gave 29 failed and 14 passed.
  - At the engineer's commit `6a78498` they gave 43 passed, and all of a-dev's acceptance tests gave 127 passed.
  - The clone history shows that only designer commits (`930b197`, `f49924a`, `2db35a4`) touch the clone's test folders.
- **Contract coverage, mechanically:** every one of the 149 W1 covers items has a closed providing ticket and an acceptance test that cites its id. CAP-52.b is cited only through the W1-38 README's map to named tests.
- **Helpers:** three read-only helpers ran: contract coverage, close history and probes, and the compliance-claim check.
  - None of their returns could be handed back, because the guard refuses SubagentHandback (F-M7). The auditor read each return from its transcript and checked every claim used here against git or the files itself.

## Audit table

| item | class | evidence |
|---|---|---|
| MR-1 Specification comes first: both programmes closed their specification before tickets (gov readiness, fresh specification audit); the plan validator passes 99 PASS 2 SKIP | OK | docs/plan/wave-1-exit/EXIT-REPORT.md, docs/plan/wave-1-exit/evidence/launch/a-audit2.json, docs/plan/wave-1-exit/evidence/launch/b-audit.json |
| MR-2 Closed specifications generate the work: ORION and ARGUS WBS tickets with KPI lines and linked gap tickets ORION-gp10 to gp12 | OK | docs/plan/wave-1-exit/EXIT-REPORT.md, docs/plan/wave-1-exit/evidence/a-dev-history.txt |
| MR-3 KPIs; the builder never writes its own acceptance tests: DEC-430 reading applied: 282 non-merge commits touch tests/acceptance, 278 parse as Role independent-test-designer, the other four (0645ec3d c44e1c2d 3d58265d 75fe2915) carry the designer role outside the final trailer block (DEC-156, DEC-175); no merge adds its own change there; the exit clones show only designer commits on their test folders; auditor re-ran ORION-im02: red 29 failed at f49924a, green 43 passed at 6a78498 | OK | docs/plan/wave-1-exit/evidence/mr3.json, tests/acceptance/W1-01/w1_01_support.py |
| MR-4 Audit, discovery and impact are distinct functions: this audit is a fresh read-only session; but W1-16 and W1-21 (FULL) have no probe or review record in the repository and no excusing decision; W1-42 has none (DEC-717 lets this audit stand in) (F-M11) | WEAKENED | governance/project/bootstrap.md, docs/DECISION_REGISTER.md |
| MR-5 The Gov OS works as a software company: ticket leads still run as role orchestrator (DEC-434 not built); the main orchestrator session records its writes under the closed ticket DAEO-6cc2 (F-m) | WEAKENED | governance/project/bootstrap.md, docs/DECISION_REGISTER.md |
| MR-6 The human is the customer and final authority: owner approvals are transcribed, not owner git facts (F-M6); three pushes of w1/integrate after 2026-10-07 and the hook reinstall of 2026-10-16 are not recorded (F-M9); W1-30 closed past an owner escalation stop and ratified after the fact (DEC-651) | WEAKENED | docs/DECISION_REGISTER.md, governance/project/bootstrap.md |
| CAP-01 Authority precedence and hard invariants (capability): precedence built and tested; approvals as owner git facts weakened in practice (CAP-01.b) | WEAKENED | tests/acceptance/W1-24/test_w1_24_authority.py, tests/acceptance/W1-11/test_w1_11_approval.py, tests/acceptance/W1-26/test_w1_26_authority.py |
| CAP-01.a (provider W1-24): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-24/test_w1_24_authority.py, tests/acceptance/W1-24/README.md |
| CAP-01.b (provider W1-11): built and tested; in practice 466 register entries read ACCEPTED (owner) but are committed under Role: orchestrator, one Role: owner commit touches the register, and no entry is ever ACTIVE, so the approval gate of DEC-360 judged no Wave 1 decision (F-M6) | WEAKENED | docs/DECISION_REGISTER.md, tests/acceptance/W1-11/test_w1_11_approval.py |
| CAP-01.c (provider W1-26): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-26/test_w1_26_authority.py, tests/acceptance/W1-26/test_w1_26_dec436.py |
| CAP-01.d (provider W1-24): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-24/test_w1_24_mandatory.py, tests/acceptance/W1-24/README.md |
| CAP-02 Release authenticity (lite: signed git tags) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-27/test_w1_27_doctor.py |
| CAP-02.a (provider W1-39, W1-27): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-27/test_w1_27_doctor.py, tests/acceptance/W1-27/test_w1_27_doctor_unmeasured_r3.py |
| CAP-03 Security and sensitivity classification (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-08/test_w1_08_path_map.py, tests/acceptance/W1-17/test_w1_17_corpus.py, tests/acceptance/W1-15/test_w1_15_filter.py |
| CAP-03.a (provider W1-15, W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_path_map.py, tests/acceptance/W1-15/test_w1_15_filter.py |
| CAP-03.b (provider W1-15, W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_path_map.py, tests/acceptance/W1-15/test_w1_15_product_data.py |
| CAP-03.c (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_path_map.py, tests/acceptance/W1-08/README.md |
| CAP-03.d (provider W1-17): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-17/test_w1_17_corpus.py, tests/acceptance/W1-17/README.md |
| CAP-03.e (provider W1-16, W1-15): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-15/test_w1_15_filter.py, tests/acceptance/W1-16/test_w1_16_builtin_allowlist_and_daemon_secrets.py |
| CAP-04.b (provider W1-31): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-31/test_w1_31_fourth_specimen.py, tests/acceptance/W1-31/test_w1_31_measured_and_estimated.py |
| CAP-04.c (provider W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-21/test_w1_21_paging.py, tests/acceptance/W1-21/README.md |
| CAP-05 Emergency controls (pause/freeze/cancel/rollback) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-28/test_w1_28_freeze.py, tests/acceptance/W1-28/test_w1_28_cancel.py, tests/acceptance/W1-28/test_w1_28_rollback.py |
| CAP-05.a (provider W1-28): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-28/test_w1_28_freeze.py, tests/acceptance/W1-28/README.md |
| CAP-05.b (provider W1-28): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-28/test_w1_28_cancel.py, tests/acceptance/W1-28/README.md |
| CAP-05.c (provider W1-28): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-28/test_w1_28_rollback.py, tests/acceptance/W1-28/README.md |
| CAP-05.d (provider W1-28): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-28/test_w1_28_cancel.py, tests/acceptance/W1-28/test_w1_28_freeze.py |
| CAP-06 Repository contract and path map (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-08/test_w1_08_path_map.py, tests/acceptance/W1-41/test_w1_41_path_map.py, tests/acceptance/W1-41/test_w1_41_unknown.py |
| CAP-06.a (provider W1-27, W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_path_map.py, tests/acceptance/W1-08/test_w1_08_templates.py |
| CAP-06.b (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_path_map.py, tests/acceptance/W1-41/README.md |
| CAP-06.c (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_unknown.py, tests/acceptance/W1-41/README.md |
| CAP-06.d (provider W1-41, W1-27): gov doctor path_compliance fails on four files citing docs/audit/wave-1/adoption-path-map-verdict.md, moved to docs/adoption/ (F-M2) | WEAKENED | docs/adoption/adoption-path-map-verdict.md, tests/acceptance/W1-27/test_w1_27_path_compliance.py |
| CAP-06.e (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_floor.py, tests/acceptance/W1-08/README.md |
| CAP-07 Authoritative vs derived state separation (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-27/test_w1_27_rebuild.py, tests/acceptance/W1-08/test_w1_08_frontmatter.py |
| CAP-07.a (provider W1-27): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-27/test_w1_27_rebuild.py, tests/acceptance/W1-27/test_w1_27_rebuild_r2.py |
| CAP-07.b (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_frontmatter.py, tests/acceptance/W1-08/test_w1_08_path_map.py |
| CAP-08 Deterministic structured memory (records) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-10/test_w1_10_queries.py |
| CAP-08.a (provider W1-10): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-10/test_w1_10_queries.py, tests/acceptance/W1-10/README.md |
| CAP-09 Relationship/graph memory (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-10/test_w1_10_edges.py, tests/acceptance/W1-10/test_w1_10_queries.py |
| CAP-09.a (provider W1-10): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-10/test_w1_10_edges.py, tests/acceptance/W1-20/test_w1_20_records.py |
| CAP-09.b (provider W1-10): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-10/test_w1_10_queries.py, tests/acceptance/W1-20/test_w1_20_gaps.py |
| CAP-10 Semantic memory (vector/embedding retrieval) (capability): dev-set mean hit@5 83.33 against the contract acceptance of 85; DEC-414 (owner) sets the pass line at 80; the contract is not re-baselined (F-m) | WEAKENED | tests/acceptance/W1-19/test_w1_19_embedding_policy.py |
| CAP-10.a (provider W1-19): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-19/test_w1_19_embedding_policy.py, tests/acceptance/W1-19/test_w1_19_real_models.py |
| CAP-11 Lexical memory (FTS/BM25) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-17/test_w1_17_exact_query.py |
| CAP-11.a (provider W1-17): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-17/test_w1_17_exact_query.py, tests/acceptance/W1-17/README.md |
| CAP-12 Code-structural memory (AST/LSP/SCIP) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-16/test_w1_16_code_answers.py, tests/acceptance/W1-16/test_w1_16_builtin_allowlist_and_daemon_secrets.py |
| CAP-12.a (provider W1-16): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-16/test_w1_16_code_answers.py, tests/acceptance/W1-16/README.md |
| CAP-12.b (provider W1-16): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-16/test_w1_16_builtin_allowlist_and_daemon_secrets.py, tests/acceptance/W1-16/test_w1_16_home.py |
| CAP-13 Temporal and episodic memory (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-10/test_w1_10_load.py, tests/acceptance/W1-25/test_w1_25_record.py |
| CAP-13.a (provider W1-10, W1-30): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-10/test_w1_10_load.py, tests/acceptance/W1-30/test_w1_30_close.py |
| CAP-13.b (provider W1-25): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-25/test_w1_25_record.py, tests/acceptance/W1-25/README.md |
| CAP-14 Failure memory (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-21/test_w1_21_failure_memory.py |
| CAP-14.a (provider W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-21/test_w1_21_failure_memory.py, tests/acceptance/W1-21/README.md |
| CAP-15 Context packet compilation (capability): packet ceiling not held: 814821 tokens against 6000 for DAEO-03pw (CAP-15.d) | WEAKENED | tests/acceptance/W1-24/test_w1_24_packet.py, tests/acceptance/W1-24/test_w1_24_mandatory.py, tests/acceptance/W1-24/test_w1_24_blocked.py |
| CAP-15.a (provider W1-24): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-24/test_w1_24_packet.py, tests/acceptance/W1-24/README.md |
| CAP-15.b (provider W1-24): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-24/test_w1_24_mandatory.py, tests/acceptance/W1-09/README.md |
| CAP-15.c (provider W1-24): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-24/test_w1_24_blocked.py, tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py |
| CAP-15.d (provider W1-24): gov context DAEO-03pw at the audited head: 814821 tokens against a 6000 budget, the ticket text itself dropped, envelope ok true; each DEC id resolves to the whole register (one shared sha256) (F-M5) | WEAKENED | .tickets/DAEO-03pw.md, docs/DECISION_REGISTER.md |
| CAP-15.e (provider W1-24): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-24/test_w1_24_packet.py, tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py |
| CAP-15.f (provider W1-23): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-23/test_w1_23_synthesis.py, tests/acceptance/W1-23/README.md |
| CAP-15.g (provider W1-24, W1-29): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-24/test_w1_24_brief.py, tests/acceptance/W1-29/test_session_hooks.py |
| CAP-16 Multi-batch, multi-hop, paginated retrieval (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-21/test_w1_21_command.py, tests/acceptance/W1-21/test_w1_21_closure_and_gaps.py, tests/acceptance/W1-21/test_w1_21_paging.py |
| CAP-16.a (provider W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-21/test_w1_21_command.py, tests/acceptance/W1-21/test_w1_21_paging.py |
| CAP-16.b (provider W1-36, W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-21/test_w1_21_closure_and_gaps.py, tests/acceptance/W1-21/test_w1_21_dev_tier.py |
| CAP-16.c (provider W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-21/test_w1_21_paging.py, tests/acceptance/W1-21/README.md |
| CAP-17 Incremental indexing and freshness (capability): canaries miss on this repository (CAP-17.c) | WEAKENED | tests/acceptance/W1-17/test_w1_17_freshness.py, tests/acceptance/W1-22/test_w1_22_canaries.py |
| CAP-17.a (provider W1-17): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-17/test_w1_17_freshness.py, tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py |
| CAP-17.c (provider W1-22): gov doctor on this repository: semantic canary FACET_UNAVAILABLE, a miss; b-dev canaries not run in the exit run (F-M2) | WEAKENED | docs/plan/wave-1-exit/evidence/gov-doctor.json, tests/acceptance/W1-22/test_w1_22_canaries.py |
| CAP-18 Retrieval router (multi-route fusion) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-19/test_w1_19_fusion.py, tests/acceptance/W1-17/test_w1_17_incremental.py |
| CAP-18.a (provider W1-19, W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-19/test_w1_19_fusion.py, tests/acceptance/W1-19/test_w1_19_real_models.py |
| CAP-18.b (provider W1-17, W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-17/test_w1_17_incremental.py, tests/acceptance/W1-17/test_w1_17_parents.py |
| CAP-20 Rebuild guarantee (delete derived, rebuild from git) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-25/test_w1_25_live_session.py |
| CAP-20.a (provider W1-27, W1-25): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-25/test_w1_25_live_session.py, tests/acceptance/W1-25/test_w1_25_record.py |
| CAP-21 Owner-only approval facts (lite of L0-L5 authority levels) (capability): approval facts (CAP-21.a) | WEAKENED | tests/acceptance/W1-11/test_w1_11_approval.py |
| CAP-21.a (provider W1-11): as CAP-01.b: the owner approval fact exists for 10 commits only; every accepted exception rests on the orchestrator transcribing the owner (F-M6) | WEAKENED | docs/DECISION_REGISTER.md, tests/acceptance/W1-11/test_w1_11_approval.py |
| CAP-22.a (provider W1-05, W1-33): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-33/test_w1_33_agent_definitions.py, tests/acceptance/W1-33/test_w1_33_kernel_role_files.py |
| CAP-22.d (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_research_role.py, tests/acceptance/W1-46/README.md |
| CAP-23.a (provider W1-09): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-09/test_w1_09_claims.py, tests/acceptance/W1-09/test_w1_09_review.py |
| CAP-23.c (provider W1-42): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-42/test_w1_42_exit_report.py, tests/acceptance/W1-42/README.md |
| CAP-24 Skill lifecycle and versioning (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-30/test_w1_30_close.py, tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-26/test_w1_26_skill.py |
| CAP-24.a (provider W1-35, W1-30): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_close.py, tests/acceptance/W1-35/test_w1_35.py |
| CAP-24.b (provider W1-35, W1-36): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/test_w1_35_orchestration.py |
| CAP-24.c (provider W1-35, W1-26): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-26/test_w1_26_skill.py, tests/acceptance/W1-35/test_w1_35.py |
| CAP-25 Tool registry and capability memory (lite) (capability): doctor false failure on pytest-xdist (CAP-25.a) | WEAKENED | tests/acceptance/W1-04/test_w1_04_registry_schema.py, tests/acceptance/W1-04/test_w1_04_auto_mode.py, tests/acceptance/W1-48/test_w1_48_claude_code.py |
| CAP-25.a (provider W1-04, W1-06, W1-27): gov doctor reports pytest-xdist found_version null, ok false, while pytest-xdist 3.8.0 (the pin) is installed and ran this audit suite: a false failure (F-M2) | WEAKENED | docs/plan/wave-1-exit/evidence/gov-doctor.json, tests/acceptance/W1-27/test_w1_27_doctor.py |
| CAP-25.b (provider W1-04): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-04/test_w1_04_auto_mode.py, tests/acceptance/W1-04/test_w1_04_install_rule.py |
| CAP-25.d (provider W1-48): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-48/test_w1_48_claude_code.py, tests/acceptance/W1-48/README.md |
| CAP-25.e (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_live_sessions.py, tests/acceptance/W1-46/test_w1_46_research_installs.py |
| CAP-25.f (provider W1-47): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-47/test_w1_47_settings_rules.py, tests/acceptance/W1-47/README.md |
| CAP-25.g (provider W1-47): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-47/test_w1_47_uv_installs.py, tests/acceptance/W1-47/README.md |
| CAP-27 Read/act separation of commands (lite of MCP/A2A/knowledge layers) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-07/test_w1_07_read_act.py |
| CAP-27.a (provider W1-07, W1-32): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-07/test_w1_07_read_act.py, tests/acceptance/W1-32/test_w1_32_status_read_only.py |
| CAP-28 Natural-language intent routing and small command surface (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-32/test_w1_32_command_set.py, tests/acceptance/W1-07/test_w1_07_registry.py |
| CAP-28.a (provider W1-32, W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-32/test_w1_32_command_set.py, tests/acceptance/W1-35/test_w1_35_orchestration.py |
| CAP-28.b (provider W1-07, W1-42): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-07/test_w1_07_registry.py, tests/acceptance/W1-13/test_w1_13_command.py |
| CAP-30.a (provider W1-12, W1-13): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-12/test_w1_12_rows_and_states.py, tests/acceptance/W1-13/test_w1_13_na.py |
| CAP-30.b (provider W1-13, W1-26, W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-13/test_w1_13_gap_tickets.py, tests/acceptance/W1-26/test_w1_26_gap_tickets.py |
| CAP-30.e (provider W1-12, W1-26): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-12/test_w1_12_capability_types.py, tests/acceptance/W1-13/test_w1_13_report.py |
| CAP-30.f (provider W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/README.md |
| CAP-31 Unified task DAG with dynamic generation (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-08/test_w1_08_schemas_exist.py, tests/acceptance/W1-30/test_w1_30_disposition.py, tests/acceptance/W1-09/test_w1_09_ready.py |
| CAP-31.a (provider W1-08, W1-14): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_schemas_exist.py, tests/acceptance/W1-08/test_w1_08_ticket.py |
| CAP-31.b (provider W1-30): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_disposition.py, tests/acceptance/W1-30/test_w1_30_iteration.py |
| CAP-31.c (provider W1-09): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-09/test_w1_09_ready.py, tests/acceptance/W1-09/test_w1_09_review.py |
| CAP-31.d (provider W1-09): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-09/test_w1_09_inputs.py, tests/acceptance/W1-14/test_w1_14_derive.py |
| CAP-32.c (provider W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/README.md |
| CAP-33.a (provider W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py, tests/acceptance/W1-35/test_w1_35.py |
| CAP-33.d (provider W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py, tests/acceptance/W1-35/test_w1_35.py |
| CAP-33.e (provider W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/README.md |
| CAP-33.f (provider W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/README.md |
| CAP-34 Human decision gates and contradiction resolution (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-34/test_w1_34_decision_package.py, tests/acceptance/W1-32/test_w1_32_status_not_read.py, tests/acceptance/W1-11/test_w1_11_citing_files.py |
| CAP-34.a (provider W1-34): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-34/test_w1_34_decision_package.py, tests/acceptance/W1-34/README.md |
| CAP-34.b (provider W1-34): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-34/test_w1_34_decision_package.py, tests/acceptance/W1-34/README.md |
| CAP-34.c (provider W1-34, W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-32/test_w1_32_status_not_read.py, tests/acceptance/W1-34/test_w1_34_decision_package.py |
| CAP-34.d (provider W1-11, W1-34): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-11/test_w1_11_citing_files.py, tests/acceptance/W1-11/test_w1_11_gates.py |
| CAP-34.e (provider W1-09): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-09/test_w1_09_decisions.py, tests/acceptance/W1-09/test_w1_09_unloaded_package.py |
| CAP-37 Structured checkpoints and mandatory triggers (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-25/test_w1_25_record.py, tests/acceptance/W1-25/test_w1_25_triggers.py, tests/acceptance/W1-25/test_w1_25_command.py |
| CAP-37.a (provider W1-25): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-25/test_w1_25_record.py, tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py |
| CAP-37.b (provider W1-25, W1-29): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-25/test_w1_25_triggers.py, tests/acceptance/W1-29/test_session_hooks.py |
| CAP-37.c (provider W1-25, W1-29): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-25/test_w1_25_command.py, tests/acceptance/W1-25/test_w1_25_watch.py |
| CAP-37.d (provider W1-29): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-29/test_session_hooks.py, tests/acceptance/W1-29/README.md |
| CAP-37.f (provider W1-25): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-25/test_w1_25_live_session.py, tests/acceptance/W1-25/test_w1_25_resume.py |
| CAP-37.g (provider W1-49): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-49/test_w1_49_live_session.py, tests/acceptance/W1-49/test_w1_49_precompact.py |
| CAP-38 Verification test families (product and governance) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-30/test_w1_30_close.py, tests/acceptance/W1-15/test_w1_15_family_check.py, tests/acceptance/W1-02/test_w1_02_multiedit.py |
| CAP-38.a (provider W1-30): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_close.py, tests/acceptance/W1-30/README.md |
| CAP-38.b (provider W1-26, W1-15, W1-17, W1-21, W1-24, W1-25, W1-27, W1-30, W1-35, W1-36, W1-38, W1-42): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-15/test_w1_15_family_check.py, tests/acceptance/W1-15/test_w1_15_review_batch.py |
| CAP-38.c (provider W1-30, W1-02): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-02/test_w1_02_multiedit.py, tests/acceptance/W1-02/test_w1_02_test_independence.py |
| CAP-38.d (provider W1-30): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_check_blocks.py, tests/acceptance/W1-30/test_w1_30_governance_checks.py |
| CAP-38.e (provider W1-35): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/README.md |
| CAP-38.f (provider W1-30): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_probe.py, tests/acceptance/W1-30/README.md |
| CAP-39.a (provider W1-40, W1-02): hooks pass their GIT_ environment to child git calls (DEC-710 to DEC-712, FIRST Wave 2 item); after the reinstall of 2026-10-16 09:42 the W1-40 case test_no_lefthook_hook_is_installed_in_this_repository is red and no decision names it (F-M4) | WEAKENED | tests/acceptance/W1-40/test_w1_40_workflow_text.py, docs/DECISION_REGISTER.md |
| CAP-39.d (provider W1-26): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-26/test_w1_26_command.py, tests/acceptance/W1-26/test_w1_26_provenance.py |
| CAP-40 Execution telemetry and organisational questions (capability): governance share not per programme (CAP-40.c) | WEAKENED | tests/acceptance/W1-31/test_w1_31_measured_and_estimated.py, tests/acceptance/W1-31/test_w1_31_share_counter.py |
| CAP-40.a (provider W1-31): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-31/test_w1_31_measured_and_estimated.py, tests/acceptance/W1-31/test_w1_31_second_specimen.py |
| CAP-40.c (provider W1-31, W1-42): governance share measured on ORION-im02 only (4.49 percent); ARGUS missing (accepted, DEC-714); ORION per programme not measured and not accepted; governance-share.json absent (F-M1) | WEAKENED | docs/plan/wave-1-exit/evidence/telemetry-ORION-im02.json, docs/plan/wave-1-exit/EXIT-REPORT.md |
| CAP-40.d (provider W1-31): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-31/test_w1_31_share_counter.py, tests/acceptance/W1-31/README.md |
| CAP-41 Lesson records with scope (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-08/test_w1_08_frontmatter.py, tests/acceptance/W1-44/test_w1_44_lessons.py, tests/acceptance/W1-08/test_w1_08_lesson.py |
| CAP-41.a (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_frontmatter.py, tests/acceptance/W1-08/test_w1_08_lesson.py |
| CAP-41.b (provider W1-44): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-44/test_w1_44_lessons.py, tests/acceptance/W1-44/README.md |
| CAP-41.c (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_lesson.py, tests/acceptance/W1-08/README.md |
| CAP-41.d (provider W1-44): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-44/test_w1_44_lessons.py, tests/acceptance/W1-44/README.md |
| CAP-41.f (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_lesson.py, tests/acceptance/W1-08/README.md |
| CAP-42 Legacy governance retirement and archive policy (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-41/test_w1_41_legacy.py |
| CAP-42.a (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_legacy.py, tests/acceptance/W1-41/README.md |
| CAP-42.b (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_legacy.py, tests/acceptance/W1-41/README.md |
| CAP-42.c (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_legacy.py, tests/acceptance/W1-41/README.md |
| CAP-43 Canonical OS repo separation and immutable releases (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-39/test_w1_39_layout.py |
| CAP-43.a (provider W1-39): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-39/test_w1_39_layout.py, tests/acceptance/W1-39/README.md |
| CAP-44.a (provider W1-39): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-39/test_w1_39_copy.py, tests/acceptance/W1-39/README.md |
| CAP-44.b (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_baseline.py, tests/acceptance/W1-41/test_w1_41_path_map.py |
| CAP-44.c (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_verdict.py, tests/acceptance/W1-41/README.md |
| CAP-44.d (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_migration.py, tests/acceptance/W1-41/README.md |
| CAP-44.e (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_legacy.py, tests/acceptance/W1-41/README.md |
| CAP-44.j (provider W1-41): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-41/test_w1_41_path_map.py, tests/acceptance/W1-41/README.md |
| CAP-46 Cross-machine sync via git (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-27/test_w1_27_rebuild.py |
| CAP-46.a (provider W1-27): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-27/test_w1_27_rebuild.py, tests/acceptance/W1-27/README.md |
| CAP-47.b (provider W1-36): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-36/test_w1_36_audit_skill.py, tests/acceptance/W1-36/README.md |
| CAP-47.d (provider W1-13, W1-35, W1-36): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-13/test_w1_13_close.py, tests/acceptance/W1-35/test_w1_35.py |
| CAP-49.b (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_duplicate_keys.py, tests/acceptance/W1-46/test_w1_46_held_out.py |
| CAP-49.c (provider W1-47): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_duplicate_keys.py, tests/acceptance/W1-47/test_w1_47_kernel_template.py |
| CAP-50.a (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_frontmatter.py, tests/acceptance/W1-08/README.md |
| CAP-50.c (provider W1-30): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_receipt.py, tests/acceptance/W1-30/README.md |
| CAP-51 Decisions register (structured, versioned, authoritative) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-11/test_w1_11_b_dev.py, tests/acceptance/W1-21/test_w1_21_authority.py |
| CAP-51.a (provider W1-11): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-11/test_w1_11_b_dev.py, tests/acceptance/W1-11/test_w1_11_hazards.py |
| CAP-51.b (provider W1-21): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-21/test_w1_21_authority.py, tests/acceptance/W1-21/README.md |
| CAP-52 Model-agnostic adapters (provider, IDE, CLI) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-38/test_w1_38_rulesync.py, tests/acceptance/W1-38/README.md |
| CAP-52.a (provider W1-38): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-38/test_w1_38_rulesync.py, tests/acceptance/W1-38/README.md |
| CAP-52.b (provider W1-38): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-38/README.md |
| CAP-53.a (provider W1-13, W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_schemas_exist.py, tests/acceptance/W1-08/test_w1_08_ticket.py |
| CAP-53.c (provider W1-31): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-31/test_w1_31_measured_and_estimated.py, tests/acceptance/W1-31/test_w1_31_share_counter.py |
| CAP-54 Progressive adoption (day-one to maturity) (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-27/test_w1_27_adoption.py, tests/acceptance/W1-08/test_w1_08_floor.py |
| CAP-54.a (provider W1-27): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-27/test_w1_27_adoption.py, tests/acceptance/W1-27/test_w1_27_doctor_unmeasured_r3.py |
| CAP-54.b (provider W1-08): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-08/test_w1_08_floor.py, tests/acceptance/W1-08/README.md |
| CAP-55 Retrieval stopping reasons (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-21/test_w1_21_bundle.py |
| CAP-55.a (provider W1-21, W1-22): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-21/test_w1_21_bundle.py, tests/acceptance/W1-21/test_w1_21_closure_and_gaps.py |
| CAP-56 Retrieval in disposable subagent context (capability): acceptance sentence untested (CAP-56.a) | WEAKENED | tests/acceptance/W1-36/test_w1_36_retrieval_skill.py |
| CAP-56.a (provider W1-36): tested on the skill text only; no test reads a main-session transcript as the CAP-56 acceptance asks (F-m) | WEAKENED | tests/acceptance/W1-36/test_w1_36_retrieval_skill.py |
| CAP-57 Deterministic worklist closure for facets (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-20/test_w1_20_code.py |
| CAP-57.a (provider W1-20, W1-22): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-20/test_w1_20_code.py, tests/acceptance/W1-20/test_w1_20_determinism.py |
| CAP-58 Path guards as default-deny allow-lists (capability): guard known-tool list lacks SubagentHandback (CAP-58.c) | WEAKENED | tests/acceptance/W1-02/test_w1_02_allow_list.py, tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py, tests/acceptance/W1-02/test_w1_02_multiedit.py |
| CAP-58.a (provider W1-02, W1-03, W1-26): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-02/test_w1_02_allow_list.py, tests/acceptance/W1-03/test_w1_03_finding_record.py |
| CAP-58.b (provider W1-33): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py, tests/acceptance/W1-33/test_w1_33_kernel_role_files.py |
| CAP-58.c (provider W1-02): unknown-tool default deny (DEC-685) refuses SubagentHandback, so a helper return cannot be handed back under the guard; no check compares the known-tool list with the installed CLI (F-M7) | WEAKENED | src/gov/guard/decide.py, tests/acceptance/W1-02/test_w1_02_unknown_role.py |
| CAP-58.d (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_guard_wiring.py, tests/acceptance/W1-46/test_w1_46_live_sessions.py |
| CAP-58.e (provider W1-45): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-45/test_w1_45_containment.py, tests/acceptance/W1-45/test_w1_45_orchestrator_scope.py |
| CAP-58.f (provider W1-47): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-47/test_w1_47_failed_commands.py, tests/acceptance/W1-47/test_w1_47_kernel_template.py |
| CAP-58.h (provider W1-50): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-50/test_w1_50_author_chosen_bytes.py, tests/acceptance/W1-50/test_w1_50_committed_path_names.py |
| CAP-59 Review-repair loop budget (capability): W1-43 part untested and not yet run (CAP-59.a, CAP-59.b) | WEAKENED | tests/acceptance/W1-30/test_w1_30_iteration.py, tests/acceptance/W1-30/test_w1_30_disposition.py |
| CAP-59.a (provider W1-30, W1-43): W1-30 part tested; the W1-43 part (audit to repair loop) has no tests/acceptance/W1-43 and has not run yet (F-M10) | WEAKENED | tests/acceptance/W1-30/test_w1_30_iteration.py, .tickets/DAEO-03pw.md |
| CAP-59.b (provider W1-30, W1-43): W1-30 part tested; the auditor saw no iteration count (DEC-096 held in this audit); the W1-43 part has no acceptance test (F-M10) | WEAKENED | tests/acceptance/W1-30/test_w1_30_iteration.py, .tickets/DAEO-03pw.md |
| CAP-59.c (provider W1-30, W1-44): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-30/test_w1_30_disposition.py, tests/acceptance/W1-44/test_w1_44_lessons.py |
| CAP-61 Worker session launcher and OS sandbox (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-46/test_w1_46_sandbox_settings.py, tests/acceptance/W1-46/test_w1_46_guard_wiring.py, tests/acceptance/W1-46/test_w1_46_live_sessions.py |
| CAP-61.a (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_sandbox_settings.py, tests/acceptance/W1-46/README.md |
| CAP-61.b (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_guard_wiring.py, tests/acceptance/W1-46/test_w1_46_live_sessions.py |
| CAP-61.c (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_live_sessions.py, tests/acceptance/W1-46/test_w1_46_research_allowlist.py |
| CAP-61.d (provider W1-46): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-46/test_w1_46_live_sessions.py, tests/acceptance/W1-46/test_w1_46_role_settings.py |
| CAP-61.e (provider W1-48): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-48/test_w1_48_cli.py, tests/acceptance/W1-48/test_w1_48_drift.py |
| CAP-62 Sandbox escape hatch denied (capability): delivered by closed tickets; covers items tested | OK | tests/acceptance/W1-47/test_w1_47_escape_hatch.py |
| CAP-62.a (provider W1-47): delivered and closed; acceptance test cites it | OK | tests/acceptance/W1-47/test_w1_47_escape_hatch.py, tests/acceptance/W1-47/test_w1_47_kernel_template.py |
| DEC-070 contested and owner-level findings go to the owner as decision packages: this report gives each MAJOR finding an owner question | OK | docs/DECISION_REGISTER.md |
| DEC-088 audit names its milestone, one row per contract item: milestone wave-1-exit; 149 covers items, 42 W1 capabilities and 6 MR clauses each have a row | OK | docs/DECISION_REGISTER.md, docs/contract/contract.yaml |
| DEC-092 every W1 covers item gets a finding row: every covers item has a closed provider and an acceptance test that cites it (CAP-52.b through the W1-38 README map) | OK | docs/contract/contract.yaml, tests/acceptance/W1-38/README.md |
| DEC-096 loop count held by the orchestrator, never disclosed: the auditor read no iteration or escalation record and was told no count | OK | docs/DECISION_REGISTER.md |
| DEC-430 the owner reading of MR-3: stated in this report and in the audit skill; the W1-43 brief did not state it, as W1-43 KPI line 3 requires (F-m) | WEAKENED | .tickets/DAEO-03pw.md, template/governance/kernel/skills/audit/SKILL.md |
| DEC-441 audit-report form: this report follows src/gov/check/audit_validator.py and passes it (audit reproducibility GREEN on the re-run) | OK | src/gov/check/audit_validator.py |
| The audit-report form against the schema check (core-schema): core-schema reads every frontmatter Markdown under docs and knows no audit-report type, so a report in the DEC-441 form is SCHEMA_INVALID_TYPE (hard-block G1) and the pre-commit hook refuses it (F-M13) | CONTRADICTS | src/gov/check/schema.py, template/governance/kernel/checks/core-schema.yaml |
| DEC-522 from adoption every ticket closes only through a clean gov close: no CL record exists in any history; all seven closes after 1c33dd28 used tk close, each under an owner decision (DEC-651 DEC-683 DEC-689 DEC-690 DEC-703 DEC-717); none is in the DEC-714 block; the one clean gov close is ORION-im02 in the a-dev clone (F-M3) | WEAKENED | docs/plan/wave-1-exit/evidence/close-ORION-im02.json, docs/DECISION_REGISTER.md |
| W1-30 final close 6eff3a00 (2026-10-11 23:25): tk close past ESCALATION_BLOCKED exit 4 with no Role trailer; DEC-651 ratified it the next morning (4b18d562), after the fact (F-M3) | CONTRADICTS | docs/DECISION_REGISTER.md, governance/project/bootstrap.md |
| DEC-465 who pushed w1/integrate: covers the pushes up to 2026-10-07 (13 by the remote reflog, not 12); c7e5c3ed (10-09), 3acc863f (10-10) and 60ea6924 (10-16 09:43, 29 s after the hooks were reinstalled) have no record of who pushed (F-M9) | WEAKENED | docs/DECISION_REGISTER.md |
| DEC-412 never rewrite w1/integrate: 19 amends of merge commits on w1/integrate between 2026-10-07 22:32 and 2026-10-14 00:48 (branch reflog); none pushed before its amend (F-m) | CONTRADICTS | docs/DECISION_REGISTER.md |
| DEC-685 guard default deny of unknown tools: fail closed on SubagentHandback: all three helper returns of this audit were refused (F-M7) | WEAKENED | src/gov/guard/decide.py, docs/DECISION_REGISTER.md |
| DEC-096 and CAP-59.a loop budget applied to refused calls: a helper of this audit made 58 identical refused SubagentHandback calls before the auditor stopped it; neither briefs nor the refusal text say to stop (F-M12) | WEAKENED | docs/DECISION_REGISTER.md, src/gov/guard/decide.py |
| DEC-704 ORION-im01 closed with tk close: owner decision; the trailer-gate base is on the Wave 2 list | OK | docs/DECISION_REGISTER.md, docs/plan/wave-1-exit/evidence/close-ORION-im01-refused-run7.json |
| DEC-710 to DEC-712 the hook incident: recorded; two foreign commits kept on the w1/W1-42 reflog; hook git environment is the FIRST Wave 2 item | OK | docs/DECISION_REGISTER.md, docs/plan/wave-1-exit/EXIT-REPORT.md |
| DEC-713 W1-42 merged with three named reds: the worktree-list red now passes (this audit regression); RETR-X-02 and the share stay red | OK | docs/DECISION_REGISTER.md, docs/plan/wave-1-exit/evidence/git-worktree-list.txt |
| DEC-714 intended exit and adoption-readiness block: block present in the exit report with ARGUS, the three a-dev reds, RETR-X-02, the ARGUS share and the hook item, each with what closes it; it does not hold the unaccepted items of F-M1 to F-M13 | OK | docs/plan/wave-1-exit/EXIT-REPORT.md, docs/DECISION_REGISTER.md |
| DEC-716 no run 8c: this audit ran the full regression in its place: 3 failed, 13189 passed, 31 skipped in parallel, then 263 passed serial-only; the third red is F-M4 | OK | docs/DECISION_REGISTER.md, tests/acceptance/serial-only.txt |
| DEC-717 W1-42 closed with tk close, 22 findings named: the 22 findings are named; gov check product traceability is red on exactly the eight DAEO-gjjf trailer commits it names; PROBE_MISSING stood in for by this audit | OK | docs/DECISION_REGISTER.md, .tickets/DAEO-gjjf.md |
| DEC-668 and DEC-707 owner freeze, pause and lift checks: B1, B2 part 1 and B2 part 2 recorded with output | OK | docs/plan/wave-1-exit/evidence/owner-freeze-check.json, docs/DECISION_REGISTER.md |
| DEC-360 owner approval fact: see CAP-21.a (F-M6) | WEAKENED | docs/DECISION_REGISTER.md |
| DEC-414 hit@5 pass line 80: measured 83.33, above 80, below the 85 baseline (F-m on re-baselining CAP-10) | OK | docs/plan/wave-1-exit/evidence/retrieval-hit5.json, docs/DECISION_REGISTER.md |
| DEC-091 named parent expansions: RETR-X-02 bundle has none; accepted exception under DEC-714 | WEAKENED | docs/plan/wave-1-exit/evidence/RETR-X-02.json, docs/DECISION_REGISTER.md |
| DEC-086 governance share at most 15 percent per programme: ORION-im02 4.49 percent (verified: 4834 governance of 107575 tokens); per programme not measured (F-M1) | WEAKENED | docs/plan/wave-1-exit/evidence/telemetry-ORION-im02.json, docs/DECISION_REGISTER.md |
| DEC-376 DEC-385 DEC-508 held-out exposures: every exposure recorded under an owner decision; no record shows held-out content displayed to an agent; the auditor never read it | OK | docs/DECISION_REGISTER.md, governance/project/bootstrap.md |
| Wave 2 list and adoption-readiness block (DEC-712, DEC-714): no single list with a severity per item; the exit report itself names residuals that are on no list yet (F-M8) | MISSING | docs/plan/wave-1-exit/EXIT-REPORT.md, governance/project/bootstrap.md |
| Compliance report of the orchestrator: pinned at 3021a87e (2026-10-07): 47 rows checked, 31 confirmed, 15 partly, 1 unverifiable, none false; base counts wrong (40 tickets closed, not 43; 13 pushes, not 12); nothing after 2026-10-07 (F-m) | WEAKENED | docs/DECISION_REGISTER.md, governance/project/bootstrap.md |

## Findings

Classes: BLOCKER means Wave 1 cannot close. MAJOR means it closes only with an accepted exception and a Wave 2 owner. MINOR means neither. Under DEC-584 every finding goes to the owner, with a recommendation for the Wave 2 list. The only file the auditor fixed is this report.

### BLOCKER

None. No MR-3 breach was found: test-folder history, merges and clones all checked. Nothing shows held-out content displayed to an agent. ORION-im02's clean `gov close` (exit 0, no exception), the retrieval measurements and the governance-share arithmetic all reproduce from the evidence. The exit report does not overstate: its own verdict is NOT MET.

### MAJOR

- **F-M1: Governance share is not measured per programme for ORION, and no exception accepts that.**
  - **What:** criterion 4 and DEC-086 ask for a share of at most 15 % on each programme's run. The one measured total is ORION-im02's.
    - The auditor recomputed it: governance 1,482 measured plus 3,352 estimated, giving 4,834. The denominator is input, output and cache creation, 32 + 19,644 + 87,899 = 107,575, so the share is **4.49 %**.
    - ORION's other tickets (ORION-im01, the specification and test sessions) are not measured, and `docs/plan/wave-1-exit/evidence/governance-share.json` does not exist.
  - **Decisions:** DEC-714 accepts only ARGUS's missing share. DEC-713 keeps the per-programme share "as NOT MET evidence", which is not an acceptance.
  - **To close:** the owner accepts ORION's per-programme share as a named exception, with what closes it (a measured run share), or orders the measurement.
- **F-M2: `gov doctor` is not green on this repository, and three of its four causes are on no list.**
  - **What:** four causes.
    - **tools:** a false failure. pytest-xdist 3.8.0 is installed and ran this audit's suite, but doctor reads `found_version null`.
    - **path_compliance:** four files cite the moved `docs/audit/wave-1/adoption-path-map-verdict.md`: `gov-commands.json`, `gov-doctor-run1.json` and `gov-doctor.json` in the exit evidence, and the A5 review record under `governance/adoption/`.
    - **canaries:** the semantic canary misses (`FACET_UNAVAILABLE`).
    - **drift:** CLI against extension.
  - **Decisions:** only the drift is on the Wave 2 list (DEC-667). The exit report marks doctor NOT MET, and no owner decision accepts it.
  - **To close:** an accepted exception naming the three causes, with a Wave 2 owner, or a repair ticket. Fixing the citations is a documentation fix for product-spec; the canary and the tools reading are product fixes.
- **F-M3: No Wave 1 ticket closed through a clean `gov close`, against DEC-522 and W1-42's KPI line.**
  - **The record:**
    - no close record (CL-*) exists in any history of this repository;
    - all seven closes after the adoption commit `1c33dd28` used `tk close`: W1-30 `6eff3a00`, W1-38 `1abc4f2d` and later `1ca20b00`, W1-31 `de7bbb79`, W1-02 `8a00f832`, W1-41 `6506b7ce`, W1-42 `c215459d`;
    - each is under an owner decision (DEC-651, DEC-683, DEC-689, DEC-690, DEC-703, DEC-717), but none is in DEC-714's adoption-readiness block, and the exit report does not say what closes this as a whole.
  - **W1-30's final close `6eff3a00`:**
    - it went past an `ESCALATION_BLOCKED` owner stop (exit 4);
    - it has no `Role:` trailer;
    - DEC-651 ratified it the next morning (`4b18d562`), after the fact. It is the CONTRADICTS row of the table.
  - **What the evidence still shows:** the one clean `gov close` anywhere is ORION-im02, in the archived a-dev clone. That proves the command works, not that the method held in this repository.
  - **To close:** the owner adds "every ticket through a clean `gov close`" to the adoption-readiness block, with what closes it: a Wave 2 ticket closed cleanly in this repository, after DEC-704's trailer-gate fix.
- **F-M4: An unnamed red case in the regression.**
  - **What:** `tests/acceptance/W1-40/test_w1_40_workflow_text.py::test_no_lefthook_hook_is_installed_in_this_repository` is red at the audited head. It turned red when the hooks were reinstalled on 2026-10-16 at 09:42:38, as DEC-712 ordered; the test's own docstring makes activating the hooks the owner's step at the exit.
  - **Decisions:** no decision names this red. DEC-717 counted 2 reds; this audit counts 3.
  - **To close:** the independent test designer retires or restates the case (MR-3, DEC-136), or the owner names it as an exception.
- **F-M5: The context packet breaks its ceiling and reports success.**
  - **What:** `gov context DAEO-03pw` returns `ok: true` with tokens 814,821 against a budget of 6,000 (CAP-15, CAP-15.d).
    - Every DEC id resolves to the whole decision register, so all four decisions carry the same sha256 (`cd983b…`).
    - The ticket's own text is among the 20 dropped items.
    - The decision hash therefore pins the register, not the decision, and the packet a worker receives is not bounded.
  - **Lists:** this is on no list.
  - **To close:** a Wave 2 item, ranked high because every worker brief rests on it: resolve each decision to its own entry, and refuse or block when the mandatory inputs exceed the ceiling.
- **F-M6: Owner approvals are transcribed, not owner git facts (CAP-01.b, CAP-21.a, DEC-360).**
  - **What:** the register holds 713 entries, of which 466 read "ACCEPTED (owner …)".
    - They are committed under `Role: orchestrator`.
    - Only 10 commits in the repository carry `Role: owner`, and one of them touches the register (`700bb5b5`).
    - No entry is ever `ACTIVE`, so the approval gate (which fires on a commit setting ACTIVE) judged no Wave 1 decision.
  - **Why it matters:** every accepted exception, DEC-714 included, rests on the orchestrator's transcription of the owner's word. The auditor cannot verify any of them from git.
  - **To close:** the owner records the exit decision in a commit carrying `Role: owner`. A Wave 2 item makes register acceptances owner git facts, or states the owner's reading.
- **F-M7: The guard's known-tool list lacks SubagentHandback (DEC-685).** Raised by the owner; the severity is the auditor's.
  - **What:** the guard's default deny (`src/gov/guard/decide.py`, the DEC-685 branch) refuses SubagentHandback to every role. SubagentHandback only returns a helper's message to its caller.
    - All three helpers of this audit had their returns refused; the reports survived only in their transcripts.
    - This is a fail-closed defect that blocks ordinary work wherever Claude Code's agent teams are enabled.
    - No check compares the guard's list with the installed CLI's tool list when the CLI version changes (CAP-61.e detects version drift only).
  - **To close:** a Wave 2 item: add the tool through the CIT-P route, and add a check against the CLI's tool list at each version change.
- **F-M8: There is no consolidated Wave 2 list with a severity per item (DEC-712, DEC-714).**
  - **What:** the Wave 2 items are spread across the bootstrap record's Wave 2 list, the exit report's block and individual decisions (DEC-667, DEC-704, DEC-715, DEC-716).
    - The exit report itself names residuals that are "not on any list yet": lexical phrase matching, `test_exact_agreement`, the doctor's pytest-xdist reading, the stale store after `tk close`, context reproducibility depending on the store, no hook on merge commits, and `gov --help` saying check is not built.
    - This audit adds F-M1 to F-M13 and the MINOR findings.
  - **To close:** one list, each item with a severity, an owner and what closes it. A product-spec or orchestrator task, under the owner's ranking.
- **F-M9: Outward actions after 2026-10-07 are unrecorded.**
  - **What:** the remote reflog shows 16 pushes of `w1/integrate`. DEC-465 covers those up to 2026-10-07 (13, not the 12 it says). Three later pushes have no record of who made them:
    - `c7e5c3ed` on 10-09;
    - `3acc863f` on 10-10;
    - `60ea6924` on 10-16 at 09:43:07, after DEC-717's "the orchestrator stays idle", 29 s after the hooks were reinstalled and 3 s after a git note was written.
  - **Lists:** the reinstall itself has no register entry. No containment record shows an agent `git push`.
  - **To close:** if these were the owner's, a record like DEC-465 makes this MINOR.
- **F-M10: W1-43's own acceptance tests do not exist.**
  - **What:** `tests/acceptance/W1-43/` is missing, although the ticket names it.
    - The W1-43 part of CAP-59.a and CAP-59.b (the audit→repair loop) is untested and has not run yet.
    - `gov close DAEO-03pw` will refuse with no acceptance tests, so a clean close of this ticket is not possible as things stand.
  - **To close:** the test designer writes the cases, or the owner names this ticket's close as an exception.
- **F-M11: FULL tickets have no probe or review evidence (MR-4, DEC-137).**
  - **What:** neither the repository nor its history holds a probe or review record for W1-16 (DAEO-lkeb) or W1-21 (DAEO-5x4l), and no decision excuses them. The W1-26 follow-ups (`80ddf4d5`, `b355fa24`) and the W1-50 follow-up (`f270e3c9`) also show none.
  - **Context:** before DEC-565 (2026-10-09), probes were recorded only in prose. W1-42's missing probe is excused by DEC-717, which lets this audit stand in for it; this audit found no defect in W1-42's deliverable beyond the named reds and F-M4.
  - **To close:** the owner rules whether the lead logs outside the repository hold these reviews, or accepts them as named exceptions.
- **F-M12: A helper retried one refused call 58 times (DEC-096, CAP-59.a).** Raised by the owner; the severity is the auditor's.
  - **What:** this audit's close-history helper made 58 identical SubagentHandback calls before the auditor stopped it. The count is of distinct tool calls in its transcript.
    - Those turns read 11,994,916 cached tokens; their input, output and cache creation came to 16,312 tokens.
    - The other two helpers made 6 and 3 such calls.
    - The owner's estimate was about 53 calls and about 257k tokens; the transcript gives the figures above.
  - **Why:** neither the briefs (the auditor's own included) nor the guard's refusal text tell an agent to stop retrying a refusal. The auditor also stopped the helper late.
  - **To close:** a Wave 2 item. The refusal text says the refusal is final for that call, and briefs carry a rule to stop after two identical refusals. An optional loop counter on identical refused calls would back it.

- **F-M13: No audit report in the DEC-441 form can be committed through the hook.**
  - **The schema conflict:** `src/gov/check/schema.py` reads every Markdown file with frontmatter under `docs/` and `.tickets/` and requires a known `type`. Its map has no audit-report type.
    - This report, in the form the audit skill and the validator ask for, therefore makes schema/invariants (G1, hard-block) red.
    - Adding a `type` would only change the finding to an unknown type with missing `id`, `status` and `state_class`. The auditor does not work round the check.
  - **The traceability block:** with the hooks reinstalled (DEC-712), the pre-commit hook runs `gov ci checks G1 G2`, and G1 holds product traceability. That check is red on eight history commits that DEC-717 accepts. So every commit in this repository, not only this one, meets a red hard-block check.
  - **Effect:** every STANDARD and FULL feature audit and every wave exit audit meets the same conflict.
  - **To close:** a product fix: an audit-report record type known to the schema check. Ticket closes and accepted history also need to stop blocking all later commits.
  - **What happened:** the hook refused this report's commit on exactly these two checks (see "What the auditor ran").
  - **Interim:** an owner decision on how this report is committed. For example, the owner commits it with an owner-recorded exception, or orders the product fix first.

### MINOR

- **F-m1:** the W1-43 brief did not state DEC-430, as W1-43's third KPI line requires. The audit skill states it, and so does this report.
- **F-m2:** CAP-10's contract acceptance is a mean hit@5 of 85. DEC-414 sets the pass line at 80, and the measured value is 83.33. The contract is not re-baselined (DEC-105). Separately, the exit report's "callers/impact 100.0" is a single-class figure beside 87.5 for all code classes (14 of 16).
- **F-m3:** CAP-56's acceptance sentence asks that the main session's transcript on RETR-X-02 holds the bundle and no intermediate batch. No test reads a transcript; CAP-56.a is tested on the skill text only.
- **F-m4:** 19 amends of merge commits on `w1/integrate` (branch reflog, 2026-10-07 22:32 to 2026-10-14 00:48), against DEC-412's "never rebase w1/integrate". None was pushed before its amend.
- **F-m5:** the compliance report (`COMPLIANCE.md`, pinned at `3021a87e`, 2026-10-07) is stale.
  - It records nothing after 2026-10-07, and its base counts are wrong: 40 tickets closed, not 43; 13 pushes, not 12; DEC-323 is not a digest of DEC-266 to DEC-270.
  - Of its 47 deviation rows, 31 are confirmed, 15 partly confirmed and 1 unverifiable; none is false. 40 sampled claims from sections A and B: 33 confirmed, 6 partly, 1 unverifiable. Many of its "Fix: none found" cells were answered by DEC-460 to DEC-466 the same day.
- **F-m6:** trailer findings outside DEC-717.
  - 20 register commits and the close commits `1abc4f2d` and `6eff3a00` carry no `Role:` trailer.
  - `4b18d562` credits Opus 4.6 after DEC-460.
  - Close commit `a7964c97` (W1-23) has `Task: decision-record`; `f338b1a2` closes W1-25 under `Task: DAEO-zsvl` only.
  - Before adoption, close commit `abcb3095` cites DEC-594 one commit before it was recorded.
- **F-m7:** the orchestrator's main session records its writes under the closed ticket DAEO-6cc2 (W1-45) in the containment records. Ticket leads still run as role orchestrator: DEC-434 is unbuilt (MR-5).
- **F-m8:** repair tickets DAEO-52q7 and DAEO-ldvk were moved out of `.tickets/` into the orchestrator's scratch log. Only DEC-717's basis mentions it.
- **F-m9:** the Charter, the Contract and the WBS still carry status PROPOSED in their frontmatter while they serve as the yardstick.
- **F-m10:** in the a-dev clone, ORION's merge `736669f` was the lead's, made after a red CI, not an owner merge. DEC-714 accepts the reds, but no decision says the lead's merge stands for criterion 1's "owner merge".

## Exit criteria

The audit-report form allows exactly one pipe table (`src/gov/check/audit_validator.py`), so the exit criteria are listed here instead of tabled. "Accepted" means an ACCEPTED owner decision names the exception and the exit report states what closes it.

1. **Spec-first cycle end to end on both programmes: MET WITH ACCEPTED EXCEPTIONS, and one unaccepted residual.**
   - ORION ran every step: discovery, a closed specification, two fresh specification audits (`a-audit.json`, `a-audit2.json`), tickets with gap tickets, the designer's tests (red at `f49924a`), implementation (green at `6a78498`), a clean `gov close` of ORION-im02, CI and the merge.
   - Accepted under DEC-714: ARGUS stops at the close, and a-dev's CI is red on three checks.
   - ORION-im01's `tk close` is accepted by DEC-704.
   - Unaccepted residual: the merge was the lead's, after a red CI (F-m10).
2. **RETR-A-04 and RETR-X-02 run: MET WITH AN ACCEPTED EXCEPTION.**
   - RETR-A-04 has batches, citations by id and sha256, three named parent expansions and a stopping reason.
   - RETR-X-02 has no parent expansion, accepted under DEC-714 with its closing condition stated.
3. **MR-3 containment holds: MET.**
   - The exit evidence is `mr3.json` and `worker-sessions.json`.
   - This audit's own history check: every non-merge commit touching `tests/acceptance/` is the designer's, no merge adds its own change there, and the clones show only designer commits on their test folders.
4. **Governance share ≤ 15 % on each programme: NOT MET.**
   - ARGUS's missing share is accepted (DEC-714).
   - ORION's per-programme share is not accepted (F-M1). ORION-im02 alone is 4.49 %.
5. **Independent wave-exit audit against Contract v4: MET by this report, with the audit→repair loop still to run (F-M10).**
   - Every W1 capability, W1 covers item and MR clause has a row.
   - The MAJOR findings go to the owner below.
6. **`gov doctor` green on this repository: NOT MET**, and not accepted (F-M2).
7. **Dev-tier canaries hit, no canary secret in a derived store: NOT MET.**
   - b-dev's canaries were not run. This sits inside the accepted ARGUS line, which says so.
   - This repository's semantic canary misses, unaccepted (F-M2).
   - No dev canary secret was found in any derived store: secrets indexing is GREEN on the second `gov check` run.
8. **`gov check` reports 17 of 17 families with an executable check, and all twelve Wave 1 commands are implemented: MET.**
   - All 17 families report. Evidence: `gov-check.json` and `gov-commands.json` in the exit evidence, and this audit's own run.
   - At the head the check is red, mostly on findings DEC-717 names; see "Re-runs".
9. **W1-42 KPI, "a ticket closes only through a clean gov close": NOT MET** (F-M3).
   - The owner's freeze, pause and lift checks are met (DEC-668, DEC-707, `owner-freeze-check.json`).
10. **W1-43 KPI lines:**
    - the fresh read-only audit with a verdict: MET by this report;
    - the audit→repair loop: not yet run (F-M10);
    - DEC-430 stated in the brief: NOT MET in the brief, met in this report (F-m1).

## Verdict

**FAIL as the record stands at `60ea6924`. No finding is a BLOCKER.**

- **Why FAIL:** three exit criteria are NOT MET without an accepted exception: criterion 4 for ORION, the doctor (6), and W1-42's clean-close KPI. Thirteen MAJOR findings have no accepted exception and no Wave 2 owner yet.
- **Why no BLOCKER:** the deliverables the wave was for are built and tested.
  - All 149 W1 covers items are delivered and cited by an acceptance test.
  - The suite gives 13,189 passed against 3 reds, two of them named.
  - MR-3 held.
  - The key proofs reproduce: ORION-im02's clean close, retrieval, the share arithmetic and the owner's freeze checks.
- **What would make it PASS WITH ACCEPTED EXCEPTIONS:** one owner decision, committed with `Role: owner`, that accepts F-M1 to F-M13 as named exceptions. Each needs what closes it and a Wave 2 owner on one consolidated Wave 2 list with severities (F-M8). That turns this verdict into PASS WITH ACCEPTED EXCEPTIONS without further audit work.

## Recommendations to the owner

1. Decide whether to accept the exit with exceptions (option a), or repair first (option b).
   - **Option b, the repairs:** F-M2's citations and doctor reading, F-M4's test (by the test designer), F-M10's tests and F-M5's packet.
   - **Cost:** option (a) costs one owner commit; option (b) costs about four tickets and a re-audit of the changed rows.
   - **Recommendation:** option (a). F-M3, F-M5, F-M6, F-M7, F-M12 and F-M13 go into the adoption-readiness block, before any pilot adoption, beside DEC-712's FIRST item. They affect every adopted project.
2. Record who made the three pushes and the hook reinstall (F-M9), as DEC-465 did.
3. Rule on the probe gaps of W1-16 and W1-21 (F-M11).
4. Have the test designer write `tests/acceptance/W1-43/`, or name this ticket's `tk close` as an exception (F-M10).
