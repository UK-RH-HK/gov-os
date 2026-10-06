# W1-19 acceptance tests — semantic retrieval, RRF and rerank

Ticket `DAEO-t6hf` (`W1-19`), profile STANDARD (DEC-221). Written by the Independent Test Designer before
implementation (MR-3, DEC-069), from the ticket's five KPI lines, Contract v4 (CAP-10, CAP-18) and the decisions
named below. Three batches: the first returned seven decision packages; the second, after they were decided
(DEC-373, DEC-374, DEC-379 to DEC-384), revised the suite to the answers; the third, after the installs (DEC-397)
and the suite's first run with them, put right the scratch environment and added the cases for how the default
reranker starts; the fourth, after implementation, revised the hit@5 case to the owner's restated KPI line
(DEC-414).

**41 test functions, 41 cases** in six files, with a support module and a conftest (33 after the first batch, 39
after the second, 42 after the third). Run:

```
python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider
```

Run `test_w1_19_real_models.py` alone, never beside another suite: it is heavy and one of its cases is a latency
case (DEC-372).

## The fourth batch: the hit@5 pass line is 80 on the dev tiers (DEC-414)

A **rewrite after implementation**; its reason is the owner's decision DEC-414, which restates the ticket's second
success line: "Dev query set mean hit@5 >= 80 on the dev tiers is the pass line; 85 (the S0b2 R1 baseline) is
re-measured at the Wave 1 exit run (W1-42) and at qualification (DEC-414); warm p95 <= 0.5 s". The failure line
"Mean hit@5 falls below 80" is unchanged. The method (DEC-380, DEC-388), the query set and every other case are as
they were.

| Case | What happened | Reason |
|---|---|---|
| `test_the_dev_query_set_reaches_the_baseline_mean_hit_at_5` | Rewritten and renamed `test_the_dev_query_set_mean_hit_at_5_is_at_or_above_the_pass_line_of_80`: it fails below 80, no longer below 85 | DEC-414. The old name would say that 85 is reached. |
| `test_mean_hit_at_5_is_not_below_the_failure_line` | Removed | Since DEC-414 it asserted the same thing as the case above, on the same measurement: "at or above 80" is "not below 80". Two cases that cannot differ would count one observation twice. |

**One case now holds both hit@5 lines.** Success 2 (at or above 80 passes) and failure 1 (below 80 fails) are the
two sides of one comparison of one measured mean, so the case passes exactly when the success line holds and fails
exactly when the failure line holds. Each KPI line still has its test; it is the same test.

**The measured figure is shown whether the case passes or fails**, and 85 is reported, never asserted. Nothing
fails, is expected to fail or skips under 85. Three places, the first needs no option:

1. **The terminal summary.** A section `W1-19 measured mean hit@5 (DEC-414)` at the end of the run, written by the
   conftest. Five lines, each beginning `W1-19 hit@5:`: the mean of the ten classes (two decimals); at or above, or
   below, the pass line of 80; at or above, or below, the S0b2 R1 baseline of 85, with the signed difference; the
   percentage of each class; the queries missed, by id. `grep "W1-19 hit@5:"` over a saved run returns them.
2. **The case's own output**: the same five lines, printed, shown with `-rP` or `-s`.
3. **Recorded properties**, in a `--junitxml` report: `w1_19_mean_hit_at_5`, `w1_19_hit_at_5_pass_line`,
   `w1_19_hit_at_5_baseline`, `w1_19_hit_at_5_against_baseline`, `w1_19_hit_at_5_per_class`, `w1_19_hit_at_5_missed`.

When the case fails, its message carries the same figures. In the support module `HIT_AT_5_PASS_LINE` is 80 and
`HIT_AT_5_BASELINE` is 85, the second named as a reported figure and not a pass line.

**What was run.** The designer's sandbox reaches neither Ollama nor the reranker, so **the revised case was not run
by the designer**; the ticket lead runs it. The collection was run (41 cases). The case's function was called apart,
in a throwaway folder outside the repository, with made-up measurements and no model: it passes at 100, 82 and
exactly 80, fails at 78, and shows the five lines and the properties each time. The lead's last run before this
batch measured 83.3, which the old case refused and this one accepts; that figure is the lead's, not the designer's.

## The state after the third batch

*As written at the third batch, when the suite had 42 cases and the real-model file seven.*

The model-free part of the ticket is built; `rerank.default_reranker()` still returns `None`. Observed by the
designer on `w1/W1-19` at `1805a2a7` plus this batch, in a sandboxed session:

```
python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider -rs --deselect tests/acceptance/W1-19/test_w1_19_real_models.py
35 passed, 7 deselected
```

- **The 35 cases outside `test_w1_19_real_models.py` pass**, none skipped: this machine has `gitleaks`,
  `sqlite_vec` and the reranker environment.
- **Two of the 35 pass before what they hold is written.** The two new cases for an absent default
  (`test_with_no_reranker_environment_…`, `test_with_the_environment_and_no_snapshot_…`) are met by a default that
  is always absent. They are guards for the engineer's `default_reranker()`, not evidence of it. The premise of the
  second was checked apart, with a throwaway script outside the repository (see "How the tests decide").
