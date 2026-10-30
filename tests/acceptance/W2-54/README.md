# W2-54 acceptance tests (DAEO-0rfi, FULL; DEC-768)

Written before the implementation by the independent test designer (MR-3), from the ticket's KPI lines and its
sources (DEC-768, DEC-626, DEC-441, DEC-565, CAP-33) and the decisions that apply (DEC-595, DEC-600, DEC-285,
DEC-628, DEC-221, DEC-462, DEC-136, DEC-491, DEC-732). **50 cases in four files** in round 1; round 2 (the
query vector, below) adds **15 cases in a fifth file**, `test_w2_54_query_vector.py`: **65 cases in five files.**
Round 3 (the query-vector cache, at the end) adds **15 cases in two files**, `test_w2_54_query_cache.py` and
`test_w2_54_sandboxed_worker.py`: **80 cases in seven files.**
Round 4 (the CPU-only embedder, at the end) adds **16 cases in two files**, `test_w2_54_cpu_embedder.py` (14, with
stand-ins) and `test_w2_54_shared_gpu.py` (2, `shared_gpu`, run by the lead): **96 cases in nine files.**
No private part of the code to be written was read; the cases reach the behaviour through public interfaces only.

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
| **S3** `gov check` gives context-reproducibility green here (in a close, gate (b)'s `gov check`: "W2-75", at the end) | `test_w2_54_green_here.py`: `test_gov_check_gives_context_reproducibility_green_here` (and `test_the_suite_runs_this_worktree_s_code`, passes) | **red** |
| **S4** `audit-report` exactly W2-02's; nothing of W2-02's other types; core-schema green here, W1-43 untouched | `test_w2_54_audit_report.py`: `test_the_schema_file_is_w2_02_s_byte_for_byte`, `test_a_record_in_the_audit_folder_that_states_no_type_is_held_as_an_audit_report[2]`, `test_a_record_of_type_audit_report_owes_no_shared_frontmatter[2]`, `test_an_audit_report_s_fields_are_held_to_the_schema_s_shapes[3]`, `test_core_schema_is_green_on_this_repository_with_w1_43_untouched`; `test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here` (in a close, gate (b)'s `gov check`: "W2-75") | **red** |
| S4 (nothing of W2-02's other types; W1-43 untouched) | `test_no_schema_file_of_w2_02_s_other_types_comes_with_it[HEAD, 4ce16df2]`, `test_w2_02_s_other_types_are_judged_as_an_unknown_type[close, adoption-verdict × HEAD, 4ce16df2]` (read through git since run 5: "Run 5 (DEC-874)", at the end), `test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched` (in a close, after gate (b)'s `gov check`: "W2-75") | pass |
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
  Since W2-75 (DEC-937), inside a close it runs no `gov check` and takes well under a second ("W2-75", at the end).
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

---

# Round 2: the query vector (owner, 2026-10-18, P-W2-30 (a))

The owner widened the ticket for one more round (DEC-773, staged; the ticket cites it as "owner, 2026-10-18,
P-W2-30 (a)"). Round 1's verification left context-reproducibility red on 14 tickets of this repository, with
**different items** in the two computations: the embedder gives a text a slightly different vector when a
different text was embedded just before it. The new KPI line (success 2):

> The same text always gets the same query vector, whatever was embedded before it: query vectors are stored,
> keyed by the model, the model's revision and the exact text, and a stored vector is used whenever its key
> matches; whether an embedder setting (thread count, seed) also removes the variation is measured first and
> recorded in the change record.

Written by a fresh independent test designer before the implementation, from the KPI line, the owner's decision
as the lead gave it, DEC-768, DEC-374, DEC-379, DEC-381, DEC-342, DEC-322, DEC-221, DEC-462, DEC-136, DEC-491 and
DEC-732, and W1-19's suite (its interface table and how it stands in for Ollama). The round-1 cases are unchanged;
no existing case was rewritten. The measurement of an embedder setting is the engineer's, recorded in the change
record: no case judges it (the KPI line says it is measured, and the stored vectors are used whatever it shows).

## What the cases state, and what they do not

The cases state **what an answer is**: the hits of `gov.retrieval.semantic.search(root, q, refresh=False)`, their
order and their `distance`; the bundle of `gov.retrieval.retrieve.retrieve(root, q)`; the packet and hash of
`gov context --json`; the verdict of the context-reproducibility check run as its declaration says. They never
state where a vector is kept, in what form, when it is written, or under what name; they name no part of the code
to be written. "Stored" is seen only as its effect: an answer that does not change whatever was asked before it,
across processes as well as within one.

## The stand-in embedder (`w2_54_support.EmbedderStandIn`)

Built in this suite's support file (no other suite's support is imported), after the manner of W1-19's: a loopback
HTTP server at `OLLAMA_HOST` that answers `GET /api/version`, `GET /api/tags` (the model list: the pinned model with
its digest, the model's revision, DEC-374), `POST /api/show`, `GET /api/ps`, `POST /api/embed` and
`POST /api/embeddings`, with 1024 numbers made of the words of a text. What it adds:

- **The measured variation.** A text embedded right after a *different* text gets
  `unit(own + 0.35 × previous)`; right after itself (a repeat), or as the very first text, it gets its own vector.
  This is the real embedder's shape as the owner's finding states it (the first embedding of a text after another
  text differs from its repeats; repeats are stable). **Its size is exaggerated on purpose**: the measured
  difference is up to 0.001948 in a component; 0.35 moves a question's nearest hits, so the variation shows in the
  order of the hits and in a context's items, not only in a distance. The corpus of every fixture is embedded with
  the variation off, so two projects built alike hold the same vectors.
- **Targets.** A question can be sent to the words of one file of the corpus (`targets`), matched by the longest
  key the text sent *ends with*, **character for character**: no case folding, no Unicode normalisation, no
  stripping. The nearest hit then shows which vector a search used. (Today the facet sends
  `Instruct: …\nQuery: <the question>` with the question exactly as given; the match by the end of the text needs
  no knowledge of that prefix.)
- **Another revision.** `digest` is what its model list reports; `OTHER_DIGEST` is another build of the same model.
- **Failure.** `mode = "fail"`: every embedding request answers HTTP 500; `mode = "short"`: one vector fewer than
  asked (none, for one question).
- Every request is recorded: the texts sent to be embedded, in order, and the model each request names.

**The model part of the key.** No public interface lets a case change the embedding model: the model is the pin of
ADR-0002 §2, and selecting another is W2-32's (CAP-19, "swap by configuration"). The key's model part is held
instead by (a) the revision case, since another build of the model under the same name is another key, and (b) that
case's assertion that every request to be embedded names the pinned model (`qwen3-embedding:0.6b`), so every
stored vector is one of that model's. When W2-32 makes the model configurable, a case for "another model, another
vector" belongs to it.

## The fixtures

Temporary git repositories built from scratch (single named files of this worktree only: the path map and
`template/.gitleaks.toml`), each with its own store, lexical index and vectors, built through the stand-in
(`gov.retrieval.semantic.refresh`, then `gov.store.load`). The corpus is six notes, each about one subject with words
no other note holds (bakery, tides, orchard, kiln, forge, apiary). The context fixture adds a charter and three
tickets whose titles differ (`TK-W254-BAKERY`, `TK-W254-TIDES`, `TK-W254-ORCHARD`), so each ticket's context asks
the retrieval its own question. (As seen at the stand-in, a context sends the embedder **the first word of the
ticket's title**: `Sourdough`, `Harbour`, `Pear` here. In a first probe, three tickets whose titles all began with
"the" sent `the` for every context, so the variation never showed and the check was green. Round 1's fixture gives
its two tickets one title. No case depends on how the question is made from the ticket; the titles only begin with
words of their own.) Every process gets the scratch environment of round 1 (empty `HOME`,
this worktree's `src/` on `PYTHONPATH`, DEC-732), `OLLAMA_HOST` naming the stand-in, and a folder that links the one
`sqlite_vec` package the Python that runs pytest imports (as W1-19's suite does).

## The new KPI line and its cases

| part of the KPI line | case | red today? | red reason (as seen at `5ac58b7a` plus this suite) |
|---|---|---|---|
| **1. one text, one vector, whatever was embedded before** (separate processes) | `test_one_question_asked_again_after_others_gives_the_same_answer_across_processes` | **red** | "answer 2 … differs from the first": kiln at 0.483027488 then 0.483027518, tides at 0.6696 then 0.7911 |
| 1 (within one process) | `test_one_question_asked_again_after_others_gives_the_same_answer_within_one_process` | **red** | the same figures: answer 2 differs from the first |
| 1 (the retrieval's public entry) | `test_the_retrieval_s_public_entry_gives_one_bundle_for_one_question_whatever_was_asked_before` | **red** | "one question, two bundles in one store (bundle 3)": the bundle asked in a later process holds the same six items with tides last instead of second |
| **2. two computations of every ticket's context give one hash** | `test_gov_context_twice_for_each_ticket_with_others_between_gives_one_packet` | **red** | "TK-W254-BAKERY: 3 hashes in 3 computations in one store" |
| 2 (the check, over several tickets) | `test_the_context_check_is_green_over_several_tickets_with_an_embedder_whose_vectors_vary` | **red** | the check exits 1: `FAIL: TK-W254-BAKERY: … != …` (and the two other tickets) |
| **3. a stored vector is never taken for another key**: another revision; the same revision again | `test_a_stored_vector_is_not_used_under_another_revision_and_is_used_again_when_the_revision_matches` | **red** | its last part: with the first digest again the answer is not the first answer (kiln at 0.0561416708 against 0.0561417267, the second hit orchard at 0.885 in place of tides at 0.670); its other parts pass today |
| 3: a text that differs in any character | `test_a_text_that_differs_in_any_character_gets_its_own_answer[case, spacing, trailing-newline, unicode-normal-form]` | pass | — |
| **4. the first answer is unchanged** | `test_a_question_asked_for_the_first_time_gets_the_vector_the_embedder_returns_for_it` | pass | — |
| **5. nothing is left behind by a failed or partial call** | `test_a_failed_embedding_gives_no_hit_and_leaves_nothing_a_later_search_uses[fail, short]` | pass | — |
| **6. one project's vectors are never another's** | `test_two_projects_do_not_share_query_vectors` | pass | — |
| 1 with **the real embedder** | `test_with_the_real_embedder_one_question_gives_one_answer_whatever_was_asked_before` | **red** (here) | answer 2 differs from the first: kiln at 0.36549 then 0.36438, orchard at 0.72068 then 0.72273 (the real variation) |

**Count:** 15 cases (11 functions); 7 red today, 8 pass today.

### The cases that pass today, and why they are here

They hold what storing a vector could break; today nothing is stored, so each holds trivially, and each turns red
under a store that gets the key wrong.

- **Another spelling** (case, two spaces for one, the decomposed Unicode form of `café`, a trailing newline): the
  embedder sends the question to the kiln and the other spelling to the forge. A key that folds case, collapses
  spacing, normalises Unicode or strips the text would give the other spelling the kiln.
- **Another revision**: under the other digest, the answer is the forge's (that build's vector), **or the facet is
  unavailable with no hit**; never the kiln's. Unavailable is accepted because a mismatched model failing closed is
  CAP-19's (Wave 2) and no source here decides it; a store keyed without the revision, or with the index's
  revision instead of the one the model list reports now, gives the kiln. This part passes today; the case is red
  for its last part.
- **The first answer**: a question asked for the first time is sent to the embedder once, and answered with the
  vector it returns (the orchard, which the question's own words do not lead to); two projects built and asked alike
  give the same first answer, hit for hit and distance for distance.
- **A failed or partial call** (HTTP 500; one vector fewer than asked): unavailable, no hit, as today; the next
  search with a healthy embedder **asks the embedder again** and gets its vector. A store that kept anything from
  the failed call (an empty or partial vector, a marker) would not ask again or would answer from it.
- **Two projects**: the same model, revision and question, two stores, two embedders that answer differently: each
  project gets its own embedder's answer; the second project's search changes no file of the first project's
  runtime folder and writes nothing under `HOME` (a vector kept for every project, under `HOME`, would show there).

## The real embedder

`test_with_the_real_embedder_one_question_gives_one_answer_whatever_was_asked_before` **needs the real embedder**
(an `ollama` executable at `GOV_OLLAMA_BIN`, on `PATH` or at `~/.local/ollama/bin/ollama`, with
`qwen3-embedding:0.6b` in Ollama's model folder), `sqlite_vec` and `gitleaks`, and **skips with the reason** when
one is absent; nothing is started or installed to decide it. It runs in this machine's own environment (W1-19's
`real_env` manner: `GOV_ROLE` and `GOV_TICKET` removed, this worktree's `src/`, the Hugging Face libraries held
offline), so `gov` reaches this machine's Ollama (and, DEC-261, starts it and leaves it running if it is not). It
embeds a fixture of six notes and asks the question, three other questions, and the question again, in separate
processes and in one. **Here it ran and is red**: the real variation reproduced on the first repeat. Every other
round-2 case runs against the stand-in only; the stand-in cases skip, with the reason, only where `gitleaks` or
`sqlite_vec` is absent.

## How long the new cases run

`test_w2_54_query_vector.py` alone: **22 to 24 s** (61 s the first time, when the real-embedder case waited for
Ollama to load the model). The stand-in is deterministic: two runs gave the same figures, hash for hash. Each stand-in case takes 2.5 to 6 s; the real-embedder case 7.7 s with the model
loaded. The whole suite: about 9 minutes as before, plus about half a minute.

## The tension with W1-19's "a search that may not write" (returned as a package)

W1-19's interface table says a semantic search with `refresh=False` writes nothing (DEC-379: "`refresh=False` never
writes"; DEC-342; DEC-322: only orchestrator-role sessions write the live store). The retrieval's public entry, and
so `gov context` and the context check, search with `refresh=False`. The new line says query vectors are stored.
These cases require the same answer across separate processes, through `refresh=False` searches, in an environment
with no `GOV_ROLE`: so some search that may not write must leave something a later process reads. **No W1-19 case
necessarily turns red**: `test_a_search_that_may_not_write_reports_a_missing_index_and_writes_nothing` (W1-19,
`test_w1_19_unavailable.py`) asks a project with **no** index and requires that no `.gov-runtime/` appear; an
implementation that stores a query vector only where an index exists keeps it green. But the decided text of
DEC-379 and W1-19's README line do not hold together with the new line, and in a worker session the vector would be
written into the live store against DEC-322. The designer's package (P-R2-1) is in the return; this suite does not
settle it, and no case states where the vector is written.

## Risks (round 2)

- **The "green here" cases mean nothing on a stale store.** `gov check`'s context-reproducibility, and the
  run-as-declared case, read this worktree's store. Any change to a tracked file after the lead's rebuild (this
  round's own test files included) makes the lexical and semantic indexes `stale`; both facets are then unavailable,
  the retrieval returns nothing, every context is the same twice, and the check is green **for that reason**. Seen
  in this round: with this suite's files in the tree, `retrieve(DAEO-0rfi)` reports both facets `stale` and returns
  0 items, the run-as-declared case passed in 31 s and `test_gov_check_gives_context_reproducibility_green_here`
  passed, where round 1's verification saw 14 tickets red on a fresh store. They are only evidence after a full
  rebuild at the commit under test.
- **The stand-in's size of variation** is not the real one (0.35 against at most 0.002 a component). The cases do
  not depend on the size, only on its shape (after another text, not on a repeat); the real-embedder case holds the
  real size, where Ollama is present.
- **The revision part needs the revision now**: a store that keys a vector by the revision the index was built with,
  and not by what the model list reports at the time of the search, fails the revision case. That is the stricter
  reading of "keyed by … the model's revision": a vector made by one build is never another build's.
- **"The same answer" is exact**: equal distances as floats. A store that kept a vector at a lower precision than the
  first answer used would make the first answer and the later ones differ (the first answer is the embedder's
  vector, KPI part 4); keeping it exactly as the first search used it passes both.

---

# Round 3: the query-vector cache (owner, 2026-10-18, P-W2-32 (a))

The owner allowed one more round after the lead's package PKG-W2-54-2: DEC-782 (P-W2-32 (a)) and DEC-784 (P-W2-34
(a)), staged, cited by the ticket as "owner, 2026-10-18, P-W2-32 (a)" and "P-W2-34 (a)". Round 2's code stores query
vectors at query time; its verification left five W1 cases red because a read now writes one file. DEC-782 amends
DEC-379 for that one file only. The ticket's three new success lines:

> **S3.** The query-vector cache is the one file a read command writes: a derived file under .gov-runtime/, keyed by
> model, model revision and a hash of the exact text, written atomically and safely by several sessions at once,
> bounded in size, and rebuildable from nothing.
>
> **S4.** Where the cache cannot be written (a sandboxed worker, whose .gov-runtime is read-only), the same text still
> gets the same vector; a test shows it inside a launched, sandboxed worker.
>
> **S5.** W1-46's live cases launch their sessions with no CLAUDE* variable in the environment.

Written by a fresh independent test designer before the implementation, from those lines, DEC-782 and DEC-784 as the
lead gave them, DEC-768, DEC-773, DEC-374, DEC-379, DEC-381, DEC-342, DEC-322, DEC-317, DEC-221, DEC-462, DEC-136,
DEC-491 and DEC-732, W1-19's interface table and W1-46's live suite. No earlier W2-54 case was changed (two helpers
were added to `w2_54_support.py`: a `wait` call for the driver and the round-3 section; and the `local_only` marker
to `conftest.py`). S5 is W1-46's rewrite (below, "The rewrites"); no W2-54 case states it.

## What the cases state, and what they do not

What a read gives (the semantic search's hits and distances, `gov retrieve --json`'s bundle, `gov context --json`'s
packet and hash) and what it leaves on disk (the project's file tree before and after). **No case names the cache
file, its form, its key's form or the code that writes it.** The cache is seen as "the file under `.gov-runtime/` a
read wrote that is not the store" (the store is `store.db*`, W1-19's "one shared store"). "Deleted" means every file
under `.gov-runtime/` beside the store removed; "the file read-only" means every such file read-only.

## The bound: where it is stated and how a case sees it (an interface this KPI needs)

"Bounded in size" needs a stated bound and, to run in seconds, a way to lower it. The cases use:

- **The setting `GOV_QUERY_VECTOR_CACHE_MAX_BYTES`**, an environment variable read by the read commands: the bound,
  in bytes, on the files beside the store under `.gov-runtime/` (the cache, and anything it keeps beside itself).
  The cases lower it to **262,144 bytes (256 KiB)**.
- **The default bound** is stated in the change record `docs/changes/W2-54-CIT-E.md`, on a line that names the
  setting, as a whole number of bytes; the change record also says what happens at the bound (no case judges the
  prose).
- **How a case sees it:** the sum of the sizes of the files beside the store, after every process, is at most the
  bound. 200 distinct texts of at least 4,096 bytes each (1,024 numbers kept exactly) are at least 819,200 bytes,
  more than three times the lowered bound, so the bound is reached whatever the cache keeps per entry.

What the cache does at the bound (evict, stop writing) is the engineer's to choose and state; the cases require only
that reads go on succeeding and give the same answers.

## The new KPI lines and their cases

| part | case | red today? | red reason (as seen at `3bee9a50` plus this suite) |
|---|---|---|---|
| **S3.1** the one file a read writes; nothing authoritative | `test_w2_54_query_cache.py::test_gov_retrieve_and_gov_context_write_at_most_one_derived_file_under_the_runtime_folder` | pass | — |
| S3.1 no index, nothing created | `::test_in_a_project_without_an_index_a_read_creates_nothing` | pass | — |
| **S3.2** keyed by a hash of the text, not the text | `::test_no_file_of_the_project_holds_a_question_in_clear_after_it_was_asked` | **red** | "the question is kept in clear: `['.gov-runtime/query-vectors.db (UTF-8)']`" |
| S3.2 the exact text, all of it | `::test_two_long_texts_that_differ_only_in_their_last_character_get_their_own_answers` | pass | — |
| **S3.3** several sessions at once | `::test_several_processes_reading_at_once_on_a_cold_cache_get_the_one_answer_and_lose_no_entry` | **red** | "process 1, 'how does the glazed meet the prunes item0103': one text, two answers": the third hit apiary at 0.95327 in place of tides at 0.95820 (the answer depends on the interleaving) |
| **S3.4** a stated bound | `::test_the_change_record_states_the_cache_s_bound_and_the_setting_that_lowers_it` | **red** | "docs/changes/W2-54-CIT-E.md does not name the setting GOV_QUERY_VECTOR_CACHE_MAX_BYTES" |
| S3.4 never past it; reads at it give the same answers | `::test_the_cache_never_grows_past_its_bound_and_reads_at_the_bound_give_the_same_answers` | **red** | "the cache grew past its bound of 262144 bytes: [258048, 503808] after 100 texts" |
| **S3.5 / S4** one answer whatever the cache's state: cold, warm, deleted, full, `.gov-runtime/` read-only, the file read-only | `::test_one_text_gets_one_answer_whatever_the_cache_s_state[cold, warm, deleted, full, unwritable-folder, unwritable-file]` | **red** (6) | each "one text, two answers" against the answer the text gets first in a new store (kiln 0.48303, tides 0.66965 second): cold after two other texts gives bakery 0.90656 second; warm, apiary 0.94777 second; deleted, forge 0.95328 second; full ("first asked after 200 other texts"), bakery 0.90656 second; `.gov-runtime/` read-only, tides 0.95328 second; the file read-only, kiln 0.52975 first |
| S3.5 / S4 for a context: one packet hash | `::test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state` | **red** | "cold, after another ticket: one ticket, two packets: f5beed7f… != a1a24120… (the first in a new store)" |
| **S4** inside a launched, sandboxed worker | `test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written` (`local_only`) | **red** | "inside the sandbox, one text got two answers": first kiln 0.45228, forge 1.0; again kiln 0.48303, tides 0.79107 |

**Count:** 15 cases (10 functions); 12 red today, 3 pass today.

(The `full` state first asked the question before filling the cache, and passed today: the answer came from the
cache, which today's code never empties. It now asks the question for the first time when the cache is full; a
question asked before the cache filled, and perhaps evicted, is the bound case's "first and last ten texts asked
again".)

### The cases that pass today, and why they are here

Round 2's code already writes one file and keys it by the whole text; these cases hold what the change must keep.

- **One file, nothing authoritative:** two `gov retrieve` and two `gov context` runs leave at most one file changed,
  always the same, under `.gov-runtime/`, not `store.db*`, not tracked. A fix that added a lock file, a journal left
  behind, a second cache or a write to the store turns it red.
- **No index, nothing created:** a project never indexed gets no `.gov-runtime/` from a read (W1-21 holds it for the
  retrieval; here for `gov context` too). A cache made before the index is checked turns it red.
- **The long texts:** about 8,000 characters differing only in the last; the stand-in is sent the whole text (seen:
  7,893 characters for a 7,801-character question). A key cut to the first characters of the text, or a hash of a
  prefix, gives the second text the first's answer.

### The red reasons, and what each case holds after them

- **Concurrency** is red today only for the variation: run three times with the stand-in's variation off, today's
  code passed it every time (no error, no lost or torn entry, nothing left beside the store). After the fix it holds
  the atomic, safe writes: six processes released together (each waits on a file until all have imported the code),
  then every text asked again sends none to the embedder, and at most one file is beside the store.
- **The states:** today the first answer a text gets depends on what was embedded just before it, so the cold answer
  differs from the reference and the warm and deleted answers repeat or recompute that drifted vector; with the
  cache unwritable each read embeds afresh after another text. No state errors today (exit code 0, no traceback:
  checked on every read).
- **The reference** is the answer a text gets as **the first question asked of a new store built alike**, by a fresh
  stand-in right after it embedded that store's corpus (an ordinary process, the cache writable and cold). In the
  sandboxed case it is the first text a fresh stand-in sees, inside and outside alike. A deterministic computation
  gives every state that answer; a computation that depends on the order, or on the cache, does not.

## The sandboxed worker (S4)

`test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written` starts **one
real worker session through `gov launch`** under its OS sandbox, as W1-46's live cases do: W1-46's fixture project
(`w1_46_support.make_project`, its held-out stand-in), the engineer role on W1-46's ticket, `--model haiku`,
`--permission-mode acceptEdits`, `--allowedTools Bash`, `--max-turns 6`, and the environment of DEC-784 (no `CLAUDE*`,
`GOV_ROLE` or `GOV_TICKET`). The session runs one Bash command, a probe the case wrote into
`.gov-runtime/scratch/w2-54/`.

**How it reaches an embedder.** Checked first, with one real session: from inside the sandbox **this machine's Ollama
is not reachable** (`curl http://127.0.0.1:11434/api/version` ends with exit code 7: the sandbox has its own network,
and the engineer's allowlist is empty). A stand-in **started inside the sandbox** binds a loopback port there and
answers. So the probe starts round 2's stand-in embedder (from this suite's support file, with its variation) inside
the sandbox, and every read inside names it at `OLLAMA_HOST`. The probe records the outcome of the curl to this
machine's Ollama in its result file; the case does not judge it.

**Where the cache cannot be written.** Also checked first: the sandbox makes read-only only the names under the
launched project's `.gov-runtime/` that a literal deny rule names at launch. The launcher's rules for the rest of
`.gov-runtime/` have patterns, which the Linux sandbox skips (DEC-311's recorded residual). **A new file under the
worker's own `.gov-runtime/` is writable from its Bash:** in the probe run, `touch .gov-runtime/w2-54-new-name`
succeeded and round 2's cache file was made there from inside the sandbox. A project **outside** the launched
repository is read-only to the worker as a whole (W1-46 success 8; in the probe run a new file there was refused). So
the worker reads a project with a built index that lies outside its repository: that project's `.gov-runtime/` is the
read-only one the KPI line names. The case holds that premise: the reader inside tries to make a file there and must
fail, and the folder's files are unchanged after the session.

**What it asserts.** This worktree's `gov` inside (`gov.__file__`); the stand-in inside was asked the text; every read
ends with exit code 0 and no traceback, and the semantic facet answers (a read with no semantic answer fails the
case: it did not reach an embedder); the text, asked again after another text, gets the same hits, order and
distances, and `gov retrieve` gives the same bundle; and both are the answer an ordinary process outside the sandbox
gets, with the same reader, the same environment (only `OLLAMA_HOST` and `TMPDIR` differ) and a fresh stand-in, for
the same project afterwards.

**Cost and needs.** One headless session (the real CLI at `~/.local/bin/claude`, the caller's credentials), one Bash
call; `bwrap`, `socat`, `gitleaks`, `sqlite_vec`. No network. It fails (it does not skip) when a prerequisite is
missing, as W1-46's live cases do. Leave it out with `-m "not local_only"`. Its run here: 8 s.

## The real embedder and the real CLI

- **The real embedder** (this machine's Ollama): no round-3 case needs it. Every round-3 case uses the stand-in; the
  stand-in cases skip, with the reason, only where `gitleaks` or `sqlite_vec` is absent.
- **The real CLI**: only the sandboxed-worker case (`local_only`, above). The `gov` commands of the other cases are
  this worktree's `gov`, run as `python3 -c` of its entry (as round 1 and 2), never an installed console script.

## How long the new cases run

The two new files together: **49 s** in the last red run (a 1-minute load of 15 on 20 processors); 92 to 131 s in
runs at a higher load. The concurrency case takes 8 to 21 s, the bound case 6 to 23 s, the full state about 4.5 s,
the others 1 to 4.5 s each. `test_w2_54_sandboxed_worker.py`: **8 to 10 s** here (one haiku session; allow up to its
420 s limit). The whole suite: as before (about 9 minutes, most of it the green-here file) plus about one minute.

## The rewrites (other suites)

- **W1-21** (`test_a_retrieval_writes_nothing[a question, a ticket, batches of one]`,
  `test_the_command_writes_nothing`) and **W1-19**
  (`test_the_vectors_are_in_the_shared_store_beside_the_lexical_index`): the expectation "a read writes nothing" /
  "`.gov-runtime/` holds only `store.db*`" becomes "nothing but one derived file under `.gov-runtime/`, not the
  store". Each suite's README has a section "Rewrite (W2-54, DEC-782, 2026-10-18)". No pass line or threshold moves.
- **W1-46**: the live fixture removes every `CLAUDE*` variable, and still `GOV_ROLE` and `GOV_TICKET` (DEC-784).

## Risks (round 3)

- **The worker's own `.gov-runtime/` is not read-only for new names** (above). The KPI line's premise ("a sandboxed
  worker, whose .gov-runtime is read-only") holds for the names a literal rule covers and for any folder outside the
  repository, not for a new file in the worker's own `.gov-runtime/`: a worker's read writes the cache there. That
  is DEC-311's residual, not this ticket's; the sandboxed case does not depend on it.
- **The bound's setting is an interface this suite names.** If the engineer states the bound another way (a count of
  entries, a constant), the two bound cases and the `full` states stay red until the setting exists; the README
  names it so the engineer can provide it, and the lead can change it by a decision.
- **Concurrency against the stand-in is strict.** The stand-in's "previous text" is shared by every process, so a
  computation that sends a text in two requests can be split by another process's request. A computation that is
  deterministic per request (one request whose result does not depend on another's) passes.
- **Time-dependence:** the concurrency case releases its processes after 1.5 s; on a very slow machine a process may
  not yet wait at the start line. The case is still valid (fewer processes truly at once), it does not pass falsely.

# Round 4: the CPU-only embedder (owner, 2026-10-19, P-W2-40 (b))

The lead's measurement after round 3 (change record §5.5) was red: on the shared GPU runner a text's vector depends on
the prompt computed just before it, and round 3's `num_gpu: 0` on a request to the shared runner reloads that runner
on the CPU for every user of the machine. The owner decided DEC-798 (P-W2-40 (b), 2026-10-19; not yet in the
register): (1) a CPU-only embedder that `gov` starts on its own port answers query embeddings, and only those; the
shared GPU runner keeps building the index; no request to the shared runner names `num_gpu: 0`; (2) the cache's key
names the device, so a GPU-computed vector (as `b33ef9b3` cached) is never served; (3) W1-21's hit@5 is re-measured
before merge on the real models with CPU query vectors against the GPU-built index, in the lead's session, and a
figure below 80 is a red for this ticket; (4) the resource gate counts the CPU embedder's 2.4 GB (nothing to test);
(5) DEC-261 is amended: `gov` starts two daemons on demand and stops neither. DEC-797 (delegated): the setting
`GOV_QUERY_VECTOR_CACHE_MAX_BYTES` (default 64 MiB) is the cache bound's public interface. The ticket's two new lines:

> **Success 5.** On the shared GPU Ollama, the same text read many times, after different texts and by two sessions at
> once, gets one vector: query embeddings come from the CPU-only embedder on its own port, the shared runner is never
> moved to the CPU, and the cache key names the device.
>
> **Success 6.** W1-21's hit@5 on the real models, with CPU query vectors against the GPU-built index, is at or above
> its pass line of 80; the figure is recorded in the change record.

Written by a fresh independent test designer before the implementation, from those lines, DEC-798 and DEC-797 as the
lead gave them, DEC-260, DEC-261, DEC-782, DEC-374, DEC-414, DEC-732, W1-19's interface for an unavailable facet and
the change record's §5 (the measurements). No private part of the code was read.

## The interfaces this KPI needs

The cases name these; none exists yet, and the lead can change any of them by a decision:

- **The setting `GOV_QUERY_OLLAMA_HOST`**: the CPU embedder's address, in `OLLAMA_HOST`'s form (`host:port`, with or
  without `http://`). **Its default `127.0.0.1:11435`** (the shared runner's default port plus one), which the
  `shared_gpu` cases use with the setting unset. `OLLAMA_HOST` stays the shared runner's address.
- **The start (DEC-260, DEC-261 as DEC-798 amends it):** where nothing answers at that address, a read starts the
  executable found as DEC-260 finds it (`GOV_OLLAMA_BIN`, then `PATH`, then `~/.local/ollama/bin/ollama`) as
  `ollama serve`, with **`OLLAMA_HOST` set to the CPU address** in its environment, and **told to use no GPU**: in its
  environment `CUDA_VISIBLE_DEVICES` names no device (`-1`, Ollama's documented way; any non-empty value none of whose
  comma-separated items is a device number or a `GPU-…`/`MIG-…` id), or `OLLAMA_LLM_LIBRARY` begins with `cpu`. An
  empty or absent `CUDA_VISIBLE_DEVICES` does not count. It is never
  stopped (no SIGTERM or SIGINT reaches it; it is alive after the read ends).
- **"The CPU embedder computed it":** the embedder at the CPU address reports, at `GET /api/ps`, the pinned model with
  `size_vram` 0 (and `size` above 0). The case reads it the way Ollama reports it; how `gov` asks is not judged.
- **An unavailable facet** is W1-19's: `available` false, `state` `FACET_UNAVAILABLE`, a non-empty `reason`, no hits;
  in `gov retrieve --json`, `result.facets.semantic.{available, reason}`.

## The stand-ins of round 4 (`w2_54_support.py`)

- **`EmbedderStandIn`** (round 2's, with its variation: on its "GPU" a text's vector drifts with the text before it)
  now has a device. `device="gpu"` stands for the shared runner, `device="cpu"` for the CPU embedder. It models the
  runner as §5.5.2 measured it: a request without `options` is served by the runner already loaded, and a request
  with `num_gpu` 0 reloads it on the CPU. `/api/ps` reports the model once loaded, with `size_vram` equal to `size`
  (gpu), half of it (partial) or 0 (cpu). Before anything is loaded it reports nothing, as Ollama does. A case can
  make it report the GPU, half, nothing or only another model. It records each request's route, texts and `options`.
  **Its variation is kept whatever the device.** The stand-in does not model the CPU's determinism, so the
  determinism cases of rounds 2 and 3 still hold the code to a computation that does not depend on the text sent
  before.
- **The stand-in `ollama` executable** (`Daemons`): a script put where DEC-260 looks. Run as `serve`, it records its
  argv, its pid and its environment (`OLLAMA_*`, `CUDA_*`, `HIP_*`, `ROCR_*`, `GPU_DEVICE_ORDINAL`), waits a second,
  and then serves `EmbedderStandIn` at its `OLLAMA_HOST`. That embedder runs on the CPU when the GPU was hidden, and
  otherwise reports the model on the GPU. A second start at the same address fails to bind and exits 1, as Ollama
  does. A stop signal is recorded. Each case kills what it started when it ends.
- **`NotAnEmbedder`**: a listener that answers HTTP 404 with an HTML page to every request.
- **`plant_round_3_entry`**: writes the question's vector into `.gov-runtime/query-vector-cache.db` in round 3's
  layout, as seen read-only in this worktree's store: the table `query_vector(model, revision, text_sha256,
  embedding)`, the key being the model, the full digest and the sha256 of the exact text sent, and the vector 1,024
  float32 numbers. The vector is the shared runner's (the forge's), keyed by both the text round 3 sent
  (`Instruct: … Query: ` plus the question) and the text sent today.

## The fixture change (rounds 2 and 3, and the sandboxed worker)

Because round 4's code reads the question's vector from `GOV_QUERY_OLLAMA_HOST`, the earlier cases set it too:
`embed_env(box, endpoint, cpu=None)` sets `OLLAMA_HOST` to `endpoint` (or a dead port) and `GOV_QUERY_OLLAMA_HOST` to
`cpu`, **or, when no `cpu` is given, the same as `OLLAMA_HOST`**. `semantic_project` passes `cpu` through. The
sandboxed reader sets `GOV_QUERY_OLLAMA_HOST` to the `OLLAMA_HOST` it gives (the stand-in inside the sandbox).
`/api/ps` of the stand-in now reports the loaded model, where it was `[]`. **So rounds 2 and 3 run against one
stand-in at both addresses, which keeps its variation:** each case's expectation, reference and red reason is
unchanged. This is the fixture change the commit's `Rewrite-Reason` names.

The stand-in of rounds 2 and 3 has the default device, `cpu`. Once a request has loaded the model, its `/api/ps`
reports the model with `size_vram` 0, so round 4's rule (a vector is used only from an embedder that reports the
model on the CPU) lets those cases be answered, as before. Before the first request it reports nothing (as Ollama
does), so the code has to look at `/api/ps` after it has asked for the vector, not before.

## The KPI parts and their cases

All in `test_w2_54_cpu_embedder.py` but the last two rows. Red reasons as seen at `0914d8f8` plus this suite:

| part | case | red reason |
|---|---|---|
| **1** questions to the CPU embedder, and only those; no option to the shared runner | `test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner` | "`gov retrieve … who fires the glazed bowls` sent the shared runner texts to embed: [`…Query: `, `…Query: who fires the glazed bowls`]" |
| **1** chunks to the shared runner only (build, `gov rebuild`, a search with `refresh=True`) | `test_a_rebuild_and_a_search_that_builds_vectors_send_every_chunk_to_the_shared_runner_and_none_to_the_cpu_one` | "the search sent its question to the shared runner" (the build and rebuild parts pass) |
| **2** the device: GPU, half, nothing, another model → no vector, unavailable with a reason, nothing cached, no fallback; then on the CPU → the CPU vector | `test_an_embedder_at_the_cpu_address_that_does_not_report_the_model_on_the_cpu_gives_no_query_vector[gpu, partial, nothing, other-model]` (4) | each "the CPU address reports 'gpu' (…), yet the search answered (available is True …); nearest forge.md 0.0561" |
| **3** the key names the device: round 3's entry is never served; one answer after it | `test_a_vector_cached_under_round_3_s_key_is_never_served` | "the read served the vector cached by the shared runner under round 3's key (nearest forge.md 0.0), not the CPU embedder's (the kiln)", which also shows the planted layout is round 3's |
| **4** started on demand at its address, no GPU, `serve`, never stopped; found as DEC-260 finds it | `test_a_read_starts_the_cpu_embedder_at_its_address_with_no_gpu_and_never_stops_it[GOV_OLLAMA_BIN, PATH, HOME]` (3) | "the read started no Ollama executable" |
| **4** two sessions at once: one embedder serving, both answered | `test_two_reads_at_once_leave_one_cpu_embedder_serving_and_both_get_their_answer` | the same |
| **4** the address held by a non-embedder: no other port, no fallback, exit 0, unavailable with a reason, the other routes answer | `test_an_address_held_by_something_that_is_not_an_embedder_gives_no_semantic_answer_and_no_fallback` | "the semantic facet is not unavailable with a reason (available is True, no reason (None))" |
| **4** no executable: the same | `test_with_no_executable_and_nothing_at_the_cpu_address_the_semantic_facet_is_unavailable_and_the_rest_answers` | the same |
| **5** on the shared GPU: one answer cold, warm, unwritable, after other texts, two processes; the shared runner on the GPU before and after | `test_w2_54_shared_gpu.py::test_shared_gpu_one_text_gets_one_answer_after_other_texts_at_once_and_whatever_the_cache_s_state` | run by the lead (not run here) |
| **5** the shared runner holds the model on the GPU, the CPU embedder with `size_vram` 0; one revision; prints the port and the size | `test_w2_54_shared_gpu.py::test_shared_gpu_the_shared_runner_keeps_the_model_on_the_gpu_and_the_cpu_embedder_holds_it_on_the_cpu` | run by the lead (not run here) |
| **6** the change record states the figure | `test_the_change_record_states_w1_21_s_hit_at_5_with_cpu_query_vectors_at_or_above_80` | "docs/changes/W2-54-CIT-E.md has no line naming W1-21, hit@5 and CPU query vectors" |

**Count:** 16 new cases (11 functions). The 14 stand-in cases are all red here. The 2 `shared_gpu` cases are not
run here.

**Success 6, the figure:** the case looks for a line of the change record that names `W1-21`, `hit@5`, `CPU` and
"query vector", and does not name round 3's `5f038b47`. That line must hold a figure written with its decimals (as
W1-21 prints it, `81.67`) between 80 and 100. The decimals keep "the pass line of 80" from counting as the figure. The
figure itself is W1-21's own case, unchanged: neither its case, its pass line nor its real-models environment
(`real_env`) was touched.

### What passes today, and why it is here

- In the rebuild case, the build, `gov rebuild` and the refresh already send every chunk to the shared runner and
  none elsewhere (today there is no other address). A change that embedded chunks at the CPU address would turn
  those parts red. Only the search's question is red today.
- Rounds 1 to 3 pass with the fixture change, as before it: 75 passed, with the four green-here cases and the
  `local_only` case left out (80 − 5).

## The cases on the shared GPU, and W1-21's case: how the lead runs them

Outside any sandbox, in the lead's session, on this machine: the shared Ollama at `127.0.0.1:11434` with
`qwen3-embedding:0.6b`, the real `ollama` where DEC-260 looks, `gitleaks` and `sqlite_vec`. **Neither address set:**

    env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST \
      PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
      python3 -m pytest tests/acceptance/W2-54/test_w2_54_shared_gpu.py -m shared_gpu -s -q -p no:cacheprovider -rs

- `-m shared_gpu` selects them; without it `conftest.py` deselects them (counted as deselected), so a sandboxed or CI
  run leaves them out. Selected, **they fail and do not skip** when a prerequisite is missing or the shared server does
  not hold the model wholly on the GPU (`size_vram` equal to `size`).
- `-s` shows the line the second case prints: the CPU embedder's address and port, its `size` (in bytes and GiB) and
  `size_vram`, and the shared runner's.
- The first read starts the CPU embedder at `127.0.0.1:11435` (if the engineer kept that default) and leaves it
  running (DEC-261 as amended). The lead decides whether to stop it afterwards.

W1-21's hit@5 with CPU query vectors (DEC-798 item 3), the same environment, with the dev tiers (`GOV_DEV_TIERS`, or
the default folder):

    env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST \
      PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
      python3 -m pytest "tests/acceptance/W1-21/test_w1_21_dev_tier.py::test_the_dev_query_set_meets_the_hit_at_5_pass_line" \
      -q -p no:cacheprovider -rs

The index is built through the shared runner on the GPU, and the questions are embedded by the CPU embedder (both
default addresses). The terminal summary prints `mean hit@5 of gov.retrieval.retrieve: NN.NN (pass line 80 …)`. That
figure goes into the change record on a line naming W1-21's hit@5 and CPU query vectors, which the success-6 case
then reads. A figure below 80 is a red for this ticket (DEC-798 item 3), not a rewrite.

## The real CLI, and what could not run here

- The sandboxed-worker case (`local_only`, round 3) could not reach `api.anthropic.com` from this designer's sandbox
  ("Couldn't connect through your proxy"). Its fixture change (above) is **unverified here**; the lead runs it.
- In this sandbox, an Ollama started by a real-models case tries `ollama.com:443` (denied). It is harmless, and is
  why the real-models cases here are the lead's.

## How long the new cases run

`test_w2_54_cpu_embedder.py`: **about 23 s** (14 cases; each start case waits about 1 s for the stand-in executable
to listen). The rest of W2-54 without the green-here file: 138 s. The `shared_gpu` file: not run here; expect a few
minutes (an index of six notes, about thirty reads, the first of which may load the model on the CPU).

## Risks (round 4)

- **The default port and the no-GPU rule are this suite's choice** (above). If the engineer starts the CPU embedder
  another way, for example with `OLLAMA_NUM_GPU` or a Vulkan or ROCm variable, the start cases stay red until the
  lead decides.
- **When `/api/ps` is read.** A fresh embedder (the stand-in, and Ollama) lists nothing until a request has loaded the
  model, and the device case `nothing` holds that a listing of nothing gives no vector. Code that reads `/api/ps`
  before its first embedding request, and refuses on an empty list, never answers a first question; the stand-in
  cases then show it as "facet unavailable". The KPI's words ("the embedder that computed it reports …") read as
  after the computation, and this suite holds that reading.
- **One file under `.gov-runtime/`** (W1-19's and W1-21's DEC-782 rewrites): if round 4 keeps round 3's cache file
  and adds a new one beside it, those suites see two files and turn red. The cache with the device in its key has
  to stay one file (or replace the old one).
- **W1-27's other files** name no endpoint and so use the default addresses on the machine they run on. Today they
  do the same with `OLLAMA_HOST`.
- The success-6 case reads a figure with decimals. A whole-number figure (for example exactly `85`) is not read; the
  change record then writes `85.00`.

## Round 4c: three cases rewritten (DEC-811, orchestrator, delegated, 2026-10-19)

At `fd66ed9c` the lead's run had 7 of these cases red for reasons in the cases, not the code (change record §5.6.4).
DEC-811 decides the rewrites; each carries `Rewrite-Reason: DEC-811 …` in the file. No pass line, threshold or
expectation is lowered, and the lexical route is not changed.

- **PKG-W2-54-4-1 (a)**, `test_an_embedder_at_the_cpu_address_that_does_not_report_the_model_on_the_cpu_gives_no_query_vector[4]`
  and the helper of `test_an_address_held_by_something_that_is_not_an_embedder_…` and
  `test_with_no_executable_and_nothing_at_the_cpu_address_…`. **Before:** `gov retrieve` asked `who fires the glazed
  bowls`, which no fixture note holds as a phrase, so the lexical route (an exact-phrase search) gave no evidence
  whatever the semantic facet did. **After:** it asks `fires the glazed bowls` (`PHRASE`), which the kiln note holds.
  The no-fallback check now looks for `PHRASE`; the question (`QUESTION`) ends with it, so every text sent for either
  read (the semantic search still asks `QUESTION`) is caught. Every other assertion stands: the semantic facet
  unavailable with a reason, exit code 0, no traceback, nothing cached, the lexical route available with evidence.
- **PKG-W2-54-4-2 (a)**, `test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner`.
  **Before:** steps 5 and 6 asked `QUESTION` and `OTHER` again, whose vectors steps 1 and 2 had cached, so the CPU
  embedder was rightly asked nothing (KPI success 2). **After:** step 5 searches `where are the glazed bowls fired`
  (`AGAIN_KILN`; both stand-ins target it as `QUESTION`: the kiln on the CPU embedder, the forge on the shared runner),
  step 6 retrieves `who lifts the honey frames` (`AGAIN_OTHER`). Each step still sends the CPU embedder at least one
  text and the shared runner none; the search's answer is still the kiln; every one of the four texts must have
  reached the CPU embedder.
- **Ride-along (DEC-802)**, `test_the_change_record_states_w1_21_s_hit_at_5_with_cpu_query_vectors_at_or_above_80`.
  **Before:** any figure with decimals from 80 to 100 on the line counted, so a per-class figure (the line also lists
  `failed-approaches 100.0`) met it with a headline below 80. **After:** the case reads W1-21's headline hit@5, the
  first figure with decimals after `hit@5` and before any per-class list (`per class`, `per-class`), on every line
  that qualifies, and requires each at or above 80 (the pass line stays 80). Shown once with a throwaway outside the
  tree: the record's line with its headline set to `78.33` fails the case (the old reading passed it on
  `failed-approaches 100.0`); with `81.67`, as recorded, it passes.

# Run 5 (DEC-874): "nothing of W2-02's other types" is read from W2-54's own commits

DEC-874 (orchestrator, delegated, 2026-10-20) item 1: KPI S4's "nothing of W2-02's other types" (DEC-768 item 1) is
about **W2-54's own change, not the tree**. Three cases judged the tree, so they were red on any tree that holds
W2-02's merge (W2-02's own `close` and `adoption-verdict` then exist) although W2-54 did nothing wrong. They are
corrected to that meaning; each change carries `Rewrite-Reason: DEC-874`. No other case and no other expectation of
`test_w2_54_audit_report.py` changed (the schema file byte for byte as W2-02's at `2a35fd7b`, the audit folder, the
fields, failure line 3, W1-43 untouched).

**W2-54's own change** is the commits of a history that are **no merge** (`git log --no-merges`) and whose `Task:`
trailer is `DAEO-0rfi` (read with `%(trailers:key=Task,valueonly)`), each read against its one parent. A merge of
`w2/integrate` into this branch, or this branch's merge into `w2/integrate`, carries the same trailer but is no own
change. Nothing is checked out; everything is `git log`, and `git show` of one named file.

**Two histories** (a new parameter, `history`): `HEAD`, and `4ce16df2` (`w2_54_support.W2_02_MERGED_COMMIT`), W2-02's
branch with its types merged with `w2/integrate`. All 38 of W2-54's own commits are among its ancestors. Both pass
today. The existing ids gain this parameter: `[HEAD]`, `[4ce16df2]`, `[close-HEAD]`, `[close-4ce16df2]`,
`[adoption-verdict-HEAD]`, `[adoption-verdict-4ce16df2]` (6 cases where there were 3: **24 in the file, 99 in the
suite**).

| case | before | after |
|---|---|---|
| `test_no_schema_file_of_w2_02_s_other_types_comes_with_it[history]` | `close.schema.json` and `adoption-verdict.schema.json` do not exist in this tree's two schema folders | no own commit of `history` adds or changes (`--name-status --no-renames`, deletions left out) `close.schema.json` or `adoption-verdict.schema.json` under `template/governance/kernel/schemas/` or `governance/kernel/schemas/`; the failure names the commit, its status and the path. `history` must hold at least one own commit |
| `test_w2_02_s_other_types_are_judged_as_an_unknown_type[kind-history]` | core-schema from this tree judges a `kind` record exactly as a record of an unknown type | (1) no line an own commit of `history` adds to `src/gov/check/schema.py` (`-p`, `+` lines) names `kind` as a quoted string (a type map key, a standalone type) or `kind.schema.json`; the failure names the commit and the line. (2) **The behaviour, kept:** core-schema as W2-54's own **last commit to that module** leaves it (`4f753c72` today, in both histories): its declared command, with `gov.check.schema` read from `git show <commit>:src/gov/check/schema.py` into the case's temporary folder (every other module is this worktree's), in a project whose common and audit-report schema files are that commit's. A `kind` record gets the findings an unknown type gets, no more and no fewer (the assertion as before) |

**Each case proves its reading first.** The fixture `histories_that_bring_in_w2_02_s_types` builds two temporary
repositories from scratch (`w2_54_support.own_task_repo`). In each: an own commit that adds `audit-report` (as
W2-54 does); then a commit that adds both schema files, a `"close"` type map entry and `"adoption-verdict"` among
the standalone types, carrying `Task: DAEO-0rfi` in one repository and `Task: DAEO-zflj` in the other; then a merge
carrying `Task: DAEO-0rfi` of a `DAEO-zflj` commit that adds both schema files. Each case's reading must name exactly
the first repository's offending commit and find nothing in the second (so another Task's commit and a merge never
count). Only then does it read the real history.

**Shown red (throwaway outside the tree, the cases' own bodies run against a built history as `HEAD`):** an own
commit adding `template/…/close.schema.json` fails case 1 (`… A template/governance/kernel/schemas/close.schema.json`);
an own commit adding `governance/kernel/schemas/adoption-verdict.schema.json` fails it too; an own `"close"` map entry
fails `[close-HEAD]` (`… +    "close": "close.schema.json",`); `"adoption-verdict"` added to the standalone types
fails `[adoption-verdict-HEAD]`. When only `Task: DAEO-zflj` brings all of it in (with an own merge too), every case
passes. The behavioural half tells W2-02's change apart: run as W2-02's `81eac9a7` leaves the module, a `close`
record gets `SCHEMA_UNREADABLE` and an `adoption-verdict` record only `SCHEMA_UNREADABLE`, where an unknown type gets
`SCHEMA_UNKNOWN_TYPE` (the case fails); as `4f753c72` leaves it, they are the same.

**Why the behaviour is kept, and its limit.** The added-lines reading states S4's words. The run states what they
mean: core-schema as W2-54 left it knows no `close` or `adoption-verdict` type. It runs W2-54's last module at
`4f753c72`, which has no W2-02 commit among its ancestors. **Risk:** if a later W2-54 commit changes
`src/gov/check/schema.py` after W2-02's merge has come into this branch, that module holds W2-02's types, and the
behavioural half turns red although the line reading stays green. That would be a new finding for the lead, not a
fault of the code. The line reading is the part that holds whatever is merged.

## Second batch (after the first review of `0ccafe25`; `Rewrite-Reason: DEC-874`)

**What was wrong.** The two readings of core-schema's module (`own_added_lines`, under `other_type_lines_brought_in`,
and `last_own_commit_of`) ran `git log … -- src/gov/check/schema.py <history>`: the history stood after `--`, so git
took it as a path and read the checked-out branch. `[…-4ce16df2]` therefore read `HEAD`'s history, and a revision
that does not exist gave the same answer (`4f753c72`). Read on `4ce16df2` itself, a walk limited to the module follows
only the side W2-02's merge-back `666f56d1` kept of it (W2-02's) and never reaches W2-54's `4f753c72`: all four
parametrisations of `test_w2_02_s_other_types_are_judged_as_an_unknown_type` would fail ("no commit of W2-54's own …
touches src/gov/check/schema.py"), here once W2-02 merges into `w2/integrate`, and on W2-02's branch after its re-merge.
The file case's reading (no path, history last) did read the named history.

**What changed (only the reading, in `w2_54_support._own_log`).** It runs `git log --no-merges --no-renames
--full-history <args> <history> -- <paths>`: the history always stands before `--`, so it is always a revision (one that
does not exist is git's `bad revision`, an error); `--full-history` keeps the walk limited to the module from pruning
the side a merge did not keep, so every own commit that changes the module is found whatever merges lie between. The
file case's reading goes through the same function (no path) and reads as before. Before → after, on this repository:
`last_own_commit_of` gives `4f753c72` on `HEAD`, on `4ce16df2` and on a revision that does not exist → `4f753c72` on
`HEAD` and `4ce16df2`, an error on a revision that does not exist; read on `4ce16df2` without `--full-history`, it would
give none.

**The case proves it first** (in addition to the two built histories above): a third built history
(`w2_54_support.merge_back_repo`, fixture `a_merge_that_keeps_its_own_side_of_the_module`) in the shape of W2-02's
merge-back. An own commit adds `audit-report` to the module on `main`; a `Task: DAEO-zflj` branch from the base writes
the module with `close` and `adoption-verdict`, then merges `main` keeping its own side (`-s ours`); the checked-out
branch is left at the base, with no own commit. Read at the merge, the last own commit of the module is the own commit,
its added lines are read, no line of the type is counted; read at `HEAD` (the base) there is none, so the named history
is what is read; a history that does not exist, in that repository and in this one, raises `bad revision`. Shown once
with a throwaway outside the tree: the old reading and a reading of the named revision without `--full-history` both
fail this self-check ("… misses the own commit that changed it"); the corrected one passes it.

No expectation changed: the case's two assertions (no own added line names the type; core-schema as the last own
commit to the module leaves it judges the record as an unknown type), the file case and every other case stay as they
were; the ids are the same (24 in the file, 99 in the suite).

# W2-75 (DEC-937, 2026-10-28): the green-here fixture reads the close's own check result

Ticket W2-75 (`DAEO-ebmh`, LITE, test-revision; row W2-L429; DEC-937, delegated under DEC-936; under DEC-889 item 2,
P-IS-2 (a)). Every change carries `Rewrite-Reason: W2-L429`.

**Why.** W2-58's full close (2026-10-28) ran 15,672 regression cases with 0 failed and 3 errors: the three cases of
`test_w2_54_green_here.py` that use `gov_check_here` "failed on setup with Timeout (>900.0s) from pytest-timeout". The
fixture ran `gov check` on this repository, about six minutes alone and over the close's 900 s per-test limit under a
full close's parallel load (row W2-L429 saw the same at 600 s on 2026-10-24).

**The two routes** (`w2_54_support.green_here_check`; the fixture stays session-scoped, so one route serves the three
cases):

1. **Inside a close** (`GOV_CLOSE_CHECK_RESULT` set and not empty): the pinned `gov close --check-result <file>` copies
   the queue's gate (b) output, `gov check --json` run on the same commit in the same tree after the full rebuild,
   byte for byte under its JUnit folder and names that copy in the variable in every test run's environment. The
   fixture reads that envelope (`w2_54_support.read_check_result`) and starts **no** `gov check`. The queue stops before
   the close if gate (b) is not green, so this `gov check` has already been judged once.
2. **Outside a close** (the variable unset or empty: a lead's run, a plain run, the nightly): one `gov check --json` in
   this worktree with its `src/` on `PYTHONPATH` and the same 1800 s timeout, exactly as before.

**A bad result fails the cases, naming the file** (the route chosen, on the lead's recommendation under DEC-937's
delegated ground). A result that is missing, unreadable, not JSON, not gov check's envelope (a JSON object with `ok`
and `command: "check"`), or that lists no checks (a passing run's `result.checks`, a failing run's
`error.details.checks`, a non-empty list of objects) is an `AssertionError` naming the file and what is wrong: the
session fixture fails, and each of the three cases errors on setup with that message. It is never read as green, and
the fixture does not fall back to running `gov check` itself. Why not the fallback: the close already refuses an
unreadable `--check-result` before any test runs (`CHECK_RESULT_UNREADABLE`), so a bad file inside a close is a real
fault to surface; a fallback would hide it behind the same six-minute `gov check` under load, and time out as before.

**What each case still asserts (nothing less).** `test_gov_check_gives_context_reproducibility_green_here`:
context-reproducibility listed, GREEN, severity hard-block. `test_gov_check_gives_core_schema_green_here`: core-schema
listed, GREEN, severity hard-block. A check that is RED or missing fails its case naming the check and its status,
whichever route gave the envelope. `test_the_w1_43_audit_report_is_untouched`: the W1-43 report's sha256 and its bytes
as at `b644d28a`, read after `gov check` has run in this tree. In a close that `gov check` is gate (b)'s: the queue
runs it in the same tree on the commit being closed, after the rebuild and before the close starts any test run, and
the fixture still stands between it and the case, so the report is read after it as it is read after the fixture's
own run outside a close. `test_the_suite_runs_this_worktree_s_code` is unchanged.

**The route cases (new, deterministic, no network, no real `gov check`):**

| KPI line (W2-75) | case |
|---|---|
| 1. in a close, the fixture reads the check result and runs no `gov check` | `test_in_a_close_the_fixture_reads_the_check_result_and_starts_no_gov_check`: a planted envelope (passing and failing forms) with every process start refused (`subprocess.Popen`, `os.system`); the checks come back by id and the result names its file |
| 2. outside a close, `gov check --json` in this tree as now, same timeout | `test_outside_a_close_the_fixture_runs_gov_check_in_this_worktree`: the variable unset and empty; a spy in place of `w2_54_support.run` sees one `gov check --json` with `_GOV`, cwd this worktree, `PYTHONPATH` its `src/`, timeout 1800 s |
| 3. a missing or broken result is never green | `test_a_check_result_that_is_missing_or_broken_is_never_read_as_green`: missing, a folder, empty, not JSON, a JSON list, another command's envelope, no `ok`, no checks, checks not a list, an empty list, a check that is no object: each fails naming the file, and no process is started |
| 4. each case keeps its meaning | `test_a_red_or_missing_check_in_the_close_s_result_still_fails_the_cases`: from a planted result, each check case fails on its check RED (naming it and `RED`), missing (`lists no …`), or advisory; the three cases above, unchanged in what they assert |
| 5. no other expectation lowered | nothing else in W2-54 changes; the full run in the close's form is the lead's |

**Shown red first.** A throwaway spy on `subprocess.Popen` (outside the tree) ran the green-here file with
`GOV_CLOSE_CHECK_RESULT` naming a planted green envelope. At `3eef001d` (the old fixture) the fixture started one
`gov check --json` (the three cases erred on the spy's refusal: 1 passed, 3 errors); with this revision it started
none (8 passed in 0.05 s). The four route cases fail on the old support module, which has no `green_here_check`.

**Counts.** `test_w2_54_green_here.py`: 8 cases where there were 4; the suite: 103 where there were 99.
