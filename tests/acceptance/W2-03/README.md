# W2-03 acceptance tests (DAEO-ym8a): decisions as records, each with its own hash

A fresh independent test designer (MR-3, DEC-136) wrote these tests before the implementation. They come from the ticket's KPI lines and its sources: DEC-729, DEC-752, the list rows W2-L221, W2-M267, W2-M145, W2-M106 and W2-L069 and their origin in `governance/project/bootstrap.md`, and the decisions DEC-012, DEC-274, DEC-276, DEC-277, DEC-463, DEC-473, DEC-479, DEC-485, DEC-521, DEC-579, DEC-718 (AR-1), DEC-746 (item 5) and DEC-732. The profile is STANDARD (DEC-221): each KPI line's success and failure, plus the key edge cases.

## How the suite runs, and the code it runs (DEC-732)

From this worktree's root:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -m pytest tests/acceptance/W2-03 -q -p no:cacheprovider -rs

- **This worktree's code.** The `PYTHONPATH` in the command makes the suite import this worktree's `gov`. Every process a case starts gets the environment from `w2_03_support.env`. That environment sets `PYTHONPATH` to this worktree's `src/` (`SRC`), found from the support file's own place. `test_w2_03_code_under_test.py` checks that `gov.__file__` in a started process lies under `SRC`.
- **Public interfaces only.** No case reads `src/`.
  - **The store, as `gov rebuild` builds it:** `gov.store.load(root)`, then the record query `gov.records.records(root)`. Both run in one new process through a small driver.
  - **The decision checker:** `gov.decisions.check(root)`, after a load. It returns a list of findings, each with `code`, `ids`, `paths` and `message` (W1-11's interface).
  - **The decision-citations check, as `gov check` runs it:** the command declared in `template/governance/kernel/checks/core-decision-citations.yaml`, run by `sh -c` in a project's root. The cases read its JSON object (`DECISION_UNRECORDED` findings with `commit` and `decision`) and its exit code (W1-26's interface).
- **Nothing is written in this worktree.** Each project is a temporary git repository built from scratch under pytest's `tmp_path`. Its path map is valid under the kernel's schema and names `records/decision-log.md` as the register (`decision_register`, DEC-479). One case reads this checkout's `docs/DECISION_REGISTER.md`, read-only, and commits its text into a temporary project.
- **Deterministic, no network.** Fixed authors, dates and trailers. About 2 s in all.

## KPI lines → tests, and why each is red today

The red reasons below are what this suite printed at the commit that added it: **31 failed, 8 passed, 0 skipped.**

### Success 1: each `### DEC-nnn` entry is a record of its own, with its own sha256 over its own span; two decisions never share a hash [AR-1, F-M5]