- **`test_w1_19_real_models.py` (7 cases) was not run as a file.** One of its cases, the new
  `test_the_default_reranker_is_a_process_of_its_own_…`, was run alone and is red for the reason it should be: no
  candidate is scored, because there is no default yet. It loads no model while that is so. The other six were not
  run by the designer: they start `ollama serve` and load the models, which a sandboxed session is told not to
  reach. The ticket lead ran them once before this batch: the embedder case passed; the five dev-tier cases wait for
  the default reranker.

### What the first run with the installs showed, and what was put right

With `sqlite_vec` installed the `needs` marker stopped skipping the ten stand-in cases, and nine failed with
`sqlite_vec cannot be loaded`. The designer checked the lead's reading and it holds:

- DEC-397 installed the package with `pip install --user`, into the user site folder under the home folder.
- The marker asks the Python that runs pytest, which has the real `HOME` and finds the package.
- The process under test ran in the scratch environment, whose `HOME` is an empty folder. Python derives the user
  site folder from `HOME`, so that process had none: `find_spec("sqlite_vec")` is `None` there.

So the marker and the process under test disagreed about the same machine. **The fault was in the suite, not in
the implementation.** The scratch environment now carries a folder that holds one link, to the one package the
marker found, and that folder follows `src` on `PYTHONPATH`. The `HOME` stays empty. `env_without_sqlite_vec` still
puts its blocking module first and does not carry the link. All ten cases pass now.

**The tenth case had passed for the wrong reason.** `test_the_vectors_are_in_the_shared_store_beside_the_lexical_index`
never asked whether vectors were built: the store file, a fresh lexical index and a clean tree are all there when
only the lexical index was built. It now holds its premise (the build reports `available`), and that the vectors are
in the store: a second clone given only the store's files answers a question from them without writing. That is a
**rewrite after implementation**, since the case had passed once; the reason is that it held nothing about vectors.
The nine others were revised by nothing but the environment, and had never passed.

## Red before implementation (the first two batches)

Observed on `w1/W1-19` at `1a6f9a45` plus this suite: **1 passed, 16 skipped, 22 errors**.

- **22 errors.** Every model-free case stops in the `api` fixture with one line:
  `the semantic route, the fusion or the rerank does not exist: ModuleNotFoundError: No module named 'gov.retrieval.semantic'`
- **16 skipped.** The cases that need what this machine's Python lacks skip before they reach the ticket. All 16
  name `sqlite_vec` as the reason today (it cannot be imported by `/usr/bin/python3`). A skip is decided by the
  machine alone, never by what the implementation reports.
- **1 passed.** A premise, not a test of the ticket:
  `test_the_secret_filter_lets_the_fixture_corpus_through_and_nothing_else` asks W1-15's `gov.secrets.indexable`
  about the fixture and expects the eight corpus files through, and the product-data file and the file with the
  planted secret out.

In the first batch the 19 model-free cases of that time were run against a throwaway reference outside the
repository (20 passed, 13 skipped). The second batch built no reference and no stand-in of the ticket's modules: its
three new model-free cases and the one it tightened were reasoned from the decisions, and have never run green. The
16 cases that need `sqlite_vec` or a model have never run at all. No model was loaded and Ollama was not started in
either batch (DEC-384).

## The interface (DEC-379)

A Python interface, as `gov.retrieval.lexical` is (DEC-340): no KPI names a `gov` command, `src/gov/cli/**` is
outside the ticket's paths, and W1-21 builds `gov retrieve`. The functions are reached as attributes of three
modules. `root` is the project root, a `Path`. Every value is plain JSON data. Each call is made in a new Python
process whose working directory is not the project. **No function raises because Ollama, `sqlite_vec` or the
reranker is absent.**

| Function | Returns |
|---|---|
| `gov.retrieval.semantic.refresh(root)` | Brings the lexical index up to date, then embeds the chunks that have no vector. `{"available": bool, "facet": "semantic", "state": str, "reason": str or None, …}`. Unavailable (Ollama absent, no `sqlite_vec`): `available` false, `state` `"FACET_UNAVAILABLE"`, a non-empty `reason`. More keys are allowed. |
| `gov.retrieval.semantic.search(root, query, refresh=True)` | The same four keys and `"hits": [...]`, nearest first, each chunk once. A hit is the chunk record of W1-17: `{"chunk_id", "path", "start_line", "end_line", "parent_id"}`, more keys allowed. Unavailable carries no hit. With `refresh=False` nothing is written, and a missing or stale index is reported unavailable (DEC-342, DEC-322). |
| `gov.retrieval.semantic.manifest(root)` | `None` when there is no index; else `{"embedder": {"model", "revision"}, "reranker": {"model", "revision"}}`. Writes nothing and asks Ollama nothing: the manifest is held in the shared store (DEC-374). The embedder's revision is the digest the endpoint's model list reported when the vectors were built, not a constant (DEC-374); the tests accept the digest or its first twelve or more characters, with `sha256:` allowed in front. |
| `gov.retrieval.fusion.rrf(routes, k=60)` | `routes` is `route name -> ranked hits`, each hit a map with `chunk_id`. One list, best first: each chunk once, with the fields it came with, `score` (the sum of `1 / (k + rank)` over the routes that returned it, ranks from 1) and `routes` (the names of those routes). Several hits of one route in one chunk count once, at the best rank. |
| `gov.retrieval.fusion.search(root, query, limit, refresh=True, reranker=None)` | The whole retrieval: both routes, RRF, one rerank. `{"hits": [...], "facets": {"lexical": {…}, "semantic": {…}}, "reranked": bool}`. A hit is a chunk record with `routes`. Each facet entry has `available`, `facet`, `state`, `reason`. A limit cuts after the rerank; `limit=None` returns the whole reranked merged set. The tests always pass `limit` by name. |
| `gov.retrieval.rerank.rerank(query, candidates, reranker=None)` | `candidates` in the order of the reranker's scores, each with what it came with and `rerank_score`; equal scores keep the order given. A candidate carries `text`. |
| `reranker` | The loader: a function without arguments that returns `score(query, texts) -> [float, …]`, higher is better. It is called at the first rerank and not before, and one rerank calls `score` once with every candidate's text. The default is the pinned Qwen3 reranker (ADR-0002 §2: a separate, pinned process). |

