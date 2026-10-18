# W2-49 acceptance tests: Contract v4.2, lite (CAP-44.h with A7 and A10, CAP-43.b)

Ticket `DAEO-ha8z` (W2-49), profile STANDARD, class specification. Written by the Independent Test Designer (MR-3)
before the implementation, from the ticket's KPI lines, the W2-49 card (`docs/plan/WAVE_2_WBS.md` §2), §1's paragraph
"Contract v4.2 adds, lite (DEC-722)", exit criteria 6 and 7 (§5), list row W2-I017, and the sources DEC-722, CAP-33,
CAP-44.h, CAP-44.f, CAP-43.b, CAP-02.c (with DEC-105, DEC-090 and CAP-43.c read for context).

Run (DEC-732: this worktree's own `src/` first on the path, set per command):

```
PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m pytest tests/acceptance/W2-49 -q -p no:cacheprovider -rs
```

129 tests, deterministic, no network, nothing skipped: the 76 written before the CIT-P, and 53 added after the owner
approved it (DEC-741, 2026-10-17; §2a). No earlier test was rewritten.

## 1. What the suite reads (its public interface)

| File | Written by W2-49 | When |
|---|---|---|
| `docs/changes/W2-49-CIT-P.md` | the change-impact proposal | next, before review |
| `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md` | Contract v4.2 | only after the owner approves the CIT-P (CAP-33) |
| `docs/changes/W2-49-CIT-E.md` | the change-evidence record | after the Contract change |
| `docs/contract/capabilities/*.md` | the derived capability records (DEC-614), regenerated for v4.2 (DEC-741 K) | after the Contract change |

The reference for "moves exactly those parts" is the Contract at this branch's base, read with
`git show a02e3485:docs/contract/contract.yaml` (and `...:docs/contract/CONTRACT_v4.md` for the earlier change rows).

**DEC-732, the code under test.** These tests import no `gov` code: the documents are the interface. Every path is
found from the test file's own location (`Path(__file__).parents[3]`), so the suite reads this worktree's files, never
the main tree's and never an installed package's. The run command sets `PYTHONPATH` to this worktree's `src/` anyway,
so that `pytest`'s own conftest chain and any later helper resolve here; `python3 -c "import gov; print(gov.__file__)"`
with the same `PYTHONPATH` prints `/home/usain/gov-os-worktrees/W2-49/src/gov/__init__.py`.

## 2. KPI lines, tests and red reasons

### KPI success line 1: the CIT-P — `test_w2_49_cit_p.py` (24 tests)

The CIT-P names each change, its source (DEC-722) and its impact. A fact "is in the CIT-P with" another when both
appear in one table row, one list item, one paragraph, or one section from a heading to the next heading.

| Test | What it checks | Sources |
|---|---|---|
| `test_cit_p_exists_and_names_its_source_dec_722` | the file exists and cites DEC-722 | DEC-722 |
| `test_cit_p_names_cap_44h_lite_with_the_three_verdicts` | CAP-44.h with "lite"; CAP-44.h with ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS, NOT_ADOPTED_HEALTHY | CAP-44.h, DEC-722 |
| `test_cit_p_states_the_conditions_a_lite_verdict_checks` | CAP-44.h (or "verdict") with "condition" | CAP-44.h |
| `test_cit_p_names_each_lite_gate_of_cap_44f_with_what_it_checks[A7, A10]` | CAP-44.f named; each gate with "lite" and with what it checks ("check"/"verif") | CAP-44.f, DEC-722 |
| `test_cit_p_says_what_of_cap_44f_stays_for_wave_3[A9, A11]` | each with "W3"/"Wave 3" | CAP-44.f, DEC-090 |
| `test_cit_p_names_cap_43b_lite_manifest_and_file_hashes` | CAP-43.b with "lite", "manifest" and "hash" | CAP-43.b, DEC-722 |
| `test_cit_p_says_the_rest_of_cap_43b_stays_for_wave_3` | "rest of CAP-43.b" with Wave 3, or every other release content with Wave 3 | CAP-43.b |
| `test_cit_p_keeps_cap_02c_signed_tags_in_wave_3` | CAP-02.c with Wave 3 | CAP-02.c, DEC-722 item 2 |
| `test_cit_p_keeps_the_qualification_certificate_in_wave_3` | "qualification certificate", CAP-43.c or "certification by qualification", with Wave 3 | the W2-49 card |
| `test_cit_p_names_each_impacted_ticket[W2-02, W2-16, W2-18, W2-27…W2-30]` | each ticket, or the range "W2-27 to W2-30" | the W2-49 card |
| `test_cit_p_names_exit_criteria_6_and_7_in_its_impact[6, 7]` | "exit criterion 6", "exit criteria 6 and 7" and the like | WBS §5 |
| `test_cit_p_presents_dec_105_three_options_with_their_cost[apply-now, defer, re-baseline]` | DEC-105 cited; each option with "cost" | DEC-105, CAP-33.e |
| `test_cit_p_goes_the_cap_33_route_to_the_owner` | CAP-33 cited; the owner's approval; the independent review | CAP-33 |

**Red reason now:** `docs/changes/W2-49-CIT-P.md does not exist yet` (24 failures). These turn green when the CIT-P
is written; they do not depend on the Contract change.

### KPI success line 2: Contract v4.2 — `test_w2_49_contract.py` (42 tests)

Contract v4.2 moves exactly DEC-722's parts to Wave 2; CAP-02.c, A9, A11, the qualification certificate and the rest
of CAP-43.b stay in Wave 3. The placement tests run once on `contract.yaml` and once on `CONTRACT_v4.md`, so the two
files must agree on the moved and the kept parts.

| Test | What it checks | Sources |
|---|---|---|
| `test_yaml_version_is_4_2_with_a_change_log_entry_citing_dec_722` | `version: '4.2'`; one change-log entry 4.2 citing DEC-722 | DEC-722 |
| `test_yaml_change_log_keeps_every_earlier_version_unchanged` | the 4.0 and 4.1 entries as at the base | CAP-33.e, DEC-105 |
| `test_markdown_version_is_4_2_with_a_change_row_citing_dec_722` | frontmatter `version: "4.2"`; a `\| 4.2 \|` row citing DEC-722; earlier rows unchanged | DEC-722 |
| `test_cap_44h_verdict_moves_to_wave_2_lite[yaml, markdown]` | the verdict placed in W2, on a covers item that says "lite" and cites DEC-722 | CAP-44.h, DEC-722 |
| `test_cap_44f_gate_moves_to_wave_2_lite[A7, A10 × yaml, markdown]` | each gate placed in W2, lite, citing DEC-722 | CAP-44.f, DEC-722 |
| `test_cap_43b_manifest_and_file_hashes_move_to_wave_2_lite[yaml, markdown]` | manifest and hashes placed in W2, lite, citing DEC-722 | CAP-43.b, DEC-722 |
| `test_cap_44f_gate_stays_in_wave_3[A9, A11 × yaml, markdown]` | each still placed in W3 | CAP-44.f, DEC-090 |
| `test_rest_of_cap_43b_stays_in_wave_3[9 contents × yaml, markdown]` | semantic version, supported migrations, schema versions, CLI/runtime versions, adapter/capability versions, release notes, affected indexes, required human decisions, rollback procedure: each still placed in W3 | CAP-43.b |
| `test_cap_02c_signed_release_tag_stays_in_wave_3[yaml, markdown]` | CAP-02.c present, `[W3]`, still the signed tag | CAP-02.c, DEC-722 |
| `test_qualification_certificate_cap_43c_stays_in_wave_3[yaml, markdown]` | CAP-43.c present, `[W3]`, still the certification | the W2-49 card |
| `test_no_other_covers_item_changes_wave` | against the base: only CAP-44.f, CAP-44.h, CAP-43.b may change wave in place, and only to W2 | "exactly" |
| `test_no_covers_item_is_removed` | every base covers id is still there | "exactly" |
| `test_new_covers_items_are_only_splits_of_cap_43_and_cap_44` | a new covers id is in CAP-43 or CAP-44, in W2 or W3 | "exactly" |
| `test_no_capability_is_added_removed_or_changes_wave` | every capability's `wave` as at the base (CAP-44 stays W3: A11 stays) | "exactly" |
| `test_yaml_and_markdown_agree_on_every_covers_item_and_wave` | same covers ids, same waves, same capability waves in both files | the files' own rule ("same content") |

**Red reason now:** `the Contract's yaml/markdown file is version '4.1', not 4.2: Contract v4.2 is not written yet`
(40 failures), and for the two version tests `contract.yaml is (version '4.1',) not 4.2` (2 failures). Every test
here first checks the version, so none passes by accident on the unchanged 4.1 text. They stay red after the CIT-P is
written, until the owner approves it and the Contract change is made.

**The form of a split item (an assumption, not a source).** No source fixes how the Contract shows an item split
between waves (CAP-44.f: A7 and A10 move, A9 and A11 stay; CAP-43.b: manifest and file hashes move, the rest stays;
CAP-44.h: the lite verdict moves). The placement tests accept any of these, on the covers items themselves:

1. a split into separate covers items (new ids in CAP-43 or CAP-44), each with its own `wave`;
2. the original item moved whole to `wave: W2`, with a note on it naming what stays in W3;
3. the original item kept in `wave: W3`, with a note on it naming what moves to W2.

A part is "placed in a wave" when a covers item of the capability names it and either the item's `wave` is that wave,
or one clause of the item's text (any field but `id`, `wave`, `provider`; in the markdown, the line and its indented
continuation) names the part together with "W2"/"Wave 2" (or "W3"/"Wave 3"). Clauses are split at `;`, `. ` and line
ends; a ticket id such as `W2-02` is never read as a wave. Each test's own assumptions:

