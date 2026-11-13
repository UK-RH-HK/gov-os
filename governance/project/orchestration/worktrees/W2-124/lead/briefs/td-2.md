# Brief: independent test designer, DAEO-mb2t (W2-124), STANDARD, class C2 — P1-L (a): revise 20 earlier cases under DEC-1027 C (run 3, td-2)

Budget: projection 3 USD. Keep your context short: read only what each case needs; cut long outputs to head and tail.
(Hand-built by the lead: `gov context DAEO-mb2t --role independent-test-designer` refuses this ticket with
CONTEXT_OVER_CEILING; this brief and the ticket are your inputs.)

You are a fresh independent test designer (MR-3) for ticket DAEO-mb2t (W2-124). You work only in
`/home/usain/gov-os-worktrees/W2-124-tests` on branch `w2/W2-124-tests` (DEC-963). No engineer runs in this round.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-124-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-mb2t`. If it fails, stop and return (delete nothing). Then read `EMG-common.md` beside it (its test-designer
paragraph applies).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-mb2t`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-124-tests`, `w2/W2-124-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-mb2t.md`: its `## Interface` and the section
  **"P1-L decided"** at its end are binding. The register (`docs/DECISION_REGISTER.md`): grep only by id
  (`### DEC-1027`, `### DEC-1150`).
- **Writes: only these 13 files**, and in them only the cases listed below:
  `tests/acceptance/W2-32/test_w2_32_s2_fail_closed.py`, `tests/acceptance/W2-32/test_w2_32_s10_no_cpu_fallback.py`,
  `tests/acceptance/W2-13/test_w2_13_secrets.py`, `tests/acceptance/W2-13/test_w2_13_unavailable.py`,
  `tests/acceptance/W2-13/test_w2_13_latency.py`, `tests/acceptance/W2-76/test_w2_76_timings.py`,
  `tests/acceptance/W2-76/test_w2_76_unchanged.py`, `tests/acceptance/W2-116/test_w2_116_reindex.py`,
  `tests/acceptance/W1-41/test_w1_41_embedding_policy.py`, `tests/unit/rebuild/test_w2_116_integration.py`,
  `tests/unit/rebuild/test_no_embeddings.py`, `tests/unit/rebuild/test_w2_122_seed.py`,
  `tests/unit/retrieval/test_w2_32_rebuild_cut.py`.
  **The support modules beside them (`w2_32_support.py`, `w2_13_support.py`, `w2_76_support.py`, `w2_116_support.py`,
  conftest files) are NOT yours**: a small local helper inside the test file is fine; if a case truly cannot be revised
  without editing a support module or conftest, do not edit it: return PACKAGES naming the case and why.
- You may read the code (`src/gov/rebuild/command.py`, `src/gov/close/rebuild_gate.py`, `src/gov/rebuild/integration.py`)
  to learn where a refusal's stores now sit; the implementation is done and is not changed in this round.
- **Every pytest** goes through the heavy slot, with the sandbox's TMPDIR (outside the repository and outside
  `~/gov-os-runs`; check `echo $TMPDIR`), in this form (one file or node id at a time is fine):
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-124-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-124-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or node> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (create the empty-home folder first if absent). A resource gate's refusal is a wait, not a refusal (DEC-1146): wait
  and run again. If the sandbox itself refuses the heavy slot, say so and run the same line without it.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). No `$(…)` or variable as a write target, no here-document, no `bash -c`.
  Foreground only. No reset, checkout, clean, amend, rebase, push, merge or install.
- No test starts a real embedder or model; stand-ins only (the suites' own loopback stand-ins).
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). On an authentication error return `AUTH_REQUIRED`.

## Why these cases are red

DEC-1027 C, now implemented on this branch: a rebuild whose path map has a namespace with `embedding_policy: embedded`
and no `--no-embeddings` *asks for* the semantic store; when that store is not recreated (no embedder, hung, failing
part way, or refused for a pin / CPU reason) `gov rebuild` fails: `GovError` `REBUILD_FAILED`, exit 1, `--json`
envelope `"ok": false`, `error.code == "REBUILD_FAILED"`, `error.details == {store: "semantic", reason, stores}` where
`stores` is the full stores map the run built (`stores.semantic` holds the refusal and its named code; `stores.lexical`
etc. as built). In-process, `gov.rebuild.command.run` raises that `GovError` with `.details["stores"]`. Where
`gov.rebuild.integration` wraps `command.run`'s error, the inner details sit one level down (`details["details"]["stores"]`
as observed in run 2; confirm by reading `integration.py`). A project with no embedded namespace is not asked:
`stores.semantic = {status: not_recreated, requested: false, reason, ...}` and the rebuild is ok. Each of the cases below
built a project with an embedded namespace and no healthy embedder, so its rebuild now fails before its own assertion.

