# W2-51 acceptance tests: the Wave 2 plan validator

Ticket `DAEO-egsy` (W2-51), profile STANDARD, class implementation. These tests were written by the Independent Test
Designer (MR-3) before the implementation. They come from the ticket's six KPI lines and its sources: DEC-744 (staged,
given in the brief as written), DEC-723 and DEC-741. They also draw on DEC-730, DEC-722, DEC-105, DEC-221 and DEC-732,
`docs/plan/WAVE_2_WBS.md` §0, §1, §5 and the W2-49 card, and the real forms of `.tickets/`,
`docs/plan/WAVE_2_LIST.md`, `docs/plan/WAVE_2_TRIAGE.md` and `docs/contract/contract.yaml` (version 4.1). For the 4.2
form they use W2-49's CIT-P, CIT-E and `contract.yaml` on branch `w2/W2-49`, read with `git show` and never checked out.
`docs/plan/tools/validate_s1.py` was read as a reference only and was never run.

**47 tests**, deterministic, no network. Each test builds its own plan tree from scratch in pytest's `tmp_path`, and
no test reads this repository's live plan. The Contract ids in the trees are fictitious (CAP-91 to CAP-99). As a
result, no file in this folder reads as an acceptance test citing a real Contract item. That matters because, under
reading R4 below, the validator counts every file under `tests/acceptance/` as a possible citation.

## Run (DEC-732: this worktree's own code)

```
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -m pytest tests/acceptance/W2-51 -q -p no:cacheprovider -rs
```

The validator is run as a subprocess, `sys.executable docs/plan/tools/validate_w2.py --root <tree>`. The script path
comes from the test file's own location (`Path(__file__).parents[3]`), so it is always this worktree's script. The
subprocess gets `PYTHONPATH=<this worktree>/src`, which is set per command and never in a session's settings.
`HOME` is a temporary folder and the working directory is a temporary folder. `GOV_OS_WORKBENCH` is removed unless a
test sets it. Shown at design time:

```
$ PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -c "import gov; print(gov.__file__)"
/home/usain/gov-os-worktrees/W2-51/src/gov/__init__.py
```

## 1. The public interface these tests fix

- **Invocation:** `python3 docs/plan/tools/validate_w2.py --root <tree root>`. The tests always pass `--root` and never
  depend on the working directory. With no `--root`, the default is the implementer's choice; no test uses it.
- **Output:** on stdout, one line per check, in the form `<STATUS> <name> — <reason>`:
  - `STATUS` is `PASS`, `FAIL` or `NOT RUN`;
  - `name` is one token (`[A-Za-z0-9._-]+`);
  - the separator is a space, an em dash (U+2014) and a space;
  - the reason is never empty, and a pass also gives one.

  Lines that start with none of the three statuses (for example a closing summary) are free.
- **Exit status:**
  - `0` when no check prints `FAIL`. `NOT RUN` lines do not fail the run; otherwise the default run, whose
    workbench checks are always NOT RUN, could never pass.
  - `1` when any check prints `FAIL`, an unreadable input included.
  - A root that does not exist gives a non-zero exit and no `PASS` line.
- **The eight named checks.** Each prints exactly one line:

