---
type: probe
task: DAEO-2bdu
round: 2
reviewer_session: c56e1745-57dd-42fb-bece-ed52b319a502
implementer_session: dab23ba0-5ebf-4d2b-ad86-7864ac080286 (eng-2, run 4's fix); 18a2ad97-3f9c-46b2-8b10-5f13aa084636 (eng-3, L-1)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 15ad055adbb5d12abe4ecdf83344c7f504315d01
decisions_applied: [DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1112, DEC-1144, DEC-1157, DEC-1150]
---

# Probe record: W2-88 (DAEO-2bdu), review round 2 of 2, the last (DEC-1010): FAIL

## The lead's judgement and triage

- **Who probed.** A fresh, read-only Independent Auditor session (`c56e1745-57dd-42fb-bece-ed52b319a502`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-13. Step 0 held (the write outside the tree failed with a read-only file system; the index refresh worked). The head was 15ad055adbb5 and `git status --porcelain` was empty at start and end. Its tripwire shows no change in this ticket's trees.
- **Refusals the reviewer met, once, not retried:** one Write of a probe script into its own TMPDIR (the auditor's tool list holds no Write; expected).
- **The lead's verification at the head** (outside the sandbox): `gov accept W2-88`: outcome pass, every KPI line pass, 204 passed, 0 failed, 0 skipped (`.gov-runtime/scratch/lead/log/accept-4.txt`). lead_verify (scoped, DEC-968): RED, parallel 6,237 tests, 9 failed, 8 skipped; serial 3 passed (`.gov-runtime/scratch/lead/log/verify/parallel.xml`, `serial.xml`). The 9: (i) four cases (W2-02 `test_core_schema_is_green_on_this_repository`, W1-08 `test_the_probe_schema_accepts_this_repository_s_probe_records`, W1-26 `test_this_repository_s_probe_records_are_well_formed` and `test_no_finding_of_the_check_on_this_repository_names_a_probe_record`) are this branch's: round 1's probe record lacked `implementer_session` (probe.schema.json requires it); fixed in the commit that adds this record, and this record carries it; (ii) `tests/acceptance/W2-124/test_w2_124_s1_semantic_fails_named.py::test_s1_hung_or_transient_failing_embedder_raises_rebuild_failed_semantic[hung]` took 61.8 s against 60 s under the full run's load; alone: 2 passed in 53 s (load-sensitive); (iii) three cases of `tests/unit/orchestration/test_cto_safety_nets.py` read the live CTO inbox (2 unread items at 12:01) and passed alone (15 passed): environment-dependent, not this branch's (the CTO's, DEC-1156 (7)); (iv) `tests/acceptance/W2-23/test_w2_23_space.py:94` (`context_watch.py` not in the settings' hook lines), red on the integrate tree in round 1 too: integrate's, not this branch's.
- **The verdict stands as FAIL** (never decided away; this was the last round, there is no third, DEC-1010). All three round-1 blockers (RV1-1, RV1-2, RV1-3), the five minors (RV1-4 to RV1-8) and the package items (RV1-9 to RV1-11) are fixed and probed; L-1 is built and probed. The triage of the new findings:

| finding | severity | triage | the fix, as a described behaviour for the test designer (DEC-136) |
|---|---|---|---|
| RV2-1 a refused or interrupted A9 throws away work done in the repository while it ran (`fabric.undo` → `project.restore` = `git reset --hard <head>`, `fabric.py:218-226`, `project.py:110-125`; reached on any exception after the copy step, `fabric.py:564-569`) | blocker | to the owner with options (the last round: no third review; an owner-decided fix gets a narrow independent check). Lead's recommendation: (a) fix, within the ticket's paths (`fabric.py` only; `project.restore`, W2-23's, unchanged) | when A9 refuses or is interrupted after installing the kernel files, it unstages only the paths it staged and deletes only the files it wrote whose bytes are still the ones it wrote (and the empty folders it made); a tracked file edited during the run keeps its edit; a file staged during the run stays staged; if HEAD moved during the run, A9 refuses without resetting, names the new commit and leaves the branch where it is |
| RV2-2 `PLAN.md`'s first unscanned path sits on the heading's line (`refactor_plan.py:172-178`) | minor | fix with RV2-1 (one line) | the unscanned paths form a list starting on the line after `Unscanned paths:`, each `- \`path\`` at the start of a line |

The reviewer's review follows, unchanged.

# W2-88 (DAEO-2bdu): review round 2
probed_commit: 15ad055adbb5d12abe4ecdf83344c7f504315d01
round_1: 5b41893beb79

## Sandbox and identity
- **Step 0 (a):** writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `OSError: [Errno 30] Read-only file system`, as it should.
- **Step 0 (b):** `echo sandbox-trial | git hash-object -w --stdin` printed `1ae28402…` (exit 0) and `git update-index --refresh` exited 0. That loose object in the shared `.git` is the one write the launcher requires.
- **Identity:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`.
- **Head and status:** head `15ad055adbb5d12abe4ecdf83344c7f504315d01` with `status --porcelain` empty, both at start and at end.
- **Model processes:** `ps … [o]llama|[l]lama-server` showed nothing at the end.
- **Refusals met, each once, not retried:** one Write of a probe script into my own TMPDIR (permission not granted). I used short Bash commands instead.

## Round 1's findings
| finding | state | file:line | how I probed it |
|---|---|---|---|
| RV1-1 tuned pool is no departure | **fixed** | `src/gov/adopt/fabric.py:84-101` (`settings_of`, `departures`), `:122-138` (`read_standard`) | In process, `departures` named `pool` with its value for: route_depth 5, a missing key, an added key, no block, and meaning_uncut false. The shipped block, and the same block with 60.0 for 60, gave `[]`. On a planted repository that tracks a `retrieval.yaml` with route_depth 5: no decision → `STANDARD_DEPARTURE ['pool']`; `DEC-1:reranker` → still `STANDARD_DEPARTURE ['pool']`; `DEC-1:pool` or `DEC-1` → ok, with `decision: DEC-1` on the departure. |
| RV1-2 an unavailable scan recorded as one | **fixed** | `fabric.py:410-451` (`vector_scan`, `_scan`, `scale`), `:454-464` (`over`) | `scale` on a folder with no store gave `vector_scan_ms` None, reason `missing`, `over` []. A replaced seam answering `available: 'true'` (a string) → None. Answering None → None, with a reason. Raising → None, `ZeroDivisionError`. Answering `available: True` after 50 ms against a 10 ms budget → 53.3, and `over` named the scan. Route times are recorded and never compared with the budget. |
| RV1-3 without gitleaks the plan says "no secret" | **fixed** | `src/gov/adopt/assess.py:133-154,320-354`; `refactor_plan.py:134-189`; `stages.py:84-93` | Planted repository with a github-pat line, a 2 MiB binary, and `.vue`/`.ps1`/`.proto` files. With gitleaks: exit 0, proposals `over-limit` and `secret`. With `PATH=/usr/bin:/bin`: exit 1, `SECRETS_UNSCANNED (gitleaks is not on PATH)`; `PLAN.md` holds `secrets: not scanned (gitleaks is not on PATH)` and `Unscanned paths: all 6 tracked files`; no `NOTHING-TO-REFACTOR.md`; the earlier run's stale `RP-02-secret.md` was removed. The hash of the files (including `.git`), `ls-files -s`, `for-each-ref` and `log --all` was identical before and after. A grep of the outputs, stdout and stderr for the secret's value: 0 hits. A 17 MiB text blob with gitleaks gave `SECRETS_UNSCANNED (1 blob(s) over 16777216 bytes …)` and named the blob. The same repository without the blob gave exit 0 and `NOTHING-TO-REFACTOR.md`. |
| RV1-4 binaries refused while the store holds them | **fixed** | `fabric.py:346-347,388-393` | Code read: a state-1 file is always indexed and named in `binary_held`, and `binary` stays only for a binary the store did not take. The stand-in proof's legacy-docs shows `binary_held` 2 with lexical 29/29 and 0 refused. |
| RV1-5 code graph lists, swallowed read error | **fixed** | `fabric.py:369-388`, `:251-256,268-269` | Code read: a suffix outside `CODE_GRAPH_SUFFIXES` is refused `unsupported-language` before the staging check. A failed `_graph` gives `built: false, error`, and `check_coverage` then puts `codegraph` in `not_built` with the error in the message. |
| RV1-6 a load re-stamps a stale store | **fixed** | `src/gov/store/loader.py:679-690,704,718-719` | Planted an unstamped store whose `lexical_chunk` lacks `parent_id`. `connect` gave `STORE_LAYOUT_STALE {found: 0}` both before and after `loader.load`. |
| RV1-7 the evidence calls an unrun scan a scan time | **fixed** | `docs/changes/W2-88-evidence.md:247-251,283,294,305,316,327` | Each stand-in section says "no vector scan was measured (`vector_scan_ms` null; reason: missing)", and the results file agrees (legacy-docs: None, `missing`). |
| RV1-8 the no-route rule stated differs from the code | **fixed** | `assess.py:9-15` (module text), `:66-67`, `:329-330`; evidence `:205-210` | The planted `.vue`, `.ps1` and `.proto` files were each in `no_route` as `unsupported-language`. |
| RV1-9 = B-1.1 no copy of the kernel skills | **fixed** (but see RV2-1) | `fabric.py:46-49,153-226,555-569` | All four sources hold the decided lines: retrieval skill, T-0 and T-8 each 1/1/1/1 for the four phrases; the discovery skill holds W2-142 S2's line (td-4's decided revision). The real run records `installed` 5 on all four finished repositories. |
| RV1-10 = B-1.2 the loader refuses `rerank:`/`bundle:` | **fixed** as decided | `fabric.py:69-111` | `check_keys` gives `CONFIG_INVALID {keys: [rerank]}` and `{keys: [bundle]}`. With the constants patched (MODEL `Org/Other`, SOCKET `private.sock`, BUNDLE_BUDGET 4000), `departures` names `reranker`, `reranker_service` (`.cache/gov-os/private.sock`) and `bundle_tokens`. |
| RV1-11 = B-1.3 no `retrieval.yaml` installed | **fixed** | `fabric.py:130-132,183-186` | With no tracked file, Gov OS's copy is the file in force and the one installed. The real run on four repositories: departures 0, `retrieval_yaml_sha256` `53970c0c…`, `kept: []`. |

## What I probed and found sound
1. **Scope.** There are 7 first-parent non-merge commits since 7bcd84765.
   - Every file they change is in `allowed_paths`: `assess.py`, `fabric.py`, `refactor_plan.py`, `stages.py`, `store/loader.py`, `tests/unit/adopt/test_w2_88*`, `docs/changes/W2-88-evidence.md`.
   - Each carries `Task: DAEO-2bdu`.
   - Each `Implements:` lists only ids from `sources:`. The lead's c13c0d2bb (`Role: orchestrator`, evidence only) lists the whole `sources:` list.
   - `close/`, `guard/install.py` and `W2-145-evidence.md` came with the `w2/integrate` merge (b1fe858ac): not the ticket's changes.
2. **L-1a (S1, S2).** On my planted repository the 2 MiB binary is in `binary` and in `no_route` as `over-limit`, and `RP-01-over-limit.md`'s `allowed_paths` is `assets/big.bin`. The stand-in proof's legacy-docs gives `no_route` 2 (over-limit), plan 1 (`over-limit`). The real run's pre-L-1 legacy-docs output has `NOTHING-TO-REFACTOR.md` and 17 s, as the evidence says.
3. **L-1b.** On the planted repository `estimate.chunks` is 1,947 (= ⌈2,097,153/1,080⌉ = 1,942, plus 5 one-chunk files) and `index_seconds` is 78 (1,947 × 0.04 plus 2 code files × 0.061). `CHUNK_STEP` is 1,200 − 120 (`chunking.py:23-24`). `EMBED_S_PER_CHUNK` states its source (`assess.py:51-54`).
4. **No fail-open in the scan.** A gitleaks exit code other than 0 or leaks raises `ASSESS_SCAN_FAILED` (`assess.py:194-195`). A timeout raises too. Unreadable rules give `SECRETS_UNSCANNED` with their reason.
5. **The plan clears stale files.** `refactor_plan.py:155-156` removes old `RP-*`, `PLAN.md` and `NOTHING-TO-REFACTOR.md` before writing, so a repeated MA leaves no contradiction (probed: RP-02 removed). A9 likewise removes a stale `SCALE-PROPOSAL.md` (`fabric.py:596-597`).
6. **Coverage still fails closed.** The lexical store is judged against every tracked file, including the copies and files outside the path map (`fabric.py:356-361`). A chunked file in an embedded namespace with no vector leaves a gap in the vector store and gives `FABRIC_INCOMPLETE` (`:262-264`).
7. **Installing over an untracked file is refused** (`WOULD_OVERWRITE`, `fabric.py:187-190`), and a write through a link or outside the project is refused (`INSTALL_PATH_UNSAFE`). A9 still needs a clean tree at its start (`stages.py:63`, `project.py:98-107`).
8. **Proof (a), stand-in.** The legacy-docs figures match `proof-a-results.json`: plan, `no_route`, assessment peak 41,353,216 B, scan null/`missing`, route times, 3,729 s, `binary_held` 2, lexical 29/29.
9. **Proof (a), real embedder.** The figures match `proving-ground-real/*-result.json` for python-app, rust-workspace, typescript-monorepo and secret-history: commits, sizes, A9 seconds, per-store counts, nodes and edges, stage peaks, routes, vector scans (415.3 / 11.1 / 10.1 / 11.9 ms, reason null), measures, digests, departures 0, installed 5. `proof-a-real-results.json` holds the first three. Secret-history's file is separate (run at 09:12, before L-1's commit at 09:24), which fits the evidence's "A9 code unchanged by L-1".
10. **The legacy-docs residual is stated plainly.** The evidence says (`:352`, `:363-373`) that the run did not finish in the hour, that no record or figures exist, why (the two binaries' 94,222 chunks), and that a re-run would take as long. S5, S6, S7 and S8 still hold with it: S5 and S6 are data with no bar, and four repositories have real scans; S7 and S8 each have a section with a commit (the stand-in run) for all five, and the residual is named with its cause. The evidence does not claim a real figure for legacy-docs.
11. **Proof (d).** It names W2-27 and records no run on EXAMIN's copy (`:375-380`). Unchanged since round 1.
12. **Lines not touched since round 1, briefly re-confirmed:** `memory_sets.py`, `layout.py` and `rebuild/command.py` have no change since 7bcd84765. success-12 and 18 to 23, failure-6, 8 and 9 stand as round 1 judged them; success-10 and failure-3 now also hold RV1-6's fix.

## Findings
**Classification:** 1 blocking (RV2-1: in scope, reachable in ordinary work, loses work); 1 minor recorded row (RV2-2).

**RV2-1 (success-16; also reached through success-3's refusals), blocker. A refused or interrupted A9 throws away work done in the repository while it ran.**
- **What happens:** run 4's copy step undoes its copies with W2-23's `project.restore`, which is `git reset --hard <the commit A9 started on>` (`fabric.py:218-226`, `project.py:110-125`). `a9` calls it on any exception after the copies, including `FABRIC_INCOMPLETE`, `REBUILD_FAILED`, `DIGESTS_INCOMPLETE` and Ctrl-C (`fabric.py:564-569`). That window is the whole rebuild and the measure, which on legacy-docs with the real embedder ran more than an hour. Before run 4 a refusal after the build left the tree alone.
- **Reproduce 1 (planted, in process, stand-ins as in `test_w2_88_fabric.py`):** a lexical stand-in rewrites the tracked `a.md` (an edit made while A9 runs) and then raises `KeyboardInterrupt` (Ctrl-C). After A9 returns, `a.md` holds its committed text again: the edit is gone.
- **Reproduce 2:** the stand-in commits a new `notes.md` (`git commit -- notes.md`) and then raises a `GovError`. After A9 returns, the branch is back at `init`, `notes.md` is gone from the tree, and the commit survives only in the reflog (`HEAD@{0}: reset: moving to 563ce1b`).
- **No procedure text keeps the tree untouched while a stage runs.** I searched the adopt skill twice, in different words ("during a stage / do not edit or commit" and "reset --hard / concurrent / meanwhile"): not found.
- **Behaviour it should have (for a test designer):**
  - When A9 refuses or is interrupted after installing the kernel files, it removes from the index only the paths it staged. It deletes from the tree only the files it wrote, and only where their bytes are still the ones it wrote, plus the empty folders it made.
  - A tracked file edited during the run keeps its edit, and a new file staged during the run stays staged.
  - If HEAD moved during the run, A9 refuses without resetting, names the new commit, and leaves the branch where it is.
  - Case A: A9 with a stand-in that edits a tracked file and then refuses → the edit is still there and only A9's copies are gone.
  - Case B: the same, but the stand-in commits → the branch head is that commit.
- Ordinary work: yes. A9 now runs for many minutes to more than an hour, nothing holds the repository during that time, and stopping a long A9 with Ctrl-C or editing the repository in another terminal is an ordinary accident. Consequence: loses work.
- **Reverses it:** a decided rule, stated to the operator in the adopt skill or A9's own output, that the repository must not be edited or committed while a stage runs; or a ruling that concurrent work during adoption is not ordinary work under ADR-0001.

**RV2-2 (success-2), minor. In `PLAN.md` the first unscanned path sits on the heading's line.**
- **What happens:** `PLAN.md` reads ``Unscanned paths: - `huge.txt` ``: the first list item is inline with its heading and the rest go on new lines (`refactor_plan.py:172-178`). The paths are all there.
- **Behaviour it should have:** the paths form a list that starts on the line after "Unscanned paths:", so a reader or a grep for `` - `path` `` at the start of a line finds every unscanned path.
- Ordinary work: yes. Consequence: other.
- **Reverses it:** a reading that the form of PLAN.md's list is free.

## Notes, not findings
- **The copy step replaces a repository's own tracked kernel files.** If the repository already tracks a skill or template at `.claude/skills/retrieval/…`, `.claude/skills/discovery/…` or `governance/kernel/templates/{brief,role-cto}.md`, A9 overwrites it with Gov OS's version (decided: "always as Gov OS ships them"). The old version stays in history, but the record lists the file only under `installed` and does not say it replaced one. A `replaced` list would help the owner.
- **`gov_pin` in the record.** It is the pin of the `gov` found on `PATH` (`fabric.py:139`), not the code that ran A9. The real proof ran from source and recorded `pin-797495bdfc70`. This is unchanged since round 1. Taken with round 1's note on the pinned install, which still applies (`GOV_OS` under site-packages now also breaks `_sources` and `read_standard`, both failing closed: `KERNEL_SOURCE_MISSING` / `FileNotFoundError`), it is one for W2-27.
- **Binaries are not scanned for secrets** and are not counted as unscanned either (`assess.py:316-324`). Gitleaks skips binaries anyway, so `secrets_unscanned` reflects only text files.
- **The real run's `embedder`** is read before the build (`fabric.py:140-144`, unchanged). The four finished repositories still recorded it.
- **td-4's revision** of S16's discovery case (W2-142 S2's decided line in place of the literal phrase) is a decided-behaviour revision. The KPI's four phrases are held by the retrieval skill and T-0, as S15's Verify asks.

```verdict
{"kpis": [
{"kpi": "success-1", "verdict": "pass", "findings": ["RV1-8"]},
{"kpi": "success-2", "verdict": "pass", "findings": ["RV1-3", "RV2-2"]},
{"kpi": "success-3", "verdict": "pass", "findings": ["RV1-4", "RV1-5"]},
{"kpi": "success-4", "verdict": "pass", "findings": []},
{"kpi": "success-5", "verdict": "pass", "findings": ["RV1-2"]},
{"kpi": "success-6", "verdict": "pass", "findings": []},
{"kpi": "success-7", "verdict": "pass", "findings": []},
{"kpi": "success-8", "verdict": "pass", "findings": ["RV1-7"]},
{"kpi": "success-9", "verdict": "pass", "findings": []},
{"kpi": "success-10", "verdict": "pass", "findings": ["RV1-6"]},
{"kpi": "success-11", "verdict": "pass", "findings": ["RV1-1", "RV1-10", "RV1-11"]},
{"kpi": "success-12", "verdict": "pass", "findings": []},
{"kpi": "success-13", "verdict": "pass", "findings": []},
{"kpi": "success-14", "verdict": "pass", "findings": []},
{"kpi": "success-15", "verdict": "pass", "findings": []},
{"kpi": "success-16", "verdict": "fail", "findings": ["RV1-9", "RV2-1"]},
{"kpi": "success-17", "verdict": "pass", "findings": []},
{"kpi": "success-18", "verdict": "pass", "findings": []},
{"kpi": "success-19", "verdict": "pass", "findings": []},
{"kpi": "success-20", "verdict": "pass", "findings": []},
{"kpi": "success-21", "verdict": "pass", "findings": []},
{"kpi": "success-22", "verdict": "pass", "findings": []},
{"kpi": "success-23", "verdict": "pass", "findings": []},
{"kpi": "failure-1", "verdict": "pass", "findings": []},
{"kpi": "failure-2", "verdict": "pass", "findings": ["RV1-5"]},
{"kpi": "failure-3", "verdict": "pass", "findings": ["RV1-6"]},
{"kpi": "failure-4", "verdict": "pass", "findings": []},
{"kpi": "failure-5", "verdict": "pass", "findings": []},
{"kpi": "failure-6", "verdict": "pass", "findings": []},
{"kpi": "failure-7", "verdict": "pass", "findings": ["RV1-1", "RV1-10"]},
{"kpi": "failure-8", "verdict": "pass", "findings": []},
{"kpi": "failure-9", "verdict": "pass", "findings": []}
], "overall": "fail"}
```
