# Brief: independent test designer, W2-52 run 6, batch 2 (P-9 (a), the failing output after batch 1)

You are a fresh independent test designer (MR-3). Ticket: DAEO-siiz (W2-52, "The lite A7 and A10 stage records"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-52-tests` on branch `w2/W2-52-tests` (its head `6ef2e85129fe`), and you commit only there.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-siiz','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.
Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-siiz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-52-tests`, `w2/W2-52-tests`). If anything differs, stop and say so.

## Where things stand
W2-52's acceptance suite predates changes that reached the branch with the latest merge of `w2/integrate`; the product fails closed, the harness is behind. The previous batch (commit `d9028de120e7`, merged as `6ef2e85129fe`) put W2-52 in `_CBM_SUITES` of `tests/conftest.py` and made `EmbeddingStandIn` in `tests/acceptance/W2-52/w2_52_support.py` answer `GET /api/ps` (the device listing, DEC-1065). Run outside the sandbox by the lead, the suite is now **55 passed, 10 failed**, every failure the same:

```
AssertionError: stage A10 did not pass
gov adopt --lite --stage A10 --verdict audit/adoption/a10-verdict.md --json --session adopter-001
exit code: 1
{"ok": false, "command": "adopt", "result": {}, "session": "adopter-001", "error": {"code": "ADOPT_GATE_NOT_PASSED", "message": "gate A10 did not pass, recorded in governance/adoption/A10-independent-memory-verification.md: the canary of the semantic index: FACET_UNAVAILABLE: misses ['juniper lantern protocol sentinel'], no reason given; the semantic index is recreated", ...
stderr:
EMBEDDER_UNAVAILABLE: Ollama is unavailable: semantic retrieval is skipped and results are FTS-only.
```
The 10: `test_w2_52_a10_gate.py`: test_a10_passes_on_the_auditors_pass_and_is_recorded_as_its_own_stage, test_a10_writes_over_no_other_stages_record, test_a10_record_names_the_a8_record_and_the_auditor, test_a10_record_carries_the_digest_of_the_derived_state_rebuilt_from_git, test_a10_record_names_the_canary_of_each_index, test_a10_record_names_what_stays_for_wave_3, test_a10_record_gives_a_met_condition_a_verdict_can_carry; `test_w2_52_verdict_conditions.py`: test_the_a7_and_a10_records_each_give_a_condition_the_verdict_carries, test_a_verdict_reading_both_passing_records_can_be_healthy, test_the_conditions_say_where_they_come_from.

## The behaviour to restore (state, not a design)
Since the merge, `gov` embeds a **question** (a search, and so the semantic index's canary) with the **query embedder**, a server of its own at its own address: the public setting `GOV_QUERY_OLLAMA_HOST` (in `OLLAMA_HOST`'s form; default `127.0.0.1:11435`), separate from the shared one at `OLLAMA_HOST`, which builds the index. Under DEC-1065 (1) and DEC-1033 (2)(b) a question's vector is used only when that server reports the model on the GPU, and when the query server cannot be reached the semantic part is unavailable (never a CPU fallback). W2-52's harness points only `OLLAMA_HOST` at its stand-in, so the canary's question reaches no server.

Make the cases' environment also give the query embedder's address to a stand-in that answers as the shared one does (version, model list, device listing on the GPU, embed with the same deterministic vectors), so the questions and the chunks are embedded alike. Whether one stand-in serves both addresses or a second instance serves the query address is your choice; see how W2-54's support (`tests/acceptance/W2-54/w2_54_support.py`, `QUERY_HOST_SETTING`, and `test_w2_54_shared_gpu.py`) and W2-32's (`tests/acceptance/W2-32/`) give both addresses. Never let a case reach the machine's real servers at the default addresses: a case sets both settings explicitly, so a run's own environment never leaks into it.

**Lower no expectation:** no assertion is removed, weakened or skipped, no case deselected, no failure KPI loosened. If, with both addresses served, a case still fails for a reason that is not the harness (a product behaviour the KPIs contradict), do not edit it: name it and return a package.

## Rules
- Write only `tests/acceptance/W2-52/**`. Nothing else (not `tests/conftest.py` this time).
- **Policy 2 (c):** never read this ticket's implementation: the files `git diff --name-only w2/integrate...HEAD` names other than tests (`src/gov/adopt/lite_gates.py`, `src/gov/adopt/stages.py`, `src/gov/adopt/command.py`, the adopt skill). You may read the shared product code that is not this ticket's (for example `src/gov/retrieval/ollama.py`, `src/gov/retrieval/semantic.py`) to learn the public settings. **(d):** never read the hidden half of any evaluation set, or the held-out material's contents; never print a secret.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. (Here: for your runs in the tests worktree use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52-tests/src`; its `src/` is identical to W2-52's head.)
- **Memory first (DEC-836, DEC-963):** ask the integration store, never this ticket's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`, small batches (`--batch-size`, `--continue <token>`; DEC-860); code questions by small targeted traversals only (DEC-859). Then `cd` back to the tests worktree by its absolute path. Drop unread any result under `src/gov/adopt/lite_gates.py`, `stages.py`, `command.py` or the adopt skill, and name any such result you were served (P-R1).
- Inside the sandbox the code graph cannot index (`/tmp/gov-cbm-<uid>` read-only until W2-56), so the adopt stages stop at A3 there and you cannot see A10. Check your stand-in directly (start it, ask both addresses for version, tags, ps and an embed) and run the suite to its end once (never `-x`): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52-tests/src python3 -m pytest tests/acceptance/W2-52 -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed`; quote the counts. The lead runs it outside the sandbox.
- Scratch: 2 GB and 100,000 files for you, outside the tracked tree, in your sandbox's temp folder; leave nothing in the tree.
- No subagents that write; no here-documents, backticks or `bash -c` scripts; write files with Write and Edit and literal paths. Run everything in the foreground; return only after your commit exists.
- No `git checkout` of another commit, reset, clean, amend, rebase, merge, push or tag. Never copy the repository or a folder of it. No search starting at the repository root, `governance/project/` or `.claude/` (DEC-849): search named folders; a read refusal is taken, never retried in another spelling, and counted in your return. Never read `~/.claude/`, never write `~/gov-os-workbench`.
- Under `.gov-runtime/` write commit hashes as 12 digits, never 40 (row W2-L423's rule).
- Install nothing (a needed tool is a P1 in your return). Nobody runs `gov close`, `gov adopt` (outside your tests' temporary repositories), `gov pause` or `gov rebuild --no-embeddings`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). On 401/403/"Failed to authenticate": stop, status AUTH_REQUIRED.

## Commit
The git hooks are uninstalled; never `--no-verify` or `core.hooksPath`. One commit, your paths only:

    git commit -m "W2-52 (DAEO-siiz): the harness gives the query embedder's address to the stand-in (GOV_QUERY_OLLAMA_HOST)" --trailer "Task: DAEO-siiz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-741, DEC-1065, DEC-1033, DEC-1112" --trailer "Rewrite-Reason: DEC-1065, DEC-1033" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`. Update the README's run notes in the same commit if they name the embedder's address.

## Return
Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in it: the sandbox check; your commit's 12-digit hash and `git show --stat`; your direct check of the stand-in; the suite counts and reasons; the `gov.__file__` line; that no expectation was lowered (and how you checked); `gov retrieve` use; read refusals; anything you could not do.

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

Refused twice for the same call: stop and say so.