| Name | What it checks | KPI line |
|---|---|---|
| `wave2-tickets` | The W2 ids of the WBS §1 ticket table and of the Wave 2 tickets in `.tickets/` are the same set; the reason names each id on one side only | 1 |
| `contract-items-delivered` | Every covers item with `wave: W2` (the Contract's Wave 2 items and, on a 4.2 tree, its lite items) is delivered by a Wave 2 ticket; the reason names each item that is not | 2 |
| `contract-items-cited-by-tests` | Every such item is cited by an acceptance test; the reason names each item that is not | 2 |
| `ticket-contract-ids-exist` | Every Contract id a Wave 2 ticket cites exists in the tree's Contract; the reason names each unknown id | 2 |
| `cit-p-moved-items` | Every item moved to Wave 2 has a CIT-P line; the reason names each that has none | 3 |
| `cit-p-lines-applied` | Every CIT-P line has its change in the Contract; the reason names each line's id that has none | 3 |
| `list-counts` | Each severity count the list states agrees with its rows; the reason names the severity | 4 |
| `triage-counts` | Each cell of the triage's Counts table agrees with its rows; the reason names the row (`high` … `info`, `all`) | 4 |

Checks that would need `~/gov-os-workbench` or `docs/source/` print `NOT RUN`, with names the implementer chooses
(none of the eight). Their reason names what they would need (`gov-os-workbench` or `docs/source`). Wave 1's
validator had five such checks: four against the workbench and the readiness dimensions against the Framework's
original under `docs/source/`. The tests require at least one `NOT RUN` line (DEC-744 item 2: "a check that would need
them is reported as not run, by name").

## 2. Readings of the open input forms (each fixed as the smallest form found in the real files)

| # | Open form | Reading fixed here | Source |
|---|---|---|---|
| R1 | A Wave 2 ticket | A `.tickets/*.md` file whose frontmatter `wbs_id`, or `external-ref` when it has no `wbs_id`, matches `^W2-[0-9]{2}[a-z]?$`. `W2-15ab`, `W2-15A` and `W2-1` are not W2 ids: such a ticket is not a Wave 2 ticket, so its citations are not checked and its `closes` deliver nothing | DEC-730; DEC-744; the real `DAEO-rd0g.md` (W2-15a, `external-ref` only) |
| R2 | The WBS ticket table | The rows of `docs/plan/WAVE_2_WBS.md` whose first cell is a W2 id, bold or not (`\| **W2-03a** \|`) | WBS §1 |
| R3 | A ticket "delivers" an item | One entry of the ticket's frontmatter `closes:` list names the item's id as a whole token. That includes an entry cut by YAML at a comma, like the real W2-16 ticket's `- <id> (lite` / `- DEC-722)`. The fixtures keep each WBS row's Closes column in step, so a validator that reads that column instead sees the same | the real `closes:` lists (`DAEO-wbdh.md`, `DAEO-49o5.md`) |
| R4 | An acceptance test "cites" an item | Any file under `tests/acceptance/` (test or README) holds the id as a whole token (not followed by a letter or digit). A file outside `tests/acceptance/` does not count. The fixtures put each citation in the delivering ticket's own folder, so a stricter "the delivering ticket's own tests" reading sees the same | `tests/acceptance/W1-31/*.py` comments (`# Success line 1 [CAP-nn.x]: …`), W2-49's README tables |
| R5 | The Contract ids a ticket "cites" | Every `CAP-nn` or `CAP-nn.x` token anywhere in the ticket file (KPIs, `sources`, `closes`, body). "Exists" means it is a capability or covers id of the tree's `docs/contract/contract.yaml`, whatever its version | the real ticket frontmatter; `validate_s1.py`'s two-way check |
| R6 | A Contract item "in Wave 2", a "lite item of Contract v4.2" | A covers item with `wave: W2`. The lite items of 4.2 are covers items with `wave: W2` (W2-49's CIT-E §1: the three moved items carry `W2`), so the two sets are checked alike | the 4.1 and 4.2 `contract.yaml`; W2-49 CIT-P §6.1 and CIT-E §1 |
| R7 | An item "moved to Wave 2" | A covers item with `wave: W2` whose id is not among the plan's baseline Wave 2 items. The baseline is the ids in the list items directly under the WBS §1 line `**The Contract's N Wave 2 items, by ticket.**`, up to the first line that is not a list item. The next paragraph ("Contract v4.2 adds, lite …") and exit criterion 7's sentence are not the baseline. In the fixtures each moved item also says "lite" and cites the decision, as the real ones do | WBS §1 and §5 criterion 7 ("The Contract's 17 Wave 2 items, and Contract v4.2's lite items"); W2-49 CIT-E §1 |
| R8 | A CIT-P, a "CIT-P line" | A CIT-P is any `docs/changes/*-CIT-P.md`. A CIT-P line is a covers entry in one of its fenced ```` ```yaml ```` blocks: a line `- id: CAP-nn.x` followed, before the next `- id:`, by `wave: <W1 \| W2 \| W3 \| NONE>`. An entry with no `wave:` (W2-49's `- id: … # unchanged, W3`) is not a line. `S2-CIT-P.md` in this tree holds no such entry | W2-49 CIT-P §6.1; `docs/changes/S2-CIT-P.md` |
| R9 | A CIT-P line "with no change" | The Contract has no covers item with that id, or has it in another wave | W2-49's failure KPI; CIT-E §3 "Applied" |
| R10 | The list's counts | Each heading `### 3.n <severity> (<count>)` of `docs/plan/WAVE_2_LIST.md` states the number of rows (`\| W2-[HMLI]nnn \|`) in its section's table. Closed rows (§4, `W2-Cnnn`) are not counted. The prose summary line is not a count these tests fix | `WAVE_2_LIST.md` §3 and §4 |
| R11 | The triage's counts | The `## Counts` table of `docs/plan/WAVE_2_TRIAGE.md`: each cell (severity or `**all**` × Wave 2 / Wave 3 / backlog / Total) equals the count of rows (`\| W2-[HMLI]nnn \| … \| <severity> \| <disposition> \| … \|`) under "Every open row". A disposition that is a W2 ticket id counts as Wave 2. The table of outline items (`S0b2 G-13 …`) is not counted | `WAVE_2_TRIAGE.md` "Counts" and "Every open row" |
| R12 | An input it "cannot read" | Missing, not parsable (YAML or frontmatter), a folder where a file belongs, or no read permission | KPI failure line 2 |

The trees also hold a `docs/contract/CONTRACT_v4.md` built from the same data as the YAML, so a validator that compares
the two finds them in agreement. The validator reads the Contract; that comparison is not fixed here.

## 3. KPI lines, tests and the red reason

Every test fails now for one reason, from `w2_51_support.require_script()`:
`docs/plan/tools/validate_w2.py does not exist yet: the Wave 2 plan validator is not written (W2-51 not implemented)`.

### KPI success line 1: it reads the Wave 2 plan; each check prints pass or fail with a named reason — `test_w2_51_plan_reading.py` (13)

| Test | Success / failure / edge |
|---|---|
| `test_every_check_prints_one_line_with_pass_and_a_named_reason[contract-4.1, contract-4.2]` | success: the eight lines, each PASS with a reason, all in the line form; exit 0 |
| `test_a_ticket_with_only_external_ref_is_read_as_a_wave_2_ticket` | edge: the `W2-03a` ticket, `external-ref` only, matches its bold WBS row and delivers its item |
| `test_a_wbs_row_whose_ticket_is_missing_fails_naming_it` | failure: that ticket removed; `wave2-tickets` names `W2-03a` and `contract-items-delivered` names its item |
| `test_a_wbs_row_with_no_ticket_file_fails_naming_it` | failure: a WBS row with no ticket |
| `test_a_wave_2_ticket_missing_from_the_wbs_table_fails_naming_it[wbs_id-W2-06, external-ref-W2-06b]` | failure: a Wave 2 ticket the table does not list |
| `test_a_malformed_id_is_not_taken_as_a_wave_2_ticket[W2-06ab, W2-06A, W2-6]` | edge: such a ticket's unknown citation does not fail `ticket-contract-ids-exist` |
| `test_an_item_delivered_only_by_a_ticket_with_a_malformed_id_is_not_delivered[W2-03ab, W2-03A, W2-3]` | edge: a malformed id delivers nothing |

### KPI success line 2: the two-way check of exit criterion 7 — `test_w2_51_exit_criterion_7.py` (10)

| Test | Success / failure / edge |
|---|---|
| `test_the_two_way_check_passes_on_a_consistent_tree[contract-4.1, contract-4.2]` | success, on a 4.1 tree and on a 4.2 tree |
| `test_a_wave_2_item_no_wave_2_ticket_delivers_fails_naming_it` | failure: forward, delivery |
| `test_a_wave_2_item_delivered_only_by_a_wave_1_ticket_fails_naming_it` | edge: a Wave 1 ticket's `closes` does not count |
| `test_a_lite_item_of_contract_4_2_no_wave_2_ticket_delivers_fails_naming_it` | failure: a 4.2 lite item undelivered |
| `test_a_wave_2_item_no_acceptance_test_cites_fails_naming_it` | failure: forward, citation (a unit test's citation does not count) |
| `test_a_lite_item_of_contract_4_2_no_acceptance_test_cites_fails_naming_it` | failure: a 4.2 lite item uncited |
| `test_a_contract_id_a_wave_2_ticket_cites_that_the_contract_lacks_fails_naming_it[CAP-99.z, CAP-98]` | failure: backward, a covers id and a capability id |
| `test_an_id_only_contract_4_2_holds_is_unknown_on_a_4_1_tree` | edge: the validator reads the tree's own Contract version |

### KPI success line 3: W2-49's failure KPI — `test_w2_51_cit_p.py` (7)

| Test | Success / failure / edge |
|---|---|
| `test_a_4_1_tree_with_no_cit_p_passes_both_checks` | success: needs no v4.2 merged; exit 0 |
| `test_a_4_2_tree_whose_moved_item_has_its_cit_p_line_passes_both_checks` | success, on W2-49's form (§6.1 YAML, a `# unchanged` entry, a W3 split item) |
| `test_an_item_moved_to_wave_2_with_no_cit_p_line_fails_naming_it` | failure: moved without a CIT-P line |
| `test_an_item_moved_to_wave_2_with_no_cit_p_file_at_all_fails_naming_it` | failure: moved, no CIT-P in the tree |
| `test_a_cit_p_line_with_no_change_in_the_contract_fails_naming_it[wave-not-applied, new-item-not-added, proposal-on-a-4.1-tree]` | failure: a CIT-P line with no change; the third is W2-49's own state before its apply round |

### KPI success line 4: the counts agree with their rows — `test_w2_51_counts.py` (5)

| Test | Success / failure |
|---|---|
| `test_the_list_and_the_triage_counts_agree_with_their_rows` | success (closed rows and the outline table are not counted) |
| `test_a_list_severity_heading_that_disagrees_with_its_rows_fails_naming_it[high-row-added, info-heading-changed]` | failure, list |
| `test_a_triage_count_that_disagrees_with_its_rows_fails_naming_it[severity-cell, all-row]` | failure, triage |

### KPI failure line 1: never the workbench or `docs/source/` by default — `test_w2_51_outside_inputs.py` (3)

| Test | What it shows |
|---|---|
| `test_checks_that_would_need_the_workbench_or_docs_source_are_reported_not_run_by_name` | at least one NOT RUN line; each names its need; none of the eight; NOT RUN alone exits 0 |
| `test_decoy_workbench_and_docs_source_change_nothing_in_the_output` | the same tree run without and then with decoys (`HOME/gov-os-workbench` with decoy coverage matrix, architecture, register and fingerprints; `GOV_OS_WORKBENCH` pointing at it; a decoy `docs/source/` with an original and a decoy `contract.yaml`): identical status lines, the NOT RUN checks still NOT RUN |
| `test_the_decoys_are_neither_read_nor_listed` | every decoy file's and folder's access time, set by the test before its modification time, is unchanged after the run. The test first checks that this file system moves access times on a read and a listing (relatime does), and skips with that reason if it does not |

Shown by behaviour only. No test lists, globs, searches or writes the real `~/gov-os-workbench` (DEC-723), and no test
reads `docs/source/`.

### KPI failure line 2: an input it cannot read is a named failure, never a pass — `test_w2_51_unreadable_inputs.py` (9)

`test_an_input_it_cannot_read_is_a_named_failure_never_a_pass[…]` covers each of these cases: `contract-missing`,
`contract-unparsable`, `wbs-missing`, `list-missing`, `triage-is-a-folder`, `tickets-folder-missing`,
`ticket-frontmatter-unparsable` and `cit-p-unreadable` (no read permission; skipped only when run as root). Each case
asserts four things:
- no Python traceback;
- a FAIL line that names the input;
- none of the checks that need that input prints PASS;
- exit 1.

`test_a_root_that_does_not_exist_passes_nothing` checks that a missing root gives a non-zero exit and no PASS line.

## 4. How the tests were checked before the commit

- A throwaway stand-in validator was written outside the tree, in the session's scratchpad, following readings R1 to
  R12. All 47 tests passed against it, run from single-file copies of this folder whose `SCRIPT` pointed at the
  stand-in.
- Four mutants of the stand-in were each caught:
  - a loose id pattern: 6 failures;
  - reading the workbench: 1;
  - reading `docs/`, `docs/source/` included: 1;
  - ignoring `external-ref`: 10.
- The stand-in was then run read-only over this worktree. The readings hold on the real files:
  - the 17 deliveries are read from `closes:`;
  - the list's and the triage's counts agree;
  - the WBS baseline paragraph gives the 17 items.

  It reported two real findings: the WBS table lacks W2-51 and W2-52, and most Wave 2 items have no acceptance test
  yet. The stand-in was not committed. It stays in the session's scratchpad, which is removed when the session ends
  (DEC-386).

No earlier test was rewritten.
