---
type: probe
task: DAEO-2bdu
round: 1
reviewer_session: c168bd40-4462-4b61-9a70-0b7330fcf4c9
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 5b41893beb797072af8b6cad8e6c514cfee55fa4
decisions_applied: [DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1112, DEC-1144, DEC-1157]
---

# Probe record: W2-88 (DAEO-2bdu), review round 1 of at most 2 (DEC-1010): FAIL

## The lead's judgement and triage

- **Who probed.** A fresh, read-only Independent Auditor session (`c168bd40-4462-4b61-9a70-0b7330fcf4c9`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-13 at 05:13. Step 0 held (the write outside the tree failed with a read-only file system; the index refresh worked). The head was 5b41893beb79 and `git status --porcelain` was empty at start and end. Its tripwire changes were in the CTO's store trees only (W2-00-store, W2-00-store-b).
- **Refusals the reviewer met, each once, none retried:** a Write under quiet hours (DEC-991), a Bash `find` in the pin's site-packages read by the hook as a hidden-set read, and a shell variable as a write target.
- **The lead's verification at the head** (lead_verify, scoped, outside the sandbox): parallel 6,043 tests, 6 failed, 8 skipped; serial 3 passed. The 6 are five W2-88 cases tied to package P-W2-88-B-1 (S16's copy step; the loader's `rerank`/`bundle` keys) and `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`, which is red on the integrate tree too (W2-00-store at cb208f943: 1 failed), so it is integrate's, not this branch's.
- **The verdict stands as FAIL** (never decided away, DEC-1010). The triage of every finding:

| finding | severity | triage | the fix, as a described behaviour for the test designer (DEC-136) |
|---|---|---|---|
| RV1-1 tuned pool is no departure | blocker | fix; the reading goes to the CTO as P-W2-88-B-1 B-1.4 (recommended: the whole shipped block) | a `retrieval.yaml` whose pool is on but differs from the shipped `pool:` block in any key names `pool` with its value in `departures`; the stage is not ok without `--decision` |
| RV1-2 an unavailable vector scan is recorded as one | blocker | fix | when the semantic route answers unavailable or errors, `scale.vector_scan_ms` is null with the reason named (not measured), never compared as under budget; only the vector scan is compared with the budget (S5's text) |
| RV1-3 without gitleaks the plan says "no secret" | blocker | fix; the form goes to the CTO as B-1.5 (recommended: `SECRETS_UNSCANNED`) | when the secrets scan did not run, or skipped files, MA writes no `NOTHING-TO-REFACTOR.md` and its plan and result name the unscanned state |
| RV1-4 binaries listed refused while the store holds them | minor | fix | `refused` never holds a file the store holds; a binary the lexical store chunked is listed as indexed there |
| RV1-5 code graph lists, swallowed read error | minor | fix (the error part); language part with P-3 | a code graph that cannot be read is named in the record and the store is not ok, never 0 nodes and edges with ok; a file whose suffix the graph does not read is refused `unsupported-language` |
| RV1-6 a record load re-stamps a stale store | minor | fix | after `loader.load` on a stale store, `connect` still refuses it (or the load replaces it whole) |
| RV1-7 evidence calls an unrun scan a scan time | minor | fix with RV1-2 | the proof says no vector scan was measured (stand-in embedder), or gives the real figure from a run with the embedder |
| RV1-8 the no-route rule stated differs from the code | minor | fix | the evidence and `assess` state the same rule; a planted file with an unlisted code suffix lands where the rule says |
| RV1-9..11 = B-1.1..B-1.3 | package | the CTO | P-W2-88-B-1 |

- **Round 2** (the last, DEC-1010) waits for the CTO's answers to P-W2-88-B-1, so that one test-design batch and one fix carry both the findings and the decided package items.

# W2-88 (DAEO-2bdu): review round 1
probed_commit: 5b41893beb797072af8b6cad8e6c514cfee55fa4
base: b482fc5bf

## Sandbox and identity
- **Step 0 (a):** writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `OSError: [Errno 30] Read-only file system`, as it should.
- **Step 0 (b):** `echo sandbox-trial | git hash-object -w --stdin` printed `1ae28402…` (exit 0), and `git update-index --refresh` exited 0. This is the one write the launcher requires: a loose object in the shared `.git`.
- **Identity:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`.
- **Head and status at start:** head `5b41893beb797072af8b6cad8e6c514cfee55fa4`, `status --porcelain` empty.
- **Head and status at end:** the same head, status empty.
- **Model processes:** `ps … [o]llama|[l]lama-server` shows nothing, at start and at end.

## What I probed and found sound
1. **Scope.** There are 7 first-parent non-merge commits from b482fc5bf to the head.
   - Every file they touch is in `allowed_paths`.
   - Every commit carries `Task: DAEO-2bdu` and `Role: engineer`.
   - Every `Implements:` id is in `sources:`: DEC-954, DEC-957, DEC-078, CAP-44.b, DEC-941, DEC-1099, DEC-694, DEC-388, CAP-44.f, CAP-44.g, CAP-17, CAP-20, DEC-016, DEC-1098, DEC-1101, DEC-1125, CAP-19.
2. **MA writes nothing in the repository (F1/S1).** I planted a repository with a vendored folder, a vendored-by-header file, a generated file, a minified file, a binary, a 1.2 MB file, a COBOL file and a github-pat secret. I hashed every file (including `.git`), `ls-files -s`, `log --all` and `for-each-ref`, ran `gov adopt --lite --stage MA --out`, and hashed again: identical. Exit 0, kinds `generated-no-folder, over-limit, secret`. The assessment holds every field of the interface, each planted item under its category with `by`, and the secret as `{path, rule: github-pat}`.
3. **The secret's value never leaks (F5).** `grep -F -f secret.val` over the output folder, stdout and stderr finds 0 hits. The same holds for the run without gitleaks.
4. **`OUT_INSIDE_PROJECT` refuses.** Tried through a link into the project, through `out1/../p1/outy`, through `./.git/outz`, and with the project root itself. All four are refused; nothing was written in the repository and no file was created there. Code: `assess.py:76-78,259`; `fabric.py:392-401` uses resolved paths, and `require_commit` makes the root resolved.
5. **No `tk`, no commit.** The only child processes in `assess.py` and `refactor_plan.py` are `git` and `gitleaks`. MA returns without `run.finish` (`stages.py:68-82`).
6. **Streaming (F4).** Blobs are read one at a time through `git cat-file --batch` (`assess.py:81-108`), each capped at 16 MiB (`SCAN_LIMIT_BYTES`). Scan batches hold at most 1 MiB or one file. What grows with the tree is only the path listing. The upper-bound case passes in the lead's run.
7. **Layout (success-10, F3).** I planted stores and opened them with `loader.connect`:

   | Store planted | Result |
   |---|---|
   | stamped 1 | `STORE_LAYOUT_STALE {'found': 1, 'expected': 2}` |
   | stamped 3 | `STORE_LAYOUT_STALE {'found': 3, 'expected': 2}` |
   | unstamped, `register_entries` without `span` | `STORE_LAYOUT_STALE {'found': 0, 'expected': 2}`, never `STORE_MISSING` |
   | unstamped with complete tables | opens |
   | stamped 2 | opens |
   | empty or doubled stamp | stale (0) |

   The column lists in `STORES` match the real `CREATE TABLE` statements (`lexical.py:92-96`, `semantic.py:125-128`).
8. **Rebuild.** `_replace_stale` runs under the lock, before the seed, and reports `layout`. `digests_of` adds four digests: chunk_id is TEXT and content-derived, and `semantic_pin` holds config values, so both are deterministic. `check_digests` refuses when any of the four is absent (`fabric.py:130-136`). Rebuild's `ok` rules are unchanged: the diff only adds `digests`, `layout` and `_replace_stale`.
9. **Stores not built (F2).** A store the rebuild names `not_built` (lexical with no rules, codeintel when called for and failed, reverse_edges) makes A9 raise `FABRIC_INCOMPLETE` (`fabric.py:434-442`). A semantic store that was asked for and not recreated fails `REBUILD_FAILED` first (`rebuild/command.py:206`).
10. **Proof (a) figures match the results file.** Every figure in `docs/changes/W2-88-evidence.md` matches `~/gov-os-runs/W2-88/proof-a-results.json`: commits, size, assessment counts and estimates, the alone peak (41,230,336 B under 805,306,368 B), plan count and kinds, per-store judged, indexed and refused, chunks, vectors, seconds, digests, routes, budget and measure. The set checks match `set-checks.txt`. The committed record `legacy-docs/governance/adoption/A9-memory-fabric.md` holds every block of the interface and no question text.
11. **Proof (d).** The evidence names W2-27 and records no run on EXAMIN's copy. The embedder stand-in, the code-graph stand-in, the lock path and the reader are stated plainly; the one exception is RV1-7.
12. **The set tools.**
    - `launch-check`: exit 10 for an unapproved file, a missing file and a malformed call; exit 0 for an approved one.
    - `memory_sets.py` imports `gov.memaudit` and defines no pre-flight, USED marker or figures.
    - It makes no crontab call and starts no audit. `walls_act` only writes under `--out`, and the sets root is only named.
13. **A9's measure has no bar.** No question text is written: residuals name questions by id (`fabric.py:360-387`).

**The P-W2-88-B-1 items, each found as stated:**
- **B-1.1:** no stage copies the kernel skills (evidence seam 5; `STAGE` in `stages.py:544`). `test_s16_a_…` fails.
- **B-1.2:** `gov.config.loader` refuses `rerank:` and `bundle:` keys, so the second-reranker and bundle-budget departures cannot be planted through the CLI. 4 cases fail.
- **B-1.3:** nothing under `src/gov/adopt/` installs `retrieval.yaml`. `fabric.departures(None)` returns `[{'setting': 'pool', 'value': False}]`, so A9 on a fresh adoption refuses `STANDARD_DEPARTURE` unless a `--decision` is given. This fails closed.

## Findings
**Classification:** 3 blocking (RV1-1, RV1-2, RV1-3: in scope, reachable in ordinary work, fail open). 5 minor recorded rows (RV1-4 to RV1-8). 3 package items (RV1-9 to RV1-11 = B-1.1 to B-1.3).

**RV1-1 (success-11, failure-7), blocker. A tuned pool is not a departure.**
- **What happens:** A9 reports no departure when the repository's `retrieval.yaml` turns the pool on with values other than those Gov OS ships. Only `meaning_uncut: false` or a missing block counts (`fabric.py:75,89`).
- **Reproduce:** `fabric.departures({'pool': {'meaning_uncut': True, 'route_depth': 5, 'rerank_depth': 3, 'per_file_first10': 9, 'drop_nested': False}})` returns `[]`, and so does `{'pool': {'meaning_uncut': True}}`. `STANDARD['pool']` is the shipped block (60/40/2/True).
- **Expected behaviour:** a planted `retrieval.yaml` whose pool is on but differs from the shipped block in any key names `pool` with its value in `departures`, and the stage is not ok without `--decision`.
- Ordinary work: yes, because the loader accepts every pool key, and an adopter tuning depth is ordinary. Consequence: fails open.
- **Reverses it:** an owner or CTO ruling that "the pool on" means `meaning_uncut: true` alone. The interface's "compares with `pool_on`" points that way, but the KPI and `STANDARD` say "the block as Gov OS ships it".

**RV1-2 (success-5), blocker. A vector scan that never ran is recorded as one.**
- **What happens:** when the semantic route answers unavailable, its few-ms reply is recorded as `vector_scan_ms` and compared with the budget as if it were a scan (`fabric.py:299-316`; `semantic.search` returns `FACET_UNAVAILABLE` without scanning). So an over-budget scan can never be seen and no `SCALE-PROPOSAL.md` is written.
- **Seen in all five proof repositories:** `embedder: null` alongside `vector_scan_ms: 1.7` (legacy-docs record lines 104 and 112), against 94,192 vectors.
- **Also:** only the vector scan is compared. The `retrieve` route took 6,356 ms against the 2,000 ms "retrieve budget" with no proposal.
- **Expected behaviour:**
  - When the semantic route answers unavailable or errors, `vector_scan_ms` is null and the record names the reason, as an unmeasured figure, never under budget.
  - A planted unavailable embedder gives that record.
  - The designer should state whether a route time over the budget also writes the proposal.
- Ordinary work: yes, because A9 run while the query embedder is not up gives exactly this, and it happened in every proof run. Consequence: fails open.
- **Reverses it:** a case showing an unavailable route yields a null scan time or a proposal.

**RV1-3 (success-2), blocker. Without gitleaks, the plan calls a repository with a secret clean.**
- **What happens:** on a machine without gitleaks, MA exits ok and writes `NOTHING-TO-REFACTOR.md` saying "no secret in a tracked file" for a repository that holds one. The only trace is `secrets_scanned: false` inside the JSON (`assess.py:124-125`; `refactor_plan.py:80-82,159-163`). Blobs over 16 MiB are skipped the same way (`secrets_unscanned`).
- **Reproduce:** a repository with one github-pat line. With gitleaks on PATH: 1 proposal (`secret`). With `PATH=/usr/bin:/bin`: 0 proposals and `NOTHING-TO-REFACTOR.md`. Adoption itself does not require the gitleaks binary.
- **Expected behaviour:** when the secrets scan did not run, or skipped files, the plan says so (a blocker or a refusal) and never writes "no secret". A planted run without gitleaks yields no `NOTHING-TO-REFACTOR.md` claiming none.
- Ordinary work: yes, because gitleaks is an external tool an adopter may lack. Consequence: fails open.

**RV1-4 (success-3), minor. Binary files are listed as refused while the store holds them.**
- **What happens:** the lexical index chunks a binary file as text, the embedder embeds it, and A9's record lists the file as refused for `binary` (`fabric.py:242-243`). In legacy-docs the 2 binaries make up most of the 94,192 chunks and vectors, while `vectors.indexed` lists 15 files.
- **Expected behaviour:** a tracked binary held by the store is listed as indexed (or the stage names the contradiction); `refused` never holds a file the store holds.
- Ordinary work: yes. Consequence: other.

**RV1-5 (success-3, failure-2), minor. The code graph's lists are not what the tool indexed.**
- **What happens:** A9 counts a code file as indexed by the code graph when it was merely copied to the tool's staging folder, so a COBOL file the graph cannot read is listed as indexed, and `unsupported-language` is reachable only for files the lexical index refused (`fabric.py:263-269`).
- **The coverage check is empty:** `judged` = `|indexed| + |refused|` by construction.
- **An error is swallowed:** a failure reading the graph becomes nodes 0, edges 0 with the stage ok (`fabric.py:272-276`).
- **Expected behaviour:** with the code graph called for, a file in a language the tool does not read is refused `unsupported-language`, and a graph that cannot be read is named, not shown as 0.
- Ordinary work: yes, when `code_intelligence` is on. Consequence: other (nodes and edges are P-3's residual).

**RV1-6 (success-10, failure-3), minor. A record load re-stamps a stale store as current.**
- **What happens:** any load of the record store (`gov close`, adoption stages through `record_graph`) stamps the whole file layout 2 while rebuilding only the record tables (`loader.py:694-703`). A stale store then opens as current, and `gov rebuild` no longer replaces it.
- **Reproduce:** an unstamped store whose `lexical_chunk` lacks `parent_id`. `connect` gives `STORE_LAYOUT_STALE (0)`; after `loader.load` it opens, with the old row still there.
- **Expected behaviour:** a load into a stale store either replaces it or leaves it stale; `connect` after a load still refuses it.
- Ordinary work: yes. Consequence: other (today the lexical index rebuilds its own older forms).

**RV1-7 (success-8), minor. The evidence presents 1.2–3.2 ms as each proof repository's vector-scan time against the budget.**
- **What happens:** the evidence calls these figures "the stand-in's route", but the semantic route answered unavailable and scanned nothing (see RV1-2).
- **Expected behaviour:** the proof says plainly that no vector scan was measured.
- Ordinary work: yes. Consequence: other.

**RV1-8 (success-1), minor. The no-route rule in the evidence is not what the code does.**
- **What happens:** the evidence (seam 6) says a file whose suffix is in no list and is no document is `no_route: unsupported-language`. The code flags only the fixed `OTHER_CODE_SUFFIXES` list (`assess.py:305-306`), so for example `.vue`, `.ps1` and `.proto` files are not flagged.
- **Expected behaviour:** the code and the stated rule agree. A planted file with an unlisted code suffix lands where the rule says.
- Ordinary work: yes. Consequence: other.

**RV1-9 = P-W2-88-B-1.1 (success-16).** No stage copies the kernel's retrieval skill and T-0.

**RV1-10 = P-W2-88-B-1.2 (success-11, failure-7).** The loader refuses `rerank:` and `bundle:` keys.

**RV1-11 = P-W2-88-B-1.3 (success-11).** Adoption installs no `retrieval.yaml`, so A9 on a fresh adoption refuses `STANDARD_DEPARTURE` without a decision.

## Notes, not findings
- **The pinned install.** Under a site-packages pin (`~/.local/share/gov-os/pin-797495bdfc70` is a venv), `fabric.GOV_OS` and `memory_sets.GOV_OS` resolve to `lib/python3.12`. A9 would stop with FileNotFoundError on the briefs after the rebuild (this fails closed), and `walls_act` would copy an empty walls folder. A0's `TEMPLATE_GITLEAKS` has the same dependence, so adoption may be meant to run from a source checkout. W2-27 should know this.
- **Per-store peak RSS.** It is the stage's single high-water mark, repeated for every store. This is stated in the code and the evidence.
- **Cost.** It is always given for 40 questions (`COST_BASIS_N`), not for the repository's set size.
- **Real embedder.** Equal vector digests across two A9 runs are shown with the stand-in only.
- **Reading of the practice lines.** success-13, 14, 15 and 17 and failure-6 and 8 rest on `gov.memaudit` and the guard (GUARD cases). Their full use is W2-27's run. P-8 and P-9 are residuals. success-17's miss-section half has no case.

```verdict
{"kpis": [
{"kpi": "success-1", "verdict": "pass", "findings": ["RV1-8"]},
{"kpi": "success-2", "verdict": "fail", "findings": ["RV1-3"]},
{"kpi": "success-3", "verdict": "pass", "findings": ["RV1-4", "RV1-5"]},
{"kpi": "success-4", "verdict": "pass", "findings": []},
{"kpi": "success-5", "verdict": "fail", "findings": ["RV1-2"]},
{"kpi": "success-6", "verdict": "pass", "findings": []},
{"kpi": "success-7", "verdict": "pass", "findings": []},
{"kpi": "success-8", "verdict": "pass", "findings": ["RV1-7"]},
{"kpi": "success-9", "verdict": "pass", "findings": []},
{"kpi": "success-10", "verdict": "pass", "findings": ["RV1-6"]},
{"kpi": "success-11", "verdict": "fail", "findings": ["RV1-1", "RV1-10", "RV1-11"]},
{"kpi": "success-12", "verdict": "pass", "findings": []},
{"kpi": "success-13", "verdict": "pass", "findings": []},
{"kpi": "success-14", "verdict": "pass", "findings": []},
{"kpi": "success-15", "verdict": "pass", "findings": []},
{"kpi": "success-16", "verdict": "fail", "findings": ["RV1-9"]},
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
{"kpi": "failure-7", "verdict": "fail", "findings": ["RV1-1", "RV1-10"]},
{"kpi": "failure-8", "verdict": "pass", "findings": []},
{"kpi": "failure-9", "verdict": "pass", "findings": []}
], "overall": "fail"}
```