Route and facet names are `lexical` and `semantic`.

## How the default reranker starts (DEC-397)

Decided by the owner: the default reranker's process starts from the environment
`~/.local/share/gov-os/reranker-venv`, with its interpreter `~/.local/share/gov-os/reranker-venv/bin/python`, as a
process of its own (ADR-0002 §2), never from the S0b2 environment in the workbench, and offline
(`HF_HUB_OFFLINE=1`; nothing is downloaded). With the environment or the snapshot absent, DEC-374 holds.

| What is held | Case | How it is seen from outside |
|---|---|---|
| The process is that environment's interpreter, and never the workbench's | `test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment` (real reranker) | The process watcher records every descendant's `argv`. One descendant's first argument is a `python` in that environment's `bin`; no Python descendant has another interpreter; no descendant's first argument is in the workbench. The path is compared as written: the environment's interpreter is a link to the system's. |
| It is a process of its own | the same case, and the two below | `torch`, `transformers` and `sentence_transformers` are not in the calling process's `sys.modules` after the call (the driver now reports them after each call, as it did before each). |
| It scores | the same case | Every candidate carries a number as `rerank_score`, the order is the order of the scores, and of three texts the one that answers the question is first. |
| It runs offline; an absent snapshot is not fetched | `test_with_the_environment_and_no_snapshot_nothing_is_reranked_nothing_is_fetched_and_nothing_raises` | The caller's environment does not hold the libraries offline and names a recording stand-in as the only hub. The stand-in must be asked nothing. |
| Snapshot absent: DEC-374 | the same case | The fused order, `reranked` false, no exception. |
| Environment absent: DEC-374, and no process from elsewhere | `test_with_no_reranker_environment_no_other_interpreter_is_started_and_nothing_heavy_is_loaded`, with the two older cases | The order given, no exception, no Python descendant, nothing heavy in the calling process. |

**Not fixed by any test:** how the calling process and the reranker's process talk to each other, the command
after the interpreter, whether the process stays between retrievals, and how the environment is told to be
offline (a variable given to the process, or set inside it). No public name and no environment variable was
invented for any of it.

**Two readings the designer made.**

- **`~` is the folder `HOME` names.** The two older cases and the two new absent cases rest on it: they make the
  default absent, or half present, by giving the process another `HOME`. `gov.retrieval.ollama` finds its
  executable the same way. An implementation that finds the home folder another way (the password database) would
  find the real environment under an empty `HOME`, and the two older cases would go red. That would be a matter to
  decide, not a test to bend.
- **The reranker's process is a descendant of the calling process.** DEC-373 already records that a reranker that
  detaches from the process tree is not seen by the memory measure. The same holds here: a detached process fails
  the first row of the table.

**What the offline observation can and cannot show.** It is made where the snapshot is absent, because only there
is it certain that a process which is not offline asks the hub: checked with a throwaway script, the environment's
`CrossEncoder` asked the stand-in three times without `HF_HUB_OFFLINE`, and nothing with it. Where the snapshot is
complete, no observation was made of whether the libraries ask anything. One residual: an implementation that both
discards its caller's environment and does not set `HF_HUB_OFFLINE` would pass the stand-in by and reach the real
hub. The engineer is told.

## The seven packages of the first batch, and what settled each

