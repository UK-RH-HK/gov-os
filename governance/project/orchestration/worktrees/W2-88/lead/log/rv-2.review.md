task: DAEO-2bdu (W2-88), review round 2 of 2, the last (DEC-1010), at head 15ad055adbb5d12abe4ecdf83344c7f504315d01
status: DONE. **FAIL.** All three round-1 blockers are fixed and probed, but the copy step built in run 4 brought in one new blocker (RV2-1): when A9 refuses or is stopped, it discards work done in the repository while it was running.
work_completed: Step 0 and identity checks at start and end. Read round 1's record, both run-4 interfaces, the ticket's three interface sections, and the diff of every ticket commit since 7bcd84765. Checked scope and trailers. Probed RV1-1 to RV1-8 and L-1 on repositories I planted in my TMPDIR: MA through the CLI with and without gitleaks, with a blob over 16 MiB, and on a clean repository; `read_standard`, `departures`, `check_keys` and the pin's constants in process; the `vector_scan` seam with five kinds of reply; a load into a stale store; A9's undo path with stand-ins. Checked the evidence's figures against the three results sources.
files_changed: none
evidence: Commands and results are under "What I probed and found sound" and "Findings" below. Planted repositories are in /tmp/gov-launch-6wklgg_u/claude-1000/rv2/ (outside every repository).
tests: No pytest was run; the lead's `gov accept` and lead_verify cover the suites (DEC-1144 (7): I re-run nothing the lead ran). Probes were in process and through the CLI, on planted repositories only.
discoveries: RV2-1 (blocker). A9's undo (`fabric.undo` → `project.restore`) is `git reset --hard` to the commit A9 started on. Since run 4 it runs on any refusal or Ctrl-C after the kernel copies, which covers the whole rebuild (more than an hour on legacy-docs with the real embedder). An edit or commit made in the repository during that time is lost. RV2-2 (minor): in `PLAN.md` the first unscanned path sits on the same line as its heading.
risks: RV2-1 loses work (edits to tracked files, staged new files, commits moved off the branch). Recovery is possible only through the reflog, and only for commits.
lessons: When a change makes a stage write into the tree, check that its undo stays as narrow as the writes.
proposed_decisions: none. RV2-1's fix is a described behaviour (below), within this ticket's paths.
unresolved: Round 2 is the last (DEC-1010), so RV2-1 goes to the owner once, with options. Not checked here: the stamped-1 case of RV1-6 (the unit tests cover it; I probed the unstamped case).
recommended_next_action: The lead takes RV2-1 to the owner with options: (a) a narrow fix in `fabric.undo`: unstage and delete only what A9 wrote, never reset, and refuse rather than undo if HEAD moved, followed by a narrow independent check; (b) accept it as a named residual and have the adopt skill and A9's output say the tree must stay untouched while A9 runs; (c) re-baseline.

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