## The rule for every revision (the owner's P1-L (a), DEC-1150 (3)) — read twice

1. One revision per case, with a `Rewrite-Reason: DEC-1027 C (the rebuild refuses an embedded namespace with no
   embedder); P1-L (a), DEC-1150 (3)` line in its docstring or a comment beside the change (the files' existing form).
2. The only means: the case's rebuild gets `--no-embeddings`, **or** a healthy stand-in embedder, **or** (where the case
   checks a refusal) it reads the refusal from `error.details.stores` (CLI) / `GovError.details["stores"]` (in-process,
   or the wrapped level for integration) instead of `result.stores`. Choose per case the means that keeps its point.
3. **Each revised case keeps what it was guarding.** A case that proved a refusal still proves that same refusal, with
   the same named code and the same "nothing embedded / no vector / nothing started / no record" assertions. The test:
   if the behaviour the case guards were broken (e.g. the pin check removed, vectors written on the CPU, the link
   moved, a record left), the revised case must turn red. Never weaken an assertion, drop one, or widen a bound; you
   may add an assertion that the run failed with `REBUILD_FAILED` where that is now the shape of the refusal.
4. `--no-embeddings` is the wrong means for a case whose point is the semantic stage itself (a refusal, a cut, a "full"
   rebuild's semantic timing): there use the refusal-read or a healthy stand-in. A "full" mode must stay a rebuild
   without `--no-embeddings`.
5. Nothing else in the files changes: no other case, no reformatting, no renamed helper used elsewhere.

## The 20 cases and what each guards (node ids at the base 1f9bd6d90)

W2-32 S2 (fail-closed, the most important: a refusal stays a refusal):
1. `test_w2_32_s2_fail_closed.py::test_an_endpoint_reporting_another_revision_of_the_pinned_model_fails_closed_at_rebuild`
   — guards: an endpoint reporting another revision is refused at rebuild: semantic not `recreated`, named `…_MISMATCH`,
   nothing embedded, no vector in the store. Means: read `error.details.stores.semantic` (its `s.semantic_store`
   helper reads `result.stores`; a local reader in the file is fine).
2. `…::test_a_configured_model_without_a_revision_fails_closed_at_rebuild[no-revision|empty-revision|null-revision]` (3)
   — guards: a model without a revision is refused: not recreated, named `…_UNPINNED`, nothing embedded.
3. `…::test_a_pinned_model_the_endpoint_does_not_list_fails_closed_at_rebuild` — guards: refusal names a code and the
   pinned model; no other model asked in its place.
W2-32 S10:
4. `test_w2_32_s10_no_cpu_fallback.py::test_a_rebuild_with_the_embedder_unreachable_refuses_the_vectors_and_starts_nothing`
   — guards: semantic refused with a named code, the lexical index still `recreated` (now in `error.details.stores.lexical`),
   no vector, nothing started.
5. `…::test_a_rebuild_with_the_embedder_on_the_cpu_refuses_to_embed` — guards: refused with a named code, no vector,
   no cache row, nothing started.
W2-13:
6. `test_w2_13_secrets.py::test_a_second_rebuild_answered_from_the_secrets_cache_indexes_the_canary_no_more` — guards:
   two rebuilds answered from the secrets cache never index the canary, and the clean file is still found. Semantic
   is not its point (`--no-embeddings` or a healthy stand-in both fit; `box.rebuild` takes `host=`/`env=`).
7. `test_w2_13_unavailable.py::test_a_search_of_an_unusable_index_answers_unavailable_and_never_raises[stale]` — guards:
   a lexical search of a stale store answers unavailable and never raises. (`make_store` is in the test file.)
8. `…::test_gov_retrieve_on_an_unusable_index_answers_without_a_traceback[stale]` — guards: `gov retrieve` on a stale
   store answers with no traceback. Keep the other `STORES` parameters' behaviour unchanged.
9. `test_w2_13_latency.py::test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget` (serial) — guards:
   the ranked lexical route answers a warm question within its budget; the budget is not widened.
W2-76:
10. `test_w2_76_timings.py::test_every_stage_timed_in_output_and_record[full]` — guards: a *full* rebuild (no
    `--no-embeddings`) times every stage (incl. the semantic one) in output and record, the record matches the output,
    slow/threshold/watchdog fields. Means: a healthy stand-in (keep "full" full), not `--no-embeddings`.
11. `test_w2_76_unchanged.py::test_two_full_rebuilds_of_the_same_tree_give_the_same_digest` — guards: two full rebuilds of
    one tree give the same digest, the same stores and compaction, and today's result keys remain. Its line on the
    semantic stage "as today" with no endpoint is what DEC-1027 C changed; keep the determinism point (healthy stand-in,
    or state why another means keeps it) and say in the Rewrite-Reason what the semantic line now asserts.
W2-116:
12. `test_w2_116_reindex.py::test_s5_guard_a_model_less_re_index_of_a_tree_keeps_its_vectors_and_reports_the_facet_unavailable`
    — guards: a model-less re-index keeps the earlier vectors (count unchanged) and reports the semantic facet not
    recreated with a reason. Means: read the refusal (`run`'s error details) — the vector-count assertion stays.
W1-41:
13. `test_w1_41_embedding_policy.py::test_the_rebuild_says_no_namespace_is_embedded[every-namespace-not-embedded-full]`
    — guards: a project with no embedded namespace rebuilds ok, the lexical index recreated, the stores' outcomes as for
    the project with one embedded namespace, and the semantic answer carries the words "no namespace is embedded".
    The `reference` (embedded) run is what fails now; under the Interface the semantic entries legitimately differ
    (`requested: false`). Keep: ok + exit 0 + lexical recreated + the words + every other store as the reference's.
Unit:
14. `tests/unit/rebuild/test_w2_116_integration.py::test_a_failed_build_never_moves_the_link_and_leaves_the_ready_half_as_it_was[endpoint fails]`
    — guards: a failed build never moves the link, the ready half unchanged, no warm-base record in the other half, and
    the semantic store reported `not_recreated`. Means: read the stores at the level integration puts them.
15. `…test_w2_116_integration.py::test_a_model_less_reindex_keeps_the_vectors_and_reports_the_facet_unavailable` —
    guards: model-less re-index keeps vectors (> 0, count unchanged), never asks the endpoint, reports semantic
    `not_recreated` with the warning as reason, search answers unavailable. Means: `pytest.raises(GovError)` and read
    `details["stores"]["semantic"]` (compare the status and reason; an added `requested` key is the Interface's).
16. `tests/unit/rebuild/test_no_embeddings.py::test_both_modes_say_where_no_namespace_is_embedded_and_nothing_else_changes[not embedded-mode0]`
    (and its siblings in the same parametrize if they share the cause) — guards (DEC-694): only exactly `embedded`
    embeds; the words stand beside the store's own answer; no path map gives no words. Under the Interface the
    not-embedded store says `requested: false` while the embedded one is asked; keep the words and "does not embed".
17. `tests/unit/rebuild/test_w2_122_seed.py::test_a_semantic_store_not_recreated_answers_as_before_and_leaves_no_record[unavailable-False]`
    (and its siblings `[part way|hung]-[False|True]`, same cause) — guards: a tree whose semantic store was not
    recreated keeps no warm-base record, is refused as a seed base, and nothing of its partial store is copied; the
    part-way store holds partial vectors. Means: `pytest.raises(GovError)` with `REBUILD_FAILED`, read the stores from
    its details; every no-record / refused / nothing-copied assertion stays.
18. `tests/unit/retrieval/test_w2_32_rebuild_cut.py::test_a_stage_not_built_still_names_the_cut` — guards: a semantic
    stage not built still names the cut. Means: read `details["stores"]["semantic"]` from the raised `GovError`.

(The counts in the ticket's run-2 list: W2-32 s2 5, s10 2, W2-13 4, W2-76 2, W2-116 1, W1-41 1, unit 5 = 20.)

## Check and commit

1. Run each of the 13 files whole (the pytest line above, one file per run) on your branch: every case must pass,
   and no case outside the list may change outcome. Quote each run's last line.
2. **Prove each revised case still guards** (the owner asks this of you and of the reviewer): for at least the W2-32 S2
   and S10 cases, cases 12, 14, 15 and 17, describe in one line per case the break that turns it red (e.g. "with the
   `_MISMATCH` code removed from stores.semantic the assertion at line N fails"). Where you can show it cheaply (a
   monkeypatch in a throwaway script under your TMPDIR, never committed, never in `src/`), do so and quote it.
3. Commit only the 13 files' changes, one commit:

       git commit -m "W2-124 P1-L (a): 20 earlier cases revised under DEC-1027 C, each keeping its guard" --trailer "Task: DAEO-mb2t" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1027 C" --trailer "Implements: DEC-1027, DEC-1015, DEC-1014, DEC-1083, DEC-530, DEC-954, DAEO-2ds6, DAEO-2bdu" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <the files you changed>

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, each file's last line, the commit hash with its trailers, `du -sh` of your TMPDIR. In
`tests`: a table, one row per revised case: node id | means used | what it still guards | the break that turns it red.
Also the refusals met.
