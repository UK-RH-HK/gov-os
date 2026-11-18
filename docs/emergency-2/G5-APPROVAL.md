# G5: Charter v6 and Contract v5, for the owner's approval by group

`docs/emergency-2/G5-APPROVAL.md` · 2026-11-18 · the owner decided in DEC-1214: **G5 (a)**, Charter v6 and Contract v5 in one change, approved by group; **G6 (a)**, **L3 (a)**, **M1 (c)**, **G7 (c)**, T1 to T3, Q-UPD and Q-CLOSE as recorded.

Branch `e2/g4-g5`, worktree `/home/usain/gov-os-worktrees/E2-g4-g5`. Nothing is on `w2/integrate` yet. Both documents say `status: PROPOSED`: no agent may set a decision or a Contract ACCEPTED (CAP-21), so the status flips only after your yes.

## How to answer

One line, for example: **`G5-1 yes, G5-2 yes, G5-3 yes, ...`** (or `G5 all yes`). A `no` names what to change. Each group below is one commit (or two) on the branch, so a `no` is a revert of that commit, followed by `python3 docs/contract/tools/gen_contract.py --write`, which regenerates the 308 capability records, the 6 master-rule records and the Contract text from `contract.yaml`.

Every clause's new wording is in `docs/emergency-2/audits/07-contract-rebaseline.md` (Table 1 and Table 2), applied as written except where the last column says otherwise. "Rows" are lines of `contract.yaml` (a capability, a covers item, a master rule or an envelope clause); "Charter" counts the Charter v6 paragraphs or table rows changed.

