# Brief: independent auditor (STANDARD review), DAEO-mb2t (W2-124), class C2 — one review round, read-only

Budget: projection 6 USD. Keep your context short: read what each check needs; cut long outputs to head and tail.

You are a fresh independent auditor, read-only, for ticket DAEO-mb2t (W2-124). You probe head `7a3aecb38fb5` of
`w2/W2-124` in `/home/usain/gov-os-worktrees/W2-124`. You write nothing in any repository; every file you make (probe
scripts, copies, planted projects) lives under your sandbox's TMPDIR (outside the repository and outside
`~/gov-os-runs`; check `echo $TMPDIR`). Your read-only probes are allowed at any hour, by Bash into your own TMPDIR
(DEC-1144 (7)).

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-124/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-mb2t`. If it fails, stop and return. Then read `EMG-common.md` beside it (its auditor paragraph applies).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-mb2t`) and
  `git -C /home/usain/gov-os-worktrees/W2-124 rev-parse HEAD` (expect the head above; if it differs, say so and probe
  the head above by `git show`/`git worktree` copies in your TMPDIR only).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-mb2t.md`: KPI lines S1-S5, F1, F2, the
  `## Interface`, run 1's P2 and P3, and **"P1-L decided"** (all binding). The register
  (`docs/DECISION_REGISTER.md`): grep only by id (`### DEC-1027`, `### DEC-1015`, `### DEC-1150`, `### DEC-954`).
- The ticket's whole change: `git -C /home/usain/gov-os-worktrees/W2-124 diff w2/integrate 7a3aecb38fb5` (28 files):
  code in `src/gov/rebuild/command.py`, `src/gov/adopt/stages.py`, `src/gov/close/rebuild_gate.py`; its own tests in
  `tests/acceptance/W2-124/`, `tests/unit/rebuild/test_w2_124_*.py`, `tests/unit/adopt/test_w2_124_*.py`; and the 13
  earlier files revised under P1-L (a) in commit `bb6a068bd` (merged at `08b4cd8fb`).
- Any pytest you run goes through the heavy slot, in this form:
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=<your TMPDIR>/empty-home PYTHONPATH=<the tree or your copy>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <node ids> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  Note: `tests/conftest.py` collects only one representative per parametrization unless the node id is named: name
  node ids. A resource gate's refusal is a wait, not a refusal (DEC-1146). The lead has already run the full suites;
  do not re-run whole folders (DEC-959 item 1): run what a probe needs.
- No `gov retrieve` or `gov context`; search with Read and Grep, and once more in other words if needed (DEC-1065).
  No test or probe starts a real embedder or model; stand-ins only. No here-document, no `bash -c`; scripts as files in
  your TMPDIR. Foreground only. No reset, checkout, clean, commit, push, merge or install in any tree.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). On an authentication error return `AUTH_REQUIRED`.

## What to check

### A. The KPI lines (S1-S5, F1, F2) against the code and its own tests
For each line: trace it to its tests and the code; probe it with a planted case of your own where cheap (a stand-in
embedder that is unavailable, one that hangs, one that fails part way; a project with no path map and one with no
embedded namespace; an adoption run to A6 with the embedder unavailable; a planted rebuild result through
`gov.close.rebuild_gate` and, if the sandbox lets it run, `rebuild_slot.sh` with `GOV_REBUILD_PYTHON` pointing at a
stand-in that prints the envelope, expecting exit 75). F1 above all: no ok answer and no close/prepare pass over a
partial semantic store.

### B. The 20 revised earlier cases (the owner's own check, DEC-1150 (3)) — blocking
The owner's rule: each revised case gets `--no-embeddings`, a healthy stand-in embedder, or reads
`error.details.stores` where it checks a refusal; **each keeps what it was guarding**; nothing else in the files
changes. **Check case by case that no revised case loses its point**: its assertion must still fail on the behaviour
it guarded against. For each case, a probe that breaks the guarded behaviour must turn the revised case red. Do it by
running the case against a broken copy: `git -C /home/usain/gov-os-worktrees/W2-124 worktree add` is a write, so instead
copy the tree's `src/` and the needed `tests/` into your TMPDIR (`cp -r`) or use a throwaway pytest plugin / monkeypatch
module under your TMPDIR loaded with `-p`, and break one behaviour at a time (e.g. the pin check no longer refuses a
mismatched revision; vectors written on the CPU; the lexical index not built; the link moved on a failed build; a
warm-base record left; the cut dropped; the canary indexed). Name any revised case that stays green under the break
of its own guard as a **blocking** finding. Also check `git diff 1f9bd6d90 bb6a068bd`: no case outside the list
below changed, nothing was weakened (an assertion dropped, a bound widened), and each change carries its
`Rewrite-Reason`.