| Package | Settled by | What the answer changed in the suite |
|---|---|---|
| **DP-1** the public interface | **DEC-379** (owner): as proposed, name by name | Nothing in the cases. One case added for the last line of the decision: `test_without_sqlite_vec_the_semantic_facet_is_unavailable_and_nothing_raises`. |
| **DP-2** what mean hit@5 is | **DEC-380** (owner): S0b2's own method where it is stated | S0b2 states it (below). The two hit@5 cases were revised: per class and the mean of the ten classes, not per tier; the first five distinct paths, not the first five chunks; every query counts. |
| **DP-3** warm p95 and peak RAM | **DEC-373** (delegated): option (a) for both | Nothing: the two cases measure as the decision states it. |
| **DP-4** a reranker that cannot be loaded | **DEC-374** (delegated): the fused order is kept, the answer says nothing was reranked, nothing raises | The existing case now also holds the order to the fused order, and no longer skips by what the test interpreter can import. One case added for `rerank.rerank`. |
| **DP-5** the manifest | **DEC-374** (delegated): held in the shared store, read through the semantic module; the embedder's revision is the one observed from Ollama's model list | The manifest case now holds the revision to the digest the stand-in's model list reports. Two cases added: another digest in the model list, and a clone given only the store's files. The stand-in's `/api/show` no longer carries a digest. |
| **DP-6** `embedding_policy` | **DEC-381** (owner): a namespace that is `not embedded` never reaches the vectors | Two cases added, in `test_w1_19_embedding_policy.py`. |
| **DP-7** the read of G-17's row | **DEC-382** (owner): accepted; DEC-370 extends to G-17 | Nothing. |

Also read: DEC-383 (the four S0b2 files a worker may read by exact path) and DEC-384 (nothing is installed in
that round).

## The two packages of the second batch, and the installs

| Package | Settled by | What the answer changed in the suite |
|---|---|---|
| **DP-8** how `embedded, except vendored code` is read | **DEC-388** (delegated): the closed list is `embedded` and `not embedded`; any other value is not embedded | Nothing: the policy cases already read it closed, with `embedded on request` as the unknown value. |
| **DP-9** the two queries with no gold path | **DEC-388** (delegated): hit@5 per class over all 52 queries; the two count as misses | Nothing: the rule in the tests is the one decided. It is not changed. |
| The installs, and how the default reranker starts | **DEC-397** (owner) | The scratch environment was put right, the `needs` marker sees the reranker environment, and three cases were added (the section above). |
| **DP-12** the pass line of mean hit@5 | **DEC-414** (owner): at or above 80 on the dev tiers is the pass line; 85 is re-measured at the Wave 1 exit run (W1-42) and at qualification | The baseline case was rewritten to the pass line of 80 and renamed; the failure-line case, now the same assertion, was removed; the measured figure and where it stands against 85 are always shown (the fourth batch, above). 42 cases became 41. |

## hit@5: S0b2 states its method, and the cases follow it (DEC-380)

`~/gov-os-workbench/s0b2/out/RESULTS.md`, read by exact path (DEC-383), states the method in three places:

> **Corpus:** clones of `synthetic/a-dev` and `b-dev`, queries from `synthetic/dev-queryset.yaml` (52 queries, ten classes).

> Scoring: each candidate's top-5 distinct paths per query against `must_cite` / `must_not_cite` in
> `dev-queryset.yaml`. The same matcher is applied to both: the agent's `eval_r*.py` path matcher, not
> `synthetic/scoring/score.py`, so the absolute numbers are not directly comparable with a scorer run

and the table of §1, whose rows are the ten classes with their sizes (`decisions (6)` … `why (5)`, `history (6)`),
and whose last row is

> | **Mean of ten classes** | **85.0** | **76.0** | **0.711** | **0.584** |

So S0b2's 85 is the mean of ten per-class percentages. It is not a mean of two tiers. Since DEC-414 it is the
baseline the measured mean is reported against, not the pass line: the pass line on the dev tiers is 80, by the
same method.

**The rule in the tests.**

1. Stated by S0b2: the **first five distinct paths** of a query's results are scored (the cases ask for the whole
   reranked list and take the first five distinct paths in rank order).
2. Stated by S0b2: a **percentage per class**, both tiers together, over every query of the class. The sizes in
   S0b2's table add up to 52, so **all 52 queries count**.
3. Stated by S0b2: the **mean of the ten classes' percentages**, against 80 (the pass line of success 2 and the
   failure line of failure 1, DEC-414). Where it stands against 85 is reported and not asserted.
4. Not stated by S0b2, so DEC-380's option (a): a query is a **hit when one of its `must_cite` paths** is among
   those five paths, by equal path. The matcher itself (`eval_r*.py`) is not one of the four files a worker may
   read. `must_not_cite` does not enter hit@5: S0b2 reports it apart ("Forbidden citations (top-5)").

**One point where the two halves of DEC-380 meet.** Two queries (`DQ-A-21`, class why; `DQ-A-24`, class history)
name no `must_cite` path. Option (a) would leave them out; S0b2's class sizes (`why (5)`, `history (6)`) include
them. The cases follow what S0b2 states: they count in their classes, and with no path to reach they are misses.
This is the stricter reading (it can only lower the mean: at most 96.3 instead of 100). How S0b2 scored those two
is not stated; its figures for the two classes (80.0 and 83.3) are what one miss in each gives.

The code-intelligence report (`~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md`) was searched for the scoring
words only; it scores the code classes of the same set by "in top 5" and adds nothing to the method.

## `embedding_policy`: the closed reading (DEC-381)