| Test | Holds | Today |
|---|---|---|
| `test_w2_03_entry_records.py::test_each_entry_is_one_record_of_its_own` | Five entries are five records placed in the register. Nothing of the register is invalid. | green: the store already loads entries (W1-10's follow-up, DEC-521). It is here so that the cases below are about the hash and the span. |
| `…::test_each_entry_carries_the_sha256_of_its_own_span` (5) | `content_hash` is a sha256 in hex, and it equals the sha256 of the record's `span` | red: the record carries no `content_hash` and no `span` (keys: heading, id, path, status, title, type) |
| `…::test_the_span_is_the_entrys_own_text_in_the_register` (5) | The span starts at the entry's heading, holds the entry's own lines, is text of the register as written, and holds no other entry's heading | red: as above |
| `…::test_two_decisions_never_share_a_hash` | Five different hashes. DEC-103 and DEC-104 differ only in their ids. | red: as above |
| `…::test_every_entry_of_this_repositorys_register_has_its_own_hash` | All 745 entries of this checkout's register carry the sha256 of their own span, and no two share a hash (DEC-746 item 5) | red: 745 entries without it |

### Success 2: a decision id resolves to its entry, not to the register [AR-1]

| Test | Holds | Today |
|---|---|---|
| `test_w2_03_entry_records.py::test_a_decision_id_resolves_to_its_entry_not_to_the_register` | DEC-102's hash is not the register file's, and its span is less than half the register | red: no `content_hash` / `span` |
| `…::test_the_decision_citations_check_resolves_a_cited_id_to_its_entry` | A commit that cites DEC-101 (an entry) and DEC-900 (recorded nowhere) is flagged for DEC-900 alone | green: the control, already true (W1-26) |
| `test_w2_03_not_records.py::test_the_check_and_the_store_count_the_same_entries` | "In the same way": the check takes as recorded exactly the ids the store loads from the register, DEC-101 and DEC-105 | red: the check takes all five; the store takes three (the commented heading included) |

### Success 3: a register heading alone, or any Markdown file with a decision id in its frontmatter, is not a decision record [W2-L221, W2-M267, W2-M145]

| Test (`test_w2_03_not_records.py`) | Holds | Today |
|---|---|---|
| `test_a_heading_alone_is_no_record_of_the_store` (DEC-102: nothing under it; DEC-103: a body, no status line) | No record. `invalid` names the id in the register. | green: the store already refuses them (W1-10) |
| `test_a_heading_inside_an_html_comment_is_no_record_of_the_store` | A heading and its status line inside `<!-- -->` make no record (reading R4) | red: DEC-104 is a record |
| `test_a_file_with_a_decision_id_in_its_frontmatter_is_not_loaded_as_that_decision` (no type; `type: note`) | The store holds no decision record of DEC-110 | green: the store already needs a type (DEC-274) |
| `test_the_check_counts_a_heading_alone_and_a_commented_heading_as_unrecorded` | A commit citing DEC-101 to DEC-105 is flagged for DEC-102, DEC-103 and DEC-104 | red: no finding |
| `test_a_file_with_a_decision_id_in_its_frontmatter_does_not_satisfy_a_citation` (id only; `type: note`; `type: decision` without `state_class`) | A commit citing DEC-120 is flagged. The schema-valid DEC-121 beside it is not flagged (the control). | red: no finding |

### Success 4: status and id comparisons follow the schema's grammar, case included [W2-M106, W2-L069]

| Test (`test_w2_03_grammar.py`) | Holds | Today |
|---|---|---|
| `test_a_register_heading_outside_the_id_grammar_is_no_record` | `dec-131`, `Dec-132` and `DEC-13` make no record, nor do their upper-cased or padded forms. DEC-130 does (the control). | red: `DEC-13` is a record (`decision_id` asks for three digits or more) |
| `test_an_id_in_lower_case_does_not_record_the_upper_case_id` | A heading `### dec-131` and a decision file with `id: dec-133` record neither DEC-131 nor DEC-133 for the citations check | green: already exact |
| `test_a_decision_with_a_non_canonical_status_is_reported` (`active`, `Active`) | An owner-set decision file with that status gets a finding that names its path. The owner-set `ACTIVE` control gets none. | red: passes silently |
| `test_a_decision_with_an_empty_id_is_reported_never_followed_as_none_or_empty` (`id:`, `id: ""`) | An owner-set `ACTIVE` decision with an empty id gets a finding that names its path. No finding, and no store record, carries the id `None` or `""`. | red: passes silently |
| `test_a_register_entry_with_a_non_canonical_status_is_reported_not_passed_as_canonical` | `**Status:** accepted` is never held as ACCEPTED, and the store's `invalid` or a finding of the checker names DEC-140 (reading R7) | red: neither names it |

### Failure: an edited entry changes only its own hash; a duplicate DEC id is refused with both locations

| Test (`test_w2_03_failure.py`) | Holds | Today |
|---|---|---|
| `test_an_edited_entry_changes_only_its_own_hash` (the body or the status of a middle entry, the title of the first, the body of the last) | Reloading an unchanged commit gives the same hashes. After the edit is committed, the edited entry's hash changes. Every other entry keeps its hash and its span. | red: no `content_hash` |
| `test_a_duplicate_id_in_the_register_is_refused_with_both_locations` | DEC-202 sits under two headings. The other entries load, DEC-202 is no record, and `invalid` names the register with the line of each heading (9 and 23). | red: the reason ("stands under 2 headings of the register") names no line |
| `test_an_id_recorded_as_a_file_and_as_an_entry_names_both_locations` | DEC-203 is both a decision file and an entry. `invalid` names the file's path and the line of the entry's heading (15). | red: the reason names the file and not the line |

### DEC-732

`test_w2_03_code_under_test.py::test_the_processes_the_suite_starts_run_this_worktrees_code`: green.

## Readings taken

- **R1. The hash and the span.** The store's record of an entry carries `span` and `content_hash`.
  - `span` is the entry's own text in the register, starting at its heading (register-entry.schema.json: "the entry's own text in the register, from its heading to the next; its form is the store's (W2-03)").
  - `content_hash` is the sha256, in lower-case hex, of the span's UTF-8 bytes. The name comes from DEC-012's computed `content_hash`, from W2-L031, and from common.schema.json ("content_hash [is] derived by gov").
  - Where a span ends before the next heading (blank lines, a part heading, a version table) is the store's choice. The cases hold only these things: the span starts at the heading, holds the entry's lines, is text of the register, and stops before the next entry's heading.
- **R2. "Refused with both locations."** "Refused" is the store's refusal of a record, as DEC-274 and W1-10 fix it: the load goes on, no record is made of the id, and `invalid` names it. A raised error would contradict W1-10's case.
  - A register entry's location is the register's path and the line number of its heading. In one file, the line is what tells the two apart.
  - A decision file's location is its path.
  - For an id recorded both by a file and by an entry, which one stands stays W1-10's (the file). The case holds only the two locations.
  - Two decision files with one id stay W1-11's `DUPLICATE_ID`: the line is read as being about register entries.
- **R3. "A heading alone"** is a heading with no status line under it. The status line is the one W1-10's store reads: `- **Status:** WORD` as the entry's first line that is not blank.
- **R4. A heading inside an HTML comment is no live entry** (W2-M145, "live register entries"). Bootstrap's residual names it: "a heading inside an HTML comment too". This checkout's register has no HTML comment, so the real-register cases do not move.
- **R5. "Schema-valid decision record"** (W2-M267) means valid under the kernel's schema for the `decision` type, `madr.schema.json`: an `id` in the `decision_id` grammar, `type: decision`, a `status` and a `state_class`. This is held for the citations check only. The store's own record rule (DEC-274) is not changed by these cases.
- **R6. A canonical status** is the status word in capitals, as the sources write it (`ACTIVE`, `ACCEPTED`). A word in lower or mixed case is not canonical.
- **R7. Reporting a register entry's non-canonical status.** "Reported as a finding" is met by the store's `invalid` or by a decision-checker finding that names the id. No source says which of the two, and the case accepts either. It never accepts the entry being held as the canonical word.
- **The grammar** is `decision_id` in `common.schema.json` (`^(ADR|DEC)-[0-9]{3,}$`). DEC-473's heading grammar (`DEC-<digits>`) is read through it, so `### DEC-13` is no entry.
- **No case depends on the record's `type`** or on the "declared folders" (packages P-3 and P-4). Entries are found by their path in the register. A note "loaded as that decision" is a record of type `decision` or `register-entry`. Every decision file in these cases lies in `docs/adr/`.

## Earlier tests this ticket's KPIs contradict (packages, not edited here)

- **P-1:** `tests/acceptance/W1-26/test_w1_26_decision_register_and_base.py::test_a_heading_after_a_closed_fence_records_its_id`. Its entry `### DEC-101 — The parser changes` has no status line under it, and the case expects the entry to record DEC-101. Under W2-L221 that entry is a heading alone, so the case turns red once W2-03 is built.
- **P-2:** `tests/acceptance/W1-26/test_w1_26_decision_citations.py::test_a_decision_file_records_its_id[no-type-id-in-grammar]`. A file whose frontmatter has only `id: DEC-101` (no type, no state_class) is expected to satisfy a citation. That contradicts W2-M267 and W2-M145.