The cases (the designer's per-case "means" and "break" claims are in its return; verify, do not trust):
1. W2-32 `test_w2_32_s2_fail_closed.py::test_an_endpoint_reporting_another_revision_of_the_pinned_model_fails_closed_at_rebuild` — mismatch refused, `…_MISMATCH`, nothing embedded, no vector.
2. `…::test_a_configured_model_without_a_revision_fails_closed_at_rebuild[no-revision|empty-revision|null-revision]` — `…_UNPINNED`, nothing embedded.
3. `…::test_a_pinned_model_the_endpoint_does_not_list_fails_closed_at_rebuild` — a code and the pinned model named; no other model asked.
4. `test_w2_32_s10_no_cpu_fallback.py::test_a_rebuild_with_the_embedder_unreachable_refuses_the_vectors_and_starts_nothing` — refused with a code; lexical recreated; no vector; nothing started.
5. `…::test_a_rebuild_with_the_embedder_on_the_cpu_refuses_to_embed` — refused with a code; no vector; no cache row; nothing started.
6. `tests/acceptance/W2-13/test_w2_13_secrets.py::test_a_second_rebuild_answered_from_the_secrets_cache_indexes_the_canary_no_more` — the canary never indexed; the clean file found.
7. `test_w2_13_unavailable.py::test_a_search_of_an_unusable_index_answers_unavailable_and_never_raises[stale]` — unavailable, never raises.
8. `…::test_gov_retrieve_on_an_unusable_index_answers_without_a_traceback[stale]` — no traceback.
9. `test_w2_13_latency.py::test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget` (local_only; the lead ran it outside the sandbox, see below) — budget unchanged.
10. `tests/acceptance/W2-76/test_w2_76_timings.py::test_every_stage_timed_in_output_and_record[full]` — a *full* rebuild times every stage (stand-in embedder added).
11. `test_w2_76_unchanged.py::test_two_full_rebuilds_of_the_same_tree_give_the_same_digest` — determinism of digest, stores, compaction; its semantic line changed from `not_recreated` to `recreated` (judge whether that keeps its point).
12. `tests/acceptance/W2-116/test_w2_116_reindex.py::test_s5_guard_a_model_less_re_index_of_a_tree_keeps_its_vectors_and_reports_the_facet_unavailable` — vectors kept; semantic not recreated with a reason.
13. `tests/acceptance/W1-41/test_w1_41_embedding_policy.py::test_the_rebuild_says_no_namespace_is_embedded[every-namespace-not-embedded-full]` — ok, exit 0, lexical recreated, the words, stores as the reference's (now compared over the stores the refused reference built: judge whether that loses the point).
14. `tests/unit/rebuild/test_w2_116_integration.py::test_a_failed_build_never_moves_the_link_and_leaves_the_ready_half_as_it_was[endpoint fails]` (and `[model-less]`) — link not moved, ready half unchanged, no warm-base record, semantic `not_recreated`.
15. `…::test_a_model_less_reindex_keeps_the_vectors_and_reports_the_facet_unavailable` — vectors kept, endpoint never asked, reason, search unavailable.
16. `tests/unit/rebuild/test_no_embeddings.py::test_both_modes_say_where_no_namespace_is_embedded_and_nothing_else_changes` (6 rows) — only exactly `embedded` embeds; the words; no path map, no words.
17. `tests/unit/rebuild/test_w2_122_seed.py::test_a_semantic_store_not_recreated_answers_as_before_and_leaves_no_record` (6 rows) — no record, refused as a seed base, nothing copied, partial vectors on the part-way row.
18. `tests/unit/retrieval/test_w2_32_rebuild_cut.py::test_a_stage_not_built_still_names_the_cut` — the cut named.

### C. Commits
Each commit of the ticket (`git log --format='%h %s%n%b' w2/integrate..7a3aecb38fb5`, the ticket's own, not the
integrate merges): `Task: DAEO-mb2t`, a `Role:` matching the paths, `Implements:` within the ticket's `sources:`; the
designer's commit carries `Rewrite-Reason: DEC-1027 C`; every path within the ticket's `allowed_paths`.

## Verdict

PASS only if every KPI line holds, no revised case loses its point, and no blocking finding stands. Each finding:
id, severity (blocking / high / low), what was done, what happened, what should have happened, the KPI line or case
number. End your return with a fenced verdict block:

```verdict
ticket: DAEO-mb2t
head: <the full head you probed>
verdict: PASS | FAIL
blocking: <ids or none>
findings: <ids with severity, or none>
revised_cases_checked: <n of 20 rows run against a break> / <n stated only>
```

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` DONE (the review ran, whatever the verdict), ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED. In
`evidence`: the sandbox check, the head, each probe's command and last line. In `tests`: a table, one row per revised
case: case | break applied (or "stated") | red under the break: yes/no. Then the findings, then the verdict block.
Also the refusals met.