| Code | Group | What changes | Rows | Charter | Risk | Commit |
|---|---|---|---|---|---|---|
| **G5-0** | Names and version | `CONTRACT_v5.md`, id `CONTRACT-v5`, version 5.0; `CHARTER_v6.md`; the path map, the two ADRs' cross-references and all 308 generated records follow (275 said "4.3" by mistake; now one version). Alternative, as 4.4 did: keep the file names and ids and bump only the version. | all files, no clause | the title | Low. Collateral: 9 test files and 12 memory-evaluation fixture files name the old file `CONTRACT_v4.md`; 4 tests fail on it (red list below) | `889da33d0`, `6aa8fcfe7` |
| **G5-1** | No guard, no sandbox, no box (§2.2 to §2.4) | §2 Boundary rewritten (git history, your push and release, two deny lines, hourly bundles). CAP-58 a to g, CAP-61 a, c, f, CAP-62, CAP-25 e to g and CAP-40.d are dropped (kept as `NONE` items with the reason, so every id still resolves; CAP-62 becomes a DROP capability like CAP-26). CAP-61, CAP-58.h, CAP-22.d, CAP-32.c, CAP-38.b, CAP-39.a, CAP-52 reworded. Two ADRs get an amendment note. | 26 | 5 | Low: all of it follows EMERGENCY-2 §2. One judgment (audit 7 C-6, the CTO's recommendation): a path outside the ticket's allowed paths is a **notice** at the landing, never a refusal; only a test-authorship breach is refused | `92630a7da` |
| **G5-2** | Pause (§9.2) | CAP-05 says what `gov pause` must stop: `gov launch`, the dispatcher, the landing, plus a stop message to running sessions. Owner-in-person lift kept (DEC-409). | 2 | 0 | Low in text; **the code fails open today** (only the retired guard reads the flag): a fix for the CTO, test first | `3ba778680` |
| **G5-3** | Memory without `gov context` (§5.2 to §5.5; M1 (c)) | CAP-15 becomes "the brief carries the ticket's retrieval, uncut" (packet mechanics CAP-15.d, .g dropped; CAP-15.f to friction); CAP-01 answers from `gov retrieve`; CAP-10 is a fresh 80 judged end to end at 95 %, hit@k a diagnostic only; CAP-17.b, CAP-19.c, CAP-48.a, §2 Token budget (no packet ceiling anywhere). | 15 | 2 | Medium: CAP-15 moves to W2 because the brief carrying the retrieval is a release item (W2-197) | `91f280f9b` |
| **G5-4** | The landing and the flow (§3.3, §4; L2) | MR-1 (feature tickets, READY by code), MR-2 (`gov discover`), MR-3 (the landing refuses an acceptance-test commit without the designer's role, in Gov OS and in an adopted repository), CAP-31 (a red landing makes no repair ticket), CAP-53 (feature, fix or chore; the rubric replaces a profile computed from impact), CAP-59 and §2 Loop budget (**two rounds**, not three), CAP-23.c, CAP-38, CAP-39 (acceptance, `.c`, new `.e` for the scheduler left to friction). | 19 | 4 | Medium: MR-3 only holds in an adopted repository once `gov queue` exists (W2-115b); CAP-39 moves to W2 | `87d2551cf` |
| **G5-5** | Reviews, audits, who approves (§3.4 to §3.6; G6 (a)) | MR-4 and CAP-47.d: a fresh audit **only** at the release acceptance and at adoption stages A5, AS, A7 and A10, otherwise a review only for a red test, a failed landing or merge, or a feature not working. CAP-38.f (FULL probe after green) dropped. Kernel and instruction text is the CTO's call (CAP-24.c, CAP-33.d, CAP-21.a). | 8 | 3 | Low: your G6 (a) | `d13de58aa` |
| **G5-6** | The lean release (§6.1, §7.6, §8; L3 (a); Q-UPD) | Releases are pinned and hash-verified, **no signing** (CAP-02, CAP-02.c waits for friction). `gov update` is in the release, with the three-way merge that keeps your edits (CAP-45 to W2). CAP-43.c and CAP-39.b become the release acceptance and the proving run; CAP-30.c and CAP-32.d name `gov discover` (W2-36); CAP-44.f/.h add the 95 % verdict for EXAMIN's copy. CAP-49 drops the sandbox and guard hiding of the oracle (the transcript scan replaces it, CAP-66). | 20 | 4 | Medium: CAP-45 and CAP-49 into W2; no transcript scanner exists yet (CAP-66 is new in G5-10) | `acc796f9b` |
| **G5-7** | Secrets (§2.11) | Sensitivity classes keep secrets out of every index; one full gitleaks scan only before a repository goes public or is shared (CAP-03, CAP-41.g). | 4 | 0 | Low | `f84d5dc42` |
| **G5-8** | The run-time tool, the rubric, the measures (§6.3, §10.2; K1, T3) | §2 RAM budget (GPU never spills, slots from the machine detected), CAP-04 (the runaway brake; budgets per task to friction), CAP-22.b (inbox files), CAP-23.b (dispatch into slots), CAP-35 (the owner's rubric), CAP-37 (resume after compaction or crash; no packet), CAP-40 (weekly measures), CAP-27. | 21 | 1 | Medium: CAP-23 and CAP-35 move to W2 | `e5db4eb71` |
| **G5-9** | Installs (G7 (c)) | The CTO approves and records every install, no prompt, `sudo` stays yours: §2 Tool installs, CAP-25 (outcome, acceptance, lite form, `.b`). | 3 | 3 | Low: your G7 (c) | `d14bc375a` |
| **G5-10** | Seven new capabilities (audit 7 NEW-1 to NEW-7) | CAP-63 the landing, CAP-64 the run-time tool (RT-1 to RT-8, T1 stall check, T2 phone pushes), CAP-65 memory by construction, CAP-66 the hidden-set scan, CAP-67 hourly backups, CAP-68 the basis line, CAP-69 transcripts kept. 62 capabilities become 69. | 30 new | 0 | Medium: 36 new W2 items need a ticket's `closes:` line and an acceptance test citing them (the validator lists them) | `7c2f545d0` |
| **G5-11** | Wave 3 is friction (§8.4) | W2 means "what the lean release must have", W3 means "built only when an adopted repository needs it". CAP-04.a/.d, CAP-22.c, CAP-30.g and CAP-37.e move to W3 (DEC-841 had moved them; the text never changed); 34 friction items carry the §8.4 source. Charter roles table follows. | 34 | 1 | Low | `f4a3d37e6` |
| **G5-12** | The Charter's aim and precedence | §1 Purpose carries the aim (§1.1); §8 says EMERGENCY-2 holds until this lands and the register is read from the one that replaces the archived one. | 0 | 2 | Low | `b2b0d2786` |
| **G5-13** | The decision checker | CAP-51: the checker also runs on the register that replaces the archived one. | 1 | 0 | Low | `283c9901e` |

Totals, base to branch (counted from the yaml): 143 existing rows changed, 22 of them dropped to `NONE` or DROP (so their ids still resolve); 31 rows added (7 capabilities, 24 covers items); 27 rows change wave. 62 capabilities and 215 covers items become 69 and 239. 25 Charter paragraphs or table rows change (audit 7 lists 21 rows; four of them split across groups). 8 rows are new in `SOURCE_MAP.csv`; 293 of its rows now read "Contract v5" with each capability's class and wave taken from the yaml.

## After your yes

The CTO does these; none needs you again.

1. Set `status: ACCEPTED` in `contract.yaml`, `CONTRACT_v5.md` and `CHARTER_v6.md`, run `gen_contract.py --write`, and record your approval once in the register (DEC-861, DEC-1211 style).
2. Retire the tests that assert dropped or moved clauses (a test designer, with a Rewrite-Reason); the list is below. Not done tonight.
3. Give every W2 item that has no ticket one (`closes:` on W2-115b, W2-121c/d, W2-197, W2-17, W2-18, W2-36, W2-81 and the rest), so `validate_w2.py` goes green.
4. Kernel text that still names the old documents ("Charter v5 §6" in `template/governance/kernel/roles/orchestrator.md` and its generated copies, the adopt skill's "Contract v4.2") is the CTO's to change (EMERGENCY-2 §3.5); I did not touch it.
5. Update ADR-0001 and ADR-0002 in full (audit 7 C-4): tonight each got an amendment note only.

## Tests v5 turns red, and why

Run on branch `e2/g4-g5`, through the heavy slot, against `w2/integrate` at `0123c8b5f`. **Base:** W2-49, W1-48 and W2-51 together 127 passed; `validate_w2.py` 3 FAIL, 5 NOT RUN (all three FAILs were already on the base).

**On the branch:** W2-49, W1-48, W2-51, W2-129, W2-134, `tests/unit/links` and `tests/unit/retrieval/test_w2_61h_families.py` together: **382 passed, 11 failed, 1 error** (`validate_w2.py`: 4 FAIL, 5 NOT RUN). W1-48, W2-51, W2-129, W2-134 and the links tests are green. The register's class lines and the path-map edit break nothing: `tests/unit/store`, `decisions`, `links`, `close` and `optin` give **435 passed**. The red ones, each with its cause and the group that causes it:

| Test | Why it is red | Group | What retires or fixes it (after your yes, by a test designer with a Rewrite-Reason) |
|---|---|---|---|
| `W2-49/test_w2_49_contract.py::test_markdown_version_is_4_2_with_a_change_row_citing_dec_722` and `::test_markdown_has_a_4_3_change_row_...` (2) | They read `docs/contract/CONTRACT_v4.md`, which is now `CONTRACT_v5.md` | G5-0 | Point at the v5 file; or keep the old file name (the alternative in G5-0) and they stay green |
| `W2-49/test_w2_49_owner_answers.py::test_cap_45_moves_to_w3_...[markdown]` (1 error at setup) and `[yaml]` (1 failed) | Same missing file; and the yaml now has CAP-45 at W2: `gov update` is in the release (§6.1, §7.6) | G5-0, G5-6 | Retire: it asserts DEC-1093's move that EMERGENCY-2 reverses |
| `W2-49/test_w2_49_contract.py::test_qualification_certificate_cap_43c_stays_in_wave_3[yaml]` (1) | CAP-43.c is W2: certified by the release acceptance (§8.2) | G5-6 | Retire |
| `W2-49/test_w2_49_records_v4_2.py::test_cap_45_and_cap_45a_records_state_wave_w3_as_contract_yaml` (2, CAP-45 and CAP-45.a) | The records say W2, as the yaml now does | G5-6 | Retire |
| `W2-49/test_w2_49_validator_lines.py` (4): `test_validator_passes_both_cit_p_checks_on_this_tree`, `test_a_tree_of_the_validators_inputs_alone_...`, `..._fails_naming_it[CAP-43.b]` and `test_a_cit_p_line_for_an_item_the_contract_does_not_change_...` | `validate_w2`'s check "cit-p-moved-items" fails for 36 items now in W2 that no CIT-P line carries (CAP-15, 23, 35, 39, 43.c, 45.b, 49.a and the new CAP-63 to CAP-68); and the last test builds on CAP-61.f staying W2, which is now dropped | G5-1, G5-3, G5-4, G5-6, G5-8, G5-10 | Rewrite: the audit 7 table is the evidence for these moves (a CIT-P per move is the ceremony EMERGENCY-2 retires); give `check_cit_p_moved` the re-baseline as its source, and rebuild the last test on another item that stays W2 |
| `unit/retrieval/test_w2_61h_families.py::test_this_repository_declares_its_families` (1) | The path map's `contract` family names `docs/contract/CONTRACT_v5.md` (I changed it; the test lists the v4 name) | G5-0 | Update the test's list to v5 (or keep the file name) |

`validate_w2.py` on the branch, against the same three FAILs as on the base:

| Check | Base (`w2/integrate`) | Branch |
|---|---|---|
| wave2-tickets | FAIL (ids only in `.tickets/`) | FAIL, unchanged: not the Contract's |
| contract-items-delivered | FAIL: CAP-22.c | FAIL: 36 W2 items with no ticket `closes:` line (CAP-15 a, b, c, e; CAP-23 b, c; CAP-35 a to c; CAP-39 b, c; CAP-43.c; CAP-45.b; CAP-49.a; CAP-63 to CAP-68). CAP-22.c is now W3, so it left the list |
| contract-items-cited-by-tests | FAIL: 7 items | FAIL: 29 W2 items no acceptance test cites |
| cit-p-moved-items | PASS | FAIL: the 36 above |
| cit-p-lines-applied, ticket-contract-ids-exist (every id a ticket cites still exists), list-counts, triage-counts | PASS | PASS |

These three are not red for a defect in the text: they list what the release still has to build and test, which is what a re-baselined Contract is for.
