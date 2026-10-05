# W1-20 — gov closure: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-jozo` (W1-20), Contract v4
CAP-57 (covers CAP-57.a, shared with W1-22) and CAP-09, DEC-033, DEC-034, DEC-035 (ratified by DEC-083 "as realised
by DEC-080"; DEC-035's numbers stay placeholders), DEC-080, DEC-221 (profile STANDARD), DEC-317, DEC-322 and DEC-344.
Written before implementation.

The suite has **36 test functions, 49 cases** in five files, a support module and a conftest.

## Run

```sh
python3 -m pytest tests/acceptance/W1-20 -q -p no:cacheprovider
```

Standard library and `pytest` only. Nothing is installed. No network: one loopback port is opened to show that
nothing connects to it.

- **Every store and every code index is built in a temporary git repository** (DEC-322). No test reads or writes
  this repository's `.gov-runtime/`, and no test indexes this repository or a worktree of it.
- **The code under test** is this worktree's `src/`, on the `PYTHONPATH` of a child process whose environment is
  built from scratch (`PATH`, an empty temporary `HOME`, `TMPDIR`, `XDG_RUNTIME_DIR`, locale). `GOV_ROLE` and
  `GOV_TICKET` are not passed on. The child's working directory is never the repository under test.
- **39 cases run with `git` alone on `PATH`**: the code tool is not there, so they run on any machine and in a
  worker's sandbox.
- **10 cases (`test_w1_20_code.py`, marked `local_only`) run the real `codebase-memory-mcp`** through
  `gov.codeintel.index` on a temporary repository of four functions. They are skipped without the
  `codebase-memory-mcp` and `gitleaks` binaries, and cannot run inside a worker's sandbox (the daemon's socket is
  refused, `/tmp/gov-cbm-<uid>` is read-only there). The lead runs them outside it.
- **The wrapper's daemon directories** of this suite's temporary repositories (`/tmp/gov-cbm-<uid>/<id>`, DEC-338)
  are removed at the end of the session, each only when it holds nothing but the tool's own folder of plain files.
  The folder above them is left alone.
- No dev tier is used: no KPI line of this ticket names one.

## The public interface the tests assume

Settled by the sources: `gov closure` is a reserved read command (CAP-57's acceptance line, CAP-27, the command
list of `src/gov/cli/main.py`), built by `src/gov/closure/command.py` alone (DEC-317), and the depth is an input
("over the same commit and depth"). The rest is package DP-1.

```
gov closure [--json] [--root <path>] (--depth <N> | --radius <R>) <id>...
gov.closure.closure(root, ids, depth=N)  ->  the same map as the envelope's `result`
```

The tests read these keys of the result, and no other:

| Key | What the tests hold it to |
|---|---|
| `stopping_reason` | One of the fixed list (DEC-034, ADR-0002 §4): `CLOSURE_COMPLETE`, `SATURATED`, `DEPTH_LIMIT_REACHED`, `BUDGET_EXHAUSTED_WITH_GAPS`, `FACET_UNAVAILABLE`. |
| `depth` | The depth the closure ran at, in hops from a start id. |
| `closure` | A list of maps, each with `id` and `kind` (`record` or `symbol`). A symbol's `id` is its name. It holds every id at most `depth` hops from a start id. |
| `gaps` | A list of maps, each with `id` and `reason`: `DEPTH_LIMIT_REACHED` (named by an entry at the depth, not followed), `UNRESOLVED` (no record and no symbol has it), `FACET_UNAVAILABLE` (the facet that could say was not available). |
| `facets.code` | `unavailable` when the code facet was asked and could not answer; `available` when it answered. |
| `uncommitted` | The repository paths whose working tree differs from `HEAD` (DP-7). |

"Byte-identical" is tested on the raw standard output of the command, with `--json` (the API-0002 envelope) and
without it.

## KPI lines, tests and red reasons

