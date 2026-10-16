# W2-49 acceptance tests: Contract v4.2, lite (CAP-44.h with A7 and A10, CAP-43.b)

Ticket `DAEO-ha8z` (W2-49), profile STANDARD, class specification. Written by the Independent Test Designer (MR-3)
before the implementation, from the ticket's KPI lines, the W2-49 card (`docs/plan/WAVE_2_WBS.md` §2), §1's paragraph
"Contract v4.2 adds, lite (DEC-722)", exit criteria 6 and 7 (§5), list row W2-I017, and the sources DEC-722, CAP-33,
CAP-44.h, CAP-44.f, CAP-43.b, CAP-02.c (with DEC-105, DEC-090 and CAP-43.c read for context).

Run (DEC-732: this worktree's own `src/` first on the path, set per command):

```
PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m pytest tests/acceptance/W2-49 -q -p no:cacheprovider -rs
```

76 tests, deterministic, no network, nothing skipped.

## 1. What the suite reads (its public interface)

| File | Written by W2-49 | When |
|---|---|---|
| `docs/changes/W2-49-CIT-P.md` | the change-impact proposal | next, before review |
| `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md` | Contract v4.2 | only after the owner approves the CIT-P (CAP-33) |
| `docs/changes/W2-49-CIT-E.md` | the change-evidence record | after the Contract change |

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

### KPI success line 3 and the failure line: pending P-W2-11 (no test)

- Line 3, "The plan validator's two-way check covers the moved parts."
- The failure line: "A Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator."

Both need a plan validator that reads Wave 2. `docs/plan/tools/validate_s1.py` is Wave 1's, is in no Wave 2 ticket's
paths, and its Wave 2 form is with the owner (P-W2-11). No test is written for these two lines here; they are
added when P-W2-11 is answered.

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

## 4. Files

- `w2_49_support.py`: readers for the four documents and the base, the two Contract models (YAML, markdown), the
  placement rule and the scope rule. No test logic of its own.
- `test_w2_49_cit_p.py`, `test_w2_49_contract.py`, `test_w2_49_cit_e.py`: the tests above.

No earlier ticket's test is changed by these KPIs.
