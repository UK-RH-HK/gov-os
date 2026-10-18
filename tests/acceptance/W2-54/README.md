# W2-54 acceptance tests (DAEO-0rfi, FULL; DEC-768)

Written before the implementation by the independent test designer (MR-3), from the ticket's KPI lines and its
sources (DEC-768, DEC-626, DEC-441, DEC-565, CAP-33) and the decisions that apply (DEC-595, DEC-600, DEC-285,
DEC-628, DEC-221, DEC-462, DEC-136, DEC-491, DEC-732). **50 cases in four files** in round 1; round 2 (the
query vector, below) adds **15 cases in a fifth file**, `test_w2_54_query_vector.py`: **65 cases in five files.**
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
