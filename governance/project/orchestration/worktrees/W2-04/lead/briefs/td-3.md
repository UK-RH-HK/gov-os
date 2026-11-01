# Brief: independent test designer, DAEO-u4oz (W2-04), profile FULL, round 2 (revision batch)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-04-tests` on branch `w2/W2-04-tests`, whose head is the run-1 test designer's commit `d2ff95b28a2e` (the ticket's base plus `tests/acceptance/W2-04/`; it holds none of this ticket's implementation). You never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-04`). You revise acceptance tests from the specification and its addendum below, in parallel with an engineer, and you show them red on your tree's base.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-u4oz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` and `git rev-parse --short=12 HEAD` (expect `/home/usain/gov-os-worktrees/W2-04-tests`, `w2/W2-04-tests` and `d2ff95b28a2e`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return. Your tests call the code of the tree they run in (a child process with that tree's `src/` on `PYTHONPATH`, as the run-1 suite's `w2_04_support.py` does), so that once merged into the ticket's worktree they exercise its code.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, **only from the integration branch's store:** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store or files. For what changed on `w2/integrate` since that store's refresh, read `git show w2/integrate:<path>`. **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`), and name in your return any such result you were served (DEC-820 (c)). You may read those files **as they stand on `w2/integrate`** or in your own tree (`git show w2/integrate:<path>`): that is the existing code, not this ticket's work.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, the files `git diff --name-only d2ff95b28a2e w2/W2-04` names outside `tests/acceptance/`, on branch `w2/W2-04` or in `/home/usain/gov-os-worktrees/W2-04` (commit `c5b771c61ada` and anything after it there is the engineer's); (d) the hidden half of any evaluation set. Writes stay inside the paths named under "What you write", in this worktree.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file in your session's own scratchpad (the Write tool may refuse `.gov-runtime/scratch/` folders) and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one from scratch (`tmp_path`). No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in copies single named files, never `governance/project/`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` and the untracked dotfiles at the top (`.bashrc`, `.idea`, …) show as placeholder device files: conclude nothing from them and never commit them.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 5 GB and 250,000 files and folders, outside the tracked tree. Keep the sandbox's own `TMPDIR` (do not set it yourself; if a `pytest-of-*` folder appears in the worktree, say so). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed (a removal the guard asks approval for: leave it and name the folder).
- Run everything in the foreground, one command after another; return only after your commits exist. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the register or plan files. Never run `gov close`, `gov adopt` or `gov pause`; never `gov rebuild --no-embeddings`.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## Why this batch (the CTO's decision, DEC-1005, delegated)