- *moves* tests: the covers item carrying the moved part says "lite" and cites DEC-722 somewhere in its fields;
- *verdict* test: the W2 placement is on CAP-44.h itself, or names all three verdicts;
- *stays* tests: each kept part is still named on a W3 placement; with form 2 the note must name each kept part (A9,
  A11, and each of the nine other release contents of CAP-43.b), not only "the rest";
- *exactly* tests: the change is recorded on the covers items, not only in a capability's prose `wave_note`; no
  covers id is removed (a split keeps the original id); no capability changes `wave`;
- the qualification certificate is CAP-43.c ("Release certification by qualification"), the only certification item in
  the Contract.

These forms were checked before the commit against throwaway stand-ins built outside the tree: forms 1, 2 and 3 each
pass all 76 tests. A9 moved with A7 and A10 fails the A9 test. CAP-43.c moved fails the certificate and exactly tests.
Gates that don't say "lite" fail the gate tests. A markdown file that doesn't follow the YAML fails the markdown
placement tests and the agreement test.

### KPI success line 4: the CIT-E — `test_w2_49_cit_e.py` (10 tests)

The CIT-E matches the CIT-P, or lists the differences (CAP-33's acceptance).

| Test | What it checks | Sources |
|---|---|---|
| `test_cit_e_names_its_proposal_and_source` | names `W2-49-CIT-P`; cites DEC-722 | DEC-722 |
| `test_cit_e_records_each_change_the_cit_p_names[CAP-44.h, A7, A10, CAP-43.b, v4.2]` | each change named (confirmed or listed as a difference) | CAP-44.h, CAP-44.f, CAP-43.b |
| `test_cit_e_states_its_differences_from_the_cit_p` | a statement of differences from the CIT-P/proposal (or that there are none) | CAP-33 |
| `test_cit_e_records_every_covers_item_the_contract_changed` | every covers item whose fields changed, or that v4.2 added, against the base, is named | CAP-33 |
| `test_cit_e_records_every_moved_item_the_cit_p_names` | each of CAP-44.f, CAP-44.h, CAP-43.b named in the CIT-P is named in the CIT-E | CAP-33 |
| `test_cit_e_records_the_owner_approval_before_the_change` | cites CAP-33; records the owner's approval | CAP-33 |

**Red reason now:** `docs/changes/W2-49-CIT-E.md does not exist yet` (10 failures). They stay red until the Contract
change is made and recorded; `test_cit_e_records_every_covers_item_the_contract_changed` also needs Contract v4.2.

### KPI success line 3 and the failure line: pending W2-51 (no test)

- Line 3, "The plan validator's two-way check covers the moved parts."
- The failure line: "A Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator."

Both need a plan validator that reads Wave 2. `docs/plan/tools/validate_s1.py` is Wave 1's and is in no Wave 2
ticket's paths. Its Wave 2 form, first held as package P-W2-11, is now ticket **W2-51 (DAEO-egsy)** (DEC-744). No test
is written for these two lines here; they are added when W2-51's validator exists.

## 2a. The owner's answers to the CIT-P (DEC-741) — added after the approval

DEC-741 (the owner's, 2026-10-17) approves the CIT-P, apply now, and answers Questions A to K as the CIT-P recommended
(C either way, K (2) staged for the owner to confirm). These tests add what the answers fix and the 76 earlier tests
could not know. Every Contract test runs on both files and first checks the version, as the earlier ones do.

### `test_w2_49_owner_answers.py` (45 tests)

| Test | What it checks | Answer |
|---|---|---|
| `test_new_split_id_exists_in_wave_3_naming_its_part[CAP-43.d, CAP-44.k, CAP-44.l × yaml, markdown]` | the id exists under CAP-43/CAP-44, `W3`, and names its part: CAP-43.d the nine other release contents; CAP-44.k A9, A11, A7 and A10 (beyond lite); CAP-44.l the verdict and "the ten … conditions" | A (a1) |
| `test_split_item_keeps_its_id_at_wave_2[CAP-44.f, CAP-44.h, CAP-43.b × yaml, markdown]` | the original id is still there, now `W2` | A (a1) |
| `test_no_new_covers_id_but_cap_43d_44k_44l[yaml, markdown]` | against the base, the new covers ids are exactly these three (failure: any other) | A (a1) |
| `test_no_other_covers_item_of_cap_43_or_cap_44_changes_wave[yaml, markdown]` | every other base covers item of CAP-43 and CAP-44 keeps its wave (failure line of A) | A (a1) |
| `test_covers_count_by_wave_is_w1_149_w2_20_w3_38_none_7[yaml, markdown]` | covers by wave W1 149 / W2 20 / W3 38 / NONE 7, 214 in all (CIT-P §6.3) | A (a1) |
| `test_lite_cap_43b_names_none_of_the_nine_other_release_contents[yaml, markdown]` | CAP-43.b names the manifest and hashes and none of the nine other contents as its own; a clause naming CAP-43.d or Wave 3 is read as an exclusion note | B (i) |
| `test_cap_43_wave_note_names_cap_43d_and_no_ticket[yaml, markdown]` | CAP-43's wave note (the `Wave:` line in the markdown) names CAP-43.d and no ticket id (option B (i)'s own text, CIT-P §7 B) | B (i) |
| `test_cap_45a_stays_w2_with_the_release_manifest_and_hashes_as_its_wave_2_source[yaml, markdown]` | CAP-45.a is `W2`; one clause names Wave 2 with the manifest and hashes; it cites CAP-43.b; one clause names the signed tag with CAP-02.c and Wave 3; it cites DEC-722 | D (ii) |
| `test_cap_45a_names_no_signed_tag_as_a_wave_2_requirement[yaml, markdown]` | failure: every clause of CAP-45.a that names a signed tag carries W3/Wave 3 | D (ii) |
| `test_cap_44h_states_the_three_verdict_rules[yaml, markdown]` | one clause each: ADOPTED_HEALTHY with "every/all … met"; ADOPTED_WITH_ACCEPTED_EXCEPTIONS with accepted, owner, by name, decision; NOT_ADOPTED_HEALTHY with "otherwise" (or "not met/not accepted/any") | F (i) |
| `test_cap_44h_says_the_auditor_accepts_no_exception[yaml, markdown]` | a clause says the auditor accepts no/none/nothing (or does not/never/cannot accept) | F (i) |
| `test_cap_44h_lets_no_one_but_the_owner_accept_an_exception[yaml, markdown]` | failure: every clause about accepting (not the verdict's name, not "acceptance") either is the auditor's refusal, or names the owner and no other actor (auditor, orchestrator, lead, engineer, agent, reviewer, worker, designer) | F (i) |
| `test_cap_44h_names_the_operational_lite_condition[3 conditions × yaml, markdown]` | `gov doctor` green or exit 0 (not only MATCH); `gov check` with no RED; `gov close` at exit 0 with "ticket" and "test" in the clause | G (i) |
| `test_cap_44h_names_its_lite_conditions_and_marks_each_of_the_ten_if_it_lists_them[yaml, markdown]` | CAP-44.h says "lite" and "condition"; **if** it lists ten entries numbered 1 to 10, each entry carries W2/Wave 2 or W3/Wave 3 | C, both outcomes |
| `test_cit_e_names_w2_52_as_the_builder_of_the_lite_a7_and_a10_stage_records` | one scope of the CIT-E names W2-52 with A7 and A10 | H (i) |
| `test_cit_p_records_the_owner_answer_naming_w2_52` | the CIT-P cites DEC-741; one scope names W2-52 with A7 and A10; one names W2-52 with DEC-741 or the owner | H (i) |
| `test_every_capability_record_cites_contract_version_4_2` | every `docs/contract/capabilities/*.md` (none of the base's removed) says "Contract v4, version 4.2" | K (1) |
| `test_no_capability_record_cites_contract_version_4_1` | failure: no record says "version 4.1" | K (1) |
| `test_both_contract_files_state_status_accepted_for_v4_2` | `contract.yaml`'s `status` and `CONTRACT_v4.md`'s frontmatter `status` are the same, ACCEPTED, and both files are 4.2 | row W2-L343 |

**Red reasons now (seen):**
- the 40 Contract tests: `the Contract's yaml/markdown file is version '4.1', not 4.2`;
- `test_cit_e_names_w2_52_…`: `docs/changes/W2-49-CIT-E.md does not exist yet`;
- `test_cit_p_records_the_owner_answer_naming_w2_52`: `the CIT-P does not record the owner's answers (DEC-741)`;
- the two K (1) tests: `273 of 273 capability records do not cite Contract v4, version 4.2` and `273 of 273 capability
  records still cite version 4.1`;
- `test_both_contract_files_state_status_accepted_for_v4_2`: `the two Contract files state different statuses:
  {'yaml': 'PROPOSED', 'markdown': 'ACCEPTED'}`.

### `test_w2_49_capability_records.py` (8 tests): K (2), in a file of its own

DEC-741 K (2) is a reading staged for the owner to confirm or overturn. If the owner overturns it, this file is dropped
alone; nothing else imports it, and the K (1) tests above hold whether or not the three new records exist.

| Test | What it checks |
|---|---|
| `test_record_of_split_item_follows_contract_v4_2[CAP-44.f, CAP-44.h, CAP-43.b, CAP-43.d, CAP-44.k, CAP-44.l]` | the record exists; frontmatter `id`, `title` = v4.2's `item`, `depends_on` = [parent]; same frontmatter keys and same `type`, `status`, `state_class` as the unchanged sibling (CAP-43.a, CAP-44.a); `Item:` and `Wave:` lines as in v4.2; the body has the sibling's form once id, item, wave and parent are replaced |
| `test_capability_record_covers_list_equals_contract_v4_2[CAP-43, CAP-44]` | the "Covers:" list holds exactly the capability's covers ids in v4.2, none twice (order not checked) |

**Red reason now (seen):** `the Contract's yaml file is version '4.1', not 4.2` (8 failures). The version is checked
first because today's records of CAP-43.b, CAP-44.f and CAP-44.h do match the 4.1 `contract.yaml`, and would pass by
accident otherwise.

### Assumptions of the added tests (not sources)

- **A list of the ten conditions (C (i))** is recognised when its entries are numbered 1 to 10, as `(1)`, `1.`, `1)` or
  `C1`. An unnumbered list is not recognised, and the marking check then holds vacuously; the lite-condition tests
  (G) hold under both outcomes.
- The earlier tests still accept the three forms of a split item (§2, "The form of a split item"); DEC-741 A fixes
  form 1 (a1), and only the added tests pin it. Nothing earlier is made wrong by DEC-741, so nothing was rewritten.
- The record form is read from the 273 records as they are: a check run before the commit found every one of the 211
  covers records and 62 capability records consistent with it.

### How the added tests were checked (before the commit)

Against throwaway stand-in trees built outside the repository (single named files: the test files, the CIT-P; the two
Contract files and all 273 records generated from the approved CIT-P §6 text; a generator that reproduces today's 273
records exactly at 4.1):
- the approved text under C (ii) (fallback) and under C (i) (the ten listed, numbered, each marked): **all 129 pass**;
- the approved text without the K (2) records (the version line alone regenerated): only the 8 K (2) tests fail;
- an exclusion note in CAP-43.b ("the semantic version … are CAP-43.d (W3)"): passes;
- each break fails its test: an extra id CAP-44.m; CAP-44.g moved to W2; CAP-44.k in W2; CAP-43.d without the
  rollback procedure; CAP-43.b with the semantic version; CAP-43's note naming W2-16; CAP-45.a unchanged; CAP-45.a
  with a signed tag and no W3; "the auditor may accept an exception"; "accepted by the owner or the orchestrator"; no
  NOT_ADOPTED_HEALTHY rule; G (ii) (MATCH only); "gov check green" with no doctor-green; one of the ten unmarked; status
  PROPOSED in the yaml; one record citing 4.1; a stale CAP-44.h record, a missing CAP-44.k record and CAP-44.l missing
  from CAP-44's Covers; the CIT-P and CIT-E without W2-52.

## 3. Source ids cited

| Source | Tests |
|---|---|
| DEC-722 | `test_cit_p_exists_and_names_its_source_dec_722`, the `*_moves_to_wave_2_lite` tests, both version tests, `test_cit_e_names_its_proposal_and_source` |
| CAP-33 | `test_cit_p_goes_the_cap_33_route_to_the_owner`, `test_cit_e_records_the_owner_approval_before_the_change`, `test_cit_e_records_every_covers_item_the_contract_changed` |
| CAP-44.h | `test_cit_p_names_cap_44h_lite_with_the_three_verdicts`, `test_cit_p_states_the_conditions_a_lite_verdict_checks`, `test_cap_44h_verdict_moves_to_wave_2_lite` |
| CAP-44.f | `test_cit_p_names_each_lite_gate_of_cap_44f_with_what_it_checks`, `test_cit_p_says_what_of_cap_44f_stays_for_wave_3`, `test_cap_44f_gate_moves_to_wave_2_lite`, `test_cap_44f_gate_stays_in_wave_3` |
| CAP-43.b | `test_cit_p_names_cap_43b_lite_manifest_and_file_hashes`, `test_cit_p_says_the_rest_of_cap_43b_stays_for_wave_3`, `test_cap_43b_manifest_and_file_hashes_move_to_wave_2_lite`, `test_rest_of_cap_43b_stays_in_wave_3` |
| CAP-02.c | `test_cit_p_keeps_cap_02c_signed_tags_in_wave_3`, `test_cap_02c_signed_release_tag_stays_in_wave_3` |
| DEC-105 | `test_cit_p_presents_dec_105_three_options_with_their_cost`, `test_yaml_change_log_keeps_every_earlier_version_unchanged` |
| DEC-741 | every test of `test_w2_49_owner_answers.py` and `test_w2_49_capability_records.py` (§2a, answer by answer) |
| CAP-45.a | `test_cap_45a_stays_w2_with_the_release_manifest_and_hashes_as_its_wave_2_source`, `test_cap_45a_names_no_signed_tag_as_a_wave_2_requirement` |
| DEC-614 | the K (1) and K (2) tests (the records are derived from `contract.yaml`) |

## 4. Files

- `w2_49_support.py`: readers for the four documents and the base, the two Contract models (YAML, markdown), the
  placement rule and the scope rule; added for DEC-741 (nothing earlier changed): frontmatter, the Contract's status,
  a capability's wave note, the capability records, the three new split ids. No test logic of its own.
- `test_w2_49_cit_p.py`, `test_w2_49_contract.py`, `test_w2_49_cit_e.py`: the tests of §2.
- `test_w2_49_owner_answers.py`, `test_w2_49_capability_records.py`: the tests of §2a (the second is K (2) alone).

No earlier ticket's test is changed by these KPIs.