The schema of W1-08 (`template/governance/kernel/schemas/path-map.schema.json`) requires the field on every
namespace and allows any non-empty text; the loader in `src/gov/config/` checks neither. DEC-289 moved the closed
list to the first ticket that reads the field, which is this one. The cases read it closed:

| The namespace's `embedding_policy` | Read as | In the policy fixture |
|---|---|---|
| `embedded` | embedded | `open/**` |
| `not embedded` | not embedded | `closed/**`, the root files, `governance/**` |
| any other value | not embedded (fail closed) | `odd/**`: `embedded on request`, which a reading by prefix or by substring would take for `embedded` |
| no field | not embedded (fail closed) | `bare/**` |

"Never reaches the vectors" is observed through the interface of DEC-379 and the stand-in endpoint, with no new
public function: no word of such a file is in any request to be embedded, and the file is not a hit of the semantic
route, alone or in the fused list. The lexical index is W1-17's and is not changed: the cases require that the same
files are still found by the lexical route.

- `test_no_text_of_a_namespace_that_is_not_embedded_is_sent_to_be_embedded_or_returned` needs no `sqlite_vec`. It
  passes. **What it can show on a machine without `sqlite_vec` is limited:** there nothing can be embedded, so it
  holds for an implementation that sends nothing at all. It catches an implementation that sends text to the endpoint before
  it knows it can store a vector, and one that drops the files from the lexical route.
