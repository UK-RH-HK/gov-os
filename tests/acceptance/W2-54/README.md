# W2-54 acceptance tests (DAEO-0rfi, FULL; DEC-768)

Written before the implementation by the independent test designer (MR-3), from the ticket's KPI lines and its
sources (DEC-768, DEC-626, DEC-441, DEC-565, CAP-33) and the decisions that apply (DEC-595, DEC-600, DEC-285,
DEC-628, DEC-221, DEC-462, DEC-136, DEC-491, DEC-732). **50 cases in four files.** No private part of the code to
be written was read; the cases reach the behaviour through public interfaces only.

Run (the project's test command, to its end):

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
      python3 -m pytest tests/acceptance/W2-54 -q -p no:cacheprovider -rs

## How the suite runs this worktree's code (DEC-732)

- Every child process gets `PYTHONPATH` naming this worktree's `src/` (`w2_54_support.SRC`, computed from this
  file's place), per process, never from the session.
- The session fixture `code_under_test` runs `python3 -c "import gov; print(gov.__file__)"` under that
  environment and fails the session unless it prints `/home/usain/gov-os-worktrees/W2-54/src/gov/__init__.py`;
  the `box` fixture asserts the same under the retrieval stand-in. `test_the_suite_runs_this_worktree_s_code`
  states it as a case.
- The checks run as their declarations say: their `command` by `sh -c` in the project root (DEC-285), read from
  this worktree's declaration, so the command under test is the declared one.

## Public interfaces used

| interface | used for |
|---|---|
| `gov context --json --root <p> [--budget N] <ticket>` (W1-24's packet: `authority`, `mandatory`, `supplementary`, `dropped`, `hash`, `tokens`, `budget`) | KPI 1 |
| `gov.retrieval.retrieve.retrieve`, the retrieval's public entry | the stand-in below |
| `python3 -m gov.context.context_check` in the project root (the declaration's command) | KPI 1, failure 1, KPI 2 |
| `gov check --json [--root <p>]` and a declaration's `timeout-seconds` (`src/gov/cli/checks.py`'s documented fields) | KPI 2, KPI 3, failure 2 |
| `python3 -m gov.check.schema` in the project root: its JSON findings and their codes, as it gives them to other types today (`SCHEMA_MISSING_FIELD`, `SCHEMA_INVALID_FIELD`, `SCHEMA_INVALID_TYPE`, `SCHEMA_UNKNOWN_TYPE`) | KPI 4, failure 3 |
| `git show b644d28a:<path>` (this ticket's claim commit) and `git show 2a35fd7b:<path>` (W2-02's held branch) | the declarations before, W2-02's schema file |
| `gov.store.load` and `gov.retrieval.lexical.refresh` | building a temporary project's store and lexical index (as W1-24's suite does) |

### The retrieval stand-in

KPI 1 lets a test control the order in which the retrieval returns its items through the retrieval's public
entry. The suite writes a `sitecustomize.py` into a temporary folder and puts that folder first on `PYTHONPATH`
of the processes of a run (the `gov context` process, and the check's process). It replaces
`gov.retrieval.retrieve.retrieve` with a wrapper that calls the real entry and returns **the same bundle with the
same items in another order**: `reverse`, `rotate` (first item last), `shuffle` (fixed seed), `alternate`
(the retrieval's own order on a question's even-numbered calls, reversed on its odd ones, counted across
processes), or `empty` (no item). The lists beside the evidence (`gaps`, `expansions`, `merge.dropped`) are
reordered alike. For the failure line, `drop-alternate` returns one item fewer on every second call (the items
differ), and `W254_TARGET=<ticket>` limits a mode to the calls for that ticket. Each call is logged, and every
case asserts the stand-in was reached and changed what it says it changed, so a computation that does not go
through the public entry fails the case rather than passing it.

The cases state behaviour only: the same packet, `dropped` included, and the same hash under any order. They
name no sort key and no part of the code to be written.

**Which cases.** Every order case is one where the order cannot decide what the packet holds: every
supplementary item is dropped because the mandatory inputs alone exceed the ceiling (this repository's shape at
`c9537e39`: `gov context DAEO-0rfi` uses 950,383 tokens of 6,000, and drops all 20 retrieval items), the
retrieval returns nothing, or the index is missing. A ticket whose supplementary items only partly fit keeps the
retrieval's best-ranked items, so its contents may follow the rank; the KPI does not fix that order, and no case
asserts it (see "Risks").

## The fixture projects

Temporary git repositories built from scratch in pytest's temporary folder: single named files of this
worktree only (the path map `governance/project/path-map.yaml`, `template/.gitleaks.toml`, and for core-schema
`template/governance/kernel/schemas/common.schema.json` and `audit-report.schema.json`), never a folder, never a
clone. The context fixture holds two charters, seven decisions (one, `ADR-W254-SPLIT`, in twelve sections, so
several retrieval items share its id), eight notes and two tickets: `TK-W254-SMALL` (a short mandatory input;
everything fits) and `TK-W254-BIG` (a mandatory input of about 25,000 tokens, past the default 6,000). The
retrieval returns 20 items for each, including same-id items and a chunk of a file that is no record.

## KPI lines and their cases

| KPI line | cases | red today? |
|---|---|---|
| **S1** one hash per ticket, whatever order the retrieval returns tied items in; nothing dropped or added | `test_w2_54_dropped_order.py`: `test_every_order_of_the_retrieval_s_items_gives_the_same_packet_and_hash[reverse, rotate, shuffle]`, `test_a_budget_below_the_mandatory_inputs_gives_the_same_packet_under_any_order`, `test_the_check_is_green_when_two_computations_see_two_orders` | **red** |
| S1 (what the fix keeps) | `test_the_stand_in_reaches_the_retrieval_s_public_entry_with_tied_and_same_id_items`, `test_two_computations_with_the_retrieval_s_own_order_give_one_packet`, `test_nothing_is_dropped_or_added_every_item_stays_in_the_packet_once[identity, reverse]`, `test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing`, `test_an_empty_retrieval_result_gives_one_packet`, `test_a_store_whose_index_is_missing_gives_one_packet_under_any_order[SMALL, BIG]` | pass |
| **S2** a declared limit that fits the measured run, recorded in the change record | `test_w2_54_time_limit.py`: `test_only_the_timeout_line_is_added_to_the_declaration`, `test_the_declared_limit_is_above_the_runner_s_and_bounded`, `test_the_change_record_states_the_limit_and_its_measurement`, `test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit` | **red** |
| S2 (the other keys unchanged) | `test_the_declaration_s_other_keys_are_unchanged` | pass |
| **S3** `gov check` gives context-reproducibility green here | `test_w2_54_green_here.py`: `test_gov_check_gives_context_reproducibility_green_here` (and `test_the_suite_runs_this_worktree_s_code`, passes) | **red** |
| **S4** `audit-report` exactly W2-02's; nothing of W2-02's other types; core-schema green here, W1-43 untouched | `test_w2_54_audit_report.py`: `test_the_schema_file_is_w2_02_s_byte_for_byte`, `test_a_record_in_the_audit_folder_that_states_no_type_is_held_as_an_audit_report[2]`, `test_a_record_of_type_audit_report_owes_no_shared_frontmatter[2]`, `test_an_audit_report_s_fields_are_held_to_the_schema_s_shapes[3]`, `test_core_schema_is_green_on_this_repository_with_w1_43_untouched`; `test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here` | **red** |
| S4 (nothing of W2-02's other types; W1-43 untouched) | `test_no_schema_file_of_w2_02_s_other_types_comes_with_it`, `test_w2_02_s_other_types_are_judged_as_an_unknown_type[close, adoption-verdict]`, `test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched` | pass |
| **F1** a context whose items or hash differ still fails the check, naming the ticket | `test_a_context_whose_items_differ_still_fails_the_check_naming_the_ticket`, `test_the_check_names_only_the_ticket_whose_context_differs` | pass |
| **F2** a check past its declared limit still fails; no hard-block check weakened | `test_a_check_past_its_declared_limit_is_red`, `test_the_same_check_within_its_limit_is_green` (its control), `test_no_hard_block_check_is_weakened`, `test_the_two_checks_of_this_ticket_stay_hard_block[2]` | pass |
| **F3** outside `docs/audit/` with no `type` still fails; an audit report lacking `milestone`, `commit` or `pack_sha256` fails naming the field | `test_a_record_outside_the_audit_folder_that_states_no_type_still_fails[docs/notes, docs/audit-archive, docs/reports/audit]` (pass); `test_an_audit_report_lacking_a_required_field_fails_naming_it[folder, stated × milestone, commit, pack_sha256]` (**red**) | mixed |

## Red reasons (as seen at `b644d28a`)

- **The order cases (S1):** the `dropped` list comes out in the order the retrieval returned its items
  (`reverse` gives `ADR-W254-SPLIT, …, TK-W254-BIG` where the retrieval's own order gives
  `TK-W254-BIG, …, ADR-W254-SPLIT`), so the packet and its hash differ. Under the `alternate` stand-in the check
  prints `FAIL: TK-W254-BIG: 30d2cf38… != 34ec711b…` and exits 1.
- **The declaration (S2):** no `timeout-seconds` line is added (`it adds []`); no limit is stated ("the check
  gets the runner's 60 seconds"); `docs/changes/W2-54-CIT-E.md` does not exist; the run-as-declared case stops at
  "states no timeout-seconds" without running the check.
- **Green here (S3, S4):** in `gov check --json` here, context-reproducibility is RED ("did not end within its
  time limit of 60 seconds") and core-schema is RED (`SCHEMA_INVALID_TYPE` on
  `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`); run alone, core-schema exits 1 with that one finding.
- **The audit-report cases (S4, F3 second half):** `template/governance/kernel/schemas/audit-report.schema.json`
  does not exist, so each fails on it first. Behind it, today's core-schema gives `SCHEMA_INVALID_TYPE` for a
  report in `docs/audit/` with no `type`, and `SCHEMA_UNKNOWN_TYPE` plus missing `status`/`state_class` for
  `type: audit-report`, naming none of the three fields.

### Cases that pass today, and why they are here

- **F1, F2, F3 first half:** behaviour that holds now and must hold after the fix (DEC-768 item 4: no hard-block
  check is weakened). A fix that made the check skip a ticket, sorted away a real difference, raised the limit
  past a hang, dropped a declaration, or read every typeless record as an audit report would turn them red.
  `docs/audit-archive/` and `docs/reports/audit/` guard against reading the folder by a prefix or a name
  anywhere in the path.
- **S1's keeping cases:** "a ticket whose context is otherwise unchanged keeps its contents: nothing is dropped
  or added by the fix". Each item the retrieval returns stays one entry (same-id items are not merged), and a
  context that fits drops nothing.
- **S4's "nothing of W2-02's other types":** a `close` or `adoption-verdict` record gets exactly the findings of a
  type core-schema does not know. These cases were run once against W2-02's own `schema.py` and schema file as a
  throwaway stand-in in a temporary folder (nothing in the tree): every audit-report case passed there, and the
  two "other types" cases failed (`SCHEMA_UNREADABLE … close.schema.json` in place of `SCHEMA_UNKNOWN_TYPE`), so
  they tell W2-02's audit-report lines apart from the rest of W2-02's change.

## The bound on the time limit (S2)

The declared `timeout-seconds` must be a whole number above the runner's 60 (DEC-595, DEC-600) and **at most
600 seconds**. Grounds:

- The measured run: 122 s alone at `c9537e39` (DEC-768); 164 s here at `b644d28a`, at a 1-minute load of 29 to
  15 on 20 processors (this designer's run; 13 tickets failed). The fix only orders a list, so the run after it
  should be of the same size.
- 600 s is what the sibling G1 check over the same store, `retrieval-regression`, declares. It is about 5 times
  the quiet run and 3.7 times the loaded one, comparable to `secrets-indexing`'s 900 s over its measured 137 to
  369 s (DEC-595). A hang is still caught within ten minutes; a higher limit would hide one longer than any
  kernel check but the secrets scan.
- "Fits" is measured, not argued: `test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit`
  runs the declared command here and requires it to end green before the declared limit, and the `gov check` case
  requires context-reproducibility GREEN under `gov check`'s own load, which a run past its limit never is.

**The added line.** The card says "the `timeout-seconds` line only": the case requires exactly one added line,
`timeout-seconds: <seconds>`, and no other line changed. The measurement goes in `docs/changes/W2-54-CIT-E.md`,
which must name `timeout-seconds`, state the declared number, and speak of the run's seconds, the load and the
tickets measured (the words `seconds`, `load` and `ticket`).

## Cases that need this worktree's store, and how long they run

- `test_w2_54_green_here.py` (4 cases) shares one `gov check --json` run in this worktree: **about 5 to 6
  minutes** (317 s in the red run, at a 1-minute load of 5 to 16; 5 min 58 s alone at a load of 12 to 21, on 20
  processors). It is the slowest part of the suite. Its other checks are
  read but not judged (here `secrets-indexing` is RED for a reason outside this ticket; see the return).
- `test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit`: one run of the check here,
  **about 2 to 3 minutes** once a limit is declared (today it stops at once).
- `test_core_schema_is_green_on_this_repository_with_w1_43_untouched`: about one second.
- Every other case builds its own temporary project: all of them together take about 10 seconds.

The whole suite: 5 min 27 s in the red run (26 failed, 24 passed); about 8 to 9 minutes once the declaration
has its limit and the run-as-declared case runs the check.

## Risks

- **A partly fitting context.** A ticket whose supplementary items only partly fit keeps the best-ranked ones, so
  if the retrieval itself returns tied items in two orders, its supplementary part can still differ. The KPI
  names the `dropped` list; this repository's tickets drop everything; no case asserts the order of
  `supplementary`. If `gov check` stays red here after the fix on such a ticket, that is a new finding.
- **The stand-in's targeting** (`W254_TARGET`) reads the `ticket` keyword the context passes to the retrieval
  today. If the context stops passing it, the targeted failure case fails (it never passes falsely).