Run 1's suite (`tests/acceptance/W2-04/`, 56 cases) and the build met. Two decisions followed:
- **P-W2-04-2 (A):** the supplementary block stays semantic-free (deterministic lexical evidence only), and one batch is one of the context's own lookups, shown in the new packet key `supplementary_batches` (the addendum's S7a). That settles the run-1 suite's own P-1: "one batch" is **not** one call of `gov.retrieval.retrieve.retrieve`; the context no longer reaches that entry, so a stand-in hooked there sees nothing.
- **P-W2-04-3 (b):** a dependency ticket counts by its front matter (id, status, title, KPI lines), as CAP-15.b asks (the addendum's S1).

Your run-1 P-2 (a reproduced refusal) and P-3 (items left for lack of room) were decided by the lead as you recommended: the same `CONTEXT_OVER_CEILING` refusal in both of the check's computations is reproduced and named (a `REFUSED:` line), any other difference or error stays red; items left for lack of room are listed in `dropped` (reason "budget exceeded") and also named in `further_batch`. P-4 (W2-M133) is a split outside this ticket: no case.

## What you read

- The ticket file `.tickets/DAEO-u4oz.md` (read-only): its KPI lines and failure line; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-04`).
- The sources: CAP-15, CAP-15.b, CAP-15.d (`docs/contract/CONTRACT_v4.md`); DEC-860, DEC-860's batches; DEC-491 and DEC-866 (rewrites carry `Rewrite-Reason`, no other expectation lowered); DEC-768 (the dropped list's one order).
- The run-1 suite in your tree, `tests/acceptance/W2-04/` (yours to revise), its README and its packages.
- The earlier suites you revise: `tests/acceptance/W2-54/` (its README, `w2_54_support.py`, `test_w2_54_dropped_order.py`, `test_w2_54_cpu_embedder.py`, `test_w2_54_query_cache.py`, `test_w2_54_query_vector.py`) and `tests/acceptance/W1-41/` (`test_w1_41_external_references.py`, its README); the decisions those suites test (W2-54's: the dropped list's one order and the reproducibility of the context check, DEC-768; its CPU embedder, query cache and query vector cases; W1-41's: external references add nothing to a packet).
- `gov retrieve --json` and its options as they stand on `w2/integrate` (`src/gov/retrieve/`, `src/gov/retrieval/retrieve.py`): the steps that move to `gov retrieve` use its public command.

{{SPEC}}

## The work, case by case

Revise only what is listed; lower no expectation; each revised case keeps the behaviour it guarded, observed now where the addendum puts it.

**A. W2-54's 17 cases** (`tests/acceptance/W2-54/`). On the build they fail for this ticket's reasons, not theirs:
1. `test_w2_54_dropped_order.py`, 14 cases: `test_the_stand_in_reaches_the_retrieval_s_public_entry_with_tied_and_same_id_items`, `test_two_computations_with_the_retrieval_s_own_order_give_one_packet`, `test_every_order_of_the_retrieval_s_items_gives_the_same_packet_and_hash[reverse|rotate|shuffle]`, `test_a_budget_below_the_mandatory_inputs_gives_the_same_packet_under_any_order`, `test_nothing_is_dropped_or_added_every_item_stays_in_the_packet_once[identity|reverse]`, `test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing`, `test_an_empty_retrieval_result_gives_one_packet`, `test_a_store_whose_index_is_missing_gives_one_packet_under_any_order[TK-W254-BIG]`, `test_the_check_is_green_when_two_computations_see_two_orders`, `test_a_context_whose_items_differ_still_fails_the_check_naming_the_ticket`, `test_the_check_names_only_the_ticket_whose_context_differs`. Three changes, as decided:
   - **the hook to what the packet shows:** the stand-in that hooked `gov.retrieval.retrieve.retrieve` (to see and to reorder the retrieval's items) is re-pointed to what the packet itself shows: its `supplementary`, `dropped`, `further_batch` and `supplementary_batches`. The premises "the stand-in saw tied and same-id items", "two computations saw two orders" and "the items differ" are re-established through the packet and the planted evidence (for example by planting the ties and same-id items in the project, or by varying the order in which the project's files, the store or the process give them), never by reaching into the code under test. If a case's behaviour (for example "two computations seeing two different orders") can no longer be produced from outside, say so for that case in the README and in your return, with what it now guards instead; never drop the case silently.
   - **TK-W254-BIG's budget:** TK-W254-BIG's mandatory inputs (about 25,000 to 36,000 tokens) now refuse at the default ceiling of 6,000 (S2). Its cases that need a packet give it a budget (`--budget N`, or `budget=` in process) that its mandatory inputs fit under with room for supplementary items, chosen from the packet's own figures as your run-1 lessons say, so that they still test dropping under pressure.
   - **the over-ceiling case:** `test_a_budget_below_the_mandatory_inputs_gives_the_same_packet_under_any_order` now expects the refusal: `ok: false`, `CONTEXT_OVER_CEILING`, a non-zero exit, the same refusal under any order.
   - The check cases (`…check_is_green…`, `…items_differ…fails_the_check…`, `…names_only_the_ticket…`) keep their point: green when two computations agree, red naming the ticket when a context differs; a reproduced `CONTEXT_OVER_CEILING` refusal is a `REFUSED:` line, not green evidence that two different contexts agreed.
2. `test_w2_54_cpu_embedder.py::test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner`, `test_w2_54_query_cache.py::test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state`, `test_w2_54_query_vector.py::test_the_context_check_is_green_over_several_tickets_with_an_embedder_whose_vectors_vary`: their premise is that `gov context` sends text to the embedder; under the addendum it sends none. **Their embedder steps move to `gov retrieve`** (the read that does reach the semantic route): the CPU-embedder case asks its questions through `gov retrieve` and still shows every read goes to the CPU embedder and nothing to the shared runner; the query-cache case shows one question gets one answer whatever the cache's state through `gov retrieve`, and keeps its packet-hash part for `gov context` (one ticket, one packet hash, whatever the cache's state); the query-vector case shows the varying vectors through `gov retrieve` and keeps the context check green over several tickets. A case may also assert, where it adds a guarantee, that `gov context` sent the embedder nothing.
3. Do **not** revise `test_w2_54_green_here.py`, `test_w2_54_time_limit.py` (red only for a missing store in the ticket's worktree; the lead rebuilds) or `test_w2_54_sandboxed_worker.py` (red on the base, another ticket's).

**B. W1-41's 2 cases** (`tests/acceptance/W1-41/test_w1_41_external_references.py`):
- `test_an_external_reference_adds_nothing_to_the_packets_tokens`: the equality now holds **without `ticket_text`**: the ticket's own text (which holds the reference) is counted whole (S1), so compare the packets' tokens less their `ticket_text`'s tokens (counted as S1 counts them), or an equivalent that keeps "an external reference adds no read content".
- `test_a_project_without_the_file_gives_the_packet_it_gave_before`: its expected key set gains the new keys the addendum names (`ticket_text`, `supplementary_query`, `further_batch`, `supplementary_batches`). The CTO's text says "the three new keys", written before `supplementary_batches` was added in the same decision: use the four, and say so in your return. Everything else it compares stays.

**C. This ticket's own 4 cases, with P-1 re-read** (`tests/acceptance/W2-04/`):
- `test_w2_04_batches.py::test_when_room_is_left_after_one_batch_the_next_batch_is_taken` and `::test_further_batch_is_at_most_one_batch_long`: observed through `supplementary_batches` (S7a): more than one entry when the evidence passes one batch and the room holds it; the stacked items a prefix of the batches' items in order; `further_batch` beginning with the first unstacked ranked item, holding no stacked item, and no longer than the largest `limit`.
- `test_w2_04_reproducible.py::test_tied_items_keep_one_order_whatever_order_the_retrieval_gives_them`: ties in `path` then `id` order, whatever order the store, the index or the process gives them, produced from outside (planted files in differing creation orders, separate processes, `PYTHONHASHSEED`, two stores), not by a stand-in at the retrieval's entry.
- `test_w2_04_reproducible.py::test_the_packet_is_the_same_whether_or_not_the_semantic_route_answers`: its premise moves to `gov retrieve` (with your semantic stand-in live, `gov retrieve` does find the semantic-only note), and the packet's hash is the same with that stand-in live and with the semantic route unavailable, and the semantic-only note never enters the packet.
- Re-read S1 as amended against the rest of your suite: a case whose planted dependency tickets are counted whole is revised to the front-matter counting, and add **one** case for S1's amendment (a dependency ticket with a very large body still fits; a change to a dependency's body alone leaves `tokens` unchanged). Add one case for `supplementary_batches`' presence and form if no revised case already covers it. Update the README's map and red reasons.

## What you write

- Only `tests/acceptance/W2-04/**`, and the files named in A and B (`tests/acceptance/W2-54/test_w2_54_dropped_order.py`, `test_w2_54_cpu_embedder.py`, `test_w2_54_query_cache.py`, `test_w2_54_query_vector.py`, `tests/acceptance/W2-54/w2_54_support.py` and `README.md` if they must change for these cases; `tests/acceptance/W1-41/test_w1_41_external_references.py`, its `README.md` if it must change). Nothing else; no conftest outside these folders. If a needed change falls outside them, return it as a package.
- Behaviour through public interfaces, never internals; deterministic, no network; each child-process call with a time limit; temporary repositories.
- No expectation lowered: a revised case asserts at least what it did, observed where the addendum puts it. Name every revised case with its reason in the README of its folder.
- **Red on your base:** run each changed folder to its end (never `-x`), `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src python3 -m pytest tests/acceptance/W2-04 tests/acceptance/W1-41 tests/acceptance/W2-54/test_w2_54_dropped_order.py tests/acceptance/W2-54/test_w2_54_cpu_embedder.py tests/acceptance/W2-54/test_w2_54_query_cache.py tests/acceptance/W2-54/test_w2_54_query_vector.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`; report the counts and, for each failing group, its reason on the base (for example "no `supplementary_batches` key", "no `CONTEXT_OVER_CEILING`"), and that none fails for a defect of the test itself.
- An ambiguous point or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

One commit per revised earlier-ticket test file (each `tests/acceptance/W2-54/…` and `tests/acceptance/W1-41/…` file in a commit of its own, a support or README file of that folder with the case it serves), and one commit for `tests/acceptance/W2-04/`. **Every one of these commits carries `Rewrite-Reason: W2-04's KPIs 2 and 4 (CAP-15.d, DEC-860), DEC-1005`**, with the trailers in the final block:

    git commit -m "W2-04: <the file>: <what changed> (independent test designer)" --trailer "Task: DAEO-u4oz" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-15.d, DEC-860" --trailer "Rewrite-Reason: W2-04's KPIs 2 and 4 (CAP-15.d, DEC-860), DEC-1005" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After each commit, show `git log --oneline -3` and `git status --short`.

## Return

Your commits' hashes (12 digits) and what each changed; the cases revised and added, each with what it now guards; any case whose old premise cannot be produced from outside any more, with what it guards instead; the red result as you saw it (counts and the reason per group); the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; any P-R1 result you were served; any package.

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Right after the twelve fields: a section `guard_refusals:` (one line per refusal: time | command form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and a section `brief_gaps:` (one line per thing you had to discover that this brief did not tell you: what | where it belonged | minutes), or `brief_gaps: none`. Refused twice for the same call: stop and say so.