- `test_only_the_namespace_that_says_embedded_reaches_the_vectors` needs `sqlite_vec`; it passes since the third
  batch. It is the whole rule, with its premise (the `embedded` namespace's text is sent and its file is a semantic hit) and one edge:
  files without a vector do not make the index stale.

The sources give no model-free way to see the positive half through the interface of DEC-379: without
`sqlite_vec` the facet is unavailable and the manifest is `None`.

**Not tested: the third value in use.** This repository's own map gives `template/**` the value
`embedded, except vendored code`. No source says which paths are vendored code. DEC-388 decides it as the cases
read it: an unknown value, so not embedded, and `template/**` is found by the lexical route only. No case uses that
value itself; `embedded on request` stands for every unknown value.

## KPI lines and their tests

| KPI line | File | Tests | Today |
|---|---|---|---|
| **Success 1.** sqlite-vec with qwen3-embedding:0.6b, RRF, and one lazily loaded Qwen3-Reranker pass over the merged set [CAP-10.a, CAP-18.a] | `test_w1_19_fusion.py` · `test_w1_19_rerank.py` · `test_w1_19_unavailable.py` · `test_w1_19_embedding_policy.py` · `test_w1_19_semantic_index.py` · `test_w1_19_real_models.py` | all 7 of `test_w1_19_fusion.py` · all 7 of `test_w1_19_rerank.py` · 8 of `test_w1_19_unavailable.py` (all but `test_there_is_no_manifest_before_there_is_an_index`) · both of `test_w1_19_embedding_policy.py` · `test_a_question_no_line_holds_reaches_its_chunk_by_its_vector` · `test_a_semantic_hit_is_a_chunk_record_of_the_shared_store_with_its_parent` · `test_the_vectors_are_in_the_shared_store_beside_the_lexical_index` · `test_no_text_the_secret_filter_refuses_is_embedded_or_returned` · `test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass` · `test_a_changed_file_is_embedded_before_the_next_retrieval_and_stale_vectors_are_reported` · `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` · `test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment` · `test_every_answer_is_one_fused_list_from_both_routes_reranked` | the 30 outside the real-model file pass; of the 3 in it, the embedder case passed in the lead's run, the default-reranker case is red (no default yet), the third waits for the reranker |
| **Success 2.** Dev query set mean hit@5 >= 80 on the dev tiers is the pass line; 85 (the S0b2 R1 baseline) is re-measured at the Wave 1 exit run (W1-42) and at qualification (DEC-414); warm p95 <= 0.5 s | `test_w1_19_real_models.py` | `test_the_dev_query_set_mean_hit_at_5_is_at_or_above_the_pass_line_of_80` (it reports the mean against 85 and asserts nothing about 85) · `test_a_warm_query_answers_within_half_a_second_at_p95` | the hit@5 case is revised in the fourth batch and not run by the designer; the latency case is unchanged and not run by the designer |
| **Success 3.** Model ids and revisions are recorded in the index manifest [CAP-10.a] | `test_w1_19_semantic_index.py` · `test_w1_19_unavailable.py` · `test_w1_19_real_models.py` | `test_the_manifest_records_the_model_ids_and_their_revisions` · `test_the_embedders_revision_is_the_one_the_model_list_reports_not_a_constant` · `test_the_manifest_is_held_in_the_shared_store_and_read_without_ollama` · `test_there_is_no_manifest_before_there_is_an_index` · `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` | the 4 stand-in and model-free cases pass; the real-embedder case passed in the lead's run |
| **Failure 1.** Mean hit@5 falls below 80 | `test_w1_19_real_models.py` | `test_the_dev_query_set_mean_hit_at_5_is_at_or_above_the_pass_line_of_80`: the same case as success 2, which fails exactly when the mean is below 80 | revised in the fourth batch; not run by the designer |
| **Failure 2.** Peak RAM of the rerank process exceeds 2.5 GB | `test_w1_19_real_models.py` | `test_the_rerank_process_stays_within_two_and_a_half_gigabytes` | unchanged; not run by the designer |

**Count.** KPI lines with tests: 5 of 5 (3 success, 2 failure). Since the fourth batch the hit@5 half of success 2
and failure 1 are held by one case, because DEC-414 made them one comparison. The "Today" column of success 1 and 3
is as written at the third batch; the dev-tier cases are the ticket lead's to run.

| Covers id | Tests |
|---|---|
| **CAP-10.a** paraphrase retrieval with the pinned embedder | `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` (real model) · `test_the_dev_query_set_mean_hit_at_5_is_at_or_above_the_pass_line_of_80` (real models) · `test_a_question_no_line_holds_reaches_its_chunk_by_its_vector`, the three manifest cases and `test_only_the_namespace_that_says_embedded_reaches_the_vectors` (stand-in endpoint) · `test_the_semantic_route_says_unavailable_when_ollama_is_absent`, `test_without_sqlite_vec_the_semantic_facet_is_unavailable_and_nothing_raises` and `test_no_text_of_a_namespace_that_is_not_embedded_is_sent_to_be_embedded_or_returned` (run now) |
| **CAP-18.a** fusion (RRF), dedup by chunk hash, one rerank | all of `test_w1_19_fusion.py` and `test_w1_19_rerank.py` · `test_without_ollama_the_fused_list_is_the_lexical_routes_reranked_in_one_pass` · `test_a_limit_cuts_the_list_after_the_rerank_not_before` · `test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so` · `test_with_the_environment_and_no_snapshot_…` · `test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass` (stand-in endpoint) · `test_the_default_reranker_is_a_process_of_its_own_…` (real reranker). The multi-route router with the graph route, and the bundle, are W1-21. |

## Which tests need which install

A `needs` marker names what a case needs; the case skips, with the reason, when this machine lacks it. Nothing is
installed, started or downloaded to decide a skip: it is `shutil.which`, `importlib.util.find_spec` and four
exact paths. Everything below is installed on this machine since DEC-397, so nothing skips here.

| Needs | Decided by | Cases | Today |
|---|---|---|---|
| nothing | — | 7 fusion, 7 rerank, `test_a_search_that_may_not_write_…`, `test_there_is_no_manifest_…` (16) | pass |
| `gitleaks` | on `PATH` | 6 of `test_w1_19_unavailable.py`, `test_no_text_of_a_namespace_that_is_not_embedded_…`, the premise (8) | pass |
| `gitleaks`, `reranker_env` | an executable file at `~/.local/share/gov-os/reranker-venv/bin/python` | `test_with_the_environment_and_no_snapshot_…` (1) | passes, as a guard (no default yet) |
| `gitleaks`, `sqlite_vec` | `sqlite_vec` importable by the Python that runs pytest | the 9 stand-in cases of `test_w1_19_semantic_index.py`, `test_only_the_namespace_that_says_embedded_…` (10) | pass |
| the above and `ollama` | an executable at `GOV_OLLAMA_BIN`, on `PATH` or at `~/.local/ollama/bin/ollama`, and the file `manifests/registry.ollama.ai/library/qwen3-embedding/0.6b` under `$OLLAMA_MODELS` or `~/.ollama/models` | `test_the_pinned_embedder_reaches_a_section_…` (1), marked `local_only` | passed in the lead's run; not run by the designer |
| `reranker` | `reranker_env`, and the folder `models--Qwen--Qwen3-Reranker-0.6B/snapshots/e61197ed…5473` in the Hugging Face cache (`HF_HUB_CACHE`, `HF_HOME` or `~/.cache/huggingface/hub`) | `test_the_default_reranker_is_a_process_of_its_own_…` (1), marked `local_only` | red: no default yet |
| `gitleaks`, `sqlite_vec`, `ollama`, `reranker` | all of the above | the 4 dev-tier cases (5 before the fourth batch), marked `local_only`; they also skip when the dev tiers or the query set are absent | not run by the designer |

16 + 8 + 1 + 10 + 1 + 1 + 4 = 41.

**The `reranker` entry now sees the environment's interpreter as well as the snapshot.** Before DEC-397 the
place of the process was not decided, so the marker could not look for it. Now it is one exact path. A machine
that has the snapshot and not the environment lacks an install, and the five cases that use the real reranker (six before the fourth batch) skip
there with that reason. Without the change they would fail, and a failure reads as a fault of the ticket. The
entry looks at the file only and starts nothing: an environment that is there and broken makes the cases fail, as
it should. `reranker_env` is the interpreter alone, for the case that holds the snapshot absent.

**Five cases use an absent thing on purpose:**

- `test_without_sqlite_vec_…` puts a module named `sqlite_vec` that raises `ImportError` first on `PYTHONPATH`, so
  the import fails whatever the machine has. Its environment does not carry the link to the installed package.
- `test_a_reranker_that_cannot_be_loaded_…`, `test_reranking_with_no_reranker_that_can_be_loaded_…` and the new
  `test_with_no_reranker_environment_…` pass no `reranker` and run in the scratch environment. **Their premise was
  checked again after the installs, as this file asked.** It now rests on one thing: the default reranker's
  environment is found under the home folder (DEC-397), and the scratch environment's `HOME` is an empty folder, so
  it holds neither the environment nor a Hugging Face cache. The S0b2 environment is in the workbench, which is
  under the real home folder too, and DEC-397 rules it out in any case. That the libraries are held offline there
  no longer carries the premise. See the reading "`~` is the folder `HOME` names" above.
- `test_with_the_environment_and_no_snapshot_…` gives the process a `HOME` that holds one link, to the reranker
  environment, and no Hugging Face cache.

**What this machine has** (DEC-397; the rows of `governance/project/tool-registry.yaml`): `sqlite_vec` 0.1.9 in
the user site folder of `/usr/bin/python3`; Ollama 0.35.0 at `~/.local/ollama/bin/ollama`, off the `PATH`, with
`qwen3-embedding:0.6b`; the reranker environment at `~/.local/share/gov-os/reranker-venv`; and the pinned snapshot
in `~/.cache/huggingface/hub`. `sentence_transformers`, `torch` and `transformers` cannot be imported by
`/usr/bin/python3`, which is as it should be.

## How the tests decide

- **Every project is a temporary git repository** (DEC-322): a clone of a fixture repository with its own path
  map, a copy of `template/.gitleaks.toml`, and its own `.gov-runtime/store.db`. No test builds an index in this
  worktree, and no test copies this repository or a folder of it.
- **Two environments.** Model-free cases get an environment built from scratch: an empty `HOME`, `PATH` without
  `ollama`, `OLLAMA_HOST` on a loopback port nothing listens on, and the Hugging Face libraries held offline.
  That is "Ollama absent". The real-model cases get this machine's own environment, also held offline.
- **The scratch environment imports `sqlite_vec` exactly when the `needs` marker says the machine has it.** The
  package the Python that runs pytest finds is linked, alone, into a folder that follows `src` on `PYTHONPATH`.
  Nothing else of the real home folder is reachable from the scratch environment, and nothing is copied.
- **The snapshot-absent premise was checked apart.** A throwaway script outside the repository started the
  reranker environment's interpreter through the linked `HOME` and asked `sentence_transformers` for the pinned
  model: the environment starts through the link, the load fails for want of the snapshot, and the stand-in hub is
  asked three times without `HF_HUB_OFFLINE` and never with it. No model was loaded and nothing was downloaded.
- **The process watcher** records, for the calling process and every descendant, the first four arguments and the
  peak resident memory. The cases for the default reranker read the first argument.
- **The stand-in reranker** lives in the driver process. Its loader counts each load; its scorer records each
  pass and scores a text by how often it holds the word `quartz`. Only the file the lexical route lists last holds
  that word, so a list that is not reranked, or reranked before the routes are merged, has another first entry.
- **The stand-in Ollama endpoint** answers `GET /api/version`, `GET /api/tags` (the model list: the model with
  its digest), `POST /api/show` (no digest, as with the daemon), `POST /api/embed` and `POST /api/embeddings`,
  with 1024 numbers computed from the words of the text. It records every request, which is how "no refused text
  was sent to be embedded" is read. Its digest begins with the pin unless a case gives it another. The scratch
  environment has no `ollama` executable, so the model list of the endpoint is the only place a revision can be
  observed (DEC-374).
- **The fixture corpus** is eight tracked files. Three hold the exact phrase `amber lantern protocol`, one of them
  on two lines of one chunk. Two more files are tracked and must never reach an index: one in a namespace the map
  classes as product data, one that holds a planted canary (built at run time from parts). All its namespaces say
  `embedded`.
- **The policy fixture** (DEC-381) is a second repository: four governance namespaces that differ only in
  `embedding_policy`, one file in each. Each file holds one word no other file and no question holds, and all four
  hold the phrase `pewter whistle signal`.
- **Lazily loaded** is read three ways: the loader is not called before the first rerank; `torch`, `transformers`
  and `sentence_transformers` are not in `sys.modules` after the three modules are imported or after a fusion;
  and reranking nothing loads nothing. Since DEC-397 a fourth: with the default reranker the calling process holds
  none of the three after the rerank either, because the model is loaded in the reranker's own process.
- **The fused order** (DEC-374) is what `fusion.rrf` returns for the lexical route's own hits; the case compares
  the chunk ids of `fusion.search` with it, one after the other.
- **hit@5**: the section above. The pass line is 80 (DEC-414); the measured mean is always shown, against 80 and
  against 85 (the fourth batch, at the head of this file).
- **Warm p95** (DEC-373): per tier, one process builds the index, asks three warm-up questions that are not
  in the set, then asks each dev query once. Each call is timed inside that process. p95 is the nearest-rank 95th
  percentile over the 52 timed calls, against 0.5 s.
- **Peak RAM** (DEC-373): while that process runs, a thread reads `VmHWM` of the process and of every
  process descended from it, every 50 ms, leaving out any process named `ollama` and its children. The largest
  single process must stay at or under 2.5 × 10⁹ bytes. A reranker that detaches from the process tree is not
  seen: a residual the decision records.
- **The tiers** are cloned into a temporary directory and adopted with a map that classes everything as
  governance memory and as `embedded`, as the W1-17 suite does.

## Readings the designer made, where a decision leaves room

Each is the stricter or the plainer reading; none is a new public name.

- **`rerank.rerank` with no reranker** returns the candidates it was given, in the order given, each with what it
  came with (DEC-379: it returns the candidates and does not raise; DEC-374: nothing is reranked and the order is
  kept). No candidate may carry a number as `rerank_score`, because nothing was scored. Whether the key is left
  out or is `None` is open, and the case accepts both.
- **`semantic.manifest` without `sqlite_vec`** on a project that has never had vectors is `None` (DEC-379:
  `None` without an index).
- **A file of a namespace that is not embedded is still a lexical hit**, in `lexical.search` and in the fused list.
- **Another digest in the model list is recorded, not refused.** A mismatched model failing closed is CAP-19
  (Wave 2).
- **The reranker's revision** in the manifest is the pin of ADR-0002: DEC-374 names only the embedder's as
  observed.

## What was read

- In the tree, first batch: the ticket, `contract.yaml` (CAP-10, CAP-18), the WBS rules, the decisions of that
  time, ADR-0002, the tool registry, the bootstrap residuals of W1-15, W1-17 and W1-18, the retrieval, secrets and
  store code, and the W1-16, W1-17 and W1-18 suites.
- In the tree, second batch: the ticket, CAP-10 and CAP-18, the WBS rules, the decisions named in this file (each
  in full), the lexical index, the Ollama lifecycle module, the secret filter's namespace code, the config loader,
  the path-map schema of W1-08 and this repository's path map (its namespaces). ADR-0002 and the tool registry were
  not read again; the chunking and store-loader code was not read in this batch.
- `~/gov-os-workbench/s0b2/out/RESULTS.md`, by exact path (DEC-380, DEC-383): the head and §1 in full, and the
  lines of the rest that a search of that one file for the scoring words returned.
- `~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md`, by exact path (DEC-383): only the lines a search of
  that one file for the scoring words returned.
- `~/gov-os-workbench/s0b2/out/GLUE_REQUIREMENTS.md` (first batch): the G-20 row, and by a mistake of the
  designer the G-17 row; DEC-382 accepts that read.
- `$GOV_DEV_TIERS/dev-queryset.yaml`, by exact path: the classes, their sizes per tier, and the two queries
  without a `must_cite` path. No folder of the workbench was listed.

- Third batch: this folder in full, the ticket, ADR-0002 §2, the reranker and `sqlite_vec` rows of the tool
  registry, DEC-397, DEC-388, DEC-374, DEC-379, DEC-373, DEC-384, DEC-322 and DEC-372 (each in full), and
  `rerank.py`, `fusion.py`, `semantic.py` and the head of `ollama.py` as they stand. No S0b2 file was read. Four
  exact paths under the home folder were looked at, to see that they exist: the two the `needs` marker reads for
  the reranker, the Ollama executable, and the user site folder (listed once, which was more than was needed).

- Fourth batch: the ticket, DEC-414, DEC-380 and DEC-388 (each in full), this file, `test_w1_19_real_models.py`,
  the conftest and the hit@5 parts of the support module, and the hit@5 lines of the lead's last run log under
  `.gov-runtime/scratch/`. Nothing under the workbench was read or listed.

## Open after the fourth batch

Nothing is returned for decision: the restated line is read as it is written. The four dev-tier cases, the revised
one among them, are the ticket lead's to run.

## Open after the third batch

*As written at the third batch.*

Nothing is returned for decision. DP-8 and DP-9 are decided (DEC-388), and how the default reranker starts is
decided (DEC-397). Three things stay with the ticket lead and the engineer:

- **The six cases of `test_w1_19_real_models.py` the designer did not run**, and the seventh, which is red until
  `default_reranker()` exists.
- **The two guards pass today against a default that is always absent.** They show something only once the
  default exists. `test_with_the_environment_and_no_snapshot_…` then starts the reranker environment's
  interpreter, which takes some seconds.
- **The reading "`~` is the folder `HOME` names"** (above). If the engineer needs another rule, it is a decision.

## Not tested, on purpose

- The quality of the stand-in vectors; anything about the graph route, the bundle, paging or `gov retrieve` (W1-21).
- The embedding model's registry row (DEC-195; the registry is outside the ticket's paths).
- Whether the reranker stays loaded between retrievals, and the idle unload (DEC-261).
- How the calling process and the reranker's process talk to each other, and the command after the interpreter.
- That the reranker's process runs offline where the snapshot is complete (see "How the default reranker starts").
- A mismatched or unpinned model failing closed (CAP-19, Wave 2).
- The RRF constant's default: the cases that compare scores pass `k=60`.
- Spellings of `embedding_policy` that differ from the two known values only by case or spacing, and a path that
  matches two namespaces with different policies.