Red run on `w1/W1-20` at `35993016`: **49 errors** inside the worker sandbox. 48 cases error in the `built` fixture
with the same reason: **`gov closure is not built: there is no src/gov/closure/command.py (the command answers
NOT_IMPLEMENTED, exit code 1)`**. The 49th, the premise test of the code fixture, does not need `gov closure`; it
errors in the sandbox because the wrapper cannot make its daemon directory there (`Read-only file system:
/tmp/gov-cbm-1000/…`). Outside the sandbox it is expected to pass before implementation; that run is the lead's.

| KPI line | Tests | Red reason once the command exists |
|---|---|---|
| **Success 1.** Resolves referenced ids through the record graph and codebase-memory callers/callees to a radius-scaled depth, with no model **[CAP-57.a]** | Record graph (`test_w1_20_records.py`): `test_a_chain_is_followed_to_the_depth_and_no_further[5]` · `test_every_one_of_the_eight_typed_edges_is_followed` (CAP-09.a's edges) · `test_a_cycle_ends_and_is_complete` · `test_several_start_ids_give_the_closure_of_all_of_them` · `test_the_result_names_the_depth_it_ran_at` · `test_a_record_that_names_the_start_record_is_in_its_closure` (DP-2). Radius: `test_the_depth_scales_with_the_impact_radius[4]` (DP-3). Code (`test_w1_20_code.py`, `local_only`): `test_the_wrapper_gives_the_callers_the_source_states` (premise) · `test_a_symbol_is_resolved_and_its_callers_are_followed_to_the_depth` · `test_the_callees_of_a_symbol_are_followed` (DP-6) · `test_records_and_symbols_are_resolved_in_one_closure` (DP-6) · `test_a_repository_without_a_code_index_states_the_facet_unavailable`. Code facet (`test_w1_20_facets_and_no_model.py`): `test_an_unavailable_code_facet_is_stated_and_ends_nothing[2]` · `test_a_closure_of_records_alone_does_not_run_the_code_tool` (DP-4). No model: `test_a_closure_starts_no_ollama_and_asks_no_model` · `test_a_closure_over_code_starts_no_ollama_and_asks_no_model` (`local_only`). Read only (CAP-27, DEC-322): `test_a_closure_changes_nothing_in_the_repository` · `test_a_closure_does_not_build_the_store`. DEC-344: `test_an_uncommitted_edit_of_a_record_is_not_in_the_closure` · `test_the_result_names_the_files_that_differ_from_head` (DP-7) · `test_an_uncommitted_function_in_the_index_is_in_the_closure` · `test_the_result_names_the_code_file_that_differs_from_head` (DP-7; both `local_only`) | No closure: no id resolved, no depth |
| **Success 2.** Byte-identical output on repeated runs; DEPTH_LIMIT_REACHED lists the gaps **[CAP-57.a]** | `test_w1_20_determinism.py`: `test_repeated_runs_print_the_same_bytes[6]` · `test_the_compared_output_is_a_closure_and_not_an_empty_answer` (premise of the comparison). `test_w1_20_gaps.py`: `test_every_id_beyond_the_depth_is_a_gap` · `test_a_gap_beyond_the_depth_says_so` (DP-5) · `test_an_id_already_in_the_closure_is_no_gap`; and the depth cases of the chain test above | No output to compare; no gap list |
| **Failure 1.** Output differs between runs on the same commit | `test_repeated_runs_print_the_same_bytes[6]` (four runs each: other hash seed, time zone, working directory) · `test_two_clones_of_one_commit_print_the_same_bytes` · `test_the_order_of_the_start_ids_does_not_change_the_closure` · `test_the_python_interface_returns_what_the_command_prints` (DP-1) · `test_repeated_runs_and_a_rebuilt_index_print_the_same_bytes` (`local_only`) | No output |
| **Failure 2.** An unresolved id is omitted from the gap list | `test_w1_20_gaps.py`: `test_an_edge_to_no_record_is_in_the_gap_list` · `test_a_start_id_that_names_nothing_is_in_the_gap_list` · `test_only_unresolved_start_ids_give_an_answer_with_gaps` · `test_an_unresolved_id_is_told_from_one_beyond_the_depth` (DP-5). `test_w1_20_code.py`: `test_an_id_that_is_no_record_and_no_symbol_is_an_unresolved_gap` (`local_only`). The unavailable-facet tests above also hold the id in the gap list | No gap list |

Covers id: **CAP-57.a** (the closure half; the synthesis citation check is W1-22's) is tested by every file. CAP-09
is a source of the ticket; its covers items CAP-09.a and CAP-09.b name W1-10 alone as provider, and the closure's
use of them is tested by the typed-edge test and the dangling-edge tests.

**Checked that the suite can go green and catches the failure lines.** The 39 cases that need no code tool were run
against a throwaway stand-in outside the worktree (single files of `src/gov/` copied to the session's scratch
space; the stand-in is not in the repository): 39 passed. With the output left in set order, 9 cases failed (the six byte comparisons,
the two-clones, start-order and Python-interface tests). With unresolved ids dropped from the gap list, 4 failed
(`test_an_edge_to_no_record_is_in_the_gap_list`, `test_an_unresolved_id_is_told_from_one_beyond_the_depth` among
them). With edges followed outwards only, exactly one failed: the DP-2 test. **The 10 `local_only` cases were
never run against anything**: their expected answers come from the fixture's source, and the premise test is
there to show whether the tool agrees.

## Readings

1. **Depth** is counted in hops from a start id. Depth 0 is the start ids themselves. A closure holds every id at
   most N hops away; an id named by an entry exactly N hops away and not already in the closure is a gap with the
   reason `DEPTH_LIMIT_REACHED`, and is not looked up.
2. **CLOSURE_COMPLETE** means no gap at all (DEC-034: "no unresolved referenced IDs within depth limit").
   `DEPTH_LIMIT_REACHED` is asserted only where the depth cut is the only kind of gap. Which reason stands when
   unresolved ids are the only gaps is open (DP-5): those tests assert "not `CLOSURE_COMPLETE`" and nothing more.
3. **The fixture's components do not name each other**, and every test but one starts from a record no other
   record names. Those tests hold whether or not edges are also followed backwards (DP-2).
4. **The same ids in another order** give the same closure, gaps and stopping reason. The whole output is not
   compared across orders.
5. **Two clones of one commit**, each with its own store, print the same bytes, and no absolute path of the
   repository is in the output.
6. **No model**: an `ollama` program stands first on `PATH` and in `GOV_OLLAMA_BIN`, and `OLLAMA_HOST` names a
   listening loopback port (the three places `gov.retrieval.ollama` looks, DEC-260). The program is never run and
   the port never connected to. The reranker's own process (ADR-0002 §3) is not watched.
7. **A read command**: after closures, `git status --porcelain` is empty, `store.db` has the same bytes and `HEAD`
   has not moved. A closure in a repository without a store builds none.
8. **A repository without a store**: an envelope either way, the error `STORE_MISSING` (exit code 1) or a result
   that is not `CLOSURE_COMPLETE`; never a traceback. Which of the two is the engineer's.
9. **Symbols** are plain functions with names of their own in one Python file. Two symbols of one name, methods,
   other languages and a name that is both a record id and a symbol are not tested.

Not tested: a depth that is negative or no number; neither `--depth` nor `--radius` given, or both; the store built
at another commit than `HEAD` (DP-7); commit trailers as edges (DP-2); `SATURATED` and
`BUDGET_EXHAUSTED_WITH_GAPS`, which belong to `gov retrieve`; a store that holds invalid records; timing.

## Decision packages

Seven points the sources do not settle. The tests are written along the recommended option of each; the table says
which tests change with another answer.

| Package | Tests that depend on it |
|---|---|
| DP-1 interface and output | every test, through the command line form and the keys above; `test_the_python_interface_returns_what_the_command_prints` alone for the Python function |
| DP-2 ids, start, direction | `test_a_record_that_names_the_start_record_is_in_its_closure` (direction); the tests that give a symbol or an unknown id on the command line (untyped start ids) |
| DP-3 radius to depth | `test_the_depth_scales_with_the_impact_radius[4]` |
| DP-4 the code facet | `test_a_closure_of_records_alone_does_not_run_the_code_tool`; `test_an_unavailable_code_facet_is_stated_and_ends_nothing[2]`; `test_a_repository_without_a_code_index_states_the_facet_unavailable`; every `CLOSURE_COMPLETE` assertion of a test that runs without the tool |
| DP-5 gap reasons | `test_a_gap_beyond_the_depth_says_so`; `test_an_unresolved_id_is_told_from_one_beyond_the_depth`; the reason lines of `test_an_edge_to_no_record_is_in_the_gap_list`, of the unavailable-facet tests and of `test_w1_20_code.py`; option (a) also changes the fixed list in `w1_20_support.REASONS` |
| DP-6 callees | `test_the_callees_of_a_symbol_are_followed`; `test_records_and_symbols_are_resolved_in_one_closure` |
| DP-7 what a caller sees | `test_the_result_names_the_files_that_differ_from_head`; `test_the_result_names_the_code_file_that_differs_from_head` |

### DP-1 — The public interface and the form of the output

- **Question.** What are the arguments of `gov closure`, is there a Python function, and what does the result hold?
- **Why now.** The contract names the command and "the same commit and depth" and nothing else. "Byte-identical"
  needs a stated output, and W1-21 (`gov retrieve`) and W1-35 call the closure.
- **Options.** (a) Both: `gov closure (--depth N | --radius R) <id>...` and `gov.closure.closure(root, ids,
  depth=N)`, which returns the command's `result`; the result holds `start`, `depth`, `stopping_reason`, `closure`
  (`id`, `kind`), `gaps` (`id`, `reason`, and `referenced_by` untested), `facets`, `uncommitted`. (b) The command
  alone; W1-21 calls it as a process or imports the command module. (c) The Python function alone, the command
  being a later ticket's.
- **Impact.** (a) one function and a thin command, inside `src/gov/closure/**`; W1-21 imports it. (b) saves a few
  lines and costs W1-21 a process per closure. (c) contradicts CAP-57's acceptance line.
- **Reversibility.** High before W1-21 is written; after it, a renamed key costs W1-21 and W1-35 an edit.
- **Cost.** (a) about 10 lines over (b).
- **Recommendation.** (a). **Confidence:** medium-high for the command and the keys the tests read, medium for
  the function's name and signature.

### DP-2 — What "referenced ids" are, where a closure starts, and which way edges run

- **Question.** Which ids does a closure start from, which ids does it follow, and does it follow an edge from its
  target back to its source?
- **Why now.** DEC-033 says "referenced IDs (spec, ADR, task, symbol) through the frontmatter graph" and no source
  gives an id grammar, a place to read ids from, or a direction.
- **Options.** (a) The start ids are the ids given on the command line, untyped: an id that is a record's id is a
  record, any other id is asked of the code index as a symbol name. Followed are the eight typed edges of the
  store, both ways (what a record names, and what names it), and for a symbol its callers and callees. No text is
  scanned for ids, commit trailers are not edges of the closure, and no edge joins a record to a symbol. (b) As
  (a), outwards only: what a record names. (c) Typed start ids (`--record`, `--symbol`). (d) The start is a ticket
  or a file whose text is scanned for ids by a grammar.
- **Impact.** (a) gives CAP-09's acceptance ("every IMPLEMENTS and VALIDATES edge of a requirement": those edges
  point at the requirement) and CAP-29's lineage reading of the command; a hub record pulls much of the graph in,
  bounded by the depth. (b) is a dependency closure in the strict sense and cannot answer "what implements this
  requirement". (c) removes the one ambiguity of (a), an id that is both. (d) needs a grammar no source gives; this
  repository's ids (`DEC-…`, `CAP-…`, `W1-…`, `DAEO-…`) mostly name no record today (W1-10 residuals).
- **Reversibility.** High: one test for the direction. (d) can be added on top later.
- **Cost.** (a) and (b) the same; (c) a few lines; (d) is a ticket of its own.
- **Recommendation.** (a). **Confidence:** medium (direction), medium-high (untyped ids from the command line, no
  text scan).

### DP-3 — "Radius-scaled depth" in numbers

- **Question.** Which depth belongs to which impact radius?
- **Why now.** The KPI says "radius-scaled depth"; DEC-035's table gives "max follow-up rounds" of 1, ~3 and ~8 and
  calls them placeholders; DEC-083 ratifies it with the numbers still placeholders.
- **Options.** (a) `--depth N` is the plain input, and `--radius R` gives R0–R1 → 1, R2 → 3, R3 and above → 8, as
  constants in `src/gov/closure/`. (b) The same numbers read from a project file. (c) `--depth` alone; the caller
  (W1-21, the impact skill of W1-35) scales it.
- **Impact.** (a) reads "follow-up rounds" as hops, which no source states. (b) adds a file to
  `governance/project/` and to `gov.config`, outside this ticket's paths. (c) leaves the KPI's "radius-scaled"
  without a test in this ticket.
- **Reversibility.** High: three constants and one test of four cases.
- **Cost.** (a) about 5 lines.
- **Recommendation.** (a), the numbers marked as placeholders to tune from telemetry. **Confidence:** medium.

### DP-4 — The code facet: when it is asked, and what happens when it cannot answer

- **Question.** When does a closure run the code tool, what does it do when the tool is missing, fails or has no
  index, and does a closure ever build the store or the index?
- **Why now.** `gov.codeintel` raises `RuntimeError` (a refused root, a failed tool, no index) and `OSError` (no
  binary, no daemon directory); the brief asks for a stated facet, never an exception or a silent omission. Each
  wrapper call starts two processes. `gov closure` is a read command (CAP-27) and only orchestrator sessions build
  the live store (DEC-322).
- **Options.** (a) Lazy: the code facet is asked only about a start id that is no record and about the symbols
  reached from a symbol. A record's edge to an id of no record is `UNRESOLVED` without asking (CAP-09.b: a
  dangling reference). When the facet cannot answer, `facets.code` is `unavailable`, each id it was asked about is
  a gap with the reason `FACET_UNAVAILABLE`, the stopping reason is `FACET_UNAVAILABLE` (DEC-034: "NOT_FOUND ≠
  absent"), and the record side is returned as usual. A closure never calls `gov.store.load` or
  `gov.codeintel.index`. (b) Eager: the facet is probed at every closure and its state always stated; a closure of
  records alone on a machine without the tool ends `FACET_UNAVAILABLE`. (c) A missing code facet is an error of the
  command.
- **Impact.** (a) a closure of records is the same with and without the tool and costs no tool process; 39 cases
  of this suite run without the tool because of it. (b) is simpler to state and makes most closures in a fresh
  project `FACET_UNAVAILABLE`. (c) loses the record side with the code side.
- **Reversibility.** Medium: (b) changes the `CLOSURE_COMPLETE` assertions of every test that runs without the
  tool, which then need the real tool.
- **Cost.** (a) a few lines over (b).
- **Recommendation.** (a). **Confidence:** medium-high.
- **Note.** Asking the wrapper about a repository that was never indexed creates the tool's home under
  `.gov-runtime/codeintel/home` (W1-16 residual). That is inside the ignored `.gov-runtime/`, so
  `git status --porcelain` stays empty; the test holds a closure only to building no index (`codeintel/files`).

### DP-5 — The reasons of a gap, and the stopping reason when unresolved ids are the only gaps

- **Question.** How does a gap say why it is one, and which stopping reason stands for a closure that reached
  everything within the depth but found ids that name nothing?
- **Why now.** The second failure line needs unresolved ids in the gap list, and a caller must tell "not followed"
  from "does not exist". DEC-034 defines `CLOSURE_COMPLETE` as "no unresolved referenced IDs within depth limit",
  and none of the other four reasons describes this case. In this repository nearly every closure meets it: every
  `DEC-…` reference and every ticket's `depends_on` is dangling today (W1-10 residuals).
- **Options.** For the gap: each gap carries `reason`, one of `DEPTH_LIMIT_REACHED`, `UNRESOLVED`,
  `FACET_UNAVAILABLE`. For the stopping reason: (a) a sixth value, `UNRESOLVED_IDS`, added to the fixed list by a
  specification change (ADR-0002 §4, DEC-034). (b) `FACET_UNAVAILABLE`, read as "not found is not proof of
  absence". (c) `CLOSURE_COMPLETE` with a non-empty gap list, against DEC-034's wording. (d)
  `BUDGET_EXHAUSTED_WITH_GAPS`.
- **Impact.** (a) is the only honest name and touches the closed specification and W1-21's bundle format. (b) and
  (d) stay inside the list and tell the caller something untrue. (c) makes "complete" mean "nothing more to
  follow". Precedence when several kinds of gap meet is also to be said: the tests assume `FACET_UNAVAILABLE`
  where the facet failed and assert `DEPTH_LIMIT_REACHED` only where the depth is the only cause.
- **Reversibility.** High for the tests: they assert "not `CLOSURE_COMPLETE`" here. Option (a) adds one value to
  `REASONS` in the support module, a one-line rewrite by a test designer.
- **Cost.** (a) a CIT on ADR-0002 §4 and one line in W1-21's reading of the list; the others nothing.
- **Recommendation.** The three gap reasons as written, and (a) for the stopping reason. Until it is decided the
  engineer may use any of the five but `CLOSURE_COMPLETE`. **Confidence:** medium-high for the gap reasons,
  medium-low for (a).

### DP-6 — Callees: `gov.codeintel` has no such function

- **Question.** How does the closure get the callees of a symbol?
- **Why now.** The KPI says "callers/callees". `gov.codeintel` offers `definitions`, `references`, `callers`,
  `impact` and `dead_code`; nothing lists what a symbol calls or every symbol, and `src/gov/codeintel/` is outside
  this ticket's `allowed_paths`.
- **Options.** (a) Add `callees(root, name)` to `gov.codeintel`, in its own commit, with `src/gov/codeintel/**`
  added to the ticket's paths for that commit (as DEC-260 did for W1-18) and one builder test. (b) The closure
  reads the wrapper's private `_graph`. (c) Callers only in W1-20; callees become a residual and the KPI line is
  not met.
- **Impact.** (a) about 5 lines in the wrapper beside `callers`, and W1-16's suite is re-run. (b) ties the closure
  to a private name. (c) leaves half of the code side out.
- **Reversibility.** High.
- **Cost.** (a) one small commit outside the ticket's paths, by decision.
- **Recommendation.** (a). **Confidence:** high.

### DP-7 — The index reads the working tree, the record graph reads `HEAD` (DEC-344): what a caller sees

- **Question.** What does the output say when the two sides can describe different states of one file?
- **Why now.** DEC-344 and the W1-17 residual leave it to W1-20.
- **Options.** (a) The closure reports what the store and the index hold and says nothing more; freshness is the
  matter of `gov doctor` and the index-freshness check (W1-26, W1-27). (b) As (a), and the result carries
  `uncommitted`: the paths `git status --porcelain` names, sorted. An empty list says the two sides describe the
  same files. (c) As (b), and the closure also checks that `HEAD` is among the store's commits and states the
  record facet stale when it is not.
- **Impact.** (b) one git call; the output still depends only on the commit and the working tree. (c) catches a
  store built at an older commit, which otherwise gives another closure "over the same commit"; it does not catch
  a store built at a newer one, because the store keeps no "built at" value and `src/gov/store/` is outside this
  ticket's paths.
- **Reversibility.** High: one key, two tests.
- **Cost.** (b) about 5 lines; (c) about 10 more and a decision on a fourth facet state.
- **Recommendation.** (b) now; (c) to W1-27, which wires `gov rebuild` and owns freshness. No test of this suite
  covers (c). **Confidence:** medium.

## Notes for the lead

- **`S0a-G-03`** is among the ticket's sources and its text is not in the tree. No test of this suite was derived
  from it, and none needs it as far as the other sources say. Whether it asks for something these tests do not
  hold cannot be said from the tree.
- **The two W1-17 residual lines that name W1-20** (`search` can raise; "every occurrence" holds for whole tokens
  only) concern the lexical index. A closure as the KPIs describe it does not call `gov.retrieval.lexical`, so this
  suite tests neither; they go on to W1-21 or W1-41.
- **The W1-16 residual "the graph is cached per process"** does not reach these tests: every call is a new process.
